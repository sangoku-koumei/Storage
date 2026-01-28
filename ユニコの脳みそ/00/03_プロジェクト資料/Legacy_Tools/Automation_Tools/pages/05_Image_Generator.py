
import streamlit as st
from openai import OpenAI
import os
import json

st.set_page_config(page_title="Image Lab", layout="wide", page_icon="🎨")

# --- Constants & State ---
DATA_DIR = "c:\\Users\\user\\Desktop\\保管庫\\ユニコの脳みそ\\Automation_Tools\\data"
AVATAR_FILE = os.path.join(DATA_DIR, "avatar_presets.json")
os.makedirs(DATA_DIR, exist_ok=True)

if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- Helper Functions ---
def load_avatars():
    if os.path.exists(AVATAR_FILE):
        with open(AVATAR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"Default": "A Japanese energetic woman, flat anime style"}

def save_avatar(name, prompt):
    avatars = load_avatars()
    avatars[name] = prompt
    with open(AVATAR_FILE, 'w', encoding='utf-8') as f:
        json.dump(avatars, f, ensure_ascii=False, indent=4)
    st.toast(f"Avatar '{name}' Saved!")

# --- UI Layout ---
st.title("🎨 Image Lab | 実験的画像生成")
st.markdown("プロンプト実験や、ブログ用アイキャッチの単発生成に使用します。")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.subheader("🧑‍🎨 Avatar Manager")
    avatars = load_avatars()
    selected_avatar_name = st.selectbox("Load Avatar", list(avatars.keys()))
    current_avatar_prompt = avatars[selected_avatar_name]
    
    # Edit & Save Avatar
    new_avatar_prompt = st.text_area("Current Avatar Prompt", value=current_avatar_prompt, height=100)
    new_avatar_name = st.text_input("New Avatar Name (to save)")
    if st.button("💾 Save Avatar Preset"):
        if new_avatar_name:
            save_avatar(new_avatar_name, new_avatar_prompt)
            st.rerun()

    st.subheader("🎨 Style Mixer")
    style_base = st.selectbox("Base Style", ["None", "Anime", "Photorealistic", "Oil Painting", "3D Render", "Pixel Art"])
    style_mood = st.selectbox("Mood", ["None", "Bright", "Dark/Cyberpunk", "Pastel", "Luxury Gold", "Horror"])


# --- Main Area ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Prompt Engineering")
    user_prompt = st.text_area("Input Prompt (Situation/Object)", height=150, placeholder="Cat holding a sign that says 'Hello'")
    
    full_prompt_preview = f"{new_avatar_prompt}, {user_prompt}"
    if style_base != "None": full_prompt_preview += f", {style_base} style"
    if style_mood != "None": full_prompt_preview += f", {style_mood} tone"
    
    st.info(f"ℹ️ **Final Prompt Preview**:\n{full_prompt_preview}")
    
    if st.button("🚀 Generate", type="primary"):
        if not api_key:
            st.error("API Key Required")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("Drawing..."):
                try:
                    res = client.images.generate(
                        model="dall-e-3",
                        prompt=full_prompt_preview,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    url = res.data[0].url
                    
                    # Add to history
                    st.session_state['history'].insert(0, {"url": url, "prompt": full_prompt_preview})
                    
                except Exception as e:
                    st.error(f"Error: {e}")

with col2:
    st.subheader("🖼️ Result & History")
    if st.session_state['history']:
        # Show latest large
        latest = st.session_state['history'][0]
        st.image(latest['url'], caption="Latest Result", use_container_width=True)
        st.text_area("Prompt used", latest['prompt'], height=80)
        
        st.markdown("---")
        st.write("🕒 Session History")
        
        # Grid for history
        grid_cols = st.columns(3)
        for i, item in enumerate(st.session_state['history'][1:]): # Skip first
            with grid_cols[i % 3]:
                st.image(item['url'], use_container_width=True)
                st.caption(f"#{i+1}")
