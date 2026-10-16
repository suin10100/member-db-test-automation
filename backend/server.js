require("dotenv").config();

const express = require("express");
const cors = require("cors");
const bcrypt = require("bcrypt");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.json({
        message: "Member API Server is running."
    });
});

const PORT = 3000;

app.listen(PORT, () => {
    console.log(`Sever is running on http://localhost:${PORT}`);
});

const mysql = require("mysql2/promise");

const db = mysql.createPool({
    host: "127.0.0.1",
    port: 3306,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: "member_db"
});

app.get("/members", async (req, res) => {
    try { 
        const [rows] = await db.query(
            "SELECT user_id, username, email, status FROM members"
        );

        res.json(rows);
    } catch(error) {
        console.error(error);
        res.status(500).json({
            message: "Database error."
        });
    }
});

app.post("/members", async(req, res) => {
    try {
        const { username, email, password, status } = req.body;

        if(!username || !email || !password || !status) {
            return res.status(400).json({
                message: "Required fields are missing."
            });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        const [result] = await db.query(
            `INSERT INTO members
            (username, email, password, status, created_at)
            VALUES (?, ?, ?, ?, NOW())`,
            [username, email, hashedPassword, status]
        );

        res.status(201).json({
            user_id: result.insertId,
            username,
            email,
            status
        });
    } catch(error) {
        console.error(error);

        res.status(500).json({
            message: "Database error."
        });
    }
});

app.get("/members/:id", async (req, res) => {
    try {
        const { id } = req.params;

        const [rows] = await db.query(
            `SELECT user_id, username, email, status
             FROM members
             WHERE user_id = ?`,
            [id]
        );

        if (rows.length === 0) {
            return res.status(404).json({
                message: "Member not found."
            });
        }

        res.json(rows[0]);

    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: "Database error."
        });
    }
});

app.put("/members/:id", async (req, res) => {
    try {
        const { id } = req.params;
        const { username, email, password, status } = req.body;

        if (!username || !email || !password || !status) {
            return res.status(400).json({
                message: "Required fields are missing."
            });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        const [result] = await db.query(
            `UPDATE members
             SET username = ?,
                 email = ?,
                 password = ?,
                 status = ?
             WHERE user_id = ?`,
            [username, email, hashedPassword, status, id]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({
                message: "Member not found."
            });
        }

        res.json({
            user_id: Number(id),
            username,
            email,
            status
        });

    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: "Database error."
        });
    }
});

app.delete("/members/:id", async (req, res) => {
    try {
        const { id } = req.params;

        const [result] = await db.query(
            "DELETE FROM members WHERE user_id = ?",
            [id]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({
                message: "Member not found."
            });
        }

        res.json({
            message: "Member deleted successfully.",
            user_id: Number(id)
        });

    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: "Database error."
        });
    }
});


 // login API
app.post("/auth/login", async (req, res) => {
    try {
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).json({
                message: "Username and password are required."
            });
        }

        const [rows] = await db.query(
            `SELECT user_id, username, email, password, status
             FROM members
             WHERE username = ?`,
            [username]
        );

        // 존재하지 않는 사용자
        if (rows.length === 0) {
            return res.status(401).json({
                message: "Username or password is incorrect."
            });
        }

        const member = rows[0];

        // 비활성 계정
        if (member.status !== "ACTIVE") {
            await db.query(
                `INSERT INTO login_history
                 (user_id, login_at, login_result)
                 VALUES (?, NOW(), ?)`,
                [member.user_id, "FAILURE"]
            );

            return res.status(403).json({
                message: "This account cannot log in."
            });
        }

        // 비밀번호 검증
        const isPasswordCorrect = await bcrypt.compare(
            password,
            member.password
        );

        // 비밀번호 오류
        if (!isPasswordCorrect) {
            await db.query(
                `INSERT INTO login_history
                 (user_id, login_at, login_result)
                 VALUES (?, NOW(), ?)`,
                [member.user_id, "FAILURE"]
            );

            return res.status(401).json({
                message: "Username or password is incorrect."
            });
        }

        // 로그인 성공 기록
        await db.query(
            `INSERT INTO login_history
             (user_id, login_at, login_result)
             VALUES (?, NOW(), ?)`,
            [member.user_id, "SUCCESS"]
        );

        res.json({
            message: "Login successful.",
            user: {
                user_id: member.user_id,
                username: member.username,
                email: member.email,
                status: member.status
            }
        });

    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: "Database error."
        });
    }
});
