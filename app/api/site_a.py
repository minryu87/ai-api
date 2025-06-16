from fastapi import APIRouter
from app.services.crawler_a import crawl_site_a

router = APIRouter()

@router.get("/crawl")
def crawl():
    return crawl_site_a()
