# ai-api

## API 목록

### 1. Health Check
- **이름:** Health Check
- **주소:** `/health`
- **메서드:** GET
- **Input:** 없음
- **Output:**
  ```json
  { "status": "ok" }
  ```

### 2. 샘플 API
- **이름:** Sample Hello
- **주소:** `/sample/hello`
- **메서드:** GET
- **Input:** 없음
- **Output:**
  ```json
  { "message": "Hello, World!" }
  ```

### 3. 유튜브 채널 크롤러
- **이름:** Youtube Channel Crawler
- **주소:** `/youtube/crawl?channel=채널명`
- **메서드:** GET
- **Input:**
  - `channel` (string, 필수): 유튜브 채널명 (예: solamc-g8y)
- **Output:**
  - 예시
    ```json
    {
      "channel": "solamc-g8y",
      "videos": [
        { "title": "동영상 제목", "url": "https://www.youtube.com/watch?v=..." },
        ...
      ],
      "videos_count": 10
    }
    ```

---

> 앞으로 API가 추가될 때마다 위와 같은 형식으로 정보를 정리해 주세요.
