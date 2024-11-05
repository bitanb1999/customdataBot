import streamlit as st
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import SimpleDirectoryReader
# Apply custom CSS for white background and blue text color
st.markdown(
    """
    <style>
    /* Set the background color to white for the entire app */
    .stApp {
        background-color: grey;
        color: ##0066b2; /* SAP-like blue color for text */
    }

    /* Customize chat message bubbles */
    .st-chat-message {
        background-color: ##B9D9EB; /* Light blue background for messages */
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        font-size: 16px;
    }

    /* Styling assistant responses */
    .st-chat-message.assistant {
        color: ##1F305E; /* Slightly darker blue for assistant text */
    }

    /* Styling user input */
    .st-chat-message.user {
        color: ##041E42; /* Darker blue for user text */
    }
    </style>
    """,
    unsafe_allow_html=True
)

openai.api_key = st.secrets.openai_key
st.header("Chat with the ARIBA Bot 💬📚")

if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about any ARIBA query you have!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the ARIBA platform and your job is to answer technical questions. Assume that all questions are related to ARIBA and SAP. Keep your answers technical and based on facts – do not hallucinate features.")
        index = VectorStoreIndex.from_documents(docs)
        return index

index = load_data()
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if "PNR Status" in prompt:  # Check if the prompt contains 'PNR Status'
                response_text = "Please refer to the ARIBA Portal directly for such inquiries."
            else:
                response = chat_engine.chat(prompt)
                response_text = response.response
            st.write(response_text)
            message = {"role": "assistant", "content": response_text}
            st.session_state.messages.append(message) # Add response to message history
