
import bcrypt
from database.connection import get_connection


# 로그인 API 테스트용 유효 계정
TEST_ACCOUNTS = [
    {
        "username": "abcdefghijklmnopqrstuvwxyz1234",
        "email": "tc_api_028@example.com",
        "password": "thritypw30!",
    },
    {
        "username": "a",
        "email": "tc_api_030@example.com",
        "password": "onecharpw",
    },
    {
        "username": "test01",
        "email": "tc_api_test01@example.com",
        "password": "Test1234!",
    },
    {
        "username": "test02",
        "email": "tc_api_test02@example.com",
        "password": "Test1234!",
    },
    {
        "username": "forshortpw",
        "email": "tc_api_forshortpw@example.com",
        "password": "!",
    },
]


def seed_test_accounts():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for account in TEST_ACCOUNTS:
                password_hash = bcrypt.hashpw(
                    account["password"].encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                cursor.execute(
                """
                INSERT INTO members
                    (username, email, password, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE user_id = user_id
                """,
                (
                    account["username"],
                    account["email"],
                    password_hash,
                    "ACTIVE",
                ),
            )

        connection.commit()
        print("테스트 계정 저장이 완료되었습니다.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_test_accounts()
