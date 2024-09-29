import streamlit as st
from llm import Chatbot
from PyPDF2 import PdfReader

# Initialize the chatbot
openai_api_key = "EMPTY"
openai_api_base = "http://192.168.0.105:7182/v1"
chatbot = Chatbot(api_key=openai_api_key, base_url=openai_api_base)

# Define command handling function
def handle_commands(command):
    if command == "/restart":
        st.session_state.conversation_history = []  # Reset conversation history
        return "Conversation restarted."
    elif command == "/clear":
        st.session_state.conversation_history = []  # Clear conversation history
        return "Conversation cleared."
    return None

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None

# Automatically detect the user's system theme
st.sidebar.markdown("<p> Choose a theme </p>", unsafe_allow_html=True)
theme = st.sidebar.selectbox("", ["System Default", "Dark", "Light"], key="themebox")

# Define CSS styles for themes
if theme == "Dark":
    st.markdown(
        """
        <style>
        :root {
            --bg-color: #1e1e1e;
            --text-color: #ffffff;
            --button-bg: #333333;
            --button-color: #ffffff;
        }
        .main {
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        .stButton>button {
            background-color: var(--button-bg);
            color: var(--button-color);
        }
        .stTextInput label {
            color: var(--text-color);  /* Change 'You:' color based on theme */
        }
        </style>
        """, unsafe_allow_html=True
    )
elif theme == "Light":
    st.markdown(
        """
        <style>
        :root {
            --bg-color: #ffffff;
            --text-color: #000000;
            --button-bg: #e0e0e0;
            --button-color: #000000;
        }
        .main {
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        .stButton>button {
            background-color: var(--button-bg);
            color: var(--button-color);
        }
        .stTextInput label {
            color: var(--text-color);  /* Change 'You:' color based on theme */
        }
        </style>
        """, unsafe_allow_html=True
    )

# Title of the web app
st.markdown("""<h1 style='text-align: center; font-weight: bold; color: var(--text-color);'>OpenAI Chatbot</h1>
<h5 style='text-align: left; font-weight: normal; color: var(--text-color); margin-bottom: 2px;'>Let's have a quick chat !!</h5>""", unsafe_allow_html=True)

# Sidebar action selection
st.sidebar.markdown("<p> Select an action</p>", unsafe_allow_html=True)
action = st.sidebar.selectbox("", ["None", "Download Conversation", "Upload a file"], key="action_selectbox")

# File uploader handling
if action == "Upload a file":
    st.sidebar.markdown("File uploader will appear on the main page.")
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"],label_visibility="collapsed")

    if uploaded_file:
        st.session_state.uploaded_file_name = uploaded_file.name  # Store the filename
        if uploaded_file.type == "text/plain":
            st.session_state.uploaded_file_content = uploaded_file.read().decode("utf-8").splitlines()
        elif uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = []
            for page in reader.pages:
                pdf_text.append(page.extract_text())
            st.session_state.uploaded_file_content = "\n".join(pdf_text)

# Input for user queries
user_input = st.text_input("You:", placeholder="Type your request here...", key="user_input")

if st.button("Enter"):
    if user_input:
        command_response = handle_commands(user_input.strip())

        if command_response:
            st.markdown(f"**Bot:** {command_response}")
        else:
            summary_requested = "summary" in user_input.lower()
            if st.session_state.uploaded_file_content:
                pdf_content = st.session_state.uploaded_file_content
                
                if summary_requested:
                    # Use a focused prompt for generating a coherent summary
                    summary_prompt = f"Please provide a comprehensive summary of the following content:\n{pdf_content}"
                    summary = chatbot.generate_response([], summary_prompt)  # Generate summary without history
                    summary_message = summary.strip()
                    st.session_state.conversation_history.append((user_input, summary_message))
                    st.markdown(f"**Bot:** {summary_message}")
                
                else:
                    # Use a focused prompt for answering questions based on the content
                    question_prompt = f"Please answer the following questions based on the content:\nContent: {pdf_content}\nQuestions: {user_input}"
                    response = chatbot.generate_response([], question_prompt)  # Get specific answers without history
                    response_message = response.strip()
                    st.session_state.conversation_history.append((user_input, response_message))
                    st.markdown(f"**Bot:** {response_message}")

            else:
                bot_response = chatbot.generate_response(st.session_state.conversation_history, user_input)
                st.session_state.conversation_history.append((user_input, bot_response))
                st.markdown(f"**Bot:** {bot_response}")

        user_input = ""  # Clear input after processing

# Function to download conversation as a text file
def download_conversation():
    conversation_text = "\n".join([f"You: {query}\nBot:\n {response}" 
                                   for query, response in st.session_state.conversation_history])
    
    st.download_button(
        label="Download Conversation",
        data=conversation_text,
        file_name="conversation.txt",
        mime="text/plain",
        key="download_button"
    )

# Display download button if "Download Conversation" is selected
if action == "Download Conversation":
    download_conversation()

# Display conversation history
if st.session_state.conversation_history:
    for query, response in reversed(st.session_state.conversation_history):
        user_style = f"background-color: var(--bg-color); color: var(--text-color);"
        bot_style = f"background-color: rgba(209, 232, 255, 0.7); color: var(--text-color);"
        line_color = f"var(--text-color)"

        st.markdown(f'''
        <div style="{user_style} padding:10px; border-radius:10px; margin-bottom:10px;">
            <strong>You:</strong> {query}
        </div>
        <div style="{bot_style} padding:10px; border-radius:10px; margin-top:5px; margin-bottom:10px;">
            <strong>Bot:</strong> {response}
        </div>
        <hr style="border: 1px solid {line_color}; margin: 10px 0;">
        ''', unsafe_allow_html=True)
