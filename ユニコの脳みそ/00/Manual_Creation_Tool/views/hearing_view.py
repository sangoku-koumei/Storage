import streamlit as st
from utils.state_manager import StateManager
from services.content_architect import ContentArchitect

def render_hearing_view(mode_key):
    st.subheader("Step 2: 不明点の確認 (Hearing)")
    st.info("より正確なアウトプットにするため、以下の質問に答えてください")
    
    qs = StateManager.get("hearing_qs")
    # Fallback if qs is error
    if not qs or "q1" not in qs:
        st.error("質問の生成に失敗しました。Step 1に戻ってください。")
        if st.button("戻る"):
            StateManager.set("stage", "input")
            st.rerun()
        return

    with st.form("hearing_form"):
        a1 = st.text_input(f"Q1: {qs.get('q1', '')}")
        a2 = st.text_input(f"Q2: {qs.get('q2', '')}")
        a3 = st.text_input(f"Q3: {qs.get('q3', '')}")
        
        if st.form_submit_button("🚀 回答して構成案を作成"):
            with st.spinner("構成案を作成中... (Agency Architect Starting)"):
                answers = {"a1": a1, "a2": a2, "a3": a3}
                input_text = StateManager.get("input_text")
                
                # Manual merging for Architect
                enhanced_input = f"""
                【元のメモ】
                {input_text}
                
                【追加ヒアリング情報】
                Q1の回答: {answers.get('a1', '')}
                Q2の回答: {answers.get('a2', '')}
                Q3の回答: {answers.get('a3', '')}
                """
                
                try:
                    architect = ContentArchitect()
                    current_type = StateManager.get("manual_type") or "SOP"
                    current_vol = StateManager.get("manual_volume") or "Standard"
                    
                    options = architect.generate_outline(
                        enhanced_input, 
                        mode_key, 
                        manual_type=current_type,
                        volume=current_vol
                    )
                    
                    StateManager.set("options_text", options)
                    StateManager.set("stage", "selection")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation Error: {e}")
