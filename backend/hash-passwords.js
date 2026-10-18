
require("dotenv").config();

const bcrypt = require("bcrypt");
const mysql = require("mysql2/promise");

async function hashPasswords() {
    const db = await mysql.createConnection({
        host: "127.0.0.1",
        port: 3306,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: "member_db"
    });

    try {
        // 실제 연결된 데이터베이스 확인
        const [dbInfo] = await db.query(
            "SELECT DATABASE() AS db, @@hostname AS host, @@port AS port"
        );

        console.log("스크립트 DB 연결 정보:", dbInfo[0]);

        // TC-API-031 계정 존재 여부 확인
        const [targetMembers] = await db.query(
            `SELECT user_id, username,
                    LEFT(password, 4) AS password_prefix,
                    CHAR_LENGTH(password) AS stored_length
             FROM members
             WHERE username = ?`,
            ["tc_api_031"]
        );

        console.log("TC-API-031 계정 확인:", targetMembers);

        // username을 포함해 회원 정보 조회
        const [members] = await db.query(
            "SELECT user_id, username, password FROM members ORDER BY user_id"
        );

        console.log(`조회된 회원 수: ${members.length}`);

        // 평문 비밀번호만 해시 처리
        let convertedCount = 0;
        let skippedCount = 0;

        for (const member of members) {
            if (typeof member.password !== "string") {
                console.log(
                    `처리 제외: user_id=${member.user_id}, ` +
                    `username=${member.username}, 비밀번호 값이 문자열이 아닙니다.`
                );
                skippedCount++;
                continue;
            }

            // 이미 bcrypt 해시인 비밀번호는 건너뜀
            if (/^\$2[aby]\$/.test(member.password)) {
                skippedCount++;
                continue;
            }

            const hashedPassword = await bcrypt.hash(
                member.password,
                10
            );

            await db.query(
                "UPDATE members SET password = ? WHERE user_id = ?",
                [hashedPassword, member.user_id]
            );

            convertedCount++;

            console.log(
                `해시 완료: user_id=${member.user_id}, ` +
                `username=${member.username}`
            );
        }

        console.log("비밀번호 해시 처리 완료");
        console.log(`변환한 회원 수: ${convertedCount}`);
        console.log(`건너뛴 회원 수: ${skippedCount}`);

        // TC-API-031 계정의 최종 저장 상태 확인
        const [finalCheck] = await db.query(
            `SELECT user_id, username,
                    LEFT(password, 4) AS password_prefix,
                    CHAR_LENGTH(password) AS stored_length
             FROM members
             WHERE username = ?`,
            ["tc_api_031"]
        );

        console.log("TC-API-031 최종 확인:", finalCheck);
    } finally {
        await db.end();
    }
}

hashPasswords().catch((error) => {
    console.error("비밀번호 해시 처리 중 오류 발생:", error);
    process.exitCode = 1;
});
