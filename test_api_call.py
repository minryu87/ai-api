import os
import requests
import json
import sys
from dotenv import load_dotenv

def test_naver_api_call(club_id, article_id):
    """
    주어진 club_id와 article_id를 사용하여 네이버 카페 API를 호출하고,
    성공 시 JSON 결과를 stdout으로 출력합니다.
    """
    # .env 파일 로드 (ai-api 폴더 기준)
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    naver_cookie = os.getenv('NAVER_COOKIE')

    if not naver_cookie or naver_cookie == "여기에_네이버_쿠키_값을_붙여넣으세요":
        print(f"오류: '{dotenv_path}' 파일에 유효한 NAVER_COOKIE 값이 설정되지 않았습니다.", file=sys.stderr)
        return

    # API 정보
    api_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v4/cafes/{club_id}/articles/{article_id}"
    
    headers = {
        'Cookie': naver_cookie
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        # 성공 시, 순수한 JSON 텍스트만 stdout으로 출력
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"JSON 파싱 오류. 응답 내용: {response.text}", file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("사용법: python test_api_call.py <club_id> <article_id>", file=sys.stderr)
        sys.exit(1)
        
    club_id_arg = sys.argv[1]
    article_id_arg = sys.argv[2]
    test_naver_api_call(club_id_arg, article_id_arg) 