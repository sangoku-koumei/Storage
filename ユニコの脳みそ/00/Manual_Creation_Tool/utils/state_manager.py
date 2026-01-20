import streamlit as st

class StateManager:
    """
    StreamlitのSession Stateを一元管理するクラス
    初期化漏れやキーのタイプミスを防ぐ
    """
    
    DEFAULTS = {
        "stage": "input",
        "input_text": "",
        "options_text": "",
        "selected_option": "",
        "hearing_qs": None,
        "final_result": "",
        "last_result": "",
        "current_data": None,
        "html_content": "",
        "thumbnail_html": "",
        "thumb_data": None,
        "manual_input": ""
    }

    @staticmethod
    def init():
        for key, value in StateManager.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_all():
        """Get all session state data."""
        return dict(st.session_state)

    @staticmethod
    def save_project(filepath):
        """Save current session state to a JSON file."""
        data = dict(st.session_state)
        # Filter out non-serializable objects if any (mostly simple types here)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    @staticmethod
    def load_project(filepath):
        """Load session state from a JSON file."""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v
            st.rerun()
        else:
            st.error("File not found.")

    @staticmethod
    def get(key):
        return st.session_state.get(key, StateManager.DEFAULTS.get(key))

    @staticmethod
    def set(key, value):
        st.session_state[key] = value

    @staticmethod
    def append(key, value):
        current = StateManager.get(key)
        if isinstance(current, str):
            st.session_state[key] = current + value
        else:
            # List or other appendable types
            pass
