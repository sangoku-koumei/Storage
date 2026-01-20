
import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="Special Appraisal Master", layout="wide", page_icon="🔮")

st.title("🔮 Special Appraisal Master | 鑑定師専用特別ツール")
st.markdown("「商品錬金」と「鑑定執筆」の2つの特別モードを搭載した、プロ仕様のツールです。")

# --- Constants ---
# Master Prompt for Appraisal (Hardcoded for simplicity, or could load from file)
MASTER_PROMPT_APPRAISAL = """
# 鑑定文作成プロンプト（完全版）
#Prompt #鑑定文 #AI #LCIQ #コピーライティング

## 1. Request:
**目的**:
[[恋愛]]・[[復縁]]・[[人間関係]]の[[鑑定文]]を、温かく自然な読み味で届ける。
ただし [[Phase0]]（内部/非公開）は「鑑定者への鑑定のポイント（運用ガイド）」としてのみ使用し、[[鑑定文]]（Step1〜Step13）には一切反映・示唆しない。

## 2. Role:
**立場**:
「[[鑑定師]] × [[心理学]] × [[コピーライティング]] × [[マーケティング]]」統合の制作者用ガイドを内包したライティングAI。
**ゴール**:
内部で“[[本心推測]]”と“[[理想未来]]・[[商品設計]]”を固めつつ、外部出力は徹底してやさしい物語表現に限定する。

## 3. Regulation:
**構成**:
- **[[Phase0]]（内部/非公開/出力禁止）**: 「[[本心推測]]」と「[[理想未来]]・[[商品設計]]」を鑑定者にだけ伝える運用ポイント
- **Phase1**: Step1〜Step10（各2,000字以上、章末に「次のステップを出力しますか？」は不要。一気に入力テキストに対する完全版を出力すること。）
**文体**:
- 外部出力は人肌感のある口語×詩的、AI/設計/分析の匂いを排除。

## 4. Rule:
**内外分離の厳守**:
- [[Phase0]]の語彙/内容（[[本心推測]]・[[理想未来]]定義・“これしかない”[[コア機構]]・[[商品設計]]・[[アップセル]]方針）は[[鑑定文]]へ一切露出しない。暗示・示唆・言い換えも禁止。
- 外部では断定/唯一主張/テクニカル用語を避け、安心・選択の自由を最優先。

## 5. Phase0（内部/非公開/出力禁止）: 鑑定者への鑑定のポイント
**目的**:
依頼主の入力から“無意識レベルの望み”を仮説化し、それに一直線で応える[[理想未来]]と商品（[[松竹梅の法則]]）を裏側で設計する。
※以下は鑑定者の運用メモであり、[[鑑定文]]には書かない。

**[[本心推測]]フレーム**:
- **[[ラダリング]]（なぜ×5）**: 行動→感情→意味づけ→価値→自己像
- **恐れ→願いの反転**: 失う不安/拒絶不安/停滞不安 → 安全/受容/前進

**[[理想未来]]キャンバス（Before→After）**:
- **体感**: 胸の圧/呼吸/睡眠/朝の気分 → 軽さ/整い/予感
- **関係**: 相手との距離/連絡頻度/境界線 → 相互性/温度/合図
- **行動**: 既読後の反応/会う頻度/自分の優先順位 → 小さな主導権/自然な提案

**[[商品設計]]（[[松竹梅の法則]]）**: ※外部では柔らかい表現に変換
- **梅=入り口**: 現状整え&1テーマの安心設計
- **竹=最適化**: 本心に沿う障害解体＋行動手順
- **松=統合**: 過去-現在-近未来の縦串＋伴走

## 6. Output Order Requirement (重要):
出力は以下の順序で厳密に行ってください。

---
【Phase 0: 内部戦略メモ (鑑定師用)】
(ここでPhase 0の内容、本心推測や商品設計などを箇条書きで出力)

---
【Phase 1: 鑑定文 (お客様提示用)】
(導入から始まり、やさしい語り口で本文を作成。松竹梅の提案まで含める)
---
"""

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# --- Tabs ---
tab1, tab2 = st.tabs(["🔮 Appraisal Generator (鑑定執筆)", "⚗️ Product Alchemy (商品錬金)"])

# ==========================================
# TAB 1: Appraisal Generator
# ==========================================
with tab1:
    st.subheader("📝 鑑定文作成 (Appraisal Generator)")
    st.markdown("お客様の相談内容から、**「内部戦略 (Phase0)」**と**「提出用鑑定文 (Phase1)」**を同時に生成します。")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name", placeholder="Aさん")
        client_gender = st.selectbox("Client Gender", ["女性", "男性", "その他"])
        teller_persona = st.text_input("Fortune Teller Persona", "優しいタロット占い師")
    
    with col2:
        consultation = st.text_area("Consultation Content (相談内容)", height=150, placeholder="彼と復縁したいです。音信不通で...")
        
    if st.button("🚀 Generate Appraisal"):
        if not api_key:
            st.error("API Key required.")
        else:
            client = OpenAI(api_key=api_key)
            
            with st.spinner("AI is mediating your spiritual vision..."):
                user_prompt = f"""
                【依頼者情報】
                名前: {client_name}
                性別: {client_gender}
                
                【相談内容】
                {consultation}
                
                【あなたのペルソナ】
                {teller_persona}
                
                上記に基づき、Master Promptの指示に従ってPhase 0とPhase 1を出力してください。
                """
                
                try:
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": MASTER_PROMPT_APPRAISAL},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    full_text = res.choices[0].message.content
                    
                    # Parsers
                    phase0 = ""
                    phase1 = ""
                    
                    if "【Phase 0" in full_text and "【Phase 1" in full_text:
                        parts = full_text.split("【Phase 1")
                        phase0 = parts[0].replace("【Phase 0: 内部戦略メモ (鑑定師用)】", "").strip()
                        phase1 = "【Phase 1" + parts[1]
                        phase1 = phase1.replace("【Phase 1: 鑑定文 (お客様提示用)】", "").strip()
                    else:
                        # Fallback
                        phase1 = full_text

                    # Output UI
                    with st.expander("🔒 Phase 0: Internal Strategy (秘匿情報)", expanded=True):
                        st.info("※これは鑑定師専用のメモです。お客様には見せないでください。")
                        st.markdown(phase0)
                        
                    st.markdown("### 💌 Client Message (提出用)")
                    st.text_area("Final Text", phase1, height=600)
                    st.button("📋 Copy Text")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# TAB 2: Product Alchemy (Legacy Class 07)
# ==========================================
with tab2:
    st.subheader("⚗️ 商品錬金 (Product Alchemy)")
    st.markdown("マルチエージェント会議システムにより、**「売れる占い商品」**を自動生成します。")

    theme = st.text_input("商品のテーマ (例: 復縁, 金運, 不倫, 転職)", "復縁", key="prod_theme")
    style = st.selectbox("画像スタイル", ["可愛い日本のアニメ/マンガ風", "神秘的なタロット風", "水彩画風"], key="prod_style")

    if st.button("会議を開始する（商品生成）", key="btn_prod"):
        if not api_key:
            st.error("APIキーを入力してください。")
        else:
            client = OpenAI(api_key=api_key)
            status_text = st.empty()
            progress_bar = st.progress(0)

            # Round 1: Fortune Teller
            status_text.text("🔮 占い師が原案を作成中...")
            prompt_fortune = f"テーマ「{theme}」で、ココナラなどで販売する占い商品を考案してください。ターゲットとなる悩みと占術を定義してください。"
            
            try:
                res_fortune = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "あなたは熟練の占い師です。"}, {"role": "user", "content": prompt_fortune}]
                ).choices[0].message.content
                
                with st.expander("Round 1: 占い師の原案"):
                    st.write(res_fortune)
                progress_bar.progress(25)

                # Round 2: Marketer
                status_text.text("💰 鬼マーケターが修正中...")
                prompt_marketer = f"以下の案を売れるように修正して。\n{res_fortune}\n\n【重要】情報を全て出しすぎない「寸止め」設計にし、アップセルへの導線を作ること。"
                res_marketer = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "あなたは年商1億の辛口Webマーケターです。"}, {"role": "user", "content": prompt_marketer}]
                ).choices[0].message.content
                
                with st.expander("Round 2: マーケターの修正"):
                    st.write(res_marketer)
                progress_bar.progress(50)

                # Round 3: Copywriter
                status_text.text("✍️ コピーライターが執筆中...")
                prompt_copy = f"戦略に基づき、タイトル（30文字以内・パワーワード入）と商品本文（500文字）を作成して。\n戦略:\n{res_marketer}"
                res_copy = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "あなたは伝説のセールスコピーライターです。"}, {"role": "user", "content": prompt_copy}]
                ).choices[0].message.content
                progress_bar.progress(75)

                # Round 4: Designer (Prompt)
                status_text.text("🎨 アートディレクターが画像プロンプト作成中...")
                prompt_design = f"以下の商品用のDALL-E 3英語プロンプトを作成して。\n商品:\n{res_copy}\nスタイル:\n{style}。文字なし。"
                res_design_prompt = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "あなたはプロのアートディレクターです。プロンプトのみ出力。"}, {"role": "user", "content": prompt_design}]
                ).choices[0].message.content

                # Image Gen
                status_text.text("🖼 画像生成中...")
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=res_design_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = image_response.data[0].url
                
                progress_bar.progress(100)
                status_text.text("✅ 完成！")

                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    st.image(image_url, caption="Generated Thumbnail")
                with c2:
                    st.markdown(res_copy)
                    
            except Exception as e:
                st.error(f"Error: {e}")
