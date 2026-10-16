import requests

BASE_URL = "http://localhost:3000"

def test_get_members():
    response = requests.get(f"{BASE_URL}/members")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if len(data)> 0:
       member = data[0]

       assert "user_id" in member
       assert "username" in member
       assert "email" in member
       assert "status" in member

       assert isinstance(member["user_id"], int)
       assert isinstance(member["username"], str)
       assert isinstance(member["email"], str)
       assert isinstance(member["status"], str)