"""Streamlit chatbot application with authentication and streaming."""
import os
import json
import httpx
import streamlit as st
from typing import Optional
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def init_session_state():
    """Initialize session state variables."""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new user."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=30.0
        )
        if response.status_code == 201:
            return True, "Registration successful! Please login."
        else:
            error_detail_message = response.json().get("detail", "Registration failed")
            return False, error_detail_message
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(username: str, password: str) -> tuple[bool, str]:
    """Login user and get access token."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/auth/token",
            data={
                "username": username,
                "password": password
            },
            timeout=30.0
        )
        if response.status_code == 200:
            token_response_data = response.json()
            st.session_state.access_token = token_response_data["access_token"]
            st.session_state.username = username
            return True, "Login successful!"
        else:
            return False, "Invalid username or password"
    except Exception as e:
        return False, f"Error: {str(e)}"


def logout():
    """Logout user."""
    st.session_state.access_token = None
    st.session_state.username = None
    st.session_state.messages = []
    st.session_state.conversation_id = None


def stream_chat(message: str) -> Optional[str]:
    """Send message and stream response."""
    if not st.session_state.access_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    
    request_payload = {
        "message": message,
        "conversation_id": st.session_state.conversation_id
    }
    
    try:
        with httpx.stream(
            "POST",
            f"{API_BASE_URL}/chat/stream",
            json=request_payload,
            headers=headers,
            timeout=60.0
        ) as response:
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "content" in data:
                                full_response += data["content"]
                                # Update conversation_id if provided
                                if "conversation_id" in data and not st.session_state.conversation_id:
                                    st.session_state.conversation_id = data["conversation_id"]
                                yield data["content"]
                            elif "error" in data:
                                st.error(data["error"])
                                return
                        except json.JSONDecodeError:
                            continue
                return full_response
            else:
                st.error(f"Error: {response.status_code}")
                return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def show_login_page():
    """Show login/register page."""
    st.title("🤖 UARAG - Uncertainty Aware RAG")
    st.markdown("---")
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    with register_tab:
        st.subheader("Register")
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
            reg_submit = st.form_submit_button("Register")
            
            if reg_submit:
                if reg_username and reg_email and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 8:
                        st.error("Password must be at least 8 characters")
                    else:
                        success, message = register_user(reg_username, reg_email, reg_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")


def show_chat_page():
    """Show chat interface."""
    # Header with logout button
    title_column, action_column = st.columns([3, 1])
    with title_column:
        st.title("🤖 UARAG")
    with action_column:
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()
    
    st.markdown(f"**User:** {st.session_state.username}")
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response with streaming
        with st.chat_message("assistant"):
            streaming_message_placeholder = st.empty()
            accumulated_response = ""
            
            for chunk in stream_chat(prompt):
                if chunk:
                    accumulated_response += chunk
                    streaming_message_placeholder.markdown(accumulated_response + "▌")
            
            streaming_message_placeholder.markdown(accumulated_response)
        
        # Add assistant message
        if accumulated_response:
            st.session_state.messages.append({"role": "assistant", "content": accumulated_response})
    
    # Sidebar with conversation options
    with st.sidebar:
        st.header("Conversation")
        if st.button("New Conversation"):
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        if st.session_state.conversation_id:
            st.info(f"Conversation ID: {st.session_state.conversation_id}")
        
        st.markdown("---")
        st.header("About")
        st.markdown("""
        This chatbot uses:
        - **LLM**: Groq (llama-3.1-8b-instant)
        - **Framework**: LangChain
        - **Backend**: FastAPI
        - **Frontend**: Streamlit
        """)


def main():
    """Main application."""
    st.set_page_config(
        page_title="UARAG",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    if st.session_state.access_token:
        show_chat_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
