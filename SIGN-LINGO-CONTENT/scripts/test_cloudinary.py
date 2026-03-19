#!/usr/bin/env python3
"""Test script to verify Cloudinary configuration"""

import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

# Configure Cloudinary
cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', '788746597461992')
api_key = os.getenv('CLOUDINARY_API_KEY', '788746597461992')
api_secret = os.getenv('CLOUDINARY_API_SECRET', '5JNheSh-W_dytkxmeBRICisTSNE')

print(f"🔧 Cloudinary Configuration:")
print(f"   Cloud Name: {cloud_name}")
print(f"   API Key: {api_key[:10]}...")
print(f"   API Secret: {api_secret[:10]}...")

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

try:
    print("\n📸 Testing Cloudinary connection...")
    
    # Create a test image file
    test_image_path = 'test_image.txt'
    with open(test_image_path, 'w') as f:
        f.write("This is a test image")
    
    # Try to upload
    result = cloudinary.uploader.upload(
        test_image_path,
        public_id='test_upload',
        resource_type='raw'
    )
    
    print(f"✅ Cloudinary connection successful!")
    print(f"   Public ID: {result.get('public_id')}")
    print(f"   URL: {result.get('secure_url')}")
    
    # Clean up
    os.remove(test_image_path)
    
except Exception as e:
    print(f"❌ Cloudinary connection failed!")
    print(f"   Error: {str(e)}")
    import traceback
    traceback.print_exc()
