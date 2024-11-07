import streamlit as st
import requests
import pandas
import re
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import SimpleDirectoryReader


openai.api_key = st.secrets.openai_key

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

def extract_number_before_hash(text):
  match = re.search(r"(\d+)\s?#", text)
  if match:
    return str(match.group(1))
  return None

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
            if "pnr" in prompt.lower():  # Check if the prompt contains 'PNR Status'
                response_text = "Please enter your PNR number followed by #"
            elif "#" in prompt.lower():
                pnr_number = extract_number_before_hash(prompt.lower())
                url = "https://jsonplaceholder.typicode.com/posts/"+pnr_number
                response = requests.get(url).json()["title"]
                response_text = response
            
            else:
                response = chat_engine.chat(prompt)
                response_text = response.response
            st.write(response_text)
            message = {"role": "assistant", "content": response_text}
            st.session_state.messages.append(message) # Add response to message history
