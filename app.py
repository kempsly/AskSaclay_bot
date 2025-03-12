import streamlit as st 
import os 
from langchain_chroma import Chroma 
from langchain.chains import create_history_aware_retriever, create_retrieval_chain 
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain_community.chat_message_histories import ChatMessageHistory 
from langchain_core.chat_history import BaseChatMessageHistory 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_groq import ChatGroq 
from langchain_core.runnables.history import RunnableWithMessageHistory 

from langchain_ollama import OllamaEmbeddings 
from langchain_text_splitters import RecursiveCharacterTextSplitter 

from langchain_community.document_loaders import PyPDFLoader 
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path

##Tools
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchRun

###For customs tools
from langchain_community.document_loaders import WebBaseLoader 
from langchain_community.vectorstores import FAISS 

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.llms import OpenAI

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool





##### Frist of all load the environnment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
openai.api_key=os.getenv("OPENAI_API_KEY")
## Langsmith Tracking
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="SaclayAI Search Engine"


#####Loading the pdf document for The RAG
#pdf folder containing the files
pdf_folder = Path("pdf_data")

#Empty list to store all documents
documents = []
# Loop through all pdf files in the document
for pdf_file in pdf_folder.glob("*.pdf"):
    # Initialize the loader for each PDF
    loader = PyPDFLoader(str(pdf_file))
    # Load the documents from the PDF
    docs = loader.load()
    # Add them to the list of all documents
    documents.extend(docs)
    
#Using openai embedding instead
embeddings=OpenAIEmbeddings(model="text-embedding-3-large")
# Split and create embeddings for the documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
splits = text_splitter.split_documents(documents)
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
retriever_pdf = vectorstore.as_retriever()   

############### Creating tools ######################
###Retriever pdf tools
retriever_pdf_tool = create_retriever_tool(
    retriever_pdf, 
    name="pdf_retriever", 
    description="Retrieve relevant information from uploaded PDF documents."
)
###Customs tools
loader_website = WebBaseLoader("https://www.universite-paris-saclay.fr")
docs_web = loader_website.load()
documents_web = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs_web)
vectordb_web = FAISS.from_documents(documents_web, embeddings)
retriever_web = vectordb_web.as_retriever()

retriever_web_tool=create_retriever_tool(retriever_web,"paris-saclay-search",
                                         "Search any information about Universite paris-saclay ")

###wikipedia tools
api_wapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=250)
wiki=WikipediaQueryRun(api_wrapper=api_wapper_wiki)

##DuckDucko search tools
# Initialize DuckDuckGo search tool
duckduckgo_search = DuckDuckGoSearchRun()

# #####Combining our differents tools
tools = [retriever_pdf_tool, wiki, duckduckgo_search, retriever_web_tool]
# The multilingual model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")  

######### CUSTOM PROMPT ############

# Step 2: Define the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant specialized in answering questions about Paris-Saclay University.\
        Use the following pieces of retrieved documents to answer.\
            Please answer in the same language as the query.\
                If the query is in French, respond in French.\
                If the query is in English, respond in English.\
                    If the query is in any other language, respond in that language"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for agent execution
    ("human", "{input}"),
])
# Step 4: Create the agent
agent = create_openai_tools_agent(llm, tools, prompt)
# Step 5: Initialize the AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


######################################Defining the streamlit application logic##################################
####################################################################################
####################################################################################
####################################################################################
st.title("AskSaclay: Your AI Assistant for Paris-Saclay")

st.sidebar.title("Settings")
#Using our Groq api key
api_key = groq_api_key

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I'm AskSaclay AI, your virtual assistant at Paris-Saclay University. \
            How can I assist you with information about courses, events, campus, or any other queries?"}
    ]
# Display all messages in the chat
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message['content'])
    