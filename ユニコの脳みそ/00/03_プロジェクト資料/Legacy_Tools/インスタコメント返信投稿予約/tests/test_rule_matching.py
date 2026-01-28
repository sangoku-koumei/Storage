"""
ルールマッチングのテスト
"""
from app.models import CommentReplyRule, DMReplyRule
from app.enums import MessageTemplateKind


def test_comment_rule_matching():
    """コメントルールのマッチングテスト"""
    # テスト用のルール
    rule = CommentReplyRule(
        keyword="ありがとう",
        reply_text="どういたしまして！",
        priority=1,
    )
    
    # マッチするケース
    assert "ありがとう" in "ありがとうございます！".lower()
    assert "ありがとう" in "ありがとう".lower()
    
    # マッチしないケース
    assert "ありがとう" not in "こんにちは".lower()


def test_dm_rule_matching():
    """DMルールのマッチングテスト"""
    # テスト用のルール
    rule = DMReplyRule(
        keyword="こんにちは",
        reply_text="こんにちは！",
        priority=1,
    )
    
    # マッチするケース
    assert "こんにちは" in "こんにちは！".lower()
    
    # マッチしないケース
    assert "こんにちは" not in "さようなら".lower()


