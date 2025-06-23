from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

# framer_service.py에서 자동화 함수 임포트
from framer_service import sync_all_cms, publish_site

app = FastAPI(
    title="Framer 자동화 로컬 API",
    description="로컬 PC에서 실행 중인 Chrome 브라우저에 연결하여 Framer 작업을 자동화하는 API입니다.",
    version="1.0.0"
)

class SyncRequest(BaseModel):
    cms_urls: List[str]

class PublishRequest(BaseModel):
    page_url: str

@app.post("/sync-cms")
async def handle_sync_cms(request: SyncRequest):
    """
    제공된 모든 CMS 컬렉션 URL을 Airtable과 동기화합니다.
    """
    try:
        print(f"CMS 동기화 요청 수신: {request.cms_urls}")
        result = await sync_all_cms(request.cms_urls)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        print(f"API 오류 발생 (sync-cms): {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/publish-site")
async def handle_publish_site(request: PublishRequest):
    """
    제공된 페이지 URL에서 사이트를 게시합니다.
    """
    try:
        print(f"사이트 게시 요청 수신: {request.page_url}")
        result = await publish_site(request.page_url)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        print(f"API 오류 발생 (publish-site): {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Framer 자동화 로컬 API 서버가 실행 중입니다. /docs 에서 API 문서를 확인하세요."}

if __name__ == "__main__":
    # Windows PC에서 실행하고 외부에서 접근할 수 있도록 host를 0.0.0.0으로 설정합니다.
    # 기존 서비스와 포트가 겹치지 않도록 8001 포트를 사용합니다.
    print("API 서버를 시작합니다. http://localhost:8001/docs 에서 문서를 확인하세요.")
    uvicorn.run(app, host="0.0.0.0", port=8001) 