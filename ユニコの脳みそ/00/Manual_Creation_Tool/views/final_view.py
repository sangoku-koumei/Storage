import streamlit as st
import streamlit.components.v1 as components
import json
from utils.state_manager import StateManager
from services.manual_generator import (
    parse_manga_content, parse_visual_content, 
    parse_lp_content, render_html_from_data, generate_dalle_image, 
    generate_thumbnail_html, render_thumbnail_from_data, generate_slide_content_json, create_presentation
)

from services.content_architect import ContentArchitect

def render_final_view(mode_key, cast_key):
    st.subheader("Step 4: 最終成果物 & Mobile Check")
    
    final_result = StateManager.get("final_result")
    last_result = StateManager.get("last_result")
    current_data = StateManager.get("current_data")
    
    # 1. Generate Text (if missing)
    # 1. State Machine for Generation
    # States: None -> Drafting -> Review (Pause) -> Polishing -> Complete
    
    gen_state = StateManager.get("gen_state") or "None"
    
    if not final_result and gen_state == "None":
        # Initial Kickoff
        StateManager.set("gen_state", "Drafting")
        st.rerun()

    if gen_state == "Drafting":
        with st.status("🏗️ Agency Architect Building...", expanded=True) as status:
            architect = ContentArchitect()
            outline = StateManager.get("selected_option")
            input_text = StateManager.get("input_text")
            
            # Step 1: Drafting
            status.write("📝 Drafting Content (Framework Injection)...")
            draft = architect.generate_draft(outline, input_text)
            StateManager.set("draft_text", draft)
            
            # Step 2: AI Critique
            status.write("🧐 Editor Chief Reviewing (Critique)...")
            critique = architect.critique_draft(draft)
            StateManager.set("ai_critique", critique)
            
            # Transition to Review
            StateManager.set("gen_state", "Review")
            status.update(label="✋ Waiting for Human Review", state="running", expanded=False)
            st.rerun()
            
    if gen_state == "Review":
        st.info("✋ **Human-in-the-Loop Review**: AI has drafted and critiqued the content. You can add your own instructions before final polishing.")
        
        col_d, col_c = st.columns([2, 1])
        with col_d:
            with st.expander("📝 Draft Preview", expanded=False):
                st.markdown(StateManager.get("draft_text"))
        with col_c:
            st.write("🤖 **AI Critique**")
            st.info(StateManager.get("ai_critique"))
            
        human_comment = st.text_area("👨‍🏫 **Your Additional Instructions** (Optional)", placeholder="Ex: Make the tone more friendly. Add a section about X.")
        
        if st.button("✨ Proceed to Final Polish"):
            StateManager.set("human_critique", human_comment)
            StateManager.set("gen_state", "Polishing")
            st.rerun()

    if gen_state == "Polishing":
        with st.status("✨ Final Polishing...", expanded=True) as status:
            architect = ContentArchitect()
            draft = StateManager.get("draft_text")
            critique = StateManager.get("ai_critique")
            human_critique = StateManager.get("human_critique")
            
            # Retrieve flags
            current_type = StateManager.get("manual_type") or "SOP"
            current_vol = StateManager.get("manual_volume") or "Standard"
            
            # Step 3: Polish with Human Input
            final_result = architect.polish_content(
                draft, 
                critique, 
                mode_key, 
                manual_type=current_type, 
                volume=current_vol,
                human_critique=human_critique
            )
            
            StateManager.set("final_result", final_result)
            StateManager.set("gen_state", "Complete")
            status.update(label="✅ Complete!", state="complete", expanded=False)
            st.rerun()

    # 2. Parse Data & Render
    if final_result != last_result or current_data is None:
        last_result = final_result
    
    if final_result:
        # Import Refiner
        from services.section_refiner import SectionRefiner
        refiner = SectionRefiner()
        
        # Tabs for Viewing & Refining
        tab_view, tab_refine = st.tabs(["📄 Full View", "🛠️ Section Refinement"])
        
        with tab_view:
            st.markdown(final_result)
            st.divider()
            st.download_button("Download Markdown", final_result, "manual.md")

        with tab_refine:
            st.subheader("🛠️ Section-Level Polish")
            st.info("特定のセクションだけを選んで、AIにリライト指示を出せます。")
            
            # Parse Sections
            sections = refiner.parse_markdown_to_sections(final_result)
            headings = [s["heading"] for s in sections]
            
            selected_heading = st.selectbox("Select Section to Refine", headings)
            
            # Find Content
            target_section = next((s for s in sections if s["heading"] == selected_heading), None)
            
            if target_section:
                with st.expander("Current Content", expanded=False):
                    st.code(target_section["content"], language="markdown")
                
                refine_instruction = st.text_area("Refinement Instruction", placeholder="Ex: Make this procedure more detailed. Add a warning about X.")
                
                if st.button("🔄 Rewrite This Section"):
                    with st.spinner("Rewriting Section..."):
                        new_content = refiner.refine_section_content(target_section["content"], refine_instruction)
                        
                        # Update Section List
                        target_section["content"] = new_content
                        
                        # Reconstruct Full Text
                        new_full_text = refiner.reconstruct_markdown(sections)
                        
                        # Update State
                        StateManager.set("final_result", new_full_text)
                        StateManager.set("gen_state", "Complete") # Ensure state remains complete
                        st.success("Section Updated!")
                        st.rerun()
        
        # This block was originally part of the "2. Parse Data & Render" section.
        # It needs to be moved inside the `if final_result:` block to ensure `final_result` is available.
        # The `if final_result != last_result or current_data is None:` check is now handled by `last_result = final_result` above.
        if mode_key == "Manga":
            new_data = parse_manga_content(final_result, cast_key)
        elif mode_key == "Visual":
            new_data = parse_visual_content(final_result)
        elif mode_key == "LP":
            new_data = parse_lp_content(final_result)
        else:
            import markdown
            try:
                html_body = markdown.markdown(final_result, extensions=['extra'])
            except:
                html_body = final_result.replace("\n", "<br>")
            new_data = {"title": "業務マニュアル", "content": html_body}
        
        StateManager.set("current_data", new_data)
        StateManager.set("last_result", final_result)
        current_data = new_data

    # 3. Render HTML
    html_out = render_html_from_data(current_data, mode_key)
    StateManager.set("html_content", html_out)

    # --- Manga Image Editor ---
    if mode_key == "Manga":
        with st.expander("🖼️ マンガ画像編集 (Image Editor)", expanded=True):
            data = current_data
            updated = False
            if data and "sections" in data:
                for i, section in enumerate(data["sections"]):
                    col_txt, col_img = st.columns([2, 1])
                    with col_txt:
                        st.text(f"Panel {i+1} Prompt: {section.get('img_prompt')}")
                    with col_img:
                        if st.button(f"🎨 Generate Image {i+1}", key=f"gen_btn_{i}"):
                            with st.spinner("Generating..."):
                                url = generate_dalle_image(section.get('img_prompt'))
                                if url:
                                    section["img_url"] = url
                                    updated = True
                        
                        # Manual Override
                        val = st.text_input(f"Image URL {i+1}", value=section.get("img_url", ""), key=f"url_input_{i}")
                        if val and val != section.get("img_url", ""):
                            section["img_url"] = val
                            updated = True
            
            if updated:
                StateManager.set("current_data", data)
                st.rerun()

    # --- Output Display ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📱 Mobile Preview (375px)")
        html_content = StateManager.get("html_content")
        components.html(html_content, height=800, scrolling=True)
        
        st.download_button("📥 Download HTML", html_content, file_name="manual.html", mime="text/html")
        
    with col2:
        st.markdown("### 🛠️ Source Markdown")
        st.text_area("Markdown Source", final_result, height=400)
    
    # --- Thumbnail Generator (Common) ---
    st.divider()
    st.header("🖼️ YouTube-style Thumbnail")
    
    if st.button("サムネイルを生成"):
        thumb_html = generate_thumbnail_html(final_result)
        StateManager.set("thumbnail_html", thumb_html)
        # Parse logic is inside generate, but we want to edit. 
        # Ideally we should parse first into state. For now, let's keep simple.
        # To support editing, we need to extract the data.
        # Refactor: Let's assume generate_thumbnail_html returns HTML. 
        # For editable, we should split parse/render like Manga.
        # Re-using logic from original app.py:
        from services.manual_generator import parse_thumbnail_content
        t_data = parse_thumbnail_content(final_result)
        StateManager.set("thumb_data", t_data)
        st.rerun()

    if StateManager.get("thumb_data"):
        t_data = StateManager.get("thumb_data")
        
        # Editor
        with st.expander("🎨 サムネイル編集 (Edit)", expanded=False):
            t_data["main_text"] = st.text_input("Main Text", t_data.get("main_text",""))
            t_data["sub_text"] = st.text_input("Sub Text", t_data.get("sub_text",""))
            
            st.text(f"Img Prompt: {t_data.get('img_prompt','')}")
            if st.button("🖼️ 背景画像を生成 (DALL-E 3)"):
                 url = generate_dalle_image(t_data.get('img_prompt'))
                 if url:
                     t_data["img_url"] = url
                     st.rerun()
            
            input_url = st.text_input("Background Image URL", t_data.get("img_url", ""))
            if input_url: t_data["img_url"] = input_url
            
            StateManager.set("thumb_data", t_data)
        
        # Render
        thumb_html = render_thumbnail_from_data(t_data)
        components.html(thumb_html, height=400)
        st.download_button("📥 Download Thumbnail HTML", thumb_html, file_name="thumbnail.html", mime="text/html")

    # --- PPTX ---
    st.divider()
    if st.button("📊 Download as PPTX"):
        with st.spinner("Converting to PowerPoint..."):
            slide_json = generate_slide_content_json(final_result)
            file_name = create_presentation(slide_json)
            with open(file_name, "rb") as f:
                 st.download_button("📥 Click to Download PPTX", f, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

    if st.button("🔙 最初に戻る"):
        StateManager.set("stage", "input")
        st.rerun()
