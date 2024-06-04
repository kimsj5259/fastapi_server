import boto3
import logging
import uuid

from ..core.config import settings
from fastapi import HTTPException, status
from botocore.exceptions import ClientError


S3_BASE_URL = "https://{}.s3.{}.amazonaws.com/".format(settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_DEFAULT_REGION)

'''
For Synchronous Events
'''
class S3Events():
    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_DEFAULT_REGION,
        )
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.region_name=settings.AWS_DEFAULT_REGION
    
    """Upload a file to an S3 bucket
    :param files - list type (maximum 4 for the moment)
    :return - unique key for each of image
    """
    async def upload_file(self, files: list, folder_name: str, user_id:int):
        obj_key_list = []

        for file in files:
            allowed_types = ["image/jpeg", "image/jpg", "image/png"]
            if not file.content_type in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{file.content_type} is not a valid JPG, JPEG, or PNG file."
                )

            # If S3 object_name was not specified, use file_name
            if (file.filename is None):
                logging.info("key cannot be None")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="file name cannot be None."
                )

            """image마다 고유의 키값을 위한 작업"""
            unique_key = str(uuid.uuid4())
            obj_key = f"{folder_name}/{user_id}/{unique_key}"
            
            try:
                self.s3_client.upload_fileobj(file.file, self.bucket, obj_key, ExtraArgs={"ContentType": file.content_type})
            except ClientError as e:
                logging.info("INFO: Failed to upload image")
                logging.error(e)
                return "failed to upload image"
            
            obj_url = "https://{}.s3.{}.amazonaws.com/{}".format(self.bucket, self.region_name, obj_key)
            logging.info(f"File object uploaded to {obj_url}")
            obj_key_list.append(obj_key)

        return obj_key_list

    
    def delete_images(self, files: list):

        for file in files:
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=file)
                logging.info(f'Deleted {file} from {self.bucket}')
                
            except ClientError as e:
                logging.info(f'Error deleting {file}: {str(e)}')
                raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"fail to delete {file} in s3 bucket {self.bucket}"
                    )
            