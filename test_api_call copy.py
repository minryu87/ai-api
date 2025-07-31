import os
import requests
import json
from dotenv import load_dotenv

def test_naver_api_call():
    """
    네이버 카페 API를 테스트하기 위한 스크립트.
    .env 파일에서 NAVER_COOKIE를 로드하여 사용합니다.
    """
    # .env 파일 로드 (ai-api 폴더 기준)
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    naver_cookie = os.getenv('NAVER_COOKIE')

    if not naver_cookie or naver_cookie == "여기에_네이버_쿠키_값을_붙여넣으세요":
        print(f"오류: '{dotenv_path}' 파일에 유효한 NAVER_COOKIE 값이 설정되지 않았습니다.")
        return

    # API 정보
    api_url = "https://apis.naver.com/cafe-web/cafe-articleapi/v4/cafes/24660992/articles/2423758"
    
    # API 호출 시 Referer 헤더가 필요한 경우가 많습니다.
    # 게시글 ID를 기반으로 일반적인 네이버 카페 게시글 URL을 Referer로 설정합니다.
    article_id = api_url.split('/')[-1]
    referer_url = f"https://cafe.naver.com/any-cafe-name/{article_id}"

    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Cookie': naver_cookie
        # 'Referer': referer_url
    }

    print(f"API 요청을 보냅니다: {api_url}")
    print(f"Referer: {referer_url}")

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        # 응답 출력
        print(f"응답 코드: {response.status_code}")
        
        # JSON 응답 파싱 및 예쁘게 출력
        try:
            response_json = response.json()
            print("응답 JSON:")
            print(json.dumps(response_json, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print("JSON 파싱 오류. 응답 내용:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")

if __name__ == '__main__':
    test_naver_api_call() 