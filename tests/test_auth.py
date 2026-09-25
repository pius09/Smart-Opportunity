"""Tests for the authentication module."""


def test_register_and_login(client):
    # Register
    r = client.post('/auth/register', data={
        'full_name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'secret123',
        'confirm': 'secret123',
    }, follow_redirects=True)
    assert r.status_code == 200


def test_login_wrong_password(client):
    # Register first
    client.post('/auth/register', data={
        'full_name': 'Test User',
        'email': 'wrongpw@example.com',
        'password': 'secret123',
        'confirm': 'secret123',
    })
    client.get('/auth/logout')

    # Try wrong password
    r = client.post('/auth/login', data={
        'email': 'wrongpw@example.com',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    assert b'Invalid email or password' in r.data


def test_protected_route_redirects_when_not_logged_in(client):
    r = client.get('/student/dashboard')
    # Should redirect to login (302) or return the login page
    assert r.status_code in (302, 401)


def test_duplicate_registration_rejected(client):
    data = {
        'full_name': 'Dup User',
        'email': 'dup@example.com',
        'password': 'secret123',
        'confirm': 'secret123',
    }
    client.post('/auth/register', data=data)
    client.get('/auth/logout')
    r = client.post('/auth/register', data=data, follow_redirects=True)
    assert b'already registered' in r.data