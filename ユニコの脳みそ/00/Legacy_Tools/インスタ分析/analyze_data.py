"""
データ分析と可視化のモジュール
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional
import os
from config import OUTPUT_DIR

# 日本語フォント設定（Windowsの場合）
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")


def calculate_basic_stats(df: pd.DataFrame) -> dict:
    """
    基本的な統計情報を計算
    
    Args:
        df: 投稿データのDataFrame
        
    Returns:
        統計情報の辞書
    """
    stats = {}
    
    if df.empty:
        return stats
    
    # 数値列の統計
    numeric_cols = ['いいね数', 'コメント数', '保存数', 'リーチ数', 'インプレッション数']
    
    for col in numeric_cols:
        if col in df.columns:
            # 文字列を数値に変換
            df[col] = pd.to_numeric(df[col], errors='coerce')
            stats[f'{col}_平均'] = df[col].mean()
            stats[f'{col}_中央値'] = df[col].median()
            stats[f'{col}_最大'] = df[col].max()
            stats[f'{col}_最小'] = df[col].min()
    
    # キャプション文字数
    if 'キャプション' in df.columns:
        df['キャプション文字数'] = df['キャプション'].str.len()
        stats['キャプション文字数_平均'] = df['キャプション文字数'].mean()
        stats['キャプション文字数_最大'] = df['キャプション文字数'].max()
        stats['キャプション文字数_最小'] = df['キャプション文字数'].min()
    
    # ハッシュタグ数
    if 'ハッシュタグ' in df.columns:
        df['ハッシュタグ数'] = df['ハッシュタグ'].str.split().str.len()
        stats['ハッシュタグ数_平均'] = df['ハッシュタグ数'].mean()
        stats['ハッシュタグ数_最大'] = df['ハッシュタグ数'].max()
    
    # 投稿タイプ別の統計
    if '投稿タイプ' in df.columns:
        stats['投稿タイプ別件数'] = df['投稿タイプ'].value_counts().to_dict()
    
    return stats


def create_comparison_charts(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> List[str]:
    """
    自分と競合の比較グラフを作成
    
    Args:
        df: 投稿データのDataFrame
        output_dir: 出力ディレクトリ
        
    Returns:
        作成したグラフファイルのパスリスト
    """
    if df.empty or '投稿タイプ' not in df.columns:
        return []
    
    chart_paths = []
    
    # 数値列を数値型に変換
    numeric_cols = ['いいね数', 'コメント数', '保存数']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # キャプション文字数とハッシュタグ数を計算
    if 'キャプション' in df.columns:
        df['キャプション文字数'] = df['キャプション'].str.len()
    if 'ハッシュタグ' in df.columns:
        df['ハッシュタグ数'] = df['ハッシュタグ'].str.split().str.len()
    
    # 1. いいね数の比較（箱ひげ図）
    if 'いいね数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='いいね数', by='投稿タイプ', ax=ax)
        ax.set_title('いいね数の比較', fontsize=14, fontweight='bold')
        ax.set_xlabel('投稿タイプ')
        ax.set_ylabel('いいね数')
        plt.suptitle('')  # デフォルトのタイトルを削除
        path = os.path.join(output_dir, 'comparison_likes.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 2. キャプション文字数の比較
    if 'キャプション文字数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='キャプション文字数', by='投稿タイプ', ax=ax)
        ax.set_title('キャプション文字数の比較', fontsize=14, fontweight='bold')
        ax.set_xlabel('投稿タイプ')
        ax.set_ylabel('文字数')
        plt.suptitle('')
        path = os.path.join(output_dir, 'comparison_caption_length.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 3. ハッシュタグ数の比較
    if 'ハッシュタグ数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='ハッシュタグ数', by='投稿タイプ', ax=ax)
        ax.set_title('ハッシュタグ数の比較', fontsize=14, fontweight='bold')
        ax.set_xlabel('投稿タイプ')
        ax.set_ylabel('ハッシュタグ数')
        plt.suptitle('')
        path = os.path.join(output_dir, 'comparison_hashtags.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 4. 投稿時間帯の分布
    if '投稿時間帯' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        for post_type in df['投稿タイプ'].unique():
            subset = df[df['投稿タイプ'] == post_type]
            if '投稿時間帯' in subset.columns:
                # 時間を数値に変換（例: "19:00" -> 19.0）
                times = subset['投稿時間帯'].str.split(':').str[0].astype(float)
                ax.hist(times, alpha=0.5, label=post_type, bins=24)
        ax.set_title('投稿時間帯の分布', fontsize=14, fontweight='bold')
        ax.set_xlabel('時間（時）')
        ax.set_ylabel('投稿数')
        ax.legend()
        ax.set_xticks(range(0, 24, 2))
        path = os.path.join(output_dir, 'comparison_time.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 5. いいね数とキャプション文字数の相関
    if 'いいね数' in df.columns and 'キャプション文字数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        for post_type in df['投稿タイプ'].unique():
            subset = df[df['投稿タイプ'] == post_type]
            ax.scatter(
                subset['キャプション文字数'],
                subset['いいね数'],
                alpha=0.6,
                label=post_type
            )
        ax.set_title('いいね数とキャプション文字数の相関', fontsize=14, fontweight='bold')
        ax.set_xlabel('キャプション文字数')
        ax.set_ylabel('いいね数')
        ax.legend()
        path = os.path.join(output_dir, 'correlation_caption_likes.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    return chart_paths


def export_to_csv(df: pd.DataFrame, filename: str, output_dir: str = OUTPUT_DIR) -> str:
    """
    DataFrameをCSVファイルにエクスポート
    
    Args:
        df: エクスポートするDataFrame
        filename: ファイル名
        output_dir: 出力ディレクトリ
        
    Returns:
        エクスポートしたファイルのパス
    """
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return filepath


def export_to_excel(df_list: List[pd.DataFrame], sheet_names: List[str], filename: str, output_dir: str = OUTPUT_DIR) -> str:
    """
    複数のDataFrameをExcelファイルの別シートにエクスポート
    
    Args:
        df_list: エクスポートするDataFrameのリスト
        sheet_names: シート名のリスト
        filename: ファイル名
        output_dir: 出力ディレクトリ
        
    Returns:
        エクスポートしたファイルのパス
    """
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for df, sheet_name in zip(df_list, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return filepath





