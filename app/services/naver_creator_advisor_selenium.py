import time
import calendar
import os
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm

# 로그인 세션을 저장할 프로필 경로 (프로젝트 루트에 'chrome_debug_profile' 폴더 생성)
PROFILE_PATH = "chrome_debug_profile"

# 크롬 드라이버 옵션 생성 함수
def get_chrome_options(headless=False):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-data-dir={PROFILE_PATH}')
    return options

def get_month_range(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    start = dt.replace(day=1)
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    end = dt.replace(day=last_day)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

# 최초 로그인용 브라우저 띄우기
def open_browser_for_login():
    print("크롬 브라우저가 열립니다. 네이버에 로그인 후, 창을 닫지 말고 엔터를 눌러주세요.")
    driver = webdriver.Chrome(options=get_chrome_options(headless=False))
    driver.get("https://naver.com")
    input("네이버 로그인을 완료했다면, 터미널에 엔터를 눌러주세요...")
    driver.quit()
    print("로그인 세션이 저장되었습니다. 이제 headless로 크롤링을 시작합니다.")

def _crawl_page_stats(driver, postId, date_for_month):
    """재사용 가능한 드라이버 인스턴스를 사용하여 한 페이지의 데이터를 크롤링합니다."""
    startDate, endDate = get_month_range(date_for_month)
    url = f"https://creator-advisor.naver.com/new-windows/article-stats?channelId=elza79&contentId=http%3A%2F%2Fblog.naver.com%2Felza79%2F{postId}&contentType=text-and-moment&endDate={endDate}&interval=month&service=naver_blog&startDate={startDate}"
    
    driver.get(url)
    time.sleep(3)  # JS 렌더링 대기, 필요시 시간 조절
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    results = []
    
    if "NCSO:GNB" in html or "로그인" in soup.title.text:
        tqdm.write(f"경고: 로그인 페이지로 리디렉션되었습니다. postId: {postId}, date: {startDate}. 세션 만료 가능성이 있습니다.")
        return []

    for li in soup.select("ul.u_ni_list.keyword_list li.u_ni_item"):
        title = li.select_one(".u_ni_title")
        value = li.select_one(".u_ni_value")
        if title and value:
            results.append({
                "postId": postId,
                "startDate": startDate,
                "endDate": endDate,
                "title": title.get_text(strip=True),
                "value": int(value.get_text(strip=True).replace(',', ''))
            })
    return results

def run_full_crawl():
    """CSV 파일을 읽어 모든 postId에 대해 월별로 반복하며 전체 데이터를 크롤링합니다."""
    print("전체 크롤링 작업을 시작합니다...")
    
    all_results = []
    input_csv_path = os.path.join("tests", "post-list.csv")
    output_csv_path = "creator_advisor_full_stats.csv"

    if not os.path.exists(input_csv_path):
        print(f"에러: 입력 CSV 파일을 찾을 수 없습니다. 경로: {os.path.abspath(input_csv_path)}")
        return

    df = pd.read_csv(input_csv_path)
    # # 앞에서 3개 postId만 사용하여 테스트
    # df = df.head(3).reset_index(drop=True)
    end_date_limit = datetime(2025, 6, 30)

    # 1. 총 크롤링할 페이지 수 계산
    total_pages = 0
    for index, row in df.iterrows():
        try:
            start_date = pd.to_datetime(row['date']).to_pydatetime()
            current_date = start_date.replace(day=1)
            while current_date <= end_date_limit:
                total_pages += 1
                current_date += relativedelta(months=1)
        except Exception:
            continue

    if total_pages == 0:
        print("크롤링할 페이지가 없습니다. 작업을 종료합니다.")
        return

    print(f"총 {len(df)}개의 포스트에 대해, {total_pages}개의 월별 페이지를 크롤링합니다.")
    options = get_chrome_options(headless=True)
    driver = webdriver.Chrome(options=options)
    
    try:
        with tqdm(total=total_pages, desc="전체 크롤링 진행률", unit="page") as pbar:
            for index, row in df.iterrows():
                postId = str(row['postId'])
                try:
                    start_date = pd.to_datetime(row['date']).to_pydatetime()
                except Exception as e:
                    tqdm.write(f"경고: postId {postId}의 날짜('{row['date']}') 형식이 잘못되어 건너뜁니다. 에러: {e}")
                    continue

                current_date = start_date.replace(day=1)
                
                while current_date <= end_date_limit:
                    date_str = current_date.strftime("%Y-%m-%d")
                    pbar.set_description(f"크롤링: {postId} ({current_date.strftime('%Y-%m')})")
                    monthly_results = _crawl_page_stats(driver, postId, date_str)
                    if monthly_results:
                        all_results.extend(monthly_results)
                    
                    pbar.update(1)
                    current_date += relativedelta(months=1)
        
        print("\n모든 크롤링이 완료되었습니다. 결과를 파일에 저장합니다...")
        if all_results:
            results_df = pd.DataFrame(all_results)
            results_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
            print(f"성공: 총 {len(all_results)}개의 데이터가 '{output_csv_path}' 파일에 저장되었습니다.")
        else:
            print("수집된 데이터가 없어 파일을 저장하지 않습니다.")

    except Exception as e:
        print(f"크롤링 중 심각한 오류 발생: {e}")
    finally:
        driver.quit()
        print("크롬 드라이버를 종료했으며, 전체 작업이 완료되었습니다.") 