import streamlit as st
import json
import os
import time

# Services
from services.manual_builder import ManualBuilder
from services.pptx_exporter import PPTXExporter
from services.contract_generator import ContractGenerator
from utils.state_manager import StateManager
from utils.styles import apply_custom_css

# Page Config
st.set_page_config(page_title="AI Manual Architect v6.0 (Agency)", layout="wide", initial_sidebar_state="expanded")

def main():
    # 1. Initialization
    StateManager.init()
    apply_custom_css()
    
    # Initialize Core Services
    api_key = StateManager.get("api_key")
    builder = ManualBuilder(api_key)
    pptx_exporter = PPTXExporter()
    contract_gen = ContractGenerator()

    # 2. Sidebar: Global Settings & Project Management
    with st.sidebar:
        st.title("🧠 Agency Control")
        
        # API Key
        current_key = StateManager.get("api_key") or ""
        new_key = st.text_input("OpenAI API Key", value=current_key, type="password")
        if new_key != current_key:
            StateManager.set("api_key", new_key)
            st.success("API Key Updated")

        st.divider()
        
        # Project State Management
        st.subheader("💾 Project State")
        
        # Save
        if st.button("Download Project JSON"):
            data = StateManager.get_all()
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button("Click to Download", json_str, file_name="agency_project.json", mime="application/json")
            
        # Load
        uploaded_file = st.file_uploader("Load Project", type=["json"])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
                # Load functionality via StateManager
                for k, v in data.items():
                    StateManager.set(k, v)
                st.success("Project Loaded!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Load Error: {e}")

        st.divider()
        st.info("Workflow:\n1. 🏗️ Architect (Structure)\n2. 📝 Production (Draft)\n3. 🧐 Review (Feedback)\n4. 🚀 Publishing (Final)")

    # 3. Main Header
    st.title("📘 AI Manual Architect v6.0 (Agency Grade)")
    
    # Pricing Tier / Quality Selector (Affects Logic)
    tier = st.selectbox("💎 Service Tier", ["Normal (100k) - Standard", "Detailed (200k) - Deep Research", "Manga (300k) - Visual Story"], index=1)
    StateManager.set("tier", tier)

    # 4. Workflow Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. 🏗️ Architect", "2. 📝 Production", "3. 🧐 Review", "4. 🚀 Publishing", "⚙️ Config"])
    
    # --- TAB 5: CONFIG (PRESETS) ---
    with tab5:
        from views.preset_builder_view import render_preset_builder
        render_preset_builder()
    
    # --- TAB 1: ARCHITECT (PLANNING) ---
    with tab1:
        st.header("Step 1: Define Structure")
        col1, col2 = st.columns([1, 1])
        with col1:
            input_mode = st.radio("Input Source", ["Raw Text", "Questionnaire Wizard"])
            
            if input_mode == "Raw Text":
                input_text = st.text_area("Client Requirements / Raw Memo", height=300, value=StateManager.get("input_text", ""))
                StateManager.set("input_text", input_text)
            else:
                st.subheader("Questionnaire Form")
                with st.expander("1. Basic Info", expanded=True):
                    q_title = st.text_input("Manual Title")
                    q_purpose = st.text_input("Purpose (Why?)")
                    q_target = st.text_input("Target Audience (Who?)")
                    q_goal = st.text_input("Goal (After reading..)")
                with st.expander("2. Scope & Content"):
                    q_scope = st.text_area("Scope (Start to End)")
                    q_points = st.text_area("Key Points / Rules")
                
                if st.button("Compile Answers to Input"):
                    compiled = f"""
                    Title: {q_title}
                    Purpose: {q_purpose}
                    Target: {q_target}
                    Goal: {q_goal}
                    Scope: {q_scope}
                    Points: {q_points}
                    """
                    StateManager.set("input_text", compiled)
                    st.success("Answers Compiled! Proceed to generate skeleton.")
                    st.code(compiled)
                    input_text = compiled # Sync for generation
            
        with col2:
            st.info("💡 AI will generate a logical skeleton based on your input.")
            if st.button("Generate Skeleton Draft (4o-mini)"):
                current_input = StateManager.get("input_text")
                if not current_input:
                    st.error("Please provide input text first.")
                else:
                    with st.spinner("Architecting..."):
                        draft = builder.create_draft(current_input, tier, hearing_data=None)
                        StateManager.set("draft_json", draft)
                        st.success("Skeleton Created!")
        
        # Show Editor
        draft_json = StateManager.get("draft_json")
        if draft_json:
            st.subheader("Structure Editor")
            # Simple JSON editor for now (In future: Drag & Drop)
            edited_json = st.text_area("Edit Structure JSON", value=json.dumps(draft_json, ensure_ascii=False, indent=2), height=400)
            if st.button("Save Structure Changes"):
                try:
                    StateManager.set("draft_json", json.loads(edited_json))
                    st.success("Structure Saved!")
                except:
                    st.error("Invalid JSON")

    # --- TAB 2: PRODUCTION (DRAFTING) ---
    with tab2:
        st.header("Step 2: Generate Content")
        draft_json = StateManager.get("draft_json")
        if not draft_json:
            st.warning("Please complete Step 1 first.")
        else:
            st.write("Current Structure:", draft_json.get("title", "Untitled"))
            if st.button("📝 Generate Full Draft Text (4o-mini)"):
                with st.spinner("Writing Draft..."):
                    # Mocking expansion for now, effectively using the draft content
                    full_text = f"# {draft_json.get('title')}\n\n"
                    for sec in draft_json.get("sections", []):
                        full_text += f"## {sec.get('heading')}\n\n{sec.get('draft_content')}\n\n"
                    
                    StateManager.set("current_markdown", full_text)
                    st.success("Draft Generated!")
            
            current_md = StateManager.get("current_markdown")
            if current_md:
                st.markdown("### Draft Preview")
                st.markdown(current_md)

    # --- TAB 3: REVIEW (FEEDBACK) ---
    with tab3:
        st.header("Step 3: Expert Review")
        current_md = StateManager.get("current_markdown")
        if not current_md:
            st.warning("Please generate a draft in Step 2.")
        else:
            col_rev1, col_rev2 = st.columns([2, 1])
            with col_rev1:
                st.markdown(current_md)
            with col_rev2:
                feedback = st.text_area("Editor Feedback (What to improve?)", height=300, placeholder="Ex: More specific examples in Section 2. Tone should be softer.")
                StateManager.set("feedback", feedback)
                st.info("This feedback will be injected into the Final Polish process.")

    # --- TAB 4: PUBLISHING (FINAL) ---
    with tab4:
        st.header("Step 4: Final Output")
        current_md = StateManager.get("current_markdown")
        feedback = StateManager.get("feedback", "")
        
        if st.button("✨ Final Polish & Generate Assets (GPT-4o)"):
             with st.spinner("Polishing Text & Generating Assets..."):
                # 1. Polishing
                final_text = builder.finalize_manual(StateManager.get("draft_json"), tier, feedback=feedback)
                StateManager.set("final_text", final_text)
                
                # 2. PPTX
                pptx_path = pptx_exporter.export(final_text)
                StateManager.set("pptx_path", pptx_path)
                
                # 3. Contract (Mock Data)
                con_path = contract_gen.generate_contract("Client Co.", "Tokyo...", "Yamada Taro", "Option 1")
                StateManager.set("con_path", con_path)
                
                # 4. Receipt
                rec_path = contract_gen.generate_receipt("Client Co.", 330000, "Receipt.pdf")
                StateManager.set("rec_path", rec_path)
                
                st.success("All Assets Generated!")
        
        final_text = StateManager.get("final_text")
        if final_text:
            st.subheader("Final Manual")
            st.markdown(final_text)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                pptx_path = StateManager.get("pptx_path")
                if pptx_path and os.path.exists(pptx_path):
                    with open(pptx_path, "rb") as f:
                        st.download_button("📥 Download PPTX", f, "manual.pptx")
            with col_b:
                con_path = StateManager.get("con_path")
                if con_path and os.path.exists(con_path):
                    with open(con_path, "rb") as f:
                        st.download_button("📥 Download Contract", f, "contract.pdf")
                
                rec_path = StateManager.get("rec_path")
                if rec_path and os.path.exists(rec_path):
                    with open(rec_path, "rb") as f:
                        st.download_button("📥 Download Receipt", f, "receipt.pdf")
            with col_c:
                st.download_button("📥 Download HTML", final_text, "manual.html", mime="text/html")

if __name__ == "__main__":
    main()
