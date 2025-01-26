from app import app
import pytest
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    os.environ['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            # Use in-memory database for testing
            app.config['DATABASE'] = ':memory:'
            from app import init_db
            init_db()
        yield client

def test_save_note(client):
    response = client.post('/', data={
        'title': 'Test Title',
        'content': 'Test Content'
    }, follow_redirects=True)
    assert b'Note saved successfully!' in response.data

def test_empty_form_submission(client):
    response = client.post('/', data={
        'title': '',
        'content': ''
    }, follow_redirects=True)
    assert b'Title and content are required!' in response.data

def test_delete_note(client):
    # First create a note
    client.post('/', data={'title': 'To Delete', 'content': 'Content'})
    response = client.get('/delete/1', follow_redirects=True)
    assert b'Note deleted successfully!' in response.data

def test_edit_note(client):
    # Create then edit
    client.post('/', data={'title': 'Original', 'content': 'Content'})
    response = client.post('/edit/1', data={
        'title': 'Updated',
        'content': 'New Content'
    }, follow_redirects=True)
    assert b'Note updated successfully!' in response.data