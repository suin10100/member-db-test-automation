
import os
import uuid
import requests
import mysql.connector
from dotenv import load_dotenv
import bcrypt

load_dotenv()

BASE_URL = "http://localhost:3000"



# TC-API-001: 회원가입 성공
def test_create_member():
    unique_id = uuid.uuid4().hex[:8]

    payload = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "Test1234!",
        "status": "ACTIVE"
    }

    response = requests.post(
        f"{BASE_URL}/members",
        json=payload
    )

    assert response.status_code == 201

    response_data = response.json()
    user_id = response_data["user_id"]

    try:
        assert isinstance(user_id, int)
        assert response_data["username"] == payload["username"]
        assert response_data["email"] == payload["email"]
        assert response_data["status"] == payload["status"]

    finally:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database="member_db",
            use_pure=True,
            connection_timeout=5
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM members WHERE user_id = %s",
                    (user_id,)
                )
            connection.commit()
        finally:
            connection.close()


# TC-API-002: 회원가입 후 DB 저장 데이터 검증
def test_create_member_db():
    unique_id = uuid.uuid4().hex[:8]

    payload = {
        "username": f"dbtest_{unique_id}",
        "email": f"dbtest_{unique_id}@example.com",
        "password": "Test1234!",
        "status": "ACTIVE"
    }

    response = requests.post(
        f"{BASE_URL}/members",
        json=payload
    )

    assert response.status_code == 201

    response_data = response.json()
    user_id = response_data["user_id"]

    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="member_db",
        use_pure=True,
        connection_timeout=5
    )

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, username, email, status
            FROM members
            WHERE user_id = %s
            """,
            (user_id,)
        )

        db_data = cursor.fetchone()

        assert db_data is not None
        assert db_data["user_id"] == response_data["user_id"]
        assert db_data["username"] == response_data["username"]
        assert db_data["email"] == response_data["email"]
        assert db_data["status"] == response_data["status"]

    finally:
        try:
            if cursor is not None:
                cursor.close()

            # 이번 테스트에서 생성한 회원만 삭제
            with connection.cursor() as cleanup_cursor:
                cleanup_cursor.execute(
                    "DELETE FROM members WHERE user_id = %s",
                    (user_id,)
                )

            connection.commit()

        finally:
            connection.close()


import pytest
import requests

# TC-API-003~006: 회원가입 필수값 누락 차단

@pytest.mark.parametrize(
    "missing_field, payload",
    [
        (
            "username",
            {
                "email": "camilo03@email.com",
                "password": "test01!",
                "status": "ACTIVE"
            }
        ),
        (
            "email",
            {
                "username": "piolo333",
                "password": "test100",
                "status": "ACTIVE"
            }
        ),
        (
            "password",
            {
                "username": "hisui",
                "email": "potatochips01@gmail.com",
                "status": "inactive"
            }
        ),
        (
            "status",
            {
                "username": "tsubaem100",
                "email": "sudenlyninja@email.com",
                "password": "amgisiro"
            }
        )
    ]
)

def test_create_member_with_missing_required_field(missing_field, payload):
    response = requests.post(
        f"{BASE_URL}/members",
        json=payload
    )

    assert response.status_code == 400, (
        f"{missing_field} 누락 시 상태 코드 오류: "
        f"실제 응답 {response.status_code}, "
        f"응답 내용 {response.text}"
    )

    assert response.json()["message"] == (
        "Required fields are missing."
    ), (
        f"{missing_field} 누락 시 오류 메시지 불일치: "
        f"{response.text}"
    )

# TC-API-007~008: 중복 username/email 가입 차단

@pytest.mark.parametrize(
    "duplicate_field, payload",
    [
        (
            "username",
            {
                "username": "test01",
                "email": "invalid@gmail.com",
                "password": "Test1234!",
                "status": "ACTIVE"
            }
        ),
        (
            "email",
            {
                "username": "justanewname",
                "email": "test02@example.com",
                "password": "Test1234!",
                "status": "ACTIVE"
            }
        )
    ],
    ids=["duplicate_username", "duplicate_email"]
)
def test_create_member_with_duplicate_data(duplicate_field, payload):
    response = requests.post(
        f"{BASE_URL}/members",
        json=payload
    )

    assert response.status_code == 500, (
        f"{duplicate_field} 중복 시 상태 코드 오류: "
        f"실제 응답 {response.status_code}, "
        f"응답 내용 {response.text}"
    )

# TC-API-009: 비밀번호 저장 시 해시 처리 확인

def test_password_is_hashed():
    username = "pwbcrypttest"
    email = "mail4bcrytest@gmail.com"
    password = "password@bcrypttest"

    payload = {
        "username": username,
        "email": email,
        "password": password,
        "status": "ACTIVE"
    }

    response = requests.post(
        f"{BASE_URL}/members",
        json=payload
    )

    assert response.status_code == 201, (
        f"회원가입 실패: {response.status_code}, {response.text}"
    )

    user_id = response.json()["user_id"]

    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="member_db",
        use_pure=True,
        connection_timeout=5
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM members WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()

        assert row is not None, "가입한 회원이 DB에 존재하지 않습니다."

        stored_password = row[0]

        # DB에 평문 비밀번호가 저장되지 않았는지 확인
        assert stored_password != password, (
            "비밀번호가 평문으로 저장되었습니다."
        )

        # 저장된 해시가 원래 비밀번호와 일치하는지 확인
        assert bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password.encode("utf-8")
        ), "저장된 비밀번호 해시가 원문 비밀번호와 일치하지 않습니다."

    finally:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM members WHERE user_id = %s",
                    (user_id,)
                )
            connection.commit()
        finally:
            connection.close()


# TC-API-010: 허용되지 않은 status 차단

def test_create_member_with_invalid_status():
    unique_id = uuid.uuid4().hex[:8]

    username = f"invalid_status_{unique_id}"
    email = f"invalid_status_{unique_id}@example.com"

    payload = {
        "username": username,
        "email": email,
        "password": "Test1234!",
        "status": "INVALID_STATUS"
    }

    connection = None

    try:
        response = requests.post(
            f"{BASE_URL}/members",
            json=payload
        )

        # 잘못된 status 요청은 거부되어야 함
        assert response.status_code == 400, (
            f"잘못된 status 요청이 거부되지 않았습니다. "
            f"실제 상태 코드: {response.status_code}, "
            f"응답: {response.text}"
        )

        # DB에 회원 데이터가 생성되지 않았는지 확인
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database="member_db",
            use_pure=True,
            connection_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM members WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()

        assert row is None, (
            "잘못된 status 요청으로 회원 데이터가 DB에 생성되었습니다."
        )

    finally:
        # 테스트 데이터가 생성되었더라도 정리
        if connection is None:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                port=3306,
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database="member_db",
                use_pure=True,
                connection_timeout=5
            )

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM members WHERE username = %s",
                    (username,)
                )
            connection.commit()
        finally:
            connection.close()
