import streamlit as st
import json
import os
from utils.state_manager import StateManager

# Path to custom presets
USER_PRESETS_FILE = "user_presets.json"

def render_preset_builder():
    st.subheader("🛠️ Custom Preset Builder")
    st.info("自社固有のマニュアル種別（レシピ、独自SOP、採用面接など）を定義して保存できます。")

    # 1. Load Existing Custom Presets
    if os.path.exists(USER_PRESETS_FILE):
        with open(USER_PRESETS_FILE, 'r', encoding='utf-8') as f:
            custom_presets = json.load(f)
    else:
        custom_presets = {}

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📝 New Preset Definition")
        p_name = st.text_input("Preset Name (Display)", placeholder="e.g. 採用面接マニュアル")
        p_key = st.text_input("Preset Key (Internal)", placeholder="e.g. RECRUIT_INTERVIEW").upper()
        p_focus = st.text_input("Focus (Critical Point)", placeholder="e.g. 見極め基準とアトラクト")
        
        st.markdown("#### 必須セクション (Required Sections)")
        p_sections_str = st.text_area("カンマ区切りで入力", placeholder="目的, 面接の流れ, 評価基準, 質問リスト, NGワード")
        
        st.markdown("#### 🤖 AI Instruction (System Prompt)")
        p_instruction = st.text_area(
            "AIへの具体的な指示", 
            height=200, 
            placeholder="あなたは熟練の人事担当者です。面接官が迷わないように具体的な質問例と、回答の良し悪しを判断する基準を明確に書いてください..."
        )

        if st.button("💾 Save Custom Preset"):
            if p_name and p_key and p_instruction:
                # Format
                new_preset = {
                    "name": p_name,
                    "focus": p_focus,
                    "required_sections": [s.strip() for s in p_sections_str.split(",") if s.strip()],
                    "instruction": p_instruction
                }
                custom_presets[p_key] = new_preset
                
                # Save to file
                with open(USER_PRESETS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(custom_presets, f, ensure_ascii=False, indent=2)
                
                st.success(f"Preset '{p_name}' Saved!")
                st.rerun()
            else:
                st.error("Please fill in Name, Key, and Instruction.")

    with col2:
        st.markdown("### 📂 Saved Custom Presets")
        if custom_presets:
            for key, val in custom_presets.items():
                with st.expander(f"📌 {val['name']} ({key})"):
                    st.write(f"**Focus**: {val['focus']}")
                    st.write(f"**Sections**: {', '.join(val['required_sections'])}")
                    st.code(val['instruction'])
                    if st.button("🗑️ Delete", key=f"del_{key}"):
                        del custom_presets[key]
                        with open(USER_PRESETS_FILE, 'w', encoding='utf-8') as f:
                            json.dump(custom_presets, f, ensure_ascii=False, indent=2)
                        st.rerun()
        else:
            st.caption("No custom presets defined yet.")
