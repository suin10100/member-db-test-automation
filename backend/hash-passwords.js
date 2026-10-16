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

    const [members] = await db.query(
        "SELECT user_id, password FROM members"
    );

    for (const member of members) {
        if (member.password.startsWith("$2")) {
            continue;
        }

        const hashedPassword = await bcrypt.hash(member.password, 10);

        await db.query(
            "UPDATE members SET password = ? WHERE user_id = ?",
            [hashedPassword, member.user_id]
        );
    }

    console.log(`Converted the passwords of ${members.length} members to hashes.`);

    await db.end();
}

hashPasswords();