
import streamlit as st
import json
import os
import pandas as pd
from openai import OpenAI
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Analytics Dashboard", layout="wide", page_icon="📊")

# --- Constants & Setup ---
DATA_DIR = "c:\\Users\\user\\Desktop\\保管庫\\ユニコの脳みそ\\Automation_Tools\\data"
LOG_DIR = os.path.join(DATA_DIR, "analytics_logs")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Helper Functions ---
def scan_profiles():
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("strategy_") and f.endswith(".json")]
    profiles = [f.replace("strategy_", "").replace(".json", "") for f in files]
    return profiles if profiles else ["default"]

def load_log(profile):
    """Load analytics log for a profile"""
    filepath = os.path.join(LOG_DIR, f"log_{profile}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_log(profile, log_data):
    """Save analytics log for a profile"""
    filepath = os.path.join(LOG_DIR, f"log_{profile}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=4)

def load_strategy(profile_name):
    filepath = os.path.join(DATA_DIR, f"strategy_{profile_name}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def update_strategy(profile_name, new_data):
    filepath = os.path.join(DATA_DIR, f"strategy_{profile_name}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

# --- UI ---
st.title("📊 Analytics Dashboard | 実績分析＆戦略進化")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    selected_profile = st.selectbox("Select Profile", scan_profiles())
    
    # Load Data
    current_log = load_log(selected_profile)
    current_strategy = load_strategy(selected_profile)

if not current_strategy:
    st.error("Strategy file missing. Please run 01_Research first.")
    st.stop()

# --- Main Layout ---
tab1, tab2, tab3 = st.tabs(["📈 Dashboard & Input", "📂 CSV Import", "🔄 Strategy Evolution"])

# TAB 1: Dashboard & Input
with tab1:
    col_kpi, col_chart = st.columns([1, 2])
    
    with col_kpi:
        st.subheader("📝 New Entry")
        with st.form("entry_form"):
            entry_date = st.date_input("Date", datetime.now())
            topic = st.text_input("Topic / Title", placeholder="Ex: 復縁のサイン5選")
            likes = st.number_input("Likes", min_value=0, value=0)
            saves = st.number_input("Saves", min_value=0, value=0)
            impressions = st.number_input("Impressions", min_value=0, value=0)
            notes = st.text_area("Notes (Qualitative)", placeholder="フォロワーからの反応など")
            
            if st.form_submit_button("💾 Save Record"):
                new_record = {
                    "date": entry_date.strftime("%Y-%m-%d"),
                    "topic": topic,
                    "likes": likes,
                    "saves": saves,
                    "impressions": impressions,
                    "notes": notes
                }
                current_log.append(new_record)
                save_log(selected_profile, current_log)
                st.success("Record Saved!")
                st.rerun()

    with col_chart:
        st.subheader("📈 Performance Trend")
        if current_log:
            df = pd.DataFrame(current_log)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Simple Line Chart
            chart_data = df.set_index('date')[['likes', 'saves']]
            st.line_chart(chart_data)
            
            with st.expander("Show Raw Data"):
                st.dataframe(df.sort_values('date', ascending=False))
        else:
            st.info("No data yet. Input records or import CSV.")

# TAB 2: CSV Import
with tab2:
    st.subheader("📂 Bulk Import via CSV")
    st.markdown("Expected Columns: `date`, `topic`, `likes`, `saves`, `impressions`, `notes`")
    
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        try:
            input_df = pd.read_csv(uploaded_file)
            st.dataframe(input_df.head())
            
            if st.button("🚀 Import Data"):
                # Convert to list of dicts and merge
                imported_data = input_df.to_dict(orient='records')
                
                # Basic validation/cleaning could go here
                # For simplicity, we just append (ensure string dates)
                for item in imported_data:
                    # Convert pandas timestamp to string if needed
                    if isinstance(item.get('date'), pd.Timestamp):
                        item['date'] = item['date'].strftime('%Y-%m-%d')
                    # Ensure basic fields exist
                    current_log.append(item)
                
                # Remove duplicates? (Project for another day, maybe strictly by date+topic)
                save_log(selected_profile, current_log)
                st.success(f"Imported {len(imported_data)} records!")
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# TAB 3: Strategy Evolution
with tab3:
    st.subheader("🔄 AI Strategy Update (Feedback Loop)")
    st.markdown("蓄積されたデータに基づき、戦略バイブルをアップデートします。")
    
    if not current_log:
        st.warning("No analytics data available to analyze.")
    else:
        # Show Top Performing Posts
        df = pd.DataFrame(current_log)
        if 'saves' in df.columns:
            top_posts = df.sort_values('saves', ascending=False).head(3)
            st.markdown("### 🏆 Top 3 Posts (by Saves)")
            for _, row in top_posts.iterrows():
                st.write(f"- **{row.get('topic', 'No Title')}**: {row.get('saves', 0)} Saves / {row.get('likes', 0)} Likes")
        
        if st.button("🚀 Analyze Trends & Update Strategy"):
            if not api_key:
                st.error("API Key required.")
            else:
                client = OpenAI(api_key=api_key)
                with st.spinner("AI is analyzing your historical performance..."):
                    # Prepare context
                    recent_log = current_log[-10:] # Last 10 records
                    context_str = json.dumps(recent_log, ensure_ascii=False)
                    
                    system_prompt = f"""
                    あなたは専属のSNS戦略コンサルタントです。
                    以下の「直近の投稿実績（Analytics Data）」を分析し、既存の戦略を洗練させてください。
                    
                    【実績データ（JSON）】
                    {context_str}
                    
                    【分析指示】
                    1. **Win Pattern**: 何が当たっているか（保存数が多い投稿の共通点）。
                    2. **Lose Pattern**: 何が滑っているか（インプの割に反応が低いもの）。
                    3. **Next Action**: 次の1週間で試すべき具体的な投稿テーマ案3つ。
                    
                    簡潔なMarkdown形式で出力してください。
                    """
                    
                    try:
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": system_prompt}]
                        )
                        insight = res.choices[0].message.content
                        
                        st.success("✅ Analysis Complete!")
                        st.markdown(insight)
                        
                        # Update Strategy File
                        new_entry = f"\n\n## 🔄 Periodic Analysis ({datetime.now().strftime('%Y-%m-%d')})\n" + insight
                        current_strategy['strategy_content'] += new_entry
                        current_strategy['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        update_strategy(selected_profile, current_strategy)
                        st.toast("Strategy Bible Updated Successfully!")
                        
                    except Exception as e:
                        st.error(f"AI Error: {e}")

