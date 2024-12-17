const express = require('express');
const mysql = require('mysql2');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const path = require("path");
const bodyParser = require('body-parser');
const cors = require('cors');

// 初始化Express应用
const app = express();
const port = 8000;



// 使用CORS中间件处理跨域请求
app.use(cors());

// 使用body-parser解析请求体
app.use(bodyParser.json());
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "static/login.html"));
});
app.use(express.static("static"));
// 创建MySQL连接池
const pool = mysql.createPool({
    host: '127.0.0.1',
    user: 'poem_user',  // 根据你的MySQL设置修改用户名
    password: '123456',  // 根据你的MySQL设置修改密码
    database: 'userAuth',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// 注册接口
app.post('/register', async (req, res) => {
    const { username, email, password } = req.body;

    // 检查邮箱是否已存在
    pool.execute('SELECT * FROM users WHERE email = ?', [email], async (err, results) => {
        if (err) {
            return res.json({ status: 'error', message: 'Database error' });
        }

        if (results.length > 0) {
            return res.json({ status: 'error', message: 'Email already in use' });
        }

        // 哈希密码
        const hashedPassword = await bcrypt.hash(password, 10);

        // 插入新用户
        pool.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', [username, email, hashedPassword], (err, results) => {
            if (err) {
                return res.json({ status: 'error', message: 'Database error' });
            }
            res.json({ status: 'success', message: 'User registered successfully' });
        });
    });
});

// 登录接口
app.post('/login', async (req, res) => {
    const { email, password } = req.body;

    // 查找用户
    pool.execute('SELECT * FROM users WHERE email = ?', [email], async (err, results) => {
        if (err) {
            return res.json({ status: 'error', message: 'Database error' });
        }

        if (results.length === 0) {
            return res.json({ status: 'error', message: 'User not found' });
        }

        const user = results[0];

        // 检查密码
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return res.json({ status: 'error', message: 'Invalid password' });
        }

        // 生成JWT
        const token = jwt.sign({ userId: user.id }, 'your_jwt_secret_key', { expiresIn: '1h' });

        res.json({
            status: 'success',
            message: 'Login successful',
            token,
            redirect: 'index.html' // 根据需要修改重定向路径
        });
    });
});

// 启动服务器
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});



