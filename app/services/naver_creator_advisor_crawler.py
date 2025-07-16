import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import calendar

# 네이버 쿠키 문자열 (직접 입력 또는 환경변수에서 불러올 수 있음)
NAVER_COOKIE = "SRT5=1752559088; BUC=A5YpfXxEpKW_xx8V-KZvfZFihuBRIwZm-jSYIX0KosU=; SRT30=1752554370; NID_SES=AAABwFRY4XrzhPl7upuRqb9umZefxA5dq43yB9M9cEGn51KJKmSx/XkTBmm499jVfKHQDKNd/T6F2EqfC+++/kfPlTXWArtdKXP+FW8Yj3+e9OcUjbMUfeOO2DBXM0yeMFG/rLC65ALhqO7I1Gq+LxM/Eny1sVA//cEjLkMS5mJeNSXH8UDxG0xrtAPA46Tj9DbK0Y8okPZKTTvSoICM7sSKNrQVpx9SXHNdsNq8EmMXLPCm8dTXA/ncTEn2QoW+gdmwJna/nU2outE9K2RgFGA6Q1Ho3wkEOnKVX2D1M7u2JH4JLBs1yL3C4i/5WJH7MWG4ju3Gma0eYfoEcAKt6EozFjdr3ztsqyWuIqfoSmVYrBF9kk5QRcYaiZmYg6lJlutgt6IdHWrn037GU8Po3ytpgXpRY7BrmLhzNJPytdXFykm6578FCIQZIZrxNH14FOhuSEbbpX47KED+dPeHwQBlF4ivYyPRu23g9y3Pk391sa/lq/3bK3UZux562ZPohlJtcXeEnIurtAB/8G5WL5GP+ogG9vFCQsoqA4Hj0aeVjkh+2IPuIZM1uqj8Rz19dZib6aMirXTY0ZkCPk4/KiQfL9Q=; NNB=ZKHGWSJXM6SGO; ASID=01dcd28c00000194f85124240000004f; NAC=LjaaBowe2zA0A; NID_AUT=nGV0MiYqN6GvEpMrMTW/iITM8gp5FWeU6xvuI2ECGWoy1L9vy5m1PdEYUUEU2FrS"


def get_month_range(date_str):
    """
    date_str: 'YYYY-MM-DD' 형식
    return (startDate, endDate) - 둘 다 'YYYY-MM-DD' 형식
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    start = dt.replace(day=1)
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    end = dt.replace(day=last_day)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def crawl_keyword_stats(postId, date):
    startDate, endDate = get_month_range(date)
    url = f"https://creator-advisor.naver.com/new-windows/article-stats?channelId=elza79&contentId=http%3A%2F%2Fblog.naver.com%2Felza79%2F{postId}&contentType=text-and-moment&endDate={endDate}&interval=month&service=naver_blog&startDate={startDate}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Cookie": NAVER_COOKIE,
    }
    resp = requests.get(url, headers=headers)

    # 디버깅을 위해 HTML 파일 저장
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
        
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text}
    soup = BeautifulSoup(resp.text, "lxml")
    results = []
    for li in soup.select("ul.u_ni_list.keyword_list li.u_ni_item"):
        title = li.select_one(".u_ni_title")
        value = li.select_one(".u_ni_value")
        if title and value:
            results.append({
                "postId": postId,
                "startDate": startDate,
                "endDate": endDate,
                "title": title.get_text(strip=True),
                "value": value.get_text(strip=True)
            })
    return {"data": results, "url": url} 