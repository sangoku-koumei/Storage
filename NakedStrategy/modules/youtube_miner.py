from googleapiclient.discovery import build
from openai import OpenAI
import pandas as pd
import streamlit as st

def search_videos(query, api_key, max_results=10):
    """
    Searches for videos on YouTube matching the query.
    Returns a list of dictionaries with video details.
    """
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            order="viewCount"
        ).execute()
        
        videos = []
        for item in search_response.get('items', []):
            videos.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            })
        return videos
    except Exception as e:
        st.error(f"YouTube Search Error: {e}")
        return []

def get_comments_for_videos(video_ids, api_key, max_comments_per_video=20):
    """
    Fetches comments for a list of video IDs.
    Returns a list of all comments text.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    all_comments = []
    
    for video_id in video_ids:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_comments_per_video,
                textFormat="plainText"
            ).execute()

            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                all_comments.append(comment['textDisplay'])
        except Exception:
            # Comments might be disabled or other error, skip video
            continue
            
    return all_comments

def extract_pains_from_comments(comments_list, openai_key):
    """
    Uses OpenAI API to extract pain points from a list of comments.
    """
    if not comments_list:
        return "コメントが見つかりませんでした。"

    client = OpenAI(api_key=openai_key)
    
    # Limit input size to prevent token overflow (approx first 50-80 comments)
    text_blob = "\n---\n".join(comments_list[:100])
    
    prompt = f"""
    あなたは凄腕のマーケターです。以下のYouTubeコメント（「--」区切り）は、あるトピックに関する視聴者の生の声です。
    ここから、ユーザーが抱えている**「切実な悩み」「満たされない欲求（ペイン）」「競合への不満」**を5つ抽出し、
    それぞれについて「売れる商品の切り口（コピー）」を提案してください。

    出力フォーマット:
    ### 1. [悩みの要約タイトル]
    - **ユーザーの声**: (代表的なコメントを要約)
    - **深層心理**: (なぜ悩んでいるのか？)
    - **勝ち筋提案**: (商品タイトルや訴求ポイント案)

    分析対象コメント:
    {text_blob}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo if cost is concern, but 4o is better for Japanese nuances
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis Error: {e}"
