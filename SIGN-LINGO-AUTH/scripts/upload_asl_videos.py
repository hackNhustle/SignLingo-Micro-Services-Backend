import json
import os
from pathlib import Path
import sys

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
MAPPING_PATH = BASE_DIR / "asl_video_mapping.json"
VIDEOS_DIR = BASE_DIR.parent / "frontend" / "videos"


def configure_cloudinary() -> None:
    load_dotenv(BASE_DIR / ".env")
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
        api_key=os.getenv("CLOUDINARY_API_KEY", ""),
        api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
    )


def load_video_ids() -> list[str]:
    with MAPPING_PATH.open("r", encoding="utf-8") as handle:
        mapping = json.load(handle)

    ids = set()
    for _, words in mapping.items():
        for _, video_id in words.items():
            ids.add(str(video_id))

    return sorted(ids)


def upload_video(video_id: str, file_path: Path) -> None:
    public_id = f"asl_videos/{video_id}"
    cloudinary.uploader.upload(
        str(file_path),
        resource_type="video",
        public_id=public_id,
        overwrite=False,
    )


def main() -> int:
    configure_cloudinary()

    missing_env = [
        key
        for key in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET")
        if not os.getenv(key)
    ]
    if missing_env:
        print("Missing Cloudinary env vars:", ", ".join(missing_env))
        return 1

    if not MAPPING_PATH.exists():
        print("Mapping file not found:", MAPPING_PATH)
        return 1

    if not VIDEOS_DIR.exists():
        print("Videos directory not found:", VIDEOS_DIR)
        return 1

    video_ids = load_video_ids()
    print(f"Found {len(video_ids)} ASL video IDs in mapping")

    uploaded = 0
    skipped = 0
    missing_files = 0

    for idx, video_id in enumerate(video_ids, start=1):
        file_path = VIDEOS_DIR / f"{video_id}.mp4"
        if not file_path.exists():
            print(f"[{idx}/{len(video_ids)}] Missing file: {file_path.name}")
            missing_files += 1
            continue

        try:
            upload_video(video_id, file_path)
            print(f"[{idx}/{len(video_ids)}] Uploaded: {file_path.name}")
            uploaded += 1
        except Exception as exc:
            print(f"[{idx}/{len(video_ids)}] Skipped: {file_path.name} ({exc})")
            skipped += 1

    print("Done.")
    print(f"Uploaded: {uploaded}")
    print(f"Skipped: {skipped}")
    print(f"Missing files: {missing_files}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
