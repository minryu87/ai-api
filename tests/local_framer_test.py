import asyncio
from playwright.async_api import async_playwright, expect
import re
import time

# --- 설정 ---
CHROME_REMOTE_DEBUGGING_PORT = 9222 # 로컬에서 실행 중인 Chrome의 디버깅 포트

CMS_URLS = [
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=uZl23C8TF",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=CK____iw6",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=kiYmEJlyL",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=G4ho77AUd",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=T10UHkSJk",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=c1kzdpJ1X",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=MYt22OJS2",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=cSF8hFL1P",
    "https://framer.com/projects/Tt9IX0zzbHWD7ghzKyjk-bfrUp?node=smPaW2mIN",
]

# Publish는 첫 번째 CMS URL에서 한 번만 수행
PUBLISH_URL = CMS_URLS[0]

# 긴 작업에 대한 타임아웃 (단위: 밀리초, 180초 = 3분)
LONG_TIMEOUT = 180 * 1000 


async def navigate_and_verify(page, url: str, verification_locator):
    """
    지정된 URL로 이동하고, 특정 요소가 나타나는지 확인하여 로딩을 검증합니다.
    실패 시 한 번 새로고침하여 재시도합니다.
    """
    for i in range(2):
        try:
            if i == 0:
                print(f"➡️ 페이지로 이동 시작: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            else:
                print("⏳ 페이지 로딩 재시도: 새로고침합니다...")
                await page.reload(wait_until="domcontentloaded", timeout=60000)

            await expect(verification_locator).to_be_visible(timeout=30000)
            print(f"✅ 페이지 로딩 확인 완료: {url}")
            return
        except Exception as e:
            print(f"- {i + 1}차 시도 실패: 페이지 로딩 중 오류 발생.")
            if i < 1:
                continue
            else:
                print(f"🚨 페이지 로딩 최종 실패: {url}")
                raise e

async def run_cms_sync(page, url):
    """지정된 URL 페이지에서 CMS 동기화 작업을 수행합니다."""
    print(f"\n--- 🔄 CMS 동기화 작업 시작: {url} ---")
    sync_button = page.locator('div[role="button"][title="Sync"]')
    await navigate_and_verify(page, url, sync_button)
    
    await sync_button.click()
    print("🖱️ 'Sync' 버튼을 클릭했습니다.")

    await expect(page.get_by_text("Success")).to_be_visible(timeout=LONG_TIMEOUT)
    print("✅ 동기화 성공 메시지를 확인했습니다!")

async def run_site_publish(page, url):
    """지정된 URL 페이지에서 사이트 게시 작업을 수행합니다."""
    print(f"\n--- 🚀 사이트 게시 작업 시작: {url} ---")
    publish_button = page.locator('button#toolbar-publish-button')
    await navigate_and_verify(page, url, publish_button)
    
    await publish_button.click()
    print("🖱️ 'Publish' 버튼을 클릭했습니다.")

    try:
        update_button = page.locator('button[title="Update"]')
        await expect(update_button).to_be_visible(timeout=15000)
        await update_button.click()
        print("🖱️ 모달의 'Update' 버튼을 클릭했습니다.")
        
        await expect(page.get_by_text("ago")).to_be_visible(timeout=LONG_TIMEOUT)
        print("✅ 게시 완료 후 상태 변경을 확인하여 게시 성공!")
    except Exception:
        print("ℹ️ 'Update' 모달이 나타나지 않았습니다. 게시할 변경 사항이 없는 것으로 간주하고 건너뜁니다.")


async def main():
    """
    실행 중인 Chrome 브라우저에 연결하여 여러 CMS 페이지를 동기화하고 최종적으로 사이트를 게시합니다.
    """
    start_time = time.time()
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(f"http://localhost:{CHROME_REMOTE_DEBUGGING_PORT}")
            context = browser.contexts[0]
            page = await context.new_page()
            print(f"✅ 실행 중인 Chrome 브라우저(port={CHROME_REMOTE_DEBUGGING_PORT})에 성공적으로 연결했습니다.")
        except Exception as e:
            print(f"🚨 에러: 실행 중인 Chrome 브라우저에 연결할 수 없습니다.")
            print(f"Chrome이 원격 디버깅 모드(port={CHROME_REMOTE_DEBUGGING_PORT})로 실행 중인지 확인해주세요.")
            return

        try:
            # 1. 모든 CMS 페이지 순차적으로 동기화
            for i, url in enumerate(CMS_URLS):
                await run_cms_sync(page, url)
                print(f"--- ({i+1}/{len(CMS_URLS)}) CMS 동기화 완료 ---")

            # 2. 모든 동기화 완료 후 사이트 게시
            await run_site_publish(page, PUBLISH_URL)

        except Exception as e:
            print(f"\n🚨🚨🚨 작업 중 심각한 오류가 발생하여 중단되었습니다: {e}")
            await page.screenshot(path="ai-api/tests/error_screenshot.png")
            print("📷 오류 발생 시점의 스크린샷을 'error_screenshot.png'로 저장했습니다.")
        finally:
            if not page.is_closed():
                await page.close()
            await context.close()
            await browser.close()

    end_time = time.time()
    print(f"\n🎉 모든 작업이 완료되었습니다. (총 소요 시간: {end_time - start_time:.2f}초)")


if __name__ == "__main__":
    asyncio.run(main()) 