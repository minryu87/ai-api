from fastapi import APIRouter, Query
from app.services.youtube_crawler import get_video_list_api

router = APIRouter()

@router.get("/videos")
def get_videos(channel: str = Query(..., description="유튜브 채널명")):
    return get_video_list_api(channel)
