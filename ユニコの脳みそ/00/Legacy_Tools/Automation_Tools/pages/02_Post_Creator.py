
import streamlit as st
from openai import OpenAI
import json
import os
import zipfile
import io
from duckduckgo_search import DDGS
import pandas as pd

st.set_page_config(page_title="Post Creator Pro", layout="wide", page_icon="📱")

# --- CUSTOM CSS FOR MOBILE PREVIEW ---
st.markdown("""
<style>
    .iphone-frame {
        width: 375px;
        min-height: 700px;
        background-color: white;
        border: 12px solid #333;
        border-radius: 40px;
        padding: 20px;
        margin: 20px auto;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.3);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #333;
        position: relative;
    }
    .iphone-notch {
        width: 150px;
        height: 25px;
        background-color: #333;
        border-radius: 0 0 15px 15px;
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
    }
    .insta-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        margin-top: 20px;
    }
    .avatar-circle {
        width: 32px;
        height: 32px;
        background-color: #ddd;
        border-radius: 50%;
        margin-right: 10px;
    }
    .username {
        font-weight: bold;
        font-size: 14px;
    }
    .post-image {
        width: 100%;
        height: 375px;
        background-color: #f0f0f0;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #888;
        margin-bottom: 10px;
    }
    .action-bar {
        font-size: 20px;
        margin-bottom: 10px;
    }
    .caption-area {
        font-size: 14px;
        line-height: 1.4;
        white-space: pre-wrap;
    }
    .more-link {
        color: #888;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# --- BRIDGE: Load Latest Strategy (Multi-Account) ---
DATA_DIR = "c:\\Users\\user\\Desktop\\保管庫\\ユニコの脳みそ\\Automation_Tools\\data"

def scan_profiles():
    """Scan available strategy files"""
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("strategy_") and f.endswith(".json")]
    profiles = [f.replace("strategy_", "").replace(".json", "") for f in files]
    return profiles if profiles else ["default"]

# --- Sidebar (Profile Selector) ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Profile Selector
    st.subheader("👤 Profile / Brand")
    available_profiles = scan_profiles()
    selected_profile = st.selectbox("Select Profile", available_profiles)
    
    STRATEGY_FILE = os.path.join(DATA_DIR, f"strategy_{selected_profile}.json")
    
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.subheader("🛠️ Mode")
    generation_mode = st.radio("Generation Mode", ["Single Post (1投稿)", "7-Day Calendar (1週間分)"])

# Load Strategy based on selection
latest_strategy_content = ""
latest_topic = ""
timestamp = ""

if os.path.exists(STRATEGY_FILE):
    try:
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            latest_strategy_content = data.get("strategy_content", "")
            latest_topic = data.get("keyword", "")
            timestamp = data.get("timestamp", "")
    except:
        pass

# --- Helper Functions ---
def get_trends():
    """Fetch realtime trends using DDGS"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("日本 トレンド 今", region="jp-jp", timelimit="d", max_results=5))
            trends = [r['title'] for r in results]
            return ", ".join(trends)
    except:
        return ""

def render_preview(text, image_url=None):
    """Render HTML for iPhone Preview"""
    img_html = f'<img src="{image_url}" style="width:100%; height:100%; object-fit:cover;">' if image_url else '<div style="width:100%;height:100%;background:#eee;display:flex;align-items:center;justify-content:center;">Image</div>'
    
    html = f"""
    <div class="iphone-frame">
        <div class="iphone-notch"></div>
        <div class="insta-header">
            <div class="avatar-circle"></div>
            <div class="username">your_account</div>
        </div>
        <div class="post-image">{img_html}</div>
        <div class="action-bar">❤️ 💬 🚀 🔖</div>
        <div class="caption-area">
            <span style="font-weight:bold;">username</span> {text[:100].replace(chr(10), '<br>')}...
            <div class="more-link">続きを読む</div>
            <br>
            {text.replace(chr(10), '<br>')}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def generate_images_grid(prompts, key_prefix, style, avatar, api_key):
    """Generate 4 images grid"""
    if not prompts:
        st.warning("No prompts available.")
        return

    st.markdown(f"**🎨 Generate 4 Images ({key_prefix})**")
    
    # Editable Prompts
    edited_prompts = []
    for i, p in enumerate(prompts):
        val = st.text_input(f"Prompt {i+1}", value=p, key=f"{key_prefix}_p_{i}")
        edited_prompts.append(val)
    
    if st.button(f"Generate {key_prefix} Images", key=f"btn_{key_prefix}"):
        if not api_key:
            st.error("API Key Required")
            return
            
        client = OpenAI(api_key=api_key)
        cols = st.columns(2)
        
        for i, p in enumerate(edited_prompts):
            if i >= 4: break
            with cols[i % 2]:
                with st.spinner(f"Gen {i+1}..."):
                    try:
                        full_prompt = f"{avatar}, {p}, {style}, high quality"
                        res = client.images.generate(
                            model="dall-e-3",
                            prompt=full_prompt,
                            size="1024x1024",
                            quality="standard",
                            n=1
                        )
                        url = res.data[0].url
                        st.image(url, caption=f"Img {i+1}")
                        # Store in session state if needed for persistence
                        st.session_state[f"img_{key_prefix}_{i}"] = url
                    except Exception as e:
                        st.error(f"Error: {e}")

def refinement_chat(target_key, current_text, api_key):
    """Chat interface to refine text"""
    st.markdown("---")
    st.caption("💬 AI Editor (Refinement)")
    
    history_key = f"history_{target_key}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []
        
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if prompt := st.chat_input(f"Discusssion on {target_key}...", key=f"chat_{target_key}"):
        st.session_state[history_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Refining..."):
                try:
                    client = OpenAI(api_key=api_key)
                    messages = [
                        {"role": "system", "content": f"You are an editor. Rewrite the text based on instructions.\nCurrent Text:\n{current_text}"},
                        *st.session_state[history_key]
                    ]
                    res = client.chat.completions.create(model="gpt-4o", messages=messages)
                    reply = res.choices[0].message.content
                    st.write(reply)
                    st.session_state[history_key].append({"role": "assistant", "content": reply})
                    st.info("☝️ Copy the result above and paste it into the editor.")
                except Exception as e:
                    st.error(e)

def to_csv_ready_data(content_json):
    """Convert content to generic CSV format for Canva"""
    data = []
    # Single Post Mode
    if "feed_script" in content_json:
        row = {
            "Feed_Script": content_json.get("feed_script"),
            "Reel_Script": content_json.get("reel_script"),
            "Story_Text": content_json.get("story_text"),
            "Prompt_1": content_json.get("feed_image_prompts", [""])[0] if content_json.get("feed_image_prompts") else ""
        }
        data.append(row)
    # Bulk Mode
    elif isinstance(content_json, list):
         for day in content_json:
             row = {
                "Day": day.get("day"),
                "Topic": day.get("topic"),
                "Feed_Script": day.get("feed_script"),
                "Reel_Script": day.get("reel_script"),
                "Story_Text": day.get("story_text")
             }
             data.append(row)
             
    return pd.DataFrame(data)

st.title("📱 Post Creator Pro | 究極の投稿作成")
if timestamp:
    st.caption(f"Strategy Loaded: {timestamp}")

# --- Sidebar ---
# --- Sidebar (legacy removed) ---
    
# --- Persona & Identity (Moved from old sidebar) ---
with st.sidebar:
    st.markdown("---")
    use_trends = st.checkbox("🔥 Inject Trends (トレンド注入)", value=False)
    
    st.subheader("🎭 Persona")
    persona_type = st.selectbox("Type", ["毒舌コンサル", "寄り添いヒーラー", "論理的ハイスペ", "熱血スポ根"])
    writing_tone = st.select_slider("Tone", options=["超辛口", "辛口", "普通", "丁寧", "超丁寧"], value="普通")
    
    st.subheader("🧑‍🎨 Visual Identity")
    avatar_prompt = st.text_area("Fixed Avatar Prompt", 
                                 value="A Japanese energetic woman, bob hair, pink hoodies, flat anime style, white background",
                                 height=100)
    image_style = st.selectbox("Style", ["Natural photo", "Anime style", "Minimal illustration", "Cyberpunk", "Luxury Gold"])


# --- Main Layout ---
left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("📝 Content Input")
    strategy_input = st.text_area("分析データ (Strategy)", value=latest_strategy_content, height=150)
    topic = st.text_input("テーマ (Topic)", value=latest_topic)
    
    if st.button("🚀 Generate Content", type="primary"):
        if not api_key:
            st.error("API Key Required")
        elif not strategy_input or not topic:
            st.warning("Input required")
        else:
            client = OpenAI(api_key=api_key)
            st.session_state['generated_content'] = None
            
            # Trend Injection
            trend_context = ""
            if use_trends:
                with st.spinner("Fetching Trends..."):
                    trends = get_trends()
                    if trends:
                        trend_context = f"\n【トレンド情報】\n現在日本で以下のワードが流行しています: {trends}\nこれらを比喩やハッシュタグに自然に混ぜて、バズりやすくしてください。"
                        
            st.success(f"Trends Injected: {trends}" if trend_context else "Trends data missing, proceeding without.")
            
            system_prompt_base = f"""
            あなたはプロのSNSクリエイターです。
            ペルソナ「{persona_type}（{writing_tone}）」で執筆してください。
            すべて日本語で出力してください。画像プロンプトのみ英語です。
            {trend_context}
            """
            
            # --- SINGLE MODE ---
            if generation_mode == "Single Post (1投稿)":
                system_prompt = system_prompt_base + """
                【出力形式】 JSON
                Keys: "post_title", "feed_script", "reel_script", "story_text", 
                "feed_image_prompts" (list 4), "reel_image_prompts" (list 4), "story_image_prompts" (list 4)
                
                【重要: Phantom Note Zero 対応】
                "feed_script" (または長文記事) の中で、画像を挿入すべき場所に以下のタグを必ず含めてください。
                例: [IMAGE: A futuristic city in neon style]
                ※画像生成AI（DALL-E 3）へのプロンプトをそのままタグの中に入れてください（英語）。
                記事全体のバランスを見て、2〜3箇所程度挿入してください。
                """
                
                with st.spinner("Writing Single Post..."):
                    try:
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"分析データ: {strategy_input}\nテーマ: {topic}"}
                            ],
                            response_format={"type": "json_object"}
                        )
                        st.session_state['generated_content'] = json.loads(res.choices[0].message.content)
                        st.session_state['mode'] = "single"
                        
                        # SAVE FOR 03_AUTO_POSTER
                        CONTENT_FILE = os.path.join(DATA_DIR, f"content_{selected_profile}.json")
                        with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(st.session_state['generated_content'], f, ensure_ascii=False, indent=4)
                        st.toast(f"Saved to Draft Station ({selected_profile})!")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            # --- BULK MODE ---
            else:
                system_prompt = system_prompt_base + """
                【出力形式】 JSON List
                テーマ「{topic}」に基づき、1週間分（Day1〜Day7）の投稿計画を作成してください。
                Output: { "days": [ 
                    { "day": 1, "topic": "...", "post_title": "...", "feed_script": "...", "reel_script": "...", "story_text": "...", "image_prompt": "1 prompt" },
                    ...
                ]}
                
                【重要: Phantom Note Zero 対応】
                各日の "feed_script" の中に、画像を挿入すべき場所に [IMAGE: prompt] タグを1つ含めてください。
                """
                with st.spinner("Writing 7-Day Calendar (This may take 30s)..."):
                    try:
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"分析データ: {strategy_input}\nテーマ: {topic}"}
                            ],
                            response_format={"type": "json_object"}
                        )
                        st.session_state['generated_content'] = json.loads(res.choices[0].message.content)
                        st.session_state['mode'] = "bulk"
                        
                        # SAVE FOR 03_AUTO_POSTER
                        CONTENT_FILE = os.path.join(DATA_DIR, f"content_{selected_profile}.json")
                        with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(st.session_state['generated_content'], f, ensure_ascii=False, indent=4)
                        st.toast(f"Saved to Draft Station ({selected_profile})!")
                    except Exception as e:
                        st.error(f"Error: {e}")


# --- Editor & Preview Logic ---
if 'generated_content' in st.session_state and st.session_state['generated_content']:
    content = st.session_state['generated_content']
    mode = st.session_state.get('mode', 'single')
    
    # --- SINGLE MODE UI ---
    if mode == "single":
        with left_col:
            tab1, tab2, tab3, tab4 = st.tabs(["Add Feed", "Add Reel", "Add Story", "Export"])
            
            # Feed Tab
            with tab1:
                feed_text = st.text_area("Feed Script", content.get("feed_script", ""), height=300, key="f_txt")
                refinement_chat("feed", feed_text, api_key)
                st.session_state['preview_text'] = feed_text 
                
                generate_images_grid(content.get("feed_image_prompts", []), "Feed", image_style, avatar_prompt, api_key)
            
            # Reel Tab
            with tab2:
                reel_text = st.text_area("Reel Script", content.get("reel_script", ""), height=300, key="r_txt")
                refinement_chat("reel", reel_text, api_key)
                st.session_state['preview_text'] = reel_text 
                
                generate_images_grid(content.get("reel_image_prompts", []), "Reel", image_style, avatar_prompt, api_key)
                
            # Story Tab
            with tab3:
                story_text = st.text_area("Story Text", content.get("story_text", ""), height=300, key="s_txt")
                refinement_chat("story", story_text, api_key)
                st.session_state['preview_text'] = story_text
                
                generate_images_grid(content.get("story_image_prompts", []), "Story", image_style, avatar_prompt, api_key)
                
            # Export Tab
            with tab4:
                st.subheader("Downloads")
                # CSV Export
                df = to_csv_ready_data(content)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Download CSV (Canva)", csv, "post_content.csv", "text/csv")
                
        # --- PREVIEW COLUMN ---
        with right_col:
            st.markdown("### 📱 Live Preview")
            preview_txt = st.session_state.get('preview_text', content.get("feed_script", ""))
            
            # Try to get image from session state if generated
            # Currently just placeholder
            render_preview(preview_txt)

    # --- BULK MODE UI ---
    # --- BULK MODE UI (Visual Calendar) ---
    elif mode == "bulk":
        days = content.get("days", [])
        with left_col:
            st.success(f"✅ Generated {len(days)} Days Plan")
            
            # Export CSV for Bulk
            df = to_csv_ready_data(days)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download 7-Day CSV (Canva)", csv, "weekly_plan.csv", "text/csv")
            
            st.markdown("### 📅 Weekly Grid View")
            
            # Create a 3-column grid for the first 6 days, then 1 for the 7th? 
            # Or just use st.columns(3) and wrap
            
            cols = st.columns(3)
            for i, d in enumerate(days):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"#### Day {d['day']}")
                        st.caption(d['topic'])
                        st.text_area("Feed", d['feed_script'], height=100, key=f"d_{i}_f")
                        st.text_area("Story", d['story_text'], height=60, key=f"d_{i}_s")
                        
                        if st.button(f"🔍 Preview Day {d['day']}", key=f"btn_p_{i}"):
                            st.session_state['preview_text'] = d['feed_script']
                            st.rerun() # Rerun to update right col preview
                    
        with right_col:
             st.markdown("### 📱 Day Preview")
             preview_txt = st.session_state.get('preview_text', "Select a day to preview...")
             render_preview(preview_txt)

