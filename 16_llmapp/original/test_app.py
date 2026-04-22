import pytest
from original.app import app
from original.graph import memory, get_messages_list

USER_MESSAGE_1 = '1たす2は？'
USER_MESSAGE_2 = '東京駅のイベントの検索結果を教えて'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'your_secret_key'
    client = app.test_client()
    with client.session_transaction() as session:
        session.clear()
    yield client

def test_index_get_request(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<form' in response.data
    assert memory.storage == {}

def test_index_post_request(client):
    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is None
    response = client.post('/', data={'user_message': USER_MESSAGE_1})
    assert response.status_code == 200
    decoded_data = response.data.decode('utf-8')
    assert '1たす2' in decoded_data
    assert '3' in decoded_data
    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is not None

def test_memory_persistence_with_session(client):
    client.post('/', data={'user_message': USER_MESSAGE_1})
    client.post('/', data={'user_message': USER_MESSAGE_2})
    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is not None
    messages = get_messages_list(memory, thread_id)
    assert len(messages) >= 2
    assert any('1たす2' in msg['text'] for msg in messages if msg['class'] == 'user-message')
    assert any('東京駅' in msg['text'] for msg in messages if msg['class'] == 'user-message')

def test_clear_endpoint(client):
    client.post('/', data={'user_message': USER_MESSAGE_1})
    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is not None
    response = client.post('/clear')
    assert response.status_code == 200
    assert b'<form' in response.data
    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is None
    cleared_messages = memory.get({'configurable': {'thread_id': thread_id}})
    assert cleared_messages is None
