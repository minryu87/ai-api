from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from app.services.postgres_airtable_service import get_thread_id_from_any_record, process_and_save_postgres_thread
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PostgresWebhookPayload(BaseModel):
    recordId: str = Field(..., description="The ID of the record that was created or updated (e.g., 'REPLY_123', 'COMMENT_456', 'THREAD_789').")

@router.post("/webhook/process", status_code=202)
async def handle_postgres_webhook(payload: PostgresWebhookPayload, background_tasks: BackgroundTasks):
    """
    Receives a webhook from n8n, determines the master thread_id from the recordId,
    and processes the entire thread data from PostgreSQL to Airtable in the background.
    """
    logger.info(f"Postgres webhook received: {payload.model_dump_json()}")
    
    try:
        # Get the master thread_id by analyzing the recordId string
        thread_id = get_thread_id_from_any_record(
            record_id=payload.recordId
        )
        
        if not thread_id:
            raise ValueError(f"Could not determine thread_id for record '{payload.recordId}'.")

        # Add the main processing task to the background
        background_tasks.add_task(process_and_save_postgres_thread, thread_id)
        
        logger.info(f"Background task scheduled for thread_id: {thread_id}")
        
        return {
            "status": "success",
            "message": "Processing task has been added to the background.",
            "resolvedThreadId": thread_id
        }

    except ValueError as e:
        logger.error(f"Value error in webhook: {e}", exc_info=True)
        # Return a 404 if the record/thread is not found, which is appropriate.
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error in webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.") 