const express = require("express");

const app = express();

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