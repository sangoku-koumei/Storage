
import streamlit as st
import json
import os
import time
from openai import OpenAI

# Optional: instagrapi
try:
    from instagrapi import Client
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False

st.set_page_config(page_title="Auto Reply", layout="wide", page_icon="💬")

# --- Constants & Setup ---
DATA_DIR = "c:\\Users\\user\\Desktop\\保管庫\\ユニコの脳みそ\\Automation_Tools\\data"
import base64

def load_credentials(profile):
    """Load credentials"""
    fpath = os.path.join(DATA_DIR, f"secrets_{profile}.json")
    if os.path.exists(fpath):
        try:
            with open(fpath, 'r') as f:
                creds = json.load(f)
                return creds.get("username"), base64.b64decode(creds.get("password")).decode()
        except:
            pass
    return "", ""

def scan_profiles():
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("strategy_") and f.endswith(".json")]
    profiles = [f.replace("strategy_", "").replace(".json", "") for f in files]
    return profiles if profiles else ["default"]

st.title("💬 Auto Reply | High-ROI Engagement")
st.markdown("「売上直結 (Lead Magnet)」と「バズ支援 (Engagement Boost)」に特化した返信ツールです。")

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
selected_profile = st.sidebar.selectbox("Select Profile", scan_profiles())

username, password = load_credentials(selected_profile)
if username:
    st.sidebar.success(f"🔑 Logged in as: {username}")
else:
    st.sidebar.warning("No credentials found. Save in 03 tool first.")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Strategy Config")
trigger_word = st.sidebar.text_input("Trigger Keyword (DM)", "詳細")
dm_template = st.sidebar.text_area("DM Template", "こんにちは！\nプレゼントはこちらです👇\nhttps://example.com/gift")
persona_tone = st.sidebar.selectbox("Reply Tone", ["親しみやすい", "エレガント・丁寧", "ミステリアス", "ビジネスライク"])

# --- Main Content ---
tab1, tab2 = st.tabs(["🛡️ Safe Mode (Manual)", "🤖 Auto Mode (Run Once)"])

# =======================
# TAB 1: SAFE MODE
# =======================
with tab1:
    st.subheader("🛡️ Safe Mode (Manual Assist)")
    st.info("AIが「最適な返信」や「DM文面」を生成します。コピペして手動送信してください。")
    
    col_input, col_output = st.columns(2)
    
    with col_input:
        user_comment = st.text_area("User Comment (貼り付け)", height=100, placeholder="例: すごく勉強になりました！詳細知りたいです！")
        
    with col_output:
        if user_comment:
            # 1. Check Trigger
            is_trigger = trigger_word in user_comment
            
            if is_trigger:
                st.success(f"🎯 Trigger '{trigger_word}' Detected!")
                st.markdown("### 📤 Recommended DM")
                st.text_area("DM Check", dm_template, height=100)
                st.caption("👈 Copy and send via DM")
                
                st.markdown("---")
                st.markdown("### 💬 Recommended Reply (Public)")
                st.info("「DM送りました！」と伝えると親切です。")
                reply_suggestion = f"コメントありがとうございます！\nDMにお送りしましたので、リクエストBOXをご確認ください📩"
                st.code(reply_suggestion, language="text")
                
            else:
                st.info("💬 Normal Engagement")
                if st.button("✨ Generate AI Question"):
                    if not api_key:
                        st.error("API Key required.")
                    else:
                        client = OpenAI(api_key=api_key)
                        with st.spinner("Thinking (Natural Mode)..."):
                            prompt = f"""
                            あなたは「{persona_tone}」なインスタグラマーです。
                            親友のような距離感で、以下のコメントに返信してください。

                            【絶対ルール】
                            1. **Reaction First**: いきなり質問せず、まず相手のコメントにリアクション（喜び・驚き・共感）してください。絵文字を使って感情を爆発させてください。
                            2. **Low Hurdle Question**: 最後に「はい/いいえ」や「AかB」で答えられる、とてつもなく簡単な質問を1つだけ添えてください。（オープンクエスチョン禁止）
                            
                            【悪い例】
                            AI: "勉強になりましたか？具体的にどこが？" (尋問っぽい・重い)
                            
                            【良い例】
                            AI: "わー！嬉しいです！😭✨ タイミング最高でしたね！今日からできそうですか？👀"

                            ユーザーのコメント: "{user_comment}"
                            """
                            try:
                                res = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=[{"role": "user", "content": prompt}]
                                )
                                ai_reply = res.choices[0].message.content
                                st.markdown("### 💬 AI Question Reply")
                                st.text_area("Reply Draft", ai_reply, height=100)
                            except Exception as e:
                                st.error(str(e))

# =======================
# TAB 2: AUTO MODE
# =======================
with tab2:
    st.subheader("🤖 Auto Mode (Run Once)")
    st.warning("⚠️ **Warning**: 最新の投稿の未読コメントをチェックし、1回だけ実行します。")
    
    if not INSTAGRAPI_AVAILABLE:
        st.error("❌ `instagrapi` not installed.")
    else:
        if st.button("🚀 Check & Reply (Latest Post)"):
            if not username or not password or not api_key:
                st.error("Credentials & API Key required.")
            else:
                status_log = st.empty()
                status_log.text("🔄 Logging in...")
                
                try:
                    cl = Client()
                    cl.login(username, password)
                    
                    # Get User ID & Latest Post
                    my_id = cl.user_id_from_username(username)
                    medias = cl.user_medias(my_id, amount=1)
                    
                    if not medias:
                        status_log.text("No posts found.")
                    else:
                        latest_media = medias[0]
                        status_log.text(f"📸 Checking Post: {latest_media.pk}")
                        
                        # Get Comments
                        comments = cl.media_comments(latest_media.pk, amount=20)
                        
                        action_count = 0
                        
                        client = OpenAI(api_key=api_key) # Init OpenAI
                        
                        for c in comments:
                            # Skip own comments
                            if str(c.user.pk) == str(my_id):
                                continue
                                
                            # Logic: In a real app, check DB if replied. 
                            # Here we just show what WOULD happen or reply if confident.
                            # For safety in this demo, we simulate logic.
                            
                            st.markdown(f"**@{c.user.username}**: {c.text}")
                            
                            # Trigger Check
                            if trigger_word in c.text:
                                st.success(f"  -> Trigger! Sending DM: '{dm_template[:20]}...'")
                                # cl.direct_send(dm_template, [c.user.pk])
                                # cl.media_comment(latest_media.pk, f"@{c.user.username} DM送りました！", replied_to_comment_id=c.pk)
                                st.caption("  (Simulation: DM Sent & Replied)")
                                action_count += 1
                            else:
                                st.info(f"  -> Engagement. Generating reply...")
                                # Generate AI Reply (Humanized)
                                prompt = f"""
                                あなたは「{persona_tone}」なインスタグラマーです。
                                以下のコメントに「Reaction First (感情優先)」かつ「Low Hurdle Question (Yes/Noで答えられる質問)」で返信して。
                                ユーザー: "{c.text}"
                                """
                                res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":prompt}])
                                ai_reply = res.choices[0].message.content
                                
                                st.text(f"     Bot: {ai_reply}")
                                # cl.media_comment(latest_media.pk, ai_reply, replied_to_comment_id=c.pk)
                                st.caption("  (Simulation: Reply Posted)")
                                action_count += 1
                        
                        status_log.success(f"✅ Processed {len(comments)} comments. Actions: {action_count}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
