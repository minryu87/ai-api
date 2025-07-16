import os
from googleapiclient.discovery import build

def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise Exception("YOUTUBE_API_KEY 환경변수가 설정되어 있지 않습니다.")
    return build("youtube", "v3", developerKey=api_key)

def get_channel_id_by_custom_name(youtube, custom_name):
    request = youtube.search().list(
        q=custom_name,
        type="channel",
        part="snippet",
        maxResults=1
    )
    response = request.execute()
    items = response.get("items", [])
    if not items:
        return None
    return items[0]["snippet"]["channelId"]

def get_video_list_api(channel_name: str):
    youtube = get_youtube_client()
    channel_id = get_channel_id_by_custom_name(youtube, channel_name)
    if not channel_id:
        return {"error": "채널을 찾을 수 없습니다."}
    # 동영상 목록 조회
    request = youtube.search().list(
        channelId=channel_id,
        part="snippet",
        maxResults=100,
        type="video",
        order="date"
    )
    response = request.execute()
    videos = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        # 영상 통계 정보
        stats_req = youtube.videos().list(part="statistics", id=video_id)
        stats_res = stats_req.execute()
        stats = stats_res["items"][0]["statistics"] if stats_res["items"] else {}
        videos.append({
            "channelId": channel_id,
            "videoId": video_id,
            "title": snippet.get("title"),
            "publishedAt": snippet.get("publishedAt"),
            "viewCount": int(stats.get("viewCount", 0)),
            "likeCount": int(stats.get("likeCount", 0)),
            "commentCount": int(stats.get("commentCount", 0))
        })
    return videos

def get_comment_list_api(channel_name: str):
    youtube = get_youtube_client()
    channel_id = get_channel_id_by_custom_name(youtube, channel_name)
    if not channel_id:
        return {"error": "채널을 찾을 수 없습니다."}
    # 동영상 목록 조회
    request = youtube.search().list(
        channelId=channel_id,
        part="snippet",
        maxResults=100,
        type="video",
        order="date"
    )
    response = request.execute()
    comment_rows = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        # 최상위 댓글(threads) 조회
        threads_req = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100
        )
        threads_res = threads_req.execute()
        for thread in threads_res.get("items", []):
            top_comment = thread["snippet"]["topLevelComment"]
            cmt_id = top_comment["id"]
            cmt_snippet = top_comment["snippet"]
            # 최상위 댓글 row
            comment_rows.append({
                "channelId": channel_id,
                "videoId": video_id,
                "comment_id": cmt_id,
                "parent_id": video_id,
                "author": cmt_snippet.get("authorDisplayName"),
                "text": cmt_snippet.get("textDisplay"),
                "publishedAt": cmt_snippet.get("publishedAt"),
                "likeCount": cmt_snippet.get("likeCount", 0),
                "type": "comment"
            })
            # replies (1단계)
            replies = thread.get("replies", {}).get("comments", [])
            for reply in replies:
                reply_id = reply["id"]
                reply_snippet = reply["snippet"]
                comment_rows.append({
                    "channelId": channel_id,
                    "videoId": video_id,
                    "comment_id": reply_id,
                    "parent_id": cmt_id,
                    "author": reply_snippet.get("authorDisplayName"),
                    "text": reply_snippet.get("textDisplay"),
                    "publishedAt": reply_snippet.get("publishedAt"),
                    "likeCount": reply_snippet.get("likeCount", 0),
                    "type": "reply"
                })
                # replies의 reply (2단계 이상)
                # YouTube API는 replies의 reply는 별도 comments.list로 조회해야 함
                # parentId=reply_id로 추가 조회
                more_replies = get_replies_recursive(youtube, reply_id, channel_id, video_id)
                comment_rows.extend(more_replies)
    return comment_rows

def get_replies_recursive(youtube, parent_id, channel_id, video_id):
    # parent_id에 대한 reply를 모두 조회 (재귀적으로)
    rows = []
    req = youtube.comments().list(
        part="snippet",
        parentId=parent_id,
        maxResults=100
    )
    res = req.execute()
    for item in res.get("items", []):
        reply_id = item["id"]
        snippet = item["snippet"]
        rows.append({
            "channelId": channel_id,
            "videoId": video_id,
            "comment_id": reply_id,
            "parent_id": parent_id,
            "author": snippet.get("authorDisplayName"),
            "text": snippet.get("textDisplay"),
            "publishedAt": snippet.get("publishedAt"),
            "likeCount": snippet.get("likeCount", 0),
            "type": "reply"
        })
        # replies의 reply가 또 있을 수 있으므로 재귀 호출
        rows.extend(get_replies_recursive(youtube, reply_id, channel_id, video_id))
    return rows
