import asyncio
from playwright.async_api import async_playwright, Browser, Page, Playwright

# 로컬 PC에서 디버깅 모드로 실행된 Chrome의 CDP 엔드포인트
CDP_ENDPOINT = "http://localhost:9222"

async def get_browser(playwright: Playwright) -> Browser:
    """실행 중인 Chrome 인스턴스에 연결합니다."""
    return await playwright.chromium.connect_over_cdp(CDP_ENDPOINT)

async def sync_cms_collection(page: Page, cms_url: str):
    """지정된 CMS 컬렉션 URL로 이동하여 Airtable과 동기화합니다."""
    print(f"CMS 컬렉션 동기화 시작: {cms_url}")
    try:
        await page.goto(cms_url, timeout=60000)
        await page.wait_for_load_state('domcontentloaded')

        # 'Sync with Airtable' 버튼 찾기 및 클릭
        sync_button_selector = "button:has-text('Sync with Airtable')"
        sync_button = page.locator(sync_button_selector).first
        await sync_button.wait_for(state='visible', timeout=30000)
        await sync_button.click()

        # 동기화 완료 메시지 대기 (타임아웃 3분)
        success_message_selector = "div:has-text('Synced with Airtable')"
        await page.locator(success_message_selector).wait_for(state='visible', timeout=180000)
        print(f"CMS 컬렉션 동기화 성공: {cms_url}")

    except Exception as e:
        print(f"오류 발생 ({cms_url}): {e}")
        raise

async def sync_all_cms(cms_urls: list[str]):
    """제공된 모든 CMS 컬렉션 URL을 동기화합니다."""
    async with async_playwright() as playwright:
        browser = await get_browser(playwright)
        # 이미 열려있는 브라우저의 기본 컨텍스트 사용
        context = browser.contexts[0]
        page = await context.new_page()

        try:
            for url in cms_urls:
                await sync_cms_collection(page, url)
            return {"status": "success", "message": "모든 CMS 컬렉션이 성공적으로 동기화되었습니다."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await page.close()


async def publish_site(page_url: str):
    """지정된 페이지 URL에서 사이트를 게시합니다."""
    async with async_playwright() as playwright:
        browser = await get_browser(playwright)
        context = browser.contexts[0]
        page = await context.new_page()

        print(f"페이지 게시 시작: {page_url}")
        try:
            await page.goto(page_url, timeout=60000)
            await page.wait_for_load_state('domcontentloaded')

            # 'Publish' 버튼 찾기
            publish_button_selector = "button:has-text('Publish')"
            publish_button = page.locator(publish_button_selector).first
            await publish_button.wait_for(state='visible', timeout=30000)
            await publish_button.click()

            # 확인 대화상자의 'Publish' 버튼 클릭
            confirm_publish_selector = "div[data-framer-name='Primary'] button:has-text('Publish')"
            confirm_button = page.locator(confirm_publish_selector)
            await confirm_button.wait_for(state='visible', timeout=30000)
            await confirm_button.click()

            # 게시 완료 메시지 대기 (타임아웃 3분)
            success_message_selector = "div:has-text('Published')"
            await page.locator(success_message_selector).wait_for(state='visible', timeout=180000)

            print("사이트 게시 성공.")
            return {"status": "success", "message": "사이트가 성공적으로 게시되었습니다."}
        except Exception as e:
            print(f"게시 중 오류 발생: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            await page.close() 