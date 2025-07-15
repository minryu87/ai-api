from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.creator_advisor_service import sync_creator_advisor_data, resume_from_keywords
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/sync-creator-advisor", status_code=202)
async def sync_data(background_tasks: BackgroundTasks):
    """
    네이버 Creator Advisor의 데이터를 가져와 Airtable에 동기화하는 작업을 시작합니다.
    - 1. 월별 유입 검색어 순위 수집
    - 2. 키워드별 트렌드 및 경쟁력 수집
    - 3. 키워드/월별 인기 콘텐츠 수집
    
    이 작업은 백그라운드에서 실행됩니다.
    """
    try:
        logger.info("Creator Advisor 데이터 동기화 요청을 수신했습니다. 백그라운드 작업을 시작합니다.")
        background_tasks.add_task(sync_creator_advisor_data)
        return {"message": "Creator Advisor 데이터 동기화 작업이 백그라운드에서 시작되었습니다."}
    except Exception as e:
        logger.error(f"동기화 작업 시작 중 에러 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="동기화 작업을 시작하는 데 실패했습니다.")

@router.post("/resume-from-keywords", status_code=202)
async def resume_data(background_tasks: BackgroundTasks):
    """
    referer-query-rank-searchQuery 테이블에서 유니크 키워드를 추출하여,
    2, 3, 4단계만 동기화하는 작업을 백그라운드에서 실행합니다.
    """
    try:
        logger.info("[Resume] Creator Advisor resume-from-keywords 요청을 수신했습니다. 백그라운드 작업을 시작합니다.")
        background_tasks.add_task(resume_from_keywords)
        return {"message": "Creator Advisor resume-from-keywords 작업이 백그라운드에서 시작되었습니다."}
    except Exception as e:
        logger.error(f"[Resume] 동기화 작업 시작 중 에러 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="resume-from-keywords 작업을 시작하는 데 실패했습니다.") 