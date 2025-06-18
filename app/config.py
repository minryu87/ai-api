# 환경설정 파일 예시

# 예시: BASE_URL = "https://example.com"

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    AIRTABLE_API_KEY: str = os.environ.get("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID: str = os.environ.get("AIRTABLE_BASE_ID")
    AIRTABLE_CAFE_THREAD_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_TABLE_NAME", "cafeThread")
    AIRTABLE_CAFE_THREAD_COMMENT_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_COMMENT_TABLE_NAME", "cafeThreadComment")
    AIRTABLE_CAFE_THREAD_REPLY_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_REPLY_TABLE_NAME", "cafeThreadReply")
    AIRTABLE_CAFE_THREAD_RELEVANCE_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_RELEVANCE_TABLE_NAME", "cafeThreadRelevance")

settings = Settings()
