
import uuid

import mysql.connector
import pytest

from database.connection import get_connection


# TC-DB-001: username 저장 (중복 차단)
def testdb_001_duplicate_username_rejected():
    connection = get_connection()
    cursor = connection.cursor()

    # 다른 테스트 데이터와 충돌하지 않도록 고유한 값 생성
    unique_id = uuid.uuid4().hex[:12]
    username = f"qa_{unique_id}"
    email = f"{unique_id}@example.com"

    try:
        connection.start_transaction()

        # 첫 번째 회원 등록
        cursor.execute(
            """
            INSERT INTO members (username, email, password, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (username, email, "Test1234!", "ACTIVE"),
        )

        # 같은 username으로 두 번째 회원 등록 시도
        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                """
                INSERT INTO members (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (
                    username,
                    f"other_{unique_id}@example.com",
                    "Test5678!",
                    "ACTIVE",
                ),
            )
    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-002: email 저장 (중복 차단)
def test_db_002_duplicate_email_rejected():
    connection = get_connection()
    cursor = connection.cursor()
    unique_id = uuid.uuid4().hex[:12]

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO members (username, email, password, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (
                f"qa_first{unique_id}",
                f"{unique_id}@example.com",
                "Test1234!",
                "ACTIVE",
            ),
        )

        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                """
                INSERT INTO members (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (
                    f"qa_second_{unique_id}",
                    f"{unique_id}@example.com",
                    "Test5678!",
                    "ACTIVE",
                ),
            )

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-003~006: 필수 컬럼 NULL 차단
@pytest.mark.parametrize(
    "null_column",
    ["username", "email", "password", "status"],
)
def test_db_003_to_006_required_colums_reject_null(null_column):
    connection = get_connection()
    cursor = connection.cursor()
    unique_id = uuid.uuid4().hex[:12]

    values = {
        "username": f"qa_{unique_id}",
        "email": f"{unique_id}@example.com",
        "password": "Test1234!",
        "status": "ACTIVE",
    }
    values[null_column] = None

    try:
        connection.start_transaction()

        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                """
                INSERT INTO members (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (
                    values["username"],
                    values["email"],
                    values["password"],
                    values["status"],
                ),
            )

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-007: 데이터 입력 시간 저장 (NULL 차단)
def test_db_007_created_at_null_rejected():
    connection = get_connection()
    cursor = connection.cursor()
    unique_id = uuid.uuid4().hex[:12]

    try:
        connection.start_transaction()

        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                """
                INSERT INTO members (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    f"qa_{unique_id}",
                    f"{unique_id}@example.com",
                    "Test1234!",
                    "ACTIVE",
                    None,
                ),
            )

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-008: status 저장 (정상, 허용값 검증)
@pytest.mark.parametrize(
    "status",
    ["ACTIVE", "INACTIVE", "SUSPENDED"],
)
def test_db_008_allowed_status_values_saved(status):
    connection = get_connection()
    cursor = connection.cursor()

    unique_id = uuid.uuid4().hex[:12]
    username = f"qa_status_{unique_id}"
    email = f"{unique_id}@example.com"

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO members (username, email, password, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (username, email, "Test1234!", status),
        )

        cursor.execute(
            "SELECT status FROM members WHERE username = %s",
            (username,),
        )
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == status

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-009: status 저장 (허용되지 않은 값 처리 확인)
def test_db_009_invalid_status_rejected():
    connection = get_connection()
    cursor = connection.cursor()
    unique_id = uuid.uuid4().hex[:12]

    try:
        connection.start_transaction()

        with pytest.raises(mysql.connector.DatabaseError) as exc_info:
            cursor.execute(
                """
                INSERT INTO members
                    (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (
                    f"qa_invalid_{unique_id}",
                    f"{unique_id}@example.com",
                    "Test1234!",
                    "INVALID_STATUS",
                ),
            )

        assert exc_info.value.errno == 3819

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-010: username 저장 (최대 길이 초과 검증)
def test_db_010_username_exceeds_max_length_rejected():
    connection = get_connection()
    cursor = connection.cursor()
    unique_id = uuid.uuid4().hex[:12]

    try:
        connection.start_transaction()

        with pytest.raises(mysql.connector.DataError):
            cursor.execute(
                """
                INSERT INTO members (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (
                    "a" * 31,
                    f"{unique_id}@example.com",
                    "Test1234!",
                    "ACTIVE",
                ),
            )

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-011: username 저장 (최대 길이 검증)
def test_db_011_username_max_length_saved():
    connection = get_connection()
    cursor = connection.cursor()
    unique_id = uuid.uuid4().hex[:12]
    username = "a" * 30
    email = f"{unique_id}@example.com"

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO members
                (username, email, password, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (username, email, "Test1234!", "ACTIVE"),
        )

        cursor.execute(
            "SELECT username FROM members WHERE username = %s",
            (username,),
        )
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == username
        assert len(result[0]) == 30

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-012: user_profiles 저장 (존재하지 않는 회원 참조 차단)
def test_db_012_profile_rejects_nonexistent_member():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                """
                INSERT INTO user_profiles (user_id, phone, birth_date)
                VALUES (%s, %s, %s)
                """,
                (100, "010-9999-9999", "2000-01-01"),
            )

    finally:
        connection.rollback()
        cursor.close()
        connection.close()


# TC-DB-013: login_history 저장 (존재하지 않는 회원 참조 차단)
def test_db_013_login_history_rejects_nonexistent_member():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        connection.start_transaction()

        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                """
                INSERT INTO login_history
                    (user_id, login_at, login_result)
                VALUES (%s, NOW(), %s)
                """,
                (100, "FAIL"),
            )

    finally:
        connection.rollback()
        cursor.close()
        connection.close()
