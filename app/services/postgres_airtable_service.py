from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.airtable_service import table_relevance
from app.models.airtable import IntegratedText, Comment, Reply
import logging

logger = logging.getLogger(__name__)

# --- Database Setup ---
try:
    engine = create_engine(
        "postgresql+psycopg2://",
        connect_args={
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "dbname": settings.DB_NAME,
            "sslmode": "require",
        },
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully using connect_args.")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}", exc_info=True)
    engine = None
    SessionLocal = None

def get_db():
    if SessionLocal is None:
        logger.error("Database session is not initialized. Cannot get DB session.")
        raise ConnectionError("Database connection not established.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_thread_data_from_postgres(thread_id: str):
    """
    Postgres DB에서 thread_id를 기반으로 데이터를 조회하고 통합합니다.
    """
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 1. 스레드 및 관련 메타데이터 조회
        main_query = text("""
            SELECT
                t.id AS "threadId",
                t.title,
                t.content AS "threadText",
                t.author,
                t.author_at AS "publishedAt",
                t.thread_url AS link,
                s.store_name AS "clientName",
                c.community_name AS community,
                c.channel_id AS channel
            FROM
                thread t
            JOIN
                community c ON t.community_id = c.id
            LEFT JOIN
                store_community sc ON c.id = sc.community_id
            LEFT JOIN
                store s ON sc.store_id = s.id
            WHERE
                t.id = :thread_id
        """)
        thread_record = db.execute(main_query, {"thread_id": thread_id}).mappings().first()

        if not thread_record:
            raise ValueError(f"Thread not found in PostgreSQL: {thread_id}")

        # 2. 댓글 조회
        comments_query = text("""
            SELECT
                id AS "threadCommentId",
                content AS "commentText",
                author,
                author_at AS "publishedAt"
            FROM
                thread_comment
            WHERE
                thread_id = :thread_id
            ORDER BY "publishedAt"
        """)
        comments_result = db.execute(comments_query, {"thread_id": thread_id}).mappings().all()

        # 3. 대댓글 조회
        replies_query = text("""
            SELECT
                r.thread_comment_id AS "threadCommentId",
                r.content AS "replyText",
                r.author,
                r.author_at AS "publishedAt"
            FROM
                thread_reply r
            JOIN
                thread_comment c ON r.thread_comment_id = c.id
            WHERE
                c.thread_id = :thread_id
            ORDER BY "publishedAt"
        """)
        replies_result = db.execute(replies_query, {"thread_id": thread_id}).mappings().all()

        replies_map = {}
        for reply in replies_result:
            comment_id = reply['threadCommentId']
            if comment_id not in replies_map:
                replies_map[comment_id] = []
            replies_map[comment_id].append(Reply(**reply))

        comments_list = []
        for comm in comments_result:
            comment_id = comm['threadCommentId']
            comments_list.append(Comment(
                **comm,
                replies=replies_map.get(comment_id, [])
            ))

        return thread_record, comments_list

    finally:
        next(db_gen, None)


def process_and_save_postgres_thread(thread_id: str):
    """
    Postgres에서 데이터를 가져와 처리하고 Airtable에 저장/업데이트합니다.
    """
    logger.info(f"Processing data from PostgreSQL for threadId: {thread_id}")

    thread_record, comments_list = get_thread_data_from_postgres(thread_id)

    # integratedText JSON 구조 생성
    integrated_text_obj = IntegratedText(
        author=thread_record['author'],
        publishedAt=thread_record['publishedAt'],
        threadText=thread_record['threadText'],
        comments=comments_list
    )

    # Airtable에 저장할 데이터 준비
    data_for_airtable = {
        'threadId': thread_id,
        'clientName': thread_record.get('clientName'),
        'channel': thread_record.get('channel'),
        'community': thread_record.get('community'),
        'title': thread_record.get('title'),
        'postedAt': thread_record.get('publishedAt').isoformat() if thread_record.get('publishedAt') else None,
        'link': thread_record.get('link'),
        'integratedText': integrated_text_obj.model_dump_json(indent=2),
    }

    # 최종 테이블에 저장 또는 업데이트
    existing_record = table_relevance.first(formula=f"{{threadId}} = '{thread_id}'")
    if existing_record:
        logger.info(f"Updating existing Airtable record for threadId: {thread_id}")
        table_relevance.update(existing_record['id'], data_for_airtable)
        record_id = existing_record['id']
    else:
        logger.info(f"Creating new Airtable record for threadId: {thread_id}")
        new_record = table_relevance.create(data_for_airtable)
        record_id = new_record['id']

    logger.info(f"Successfully processed and saved data from PostgreSQL for threadId: {thread_id}. Airtable Record ID: {record_id}")

    # API 응답으로 반환할 데이터 준비
    final_data = {
        'id': record_id,
        **data_for_airtable,
        'integratedText': integrated_text_obj,  # Pydantic 객체로 반환
        'createdAt': table_relevance.get(record_id).get('createdTime')
    }
    return final_data 