from pyairtable import Api
from app.config import settings
from app.models.airtable import IntegratedText, Comment, Reply
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Airtable API 클라이언트 초기화
api = Api(settings.AIRTABLE_API_KEY)
base = api.base(settings.AIRTABLE_BASE_ID)

# 테이블 객체
table_thread = base.table(settings.AIRTABLE_CAFE_THREAD_TABLE_NAME)
table_comment = base.table(settings.AIRTABLE_CAFE_THREAD_COMMENT_TABLE_NAME)
table_reply = base.table(settings.AIRTABLE_CAFE_THREAD_REPLY_TABLE_NAME)
table_relevance = base.table(settings.AIRTABLE_CAFE_THREAD_RELEVANCE_TABLE_NAME)


def get_thread_id_from_record(record_id: str, table_name: str) -> str:
    """
    어떤 테이블의 레코드 ID가 주어졌을 때, 최상위 threadId를 찾아서 반환합니다.
    """
    target_table = base.table(table_name)
    record = target_table.get(record_id)
    
    if not record:
        raise ValueError(f"Record {record_id} not found in table {table_name}")

    fields = record.get('fields', {})

    if 'threadId' in fields:
        return fields['threadId']
    elif 'threadCommentId' in fields:
        comment_id = fields['threadCommentId']
        comment_record = table_comment.first(formula=f"{{threadCommentId}} = '{comment_id}'")
        if not comment_record:
            raise ValueError(f"Comment record for {comment_id} not found")
        return comment_record.get('fields', {}).get('threadId')
    
    raise ValueError("Could not determine threadId from the provided record")


def process_and_save_thread_data(thread_id: str):
    """
    주어진 thread_id를 기반으로 데이터를 통합하고 최종 테이블에 저장/업데이트합니다.
    """
    logger.info(f"Processing data for threadId: {thread_id}")

    # 1. 스레드(게시글) 데이터 가져오기
    thread_record = table_thread.first(formula=f"{{threadId}} = '{thread_id}'")
    if not thread_record:
        logger.error(f"Thread record not found for threadId: {thread_id}")
        raise ValueError(f"Thread not found: {thread_id}")

    thread_fields = thread_record.get('fields', {})
    thread_text = thread_fields.get('글 내용', '')
    thread_author = thread_fields.get('작성자 닉네임', '')
    thread_published_at = thread_fields.get('작성 시점', '')

    # 2. 댓글 및 대댓글 데이터 가져오기 및 구조화
    comments_data = table_comment.all(formula=f"{{threadId}} = '{thread_id}'")
    
    comments_list = []
    for comm_record in comments_data:
        comm_fields = comm_record.get('fields', {})
        comment_id = comm_fields.get('threadCommentId')
        
        replies_data = table_reply.all(formula=f"{{threadCommentId}} = '{comment_id}'")
        
        replies_list = [Reply(
            author=rep.get('fields', {}).get('작성자 닉네임', ''),
            publishedAt=rep.get('fields', {}).get('작성 시점', ''),
            replyText=rep.get('fields', {}).get('대댓글 내용', '')
        ) for rep in replies_data]

        comments_list.append(Comment(
            author=comm_fields.get('작성자 닉네임', ''),
            publishedAt=comm_fields.get('작성 시점', ''),
            commentText=comm_fields.get('댓글 내용', ''),
            replies=replies_list
        ))

    # 3. integratedText JSON 구조 생성
    integrated_text_obj = IntegratedText(
        author=thread_author,
        publishedAt=thread_published_at,
        threadText=thread_text,
        comments=comments_list
    )

    # 4. Airtable에 저장할 데이터 준비 (JSON 문자열 사용)
    data_for_airtable = {
        'threadId': thread_id,
        'clientName': thread_fields.get('병원'),
        'channel': thread_fields.get('채널'),
        'community': thread_fields.get('커뮤니티 이름'),
        'title': thread_fields.get('글 제목'),
        'postedAt': thread_fields.get('작성 시점'),
        'link': thread_fields.get('링크'),
        'integratedText': integrated_text_obj.model_dump_json(indent=2),
    }

    # 5. 최종 테이블에 저장 또는 업데이트
    existing_record = table_relevance.first(formula=f"{{threadId}} = '{thread_id}'")
    if existing_record:
        logger.info(f"Updating existing record for threadId: {thread_id}")
        table_relevance.update(existing_record['id'], data_for_airtable)
        record_id = existing_record['id']
    else:
        logger.info(f"Creating new record for threadId: {thread_id}")
        new_record = table_relevance.create(data_for_airtable)
        record_id = new_record['id']

    logger.info(f"Successfully processed and saved data for threadId: {thread_id}. Record ID: {record_id}")
    
    # 6. API 응답으로 반환할 데이터 준비 (Pydantic 객체 사용)
    data_to_return = {
        'id': record_id,
        'threadId': thread_id,
        'clientName': thread_fields.get('병원'),
        'channel': thread_fields.get('채널'),
        'community': thread_fields.get('커뮤니티 이름'),
        'title': thread_fields.get('글 제목'),
        'postedAt': thread_fields.get('작성 시점'),
        'link': thread_fields.get('링크'),
        'integratedText': integrated_text_obj, # Pydantic 객체를 그대로 사용
        'createdAt': table_relevance.get(record_id).get('fields', {}).get('createdAt')
    }
    return data_to_return 