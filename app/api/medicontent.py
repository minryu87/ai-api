from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.medicontent_service import (
    save_to_post_data_requests,
    update_post_data_request_status,
    update_medicontent_post_status,
    generate_content_complete,
    evaluate_content
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 요청 모델 (Post Data Requests 테이블 구조와 일치)
class ContentGenerationRequest(BaseModel):
    postId: str  # Medicontent Posts에서 가져온 Post ID
    conceptMessage: str = ""  # 질환 개념 강조 메시지
    patientCondition: str = ""  # 내원 시 환자 상태
    treatmentProcessMessage: str = ""  # 치료 과정 강조 메시지
    treatmentResultMessage: str = ""  # 치료 결과 강조 메시지
    additionalMessage: str = ""  # 추가 메시지
    beforeImages: List[str] = []  # 내원 시 사진 (attachment IDs)
    processImages: List[str] = []  # 치료 과정 사진 (attachment IDs)
    afterImages: List[str] = []  # 치료 결과 사진 (attachment IDs)
    beforeImagesText: str = ""  # 내원 시 사진 설명
    processImagesText: str = ""  # 치료 과정 사진 설명
    afterImagesText: str = ""  # 치료 결과 사진 설명

@router.post("/update-post-status")
async def update_post_status_endpoint(request: Dict[str, str]):
    """PostID 선택 시 Medicontent Posts 상태 업데이트"""
    try:
        post_id = request.get('postId')
        status = request.get('status', '병원 작업 중')
        
        logger.info(f"PostID 상태 업데이트: {post_id} → {status}")
        
        await update_medicontent_post_status(post_id, status)
        
        return {
            "status": "success",
            "message": f"상태가 '{status}'로 업데이트되었습니다.",
            "postId": post_id
        }
        
    except Exception as e:
        logger.error(f"상태 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="상태 업데이트에 실패했습니다.")

@router.post("/data-requests")
async def create_data_request(request: ContentGenerationRequest):
    """UI에서 자료 요청 데이터 저장 (Post Data Requests 테이블)"""
    try:
        logger.info(f"자료 요청 데이터 저장 시작: {request.postId}")
        
        # Post Data Requests 테이블에 저장
        record_id = await save_to_post_data_requests(request)
        
        logger.info(f"자료 요청 데이터 저장 완료: {record_id}")
        
        return {
            "status": "success", 
            "message": "자료 요청이 성공적으로 저장되었습니다.",
            "record_id": record_id,
            "postId": request.postId
        }
        
    except Exception as e:
        logger.error(f"자료 요청 저장 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="자료 요청 제출에 실패했습니다.")

@router.post("/generate-content-complete")
async def generate_content_complete_endpoint(request: ContentGenerationRequest):
    """완전한 워크플로우: UI 입력 → Post Data Requests 저장 → 텍스트 생성 → 결과 업데이트"""
    try:
        logger.info(f"콘텐츠 생성 시작: {request.postId}")
        
        result = await generate_content_complete(request)
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"콘텐츠 생성 실패: {str(e)}")
        logger.error(f"상세: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"텍스트 생성 실패: {str(e)}",
                "details": error_details
            }
        )

@router.post("/evaluate-content")
async def evaluate_content_endpoint(request: Dict[str, Any]):
    """생성된 콘텐츠 평가"""
    try:
        evaluation_result = await evaluate_content(request)
        
        return {
            "status": "success",
            "evaluation": evaluation_result,
            "message": "평가 완료"
        }
        
    except Exception as e:
        logger.error(f"콘텐츠 평가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-text-generation")
async def trigger_text_generation(request: Dict[str, str], background_tasks: BackgroundTasks):
    """텍스트 생성을 백그라운드에서 실행하도록 트리거"""
    try:
        post_id = request.get('postId')
        
        # 백그라운드 작업으로 텍스트 생성 실행
        background_tasks.add_task(generate_content_complete, post_id)
        
        return {
            "status": "success", 
            "message": "텍스트 생성이 백그라운드에서 시작되었습니다.",
            "postId": post_id
        }
        
    except Exception as e:
        logger.error(f"백그라운드 작업 트리거 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
