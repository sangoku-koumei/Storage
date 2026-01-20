import streamlit as st
from utils.state_manager import StateManager
from services.manual_generator import scrape_website_content, perform_company_research, extract_text_from_pdf, extract_text_from_pptx
from services.manual_builder import ManualBuilder

def render_input_view():
    st.subheader("Step 1: 原稿データの入力 (Input)")

    # --- Manual Type Selector (New Feature) ---
    builder = ManualBuilder() # Logic only
    presets = builder.get_presets()
    
    # Get current selection or default
    current_type = StateManager.get("manual_type") or "SOP"
    
    # Create formatted options for display
    type_options = list(presets.keys())
    # Find index of current selection
    try:
        default_index = type_options.index(current_type)
    except ValueError:
        default_index = 0

    col_type, col_vol, col_focus = st.columns([1, 1, 2])
    
    with col_type:
        selected_key = st.selectbox(
            "作成するマニュアルの種別 (Type)", 
            options=type_options,
            format_func=lambda x: presets[x]["name"],
            index=default_index
        )
        if selected_key != current_type:
            StateManager.set("manual_type", selected_key)
            
    with col_vol:
        vol_options = ["Short", "Standard", "Deep"]
        current_vol = StateManager.get("manual_volume") or "Standard"
        selected_vol = st.selectbox(
            "ボリューム (Volume)",
            options=vol_options,
            index=vol_options.index(current_vol) if current_vol in vol_options else 1
        )
        if selected_vol != current_vol:
            StateManager.set("manual_volume", selected_vol)

    with col_focus:
        st.info(f"💡 **Focus**: {presets[selected_key]['focus']}")
        # st.caption(f"Tips: {presets[selected_key]['instruction']}")

    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 テキスト直接入力", "🌐 URLから自動取得", "🔍 企業リサーチ (Deep Search)", "📂 PDF/PPTX Upload"])

    # Tab 2: URL
    with tab2:
        url_input = st.text_input("抽出したいWebサイトのURL (会社概要、採用ページなど)", placeholder="https://example.com/recruit")
        if st.button("🌐 サイト内容を抽出"):
            if url_input:
                with st.spinner("サイトを解析中..."):
                    scraped_text = scrape_website_content(url_input)
                    if "Error" in scraped_text:
                        st.error(scraped_text)
                    else:
                        st.success("抽出完了！ [テキスト直接入力]タブに追加されました。")
                        append_formatted = f"\n\n--- Source: {url_input} ---\n{scraped_text}"
                        StateManager.append("manual_input", append_formatted)
                        # No rerun needed if we use StateManager effectively, but clearer to rerun to show update
                        st.rerun()

    # Tab 3: Research
    with tab3:
        st.info("会社名を入力するだけで、ネット上の情報を全方位リサーチし、マニュアルの種にします。")
        company_query = st.text_input("リサーチしたい会社名", placeholder="株式会社〇〇")
        if st.button("🚀 ディープリサーチ実行"):
            if company_query:
                with st.spinner(f"「{company_query}」を徹底調査中... (検索 -> URL特定 -> 内部リンク解析)"):
                    research_result = perform_company_research(company_query)
                    if "Error" in research_result:
                        st.error(research_result)
                    else:
                        st.success("リサーチ完了！ [テキスト直接入力]タブに追加されました。")
                        append_formatted = f"\n\n--- Research: {company_query} ---\n{research_result}"
                        StateManager.append("manual_input", append_formatted)
                        st.rerun()

    # Tab 4: Upload
    with tab4:
        st.info("PDFやPowerPointの資料をアップロードして、マニュアルの元ネタにします。(複数選択可)")
        uploaded_files = st.file_uploader("Upload File(s)", type=["pdf", "pptx"], accept_multiple_files=True)
        if uploaded_files and st.button("📂 テキスト抽出実行"):
            with st.spinner("ファイルを読み込み中..."):
                combined_extracted = ""
                for uploaded_file in uploaded_files:
                    text = ""
                    if uploaded_file.name.endswith(".pdf"):
                        text = extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.name.endswith(".pptx"):
                        text = extract_text_from_pptx(uploaded_file)
                    
                    if text:
                        combined_extracted += f"\n\n--- Source File: {uploaded_file.name} ---\n{text}"

                if combined_extracted:
                    st.success(f"{len(uploaded_files)}件のファイルから抽出完了！ [テキスト直接入力]タブに追加されました。")
                    StateManager.append("manual_input", combined_extracted)
                    st.rerun()
                else:
                    st.warning("抽出できるテキストが見つかりませんでした。")

    # Tab 1: Manual Input (Placed last to avoid instantiation error)
    with tab1:
        st.markdown("👇 全ての読み込んだデータはここに集約されます。自由に編集・追記可能です。")
        # Use StateManager.get to populate default value
        current_val = StateManager.get("manual_input")
        new_val = st.text_area("ここに箇条書きや乱雑なメモを貼り付けてください", value=current_val, height=400, placeholder="業務内容、または商品サービスの概要...", key="manual_input_widget")
        
        # Update state manually because key mismatch ("manual_input" vs "manual_input_widget")
        if new_val != current_val:
            StateManager.set("manual_input", new_val)

    # Next Button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Step 2: 不明点の確認へ進む ➡️"):
            input_text = StateManager.get("manual_input")
            if not input_text:
                st.warning("テキストを入力してください！")
            else:
                from services.manual_generator import generate_hearing_questions
                
                # Get the selected preset info to pass to generator
                selected_preset = presets.get(selected_key)
                
                with st.spinner(f"AIが「{selected_preset['name']}」として分析・ヒアリング生成中..."):
                    # Pass preset_info for Meta-Prompting
                    qs = generate_hearing_questions(input_text, preset_info=selected_preset)
                    
                    StateManager.set("hearing_qs", qs)
                    StateManager.set("input_text", input_text) # Sync explicit input_text
                    StateManager.set("stage", "hearing")
                    st.rerun()
