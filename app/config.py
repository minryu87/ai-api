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

    # Naver Creator Advisor
    NAVER_ADVISOR_COOKIE: str = os.environ.get("NAVER_ADVISOR_COOKIE")
    BLOG_AIRTABLE_API_KEY: str = os.environ.get("BLOG_AIRTABLE_API_KEY")
    BLOG_AIRTABLE_BASE_ID: str = os.environ.get("BLOG_AIRTABLE_BASE_ID")
    AIRTABLE_NAVER_KEYWORD_RANK_TABLE_NAME: str = os.environ.get("AIRTABLE_NAVER_KEYWORD_RANK_TABLE_NAME", "referer-query-rank-searchQuery")
    AIRTABLE_NAVER_KEYWORD_TREND_TABLE_NAME: str = os.environ.get("AIRTABLE_NAVER_KEYWORD_TREND_TABLE_NAME", "inflow-search-trend")
    AIRTABLE_NAVER_POPULAR_CONTENTS_TABLE_NAME: str = os.environ.get("AIRTABLE_NAVER_POPULAR_CONTENTS_TABLE_NAME", "popular-contents")


settings = Settings()
