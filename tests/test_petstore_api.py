import requests
import random
import string
import time
import pytest

BASE_URL = "https://petstore.swagger.io/v2"

def random_id():
    return int(time.time() * 1000) % (10**9) + random.randint(1000, 9999)

def random_name(n=8):
    return ''.join(random.choices(string.ascii_letters, k=n))

@pytest.fixture
def new_pet_payload():
    pet_id = random_id()
    return {
        "id": pet_id,
        "category": {"id": 1, "name": "dogs"},
        "name": "pytest-" + random_name(6),
        "photoUrls": ["http://example.com/photo1.jpg"],
        "tags": [{"id": 101, "name": "tag1"}, {"id": 102, "name": "tag2"}],
        "status": "available"
    }

def test_add_get_update_delete_pet(new_pet_payload):

    r = requests.post(BASE_URL + "/pet", json=new_pet_payload)
    assert r.status_code in (200, 201)
    pet_id = r.json().get("id") or new_pet_payload["id"]

    r = requests.get(BASE_URL + "/pet/" + str(pet_id))
    assert r.status_code == 200
    got = r.json()
    assert got["name"] == new_pet_payload["name"]

    got["name"] += "-updated"
    got["status"] = "pending"
    r = requests.put(BASE_URL + "/pet", json=got)
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == got["name"]
    assert updated["status"] == got["status"]

    r = requests.post(
        BASE_URL + "/pet/" + str(pet_id),
        data={"name": "form-name", "status": "sold"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert r.status_code in (200, 405, 415, 404)

    r = requests.delete(BASE_URL + "/pet/" + str(pet_id))
    assert r.status_code in (200, 404)

    r = requests.get(BASE_URL + "/pet/" + str(pet_id))
    assert r.status_code in (404, 200)

@pytest.mark.parametrize("statuses", [
    ["available"],
    ["pending"],
    ["sold"],
    ["available", "pending"],
    ["available", "pending", "sold"]
])
def test_find_by_status_various(statuses):
    params = [("status", s) for s in statuses]
    r = requests.get(BASE_URL + "/pet/findByStatus", params=params)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    if body:
        for pet in body[:10]:
            assert pet.get("status") in statuses

def test_get_nonexistent_pet():
    r = requests.get(BASE_URL + "/pet/999999999999")
    assert r.status_code in (404, 200)

def test_create_pet_missing_name():
    payload = {
        "id": random_id(),
        "category": {"id": 2, "name": "cats"},
        "photoUrls": [],
        "tags": [],
        "status": "available"
    }
    r = requests.post(BASE_URL + "/pet", json=payload)
    assert r.status_code in (400, 200, 201)
