from fastapi import APIRouter, BackgroundTasks

from app.services.naver_creator_advisor_selenium import run_full_crawl

router = APIRouter()

@router.post("/start-full-crawl", status_code=202)
async def start_full_crawl(background_tasks: BackgroundTasks):
    """
    CSV 파일의 모든 데이터를 기반으로 전체 크롤링 작업을 백그라운드에서 시작합니다.
    - CSV의 각 postId에 대해
    - 게시물 작성 월 ~ 2025-06-30 까지
    - 1달 간격으로 모든 키워드 데이터를 수집하여 CSV 파일로 저장합니다.
    """
    background_tasks.add_task(run_full_crawl)
    return {"message": "전체 크롤링 작업이 백그라운드에서 시작되었습니다. 완료 시 'creator_advisor_full_stats.csv' 파일이 생성됩니다."}
