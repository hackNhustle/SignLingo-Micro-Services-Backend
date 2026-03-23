
import jwt
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, ROUTE_TABLE

app = FastAPI(title="SignLingo API Gateway")

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared async HTTP client ─────────────────────────────────────────
client = httpx.AsyncClient(timeout=30.0)


# ── Helpers ──────────────────────────────────────────────────────────
def resolve_upstream(path: str):
    """Match the request path to an upstream service using the route table."""
    for prefix, upstream_url, requires_jwt, strip_prefix in ROUTE_TABLE:
        if path.startswith(prefix):
            return upstream_url, requires_jwt, strip_prefix, prefix
    return None, False, False, None


def validate_jwt(request: Request):
    """Validate the JWT Bearer token. Raises HTTPException on failure."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    try:
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ── Health check ─────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


# ── Catch-all reverse proxy ─────────────────────────────────────────
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(request: Request, path: str):
    full_path = f"/{path}"

    # Resolve upstream
    upstream_url, requires_jwt, strip_prefix, matched_prefix = resolve_upstream(full_path)
    if not upstream_url:
        raise HTTPException(status_code=404, detail=f"No route matched: {full_path}")

    # JWT gate
    if requires_jwt:
        validate_jwt(request)

    # Build upstream URL
    # If strip_prefix is True, remove the matched prefix from the path
    target_path = full_path
    if strip_prefix:
        target_path = full_path[len(matched_prefix):]
        if not target_path or not target_path.startswith("/"):
            target_path = "/" + target_path

    target_url = f"{upstream_url.rstrip('/')}{target_path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Forward headers (strip hop-by-hop & compression specs)
    forward_headers = dict(request.headers)
    for hop_header in ("host", "connection", "transfer-encoding", "accept-encoding"):
        forward_headers.pop(hop_header, None)

    # Read body
    body = await request.body()

    # Proxy the request
    try:
        upstream_response = await client.request(
            method=request.method,
            url=target_url,
            headers=forward_headers,
            content=body,
        )
    except httpx.ConnectError as e:
        print(f"DEBUG: ConnectError to {target_url}: {e}")
        raise HTTPException(status_code=502, detail=f"Upstream service unreachable (ConnectError): {e}")
    except httpx.TimeoutException as e:
        # Catch all timeouts (including PoolTimeout, ReadTimeout, etc.)
        print(f"DEBUG: TimeoutException ({type(e).__name__}) to {target_url}: {e}")
        raise HTTPException(status_code=504, detail=f"Upstream service timed out: {e}")
    except httpx.RequestError as e:
        print(f"DEBUG: RequestError ({type(e).__name__}) to {target_url}: {e}")
        raise HTTPException(status_code=502, detail=f"Upstream request failed ({type(e).__name__}): {e}")
    except Exception as e:
        print(f"DEBUG: Unknown Error proxying to {target_url}: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"Internal Gateway Error: {type(e).__name__}")

    # Forward response back
    excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    response_headers = {
        k: v for k, v in upstream_response.headers.items()
        if k.lower() not in excluded_headers
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


# ── Shutdown ─────────────────────────────────────────────────────────
@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
