from fastapi import APIRouter
from app.services.crawler_b import crawl_site_b

router = APIRouter()

@router.get("/crawl")
def crawl():
    return crawl_site_b()
