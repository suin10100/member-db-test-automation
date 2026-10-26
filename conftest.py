# DB 연결과 커서 사용 및 정리

import pytest

from test.connection import get_connection

# 테스트 공통 기능 사용
@pytest.fixture
# 공통 DB 연결 함수
def db_cursor():
    connection = get_connection()
    cursor = None

    try:
        connection.start_transaction()
        cursor = connection.cursor()

        yield connection, cursor # 연결과 커서 제공

    finally:
        try:
            connection.rollback() # 테스트 데이터 롤백
        finally:
            try:
                if cursor is not None:
                    cursor.close() # 커서 정리
            finally:
                connection.close() # 연결 정리
