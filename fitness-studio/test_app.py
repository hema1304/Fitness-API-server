import pytest
from unittest.mock import patch
from app import app, db
from models import FitnessClass, Booking



@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    with patch('app.create_tables'):
        with app.app_context():
            db.create_all()
            yield app.test_client()
            db.session.remove()
            db.drop_all()
    

def test_book_empty_body(client):
    response = client.post("/book", data=" ")
    assert response.status_code == 400
    assert "Empty or missing JSON body" in response.json["error"]


def test_book_malformed_json(client):
    response = client.post("/book", data="{invalid}", content_type='application/json')
    assert response.status_code == 400
    assert "Malformed JSON" in response.json["error"]


def test_book_invalid_email(client):
    db.session.add(FitnessClass(id=1, name="Yoga", datetime="2025-06-21 08:00", instructor="Alice", available_slots=1))
    db.session.commit()

    response = client.post("/book", json={
        "class_id": 1,
        "client_name": "John",
        "client_email": "invalid-email"
    })
    assert response.status_code == 400
    assert "Invalid email format" in response.json["error"]


def test_book_missing_field(client):
    db.session.add(FitnessClass(id=1, name="Yoga", datetime="2025-06-21 08:00", instructor="Alice", available_slots=1))
    db.session.commit()
    response = client.post("/book", json={
        "class_id": 1,
        "client_email": "john@example.com"
    })
    response_json = response.get_json()
    assert response.status_code == 400
    assert any('Missing required field' in err for err in response_json['error'])


def test_book_no_available_slot(client):
    db.session.add(FitnessClass(id=2, name="Zumba", datetime="2025-06-21 10:00", instructor="Bob", available_slots=0))
    db.session.commit()

    response = client.post("/book", json={
        "class_id": 2,
        "client_name": "John",
        "client_email": "john@example.com"
    })
    assert response.status_code == 201
    assert "No slots available" in response.json[0]["error"]


def test_book_valid(client):
    db.session.add(FitnessClass(id=3, name="HIIT", datetime="2025-06-21 12:00", instructor="Carol", available_slots=1))
    db.session.commit()

    response = client.post("/book", json={
        "class_id": 3,
        "client_name": "Jane",
        "client_email": "jane@example.com"
    })
    assert response.status_code == 201
    assert response.json[0]["message"] == "Booking confirmed"


def test_get_bookings_found(client):
    db.session.add(FitnessClass(id=4, name="Pilates", datetime="2025-06-21 14:00", instructor="David", available_slots=3))
    db.session.add(Booking(class_id=4, class_name="Pilates", client_name="Alice", client_email="alice@example.com"))
    db.session.commit()

    response = client.get("/bookings?email=alice@example.com")
    assert response.status_code == 200
    assert response.json[0]["client_email"] == "alice@example.com"


def test_get_bookings_missing_email(client):
    response = client.get("/bookings")
    assert response.status_code == 400
    assert "Email parameter is required" in response.json["error"]


def test_get_bookings_not_found(client):
    response = client.get("/bookings?email=someone@example.com")
    assert response.status_code == 404
    assert "No bookings found" in response.json["error"]
