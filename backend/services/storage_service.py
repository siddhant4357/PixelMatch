import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Service to handle Cloudflare R2 / AWS S3 uploads and downloads."""
    
    def __init__(self):
        # Supabase provides an S3-compatible API
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL")
        self.access_key = os.getenv("S3_ACCESS_KEY_ID")
        self.secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "pixelmatch")
        
        self.region_name = os.getenv("S3_REGION", "us-east-1")
        
        self.is_configured = bool(self.endpoint_url and self.access_key and self.secret_key)
        
        if self.is_configured:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region_name
            )
            logger.info(f"Cloud Storage (R2/S3) initialized for bucket: {self.bucket_name}")
        else:
            self.s3_client = None
            logger.warning("Cloud Storage credentials missing. Falling back to local disk (Ephemeral!).")
            
    def upload_file(self, file_bytes: bytes, object_name: str, content_type: str = "image/jpeg") -> bool:
        """Upload a file to the bucket directly from memory."""
        if not self.is_configured:
            return False
            
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_bytes,
                ContentType=content_type
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to upload to cloud storage: {e}")
            return False
            
    def upload_file_from_disk(self, file_path: str, object_name: str) -> bool:
        """Upload an existing file from disk to the bucket."""
        if not self.is_configured:
            return False
            
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file from disk: {e}")
            return False

    def download_file_to_disk(self, object_name: str, file_path: str) -> bool:
        """Download a file from the bucket to the local disk."""
        if not self.is_configured:
            return False
            
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                logger.info(f"Object {object_name} does not exist in bucket.")
            else:
                logger.error(f"Failed to download file from cloud storage: {e}")
            return False

    def get_file_bytes(self, object_name: str) -> Optional[bytes]:
        """Download a file straight to memory."""
        if not self.is_configured:
            return None
            
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
            return response['Body'].read()
        except ClientError as e:
            return None
            
    def get_presigned_url(self, object_name: str, expiration=3600) -> Optional[str]:
        """Generate a presigned URL for direct secure frontend access (Optional)."""
        if not self.is_configured:
            return None
            
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
            
    def delete_file(self, object_name: str) -> bool:
        """Delete a file from the bucket."""
        if not self.is_configured:
            return False
            
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from cloud storage: {e}")
            return False

# Global Singleton
_storage_service_instance = StorageService()

def get_storage_service() -> StorageService:
    return _storage_service_instance
