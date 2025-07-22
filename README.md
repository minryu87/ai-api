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

### 3. 유튜브 영상 정보 조회
- **이름:** Youtube Video List
- **주소:** `/youtube/videos?channel=채널명`
- **메서드:** GET
- **Input:**
  - `channel` (string, 필수): 유튜브 채널명 (예: solamc-g8y)
- **Output:**
  - 예시
    ```json
    [
      {
        "channelId": "UCxxxx",
        "videoId": "abc123",
        "title": "영상 제목",
        "publishedAt": "2024-06-17T12:00:00Z",
        "viewCount": 12345,
        "likeCount": 678,
        "commentCount": 10
      },
      ...
    ]
    ```

### 4. 유튜브 댓글/답글 정보 조회
- **이름:** Youtube Comment/Reply List
- **주소:** `/youtube/comments?channel=채널명`
- **메서드:** GET
- **Input:**
  - `channel` (string, 필수): 유튜브 채널명 (예: solamc-g8y)
- **Output:**
  - 예시
    ```json
    [
      {
        "channelId": "UCxxxx",
        "videoId": "abc123",
        "comment_id": "cmt1",
        "parent_id": "abc123",
        "author": "댓글작성자",
        "text": "댓글 내용",
        "publishedAt": "2024-06-17T13:00:00Z",
        "likeCount": 5,
        "type": "comment"
      },
      {
        "channelId": "UCxxxx",
        "videoId": "abc123",
        "comment_id": "rpl1",
        "parent_id": "cmt1",
        "author": "답글작성자",
        "text": "답글 내용",
        "publishedAt": "2024-06-17T14:00:00Z",
        "likeCount": 2,
        "type": "reply"
      },
      ...
    ]
    ```

### 5. Airtable 웹훅 처리
- **이름:** Airtable Webhook Processor
- **주소:** `/api/v1/airtable/webhook/process-thread`
- **메서드:** POST
- **설명:** Airtable Automation을 통해 데이터 변경(생성/수정)이 감지되었을 때 호출되는 API입니다. 관련 데이터를 통합하여 최종 테이블에 저장하는 작업을 백그라운드에서 실행합니다.
- **Input (Body):**
  ```json
  {
    "recordId": "recXXXXXXXXXXXXXX",
    "tableId": "tblXXXXXXXXXXXXXX"
  }
  ```
- **Output (Success):**
  ```json
  {
    "status": "success",
    "message": "Processing task has been added to the background.",
    "threadId": "NAVER_CAFE_THREAD_8082993"
  }
  ```

### 6. Airtable 데이터 수동 재처리
- **이름:** Airtable Manual Reprocessor
- **주소:** `/api/v1/airtable/reprocess/{thread_id}`
- **메서드:** POST
- **설명:** 특정 `thread_id`에 해당하는 데이터의 통합 및 저장을 수동으로 재실행합니다. 자동화 과정에 문제가 있었거나 특정 데이터를 다시 처리하고 싶을 때 사용합니다.
- **Input (Path Parameter):**
  - `thread_id` (string, 필수): 재처리할 네이버 카페 스레드의 고유 ID
- **Output (Success):**
  ```json
  {
    "id": "recXXXXXXXXXXXXXX",
    "threadId": "NAVER_CAFE_THREAD_8082993",
    "clientName": "솔동물의료센터",
    "channel": "NAVERCAFE",
    "community": "고양이라서 다행이야",
    "title": "(승인)아메리칸숏헤어 귀염둥이 입양보내요~",
    "postedAt": "2025-06-17T13:57:00",
    "link": "https://cafe.naver.com/ilovecat/8082993",
    "integratedText": {
      "threadText": "만두와 평생을 함께 할 새 가족을 찾습니다...",
      "comments": [
        {
          "commentText": "★국희는 외동묘나 둘째묘 정도로 생각하고 있습니다...",
          "replies": [{"replyText": "감사합니다"}]
        }
      ]
    },
    "relevance": null,
    "createdAt": "2025-06-18T14:10:00"
  }
  ```

### 7. PostgreSQL 데이터 수동 재처리
- **이름:** PostgreSQL Manual Reprocessor
- **주소:** `/api/v1/postgres/reprocess-from-postgres/{thread_id}`
- **메서드:** POST
- **설명:** 특정 `thread_id`에 해당하는 데이터를 **PostgreSQL DB**에서 가져와 통합하고 최종적으로 **Airtable**에 저장합니다. DB 마이그레이션 후 또는 데이터 정합성이 필요할 때 사용합니다.
- **Input (Path Parameter):**
  - `thread_id` (string, 필수): 재처리할 스레드의 고유 ID
- **Output (Success):**
  ```json
  {
    "id": "recXXXXXXXXXXXXXX",
    "threadId": "NAVER_CAFE_THREAD_4899403",
    "clientName": "솔동물의료센터",
    "channel": "NAVERCAFE",
    "community": "고양이라서 다행이야",
    "title": "(승인)아메리칸숏헤어 귀염둥이 입양보내요~",
    "postedAt": "2025-06-17T13:57:00",
    "link": "https://cafe.naver.com/ilovecat/4899403",
    "integratedText": {
      "threadText": "만두와 평생을 함께 할 새 가족을 찾습니다...",
      "comments": [
        {
          "commentText": "★국희는 외동묘나 둘째묘 정도로 생각하고 있습니다...",
          "replies": [{"replyText": "감사합니다"}]
        }
      ]
    },
    "relevance": null,
    "createdAt": "2025-06-18T14:10:00"
  }
  ```

### 8. 네이버 Creator Advisor 데이터 동기화
- **이름:** Naver Creator Advisor Data Sync
- **주소:** `/api/v1/creator-advisor/sync-creator-advisor`
- **메서드:** POST
- **설명:** 네이버 Creator Advisor의 4개 API에서 데이터를 가져와 Airtable에 동기화하는 작업을 백그라운드에서 실행합니다.
- **Input (Body):** 없음
- **Output (Success):**
  ```json
  {
    "message": "Creator Advisor 데이터 동기화 작업이 백그라운드에서 시작되었습니다."
  }
  ```

---

> 앞으로 API가 추가될 때마다 위와 같은 형식으로 정보를 정리해 주세요.
