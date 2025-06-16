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

---

> 앞으로 API가 추가될 때마다 위와 같은 형식으로 정보를 정리해 주세요.
