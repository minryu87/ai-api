import asyncio
from playwright.async_api import async_playwright
import os
import shutil
import tempfile

# --- 설정 ---
# 시스템 임시 디렉토리에 프로필 폴더 경로를 생성
AUTH_PROFILE_PATH = os.path.join(tempfile.gettempdir(), "framer_auth_profile")
# 로컬에서 실행 중인 Chrome의 디버깅 포트
CHROME_REMOTE_DEBUGGING_PORT = 9222
START_URL = "https://framer.com"

async def main():
    """
    실행 중인 로컬 Chrome 브라우저에 연결하여,
    시스템 임시 폴더에 인증 정보가 포함된 영구 브라우저 프로필을 생성합니다.
    """
    # 기존 프로필 폴더가 있다면 삭제하여 깨끗한 상태에서 시작
    if os.path.exists(AUTH_PROFILE_PATH):
        print(f"기존 인증 프로필 폴더 '{AUTH_PROFILE_PATH}'를 삭제합니다.")
        shutil.rmtree(AUTH_PROFILE_PATH)

    print(f"인증 프로필 생성을 시작합니다. 저장될 폴더: '{AUTH_PROFILE_PATH}'")
    
    try:
        async with async_playwright() as p:
            # 실행 중인 Chrome에 연결합니다.
            browser = await p.chromium.connect_over_cdp(
                f"http://localhost:{CHROME_REMOTE_DEBUGGING_PORT}"
            )
            # 기본 컨텍스트를 가져옵니다. 이 컨텍스트에 모든 로그인 정보가 담겨있습니다.
            default_context = browser.contexts[0]

            # 이 컨텍스트의 상태를 새 프로필 폴더에 저장합니다.
            await default_context.storage_state(path=AUTH_PROFILE_PATH)

            print(f"\n--- ➡️ [사용자 확인 필요] ⬅️ ---")
            print(f"연결된 Chrome 브라우저에서 다음 작업을 직접 수행해주세요:")
            print(f"1. Framer ({START_URL})에 구글 계정으로 로그인하세요.")
            print(f"2. Airtable.com 에도 로그인하세요.")
            print(f"3. CMS 페이지로 이동하여 Airtable 연동이 정상적인지 최종 확인하세요.")
            print(f"4. 모든 작업이 완료되었으면, 이 터미널에서 'Enter' 키를 눌러주세요.")
            print(f"---------------------------------")
            
            # 사용자가 Enter를 누를 때까지 대기
            await asyncio.to_thread(input)

            # 변경된 최신 상태를 다시 저장
            await default_context.storage_state(path=AUTH_PROFILE_PATH)

    except Exception as e:
        print(f"\n🚨 오류 발생: Chrome 브라우저에 연결할 수 없습니다.")
        print(f"Chrome이 원격 디버깅 모드(port={CHROME_REMOTE_DEBUGGING_PORT})로 실행 중인지 확인해주세요.")
        print(f"자세한 오류: {e}")
        return

    print(f"\n✅ 인증 프로필 생성이 완료되었습니다. '{AUTH_PROFILE_PATH}' 폴더를 확인하세요.")
    print("이제 'local_framer_test.py'를 실행하여 자동화를 테스트할 수 있습니다.")


if __name__ == "__main__":
    asyncio.run(main()) 