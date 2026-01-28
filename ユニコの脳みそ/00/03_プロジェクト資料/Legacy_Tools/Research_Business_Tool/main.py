
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from data import PROPOSAL_TEMPLATES, RESEARCH_PROMPTS, CHECKLIST_QUESTIONS, SOP_TEMPLATES, HTML_REPORT_TEMPLATE
from utils import clear_screen, print_header, get_input, save_to_file, wait_for_enter
from ai_engine import analyze_search_results, generate_ai_proposal, set_api_key, get_api_key
from search_engine import search_with_retry
from report_generator import generate_html_report

def setup_api_key():
    """APIキーの設定を行う"""
    current_key = get_api_key()
    if current_key:
        print(f"\n>> OpenAI API Key is currently set: {current_key[:5]}...{current_key[-3:]}")
        if get_input("再設定しますか？ (y/n)", required=False).lower() != 'y':
            return

    print("\n>> Automation機能を使用するには OpenAI API Key が必要です。")
    key = get_input("OpenAI API Keyを入力 (入力しない場合はスキップ)", required=False)
    if key:
        set_api_key(key)
        print(">> API Keyを設定しました。")

def auto_research_report():
    print_header("【自動】AIリサーチレポート生成")
    print(">> Web検索とAI分析を組み合わせて、高品質なレポートを全自動生成します。\n")
    
    if not get_api_key():
        print("!! API Keyが設定されていません。メインメニューから設定してください。")
        wait_for_enter()
        return

    query = get_input("リサーチしたいキーワード (例: 2026年 美容トレンド)")
    filename_base = get_input("保存ファイル名のベース (例: Beauty_Trend)", required=False)
    if not filename_base:
        filename_base = "Research_Report"

    # 1. Web検索
    print(f"\n[1/3] Web検索を実行中: {query} ...")
    search_results = search_with_retry(query, num_results=5)
    if not search_results:
        print("!! 検索結果が見つかりませんでした。キーワードを変えて試してください。")
        wait_for_enter()
        return
    print(f">> {len(search_results)} 件の情報を取得しました。")

    # 2. AI分析
    print("\n[2/3] AIによる分析とレポート執筆中 (これには数十秒かかります)...")
    analysis_text = analyze_search_results(query, search_results)
    
    # 3. レポート生成
    print("\n[3/3] HTMLレポートを生成中...")
    report_data = {
        "title": f"Research Report: {query}",
        "ai_analysis": analysis_text,
        "search_results": search_results
    }
    
    filename = f"{filename_base}.html"
    if generate_html_report(report_data, filename, HTML_REPORT_TEMPLATE):
        print(f"\n>> 完了！ レポートを保存しました: {filename}")
        print(">> ブラウザで開いて確認してください。")
    else:
        print("\n!! レポート生成に失敗しました。")

    wait_for_enter()

def auto_proposal():
    print_header("【自動】AI提案文作成")
    print(">> 案件内容に合わせて、最適な提案文をAIが執筆します。\n")

    if not get_api_key():
        print("!! API Keyが設定されていません。")
        wait_for_enter()
        return

    genre = get_input("案件ジャンル")
    name = get_input("あなたの名前")
    hours = get_input("週稼働時間")

    print("\n>> AIが提案文を作成中...")
    proposal = generate_ai_proposal(genre, name, hours)

    print("\n" + "-"*30 + " 作成結果 " + "-"*30)
    print(proposal)
    print("-" * 70)

    if get_input("ファイルに保存しますか？ (y/n)", required=False).lower() == 'y':
        filename = f"Proposal_Auto_{genre}.txt"
        save_to_file(proposal, filename)
    
    wait_for_enter()

# --- Legacy Functions (Kept for manual usage) ---
def generate_proposal_manual():
    print_header("【手動】提案文ジェネレーター")
    template = PROPOSAL_TEMPLATES["default"]
    genre = get_input("案件ジャンル")
    name = get_input("あなたの名前")
    hours = get_input("週稼働時間")
    print(template.format(genre=genre, name=name, hours=hours))
    wait_for_enter()

def get_research_prompts():
    print_header("【手動】リサーチ用プロンプト集")
    print("[1] 競合分析 [2] レビュー分析 [3] ネタ出し")
    c = get_input("選択")
    # ... (Simplified for brevity, logic exists in v1)
    if c == "1": print(RESEARCH_PROMPTS["competitor"])
    elif c == "2": print(RESEARCH_PROMPTS["review"])
    elif c == "3": print(RESEARCH_PROMPTS["idea"])
    wait_for_enter()

def check_suitability():
    print_header("案件適合度チェック")
    score = 0
    for q in CHECKLIST_QUESTIONS:
        if get_input(f"{q['question']} (y/n)").lower().startswith('y'): score += 1
    print(f"Score: {score}/{len(CHECKLIST_QUESTIONS)}")
    wait_for_enter()

def generate_sop():
    print_header("SOP生成")
    task = get_input("タスク名")
    print(SOP_TEMPLATES["basic"].format(task_name=task))
    wait_for_enter()

def main_menu():
    # 初回起動時にAPIキー確認（あえて強制はしない）
    setup_api_key()

    while True:
        print_header("Research Business Tool v2.0 (Automation Edition)")
        print("\n--- Automation Features (AI + Web) ---")
        print("[1] AIリサーチレポート生成 (Auto Research)")
        print("[2] AI提案文作成 (Auto Proposal)")
        print("[3] API Key設定 (Config)")
        
        print("\n--- Manual Assistance Tools ---")
        print("[4] 提案文テンプレート (Manual)")
        print("[5] プロンプト表示 (Prompts)")
        print("[6] 適合度チェック (Check)")
        print("[7] SOP生成 (SOP)")
        
        print("\n[0] 終了 (Exit)")
        
        choice = input("\n>> 番号を選択: ").strip()

        if choice == "1": auto_research_report()
        elif choice == "2": auto_proposal()
        elif choice == "3": setup_api_key()
        elif choice == "4": generate_proposal_manual()
        elif choice == "5": get_research_prompts()
        elif choice == "6": check_suitability()
        elif choice == "7": generate_sop()
        elif choice == "0":
            print("\n>> 終了します。")
            sys.exit()
        else:
            print(">> 無効な入力です。")

if __name__ == "__main__":
    main_menu()
