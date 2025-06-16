import os
from googleapiclient.discovery import build

def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise Exception("YOUTUBE_API_KEY 환경변수가 설정되어 있지 않습니다.")
    return build("youtube", "v3", developerKey=api_key)

def get_channel_id_by_custom_name(youtube, custom_name):
    # 커스텀 채널명(@xxxx)으로 채널ID 조회
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

def search_youtube_videos(youtube, channel_id, max_results=10):
    request = youtube.search().list(
        channelId=channel_id,
        part="snippet",
        maxResults=max_results,
        type="video",
        order="date"
    )
    response = request.execute()
    videos = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append({"video_id": video_id, "title": title})
    return videos

def get_video_comments(youtube, video_id, max_results=10):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )
    response = request.execute()
    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet.get("authorDisplayName"),
            "text": snippet.get("textDisplay"),
            "publishedAt": snippet.get("publishedAt"),
            "likeCount": snippet.get("likeCount", 0)
        })
    return comments

def get_video_statistics(youtube, video_id):
    request = youtube.videos().list(
        part="statistics,snippet",
        id=video_id
    )
    response = request.execute()
    if not response["items"]:
        return {}
    stats = response["items"][0]["statistics"]
    snippet = response["items"][0]["snippet"]
    return {
        "viewCount": int(stats.get("viewCount", 0)),
        "likeCount": int(stats.get("likeCount", 0)),
        "commentCount": int(stats.get("commentCount", 0)),
        "publishedAt": snippet.get("publishedAt"),
        "title": snippet.get("title"),
        "description": snippet.get("description")
    }

def crawl_youtube_channel(channel_name: str):
    youtube = get_youtube_client()
    # 채널ID 조회
    channel_id = get_channel_id_by_custom_name(youtube, channel_name)
    if not channel_id:
        return {"error": "채널을 찾을 수 없습니다."}
    # 동영상 목록 조회
    videos = search_youtube_videos(youtube, channel_id, max_results=5)
    result = []
    for video in videos:
        video_id = video["video_id"]
        stats = get_video_statistics(youtube, video_id)
        comments = get_video_comments(youtube, video_id, max_results=5)
        result.append({
            "video_id": video_id,
            "title": video["title"],
            "statistics": stats,
            "comments": comments
        })
    return {
        "channel": channel_name,
        "channel_id": channel_id,
        "videos": result,
        "videos_count": len(result)
    }
