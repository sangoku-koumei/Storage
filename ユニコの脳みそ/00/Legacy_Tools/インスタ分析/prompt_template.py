"""
ChatGPT用プロンプトテンプレート生成モジュール
"""
import os
from datetime import datetime
from config import OUTPUT_DIR


def generate_analysis_prompt(
    csv_path: str,
    analysis_type: str = 'comprehensive'
) -> str:
    """
    ChatGPT用の分析プロンプトテンプレートを生成
    
    Args:
        csv_path: CSVファイルのパス
        analysis_type: 分析タイプ（'comprehensive', 'caption', 'hashtag', 'timing'など）
        
    Returns:
        プロンプト文字列
    """
    
    base_prompt = f"""以下は私と競合のInstagram投稿データです。
キャプション、タグ、投稿時間、反応（いいね・保存・コメント）などをもとに、
私の投稿の伸び悩みの原因を分析してください。

【分析してほしいポイント】
"""
    
    if analysis_type == 'comprehensive':
        prompt = base_prompt + """
1. バズった投稿と伸びなかった投稿の違い
   - キャプションの傾向（文字数、構成、トーン）
   - ハッシュタグの使い方（数、種類、頻度）
   - 投稿時間帯や曜日の効果
   - メディアタイプ（写真/動画）の違い

2. 自分と競合の比較
   - どの要素が最も差が出ているか
   - 競合の成功パターンで真似できるものは何か
   - 自分の強みと弱み

3. 改善提案
   - 具体的な改善アクション
   - 次回の投稿で試すべきこと
   - 避けるべきパターン

【データ】
以下のCSVデータを分析してください：

"""
    elif analysis_type == 'caption':
        prompt = base_prompt + """
1. キャプションの分析
   - 文字数の最適範囲
   - 構成パターン（導入、本文、締め）
   - 絵文字の使い方
   - 共感を呼ぶフレーズ

2. キャプション改善案
   - バズった投稿のキャプションの特徴
   - 自分のキャプションの改善点

【データ】
以下のCSVデータを分析してください：

"""
    elif analysis_type == 'hashtag':
        prompt = base_prompt + """
1. ハッシュタグの分析
   - タグ数の最適範囲
   - 効果的なタグの種類
   - タグとエンゲージメントの相関

2. ハッシュタグ戦略の改善案
   - 競合が使っている効果的なタグ
   - 自分のタグ選びの改善点

【データ】
以下のCSVデータを分析してください：

"""
    elif analysis_type == 'timing':
        prompt = base_prompt + """
1. 投稿タイミングの分析
   - 効果的な投稿時間帯
   - 曜日の効果
   - 投稿頻度の影響

2. タイミング戦略の改善案
   - 最適な投稿スケジュール
   - 避けるべき時間帯

【データ】
以下のCSVデータを分析してください：

"""
    else:
        prompt = base_prompt + """
【データ】
以下のCSVデータを分析してください：

"""
    
    prompt += f"""
---CSVデータ（{csv_path}）---
[ここにCSVデータを貼り付けてください]

分析結果は、具体的で実践的なアドバイスとして出力してください。
"""
    
    return prompt


def save_prompt_template(
    csv_path: str,
    analysis_type: str = 'comprehensive',
    output_dir: str = OUTPUT_DIR
) -> str:
    """
    プロンプトテンプレートをファイルに保存
    
    Args:
        csv_path: CSVファイルのパス
        analysis_type: 分析タイプ
        output_dir: 出力ディレクトリ
        
    Returns:
        保存したファイルのパス
    """
    prompt = generate_analysis_prompt(csv_path, analysis_type)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'chatgpt_prompt_{analysis_type}_{timestamp}.txt'
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    return filepath


def generate_quick_analysis_summary(df) -> str:
    """
    簡易分析サマリーを生成（ChatGPTに渡す前の補足情報として）
    
    Args:
        df: 投稿データのDataFrame
        
    Returns:
        サマリーテキスト
    """
    import pandas as pd
    
    if df.empty:
        return "データがありません。"
    
    summary = "【データサマリー】\n\n"
    
    # 基本統計
    if '投稿タイプ' in df.columns:
        summary += f"投稿タイプ別件数:\n"
        for post_type, count in df['投稿タイプ'].value_counts().items():
            summary += f"  - {post_type}: {count}件\n"
        summary += "\n"
    
    # 数値列の平均
    numeric_cols = ['いいね数', 'コメント数', '保存数']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            avg = df[col].mean()
            if not pd.isna(avg):
                summary += f"{col}の平均: {avg:.1f}\n"
    
    # キャプション文字数
    if 'キャプション' in df.columns:
        avg_length = df['キャプション'].str.len().mean()
        summary += f"キャプション文字数の平均: {avg_length:.1f}文字\n"
    
    # ハッシュタグ数
    if 'ハッシュタグ' in df.columns:
        avg_tags = df['ハッシュタグ'].str.split().str.len().mean()
        summary += f"ハッシュタグ数の平均: {avg_tags:.1f}個\n"
    
    return summary





