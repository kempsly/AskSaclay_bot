import streamlit as st
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
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from firebase_config import db  # Import Firestore database
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

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
@st.cache_data
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
    retriever_web_tool = create_retriever_tool(retriever_web, "paris-saclay-search", "Search any information about Paris-Saclay University")

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

# # Get the chatbot prompt
# def get_prompt():
#     return ChatPromptTemplate.from_messages([
#         ("system", "You are an AI assistant specialized in answering questions about Paris-Saclay University.\
#             Use the following pieces of retrieved documents to answer.\
#             Please answer in the same language as the query.\
#             If the query is in French, respond in French.\
#             If the query is in English, respond in English.\
#             If the query is in Spanish, respond in Spanish.\
#             If the query is in any other language, respond in that language. If the user great you, you should great him also and ask him politely what does he need"),
#         MessagesPlaceholder(variable_name="chat_history"),  # Add chat history
#         ("human", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for agent execution
#     ])

def get_prompt():
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are an AI assistant specialized in answering questions about Paris-Saclay University. 
            Your goal is to provide accurate, concise, and helpful information to users.

            **Instructions:**
            1. Always respond in the same language as the user's query.
               - If the query is in French, respond in French.
               - If the query is in English, respond in English.
               - If the query is in Spanish, respond in Spanish.
               - For any other language, respond in that language.
            2. If the user greets you, respond with a polite greeting and ask how you can assist them.
            3. Use the retrieved documents to provide accurate and relevant answers.
            4. Be polite, professional, and engaging in all interactions.
            5. If you don't know the answer, politely inform the user and suggest alternative resources or actions.

            **Examples:**
            - User: "Bonjour!"
              Assistant: "Bonjour! Comment puis-je vous aider aujourd'hui?"
            - User: "Hi, what are the research areas at Paris-Saclay?"
              Assistant: "Hello! Paris-Saclay University is known for its research in fields like physics, engineering, life sciences, and social sciences. Is there a specific area you're interested in?"
            - User: "Hola, ¿cómo estás?"
              Assistant: "¡Hola! Estoy aquí para ayudarte. ¿En qué puedo asistirte hoy?"
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),  # Add chat history
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for agent execution
    ])
    
# Save chat history to Firestore
def save_chat_history(user_id, chat_history):
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            # Update the existing document
            user_ref.update({
                "chat_history": chat_history
            })
            logging.debug(f"Chat history updated for user {user_id}.")
        else:
            # Create a new document if it doesn't exist
            user_ref.set({
                "chat_history": chat_history
            })
            logging.debug(f"New document created for user {user_id}.")
    except Exception as e:
        logging.error(f"Error saving chat history: {e}")
        st.error(f"Error saving chat history: {e}")

# Save feedback to Firestore
def save_feedback(user_id, message_index, feedback):
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            # Update the feedback for the specific message
            user_ref.update({
                f"messages.{message_index}.feedback": feedback
            })
            logging.debug(f"Feedback saved for message {message_index} of user {user_id}.")
        else:
            logging.error(f"User document not found for {user_id}.")
    except Exception as e:
        logging.error(f"Error saving feedback: {e}")
        st.error(f"Error saving feedback: {e}")

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

# Chatbot UI
def chatbot_ui():

    # Use st.markdown with HTML to customize the font size
    st.markdown("<h3>🌟 Get answers and insights about Paris-Saclay in seconds</h3>", unsafe_allow_html=True)

    # st.title("🌟 Get answers and insights about Paris-Saclay in seconds")

    # Initialize session state for token usage
    if "daily_token_usage" not in st.session_state:
        st.session_state.daily_token_usage = 0
    if "last_reset_time" not in st.session_state:
        st.session_state.last_reset_time = datetime.now()

    # Check if the daily token limit has been reset
    if (datetime.now() - st.session_state.last_reset_time) >= timedelta(days=1):
        st.session_state.daily_token_usage = 0  # Reset token usage
        st.session_state.last_reset_time = datetime.now()

    # Initialize tools and agent
    tools = initialize_tools()
    agent_executor = initialize_bot(tools, groq_api_key)

    # Sidebar settings
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center;">
                <h1 style="margin: 0;">🤖 AskSaclayAI</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Display daily token usage
        st.write(f"Daily Token Usage: {st.session_state.daily_token_usage}/{DAILY_TOKEN_LIMIT}")

        # Initialize session state for managing multiple chat sessions
        if "sessions" not in st.session_state:
            st.session_state.sessions = {}
        if "current_session" not in st.session_state:
            st.session_state.current_session = None

        # Create a new chat
        if st.button("New Chat"):
            # Generate a unique session ID
            session_id = f"Chat {len(st.session_state.sessions) + 1}"
            st.session_state.current_session = session_id
            st.session_state.sessions[session_id] = {
                "messages": [
                    {"role": "assistant", "content": "Hello! I'm AskSaclay AI, your virtual assistant at Paris-Saclay University. \
                        How can I assist you with information about courses, events, campus, or any other queries?"}
                ],
                "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                "token_count": 0  # Initialize token count for the session
            }
            st.session_state.memory = st.session_state.sessions[session_id]["memory"]
            st.rerun()

        # Display list of chat sessions in the sidebar
        session_titles = list(st.session_state.sessions.keys())
        if session_titles:
            selected_session = st.selectbox("Chat History", session_titles, index=session_titles.index(st.session_state.current_session) if st.session_state.current_session else 0)
            if selected_session != st.session_state.current_session:
                st.session_state.current_session = selected_session
                st.session_state.memory = st.session_state.sessions[selected_session]["memory"]
                st.rerun()  # Refresh the app to load the selected session

        # Add a button to delete the current session
        if st.session_state.current_session and st.button("Delete Current Session"):
            del st.session_state.sessions[st.session_state.current_session]
            st.session_state.current_session = None
            st.session_state.memory = None
            st.rerun()

    # Display chat history for the current session
    if st.session_state.current_session:
        st.subheader(f"Chat: {st.session_state.current_session}")
        current_session = st.session_state.sessions[st.session_state.current_session]
        for i, message in enumerate(current_session["messages"]):
            st.chat_message(message["role"]).write(message['content'])

            # Display like/dislike buttons for assistant messages
            if message["role"] == "assistant":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Like", key=f"like_{i}"):
                        # Save feedback to session state
                        current_session["messages"][i]["feedback"] = "liked"
                        st.toast("Thanks for your feedback! 😊")

                        # Save feedback to Firestore
                        if "user" in st.session_state:
                            user_id = st.session_state.user["localId"]
                            save_feedback(user_id, i, "liked")
                with col2:
                    if st.button("👎 Dislike", key=f"dislike_{i}"):
                        # Save feedback to session state
                        current_session["messages"][i]["feedback"] = "disliked"
                        st.toast("Thanks for your feedback! We'll improve. 😊")

                        # Save feedback to Firestore
                        if "user" in st.session_state:
                            user_id = st.session_state.user["localId"]
                            save_feedback(user_id, i, "disliked")

    # Accept user input and process the message
    if prompt := st.chat_input(placeholder="Ask me anything about Paris-Saclay University!"):
        if st.session_state.daily_token_usage >= DAILY_TOKEN_LIMIT:
            st.warning("You have reached the daily token limit. Please try again tomorrow.")
            return

        if not st.session_state.current_session:
            # Create a new session with the first question as the title
            session_id = prompt[:50] + "..." if len(prompt) > 50 else prompt
            st.session_state.current_session = session_id
            st.session_state.sessions[session_id] = {
                "messages": [
                    {"role": "assistant", "content": "Hello! I'm AskSaclay AI, your virtual assistant at Paris-Saclay University.\
                        How can I assist you with information about courses, events, campus, or any other queries?"}
                ],
                "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                "token_count": 0  # Initialize token count for the session
            }
            st.session_state.memory = st.session_state.sessions[session_id]["memory"]

        # Append user message to the current session and update token count
        current_session = st.session_state.sessions[st.session_state.current_session]
        current_session["messages"].append({"role": "user", "content": prompt})
        current_session["token_count"] += count_tokens(prompt)  # Update token count
        st.session_state.daily_token_usage += count_tokens(prompt)  # Update daily token usage
        st.chat_message("user").write(prompt)

        # Run the agent to process the input
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            with st.spinner("Searching for an answer..."):  # Display spinner while processing
                try:
                    response = process_input(agent_executor, prompt)
                    current_session["messages"].append({'role': 'assistant', 'content': response})
                    current_session["token_count"] += count_tokens(response)  # Update token count
                    st.session_state.daily_token_usage += count_tokens(response)  # Update daily token usage
                    st.write(response)

                    # Save chat history to Firestore
                    if "user" in st.session_state:
                        user_id = st.session_state.user["localId"]
                        logging.debug(f"Saving chat history for user {user_id}.")
                        save_chat_history(user_id, current_session["messages"])
                except Exception as e:
                    error_message = str(e)
                    st.error(f"An error occurred: {error_message}")
                    if "Rate limit reached" in error_message:
                        wait_time = extract_wait_time(error_message)
                        if wait_time:
                            st.warning(f"Rate limit exceeded. Please try again in {wait_time}.")
                        else:
                            st.warning("Rate limit exceeded. Please wait a moment and try again.")
                            
                            



# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# ##--------------------------------------------------------------------------
# # WITHOUT SAVING THE CHAT HISTORY IN OUR DATABASE

# # import streamlit as st
# # import os
# # import re
# # from datetime import datetime, timedelta
# # from pathlib import Path
# # from transformers import AutoTokenizer
# # from dotenv import load_dotenv
# # from langchain_groq import ChatGroq
# # from langchain.memory import ConversationBufferMemory
# # from langchain.agents import AgentExecutor, create_openai_tools_agent
# # from langchain.tools import Tool
# # from langchain.callbacks.streamlit import StreamlitCallbackHandler
# # from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# # from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
# # from langchain_community.vectorstores import FAISS, Chroma
# # from langchain_community.tools import WikipediaQueryRun
# # from langchain_community.utilities import WikipediaAPIWrapper
# # from langchain.tools import DuckDuckGoSearchRun
# # from langchain_openai import OpenAIEmbeddings
# # from langchain.tools.retriever import create_retriever_tool
# # from langchain_text_splitters import RecursiveCharacterTextSplitter

# # # Load environment variables
# # load_dotenv()
# # groq_api_key = os.getenv("GROQ_API_KEY")
# # os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
# # os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
# # os.environ["LANGCHAIN_TRACING_V2"] = "true"
# # os.environ["LANGCHAIN_PROJECT"] = "SaclayAI Search Engine"

# # # Define the model's context window and token threshold
# # MODEL_CONTEXT_WINDOW = 8192  # Tokens for llama3-70b-8192
# # TOKEN_THRESHOLD = int(MODEL_CONTEXT_WINDOW * 0.9)  # 90% of the context window
# # DAILY_TOKEN_LIMIT = 500000  # Tokens per day

# # # Use the GPT-2 tokenizer as a fallback
# # tokenizer = AutoTokenizer.from_pretrained("gpt2")

# # def count_tokens(text):
# #     """Count the number of tokens in a given text."""
# #     return len(tokenizer.encode(text))

# # def extract_wait_time(error_message):
# #     """Extract the wait time from the Groq API rate limit error message."""
# #     match = re.search(r"Please try again in (\d+m\d+\.\d+s)", error_message)
# #     if match:
# #         return match.group(1)
# #     return None

# # # Load PDF documents for RAG
# # @st.cache_data
# # def load_pdfs():
# #     pdf_folder = Path("pdf_data")
# #     documents = []
# #     for pdf_file in pdf_folder.glob("*.pdf"):
# #         loader = PyPDFLoader(str(pdf_file))
# #         docs = loader.load()
# #         documents.extend(docs)
# #     return documents

# # # Initialize tools
# # def initialize_tools():
# #     # Load PDF documents
# #     documents = load_pdfs()

# #     # Using OpenAI Embeddings
# #     persist_directory = "./chroma_store"
# #     os.makedirs(persist_directory, exist_ok=True)
# #     embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
# #     splits = text_splitter.split_documents(documents)
# #     vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory)
# #     retriever_pdf = vectorstore.as_retriever()

# #     # Create PDF retriever tool
# #     retriever_pdf_tool = create_retriever_tool(retriever_pdf, name="pdf_retriever", description="Retrieve relevant information from uploaded PDF documents.")

# #     # Web scraping tools (Paris-Saclay website)
# #     loader_website = WebBaseLoader("https://www.universite-paris-saclay.fr")
# #     docs_web = loader_website.load()
# #     documents_web = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs_web)
# #     vectordb_web = FAISS.from_documents(documents_web, embeddings)
# #     retriever_web = vectordb_web.as_retriever()
# #     retriever_web_tool = create_retriever_tool(retriever_web, "paris-saclay-search", "Search any information about Université Paris-Saclay")

# #     # Wikipedia tool
# #     api_wapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=250)
# #     wiki = WikipediaQueryRun(api_wrapper=api_wapper_wiki)

# #     # DuckDuckGo search tool
# #     duckduckgo_search = DuckDuckGoSearchRun()

# #     # Combine tools into a list
# #     tools = [retriever_pdf_tool, wiki, duckduckgo_search, retriever_web_tool]
# #     return tools

# # # Initialize the chatbot
# # def initialize_bot(tools, groq_api_key):
# #     # Initialize LLM
# #     llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

# #     # Initialize memory
# #     memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# #     # Create agent
# #     prompt = get_prompt()
# #     agent = create_openai_tools_agent(llm, tools, prompt)
# #     agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
# #     return agent_executor

# # # Get the chatbot prompt
# # def get_prompt():
# #     return ChatPromptTemplate.from_messages([
# #         ("system", "You are an AI assistant specialized in answering questions about Paris-Saclay University.\
# #             Use the following pieces of retrieved documents to answer.\
# #             Please answer in the same language as the query.\
# #             If the query is in French, respond in French.\
# #             If the query is in English, respond in English.\
# #             If the query is in Spanish, respond in Spanish.\
# #             If the query is in any other language, respond in that language."),
# #         MessagesPlaceholder(variable_name="chat_history"),  # Add chat history
# #         ("human", "{input}"),
# #         MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for agent execution
# #     ])

# # # Process user input
# # def process_input(agent_executor, input_text):
# #     try:
# #         response = agent_executor.invoke({"input": input_text})
# #         return response["output"]
# #     except Exception as e:
# #         error_message = str(e)
# #         if "Rate limit reached" in error_message:
# #             wait_time = extract_wait_time(error_message)
# #             if wait_time:
# #                 return f"Rate limit exceeded. Please try again in {wait_time}."
# #             else:
# #                 return "Rate limit exceeded. Please wait a moment and try again."
# #         return f"An error occurred: {error_message}"

# # # Chatbot UI
# # def chatbot_ui():
# #     st.title("AskSaclay: Your AI Assistant for Paris-Saclay")

# #     # Initialize session state for token usage
# #     if "daily_token_usage" not in st.session_state:
# #         st.session_state.daily_token_usage = 0
# #     if "last_reset_time" not in st.session_state:
# #         st.session_state.last_reset_time = datetime.now()

# #     # Check if the daily token limit has been reset
# #     if (datetime.now() - st.session_state.last_reset_time) >= timedelta(days=1):
# #         st.session_state.daily_token_usage = 0  # Reset token usage
# #         st.session_state.last_reset_time = datetime.now()

# #     # Initialize tools and agent
# #     tools = initialize_tools()
# #     agent_executor = initialize_bot(tools, groq_api_key)

# #     # Sidebar settings
# #     with st.sidebar:
# #         st.markdown(
# #             """
# #             <div style="display: flex; align-items: center;">
# #                 <h1 style="margin: 0;">🤖 AskSaclayAI</h1>
# #             </div>
# #             """,
# #             unsafe_allow_html=True
# #         )

# #         # Display daily token usage
# #         st.write(f"Daily Token Usage: {st.session_state.daily_token_usage}/{DAILY_TOKEN_LIMIT}")

# #         # Initialize session state for managing multiple chat sessions
# #         if "sessions" not in st.session_state:
# #             st.session_state.sessions = {}
# #         if "current_session" not in st.session_state:
# #             st.session_state.current_session = None

# #         # Create a new chat
# #         if st.button("New Chat"):
# #             # Generate a unique session ID
# #             session_id = f"Chat {len(st.session_state.sessions) + 1}"
# #             st.session_state.current_session = session_id
# #             st.session_state.sessions[session_id] = {
# #                 "messages": [
# #                     {"role": "assistant", "content": "Hello! I'm AskSaclay AI, your virtual assistant at Paris-Saclay University. How can I assist you with information about courses, events, campus, or any other queries?"}
# #                 ],
# #                 "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
# #                 "token_count": 0  # Initialize token count for the session
# #             }
# #             st.session_state.memory = st.session_state.sessions[session_id]["memory"]
# #             st.rerun()

# #         # Display list of chat sessions in the sidebar
# #         session_titles = list(st.session_state.sessions.keys())
# #         if session_titles:
# #             selected_session = st.selectbox("Chat History", session_titles, index=session_titles.index(st.session_state.current_session) if st.session_state.current_session else 0)
# #             if selected_session != st.session_state.current_session:
# #                 st.session_state.current_session = selected_session
# #                 st.session_state.memory = st.session_state.sessions[selected_session]["memory"]
# #                 st.rerun()  # Refresh the app to load the selected session

# #         # Add a button to delete the current session
# #         if st.session_state.current_session and st.button("Delete Current Session"):
# #             del st.session_state.sessions[st.session_state.current_session]
# #             st.session_state.current_session = None
# #             st.session_state.memory = None
# #             st.rerun()

# #     # Display chat history for the current session
# #     if st.session_state.current_session:
# #         st.subheader(f"Chat: {st.session_state.current_session}")
# #         for message in st.session_state.sessions[st.session_state.current_session]["messages"]:
# #             st.chat_message(message["role"]).write(message['content'])

# #     # Check if the token count is approaching the threshold
# #     if st.session_state.current_session:
# #         current_session = st.session_state.sessions[st.session_state.current_session]
# #         if current_session["token_count"] >= TOKEN_THRESHOLD:
# #             st.warning(f"This conversation is approaching the token limit. To ensure the best performance, please start a new chat.")
# #             if st.button("Start New Chat"):
# #                 # Create a new session
# #                 session_id = f"Chat {len(st.session_state.sessions) + 1}"
# #                 st.session_state.current_session = session_id
# #                 st.session_state.sessions[session_id] = {
# #                     "messages": [
# #                         {"role": "assistant", "content": "Hello! I'm AskSaclay AI, your virtual assistant at Paris-Saclay University. How can I assist you with information about courses, events, campus, or any other queries?"}
# #                     ],
# #                     "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
# #                     "token_count": 0  # Reset token count for the new session
# #                 }
# #                 st.session_state.memory = st.session_state.sessions[session_id]["memory"]
# #                 st.rerun()

# #     # Accept user input and process the message
# #     if prompt := st.chat_input(placeholder="Ask me anything about Paris-Saclay University!"):
# #         if st.session_state.daily_token_usage >= DAILY_TOKEN_LIMIT:
# #             st.warning("You have reached the daily token limit. Please try again tomorrow.")
# #             return

# #         if not st.session_state.current_session:
# #             # Create a new session with the first question as the title
# #             session_id = prompt[:50] + "..." if len(prompt) > 50 else prompt
# #             st.session_state.current_session = session_id
# #             st.session_state.sessions[session_id] = {
# #                 "messages": [
# #                     {"role": "assistant", "content": "Hello! I'm AskSaclay AI, your virtual assistant at Paris-Saclay University. How can I assist you with information about courses, events, campus, or any other queries?"}
# #                 ],
# #                 "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
# #                 "token_count": 0  # Initialize token count for the session
# #             }
# #             st.session_state.memory = st.session_state.sessions[session_id]["memory"]

# #         # Append user message to the current session and update token count
# #         current_session = st.session_state.sessions[st.session_state.current_session]
# #         current_session["messages"].append({"role": "user", "content": prompt})
# #         current_session["token_count"] += count_tokens(prompt)  # Update token count
# #         st.session_state.daily_token_usage += count_tokens(prompt)  # Update daily token usage
# #         st.chat_message("user").write(prompt)

# #         # Run the agent to process the input
# #         with st.chat_message("assistant"):
# #             st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
# #             with st.spinner("Searching for an answer..."):  # Display spinner while processing
# #                 try:
# #                     response = process_input(agent_executor, prompt)
# #                     current_session["messages"].append({'role': 'assistant', 'content': response})
# #                     current_session["token_count"] += count_tokens(response)  # Update token count
# #                     st.session_state.daily_token_usage += count_tokens(response)  # Update daily token usage
# #                     st.write(response)

# #                     # Display like/dislike buttons after the assistant's response
# #                     col1, col2 = st.columns(2)
# #                     with col1:
# #                         if st.button("👍 Like", key=f"like_{len(current_session['messages'])}"):
# #                             current_session["feedback"] = "liked"
# #                             st.toast("Thanks for your feedback! 😊")
# #                     with col2:
# #                         if st.button("👎 Dislike", key=f"dislike_{len(current_session['messages'])}"):
# #                             current_session["feedback"] = "disliked"
# #                             st.toast("Thanks for your feedback! We'll improve. 😊")
# #                 except Exception as e:
# #                     error_message = str(e)
# #                     st.error(f"An error occurred: {error_message}")
# #                     if "Rate limit reached" in error_message:
# #                         wait_time = extract_wait_time(error_message)
# #                         if wait_time:
# #                             st.warning(f"Rate limit exceeded. Please try again in {wait_time}.")
# #                         else:
# #                             st.warning("Rate limit exceeded. Please wait a moment and try again.")