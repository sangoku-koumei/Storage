
import streamlit as st
import os

# Modules
from auth import login, check_permission
from ai_engine import analyze_search_results, generate_ai_proposal, set_api_key, get_api_key
from search_engine import search_with_retry
from report_generator import generate_html_report
from social_research import analyze_youtube_video
from data import HTML_REPORT_TEMPLATE

# Page Config
st.set_page_config(page_title="Research Business Tool v3.0", layout="wide")

def main():
    # Login Logic
    if not login():
        return

    # Sidebar Menu based on Permissions
    st.sidebar.title("Menu")
    
    # API Key Handling
    # API Key Handling (Shared)
    KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secret_api_key.txt")
    
    # Try logic from file if memory is empty
    if not api_key and os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            file_key = f.read().strip()
            if file_key:
                set_api_key(file_key)
                api_key = file_key # Set for local scope

    if not api_key:
        api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
        if api_key_input:
            set_api_key(api_key_input)
            with open(KEY_FILE, "w") as f:
                 f.write(api_key_input)
            st.success("API Key Saved!")
            st.rerun()
        else:
            st.warning("⚠️ OpenAI API Key is required for AI features.")
    
    menu_options = []
    
    # [Free Plan Features]
    if check_permission("proposal"):
        menu_options.append("📝 Proposal Generator")
        
    # [Pro Plan Features]
    if check_permission("auto_research"):
        menu_options.append("🔍 Auto Research Report")
    if check_permission("social_research"):
        menu_options.append("📺 YouTube Analysis")
        
    # [Agency Plan Features]
    if check_permission("sop"):
        menu_options.append("📋 SOP Generator (Agency)")
        
    selection = st.sidebar.radio("Go to", menu_options)
    
    # --- Feature Implementation ---
    
    if selection == "📝 Proposal Generator":
        st.header("📝 AI Proposal Generator")
        st.info("Available for Free Plan and above.")
        
        genre = st.text_input("Project Genre (e.g., Beauty, Tech)")
        name = st.text_input("Your Name")
        hours = st.number_input("Available Hours/Week", min_value=1, value=10)
        
        if st.button("Generate Proposal"):
            if not api_key:
                st.error("Please set API Key first.")
            else:
                with st.spinner("Writing proposal..."):
                    proposal = generate_ai_proposal(genre, name, hours)
                    st.text_area("Generated Proposal", proposal, height=400)
                    st.download_button("Download Text", proposal, file_name=f"Proposal_{genre}.txt")

    elif selection == "🔍 Auto Research Report":
        st.header("🔍 Auto Research Report")
        st.success("✨ Pro Plan Feature")
        
        query = st.text_input("Research Keyword")
        
        if st.button("Start Research"):
            if not api_key:
                st.error("API Key required.")
            else:
                progress = st.progress(0)
                st.write("Searching web...")
                results = search_with_retry(query)
                progress.progress(50)
                
                if not results:
                    st.error("No search results found.")
                else:
                    st.write(f"Found {len(results)} sources. Analyzing with AI...")
                    analysis = analyze_search_results(query, results)
                    progress.progress(90)
                    
                    st.subheader("Analysis Summary")
                    st.markdown(analysis)
                    
                    # Generate Report
                    report_data = {
                        "title": f"Research Report: {query}",
                        "ai_analysis": analysis,
                        "search_results": results
                    }
                    filename = f"Report_{query}.html"
                    if generate_html_report(report_data, filename, HTML_REPORT_TEMPLATE):
                        progress.progress(100)
                        st.success(f"Report generated: {filename}")
                        with open(filename, "r", encoding="utf-8") as f:
                            st.download_button("Download HTML Report", f.read(), file_name=filename, mime="text/html")

    elif selection == "📺 YouTube Analysis":
        st.header("📺 YouTube Deep Analysis")
        st.success("✨ Pro Plan Feature")
        
        url = st.text_input("YouTube Video URL")
        
        if st.button("Analyze Video"):
            if not api_key:
                st.error("API Key required.")
            else:
                with st.spinner("Fetching transcript and analyzing..."):
                    result = analyze_youtube_video(url, api_key)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        st.subheader("Video Insights")
                        st.markdown(result)

    elif selection == "📋 SOP Generator (Agency)":
        st.header("📋 Agency SOP Generator")
        st.warning("👑 Agency Plan Feature")
        st.write("Generates Standard Operating Procedures for your team.")
        # (Simple implementation for demo)
        task = st.text_input("Task Name")
        if st.button("Generate SOP"):
            from data import SOP_TEMPLATES
            st.markdown(SOP_TEMPLATES["basic"].format(task_name=task))

if __name__ == "__main__":
    main()
