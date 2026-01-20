
import streamlit as st

# ユーザーデータベース（デモ用）
USERS = {
    "free_user": {"password": "password", "plan": "Free", "features": ["proposal"]},
    "pro_user": {"password": "password", "plan": "Pro", "features": ["proposal", "auto_research", "social_research"]},
    "agency_user": {"password": "password", "plan": "Agency", "features": ["proposal", "auto_research", "social_research", "sop", "bulk"]}
}

def login():
    """ログイン処理とサイドバー表示"""
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        start_logout()
        return True

    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.user = USERS[username]
            st.session_state.username = username
            st.sidebar.success(f"Logged in as {username} ({USERS[username]['plan']} Plan)")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password")
    
    return False

def start_logout():
    """ログアウトボタンとユーザー情報表示"""
    user = st.session_state.user
    st.sidebar.markdown(f"**User:** {st.session_state.username}")
    st.sidebar.markdown(f"**Plan:** {user['plan']}")
    
    if user['plan'] == "Free":
        st.sidebar.info("💡 Upgrade to Pro to unlock Auto Research!")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

def check_permission(feature):
    """機能へのアクセス権限を確認"""
    if not st.session_state.user:
        return False
    return feature in st.session_state.user["features"]
