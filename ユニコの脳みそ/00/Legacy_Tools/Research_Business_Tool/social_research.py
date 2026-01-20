
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os

def get_video_id(url):
    """YouTubeのURLからVideo IDを抽出する"""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def fetch_youtube_transcript(video_id, languages=['ja', 'en']):
    """YouTubeの字幕を取得する"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        full_text = " ".join([t['text'] for t in transcript_list])
        return full_text
    except Exception as e:
        return None

def analyze_youtube_video(video_url, api_key):
    """YouTube動画の内容をAI分析する"""
    video_id = get_video_id(video_url)
    if not video_id:
        return "Error: Invalid YouTube URL."
    
    transcript = fetch_youtube_transcript(video_id)
    if not transcript:
        return "Error: Could not retrieve transcript (Video may verify age, or no subtitles)."

    # テキストが長すぎる場合の簡易カット (GPTトークン対策)
    if len(transcript) > 15000:
        transcript = transcript[:15000] + "...(省略)..."

    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    以下のYouTube動画の字幕テキストを分析し、リサーチレポートを作成してください。
    
    【対象動画】
    https://www.youtube.com/watch?v={video_id}
    
    【分析要件】
    1. **動画の要約**: 何について話している動画か（3行）
    2. **重要なポイント**: 視聴者が得られる学び（箇条書き5点）
    3. **キラーフレーズ**: 印象的な言葉やパワーワード
    4. **競合分析**: この動画が「なぜ伸びている（または伸びない）」と考えられるか、構成や話し方の観点から分析
    
    【字幕テキスト】
    {transcript}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional video analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {e}"
