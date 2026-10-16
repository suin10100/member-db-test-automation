<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToLogin = () => {
  router.push('/')
}
</script>

<template>
  <main class="complete-page">
    <section class="complete-container">
      <h1 class="logo">MEMBER</h1>

      <div class="complete-content">
        <h2>로그인이 완료되었습니다.</h2>
        <p>정상적으로 로그인되었습니다.</p>

        <button type="button" class="login-button" @click="goToLogin">
          로그인 화면으로
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.complete-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #ffffff;
  box-sizing: border-box;
  padding: 40px 20px;
}

.complete-container {
  width: 100%;
  max-width: 460px;
}

.logo {
  margin: 0 0 50px;
  text-align: center;
  color: #03c75a;
  font-size: 42px;
  font-weight: 800;
  letter-spacing: -2px;
}

.complete-content {
  text-align: center;
}

.complete-content h2 {
  margin: 0 0 12px;
  color: #333333;
  font-size: 22px;
  font-weight: 700;
}

.complete-content p {
  margin: 0 0 30px;
  color: #777777;
  font-size: 14px;
}

.login-button {
  width: 100%;
  height: 56px;
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

@media (max-width: 480px) {
  .complete-page {
    padding: 30px 20px;
  }

  .logo {
    font-size: 36px;
    margin-bottom: 40px;
  }

  .complete-content h2 {
    font-size: 20px;
  }
}
</style>