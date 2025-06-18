from fastapi import APIRouter, HTTPException, BackgroundTasks, Path
from app.services.airtable_service import process_and_save_thread_data, get_thread_id_from_record
from app.models.airtable import AirtableWebhookPayload, SuccessResponse, FinalOutput
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook/process-thread", response_model=SuccessResponse)
async def handle_webhook(payload: AirtableWebhookPayload, background_tasks: BackgroundTasks):
    """
    Airtable 자동화(Automation)에 의해 호출되는 웹훅 엔드포인트입니다.
    데이터 변경이 감지되면 백그라운드에서 데이터 처리 및 저장을 수행합니다.
    """
    logger.info(f"Webhook received: {payload.model_dump_json()}")
    
    thread_id = None
    record_id = payload.recordId

    # 여러 테이블을 순회하며 thread_id를 찾습니다.
    # Reply -> Comment -> Thread 순으로 확인하는 것이 가장 효율적입니다.
    table_names_to_check = [
        settings.AIRTABLE_CAFE_THREAD_REPLY_TABLE_NAME,
        settings.AIRTABLE_CAFE_THREAD_COMMENT_TABLE_NAME,
        settings.AIRTABLE_CAFE_THREAD_TABLE_NAME,
    ]

    for table_name in table_names_to_check:
        try:
            logger.info(f"Checking for record {record_id} in table {table_name}...")
            thread_id = get_thread_id_from_record(record_id, table_name)
            if thread_id:
                logger.info(f"Found threadId '{thread_id}' from table '{table_name}'.")
                break  # thread_id를 찾았으면 루프 중단
        except ValueError:
            # 해당 테이블에 레코드가 없으면 다음 테이블로 넘어감
            logger.info(f"Record {record_id} not found in table {table_name}. Trying next table.")
            continue
    
    if not thread_id:
        err_msg = f"Could not determine threadId for recordId {record_id} from any of the specified tables."
        logger.error(err_msg)
        raise HTTPException(status_code=404, detail=err_msg)

    background_tasks.add_task(process_and_save_thread_data, thread_id)
    
    return {
        "status": "success",
        "message": "Processing task has been added to the background.",
        "threadId": thread_id
    }


@router.post("/reprocess/{thread_id}", response_model=FinalOutput)
def reprocess_thread_manually(thread_id: str = Path(..., title="The Thread ID to reprocess")):
    """
    특정 thread_id에 대한 데이터 처리를 수동으로 실행합니다.
    성공 시, 최종적으로 저장된 데이터 전체를 반환합니다.
    """
    logger.info(f"Manual reprocessing requested for thread_id: {thread_id}")
    try:
        processed_data = process_and_save_thread_data(thread_id)
        # Pydantic 모델로 변환하여 응답
        return FinalOutput(**processed_data)
    except ValueError as e:
        logger.error(f"Value error during reprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error during reprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.") 