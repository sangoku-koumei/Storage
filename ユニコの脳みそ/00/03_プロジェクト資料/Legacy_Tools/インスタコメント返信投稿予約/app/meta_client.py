"""
Meta Graph API クライアント
Instagram API呼び出しをラップ
"""
import requests
from typing import Optional
from app.config import settings


class MetaAPIError(Exception):
    """Meta API関連の例外"""
    pass


def create_media_for_post(
    *,
    ig_user_id: str,
    post_type: str,
    media_type: str,
    image_url: str | None = None,
    video_url: str | None = None,
    caption: str | None = None,
    access_token: str,
) -> str:
    """
    メディアオブジェクトを作成（Feed/Reel/Story対応）
    
    Args:
        ig_user_id: Instagram Business Account ID
        post_type: 投稿種別 (feed, reel, story)
        media_type: メディアタイプ (image, video)
        image_url: 画像URL（imageの場合必須）
        video_url: 動画URL（videoの場合必須、reelの場合は常に必須）
        caption: キャプション
        access_token: アクセストークン
        
    Returns:
        creation_id（メディア作成ID）
    """
    endpoint = f"{settings.GRAPH_API_BASE_URL}/{ig_user_id}/media"
    payload: dict[str, str] = {"access_token": access_token}
    
    if caption:
        payload["caption"] = caption
    
    if post_type == "feed":
        if media_type == "image":
            if not image_url:
                raise MetaAPIError("image_url is required for feed image post")
            payload["image_url"] = image_url
        elif media_type == "video":
            if not video_url:
                raise MetaAPIError("video_url is required for feed video post")
            payload["video_url"] = video_url
        else:
            raise MetaAPIError(f"Unsupported media_type for feed: {media_type}")
            
    elif post_type == "reel":
        if not video_url:
            raise MetaAPIError("video_url is required for reel post")
        payload["video_url"] = video_url
        payload["media_type"] = "REELS"
        
    elif post_type == "story":
        if media_type == "image":
            if not image_url:
                raise MetaAPIError("image_url is required for story image")
            payload["image_url"] = image_url
            payload["media_type"] = "STORIES"
        elif media_type == "video":
            if not video_url:
                raise MetaAPIError("video_url is required for story video")
            payload["video_url"] = video_url
            payload["media_type"] = "STORIES"
        else:
            raise MetaAPIError(f"Unsupported media_type for story: {media_type}")
    else:
        raise MetaAPIError(f"Unsupported post_type: {post_type}")
    
    resp = requests.post(endpoint, data=payload, timeout=30)
    if resp.status_code != 200:
        raise MetaAPIError(
            f"create_media_for_post failed: {resp.status_code} {resp.text}"
        )
    
    data = resp.json()
    creation_id = data.get("id")
    if not creation_id:
        raise MetaAPIError(f"create_media_for_post no id: {data}")
    
    return creation_id


def publish_media(
    ig_user_id: str,
    creation_id: str,
    access_token: str,
) -> str:
    """
    メディアを公開
    
    Args:
        ig_user_id: Instagram Business Account ID
        creation_id: メディア作成ID
        access_token: アクセストークン
        
    Returns:
        media_id（公開されたメディアID）
    """
    endpoint = f"{settings.GRAPH_API_BASE_URL}/{ig_user_id}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": access_token,
    }
    
    resp = requests.post(endpoint, data=payload, timeout=30)
    if resp.status_code != 200:
        raise MetaAPIError(
            f"publish_media failed: {resp.status_code} {resp.text}"
        )
    
    data = resp.json()
    media_id = data.get("id")
    if not media_id:
        raise MetaAPIError(f"publish_media no id: {data}")
    
    return media_id


def reply_to_comment(
    comment_id: str,
    message: str,
    access_token: str,
) -> str:
    """
    コメントに返信
    
    Args:
        comment_id: コメントID
        message: 返信メッセージ
        access_token: アクセストークン
        
    Returns:
        reply_id（返信ID）
    """
    endpoint = f"{settings.GRAPH_API_BASE_URL}/{comment_id}/replies"
    payload = {
        "message": message,
        "access_token": access_token,
    }
    
    resp = requests.post(endpoint, data=payload, timeout=10)
    if resp.status_code != 200:
        raise MetaAPIError(
            f"reply_to_comment failed: {resp.status_code} {resp.text}"
        )
    
    data = resp.json()
    reply_id = data.get("id")
    if not reply_id:
        raise MetaAPIError(f"reply_to_comment no id: {data}")
    
    return reply_id


def send_instagram_dm(
    *,
    ig_user_id: str,
    recipient_id: str,
    message: str,
    access_token: str,
) -> str:
    """
    Instagram DMを送信
    
    Args:
        ig_user_id: Instagram Business Account ID
        recipient_id: 受信者のInstagram User ID
        message: メッセージ本文
        access_token: アクセストークン
        
    Returns:
        message_id（送信されたメッセージID）
    """
    endpoint = f"{settings.GRAPH_API_BASE_URL}/{ig_user_id}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
        "access_token": access_token,
    }
    
    resp = requests.post(endpoint, json=payload, timeout=10)
    if resp.status_code != 200:
        raise MetaAPIError(
            f"send_instagram_dm failed: {resp.status_code} {resp.text}"
        )
    
    data = resp.json()
    message_id = data.get("id") or data.get("message_id")
    if not message_id:
        raise MetaAPIError(f"send_instagram_dm no id: {data}")
    
    return message_id


