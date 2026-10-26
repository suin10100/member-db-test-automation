
import uuid

import mysql.connector
import pytest

from test.connection import get_connection


# TC-DB-001: username 저장 (중복 차단)

import uuid

import mysql.connector
import pytest

from test.connection import get_connection


# TC-DB-001: username 저장 (중복 차단)
def testdb_001_duplicate_username_rejected(db_cursor):
    connection, cursor = db_cursor

    # 다른 테스트 데이터와 충돌하지 않도록 고유한 값 생성
    unique_id = uuid.uuid4().hex[:12]
    username = f"qa_{unique_id}"
    email = f"{unique_id}@example.com"

    # 테스트 회원 등록
    cursor.execute(
        """
        INSERT INTO members (username, email, password, status, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        """,
        (username, email, "Test1234!", "ACTIVE"),
    )

    # 같은 username으로 등록 시도
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


# TC-DB-002: email 저장 (중복 차단)
def test_db_002_duplicate_email_rejected(db_cursor):
    connection, cursor = db_cursor
    unique_id = uuid.uuid4().hex[:12]

    # 테스트 회원 등록
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

    # 같은 email로 등록 시도
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


# TC-DB-003~006: 필수 컬럼 NULL 차단
@pytest.mark.parametrize( # 반복 실행 담당
    "null_column",
    ["username", "email", "password", "status"],
)
def test_db_003_to_006_required_colums_reject_null(db_cursor, null_column):
    connection, cursor = db_cursor

    # 테스트 데이터 생성
    unique_id = uuid.uuid4().hex[:12]

    values = {
        "username": f"qa_{unique_id}",
        "email": f"{unique_id}@example.com",
        "password": "Test1234!",
        "status": "ACTIVE",
    }

    # NULL 값을 입력 받을 요소
    values[null_column] = None
    assert values[null_column] is None
    
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


# TC-DB-007: 데이터 입력 시간 저장 (NULL 차단)
def test_db_007_created_at_null_rejected(db_cursor):
    connection, cursor = db_cursor
    unique_id = uuid.uuid4().hex[:12]

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

# TC-DB-008: status 저장 (정상, 허용값 검증)
@pytest.mark.parametrize(
    "status",
    ["ACTIVE", "INACTIVE", "SUSPENDED"],
)
def test_db_008_allowed_status_values_saved(db_cursor, status):
    connection, cursor = db_cursor

    # 테스트 데이터 생성
    unique_id = uuid.uuid4().hex[:12]
    username = f"qa_status_{unique_id}"
    email = f"{unique_id}@example.com"

    # 테스트 데이터 입력
    cursor.execute(
        """
        INSERT INTO members (username, email, password, status, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        """,
        (username, email, "Test1234!", status),
    )

    # SQL 실행
    cursor.execute(
        "SELECT status FROM members WHERE username = %s",
        (username,),
    )
    result = cursor.fetchone() # 결과값 한 행 가져오기

    assert result is not None # 결과 존재 확인
    assert result[0] == status # status와 일치하는 지 확인



# TC-DB-009: status 저장 (허용되지 않은 값 처리 확인)
def test_db_009_invalid_status_rejected(db_cursor):
    connection, cursor = db_cursor
    unique_id = uuid.uuid4().hex[:12]

    with pytest.raises(mysql.connector.DatabaseError) as exc_info: # 예외 정보 저장
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

    assert exc_info.value.errno == 3819 # DB 발생 오류 번호 검증 


# TC-DB-010: username 저장 (정상 길이 검증)
def test_db_011_username_max_length_saved(db_cursor):
    connection, cursor = db_cursor

    # 테스트 데이터 생성 
    unique_id = uuid.uuid4().hex[:12]
    username = "a" * 30 # 아이디 30자
    email = f"{unique_id}@example.com"

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

    assert result is not None # 30자 입력값 존재 확인
    assert result[0] == username # 테스트 데이터와 DB 입력값 저장 확인
    assert len(result[0]) == 30  # 30자 확인


# TC-DB-011: username 저장 (최대 길이 초과 검증)
def test_db_011_username_exceeds_max_length_rejected(db_cursor):
    connection, cursor = db_cursor

    # 테스트 데이터 생성
    unique_id = uuid.uuid4().hex[:12]

    with pytest.raises(mysql.connector.DataError):
        cursor.execute(
            """
            INSERT INTO members (username, email, password, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (
                "a" * 31, # 31자 아이디 생성 
                f"{unique_id}@example.com",
                "Test1234!",
                "ACTIVE",
            ),
        )



# TC-DB-012: user_profiles 저장 (존재하지 않는 회원 참조 차단)
def test_db_012_profile_rejects_nonexistent_member(db_cursor):
    connection, cursor = db_cursor

    with pytest.raises(mysql.connector.IntegrityError):
        cursor.execute(
            """
            INSERT INTO user_profiles (user_id, phone, birth_date)
            VALUES (%s, %s, %s)
            """,
            (100, "010-9999-9999", "2000-01-01"), # 존재하지 않는 프로필 저장 시도
        )


# TC-DB-013: login_history 저장 (존재하지 않는 회원 참조 차단)
def test_db_013_login_history_rejects_nonexistent_member(db_cursor):
    connection, cursor = db_cursor

    with pytest.raises(mysql.connector.IntegrityError):
        cursor.execute(
            """
            INSERT INTO login_history
                (user_id, login_at, login_result)
            VALUES (%s, NOW(), %s)
            """,
            (100, "FAIL"),
        )

