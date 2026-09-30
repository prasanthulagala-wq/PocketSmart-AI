from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_register_login_and_home():
    email = 'test@example.com'
    r = client.post('/api/register', json={'name':'Test User','email':email,'password':'password123'})
    assert r.status_code in (200, 409)
    r = client.post('/api/login', json={'email':email,'password':'password123'})
    assert r.status_code == 200
    token = r.json()['access_token']
    r = client.post('/generate-home', headers={'Authorization':f'Bearer {token}'}, json={'budget':100000,'city':'Chennai','rooms':['Living Room'],'style':'modern','priorities':'value','quantities':{'lights':2}})
    assert r.status_code == 200
    assert r.json()['planner'] == 'home'
