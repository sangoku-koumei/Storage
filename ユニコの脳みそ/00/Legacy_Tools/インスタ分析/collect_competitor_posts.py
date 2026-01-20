"""
競合アカウントのInstagram投稿をInstaloaderで収集するモジュール
"""
import instaloader
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import time
import re
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    SCRAPING_DELAY,
    MAX_POSTS_PER_ACCOUNT
)


def extract_hashtags(caption: str) -> str:
    """
    キャプションからハッシュタグを抽出
    
    Args:
        caption: キャプション文字列
        
    Returns:
        ハッシュタグの文字列（スペース区切り）
    """
    if not caption:
        return ''
    
    hashtags = re.findall(r'#\w+', caption)
    return ' '.join(hashtags)


def collect_competitor_posts(
    username: str,
    max_posts: int = MAX_POSTS_PER_ACCOUNT,
    login_required: bool = True
) -> pd.DataFrame:
    """
    競合アカウントの投稿を収集してDataFrameに変換
    
    Args:
        username: Instagramアカウント名（@なし）
        max_posts: 取得する最大投稿数
        login_required: ログインが必要かどうか（いいね数取得には必要）
        
    Returns:
        投稿データのDataFrame
    """
    print(f"競合アカウント @{username} の投稿を収集中... (最大{max_posts}件)")
    
    # Instaloaderの初期化
    loader = instaloader.Instaloader(
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # ログイン（必要に応じて）
    if login_required and INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        try:
            loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print("ログイン成功")
        except Exception as e:
            print(f"ログインエラー: {e}")
            print("ログインなしで続行します（いいね数などが取得できない可能性があります）")
            login_required = False
    
    try:
        # プロフィールを取得
        profile = instaloader.Profile.from_username(loader.context, username)
        print(f"アカウント名: {profile.full_name}")
        print(f"フォロワー数: {profile.followers:,}")
        
        # 投稿を取得
        posts = profile.get_posts()
        
        data = []
        count = 0
        
        for post in posts:
            if count >= max_posts:
                break
            
            count += 1
            print(f"処理中: {count}/{max_posts}")
            
            # 投稿日時をパース
            post_date = post.date_local.strftime('%Y-%m-%d')
            post_time = post.date_local.strftime('%H:%M')
            weekday = post.date_local.strftime('%A')
            
            caption = post.caption or ''
            hashtags = extract_hashtags(caption)
            
            # いいね数とコメント数を取得
            likes = post.likes
            comments = post.comments
            
            row = {
                '投稿タイプ': f'競合_{username}',
                '投稿日時': f"{post_date} {post_time}",
                '投稿日': post_date,
                '投稿時間帯': post_time,
                '曜日': weekday,
                'いいね数': likes,
                'コメント数': comments,
                '保存数': '',  # Instaloaderでは取得不可
                'リーチ数': '',
                'インプレッション数': '',
                'キャプション': caption,
                'ハッシュタグ': hashtags,
                'メディアタイプ': '動画' if post.is_video else '写真',
                '投稿URL': f"https://www.instagram.com/p/{post.shortcode}/",
                'メディアID': post.shortcode,
                '再生数': ''  # 後でSeleniumで取得
            }
            
            data.append(row)
            
            # BAN対策の遅延
            if count < max_posts:
                time.sleep(SCRAPING_DELAY)
        
        df = pd.DataFrame(data)
        print(f"収集完了: {len(df)}件の投稿を取得しました。")
        
        return df
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"エラー: アカウント @{username} が見つかりませんでした。")
        return pd.DataFrame()
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"エラー: アカウント @{username} は非公開です。フォローが必要です。")
        return pd.DataFrame()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return pd.DataFrame()


def collect_from_url(post_url: str) -> Optional[Dict]:
    """
    投稿URLから1件の投稿データを取得
    
    Args:
        post_url: Instagram投稿のURL
        
    Returns:
        投稿データの辞書、またはNone
    """
    # URLからshortcodeを抽出
    shortcode_match = re.search(r'/p/([^/]+)/', post_url)
    if not shortcode_match:
        print("無効なURLです。")
        return None
    
    shortcode = shortcode_match.group(1)
    
    loader = instaloader.Instaloader(
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # ログイン（必要に応じて）
    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        try:
            loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        except Exception as e:
            print(f"ログインエラー: {e}")
    
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        post_date = post.date_local.strftime('%Y-%m-%d')
        post_time = post.date_local.strftime('%H:%M')
        weekday = post.date_local.strftime('%A')
        
        caption = post.caption or ''
        hashtags = extract_hashtags(caption)
        
        return {
            '投稿タイプ': '競合_個別',
            '投稿日時': f"{post_date} {post_time}",
            '投稿日': post_date,
            '投稿時間帯': post_time,
            '曜日': weekday,
            'いいね数': post.likes,
            'コメント数': post.comments,
            '保存数': '',
            'リーチ数': '',
            'インプレッション数': '',
            'キャプション': caption,
            'ハッシュタグ': hashtags,
            'メディアタイプ': '動画' if post.is_video else '写真',
            '投稿URL': post_url,
            'メディアID': post.shortcode,
            '再生数': ''
        }
    except Exception as e:
        print(f"投稿取得エラー: {e}")
        return None


if __name__ == '__main__':
    # テスト実行
    # df = collect_competitor_posts('example_account', max_posts=10)
    # if not df.empty:
    #     print(df.head())
    #     df.to_csv('output/competitor_posts.csv', index=False, encoding='utf-8-sig')
    pass





