import asyncio
from playwright.async_api import async_playwright, expect
import json
import re
import os
import tempfile

# --- 설정 ---
CMS_URL = "https://framer.com/projects/Untitled--1NOQizSJV2Ha7dvLaS8H-MDNY9?node=BUWeLYKgl"
PUBLISH_URL = "https://framer.com/projects/Untitled--1NOQizSJV2Ha7dvLaS8H-MDNY9?node=augiA20Il"
# 시스템 임시 디렉토리에서 프로필 폴더 경로를 가져옴
AUTH_PROFILE_PATH = os.path.join(tempfile.gettempdir(), "framer_auth_profile")


async def navigate_and_verify(page, url: str, verification_locator):
    """
    지정된 URL로 이동하고, 특정 요소가 나타나는지 확인하여 로딩을 검증합니다.
    실패 시 한 번 새로고침하여 재시도합니다.
    """
    for i in range(2):  # 최대 2번 시도 (첫 시도 + 재시도 1번)
        try:
            if i == 0:
                print(f"➡️ 페이지로 이동 시작: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            else:
                print("⏳ 페이지 로딩 재시도: 새로고침합니다...")
                await page.reload(wait_until="domcontentloaded", timeout=60000)

            # 페이지 로딩 검증: 핵심 요소가 보이는지 확인
            await expect(verification_locator).to_be_visible(timeout=30000)
            print(f"✅ 페이지 로딩 확인 완료: {url}")
            return  # 성공 시 함수 종료
        except Exception as e:
            print(f"- {i + 1}차 시도 실패: 페이지 로딩 중 오류 발생.")
            if i < 1:  # 마지막 시도가 아니라면 계속
                continue
            else:  # 최종 실패 시 에러 발생
                print(f"🚨 페이지 로딩 최종 실패: {url}")
                raise e


async def main():
    """
    저장된 인증 프로필을 사용하여 Framer CMS 동기화 및 페이지 게시를 자동화합니다.
    """
    async with async_playwright() as p:
        # 1. 저장된 인증 프로필로 브라우저 컨텍스트 실행
        try:
            context = await p.chromium.launch_persistent_context(
                AUTH_PROFILE_PATH,
                headless=False, # 자동화 과정을 보려면 False, 서버에서는 True
            )
            print(f"✅ 인증 프로필 '{AUTH_PROFILE_PATH}'을(를) 사용하여 브라우저를 시작합니다.")
        except Exception as e:
            print(f"🚨 에러: 인증 프로필 '{AUTH_PROFILE_PATH}'을(를) 로드할 수 없습니다.")
            print("먼저 'create_auth_profile.py'를 실행하여 프로필을 생성했는지 확인해주세요.")
            print(f"자세한 오류: {e}")
            return

        # --- 작업 1: CMS 동기화 ---
        print("\n--- 🚀 작업 1: CMS 동기화 시작 ---")
        cms_page = await context.new_page()
        try:
            # 안정적인 페이지 이동 및 검증
            sync_button = cms_page.locator('div[role="button"][title="Sync"]')
            await navigate_and_verify(cms_page, CMS_URL, sync_button)

            # 'Sync' 버튼 클릭
            await sync_button.click()
            print("🖱️ 'Sync' 버튼을 클릭했습니다.")

            # 성공 메시지 확인 (가장 단순한 형태로 변경)
            await expect(cms_page.get_by_text("Success")).to_be_visible(timeout=30000)
            print("✅ 동기화 성공 메시지를 확인했습니다!")

        except Exception as e:
            print(f"🚨 CMS 동기화 중 오류 발생: {e}")
            await cms_page.screenshot(path="ai-api/tests/error_cms_sync.png")
            print("📷 오류 발생 시점의 스크린샷을 'error_cms_sync.png'로 저장했습니다.")
        finally:
            await cms_page.close()


        # --- 작업 2: 페이지 게시 ---
        print("\n--- 🚀 작업 2: 페이지 게시 시작 ---")
        publish_page = await context.new_page()
        try:
            # 안정적인 페이지 이동 및 검증
            publish_button = publish_page.locator('button#toolbar-publish-button')
            await navigate_and_verify(publish_page, PUBLISH_URL, publish_button)

            # 'Publish' 버튼 클릭
            await publish_button.click()
            print("🖱️ 'Publish' 버튼을 클릭했습니다.")

            try:
                # 'Update' 버튼이 있는 모달을 찾아 클릭
                update_button = publish_page.locator('div[role="dialog"] button[title="Update"]')
                # 모달이 나타날 때까지 짧게 대기
                await expect(update_button).to_be_visible(timeout=5000) 
                await update_button.click()
                print("🖱️ 모달의 'Update' 버튼을 클릭했습니다.")
                
                # 성공 확인: 게시 완료 후 나타나는 텍스트 확인 (가장 단순한 형태로 변경)
                await expect(publish_page.get_by_text("ago")).to_be_visible(timeout=30000)
                print("✅ 게시 완료 후 상태 변경을 확인하여 게시 성공!")
            except Exception:
                print("ℹ️ 'Update' 모달이 나타나지 않았습니다. 게시할 변경 사항이 없는 것으로 간주하고 건너뜁니다.")
                # 이 경우는 오류가 아니므로 그대로 통과

        except Exception as e:
            print(f"🚨 페이지 게시 중 오류 발생: {e}")
            await publish_page.screenshot(path="ai-api/tests/error_page_publish.png")
            print("📷 오류 발생 시점의 스크린샷을 'error_page_publish.png'로 저장했습니다.")
        finally:
            await publish_page.close()


        # --- 마무리 ---
        await context.close()
        print("\n🎉 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    # Playwright가 처음이라면 필요한 브라우저를 설치해야 합니다.
    # 터미널에서 `playwright install` 명령을 실행하세요.
    asyncio.run(main()) 