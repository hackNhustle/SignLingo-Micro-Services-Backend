#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
api_secret = os.getenv('CLOUDINARY_API_SECRET')

print(f"CLOUD_NAME: {cloud_name}")
print(f"API_KEY: {api_key}")
print(f"API_SECRET: {api_secret}")

if not all([cloud_name, api_key, api_secret]):
    print("\n❌ Missing Cloudinary credentials!")
else:
    print("\n✅ All credentials loaded!")
