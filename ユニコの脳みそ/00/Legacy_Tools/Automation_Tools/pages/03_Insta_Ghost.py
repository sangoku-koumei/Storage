import streamlit as st
import qrcode
import io
import os
import time
import base64
import json
from openai import OpenAI

# KEYWORDS: [Insta_Ghost, Safe_Mode, QR_Transfer, API_Auto_Post, Stealth_Post, Vol.43_VGS]
# DESCRIPTION: Instagram専用の投稿支援ツール。Vol.43『美学と共鳴』を実装し、V-G-Sキャプション生成、QR連携、API自動投稿をワンストップで提供する。

# Optional: instagrapi (Catch error if not installed)
try:
    from instagrapi import Client
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False

st.set_page_config(page_title="Insta Ghost", layout="wide", page_icon="📸")

# --- Constants ---
# Use the common data directory in Automation_Tools
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# --- Helper Functions ---
def scan_profiles():
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("content_") and f.endswith(".json")]
    profiles = [f.replace("content_", "").replace(".json", "") for f in files]
    return profiles if profiles else []

def load_draft(profile_name):
    filename = f"content_{profile_name}.json"
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def save_credentials(profile, username, password):
    creds = {
        "username": username,
        "password": base64.b64encode(password.encode()).decode()
    }
    with open(os.path.join(DATA_DIR, f"secrets_{profile}.json"), 'w') as f:
        json.dump(creds, f)

def load_credentials(profile):
    fpath = os.path.join(DATA_DIR, f"secrets_{profile}.json")
    if os.path.exists(fpath):
        try:
            with open(fpath, 'r') as f:
                creds = json.load(f)
                return creds.get("username"), base64.b64decode(creds.get("password")).decode()
        except:
            pass
    return "", ""

# --- Main UI ---
st.title("📸 Insta Ghost | Instagram Stealth Suite")
st.markdown("""
Vol.43『美学と共鳴』を実装。V-G-Sストーリーテリングによるキャプション生成から、QR連携・自動投稿までをカバーします。
""")

# --- Sidebar ---
st.sidebar.header("📂 Draft Station")
available_profiles = scan_profiles()
selected_profile = st.sidebar.selectbox("Select Profile", available_profiles if available_profiles else ["default"])

# Credential Manager
st.sidebar.markdown("---")
st.sidebar.subheader("🔐 IG Credentials")
saved_user, saved_pass = load_credentials(selected_profile)
ig_user = st.sidebar.text_input("IG Username", value=saved_user)
ig_pass = st.sidebar.text_input("IG Password", type="password", value=saved_pass)

if st.sidebar.button("💾 Save Credentials"):
    save_credentials(selected_profile, ig_user, ig_pass)
    st.sidebar.success("Saved!")

st.sidebar.markdown("---")
openai_key = st.sidebar.text_input("OpenAI API Key (Genesis)", type="password")

# --- Tabs ---
tab_gen, tab_safe, tab_auto = st.tabs(["🌌 Genesis (Content)", "🛡️ Safe Mode (Manual)", "🤖 Auto Mode (API)"])

with tab_gen:
    st.subheader("🌌 Vol.43 V-G-S Caption Generator")
    st.info("『共鳴』を生むV-G-S（脆弱性・成長・成功）ストーリーテリングでキャプションを生成します。")
    
    topic = st.text_input("Post Topic", placeholder="例: 繊細さん（HSP）が起業で成功する理由")
    target_vibe = st.select_slider("Visual Vibe", options=["Minimal", "Dark_Luxury", "Pop_Art", "Natural"])
    
    post_type = st.radio("Content Type", ["Feed Post (V-G-S)", "Stories Sequence (Vol.43 Interactive)"], horizontal=True)

    if st.button("🎭 Generate Content"):
        if not openai_key or not topic:
            st.error("API Key and Topic are required.")
        else:
            try:
                client = OpenAI(api_key=openai_key)
                
                if post_type.startswith("Feed"):
                    prompt = f"""
                    Vol.43『Instagram拡散と共鳴の極意』に基づき、以下のテーマで投稿キャプションを作成せよ。
                    テーマ: {topic}
                    Vibe: {target_vibe}
                    
                    【要件】
                    1. V-G-Sストーリーテリング (Vulnerability, Growth, Success) を適用。
                       - まず「過去の弱さ/失敗」をさらけ出し、共感を呼ぶ。
                    2. 1行目は「視覚的フック」となる強力な言葉（改行でスペースを空ける）。
                    3. 本文は「保存」を促すためのチェックリストまたはまとめ形式を含めること。
                    4. 関連ハッシュタグを30個厳選（Vol.43『Core/Community/Big』の黄金比率）。
                    5. Output JSON Keys: 'caption'
                    """
                else:
                    # Stories Logic
                    prompt = f"""
                    Vol.43に基づき、テーマ「{topic}」で「3枚構成のストーリーズ台本」を作成せよ。
                    Vibe: {target_vibe}
                    
                    【構成】
                    Slide 1 (Hook): 質問や衝撃的な事実で指を止めさせる。[STAMP: Question]
                    Slide 2 (Interaction): ユーザーに参加させる。[STAMP: Poll/Slider]
                    Slide 3 (CTA): マネタイズやNoteへ誘導する。[LINK: URL]
                    
                    出力は1つのテキストブロックにまとめること。
                    Output JSON Keys: 'caption' (Use this key for the script body)
                    """
                
                with st.spinner("Generating Resonance..."):
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "You are an Instagram Strategy Expert (Vol.43)."}, {"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    generated = json.loads(res.choices[0].message.content)
                    caption = generated.get("caption", "")
                    
                    # Save to draft
                    new_data = {"feed_script": caption, "post_title": topic}
                    with open(os.path.join(DATA_DIR, f"content_{selected_profile}.json"), 'w', encoding='utf-8') as f:
                        json.dump(new_data, f, ensure_ascii=False, indent=2)
                    
                    st.success("✅ Generated & Saved to Draft!")
                    st.text_area("Generated Content", value=caption, height=300)
                
            except Exception as e:
                st.error(f"Error: {e}")

with tab_safe:
    st.subheader("🛡️ Safe Mode (Manual Assist)")
    st.info("ブラウザで投稿画面を開き、テキストやQRコードでスマホ連携を支援します。")
    
    # Reload draft
    draft_data = load_draft(selected_profile)
    cap = draft_data.get("feed_script", "") if draft_data else ""
    
    st.text_area("Caption Draft (Saved)", value=cap, height=200, key="safe_cap")
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚀 Open Instagram (Create)", "https://www.instagram.com/create/select/")
    with col2:
        if cap:
            qr_img = generate_qr(cap[:300])
            img_byte_arr = io.BytesIO()
            qr_img.save(img_byte_arr, format='PNG')
            st.image(img_byte_arr, width=200, caption="Transfer to Phone via QR")

with tab_auto:
    st.subheader("🤖 Auto Mode (API Post)")
    st.warning("⚠️ **警告**: 自動投稿はアカウント停止のリスクがあります。サブ垢推奨。")
    
    if not INSTAGRAPI_AVAILABLE:
        st.error("❌ `instagrapi` がインストールされていません。")
    else:
        uploaded_file = st.file_uploader("Image to Post (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
        # Reload draft
        draft_data = load_draft(selected_profile)
        initial_cap = draft_data.get("feed_script", "") if draft_data else ""
        final_caption = st.text_area("Final Caption", value=initial_cap, height=150, key="auto_cap")
        
        if st.button("🚀 Upload to Instagram"):
            if not ig_user or not ig_pass or not uploaded_file:
                st.error("ユーザー名、パスワード、および画像が必要です。")
            else:
                try:
                    temp_path = f"temp_ig_{int(time.time())}.jpg"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.info("Logging in to Instagram...")
                    cl = Client()
                    cl.login(ig_user, ig_pass)
                    
                    st.info("Uploading media...")
                    media = cl.photo_upload(temp_path, final_caption)
                    st.success(f"✅ Success! Media PK: {media.pk}")
                    os.remove(temp_path)
                except Exception as e:
                    st.error(f"Failed: {e}")
