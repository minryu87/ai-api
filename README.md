# ai-api

## 📁 프로젝트 구조

```
ai-api/
├── app/
│   ├── api/                    # API 라우터들
│   │   ├── medicontent.py      # 메디컨텐츠 API
│   │   ├── airtable.py         # Airtable API
│   │   └── ...
│   ├── services/               # 비즈니스 로직
│   │   ├── medicontent_service.py  # 메디컨텐츠 서비스
│   │   └── ...
│   ├── agents/                 # AI 에이전트들 (멀티에이전트 시스템)
│   │   ├── input_agent.py      # 입력 데이터 수집/전처리
│   │   ├── plan_agent.py       # 콘텐츠 계획 수립
│   │   ├── title_agent.py      # SEO 최적화 제목 생성
│   │   ├── content_agent.py    # 전문 콘텐츠 생성
│   │   ├── evaluation_agent.py # SEO/의료법 검토
│   │   └── run_agents.py       # 에이전트 실행 파이프라인
│   ├── utils/                  # 유틸리티
│   │   └── html_converter.py   # HTML 변환기
│   ├── templates/              # 템플릿 파일들
│   └── models/                 # 데이터 모델
├── requirements.txt            # Python 의존성
├── Dockerfile                  # Docker 설정
└── README.md                   # 프로젝트 문서
```

## 🤖 멀티에이전트 시스템

이 프로젝트는 **5개의 AI 에이전트**로 구성된 멀티에이전트 시스템을 포함합니다:

1. **InputAgent** - 병원 데이터 수집 및 전처리
2. **PlanAgent** - 콘텐츠 구조와 키워드 계획 수립  
3. **TitleAgent** - SEO 최적화된 제목 생성
4. **ContentAgent** - 의료법을 준수하는 전문 콘텐츠 작성
5. **EvaluationAgent** - SEO 점수 및 의료법 준수 여부 검토

각 에이전트는 **CORT (Chain of Thought)** 시스템으로 작동하여 다중 후보를 생성하고 최적 결과를 선택합니다.

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

### 9. 메디컨텐츠 상태 업데이트
- **이름:** MediContent Post Status Update
- **주소:** `/api/v1/medicontent/update-post-status`
- **메서드:** POST
- **설명:** Medicontent Posts 테이블의 특정 포스트 상태를 업데이트합니다.
- **Input (Body):**
  ```json
  {
    "postId": "post_recXXXXXX",
    "status": "병원 작업 중"
  }
  ```
- **Output (Success):**
  ```json
  {
    "status": "success",
    "message": "상태가 '병원 작업 중'으로 업데이트되었습니다.",
    "postId": "post_recXXXXXX"
  }
  ```

### 10. 메디컨텐츠 자료 요청 저장
- **이름:** MediContent Data Request Save
- **주소:** `/api/v1/medicontent/data-requests`
- **메서드:** POST
- **설명:** 병원에서 제공한 자료를 Post Data Requests 테이블에 저장합니다.
- **Input (Body):**
  ```json
  {
    "postId": "post_recXXXXXX",
    "conceptMessage": "치아 미백으로 자신감 회복",
    "patientCondition": "치아가 누렇게 변색되어 자신감이 떨어짐",
    "treatmentProcessMessage": "안전한 레이저 미백 시술",
    "treatmentResultMessage": "하얀 치아로 자신감 회복",
    "additionalMessage": "추가 요청사항",
    "beforeImages": ["before1.jpg"],
    "processImages": ["process1.jpg"],
    "afterImages": ["after1.jpg"],
    "beforeImagesText": "내원 시 치아 상태",
    "processImagesText": "레이저 미백 시술 과정",
    "afterImagesText": "시술 후 하얗게 변한 치아"
  }
  ```
- **Output (Success):**
  ```json
  {
    "status": "success",
    "message": "자료 요청이 성공적으로 저장되었습니다.",
    "record_id": "recYYYYYYY",
    "postId": "post_recXXXXXX"
  }
  ```

### 11. 메디컨텐츠 완전 생성 워크플로우
- **이름:** MediContent Complete Generation Workflow
- **주소:** `/api/v1/medicontent/generate-content-complete`
- **메서드:** POST
- **설명:** 병원 자료를 받아 AI 에이전트들이 순차적으로 실행하여 완전한 의료 콘텐츠를 생성하고 Airtable에 저장합니다.
- **Input (Body):** 10번과 동일한 구조
- **Output (Success):**
  ```json
  {
    "status": "success",
    "postId": "post_recXXXXXX",
    "recordId": "recYYYYYYY",
    "results": {
      "title": "치아 미백으로 자신감 회복한 환자 사례",
      "content": "생성된 전문 의료 콘텐츠...",
      "plan": {...},
      "evaluation": {...}
    },
    "message": "메디컨텐츠 생성 및 DB 저장 완료!"
  }
  ```

### 12. 메디컨텐츠 콘텐츠 평가
- **이름:** MediContent Content Evaluation
- **주소:** `/api/v1/medicontent/evaluate-content`
- **메서드:** POST
- **설명:** 생성된 콘텐츠의 SEO 및 의료법 준수 여부를 평가합니다.
- **Input (Body):**
  ```json
  {
    "content": "평가할 콘텐츠",
    "title": "평가할 제목"
  }
  ```
- **Output (Success):**
  ```json
  {
    "status": "success",
    "evaluation": "평가 결과",
    "message": "평가 완료"
  }
  ```

### 13. 메디컨텐츠 백그라운드 생성 트리거
- **이름:** MediContent Background Generation Trigger
- **주소:** `/api/v1/medicontent/trigger-text-generation`
- **메서드:** POST
- **설명:** 텍스트 생성을 백그라운드에서 실행하도록 트리거합니다.
- **Input (Body):**
  ```json
  {
    "postId": "post_recXXXXXX"
  }
  ```
- **Output (Success):**
  ```json
  {
    "status": "success",
    "message": "텍스트 생성이 백그라운드에서 시작되었습니다.",
    "postId": "post_recXXXXXX"
  }
  ```

---

> 앞으로 API가 추가될 때마다 위와 같은 형식으로 정보를 정리해 주세요.
