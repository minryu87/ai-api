# 환경설정 파일 예시

# 예시: BASE_URL = "https://example.com"

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import URL
import logging

load_dotenv()

# 임시 로거 설정
temp_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Settings(BaseSettings):
    # --- Existing Airtable Settings ---
    AIRTABLE_API_KEY: str = os.environ.get("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID: str = os.environ.get("AIRTABLE_BASE_ID")
    AIRTABLE_CAFE_THREAD_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_TABLE_NAME", "cafeThread")
    AIRTABLE_CAFE_THREAD_COMMENT_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_COMMENT_TABLE_NAME", "cafeThreadComment")
    AIRTABLE_CAFE_THREAD_REPLY_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_REPLY_TABLE_NAME", "cafeThreadReply")
    AIRTABLE_CAFE_THREAD_RELEVANCE_TABLE_NAME: str = os.environ.get("AIRTABLE_CAFE_THREAD_RELEVANCE_TABLE_NAME", "cafeThreadRelevance")

    # --- New PostgreSQL Settings ---
    DB_USER: str = os.environ.get("DB_USER")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD")
    DB_HOST: str = os.environ.get("DB_HOST")
    DB_PORT: int = os.environ.get("DB_PORT")
    DB_NAME: str = os.environ.get("DB_NAME")

    def __init__(self, **values):
        super().__init__(**values)
        # --- 임시 로그 출력 ---
        temp_logger.info("--- Loaded Database Credentials ---")
        temp_logger.info(f"DB_USER: {self.DB_USER}")
        temp_logger.info(f"DB_HOST: {self.DB_HOST}")
        temp_logger.info(f"DB_PORT: {self.DB_PORT}")
        temp_logger.info(f"DB_NAME: {self.DB_NAME}")
        temp_logger.info(f"DB_PASSWORD is set: {'Yes' if self.DB_PASSWORD else 'No'}")
        temp_logger.info("------------------------------------")


    @property
    def DATABASE_URL(self) -> str:
        return str(URL.create(
            drivername="postgresql+psycopg2",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"sslmode": "require"}  # SSL 연결 강제
        ))
        
    # Naver Creator Advisor
    NAVER_ADVISOR_COOKIE: str = os.environ.get("NAVER_ADVISOR_COOKIE")
    BLOG_AIRTABLE_API_KEY: str = os.environ.get("BLOG_AIRTABLE_API_KEY")
    BLOG_AIRTABLE_BASE_ID: str = os.environ.get("BLOG_AIRTABLE_BASE_ID")
    AIRTABLE_NAVER_KEYWORD_RANK_TABLE_NAME: str = os.environ.get("AIRTABLE_NAVER_KEYWORD_RANK_TABLE_NAME", "referer-query-rank-searchQuery")
    AIRTABLE_NAVER_KEYWORD_TREND_TABLE_NAME: str = os.environ.get("AIRTABLE_NAVER_KEYWORD_TREND_TABLE_NAME", "inflow-search-trend")
    AIRTABLE_NAVER_POPULAR_CONTENTS_TABLE_NAME: str = os.environ.get("AIRTABLE_NAVER_POPULAR_CONTENTS_TABLE_NAME", "popular-contents")


settings = Settings()
