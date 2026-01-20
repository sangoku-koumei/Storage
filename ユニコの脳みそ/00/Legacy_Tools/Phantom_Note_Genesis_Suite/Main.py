import streamlit as st
import qrcode
import io
import json
import os
import time
import base64
import requests
import re
from openai import OpenAI

# KEYWORDS: [Phantom_Note_Zero, Genesis_2.0, DALL-E_3, Stealth_Post, Deep_Paywall]
# DESCRIPTION: Phantom Note Genesis 2.0 のメインUI。トピック入力から戦略策定、生成、画像挿入、投稿までを全自動化するNOTE専用の最終兵器。

# Core Engine Import (Local)
try:
    from engine import NoteStealthPoster
    NOTE_AUTO_AVAILABLE = True
except ImportError:
    NoteStealthPoster = None
    NOTE_AUTO_AVAILABLE = False

st.set_page_config(page_title="Phantom Note Genesis", layout="wide", page_icon="👻")

# --- Constants ---
# Use local data directory within the suite
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
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

# --- UI Setup ---
st.title("👻 Phantom Note Genesis | 究極のnote資産化ツール")
st.markdown("""
3.5万文字超の販売戦略バイブルと2026年最新トレンドを学習した、note専用の全自動生成・投稿スイートです。
""")

# --- Sidebar ---
st.sidebar.header("📂 Profile Logic")
available_profiles = scan_profiles()
selected_profile = st.sidebar.selectbox("Select Profile", available_profiles if available_profiles else ["default"])

# Credential Manager
st.sidebar.markdown("---")
st.sidebar.subheader("🔐 Note Credentials")
saved_user, saved_pass = load_credentials(selected_profile)
note_user = st.sidebar.text_input("Note Email", value=saved_user)
note_pass = st.sidebar.text_input("Note Password", type="password", value=saved_pass)

if st.sidebar.button("💾 Save Credentials"):
    save_credentials(selected_profile, note_user, note_pass)
    st.sidebar.success("Saved!")

# --- Main Tabs ---
tab_zero, tab_manual = st.tabs(["🚀 Phantom Note Zero (Genesis)", "🛡️ Manual Assist"])

with tab_zero:
    st.subheader("🌌 One-Button Content Factory")
    st.info("トピック入力だけで「戦略策定 → 執筆 → 4パターン画像生成 → ステルス投稿」を完結させます。")
    
    zero_topic = st.text_input("💡 記事のテーマ (Topic)", placeholder="例: 生成AIで副業月5万稼ぐ方法")
    openai_key = st.text_input("OpenAI API Key", type="password")
    
    genesis_mode = st.toggle("🌌 Genesis Expert Mode", value=True)
    
    # Vol.42 Authority Personas
    st.markdown("---")
    st.subheader("🧙‍♂️ Sage Projection (Persona)")
    persona_map = {
        "Oracle (Empire Strategist)": "You are 'Oracle', the Ruthless Strategist. Focus on monetization, authority, and empire building. Tone: Commanding, Absolute, Strategic.",
        "Dr. Ashley (Psychologist)": "You are 'Dr. Ashley', the Cognitive Psychologist. Focus on deep empathy, trauma hacking, and cognitive biases. Tone: Intellectual, Persuasive, Deep.",
        "Z (Algorithm Researcher)": "You are 'Z', the Logic Keeper. Focus on data, SEO, google algorithms, and logical proof. Tone: Cold, Precise, Analytical.",
        "M (Brand Director)": "You are 'M', the Aesthetic Narrator. Focus on storytelling, worldview, and emotional resonance. Tone: Artistic, Poetic, Heroic."
    }
    selected_persona_key = st.selectbox("Select Author Persona", list(persona_map.keys()))
    selected_system_prompt = persona_map[selected_persona_key]
    
    if st.button("🎭 Execute COMPLETE Genesis Pipeline"):
        if not zero_topic or not note_user or not note_pass or not openai_key:
            st.error("入力項目が不足しています。")
        else:
            client = OpenAI(api_key=openai_key)
            poster = NoteStealthPoster(headless=False) if NoteStealthPoster else None
            
            if not poster:
                st.error("Engine failed to load.")
                st.stop()
                
            try:
                # 1. Stage 1: Target Insight (Vol.40 Three-Layer Insight)
                st.info(f"👁️ Stage 1: Abyss Gazing (深層インサイト観測中)... by {selected_persona_key}")
                insight_prompt = f"""
                Vol.40バイブルに基づき、テーマ「{zero_topic}」を深層分析せよ。
                ターゲットの心理を以下の『三層インサイト』で言語化すること。
                1. 表層（顕在ニーズ）
                2. 中層（怒り・社会への不満）
                3. 深層（根源的な恐怖・救済への飢餓）
                
                さらに『呪いの言葉』（深夜に独りで検索するようなネガティブワード）を5つ特定せよ。
                JSON Keys: 'intent', 'three_layers' {{'surface', 'middle', 'deep'}}, 'curse_words', 'keywords', 'harmonic_title_templates', 'harm_category'
                """
                res1 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": selected_system_prompt + " (Specialization: Insight Analysis)"}, {"role": "user", "content": insight_prompt}],
                    response_format={"type": "json_object"}
                )
                strategy = json.loads(res1.choices[0].message.content)
                st.success(f"✅ Reality Fixed (観測完了): {strategy.get('keywords', [])}")

                # 2. Stage 2: Copywriting (Vol.40 PASBECAS + Deep Paywall)
                st.info(f"🖋 Step 2: 究極のPASBECAS × Deep Paywall 構築中... by {selected_persona_key}")
                writing_prompt = f"""
                戦略: {strategy} を基に、Vol.40『PASBECAS』×Vol.42『神格化ライティング』で記事を執筆せよ。
                あなたのペルソナ（{selected_persona_key}）の口調と哲学を強く反映させること。
                
                【構成要件】
                - 10,000文字級の熱量を持たせる
                - Lead: 読者に『心理的借金』を負わせる（与えすぎる無料情報の質）
                - Body: 『敵』を設定し、既存の常識を破壊（パラダイムシフト）
                - Deep Paywall: 全体の80%を無料公開。有料ライン直前で『情報の空白』を作り、飢餓感を最大化する。
                - Closing: Vol.41『Metaphysical Closing』行動を儀式化する文章。
                
                出力はJSON形式。
                JSON Keys: 'post_title', 'content_draft' (Markdown)
                """
                res2 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": selected_system_prompt + " (Specialization: Copywriting)"}, {"role": "user", "content": writing_prompt}],
                    response_format={"type": "json_object"}
                )
                draft = json.loads(res2.choices[0].message.content)
                st.success("✅ Information Body Materialized (情報身体生成完了)")

                # 3. Stage 3: Visual & Format (Vol.41 Visual Domination + Vol.42 EEAT)
                st.info("⚖️ Step 3: V-EEAT Authority Design (権威性視覚化)... [Vol.42 Method]")
                review_prompt = f"""
                記事: {draft.get('content_draft')}
                """
                # Note: Keeping the Editor prompt separate for objectivity, or blending it?
                # Promoting 'M' (Aesthetics) or 'Z' (Structure) usually works best for editing.
                # Let's keep the user selected persona active to maintain tone consistency during headers/bolding.
                
                review_prompt_detailed = f"""
                記事: {draft.get('content_draft')}
                
                【指示】
                1. Vol.42『V-EEAT』に基づき、権威性を高める画像タグ [IMAGE: type: prompt] を4つ以上挿入せよ。
                   - Type: 'Graph' (論理支配), 'Photo' (リアリティ), 'Art' (世界観), 'Thumbnail' (集客)
                   - Prompt: DALL-E 3用。具体的かつ高品質な指示（例: 'A photorealistic luxury office...'）
                2. 文章の重要な箇所（キラーフレーズ）を太字強調。
                3. 見出し（##, ###）を適切に配置し、読みやすさを最適化。
                
                JSON Keys: 'post_title', 'feed_script'
                """
                res3 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": selected_system_prompt + " (Specialization: Editor & Closer)"}, {"role": "user", "content": review_prompt_detailed}],
                    response_format={"type": "json_object"}
                )
                content = json.loads(res3.choices[0].message.content)
                g_title = content.get("post_title", draft.get("post_title"))
                g_body = content.get("feed_script", "")
                st.success("✅ Authority Established (権威構築完了)")

                # 4. Image Generation
                img_matches = re.findall(r'\[IMAGE: (?:([^:]+): )?([^\]]+)\]', g_body)
                temp_img_dir = os.path.join(DATA_DIR, f"temp_zero_{int(time.time())}")
                os.makedirs(temp_img_dir, exist_ok=True)
                
                for i, (img_type, p) in enumerate(img_matches):
                    st.info(f"🎨 画像 {i+1} 生成中... ({img_type if img_type else 'Normal'})")
                    st.caption(f"📝 Prompt: {p}")
                    img_res = client.images.generate(model="dall-e-3", prompt=p, n=1, size="1024x1024")
                    url = img_res.data[0].url
                    img_data = requests.get(url).content
                    img_name = f"image_{i}.jpg"
                    img_path = os.path.join(temp_img_dir, img_name)
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    
                    tag_to_replace = f"[IMAGE: {img_type + ': ' if img_type else ''}{p}]"
                    g_body = g_body.replace(tag_to_replace, f"[IMAGE:{img_name}]")
                    st.image(img_path, width=400)

                # 5. Posting
                st.info("🕰 時間帯チェック & ステルス投稿開始...")
                if not poster.is_safe_time():
                    st.error("🚫 深夜停止モードです。07:00以降に実行してください。")
                else:
                    poster.start_driver()
                    if poster.login(note_user, note_pass):
                        if poster.post_note_rich(g_title, g_body, image_dir=temp_img_dir):
                            st.success("🎉 投稿完了！ブラウザを確認してください。")
                        else:
                            st.error("❌ 投稿処理エラー。")
                    else:
                        st.error("❌ ログイン失敗。")

            except Exception as e:
                st.error(f"Error: {e}")

with tab_manual:
    st.subheader("🛡️ Manual Support Logic")
    st.info("テキストをコピーして手動で投稿するためのツール群です。")
    # Scan for existing drafts in the local data dir
    draft_profiles = scan_profiles()
    selected_draft = st.selectbox("Select Draft", draft_profiles) if draft_profiles else None
    
    if selected_draft:
        data = load_draft(selected_draft)
        if data:
            st.text_input("Title", value=data.get("post_title", ""))
            st.code(data.get("feed_script", ""), language="text")
            st.link_button("🚀 Open Note Publish Page", "https://note.com/publish")
    else:
        st.warning("ローカルに下書きが見つかりません。Zero機能で生成するか、dataフォルダに配置してください。")
