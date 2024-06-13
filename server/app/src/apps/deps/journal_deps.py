import logging

from fastapi import HTTPException, status

from ...core.base_service import S3Events


async def s3_journal_middleware(files: list, user_id: int):
    if files:
        if len(files) > 4:
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Journal images cannot exceed maximum 4"
                    )
        
        logging.info("Jumping into the S3 bucket")
        s3_obj_key_list = await S3Events().upload_file(files=files, folder_name="journal", user_id=user_id)
        
        """ 테스트용: 위의 s3_images 변수를 아래로 바꾸면 실제 S3 접근을 안하고 테스트 가능합니다 """
        # s3_obj_key_list = ["a89bbc7a-34cf-439c-afb5-039fb2b88ee0"]

        return s3_obj_key_list