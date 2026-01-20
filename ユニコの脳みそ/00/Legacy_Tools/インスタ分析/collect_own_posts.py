"""
自身のInstagram投稿をGraph APIで収集するモジュール
"""
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import time
from config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_BUSINESS_ACCOUNT_ID,
    GRAPH_API_BASE_URL
)


def get_media_list(limit: int = 25) -> List[Dict]:
    """
    Graph APIを使用して自分の投稿一覧を取得
    
    Args:
        limit: 取得する投稿数の上限
        
    Returns:
        投稿データのリスト
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        raise ValueError("Instagram Graph APIの設定が完了していません。.envファイルを確認してください。")
    
    url = f"{GRAPH_API_BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
        'access_token': INSTAGRAM_ACCESS_TOKEN,
        'limit': limit
    }
    
    all_posts = []
    next_url = url
    
    while next_url and len(all_posts) < limit:
        try:
            response = requests.get(next_url, params=params if next_url == url else None)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                all_posts.extend(data['data'])
            
            # 次のページがあるかチェック
            if 'paging' in data and 'next' in data['paging']:
                next_url = data['paging']['next']
                params = None  # 次のURLには既にパラメータが含まれている
                time.sleep(1)  # API制限対策
            else:
                next_url = None
                
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {e}")
            break
    
    return all_posts[:limit]


def get_media_insights(media_id: str) -> Dict:
    """
    投稿のインサイトデータ（保存数など）を取得
    
    Args:
        media_id: メディアID
        
    Returns:
        インサイトデータ
    """
    url = f"{GRAPH_API_BASE_URL}/{media_id}/insights"
    params = {
        'metric': 'saved,reach,impressions',
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        insights = {}
        if 'data' in data:
            for metric in data['data']:
                insights[metric['name']] = metric['values'][0]['value'] if metric['values'] else 0
        
        return insights
    except requests.exceptions.RequestException as e:
        print(f"インサイト取得エラー (media_id: {media_id}): {e}")
        return {}


def extract_hashtags(caption: str) -> str:
    """
    キャプションからハッシュタグを抽出
    
    Args:
        caption: キャプション文字列
        
    Returns:
        ハッシュタグの文字列（カンマ区切り）
    """
    if not caption:
        return ''
    
    import re
    hashtags = re.findall(r'#\w+', caption)
    return ' '.join(hashtags)


def collect_own_posts(limit: int = 100) -> pd.DataFrame:
    """
    自分の投稿を収集してDataFrameに変換
    
    Args:
        limit: 取得する投稿数の上限
        
    Returns:
        投稿データのDataFrame
    """
    print(f"自分の投稿を収集中... (最大{limit}件)")
    
    posts = get_media_list(limit)
    
    if not posts:
        print("投稿が見つかりませんでした。")
        return pd.DataFrame()
    
    data = []
    
    for i, post in enumerate(posts, 1):
        print(f"処理中: {i}/{len(posts)}")
        
        # インサイトデータを取得（保存数など）
        insights = get_media_insights(post.get('id', ''))
        
        # 投稿日時をパース
        timestamp = post.get('timestamp', '')
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            post_time = dt.strftime('%H:%M')
            post_date = dt.strftime('%Y-%m-%d')
            weekday = dt.strftime('%A')
        else:
            post_time = ''
            post_date = ''
            weekday = ''
        
        caption = post.get('caption', '')
        hashtags = extract_hashtags(caption)
        
        row = {
            '投稿タイプ': '自分',
            '投稿日時': f"{post_date} {post_time}" if post_date and post_time else timestamp,
            '投稿日': post_date,
            '投稿時間帯': post_time,
            '曜日': weekday,
            'いいね数': post.get('like_count', {}).get('count', 0) if isinstance(post.get('like_count'), dict) else post.get('like_count', 0),
            'コメント数': post.get('comments_count', {}).get('count', 0) if isinstance(post.get('comments_count'), dict) else post.get('comments_count', 0),
            '保存数': insights.get('saved', 0),
            'リーチ数': insights.get('reach', 0),
            'インプレッション数': insights.get('impressions', 0),
            'キャプション': caption,
            'ハッシュタグ': hashtags,
            'メディアタイプ': post.get('media_type', ''),
            '投稿URL': post.get('permalink', ''),
            'メディアID': post.get('id', ''),
            '再生数': ''  # Graph APIでは取得不可
        }
        
        data.append(row)
        
        # API制限対策
        if i < len(posts):
            time.sleep(1)
    
    df = pd.DataFrame(data)
    print(f"収集完了: {len(df)}件の投稿を取得しました。")
    
    return df


if __name__ == '__main__':
    # テスト実行
    df = collect_own_posts(limit=10)
    if not df.empty:
        print(df.head())
        df.to_csv('output/own_posts.csv', index=False, encoding='utf-8-sig')





