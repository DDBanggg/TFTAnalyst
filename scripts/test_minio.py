"""
Test MinIO Connection
This script tests the connection to MinIO and performs basic operations.
"""

import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime

# MinIO Configuration
MINIO_ENDPOINT = "http://localhost:9100"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"

def create_s3_client():
    """Create and return S3 client for MinIO"""
    return boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'  # MinIO doesn't care about region, but boto3 requires it
    )

def test_list_buckets(s3_client):
    """Test: List all buckets"""
    print("\nTest 1: List Buckets")
    print("-" * 50)
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print(f"Found {len(buckets)} buckets:")
        for bucket in buckets:
            print(f"   - {bucket}")
        return True
    except ClientError as e:
        print(f"Error: {e}")
        return False

def test_upload_file(s3_client, bucket_name):
    """Test: Upload a test file"""
    print(f"\n📤 Test 2: Upload file to '{bucket_name}'")
    print("-" * 50)
    try:
        # Create test data
        test_data = {
            "test": "Hello from Python!",
            "timestamp": datetime.now().isoformat(),
            "message": "MinIO connection successful"
        }
        
        # Convert to JSON string
        json_data = json.dumps(test_data, indent=2)
        
        # Upload to MinIO
        key = f"test/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json_data.encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"   File uploaded successfully!")
        print(f"   Bucket: {bucket_name}")
        print(f"   Key: {key}")
        return key
    except ClientError as e:
        print(f"   Error: {e}")
        return None

def test_read_file(s3_client, bucket_name, key):
    """Test: Read a file from MinIO"""
    print(f"\n📥 Test 3: Read file from '{bucket_name}'")
    print("-" * 50)
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)
        
        print(f"   File read successfully!")
        print(f"   Content: {json.dumps(data, indent=2)}")
        return True
    except ClientError as e:
        print(f"   Error: {e}")
        return False

def test_list_objects(s3_client, bucket_name):
    """Test: List objects in a bucket"""
    print(f"\n📋 Test 4: List objects in '{bucket_name}'")
    print("-" * 50)
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            objects = response['Contents']
            print(f" Found {len(objects)} objects:")
            for obj in objects:
                print(f"   - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print(f" Bucket is empty (no objects yet)")
        return True
    except ClientError as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print(" MinIO Connection Test")
    print("=" * 50)
    
    # Create S3 client
    print(f"\n🔌 Connecting to MinIO at {MINIO_ENDPOINT}...")
    s3_client = create_s3_client()
    
    # Run tests
    results = []
    
    # Test 1: List buckets
    results.append(test_list_buckets(s3_client))
    
    # Test 2: Upload file to bronze bucket
    test_bucket = "tft-bronze"
    uploaded_key = test_upload_file(s3_client, test_bucket)
    results.append(uploaded_key is not None)
    
    # Test 3: Read the uploaded file
    if uploaded_key:
        results.append(test_read_file(s3_client, test_bucket, uploaded_key))
    
    # Test 4: List objects in bucket
    results.append(test_list_objects(s3_client, test_bucket))
    
    # Summary
    print("\n" + "=" * 50)
    print(" Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f" Passed: {passed}/{total}")
    print(f" Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\nAll tests passed! MinIO is working correctly!")
    else:
        print("\nSome tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)