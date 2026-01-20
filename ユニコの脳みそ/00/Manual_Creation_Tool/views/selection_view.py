import streamlit as st
from utils.state_manager import StateManager

def render_selection_view():
    st.subheader("Step 3: 構成案の選択")
    col1, col2 = st.columns([1, 1])
    
    options_text = StateManager.get("options_text")
    
    with col1:
        st.markdown("### 🤖 提案された構成案")
        st.text_area("Options", options_text, height=400, disabled=True)
        
    with col2:
        st.markdown("### 👉 採用する案をコピーして調整")
        # Use a temporary key for editing to allow modification
        user_selection = st.text_area("採用・調整後の構成案", value=options_text, height=300)
        
        if st.button("✨ この構成で決定して生成"):
            StateManager.set("selected_option", user_selection)
            StateManager.set("stage", "final")
            # Reset final result to force regeneration
            StateManager.set("final_result", "") 
            st.rerun()
        
        if st.button("🔙 入力に戻る"):
            StateManager.set("stage", "input")
            st.rerun()
