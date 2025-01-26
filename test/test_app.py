import sys
import os
import pytest

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, init_db  # Explicitly import init_db

@pytest.fixture
def client():
    """Configure app for testing"""
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'DATABASE': ':memory:'
    })
    
    with app.test_client() as client:
        with app.app_context():
            init_db()  # Now properly imported
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
    client.post('/', data={'title': 'To Delete', 'content': 'Content'})
    response = client.get('/delete/1', follow_redirects=True)
    assert b'Note deleted successfully!' in response.data

def test_edit_note(client):
    client.post('/', data={'title': 'Original', 'content': 'Content'})
    response = client.post('/edit/1', data={
        'title': 'Updated',
        'content': 'New Content'
    }, follow_redirects=True)
    assert b'Note updated successfully!' in response.data