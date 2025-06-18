from fastapi import APIRouter, HTTPException, BackgroundTasks, Path
from app.services.airtable_service import process_and_save_thread_data, get_thread_id_from_record
from app.models.airtable import AirtableWebhookPayload, SuccessResponse, FinalOutput
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
    try:
        # 웹훅 페이로드에서 테이블 이름 대신 테이블 ID를 사용해야 할 수 있습니다.
        # Airtable Automation 설정에 따라 이 부분을 유연하게 조정해야 합니다.
        # 여기서는 편의상 테이블 이름을 직접 조회하지만, 실제로는 tableId를 이름으로 변환하는 로직이 필요할 수 있습니다.
        table_name_map = {
            # 여기에 Airtable Base의 실제 Table ID와 이름을 매핑해야 합니다.
            # "tblxxxxxxxxxxxxxx": "cafeThread", 
        }
        # table_name = table_name_map.get(payload.tableId)
        # if not table_name:
        #     raise ValueError(f"Unknown tableId: {payload.tableId}")
        
        # 임시로 cafeThread 테이블로 가정. 실제 구현 시 위 로직으로 대체 필요
        # Airtable Automation 트리거가 어떤 테이블에서 발생했는지 알아야 합니다.
        # 지금은 recordId로 모든 테이블을 순회하며 찾는 방식으로 구현합니다.
        
        thread_id = None
        try:
            # cafeThreadReply 테이블부터 확인
            record = await get_thread_id_from_record(payload.recordId, "cafeThreadReply")
            thread_id = record.get('fields', {}).get('threadId')
        except Exception:
            try:
                # cafeThreadComment 테이블 확인
                record = await get_thread_id_from_record(payload.recordId, "cafeThreadComment")
                thread_id = record.get('fields', {}).get('threadId')
            except Exception:
                # cafeThread 테이블 확인
                record = await get_thread_id_from_record(payload.recordId, "cafeThread")
                thread_id = record.get('fields', {}).get('threadId')

        if not thread_id:
             raise ValueError("Failed to find threadId from any table for the given recordId.")

        background_tasks.add_task(process_and_save_thread_data, thread_id)
        
        return {
            "status": "success",
            "message": "Processing task has been added to the background.",
            "threadId": thread_id
        }
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reprocess/{thread_id}", response_model=FinalOutput)
async def reprocess_thread_manually(thread_id: str = Path(..., title="The Thread ID to reprocess")):
    """
    특정 thread_id에 대한 데이터 처리를 수동으로 실행합니다.
    성공 시, 최종적으로 저장된 데이터 전체를 반환합니다.
    """
    logger.info(f"Manual reprocessing requested for thread_id: {thread_id}")
    try:
        processed_data = await process_and_save_thread_data(thread_id)
        # Pydantic 모델로 변환하여 응답
        return FinalOutput(**processed_data)
    except ValueError as e:
        logger.error(f"Value error during reprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error during reprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.") 