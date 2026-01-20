"""
Google Sheets連携
サービスアカウントを使用してスプレッドシートにデータを書き込む
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List
from app.config import settings

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheets_client(service_account_json_path: str):
    """
    Google Sheetsクライアントを取得
    
    Args:
        service_account_json_path: サービスアカウントのJSONファイルパス
        
    Returns:
        gspreadクライアント
    """
    creds = Credentials.from_service_account_file(
        service_account_json_path,
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client


def append_log_rows(
    spreadsheet_id: str,
    sheet_name: str,
    rows: List[List[str]],
    service_account_json_path: str,
):
    """
    スプレッドシートに行を追加
    
    Args:
        spreadsheet_id: スプレッドシートID
        sheet_name: シート名
        rows: 追加する行のリスト（各行は文字列のリスト）
        service_account_json_path: サービスアカウントのJSONファイルパス
    """
    client = get_sheets_client(service_account_json_path)
    sh = client.open_by_key(spreadsheet_id)
    worksheet = sh.worksheet(sheet_name)
    worksheet.append_rows(rows, value_input_option="RAW")


def export_event_logs_to_sheets(
    spreadsheet_id: str,
    sheet_name: str,
    logs: List[dict],
    service_account_json_path: str,
):
    """
    アプリケーションイベントログをスプレッドシートにエクスポート
    
    Args:
        spreadsheet_id: スプレッドシートID
        sheet_name: シート名
        logs: ログのリスト（辞書形式）
        service_account_json_path: サービスアカウントのJSONファイルパス
    """
    if not logs:
        return
    
    # ヘッダー行
    headers = ["日時", "レベル", "ソース", "イベントタイプ", "メッセージ", "メタデータ"]
    
    # データ行
    rows = [headers]
    for log in logs:
        row = [
            log.get("created_at", ""),
            log.get("level", ""),
            log.get("source", ""),
            log.get("event_type", ""),
            log.get("message", ""),
            log.get("meta", ""),
        ]
        rows.append(row)
    
    append_log_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
        rows=rows,
        service_account_json_path=service_account_json_path,
    )


