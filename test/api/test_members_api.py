
import uuid
import requests
import bcrypt
import pytest

from database.connection import get_connection


BASE_URL = "http://localhost:3000"


# TC-API-001: 회원가입 성공
def test_api_001_create_member_success():
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
        connection = get_connection()

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
def test_api_002_create_member_db_persistence():
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

    connection = get_connection()
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
    ],
    ids=[
        "TC-API-003_missing_username",
        "TC-API-004_missing_email",
        "TC-API-005_missing_password",
        "TC-API-006_missing_status",
    ]
)
def test_api_003_006_create_member_rejects_missing_required_fields(
    missing_field, payload
):
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
    ids=[
        "TC-API-007_duplicate_username",
        "TC-API-008_duplicate_email",
    ]
)
def test_api_007_008_create_member_rejects_duplicate_data(
    duplicate_field, payload
):
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
def test_api_009_password_is_hashed_in_database():
    unique_id = uuid.uuid4().hex[:8]
    username = f"pwbcrypttest_{unique_id}"
    email = f"mail4bcrytest_{unique_id}@example.com"
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
    connection = get_connection()

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
def test_api_010_create_member_rejects_invalid_status():
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
        connection = get_connection()

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
            connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM members WHERE username = %s",
                    (username,)
                )
            connection.commit()
        finally:
            connection.close()


# TC-API-011~017: 로그인 API 테스트
@pytest.mark.parametrize(
    "payload, expected_status, expected_message, expected_user_status",
    [
        # TC-API-011: 정상 로그인
        (
            {"username": "test01", "password": "Test1234!"},
            200,
            "Login successful.",
            "ACTIVE",
        ),

        # TC-API-012: 잘못된 비밀번호
        (
            {"username": "test01", "password": "wrong!pw"},
            401,
            "Username or password is incorrect.",
            None,
        ),

        # TC-API-013: 존재하지 않는 username
        (
            {"username": "davevives", "password": "lwc2019!"},
            401,
            "Username or password is incorrect.",
            None,
        ),

        # TC-API-014: INACTIVE 계정
        (
            {"username": "inactive_test", "password": "Test1234!"},
            403,
            "This account cannot log in.",
            None,
        ),

        # TC-API-015: SUSPENDED 계정
        (
            {"username": "suspended_test", "password": "Test1234!"},
            403,
            "This account cannot log in.",
            None,
        ),

        # TC-API-016: username 누락
        (
            {"password": "Test1234!"},
            400,
            "Username and password are required.",
            None,
        ),

        # TC-API-017: password 누락
        (
            {"username": "test01"},
            400,
            "Username and password are required.",
            None,
        ),
    ],
    ids=[
        "TC-API-011_login_success",
        "TC-API-012_wrong_password",
        "TC-API-013_unknown_username",
        "TC-API-014_inactive_account",
        "TC-API-015_suspended_account",
        "TC-API-016_missing_username",
        "TC-API-017_missing_password",
    ],
)
def test_api_011_017_login_api(
    payload,
    expected_status,
    expected_message,
    expected_user_status,
):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=payload,
    )

    # HTTP 상태 코드 검증
    assert response.status_code == expected_status, (
        f"기대 상태 코드: {expected_status}, "
        f"실제 상태 코드: {response.status_code}, "
        f"응답: {response.text}"
    )

    data = response.json()

    # 응답 메시지 검증
    assert data["message"] == expected_message

    # 정상 로그인 시 반환되는 회원 정보 검증
    if expected_status == 200:
        assert "user" in data

        user = data["user"]

        assert isinstance(user["user_id"], int)
        assert user["username"] == payload["username"]
        assert isinstance(user["email"], str)
        assert user["status"] == expected_user_status



# TC-API-018: 존재하지 않는 회원 조회
def test_api_018_get_nonexistent_member():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(user_id), 0) + 1 FROM members"
            )
            nonexistent_id = cursor.fetchone()[0]
    finally:
        connection.close()

    response = requests.get(
        f"{BASE_URL}/members/{nonexistent_id}"
    )

    assert response.status_code == 404, (
        f"기대 상태 코드: 404, "
        f"실제 상태 코드: {response.status_code}, "
        f"응답: {response.text}"
    )

    assert response.json()["message"] == "Member not found."


# TC-API-019: 존재하지 않는 회원 수정
def test_api_019_update_nonexistent_member():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(user_id), 0) + 1 FROM members"
            )
            nonexistent_id = cursor.fetchone()[0]
    finally:
        connection.close()

    payload = {
        "username": "tc019_user",
        "email": "tc019@example.com",
        "password": "TestPassword123!",
        "status": "ACTIVE"
    }

    response = requests.put(
        f"{BASE_URL}/members/{nonexistent_id}",
        json=payload
    )

    assert response.status_code == 404, (
        f"기대 상태 코드: 404, "
        f"실제 상태 코드: {response.status_code}, "
        f"응답: {response.text}"
    )

    assert response.json()["message"] == "Member not found."


# TC-API-020: 존재하지 않는 회원 삭제
def test_api_020_delete_nonexistent_member():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(user_id), 0) + 1 FROM members"
            )
            nonexistent_id = cursor.fetchone()[0]
    finally:
        connection.close()

    response = requests.delete(
        f"{BASE_URL}/members/{nonexistent_id}"
    )

    assert response.status_code == 404, (
        f"기대 상태 코드: 404, "
        f"실제 상태 코드: {response.status_code}, "
        f"응답: {response.text}"
    )

    assert response.json()["message"] == "Member not found."



# TC-API-021: 회원 수정 성공
def test_api_021_update_member_success():
    unique_id = uuid.uuid4().hex[:10]
    original_username = f"tc021_{unique_id}"
    original_email = f"tc021_{unique_id}@example.com"
    updated_username = f"updated_{unique_id}"
    updated_email = f"updated_{unique_id}@example.com"

    member_id = None

    try:
        # 테스트용 회원 생성
        create_response = requests.post(
            f"{BASE_URL}/members",
            json={
                "username": original_username,
                "email": original_email,
                "password": "OriginalPassword123!",
                "status": "ACTIVE"
            }
        )

        assert create_response.status_code == 201, (
            f"회원 생성 실패: {create_response.status_code}, "
            f"{create_response.text}"
        )

        member_id = create_response.json()["user_id"]

        # 회원 정보 수정
        update_response = requests.put(
            f"{BASE_URL}/members/{member_id}",
            json={
                "username": updated_username,
                "email": updated_email,
                "password": "UpdatedPassword123!",
                "status": "INACTIVE"
            }
        )

        assert update_response.status_code == 200, (
            f"회원 수정 실패: {update_response.status_code}, "
            f"{update_response.text}"
        )

        result = update_response.json()

        assert result["user_id"] == member_id
        assert result["username"] == updated_username
        assert result["email"] == updated_email
        assert result["status"] == "INACTIVE"

        # DB에도 수정 내용이 반영되었는지 확인
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT username, email, status
                    FROM members
                    WHERE user_id = %s
                    """,
                    (member_id,)
                )
                db_member = cursor.fetchone()
        finally:
            connection.close()

        assert db_member is not None
        assert db_member["username"] == updated_username
        assert db_member["email"] == updated_email
        assert db_member["status"] == "INACTIVE"

    finally:
        if member_id is not None:
            requests.delete(f"{BASE_URL}/members/{member_id}")


# TC-API-022: 회원 수정 시 비밀번호 암호화 검증
def test_api_022_update_password_is_hashed():
    unique_id = uuid.uuid4().hex[:10]
    username = f"tc022_{unique_id}"
    email = f"tc022_{unique_id}@example.com"
    new_password = "NewPassword456!"

    member_id = None

    try:
        # 테스트용 회원 생성
        create_response = requests.post(
            f"{BASE_URL}/members",
            json={
                "username": username,
                "email": email,
                "password": "OriginalPassword123!",
                "status": "ACTIVE"
            }
        )

        assert create_response.status_code == 201, (
            f"회원 생성 실패: {create_response.status_code}, "
            f"{create_response.text}"
        )

        member_id = create_response.json()["user_id"]

        # 비밀번호 수정
        update_response = requests.put(
            f"{BASE_URL}/members/{member_id}",
            json={
                "username": username,
                "email": email,
                "password": new_password,
                "status": "ACTIVE"
            }
        )

        assert update_response.status_code == 200, (
            f"회원 수정 실패: {update_response.status_code}, "
            f"{update_response.text}"
        )

        # DB에 저장된 비밀번호 확인
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT password FROM members WHERE user_id = %s",
                    (member_id,)
                )
                row = cursor.fetchone()
        finally:
            connection.close()

        assert row is not None, "수정한 회원이 DB에 없습니다."

        stored_password = row[0]

        # 평문 비밀번호가 그대로 저장되지 않았는지 확인
        assert stored_password != new_password

        # 저장된 해시가 새 비밀번호와 일치하는지 확인
        assert bcrypt.checkpw(
            new_password.encode("utf-8"),
            stored_password.encode("utf-8")
        ), "DB에 저장된 비밀번호 해시가 수정한 비밀번호와 일치하지 않습니다."

    finally:
        if member_id is not None:
            requests.delete(f"{BASE_URL}/members/{member_id}")


# TC-API-023: 회원 삭제 성공
def test_api_023_delete_member_success():
    unique_id = uuid.uuid4().hex[:10]
    username = f"tc023_{unique_id}"
    email = f"tc023_{unique_id}@example.com"

    member_id = None

    try:
        # 테스트용 회원 생성
        create_response = requests.post(
            f"{BASE_URL}/members",
            json={
                "username": username,
                "email": email,
                "password": "TestPassword123!",
                "status": "ACTIVE"
            }
        )

        assert create_response.status_code == 201, (
            f"회원 생성 실패: {create_response.status_code}, "
            f"{create_response.text}"
        )

        member_id = create_response.json()["user_id"]

        # 회원 삭제
        delete_response = requests.delete(
            f"{BASE_URL}/members/{member_id}"
        )

        assert delete_response.status_code == 200, (
            f"회원 삭제 실패: {delete_response.status_code}, "
            f"{delete_response.text}"
        )

        result = delete_response.json()

        assert result["user_id"] == member_id
        assert result["message"] == "Member deleted successfully."

        # DB에서 실제로 삭제되었는지 확인
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM members WHERE user_id = %s",
                    (member_id,)
                )
                count = cursor.fetchone()[0]
        finally:
            connection.close()

        assert count == 0, "삭제한 회원이 DB에 남아 있습니다."

        # 삭제 완료 확인 후 정리 대상에서 제외
        member_id = None

    finally:
        if member_id is not None:
            requests.delete(f"{BASE_URL}/members/{member_id}")


# TC-API-024: 회원 삭제 시 관련 데이터 처리 확인
def test_api_024_delete_member_related_records():
    unique_id = uuid.uuid4().hex[:10]
    username = f"tc024_{unique_id}"
    email = f"tc024_{unique_id}@example.com"

    member_id = None

    try:
        # 테스트용 회원 생성
        create_response = requests.post(
            f"{BASE_URL}/members",
            json={
                "username": username,
                "email": email,
                "password": "TestPassword123!",
                "status": "ACTIVE"
            }
        )

        assert create_response.status_code == 201, (
            f"회원 생성 실패: {create_response.status_code}, "
            f"{create_response.text}"
        )

        member_id = create_response.json()["user_id"]

        # 삭제 전 관련 테이블의 데이터 확인
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM user_profiles
                    WHERE user_id = %s
                    """,
                    (member_id,)
                )
                profile_count = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM login_history
                    WHERE user_id = %s
                    """,
                    (member_id,)
                )
                history_count = cursor.fetchone()[0]
        finally:
            connection.close()

        # 삭제 API 호출
        delete_response = requests.delete(
            f"{BASE_URL}/members/{member_id}"
        )

        # 현재 외래 키 제약조건에 따라 삭제 성공 여부가 달라질 수 있음
        if delete_response.status_code == 200:
            connection = get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM members
                        WHERE user_id = %s
                        """,
                        (member_id,)
                    )
                    member_count = cursor.fetchone()[0]

                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM user_profiles
                        WHERE user_id = %s
                        """,
                        (member_id,)
                    )
                    remaining_profiles = cursor.fetchone()[0]

                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM login_history
                        WHERE user_id = %s
                        """,
                        (member_id,)
                    )
                    remaining_history = cursor.fetchone()[0]
            finally:
                connection.close()

            assert member_count == 0, "회원 레코드가 삭제되지 않았습니다."

            # 관련 데이터가 삭제 전 존재했다면 삭제 후에도 남는지 확인
            if profile_count > 0:
                assert remaining_profiles == 0, (
                    "회원 삭제 후 user_profiles 데이터가 남아 있습니다."
                )

            if history_count > 0:
                assert remaining_history == 0, (
                    "회원 삭제 후 login_history 데이터가 남아 있습니다."
                )

            member_id = None

        else:
            # 현재 API는 삭제 실패 시 500을 반환할 수 있음
            assert delete_response.status_code == 500, (
                f"예상하지 못한 응답: {delete_response.status_code}, "
                f"{delete_response.text}"
            )

            # 관련 데이터가 외래 키로 삭제를 막았는지 확인할 수 있도록
            # 실패 응답을 테스트 결과에 남김
            pytest.fail(
                "회원 삭제가 실패했습니다. user_profiles 또는 "
                "login_history의 외래 키 제약조건을 확인하세요. "
                f"응답: {delete_response.text}"
            )

    finally:
        if member_id is not None:
            # 실패 시 회원을 강제로 삭제하지 않음.
            # 외래 키와 관련 데이터 상태를 보존해 원인을 조사합니다.
            pass


# TC-API-025: 특정 회원 조회 성공
def test_api_025_get_member_success():
    unique_id = uuid.uuid4().hex[:10]
    username = f"tc025_{unique_id}"
    email = f"tc025_{unique_id}@example.com"
    member_id = None

    try:
        # 테스트용 회원 생성
        create_response = requests.post(
            f"{BASE_URL}/members",
            json={
                "username": username,
                "email": email,
                "password": "TestPassword123!",
                "status": "ACTIVE"
            }
        )

        assert create_response.status_code == 201, (
            f"회원 생성 실패: {create_response.status_code}, "
            f"{create_response.text}"
        )
        member_id = create_response.json()["user_id"]

        # 특정 회원 조회
        response = requests.get(
            f"{BASE_URL}/members/{member_id}"
        )

        assert response.status_code == 200, (
            f"회원 조회 실패: {response.status_code}, {response.text}"
        )

        result = response.json()

        assert result["user_id"] == member_id
        assert result["username"] == username
        assert result["email"] == email
        assert result["status"] == "ACTIVE"

        # 응답에 비밀번호 원문이나 해시가 노출되지 않는지 확인
        assert "password" not in result

    finally:
        if member_id is not None:
            requests.delete(f"{BASE_URL}/members/{member_id}")


# TC-API-026: 전체 회원 목록 조회
def test_api_026_get_all_members():
    unique_id = uuid.uuid4().hex[:10]
    username = f"tc026_{unique_id}"
    email = f"tc026_{unique_id}@example.com"
    member_id = None

    try:
        # 조회 대상 회원 생성
        create_response = requests.post(
            f"{BASE_URL}/members",
            json={
                "username": username,
                "email": email,
                "password": "TestPassword123!",
                "status": "ACTIVE"
            }
        )

        assert create_response.status_code == 201, (
            f"회원 생성 실패: {create_response.status_code}, "
            f"{create_response.text}"
        )
        member_id = create_response.json()["user_id"]

        # 전체 회원 목록 조회
        response = requests.get(f"{BASE_URL}/members")

        assert response.status_code == 200, (
            f"회원 목록 조회 실패: {response.status_code}, "
            f"{response.text}"
        )

        result = response.json()

        assert isinstance(result, list), "응답이 회원 목록 배열이 아닙니다."

        # 방금 생성한 회원이 목록에 포함되는지 확인
        matching_members = [
            member for member in result
            if member.get("user_id") == member_id
        ]

        assert len(matching_members) == 1, (
            "생성한 회원이 목록에 없거나 중복으로 반환되었습니다."
        )

        member = matching_members[0]

        assert member["username"] == username
        assert member["email"] == email
        assert member["status"] == "ACTIVE"

        # 회원 목록에 비밀번호 정보가 노출되지 않는지 확인
        for item in result:
            assert "password" not in item

    finally:
        if member_id is not None:
            requests.delete(f"{BASE_URL}/members/{member_id}")

# TC-API-027: 서버 상태 확인

def test_api_027_server_status():
    response = requests.get(BASE_URL, timeout=5)

    assert response.status_code == 200, (
        f"서버 상태 확인 실패: {response.status_code}, "
        f"{response.text}"
    )

    result = response.json()

    assert result["message"] == "Member API Server is running."



# TC-API-028~030: 로그인 API 아이디 길이 경계값 검증

@pytest.mark.parametrize(
    "tc_id, username, password, expected_status",
    [
        ("028", "abcdefghijklmnopqrstuvwxyz1234", "thritypw30!", 200),
        ("029", "abcdefghijklmnopqrstuvwxyz12345", "thritypw30!", 401),
        ("030", "a", "onecharpw", 200),
    ],
    ids=[
        "TC-API-028_max_length_30",
        "TC-API-029_over_max_length_31",
        "TC-API-030_min_length_1",
    ],
)
def test_api_username_length_boundary(
    tc_id, username, password, expected_status
):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=5,
    )

    assert response.status_code == expected_status, (
        f"TC-API-{tc_id} 실패: "
        f"기대 상태 코드={expected_status}, "
        f"실제 상태 코드={response.status_code}, "
        f"응답={response.text}"
    )


# TC-API-031~033: 로그인 API 비밀번호 길이 경계값 검증

TC031_PASSWORD = (
    "AbcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+=AbcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+=AbcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+="
)


@pytest.mark.parametrize(
    "tc_id, username, password, expected_status",
    [
        ("031", "tc_api_031", TC031_PASSWORD, 200),
        ("032", "tc_api_031", TC031_PASSWORD + "1", 401),
        ("033", "forshortpw", "!", 400),
    ],
    ids=[
        "TC-API-031_password_length_225",
        "TC-API-032_password_length_226",
        "TC-API-033_password_length_1",
    ],
)
def test_api_password_length_boundary(
    tc_id, username, password, expected_status
):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=5,
    )

    assert response.status_code == expected_status, (
        f"TC-API-{tc_id} 실패: "
        f"기대 상태 코드={expected_status}, "
        f"실제 상태 코드={response.status_code}, "
        f"응답={response.text}"
    )


# TC-API-038: 원본의 매우 긴 비밀번호
# 아래 문자열은 사용자가 제공한 입력값 그대로입니다.
TC038_PASSWORD = r"""Abcdef123!@#XyZ789$%^Pass456&*()Test789!@#QwEr123$%^Login456&*()AaBbCc123!@#DdEeFf456$%^GgHhIi789&*()JjKkLl012!@#MmNnOo345$%^PpQqRr678&*()SsTtUu901!@#VvWwXx234$%^YyZzAa567&*()BbCcDd890!@#EeFfGg123$%^HhIiJj456&*()KkLlMm789!@#NnOoPp012$%^QqRrSs345&*()TtUuVv678!@#WwXxYy901$%^ZzAaBb234&*()CcDdEe567!@#FfGgHh890$%^IiJjKk123&*()LlMmNn456!@#OoPpQq789$%^RrSsTt012&*()UuVvWw345!@#XxYyZz678$%^AaBbCc901&*()DdEeFf234!@#GgHhIi567$%^JjKkLl890&*()MmNnOo123!@#PpQqRr456$%^SsTtUu789&*()VvWwXx012!@#YyZzAa345$%^BbCcDd678&*()EeFfGg901!@#HhIiJj234$%^KkLlMm567&*()NnOoPp890!@#QqRrSs123$%^TtUuVv456&*()WwXxYy789!@#ZzAaBb012$%^CcDdEe345&*()FfGgHh678!@#IiJjKk901$%^LlMmNn234&*()OoPpQq567!@#RrSsTt890$%^UuVvWw123&*()XxYyZz456!@#AaBbCc789$%^DdEeFf012&*()GgHhIi345!@#JjKkLl678$%^MmNnOo901&*()PpQqRr234!@#SsTtUu567$%^VvWwXx890&*()YyZzAa123!@#BbCcDd456$%^EeFfGg789&*()HhIiJj012!@#KkLlMm345$%^NnOoPp678&*()QqRrSs901!@#TtUuVv234$%^WwXxYy567&*()ZzAaBb890!@#CcDdEe123$%^FfGgHh456&*()IiJjKk789!@#LlMmNn012$%^OoPpQq345&*()RrSsTt678!@#UuVvWw901$%^XxYyZz234&*()AaBbCc567!@#DdEeFf890$%^GgHhIi123&*()JjKkLl456!@#MmNnOo789$%^PpQqRr012&*()SsTtUu345!@#VvWwXx678$%^YyZzAa901&*()BbCcDd234!@#EeFfGg567$%^HhIiJj890&*()KkLlMm123!@#NnOoPp456$%^QqRrSs789&*()TtUuVv012!@#WwXxYy345$%^ZzAaBb678&*()CcDdEe901!@#FfGgHh234$%^IiJjKk567&*()LlMmNn890!@#OoPpQq123$%^RrSsTt456&*()UuVvWw789!@#XxYyZz012$%^AaBbCc345&*()DdEeFf678!@#GgHhIi901$%^JjKkLl234&*()MmNnOo567!@#PpQqRr890$%^SsTtUu123&*()VvWwXx456!@#YyZzAa789$%^BbCcDd012&*()EeFfGg345!@#HhIiJj678$%^KkLlMm901&*()NnOoPp234!@#QqRrSs567$%^TtUuVv890&*()WwXxYy123!@#ZzAaBb456$%^CcDdEe789&*()FfGgHh012!@#IiJjKk345$%^LlMmNn678&*()OoPpQq901!@#RrSsTt234$%^UuVvWw567&*()XxYyZz890!@#AaBbCc123$%^DdEeFf456&*()GgHhIi789!@#JjKkLl012$%^MmNnOo345&*()PpQqRr678!@#SsTtUu901$%^VvWwXx234&*()YyZzAa567!@#BbCcDd890$%^EeFfGg123&*()HhIiJj456!@#KkLlMm789$%^NnOoPp012&*()QqRrSs345!@#TtUuVv678$%^WwXxYy901&*()ZzAaBb234!@#CcDdEe567$%^FfGgHh890&*()IiJjKk123!@#LlMmNn456$%^OoPpQq789&*()RrSsTt012!@#UuVvWw345$%^XxYyZz678&*()AaBbCc901!@#DdEeFf234$%^GgHhIi567&*()JjKkLl890!@#MmNnOo123$%^PpQqRr456&*()SsTtUu789!@#VvWwXx012$%^YyZzAa345&*()BbCcDd678!@#EeFfGg901$%^HhIiJj234&*()KkLlMm567!@#NnOoPp890$%^QqRrSs123&*()TtUuVv456!@#WwXxYy789$%^ZzAaBb012&*()CcDdEe345!@#FfGgHh678$%^IiJjKk901&*()LlMmNn234!@#OoPpQq567$%^RrSsTt890&*()UuVvWw123!@#XxYyZz456$%^AaBbCc789&*()DdEeFf012!@#GgHhIi345$%^JjKkLl678&*()MmNnOo901!@#PpQqRr234$%^SsTtUu567&*()VvWwXx890!@#YyZzAa123$%^BbCcDd456&*()EeFfGg789!@#HhIiJj012$%^KkLlMm345&*()NnOoPp678!@#QqRrSs901$%^TtUuVv234&*()WwXxY"""


# TC-API-034~045: 로그인 입력값 검증

OMIT_PASSWORD = object()


@pytest.mark.parametrize(
    "tc_id, username, password, expected_status",
    [
        # TC-API-034~035: 앞뒤 공백
        ("034", " test01 ", "Test1234!\\", 401),
        ("035", "test01", " Test1234! ", 401),

        # TC-API-036~037: 특수문자 및 유니코드
        ("036", r"@#!\~!@1234", OMIT_PASSWORD, 400),
        ("037", "ㄱㅇ☺️", OMIT_PASSWORD, 400),

        # TC-API-039~040: 잘못된 자료형
        ("039", ["testuster"], "Test1234!", 401),
        ("040", "test01", ["testusterpw"], 401),

        # TC-API-041~045: null, 빈 문자열, 공백 문자열
        ("041", None, "Test1234!", 400),
        ("042", "test02", None, 400),
        ("043", "", "Test1234!", 400),
        ("044", "test01", "", 400),
        ("045", "   ", "   ", 401),
    ],
    ids=[
        "TC-API-034_username_surrounding_spaces",
        "TC-API-035_password_surrounding_spaces",
        "TC-API-036_special_characters",
        "TC-API-037_unicode",
        "TC-API-039_invalid_username_type",
        "TC-API-040_invalid_password_type",
        "TC-API-041_null_username",
        "TC-API-042_null_password",
        "TC-API-043_empty_username",
        "TC-API-044_empty_password",
        "TC-API-045_whitespace_only",
    ],
)
def test_api_login_input_validation(
    tc_id, username, password, expected_status
):
    payload = {"username": username}

    if password is not OMIT_PASSWORD:
        payload["password"] = password

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=payload,
        timeout=5,
    )

    assert response.status_code == expected_status, (
        f"TC-API-{tc_id} 실패: "
        f"기대 상태 코드={expected_status}, "
        f"실제 상태 코드={response.status_code}, "
        f"응답={response.text}"
    )


# TC-API-038: 매우 긴 비밀번호 입력 시 서버가 중단되지 않는지 확인
def test_api_038_very_long_password_does_not_crash_server():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "test01",
            "password": TC038_PASSWORD,
        },
        timeout=10,
    )

    # 이 TC의 핵심은 특정 인증 성공 여부가 아니라 서버 오류로
    # 중단되지 않고 요청에 응답하는지 확인하는 것입니다.
    assert response.status_code < 500, (
        "TC-API-038 실패: 서버가 5xx 오류를 반환했습니다. "
        f"상태 코드={response.status_code}, 응답={response.text}"
    )

    health_response = requests.get(
        f"{BASE_URL}/",
        timeout=5,
    )

    assert health_response.status_code < 500, (
        "TC-API-038 실패: 요청 후 서버가 정상 응답하지 않습니다. "
        f"상태 코드={health_response.status_code}, "
        f"응답={health_response.text}"
    )