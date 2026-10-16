import os
import mysql.connector


def get_connection():
    print("① DB 연결 시작", flush=True)

    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="member_db",
        use_pure=True,
        connection_timeout=5
    )

    print("② DB 연결 성공", flush=True)

    return connection


def test_member_count():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM members")
    result = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    assert result >= 0