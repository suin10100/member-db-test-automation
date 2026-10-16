<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const loginMessage = ref('')
const isError = ref(false)
const router = useRouter()

const login = async () => {
  loginMessage.value = ''
  isError.value = false

  try {
    const response = await fetch('http://localhost:3000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      isError.value = true
      loginMessage.value = data.message
      return
    }

    router.push('/login-complete')
  } catch (error) {
    console.error(error)
    isError.value = true
    loginMessage.value = '서버에 연결할 수 없습니다.'
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-container">
      <h1 class="logo">MEMBER</h1>

      <form class="login-form" @submit.prevent="login">
        <div class="input-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="아이디"
            autocomplete="username"
          />
        </div>

        <div class="input-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호"
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="login-button" @click="login">
          로그인
        </button>

        <p
          v-if="loginMessage"
          class="login-message"
          :class="{ error: isError }"
        >
          {{ loginMessage }}
        </p>

      </form>

      <div class="login-options">
        <label class="remember">
          <input type="checkbox" />
          <span>아이디 저장</span>
        </label>
      </div>

      <nav class="help-links">
        <a href="/signup">회원가입</a>
      </nav>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #ffffff;
  box-sizing: border-box;
  padding: 40px 20px;
}

.login-container {
  width: 100%;
  max-width: 460px;
}

.logo {
  margin: 0 0 40px;
  text-align: center;
  color: #03c75a;
  font-size: 42px;
  font-weight: 800;
  letter-spacing: -2px;
}

.login-form {
  width: 100%;
}

.input-group {
  position: relative;
  margin-bottom: 10px;
}

.input-group label {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.input-group input {
  width: 100%;
  height: 56px;
  box-sizing: border-box;
  padding: 0 18px;
  border: 1px solid #dadada;
  border-radius: 6px;
  background: #ffffff;
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s ease;
}

.input-group input:focus {
  border-color: #03c75a;
}

.input-group input::placeholder {
  color: #999999;
}

.login-button {
  width: 100%;
  height: 56px;
  margin-top: 10px;
  border: none;
  border-radius: 6px;
  background: #03c75a;
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.login-button:hover {
  background: #02b351;
}

.login-options {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.remember {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #777777;
  font-size: 13px;
  cursor: pointer;
}

.remember input {
  width: 15px;
  height: 15px;
  cursor: pointer;
}

.help-links {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 36px;
  font-size: 13px;
}

.help-links a {
  color: #777777;
  text-decoration: none;
}

.help-links a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-page {
    padding: 30px 20px;
  }

  .logo {
    font-size: 36px;
    margin-bottom: 30px;
  }
}
</style>