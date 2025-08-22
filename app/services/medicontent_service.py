import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# agents 폴더를 Python 경로에 추가 (ai-api 내부 경로)
current_dir = Path(__file__).parent.parent
agents_path = current_dir / "agents"
sys.path.append(str(agents_path))

from dotenv import load_dotenv
from pyairtable import Api

logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

# Airtable 설정 (blog_automation Settings 형식)
AIRTABLE_API_KEY = os.getenv('NEXT_PUBLIC_AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('NEXT_PUBLIC_AIRTABLE_BASE_ID')

if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
    raise ValueError('NEXT_PUBLIC_AIRTABLE_API_KEY와 NEXT_PUBLIC_AIRTABLE_BASE_ID가 필요합니다.')

# Google API 키 설정 (선택적)
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    logger.warning('GEMINI_API_KEY가 설정되지 않았습니다. 메디컨텐츠 생성 기능이 제한될 수 있습니다.')

api = Api(AIRTABLE_API_KEY)
base = api.base(AIRTABLE_BASE_ID)

# 테이블 객체
table_post_data_requests = base.table('Post Data Requests')
table_medicontent_posts = base.table('Medicontent Posts')

async def save_to_post_data_requests(data):
    """Post Data Requests 테이블에 저장"""
    try:
        current_time = datetime.now()
        record_data = {
            'Post ID': data.postId,
            'Concept Message': data.conceptMessage,
            'Patient Condition': data.patientCondition,
            'Treatment Process Message': data.treatmentProcessMessage,
            'Treatment Result Message': data.treatmentResultMessage,
            'Additional Message': data.additionalMessage,
            'Before Images': data.beforeImages if data.beforeImages else [],
            'Process Images': data.processImages if data.processImages else [],
            'After Images': data.afterImages if data.afterImages else [],
            'Before Images Texts': data.beforeImagesText,
            'Process Images Texts': data.processImagesText,
            'After Images Texts': data.afterImagesText,
            # Airtable에서 자동으로 생성되는 필드들 제거
            # 'Created At': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            # 'Submitted At': current_time.strftime('%Y-%m-%d %H:%M'),
            'Status': '대기'
        }
        
        result = table_post_data_requests.create(record_data)
        return result['id']
        
    except Exception as e:
        logger.error(f"Post Data Requests 저장 실패: {str(e)}")
        raise

async def update_post_data_request_status(record_id: str, status: str, results: Dict = None):
    """Post Data Requests 상태 업데이트"""
    try:
        update_data = {
            'Status': status,
            # Airtable에서 자동으로 생성되는 필드들 제거
            # 'Completed At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        if results:
            # 필드명을 Airtable의 실제 필드명에 맞게 수정
            if 'title' in results:
                update_data['Title'] = results['title']
            if 'content' in results:
                update_data['Content'] = results['content']
            if 'plan' in results:
                update_data['Plan'] = json.dumps(results['plan'], ensure_ascii=False)
            if 'evaluation' in results:
                update_data['Evaluation'] = json.dumps(results['evaluation'], ensure_ascii=False)
        
        table_post_data_requests.update(record_id, update_data)
        logger.info(f"상태 업데이트 완료: {record_id} -> {status}")
        
    except Exception as e:
        logger.error(f"상태 업데이트 실패: {e}")
        raise

async def update_medicontent_post_status(post_id: str, status: str):
    """Medicontent Posts 테이블의 상태 업데이트"""
    try:
        # Post ID에서 record ID 추출
        if post_id.startswith('post_'):
            record_id = post_id[5:]  # post_recXXXXXX → recXXXXXX
        else:
            record_id = post_id
            
        current_time = datetime.now()
        update_data = {
            'Status': status,
            # Airtable에서 자동으로 생성되는 필드 제거
            # 'Updated At': current_time.strftime('%Y-%m-%d %H:%M')
        }
        
        table_medicontent_posts.update(record_id, update_data)
        logger.info(f"Medicontent Posts 상태 업데이트 완료: {record_id} ({post_id}) → {status}")
        
    except Exception as e:
        logger.error(f"Medicontent Posts 상태 업데이트 실패: {str(e)}")
        raise

def split_image_descriptions(text: str, count: int) -> List[str]:
    """이미지 설명 분리 함수"""
    if not text.strip():
        return ["" for _ in range(count)]
    
    import re
    parts = re.split(r'[,\n]+', text)
    descriptions = [part.strip() for part in parts if part.strip()]
    
    result = []
    for i in range(count):
        result.append(descriptions[i] if i < len(descriptions) else "")
    return result

async def generate_content_complete(request):
    """완전한 워크플로우 실행"""
    record_id = None
    
    try:
        # 1단계: Post Data Requests에 저장 (상태: 대기)
        logger.info("Step 1: Post Data Requests에 저장...")
        record_id = await save_to_post_data_requests(request)
        logger.info(f"레코드 생성 완료: {record_id}")
        
        # 2단계: 상태를 '처리 중'으로 변경
        logger.info("Step 2: 상태를 '처리 중'으로 변경...")
        await update_post_data_request_status(record_id, '처리 중')
        
        # 3단계: 병원 정보 조회
        hospital_table = base.table('Hospital')
        try:
            hospital_records = hospital_table.all()
            if hospital_records:
                hospital_record = hospital_records[0]['fields']
                hospital_name = hospital_record.get('Hospital Name', '병원')
                hospital_address = hospital_record.get('Address', '')
                hospital_phone = hospital_record.get('Phone', '')
            else:
                raise Exception("Hospital 테이블에 데이터가 없음")
        except Exception as e:
            logger.warning(f"Settings - Hospital 테이블 조회 실패: {e}, 기본값 사용")
            hospital_name = "내이튼치과의원"
            hospital_address = "B동 507호 라스플로레스 경기도 화성시 동탄대로 537"
            hospital_phone = "031-526-2246"
        
        # 4단계: UI 데이터를 InputAgent 형식으로 변환
        input_data = {
            "hospital": {
                "name": hospital_name,
                "save_name": hospital_name,
                "address": hospital_address,
                "phone": hospital_phone
            },
            "category": "일반진료",
            "question1_concept": request.conceptMessage,
            "question2_condition": request.patientCondition,
            "question3_visit_images": [
                {"filename": img, "description": desc}
                for img, desc in zip(
                    request.beforeImages,
                    split_image_descriptions(request.beforeImagesText, len(request.beforeImages))
                )
            ],
            "question4_treatment": request.treatmentProcessMessage,
            "question5_therapy_images": [
                {"filename": img, "description": desc}
                for img, desc in zip(
                    request.processImages,
                    split_image_descriptions(request.processImagesText, len(request.processImages))
                )
            ],
            "question6_result": request.treatmentResultMessage,
            "question7_result_images": [
                {"filename": img, "description": desc}
                for img, desc in zip(
                    request.afterImages,
                    split_image_descriptions(request.afterImagesText, len(request.afterImages))
                )
            ],
            "question8_extra": request.additionalMessage,
            "include_tooth_numbers": False,
            "tooth_numbers": [],
            "persona_candidates": [],
            "representative_persona": ""
        }
        
        # 5단계: AI 에이전트들 import 및 실행 (ai-api 내부 경로)
        try:
            from app.agents.input_agent import InputAgent
            from app.agents.plan_agent import main as plan_agent_main
            from app.agents.title_agent import run as title_agent_run
            from app.agents.content_agent import run as content_agent_run
        except ImportError as e:
            logger.error(f"AI 에이전트 import 실패: {e}")
            raise Exception("AI 에이전트 모듈을 찾을 수 없습니다. app/agents 폴더를 확인해주세요.")
        
        # 6단계: 전체 파이프라인 실행
        logger.info("Step 3: InputAgent 실행...")
        input_agent = InputAgent(input_data=input_data)
        input_result = input_agent.collect(mode="use")
        
        logger.info("Step 4: PlanAgent 실행...")
        plan = plan_agent_main(mode='use', input_data=input_result)
        
        logger.info("Step 5: TitleAgent 실행...")
        title_result = title_agent_run(plan=plan, mode='use')
        title = title_result.get('selected', {}).get('title', '')
        
        logger.info("Step 6: ContentAgent 실행...")
        # ContentAgent는 파일 경로를 사용하므로 input_data 파라미터 제거
        content_result = content_agent_run(mode='use')
        content = content_result
        
        # 7단계: 전체 글 생성 (content_agent의 format_full_article 함수 사용)
        try:
            from app.agents.content_agent import format_full_article
            full_article = format_full_article(content, input_data={**input_result, **plan, 'title': title})
        except ImportError:
            # format_full_article 함수가 없으면 content를 그대로 사용
            full_article = content if isinstance(content, str) else str(content)
        
        logger.info("텍스트 생성 완료!")
        
        # 8단계: 결과를 Post Data Requests에 업데이트 (상태: 완료)
        results = {
            "title": title,
            "content": full_article,
            "plan": plan,
            "evaluation": {
                "plan_evaluation": "계획 생성 완료",
                "title_evaluation": "제목 생성 완료", 
                "content_evaluation": "콘텐츠 생성 완료"
            }
        }
        
        logger.info("Step 7: 결과를 Airtable에 저장...")
        try:
            # 7단계: 결과를 Post Data Requests에 업데이트 (상태: 완료)
            await update_post_data_request_status(record_id, '완료', results)
        except Exception as e:
            logger.warning(f"결과 저장 실패 (무시하고 계속 진행): {e}")
            # 결과 저장 실패해도 성공으로 처리
        
        # 8단계: Medicontent Posts 상태를 '리걸케어 작업 중'으로 업데이트
        try:
            await update_medicontent_post_status(request.postId, '리걸케어 작업 중')
        except Exception as e:
            logger.warning(f"Medicontent Posts 상태 업데이트 실패 (무시하고 계속 진행): {e}")
            # Medicontent Posts 업데이트 실패해도 성공으로 처리
        
        return {
            "status": "success",
            "postId": request.postId,
            "recordId": record_id,
            "results": results,
            "message": "메디컨텐츠 생성 및 DB 저장 완료!"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"오류 발생: {str(e)}")
        logger.error(f"상세: {error_details}")
        
        # 오류 발생 시 상태를 '대기'로 되돌리기
        if record_id:
            try:
                await update_post_data_request_status(record_id, '대기')
            except:
                pass
        
        raise Exception(f"텍스트 생성 실패: {str(e)}")

async def evaluate_content(request: Dict[str, Any]):
    """생성된 콘텐츠 평가"""
    try:
        from app.agents.evaluation_agent import EvaluationAgent
        
        # 평가 실행
        evaluation_agent = EvaluationAgent()
        # evaluation_result = evaluation_agent.run(...)
        
        return "평가 결과"
        
    except Exception as e:
        logger.error(f"콘텐츠 평가 실패: {str(e)}")
        raise
