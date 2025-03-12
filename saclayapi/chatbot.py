# chatbot.py
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from transformers import AutoTokenizer
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "SaclayAI Search Engine"

# Define the model's context window and token threshold
MODEL_CONTEXT_WINDOW = 8192  # Tokens for llama3-70b-8192
TOKEN_THRESHOLD = int(MODEL_CONTEXT_WINDOW * 0.9)  # 90% of the context window
DAILY_TOKEN_LIMIT = 500000  # Tokens per day

# Use the GPT-2 tokenizer as a fallback
tokenizer = AutoTokenizer.from_pretrained("gpt2")

def count_tokens(text):
    """Count the number of tokens in a given text."""
    return len(tokenizer.encode(text))

def extract_wait_time(error_message):
    """Extract the wait time from the Groq API rate limit error message."""
    match = re.search(r"Please try again in (\d+m\d+\.\d+s)", error_message)
    if match:
        return match.group(1)
    return None

# Load PDF documents for RAG
def load_pdfs():
    pdf_folder = Path("pdf_data")
    documents = []
    for pdf_file in pdf_folder.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        documents.extend(docs)
    return documents

# Initialize tools
def initialize_tools():
    # Load PDF documents
    documents = load_pdfs()

    # Using OpenAI Embeddings
    persist_directory = "./chroma_store"
    os.makedirs(persist_directory, exist_ok=True)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    splits = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory)
    retriever_pdf = vectorstore.as_retriever()

    # Create PDF retriever tool
    retriever_pdf_tool = create_retriever_tool(retriever_pdf, name="pdf_retriever", description="Retrieve relevant information from uploaded PDF documents.")

    # Web scraping tools (Paris-Saclay website)
    loader_website = WebBaseLoader("https://www.universite-paris-saclay.fr")
    docs_web = loader_website.load()
    documents_web = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs_web)
    vectordb_web = FAISS.from_documents(documents_web, embeddings)
    retriever_web = vectordb_web.as_retriever()
    retriever_web_tool = create_retriever_tool(retriever_web, "paris-saclay-search", "Search any information about Université Paris-Saclay")

    # Wikipedia tool
    api_wapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=250)
    wiki = WikipediaQueryRun(api_wrapper=api_wapper_wiki)

    # DuckDuckGo search tool
    duckduckgo_search = DuckDuckGoSearchRun()

    # Combine tools into a list
    tools = [retriever_pdf_tool, wiki, duckduckgo_search, retriever_web_tool]
    return tools

# Initialize the chatbot
def initialize_bot(tools, groq_api_key):
    # Initialize LLM
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

    # Initialize memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Create agent
    prompt = get_prompt()
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
    return agent_executor

# Get the chatbot prompt
def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant specialized in answering questions about Paris-Saclay University.\
            Use the following pieces of retrieved documents to answer.\
            Please answer in the same language as the query.\
            If the query is in French, respond in French.\
            If the query is in English, respond in English.\
            If the query is in Spanish, respond in Spanish.\
            If the query is in any other language, respond in that language."),
        MessagesPlaceholder(variable_name="chat_history"),  # Add chat history
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for agent execution
    ])

# Process user input
def process_input(agent_executor, input_text):
    try:
        response = agent_executor.invoke({"input": input_text})
        return response["output"]
    except Exception as e:
        error_message = str(e)
        if "Rate limit reached" in error_message:
            wait_time = extract_wait_time(error_message)
            if wait_time:
                return f"Rate limit exceeded. Please try again in {wait_time}."
            else:
                return "Rate limit exceeded. Please wait a moment and try again."
        return f"An error occurred: {error_message}"