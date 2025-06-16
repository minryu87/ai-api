from fastapi import APIRouter, Query
from app.services.youtube_crawler import get_comment_list_api

router = APIRouter()

@router.get("/comments")
def get_comments(channel: str = Query(..., description="유튜브 채널명")):
    return get_comment_list_api(channel)
