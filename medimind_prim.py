# -*- coding: utf-8 -*-
"""Medimind_prim

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ocLxu9WzwaVL93sc1ceD9ulFPzlkL2VZ
"""

!pip install --quiet fastapi uvicorn streamlit langchain openai faiss-cpu pypdf python-multipart python-dotenv
!pip install --quiet -U langchain langchain-community langchain-groq langchain-huggingface
!pip install fastembed

import os
os.environ["GROQ_API_KEY"] = "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"

from google.colab import files
uploaded = files.upload()
pdf_filename = list(uploaded.keys())[0]
pdf_path = "health.pdf"
os.rename(pdf_filename, pdf_path)
print(f"✅ File uploaded successfully: {pdf_path}")

!curl ifconfig.me

with open("chatbot.py", "w") as f:
    f.write("""import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import warnings

# Suppress LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Components
client = Groq(api_key=groq_api_key)
model = ChatGroq(model_name="llama3-70b-8192")
document_loader = PyPDFLoader('health.pdf')
document_data = document_loader.load()

text_division = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
document_chunks = text_division.split_documents(document_data)

embedder = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
vector_database = FAISS.from_documents(document_chunks, embedder)
retriever_tool = vector_database.as_retriever(search_type='similarity', search_kwargs={'k': 4})


instruction_template = \"\"\"
You are a knowledgeable assistant designed to answer queries based solely on the provided context.
If the information is not within the context, respond with 'I lack the necessary information.'
Provide concise answers in a single line.

Context: {context}

Query: {question}
\"\"\"

instruction_prompt = PromptTemplate(
    template=instruction_template, input_variables=["context", "question"]
)

# QA Chain Creation
knowledge_chain = RetrievalQA.from_chain_type(llm=model,
                                               chain_type='stuff',
                                               retriever=retriever_tool,
                                               return_source_documents=True,
                                               chain_type_kwargs={"prompt": instruction_prompt})

# Streamlit UI
st.set_page_config(page_title="MediMind 🧠💊", page_icon="🧠💊")

# Dual Background Styling
st.markdown(
    \"\"\"
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    /* Full Page Background */
    html, body, .stApp {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(to bottom, #F4F6F7, #E3F2FD, #BBDEFB);
        background-size: cover;
        color: #2C3E50; /* Dark Blue-Grey for Professional Look */
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #004D40, #00796B, #009688);
        padding: 20px;
        border-radius: 15px;
    }

    /* Sidebar Text */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p {
        color: white !important;
        text-align: center;
    }

    /* Title and Labels */
    .stTitle, .stMarkdown, .stHeader, .stTextArea label, .stTextInput label {
        color: #004D40; /* Deep Teal for Contrast */
        font-weight: bold;
    }

    /* Text Area & Input Fields */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(255, 255, 255, 0.85);
        color: #004D40;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #80DEEA;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #00796B;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        padding: 10px;
        transition: transform 0.2s ease-in-out, background 0.3s ease;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #005662;
    }

    /* Answer Box Styling */
    .answer-box {
        background-color: rgba(255, 255, 255, 0.9); /* Light Background */
        border-radius: 15px;
        padding: 15px;
        color: #2C3E50; /* Darker Font for Contrast */
        font-size: 16px;
        font-weight: bold;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    \"\"\",
    unsafe_allow_html=True
)

# Header
st.title("MediMind 🧠💊")

# Sidebar with Detailed About Section
with st.sidebar:
    st.header("🔍 About MediMind")

    st.markdown("🚀 **MediMind is your AI-powered healthcare companion.** It provides expert insights on symptoms, diseases, and treatments using cutting-edge AI models.")

    st.markdown("### 📌 Features")
    st.markdown("✅ **Instant Health Advice** - Get quick answers to health-related queries.")
    st.markdown("✅ **Disease Symptoms & Causes** - Know the early signs and risk factors.")
    st.markdown("✅ **Treatment & Remedies** - Understand medications and natural cures.")
    st.markdown("✅ **AI-Powered Accuracy** - Uses advanced AI models for reliable information.")

    st.markdown("---")
    st.markdown("🔗 **Powered by:**")
    st.markdown("- **Groq AI** for deep learning insights")
    st.markdown("- **LangChain** for intelligent retrieval")

# User Input Section
st.markdown("### 🩺 **Ask Your Health Query Below:**")
user_question = st.text_area("Type your question here...", height=100)

# Get Response Button
if st.button("💡 Get Health Advice"):
    if user_question:
        response = knowledge_chain(user_question)
        st.markdown("### 🏥 **Answer:**")
        st.markdown(f"<div class='answer-box'>{response['result']}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter a question.")
""")

import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import warnings

# Suppress LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Components
client = Groq(api_key=groq_api_key)
model = ChatGroq(model_name="llama3-70b-8192")
document_loader = PyPDFLoader('health.pdf')
document_data = document_loader.load()

text_division = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
document_chunks = text_division.split_documents(document_data)

embedder = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
vector_database = FAISS.from_documents(document_chunks, embedder)
retriever_tool = vector_database.as_retriever(search_type='similarity', search_kwargs={'k': 4})

instruction_template = """
You are a knowledgeable assistant designed to answer queries based solely on the provided context.
If the information is not within the context, respond with 'I lack the necessary information.'
Provide concise answers in a single line.

Context: {context}

Query: {question}
"""

instruction_prompt = PromptTemplate(
    template=instruction_template, input_variables=["context", "question"]
)

# QA Chain Creation
knowledge_chain = RetrievalQA.from_chain_type(llm=model,
                                              chain_type='stuff',
                                              retriever=retriever_tool,
                                              return_source_documents=True,
                                              chain_type_kwargs={"prompt": instruction_prompt})

# Streamlit UI
st.set_page_config(page_title="MediMind 🧠💊", page_icon="🧠💊", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    /* Full Page Background */
    html, body, .stApp {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(to bottom, #E3F2FD, #BBDEFB);
        background-size: cover;
        color: #2C3E50;
    }

    header, .st-emotion-cache-1v0mbdj {
        display: none !important;
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #004D40, #00796B, #009688);
        padding: 20px;
        border-radius: 15px;
    }

    /* Sidebar Text */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p {
        color: white !important;
        text-align: center;
    }

    /* Title and Labels */
    .stTitle, .stMarkdown, .stHeader, .stTextArea label, .stTextInput label {
        color: #004D40; /* Deep Teal for Contrast */
        font-weight: bold;
    }

    /* Text Area & Input Fields */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(255, 255, 255, 0.9);
        color: #004D40;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #80DEEA;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #00796B;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        padding: 10px;
        transition: transform 0.2s ease-in-out, background 0.3s ease;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #005662;
    }

    /* Answer Box Styling */
    .answer-box {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 15px;
        color: #2C3E50;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.title("MediMind 🧠💊")

# Sidebar with About Section
with st.sidebar:
    st.header("🔍 About MediMind")

    st.markdown("🚀 **MediMind is your AI-powered healthcare companion.** It provides expert insights on symptoms, diseases, and treatments using cutting-edge AI models.")

    st.markdown("### 📌 Features")
    st.markdown("✅ **Instant Health Advice** - Get quick answers to health-related queries.")
    st.markdown("✅ **Disease Symptoms & Causes** - Know the early signs and risk factors.")
    st.markdown("✅ **Treatment & Remedies** - Understand medications and natural cures.")
    st.markdown("✅ **AI-Powered Accuracy** - Uses advanced AI models for reliable information.")

    st.markdown("---")
    st.markdown("🔗 **Powered by:**")
    st.markdown("- **Groq AI** for deep learning insights")
    st.markdown("- **LangChain** for intelligent retrieval")

# User Input Section
st.markdown("### 🩺 **Ask Your Health Query Below:**")
user_question = st.text_area("Type your question here...", height=100)

# Get Response Button
if st.button("💡 Get Health Advice"):
    if user_question:
        response = knowledge_chain(user_question)
        st.markdown("### 🏥 **Answer:**")
        st.markdown(f"<div class='answer-box'>{response['result']}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter a question.")

!streamlit run --server.port 8000 --server.address 0.0.0.0 chatbot.py & npx localtunnel --port 8000

