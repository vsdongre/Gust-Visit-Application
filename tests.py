import pytest
from datetime import datetime, timezone
from app import app, db, Visit


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data


def test_checkin_page_get(client):
    resp = client.get('/checkin')
    assert resp.status_code == 200
    assert b'Check-In' in resp.data


def test_checkin_creates_visit(client):
    resp = client.post('/checkin', data={
        'guest_name': 'Alice',
        'guest_email': 'alice@example.com',
        'guest_phone': '555-0100',
        'host_name': 'Bob',
        'purpose': 'Interview',
        'notes': '',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Alice' in resp.data

    with app.app_context():
        visit = Visit.query.first()
        assert visit is not None
        assert visit.guest_name == 'Alice'
        assert visit.check_out is None


def test_checkin_validation(client):
    resp = client.post('/checkin', data={
        'guest_name': '',
        'guest_email': '',
        'host_name': '',
        'purpose': '',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'required' in resp.data.lower()


def test_checkout(client):
    with app.app_context():
        visit = Visit(
            guest_name='Carol',
            guest_email='carol@example.com',
            host_name='Dave',
            purpose='Meeting',
        )
        db.session.add(visit)
        db.session.commit()
        visit_id = visit.id

    resp = client.post(f'/checkout/{visit_id}', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Carol' in resp.data or b'checked out' in resp.data.lower()

    with app.app_context():
        v = db.session.get(Visit, visit_id)
        assert v.check_out is not None


def test_visit_log(client):
    with app.app_context():
        visit = Visit(
            guest_name='Eve',
            guest_email='eve@example.com',
            host_name='Frank',
            purpose='Delivery',
        )
        db.session.add(visit)
        db.session.commit()

    resp = client.get('/log')
    assert resp.status_code == 200
    assert b'Eve' in resp.data


def test_visit_detail(client):
    with app.app_context():
        visit = Visit(
            guest_name='George',
            guest_email='george@example.com',
            host_name='Hannah',
            purpose='Tour',
        )
        db.session.add(visit)
        db.session.commit()
        visit_id = visit.id

    resp = client.get(f'/visit/{visit_id}')
    assert resp.status_code == 200
    assert b'George' in resp.data


def test_api_stats(client):
    resp = client.get('/api/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_visits' in data
    assert 'active_visitors' in data
    assert 'today_visits' in data


def test_api_active_visits(client):
    with app.app_context():
        visit = Visit(
            guest_name='Ivan',
            guest_email='ivan@example.com',
            host_name='Julia',
            purpose='Training',
        )
        db.session.add(visit)
        db.session.commit()

    resp = client.get('/api/active-visits')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(v['guest_name'] == 'Ivan' for v in data)


def test_visit_log_search(client):
    with app.app_context():
        visit = Visit(
            guest_name='Unique Guest XYZ',
            guest_email='unique@example.com',
            host_name='Host',
            purpose='Demo',
        )
        db.session.add(visit)
        db.session.commit()

    resp = client.get('/log?search=XYZ')
    assert resp.status_code == 200
    assert b'Unique Guest XYZ' in resp.data

    resp2 = client.get('/log?search=nonexistent1234')
    assert resp2.status_code == 200
    assert b'Unique Guest XYZ' not in resp2.data


def test_visit_log_status_filter(client):
    with app.app_context():
        from datetime import datetime, timezone
        active = Visit(guest_name='ActiveGuest', guest_email='a@x.com', host_name='H', purpose='P')
        completed = Visit(guest_name='DoneGuest', guest_email='d@x.com', host_name='H', purpose='P',
                          check_out=datetime.now(timezone.utc))
        db.session.add_all([active, completed])
        db.session.commit()

    resp = client.get('/log?status=active')
    assert b'ActiveGuest' in resp.data
    assert b'DoneGuest' not in resp.data

    resp2 = client.get('/log?status=completed')
    assert b'DoneGuest' in resp2.data
    assert b'ActiveGuest' not in resp2.data
