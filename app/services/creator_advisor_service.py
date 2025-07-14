import requests
import logging
from datetime import datetime
from urllib.parse import urlencode

import pandas as pd
from pyairtable import Api

from app.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Airtable API 클라이언트 초기화
api = Api(settings.BLOG_AIRTABLE_API_KEY)
base = api.base(settings.BLOG_AIRTABLE_BASE_ID)

# 테이블 객체
table_keyword_rank = base.table(settings.AIRTABLE_NAVER_KEYWORD_RANK_TABLE_NAME)
table_keyword_trend = base.table(settings.AIRTABLE_NAVER_KEYWORD_TREND_TABLE_NAME)
table_popular_contents = base.table(settings.AIRTABLE_NAVER_POPULAR_CONTENTS_TABLE_NAME)

# 상수 정의
CHANNEL_ID = "elza79"
SERVICE = "naver_blog"
CONTENT_TYPE = "text"
METRIC = "cv"
START_DATE = "2024-06-01"
END_DATE = "2025-06-30" # 트렌드, 경쟁력 조회용
POPULAR_CONTENTS_END_DATE = "2025-06-01" # 인기글 조회용 마지막 날짜


def _get_headers(referer_url: str):
    """API 요청에 필요한 헤더를 반환합니다."""
    return {
        "Cookie": settings.NAVER_ADVISOR_COOKIE,
        "Referer": referer_url
    }

def _make_api_request(url: str, headers: dict):
    """주어진 URL과 헤더로 API를 요청하고 결과를 반환합니다."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API 요청 실패: {url}, 에러: {e}")
        return None

def _fetch_referer_query_rank():
    """1. 월별 유입 검색어 순위를 가져옵니다."""
    logger.info("1. 월별 유입 검색어 순위 수집 시작...")
    all_keywords = set()
    records_to_create = []
    
    # 2024-06-01부터 2025-06-01까지 월별로 날짜 생성
    dates = pd.date_range(start=START_DATE, end=POPULAR_CONTENTS_END_DATE, freq='MS').strftime('%Y-%m-%d').tolist()

    for date in dates:
        params = {
            "channelId": CHANNEL_ID,
            "date": date,
            "interval": "month",
            "limit": 100,
            "metric": METRIC,
            "service": SERVICE
        }
        url = f"https://creator-advisor.naver.com/api/v6/inflow-analysis/referrer-query-rank?{urlencode(params)}"
        headers = _get_headers("https://creator-advisor.naver.com/naver_blog/elza79/inflow-analysis")
        
        data = _make_api_request(url, headers)
        if data and data.get("data"):
            for item in data["data"][0].get("topN", []):
                keyword = item.get("searchQuery")
                if not keyword:
                    continue
                
                all_keywords.add(keyword)
                records_to_create.append({
                    "date": date,
                    "channelId": CHANNEL_ID,
                    "searchQuery": keyword,
                    "referrer": item.get("referrer"),
                    "ratio": item.get("ratio")
                })
    
    if records_to_create:
        logger.info(f"총 {len(records_to_create)}개의 검색어 순위 데이터를 Airtable에 저장합니다.")
        table_keyword_rank.batch_create(records_to_create)
        
    logger.info(f"총 {len(all_keywords)}개의 유니크 키워드를 수집했습니다.")
    return list(all_keywords)

def _fetch_trend_and_competitiveness(keywords: list):
    """2 & 3. 키워드별 트렌드 및 경쟁력을 가져옵니다."""
    logger.info("2 & 3. 키워드별 트렌드 및 경쟁력 수집 시작...")
    records_to_create = []
    
    for keyword in keywords:
        # 2. Inflow Search Trend
        trend_params = {
            "channelId": CHANNEL_ID,
            "endDate": END_DATE,
            "interval": "month",
            "keyword": keyword,
            "service": SERVICE,
            "startDate": START_DATE
        }
        trend_url = f"https://creator-advisor.naver.com/api/v6/inflow-analysis/inflow-search-trend?{urlencode(trend_params)}"
        trend_headers = _get_headers(f"https://creator-advisor.naver.com/new-windows/query-stats?channelId={CHANNEL_ID}&endDate={END_DATE}&keyword={keyword}&service={SERVICE}&startDate={START_DATE}")
        trend_data = _make_api_request(trend_url, trend_headers)

        # 3. Query Competitiveness
        comp_params = {
            "channelId": CHANNEL_ID,
            "contentType": CONTENT_TYPE,
            "endDate": END_DATE,
            "interval": "month",
            "keyword": keyword,
            "metric": METRIC,
            "service": SERVICE,
            "startDate": START_DATE
        }
        comp_url = f"https://creator-advisor.naver.com/api/v6/inflow-analysis/query-competitiveness?{urlencode(comp_params)}"
        comp_headers = trend_headers # Referer가 동일하므로 재사용
        comp_data = _make_api_request(comp_url, comp_headers)

        # 데이터 통합
        if trend_data and trend_data.get("data") and comp_data and comp_data.get("data"):
            merged_data = {}
            for item in trend_data["data"]:
                merged_data[item["date"]] = {
                    "searchInflow": item.get("searchInflow"),
                    "datalabSearch": item.get("datalabSearch")
                }
            for item in comp_data["data"]:
                if item["date"] in merged_data:
                    merged_data[item["date"]].update({
                        "my": item.get("my"),
                        "totalMean": item.get("totalMean"),
                        "topMean": item.get("topMean")
                    })
            
            for date, values in merged_data.items():
                records_to_create.append({
                    "keyword": keyword,
                    "date": date,
                    **values
                })

    if records_to_create:
        logger.info(f"총 {len(records_to_create)}개의 트렌드/경쟁력 데이터를 Airtable에 저장합니다.")
        table_keyword_trend.batch_create(records_to_create)

def _fetch_popular_contents(keywords: list):
    """4. 키워드/월별 인기 콘텐츠를 가져옵니다."""
    logger.info("4. 인기 콘텐츠 수집 시작...")
    records_to_create = []

    dates = pd.date_range(start=START_DATE, end=POPULAR_CONTENTS_END_DATE, freq='MS').strftime('%Y-%m-%d').tolist()

    for keyword in keywords:
        for date in dates:
            params = {
                "channelId": CHANNEL_ID,
                "contentType": CONTENT_TYPE,
                "date": date,
                "interval": "month",
                "keyword": keyword,
                "limit": 20,
                "metric": METRIC,
                "service": SERVICE
            }
            url = f"https://creator-advisor.naver.com/api/v6/inflow-analysis/popular-contents?{urlencode(params)}"
            headers = _get_headers(f"https://creator-advisor.naver.com/new-windows/query-stats?channelId={CHANNEL_ID}&endDate={END_DATE}&keyword={keyword}&service={SERVICE}&startDate={START_DATE}")

            data = _make_api_request(url, headers)
            if not data:
                continue
            
            # 'data'와 'myData'를 모두 처리
            all_contents = data.get("data", []) + data.get("myData", [])
            
            for item in all_contents:
                created_at_ts = item.get("createdAt")
                # timestamp(ms)를 ISO 8601 형식의 문자열로 변환
                created_at_iso = datetime.fromtimestamp(created_at_ts / 1000).isoformat() + "Z" if created_at_ts else None

                records_to_create.append({
                    "date": date,
                    "keyword": keyword,
                    "rank": item.get("rank"),
                    "title": item.get("title"),
                    "contentId": item.get("contentId") or item.get("metaUrl"),
                    "statUrl": item.get("statUrl"),
                    "mobileStatUrl": item.get("mobileStatUrl"),
                    "myContent": item.get("myContent", False),
                    "metricValue": item.get("metricValue"),
                    "channelName": item.get("channelName"),
                    "createdAt": created_at_iso
                })

    if records_to_create:
        logger.info(f"총 {len(records_to_create)}개의 인기 콘텐츠 데이터를 Airtable에 저장합니다.")
        table_popular_contents.batch_create(records_to_create)

def sync_creator_advisor_data():
    """네이버 Creator Advisor 데이터를 동기화하는 전체 파이프라인입니다."""
    logger.info("네이버 Creator Advisor 데이터 동기화를 시작합니다.")
    try:
        # 1단계: 유입 검색어 순위 수집 및 유니크 키워드 확보
        unique_keywords = _fetch_referer_query_rank()

        if not unique_keywords:
            logger.warning("수집된 유니크 키워드가 없어 다음 단계를 진행할 수 없습니다.")
            return

        # 2 & 3단계: 키워드별 트렌드 및 경쟁력 수집
        _fetch_trend_and_competitiveness(unique_keywords)
        
        # 4단계: 인기 콘텐츠 수집
        _fetch_popular_contents(unique_keywords)

        logger.info("네이버 Creator Advisor 데이터 동기화가 성공적으로 완료되었습니다.")

    except Exception as e:
        logger.error(f"데이터 동기화 중 에러 발생: {e}", exc_info=True) 