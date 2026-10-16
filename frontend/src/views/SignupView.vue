<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')

const signupMessage = ref('')
const isError = ref(false)

const signup = async () => {
  signupMessage.value = ''
  isError.value = false

  if (!username.value || !email.value || !password.value || !passwordConfirm.value) {
    isError.value = true
    signupMessage.value = '모든 항목을 입력해주세요.'
    return
  }

  if (password.value !== passwordConfirm.value) {
    isError.value = true
    signupMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  try {
    const response = await fetch('http://localhost:3000/members', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value,
        status: 'ACTIVE',
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      isError.value = true
      signupMessage.value = data.message || '회원가입에 실패했습니다.'
      return
    }

    router.push('/signup-complete')
  } catch (error) {
    console.error(error)
    isError.value = true
    signupMessage.value = '서버에 연결할 수 없습니다.'
  }
}
</script>

<template>
  <main class="signup-page">
    <section class="signup-container">
      <h1 class="logo">MEMBER</h1>

      <form class="signup-form" @submit.prevent="signup">
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
          <label for="email">이메일</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="이메일"
            autocomplete="email"
          />
        </div>

        <div class="input-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호"
            autocomplete="new-password"
          />
        </div>

        <div class="input-group">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input
            id="passwordConfirm"
            v-model="passwordConfirm"
            type="password"
            placeholder="비밀번호 확인"
            autocomplete="new-password"
          />
        </div>

        <button type="submit" class="signup-button">
          회원가입
        </button>

        <p
          v-if="signupMessage"
          class="signup-message"
          :class="{ error: isError }"
        >
          {{ signupMessage }}
        </p>
      </form>

      <nav class="login-link">
        <a href="/">로그인으로 돌아가기</a>
      </nav>
    </section>
  </main>
</template>

<style scoped>
.signup-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #ffffff;
  box-sizing: border-box;
  padding: 40px 20px;
}

.signup-container {
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

.signup-form {
  width: 100%;
}

.input-group {
  margin-bottom: 10px;
}

.input-group label {
  display: block;
  margin-bottom: 6px;
  color: #333333;
  font-size: 13px;
  font-weight: 600;
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

.signup-button {
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

.signup-button:hover {
  background: #02b351;
}

.signup-message {
  margin: 14px 0 0;
  text-align: center;
  color: #03c75a;
  font-size: 13px;
}

.signup-message.error {
  color: #e74c3c;
}

.login-link {
  display: flex;
  justify-content: center;
  margin-top: 36px;
  font-size: 13px;
}

.login-link a {
  color: #777777;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .signup-page {
    padding: 30px 20px;
  }

  .logo {
    font-size: 36px;
    margin-bottom: 30px;
  }
}
</style>
