import pytest
from langchain_openai import OpenAIEmbeddings
from original.graph import get_bot_response, get_messages_list, memory, build_graph, define_tools, create_index

USER_MESSAGE_1 = '1たす2は？'
USER_MESSAGE_2 = '東京駅のイベントの検索結果を教えて'
USER_MESSAGE_3 = '有給休暇の日数は？'
THREAD_ID = 'test_thread'

@pytest.fixture
def setup_memory():
    memory.storage.clear()
    return memory

@pytest.fixture
def setup_graph():
    return build_graph('gpt-4o-mini', memory)

def test_define_tools():
    tools = define_tools()
    assert len(tools) > 0
    assert any(tool.name == 'retrieve_company_rules' for tool in tools)

def test_create_index():
    persist_directory = './test_chroma_db'
    embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
    index = create_index(persist_directory, embedding_model)
    assert index is not None

def test_get_bot_response_single_message(setup_memory):
    response = get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    assert isinstance(response, str)
    assert '3' in response

def test_get_bot_response_with_rag(setup_memory):
    response = get_bot_response(USER_MESSAGE_3, setup_memory, THREAD_ID)
    assert isinstance(response, str)
    assert '有給休暇' in response

def test_get_bot_response_multiple_messages(setup_memory):
    get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    get_bot_response(USER_MESSAGE_2, setup_memory, THREAD_ID)
    messages = get_messages_list(setup_memory, THREAD_ID)
    assert len(messages) >= 2
    assert any('1たす2' in msg['text'] for msg in messages if msg['class'] == 'user-message')
    assert any('東京駅' in msg['text'] for msg in messages if msg['class'] == 'user-message')

def test_memory_clear_on_new_session(setup_memory):
    get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    initial_messages = get_messages_list(setup_memory, THREAD_ID)
    assert len(initial_messages) > 0
    setup_memory.storage.clear()
    cleared_messages = setup_memory.get({'configurable': {'thread_id': THREAD_ID}})
    assert cleared_messages is None or 'channel_values' not in cleared_messages

def test_build_graph(setup_memory):
    graph = build_graph('gpt-4o-mini', setup_memory)
    response = graph.invoke({'messages': [('user', USER_MESSAGE_1)]}, {'configurable': {'thread_id': THREAD_ID}}, stream_mode='values')
    assert response['messages'][-1].content

def test_get_messages_list(setup_memory):
    get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    messages = get_messages_list(setup_memory, THREAD_ID)
    assert len(messages) > 0
    assert any(isinstance(msg, dict) for msg in messages)
    assert any(msg['class'] == 'user-message' for msg in messages)
    assert any(msg['class'] == 'bot-message' for msg in messages)

if __name__ == '__main__':
    pytest.main()
