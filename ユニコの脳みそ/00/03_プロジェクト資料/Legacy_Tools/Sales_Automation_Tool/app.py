
from ai_generator import generate_sales_emails, generate_manual_content, generate_deliverable, set_api_key, scrape_company_info, verify_email_faithfulness
from db import init_db, add_company, get_all_companies, update_status, check_daily_limit

# ... (Previous imports)

def main():
    st.set_page_config(page_title="AI Sales Agent v5.0 (Pro)", layout="wide")
    st.title("🤖 AI Sales Agent v5.0 (Pro Hardened)")
    st.markdown("Professional Grade: Anti-Ban / Reputation Guard / Anti-Hallucination")

    # DB初期化
    init_db()

    # Sidebar: Settings & SMTP
    with st.sidebar:
        st.header("🛡️ Reputation Guardian")
        is_safe, count = check_daily_limit(30)
        st.metric("Sent Today", f"{count}/30", delta=30-count)
        if not is_safe:
            st.error("🚫 Daily Limit Reached!")
            
        st.divider()
        st.header("⚙️ General Settings")
        
        # ... (Rest of sidebar)

    # ... (Tabs 1, 2, 4, 5, 6 logic remains same, but let's update CRM tab to show Fact Check)

    # --- Tab 3: CRM & Send ---
    with tab3:
        st.header("📊 CRM & Fact-Check")
        df_crm = get_all_companies()
        
        if not df_crm.empty:
            for index, row in df_crm.iterrows():
                with st.expander(f"[{row['status']}] {row['name']}"):
                    st.write(f"**URL**: {row['url']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        email_body = st.text_area("Email", row['email_content'], key=f"e_{row['id']}", height=150)
                        
                        # Fact Check Button
                        if st.button("🤥 Fact Check", key=f"fc_{row['id']}"):
                            res = verify_email_faithfulness(row['vision_summary'], email_body)
                            if "SAFE" in res:
                                st.success(res)
                            else:
                                st.warning(res)
                                
                    with col_b:
                        target_email = st.text_input("To:", key=f"t_{row['id']}")
                        
                        if st.button("🚀 Send (with Guard)", key=f"s_{row['id']}"):
                            if smtp_email and smtp_password and target_email:
                                res = send_email_smtp(
                                    {"server": smtp_server, "port": smtp_port, "email": smtp_email, "password": smtp_password},
                                    target_email, "提案の件", email_body
                                )
                                if res["success"]:
                                    update_status(row['id'], "Sent")
                                    st.success("Sent!")
                                    st.experimental_rerun()
                                else:
                                    st.error(res["message"])
                            else:
                                st.error("Check SMTP settings.")

        # API Key Management (Shared)
        KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secret_api_key.txt")
        saved_key = ""
        if os.path.exists(KEY_FILE):
             with open(KEY_FILE, "r") as f:
                 saved_key = f.read().strip()

        api_key = st.text_input("OpenAI API Key", value=saved_key, type="password")
        if api_key:
            set_api_key(api_key)
            if api_key != saved_key:
                with open(KEY_FILE, "w") as f:
                     f.write(api_key)
                st.success("Key Saved!")
        
        st.divider()
        st.header("📧 SMTP Settings")
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587)
        smtp_email = st.text_input("Email", placeholder="you@gmail.com")
        smtp_password = st.text_input("App Password", type="password")
        
    # Tabs
    tab1, tab2, tab4, tab5, tab3, tab6 = st.tabs(["👤 Single", "📦 Batch", "🕵️ Prospect Agent", "🤖 Meta-Agent", "📊 CRM", "🎁 Delivery (New!)"])

    # --- Tab 1: Single Generation ---
    with tab1:
        st.header("1. Client Hearing & Analysis")
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("相手企業名", placeholder="株式会社〇〇")
            company_url = st.text_input("相手企業URL", placeholder="https://...")
            genre = st.text_input("業種", value=DEFAULT_HEARING_ITEMS["genre"])
        with col2:
            service = st.text_input("提供サービス", value=DEFAULT_HEARING_ITEMS["service"])
            strength = st.text_input("強み", value=DEFAULT_HEARING_ITEMS["strength"])
            problem = st.text_input("課題", value=DEFAULT_HEARING_ITEMS["problem"])
            goal = st.text_input("ゴール", value=DEFAULT_HEARING_ITEMS["goal"])

        if st.button("✨ Generate Proposal", key="btn_single"):
            if not api_key: st.error("API Key required.")
            else:
                with st.spinner("Processing..."):
                    scraped_data = scrape_company_info(company_url) if company_url else None
                    vision_summary = scraped_data['vision'] if scraped_data and 'vision' in scraped_data else ""
                    
                    client_info = {
                        "company_name": company_name or "Unknown",
                        "genre": genre, "target": "Unknown", "service": service,
                        "strength": strength, "problem": problem, "goal": goal
                    }
                    emails = generate_sales_emails(client_info, scraped_data)
                    add_company(company_name, company_url, genre, emails, vision_summary)
                    st.success("Generated & Saved!")
                    st.text_area("Result", emails, height=200)

    # --- Tab 2: Batch Generation ---
    with tab2:
        st.header("Batch Gen (CSV)")
        uploaded_file = st.file_uploader("CSV", type="csv")
        if uploaded_file and st.button("🚀 Process CSV"):
            df = pd.read_csv(uploaded_file)
            progress_bar = st.progress(0)
            for index, row in df.iterrows():
                c_name = row.get('company_name', 'Unknown')
                c_url = row.get('url', '')
                scraped = scrape_company_info(c_url) if c_url else None
                vision = scraped['vision'] if scraped else ""
                
                info = DEFAULT_HEARING_ITEMS.copy()
                info['company_name'] = c_name
                emails = generate_sales_emails(info, scraped)
                add_company(c_name, c_url, "Batch", emails, vision)
                progress_bar.progress((index + 1) / len(df))
            st.success("Done!")

    # --- Tab 4: Prospecting Agent ---
    with tab4:
        st.header("🕵️ Prospecting Agent (Discovery)")
        search_query = st.text_input("Search Keyword", value="営業DX パートナー募集")
        max_results = st.slider("Max Results", 5, 20, 10)
        
        if st.button("🤖 Find Prospects"):
            if not api_key: st.error("API Key required.")
            else:
                with st.spinner("Prospecting..."):
                    prospects = find_prospects(search_query, max_results)
                    for p in prospects:
                        c_name = p['company_name']
                        c_url = p['url']
                        scraped = scrape_company_info(c_url)
                        emails = generate_sales_emails({"company_name":c_name, **DEFAULT_HEARING_ITEMS}, scraped)
                        add_company(c_name, c_url, f"Agent: {search_query}", emails, scraped['vision'])
                    st.success(f"Found {len(prospects)} companies.")

    # --- Tab 5: Meta-Agent (Autonomous) ---
    with tab5:
        st.header("🤖 Autonomous Meta-Agent")
        st.markdown("自律的に「営業自動化案件」を探し、提案メールを下書きします。")
        if st.button("🔄 Run 1 Autonomous Cycle"):
            if not api_key: st.error("API Key required.")
            else:
                with st.spinner("Meta-Agent is working..."):
                    try:
                        job_automation_cycle()
                        st.success("Cycle Complete! Check CRM Tab.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- Tab 3: CRM & Send ---
    with tab3:
        st.header("📊 CRM & Execution")
        df_crm = get_all_companies()
        if not df_crm.empty:
            for index, row in df_crm.iterrows():
                with st.expander(f"[{row['status']}] {row['name']}"):
                    st.write(f"**URL**: {row['url']}")
                    email_body = st.text_area("Email", row['email_content'], key=f"e_{row['id']}", height=150)
                    target_email = st.text_input("To:", key=f"t_{row['id']}")
                    if st.button("🚀 Send", key=f"s_{row['id']}"):
                        if smtp_email and smtp_password and target_email:
                            res = send_email_smtp({"server": smtp_server, "port": smtp_port, "email": smtp_email, "password": smtp_password}, target_email, "提案の件", email_body)
                            if res["success"]:
                                update_status(row['id'], "Sent")
                                st.success("Sent!")
                            else: st.error(res["message"])
                        else: st.error("Check SMTP settings.")
        else: st.info("No records.")

    # --- Tab 6: Delivery (New!) ---
    with tab6:
        st.header("🎁 Work Delivery Generator")
        st.markdown("受注した仕事の「成果物」をAIに生成させます。")
        
        job_type = st.selectbox("納品するパッケージタイプ", 
                                ["AI Sales Auto Package (おすすめ)", "AI Hiring Package", "MA/HubSpot Setup", "Inside Sales Setup", "DX Consulting"])
        
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("クライアント名", placeholder="株式会社〇〇")
            c_target = st.text_input("ターゲット顧客", placeholder="年商10億以上の製造業")
        with col2:
            c_problem = st.text_input("クライアントの課題", placeholder="リードはあるがアポに繋がらない")
            c_service = st.text_input("商材名", placeholder="SaaSツール")
        
        if st.button("✨ Generate Deliverable"):
            if not api_key: st.error("API Key required.")
            else:
                with st.spinner("Generating Deliverables..."):
                    client_info = {
                        "company_name": c_name, "target": c_target,
                        "problem": c_problem, "service": c_service, "strength": ""
                    }
                    result = generate_deliverable(job_type, client_info)
                    st.success("Generated!")
                    st.text_area("Final Deliverable (Copy & Paste to Word/PDF)", result, height=500)

if __name__ == "__main__":
    main()
