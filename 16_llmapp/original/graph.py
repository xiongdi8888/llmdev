import os
from typing import Annotated
import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict

os.environ['OPENAI_API_KEY'] = os.environ['ENV_OPENAI_API_KEY']
os.environ['TAVILY_API_KEY'] = os.environ['ENV_TAVILY_API_KEY']
MODEL_NAME = 'gpt-4o-mini'
memory = MemorySaver()
graphs = {} # support multi session
SYSTEM_PROMPT = """너는 애니메이션 짱구의 신짱 말투를 흉내내는 챗봇이야. 대답은 입력언어와 동일하게 한다. 항상 친근하고 장난기 있게 답하되, 정보는 정확하게 말해. 답변 마지막 줄에는 반드시 출처를 표시해. 형식은 '출처: ...' 로 하고, 사용한 출처만 골라 적어. 웹 검색을 사용했으면 'WWW[Tivoly]', data 디렉토리 자료 기반 RAG를 사용했으면 'local[RAG]', 둘 다 아니면 'LLM Generated'이라고 적어."""

class State(TypedDict):
    messages: Annotated[list, add_messages]

def create_index(persist_directory, embedding_model):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    loader = DirectoryLoader(f'{current_directory}/../chatbot/data/pdf', glob='./*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()
    encoding_name = tiktoken.encoding_for_model(MODEL_NAME).name
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(encoding_name)
    texts = text_splitter.split_documents(documents)
    return Chroma.from_documents(texts, embedding_model, persist_directory=persist_directory)

def define_tools():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    persist_directory = f'{current_directory}/chroma_db'
    embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
    if os.path.exists(persist_directory):
        db = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
    else:
        db = create_index(persist_directory, embedding_model)
    retriever = db.as_retriever()
    retriever_tool = create_retriever_tool(retriever, 'retrieve_company_rules', 'Search and return company rules')
    tavily_tool = TavilySearchResults(max_results=2)
    return [retriever_tool, tavily_tool]

def build_graph(model_name, memory):
    graph_builder = StateGraph(State)
    tools = define_tools()
    tool_node = ToolNode(tools)
    graph_builder.add_node('tools', tool_node)
    llm = ChatOpenAI(model_name=model_name)
    llm_with_tools = llm.bind_tools(tools)
    def chatbot(state: State):
        messages = state['messages']
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]
        return {'messages': [llm_with_tools.invoke(messages)]}
    graph_builder.add_node('chatbot', chatbot)
    graph_builder.add_conditional_edges('chatbot', tools_condition)
    graph_builder.add_edge('tools', 'chatbot')
    graph_builder.set_entry_point('chatbot')
    return graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_message: str, thread_id):
    global graphs
    response = graphs['thread_id'].invoke({'messages': [('user', user_message)]}, {'configurable': {'thread_id': thread_id}}, stream_mode='values')
    return response['messages'][-1].content

def get_bot_response(user_message, memory, thread_id):
    #deprecated: single user mode
    #global graph
    #if graph is None:
    #    graph = build_graph(MODEL_NAME, memory)
    #return stream_graph_updates(graph, user_message, thread_id)
    # support multi session
    global graphs
    if thread_id not in graphs:
        graphs['thread_id'] = build_graph(MODEL_NAME, memory)
    return stream_graph_updates(user_message, thread_id)

def get_messages_list(memory, thread_id):
    messages = []
    memories = memory.get({'configurable': {'thread_id': thread_id}})['channel_values']['messages']
    for message in memories:
        if isinstance(message, HumanMessage):
            messages.append({'class': 'user-message', 'text': message.content.replace('\n', '<br>')})
        elif isinstance(message, AIMessage) and message.content != '':
            messages.append({'class': 'bot-message', 'text': message.content.replace('\n', '<br>')})
    return messages
