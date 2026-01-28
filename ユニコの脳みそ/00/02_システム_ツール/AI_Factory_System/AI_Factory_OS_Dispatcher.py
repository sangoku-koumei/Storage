import streamlit as st
import os
import pandas as pd
from datetime import datetime
import time
import subprocess
import json
import sys

# Configuration
STORAGE_DIR = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00"
LOG_FILE = os.path.join(STORAGE_DIR, "AI_Factory_Operation_Log.csv")

st.set_page_config(page_title="AI Factory OS - Digital Management Suite", layout="wide")

# --- Custom Premium CSS (Aesthetics Overhaul) ---
st.markdown("""
<style>
    /* Main Background & Typography */
    .stApp {
        background-color: #f1f5f9; /* Soft Slate/Gray for eye comfort */
        color: #0f172a;
    }
    h1, h2, h3 {
        color: #1e3a8a !important; /* Deep Professional Blue */
        font-family: 'Inter', 'Noto Sans JP', sans-serif;
        font-weight: 700;
        margin-bottom: 0.5rem !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important; /* Light Slate Sidebar */
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebarNav"] span {
        color: #1e293b !important;
        font-weight: 600;
    }
    
    /* Premium Cards */
    .expert-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Buttons - Clean Professional */
    .stButton > button {
        background-color: #2563eb !important; /* Professional Blue */
        color: #ffffff !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        width: 100%;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
        transform: translateY(-1px);
    }
    
    /* Inputs & Selectboxes - Absolute Readability */
    input, textarea, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #0f172a !important; /* Forces black/dark text */
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    
    /* Selectbox internal text force */
    div[data-baseweb="select"] span, 
    div[data-baseweb="select"] p,
    div[role="button"] {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* Labels - Clear Contrast */
    label, div[data-testid="stWidgetLabel"] p {
        color: #475569 !important; /* Muted Slate */
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 6px !important;
    }

    /* Dropdown Popovers - Light */
    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    li[role="option"] {
        color: #1e293b !important;
        padding: 12px !important;
    }
    li[role="option"]:hover {
        background-color: #f1f5f9 !important;
    }

    /* Global Text Visibility */
    .stMarkdown p, .stText {
        color: #334155 !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Professional Status Indicators */
    .stSuccess {
        background-color: #f0fdf4 !important;
        border-left: 5px solid #22c55e !important;
        color: #166534 !important;
    }
    .stInfo {
        background-color: #eff6ff !important;
        border-left: 5px solid #3b82f6 !important;
        color: #1e40af !important;
    }
</style>
""", unsafe_allow_html=True)

# --- App Content ---
st.markdown("<h1 style='text-align: center; color: #34d399;'>⚙️ AI Factory OS: Digital Management Suite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>次世代の業務自動化と知的資産管理のためのプロフェッショナル・ハブ</p>", unsafe_allow_html=True)

# Navigation
page = st.sidebar.radio("機能・プロトコル選択", [
    "【分析】顧客ヒアリング", 
    "【戦略】エキスパート・ブリーフィング", 
    "【制作】マーケティング・キット", 
    "【管理】プロジェクト・アーカイブ", 
    "【聖典】マニュアル・ナレッジハブ",
    "【運用】システム稼働ログ"
])

# Service Definitions (4 Low + 3 High)
SERVICES = {
    "【分析】市場リサーチ (Market Scout)": "市場動向と競合他社の分析に基づいた、戦略的インサイトの提供。",
    "【構築】SNS垂直起動 (Social Architect)": "ターゲット層の心理に最適化した、SNSプレゼンスの構築。",
    "【営業】B2B自動アプローチ (Lightning)": "確度の高いリードに対し、パーソナライズされたアプローチを自動化。",
    "【基盤】業務最適化マニュアル (Ops Order)": "複雑な業務フローを標準化し、誰でも実行可能なマニュアルに落とし込む。",
    "【成約】LINE接客シナリオ (Step Scenario)": "顧客のフェーズに合わせた自動応答による、高い成約率の実現。",
    "【導入】AI Factory OS 導入支援": "組織全体にAI駆動のワークフローを組み込み、自律的な事業運営を実現。",
    "【設計】事業モデル・アーキテクチャ": "持続可能な成長を実現するための、ビジネスモデルそのものの設計。"
}

if page == "【分析】顧客ヒアリング":
    st.header("📥 クライアント・ヒアリング")
    st.write("知識マップ: [[00_知識マップ]] | 運用マニュアル: [[Vol.75_クラウドワークス収益主権獲得・AI工場化完全攻略バイブル_深層対話]]")
    
    with st.form("intake_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("クライアント名", placeholder="例: ユニコ美容クリニック")
            service_type = st.selectbox("提供サービス", list(SERVICES.keys()))
        with col2:
            default_budget = 150000 if "【高】" in service_type else 30000
            budget = st.number_input("対価 (¥)", min_value=0, value=default_budget, step=10000)
            deadline = st.date_input("納品予定日")

        st.subheader("ビジネス課題の抽出 (Deep Analysis)")
        pains = st.text_area("根本的な課題（ペイン）", 
                           placeholder="クライアントが解決を熱望している「真の課題」は？")
        competition = st.text_area("競合・市場環境", 
                                 placeholder="競合他社と比較した際の弱み、または市場の機会は？")

        submitted = st.form_submit_button("AIエンジンを起動 ⚡")

    if submitted:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, stage in enumerate(["リクエスト処理中...", "データ構造解析中...", "AIエンジン準備中..."]):
            status_text.text(f"処理状況: {stage}")
            time.sleep(0.5)
            progress_bar.progress((i + 1) * 33)
            
        # Log entry
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Client": client_name,
            "Service": service_type,
            "Budget": budget,
            "Status": "進行中"
        }])
        
        if not os.path.exists(LOG_FILE):
            new_entry.to_csv(LOG_FILE, index=False)
        else:
            new_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)

        # Save Intake Report
        archive_dir = os.path.join(STORAGE_DIR, "AI_Factory_System", "Deliverables", client_name)
        os.makedirs(archive_dir, exist_ok=True)
        report_filename = f"00_ヒアリング結果_{client_name.replace(' ', '_')}.md"
        report_path = os.path.join(archive_dir, report_filename)
        report_content = f"# クライアント分析報告書: {client_name}\n日付: {datetime.now().strftime('%Y-%m-%d')}\nサービス: {service_type}\n予算想定: ¥{budget:,}\n\n## 根本的な課題（ペイン）\n{pains}\n\n## 競合・市場環境\n{competition}\n\n---\n*Generated by AI Factory OS*"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        # AUTO LAUNCH LOGIC & HANDOFF
        tool_launched = "None"
        handoff_data = {
            "client_name": client_name,
            "service": service_type,
            "keyword": pains.split('\n')[0][:50] if pains else client_name,
            "project_dir": archive_dir,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if "AIリサーチ" in service_type:
            tool_dir = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Legacy_Tools\Research_Business_Tool"
            tool_path = os.path.join(tool_dir, "app.py")
            with open(os.path.join(tool_dir, "handoff.json"), "w", encoding="utf-8") as f:
                json.dump(handoff_data, f, ensure_ascii=False, indent=2)
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", tool_path])
            tool_launched = "Research Business Tool"
        elif "営業DM" in service_type:
            tool_dir = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Legacy_Tools\Sales_Automation_Tool"
            tool_path = os.path.join(tool_dir, "app.py")
            with open(os.path.join(tool_dir, "handoff.json"), "w", encoding="utf-8") as f:
                json.dump(handoff_data, f, ensure_ascii=False, indent=2)
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", tool_path])
            tool_launched = "Sales Automation Tool"
        elif "SNS" in service_type:
            tool_dir = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Demo_Instagram_AI"
            tool_path = os.path.join(tool_dir, "app.py")
            with open(os.path.join(tool_dir, "handoff.json"), "w", encoding="utf-8") as f:
                json.dump(handoff_data, f, ensure_ascii=False, indent=2)
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", tool_path])
            tool_launched = "Instagram AI Suite"

        st.session_state['last_intake_success'] = {
            "client": client_name,
            "service": service_type,
            "tool": tool_launched
        }

    if 'last_intake_success' in st.session_state:
        success = st.session_state['last_intake_success']
        st.success(f"✅ プロジェクト「{success['client']}」の登録完了。")
        
        if success['tool'] != "None":
            st.info(f"🚀 **{success['tool']} を自動起動しました。**\nブラウザの別タブまたは新規ウィンドウを確認してください。")
            st.caption(f"Debug: Using Python at {sys.executable}")
        
        st.markdown("---")
        st.write("もしツールが起動しない場合は、以下のコマンドをターミナルで実行してください。")
        if "AIリサーチ" in success['service']:
            st.code(f"streamlit run \"c:\\Users\\user\\Desktop\\保管庫\\ユニコの脳みそ\\00\\Legacy_Tools\\Research_Business_Tool\\app.py\"")
        
        if st.button("新しい案件を入力する"):
            del st.session_state['last_intake_success']
            st.rerun()

elif page == "【戦略】エキスパート・ブリーフィング":
    st.header("⚖️ 戦略ブリーフィング（Expert Briefing）")
    st.markdown("各分野のエキスパート視点で、プロジェクトの戦略を多角的に分析します。")
    
    archive_base = os.path.join(STORAGE_DIR, "AI_Factory_System", "Deliverables")
    selected_client = "新規（手入力）"
    if os.path.exists(archive_base):
        clients = [d for d in os.listdir(archive_base) if os.path.isdir(os.path.join(archive_base, d))]
        if clients:
            selected_client = st.selectbox("分析対象の顧客データを選択", ["新規（手入力）"] + clients)
    
    initial_text = ""
    if selected_client != "新規（手入力）":
        report_path = os.path.join(archive_base, selected_client, "00_Intake_Report.md")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                initial_text = f.read()

    input_text = st.text_area("分析コンテキスト", value=initial_text, height=200)
    
    if st.button("エキスパート・ミーティングを開始"):
        st.markdown(f"### 戦略分析：{selected_client if selected_client != '新規（手入力）' else '新規案件'}")
        
        experts = {
            "戦略参謀（ユニコ）": "「価値の再定義が必要です。市場の独占点を見極めてください。」",
            "価値設計（アキシオロジー）": "「顧客の無知を利益に変えるのではなく、透明性を持って価値を最大化しましょう。」",
            "ビジネス心理（マキャベリ）": "「強固な信頼関係は、毅然とした態度と圧倒的な規律から生まれます。」",
            "ゲーム理論（ナッシュ）": "「双方がWin-Winとなる均衡点を設計し、LTVを最大化させます。」",
            "顧客満足（セラフィム博士）": "「不安を丁寧に取り除き、期待を超える成果物で感動を提供してください。」"
        }
        
        debate_result = f"## 戦略分析会議結果：{selected_client}\n日付: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for name, quote in experts.items():
            st.markdown(f"""
            <div class="expert-card">
                <strong>{name}</strong>: {quote}
            </div>
            """, unsafe_allow_html=True)
            debate_result += f"### {name}\n{quote}\n\n"
            
        st.session_state['last_debate_result'] = debate_result
        st.info("💡 専門家の分析に基づき、具体的な実行プランを策定してください。")

    if 'last_debate_result' in st.session_state and selected_client != "新規（手入力）":
        if st.button("この分析結果をプロジェクト書庫に保存する"):
            client_dir = os.path.join(archive_base, selected_client)
            save_path = os.path.join(client_dir, f"01_Strategy_Analysis_{datetime.now().strftime('%H%M%S')}.md")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(st.session_state['last_debate_result'])
            st.success(f"💾 プロジェクト資産として保存されました: {save_path}")

elif page == "【制作】マーケティング・キット":
    st.header("📣 プロフェッショナル・マーケティング・キット")
    st.markdown("ブランド価値を最大化するための「コピー・テンプレート」を生成。")
    
    target_job = st.text_input("案件/業界", placeholder="例: 整骨院、士業、D2Cブランド")
    if st.button("マーケティング案を制作"):
        st.subheader("1. クラウドワークス応募・提案文")
        cw_proposal = f"""
【ご提案】{target_job}の現状を「AI工場」で抜本的に改変します。

多くの提案は「作業の代行」ですが、私はそれらを排し、
15万文字の戦略バイブルに裏打ちされた『主権の算術』による
劇的な売上改変を提案します。

適性があるかどうか、こちらのヒアリング（イニシエーション）を通過した場合のみ、詳細を提示します。
        """
        st.code(cw_proposal)
        
        st.subheader("2. SNS威圧的プロフィール")
        sns_profile = f"""
- **名前**: {target_job}専門・AI主権建築士
- **バイオ**: 労働を捨て、主権を握る。| AI Factory OS 開発者 | 
  従来の{target_job}運営を「旧世代の遺物」として解体。 
  | ヒアリング通過者のみに「救済（成果物）」を提供。
        """
        st.markdown(sns_profile)

        st.subheader("3. 50ステップ・モジュール型LINE構築案")
        line_plan = f"""
聖典 `[[50_Step_Module_Construction_Template]]` に基づき、**{target_job}** に最適化された50通のモジュール構造を錬成しました。
これをこのままCursorへの指示書として使用できます。

---

### 【構成案：{target_job}覇権シナリオ】

**M1：入口・信頼構築 (Scout Phase)**
- 1-1: 【祝祭】{target_job}の呪いを解く、最初の一歩
... (中略) ...
**M9：長期ナーチャリング (Eternal Covenant)**
- 定期的な「知能の配給」と、次なる帝国の開拓準備。
        """
        st.markdown(line_plan)
        
        # Persistent storage of the kit for saving
        archive_content = f"# マーケティングキット: {target_job}\n\n## クラウドワークス応募文\n{cw_proposal}\n\n## SNSプロフィール\n{sns_profile}\n\n## LINE構築案\n{line_plan}"
        st.session_state['last_mkt_kit'] = archive_content

    if 'last_mkt_kit' in st.session_state:
        st.markdown("---")
        archive_base = os.path.join(STORAGE_DIR, "AI_Factory_System", "Deliverables")
        if os.path.exists(archive_base):
            clients = [d for d in os.listdir(archive_base) if os.path.isdir(os.path.join(archive_base, d))]
            if clients:
                target_client = st.selectbox("保存先の顧客を選択", clients, key="mkt_save_client")
                if st.button("このマーケティング案をアーカイブに保存する"):
                    save_path = os.path.join(archive_base, target_client, f"02_Marketing_Plan_{datetime.now().strftime('%H%M%S')}.md")
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(st.session_state['last_mkt_kit'])
                    st.success(f"💾 プロジェクト資産として保存されました: {save_path}")

elif page == "【管理】プロジェクト・アーカイブ":
    st.header("🗄️ プロジェクト・アーカイブ")
    st.markdown("登録されたプロジェクトと、生成された成果物の書庫です。")
    
    archive_base = os.path.join(STORAGE_DIR, "AI_Factory_System", "Deliverables")
    if os.path.exists(archive_base):
        clients = [d for d in os.listdir(archive_base) if os.path.isdir(os.path.join(archive_base, d))]
        if clients:
            selected_client = st.selectbox("閲覧するプロジェクトを選択", clients)
            client_dir = os.path.join(archive_base, selected_client)
            
            files = sorted(os.listdir(client_dir))
            selected_file = st.sidebar.selectbox("書類を選択", files)
            
            file_path = os.path.join(client_dir, selected_file)
            
            # --- ファイル管理アクションエリア ---
            st.markdown(f"### 📄 書類: {selected_file}")
            m_col1, m_col2, m_col3 = st.columns([2, 2, 6])
            
            # 1. 読込/表示 (デフォルト)
            with m_col1.popover("📝 名前を変更"):
                new_name = st.text_input("新しいファイル名 (.md/csv込み)", value=selected_file)
                if st.button("確定", key=f"f_ren_{selected_file}"):
                    if new_name and new_name != selected_file:
                        try:
                            os.rename(file_path, os.path.join(client_dir, new_name))
                            st.success("変更完了")
                            st.rerun()
                        except Exception as e:
                            st.error(f"エラー: {e}")
            
            if m_col2.button("🗑️ 削除", key=f"f_del_{selected_file}"):
                try:
                    os.remove(file_path)
                    st.success("削除しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"エラー: {e}")

            st.markdown("---")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "00_Intake_Report.md" in selected_file:
                st.info("💡 このプロジェクトに関連する外部ツールを起動できます。")
                
                # Logic for Handoff in Archive
                lines = content.split('\n')
                keyword_hint = selected_client
                service_type_hint = "AIリサーチ"
                for i, line in enumerate(lines):
                    if "## 根本的な課題（ペイン）" in line:
                        # Find the first non-empty line after the header
                        for j in range(i+1, len(lines)):
                            if lines[j].strip():
                                keyword_hint = lines[j].strip()[:50]
                                break
                    if "サービス:" in line: # Archive format uses 'サービス: ...'
                        service_type_hint = line.replace("サービス:", "").strip()
                        
                handoff_data = {
                    "client_name": selected_client,
                    "service": service_type_hint, # Added service type hint
                    "keyword": keyword_hint,
                    "project_dir": client_dir, # Changed project_path to client_dir
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                col_a, col_b, col_c = st.columns(3)
                research_dir = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Legacy_Tools\Research_Business_Tool"
                sales_dir = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Legacy_Tools\Sales_Automation_Tool"
                sns_dir = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Demo_Instagram_AI"

                with col_a:
                    if st.button("🚀 リサーチ起動"):
                        with open(os.path.join(research_dir, "handoff.json"), "w", encoding="utf-8") as f:
                            json.dump(handoff_data, f, ensure_ascii=False, indent=2)
                        subprocess.Popen([sys.executable, "-m", "streamlit", "run", os.path.join(research_dir, "app.py")])
                        st.success("Research Tool launched!")
                with col_b:
                    if st.button("🚀 営業DM起動"):
                        with open(os.path.join(sales_dir, "handoff.json"), "w", encoding="utf-8") as f:
                            json.dump(handoff_data, f, ensure_ascii=False, indent=2)
                        subprocess.Popen([sys.executable, "-m", "streamlit", "run", os.path.join(sales_dir, "app.py")])
                        st.success("Sales Tool launched!")
                with col_c:
                    if st.button("🚀 SNS分析起動"):
                        with open(os.path.join(sns_dir, "handoff.json"), "w", encoding="utf-8") as f:
                            json.dump(handoff_data, f, ensure_ascii=False, indent=2)
                        subprocess.Popen([sys.executable, "-m", "streamlit", "run", os.path.join(sns_dir, "app.py")])
                        st.success("SNS Tool launched!")
                
                st.caption("※ボタンを押すと、各ツールがデータを持って自動起動します。")
            
            st.markdown("---")
            st.markdown(content)
        else:
            st.warning("まだ保存されたプロジェクトがありません。")
    else:
        st.warning("アーカイブ・ディレクトリが見つかりません。")

elif page == "【聖典】マニュアル・ナレッジハブ":
    st.header("📖 聖典・マニュアル・ナレッジハブ")
    st.markdown("AI Factory OS の全知能とプロトコルを集約した聖典ライブラリです。")
    
    docs = {
        "📊 SNS分析ツール・マニュアル": os.path.join(STORAGE_DIR, "Demo_Instagram_AI", "SNS_AI_ANALYSIS_TOOL_MANUAL.md"),
        "📜 共通執筆ルール（憲法）": os.path.join(STORAGE_DIR, "00_共通執筆ルール.md"),
        "🗺️ 総合知識マップ": os.path.join(STORAGE_DIR, "00_知識マップ.md")
    }
    
    selected_doc = st.selectbox("閲覧する聖典を選択してください", list(docs.keys()))
    doc_path = docs[selected_doc]
    
    if os.path.exists(doc_path):
        st.markdown("---")
        with open(doc_path, "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    else:
        st.error(f"ファイルが見つかりません: {doc_path}")

elif page == "【運用】システム稼働ログ":
    st.header("📊 システム稼働ログ")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("稼働ログの記録がまだありません。")

    st.subheader("🚀 外部ツール・クイック起動")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Omniscient Scout (リサーチ)"):
            research_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Legacy_Tools\Research_Business_Tool\app.py"
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", research_path])
            st.success("Scout launched!")
            
    with col2:
        if st.button("Lightning Strike (営業DM)"):
            sales_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Legacy_Tools\Sales_Automation_Tool\app.py"
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", sales_path])
            st.success("Lightning launched!")
            
    with col3:
        if st.button("Visual Resonance (SNS分析)"):
            sns_path = r"c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Demo_Instagram_AI\app.py"
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", sns_path])
            st.success("SNS Tool launched!")

    st.caption("※「ポート使用中」等のエラーが出る場合は、READMEに記載の `Stop-Process` コマンドを実行してください。")

st.caption("AI Factory System - Grand Design Rev.2 | Built with the 00 Protocol.")
