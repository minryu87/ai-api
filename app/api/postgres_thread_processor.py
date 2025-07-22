from fastapi import APIRouter, HTTPException, Path
from app.services.postgres_airtable_service import process_and_save_postgres_thread
from app.models.airtable import FinalOutput
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/reprocess-from-postgres/{thread_id}", response_model=FinalOutput)
def reprocess_thread_from_postgres(thread_id: str = Path(..., title="The Thread ID to reprocess from PostgreSQL")):
    """
    특정 thread_id에 대해 PostgreSQL DB에서 데이터를 가져와 처리하고 Airtable에 저장합니다.
    성공 시, 최종적으로 Airtable에 저장된 데이터 전체를 반환합니다.
    """
    logger.info(f"Manual reprocessing from PostgreSQL requested for thread_id: {thread_id}")
    try:
        processed_data = process_and_save_postgres_thread(thread_id)
        # Pydantic 모델로 변환하여 응답
        return FinalOutput(**processed_data)
    except ValueError as e:
        logger.error(f"Value error during PostgreSQL reprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Could not connect to the database.")
    except Exception as e:
        logger.error(f"Internal server error during PostgreSQL reprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.") 