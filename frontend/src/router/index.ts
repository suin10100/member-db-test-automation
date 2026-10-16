import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import SignupCompleteView from '../views/SignupCompleteView.vue'
import LoginCompleteView from '../views/LoginCompleteView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: '/signup-complete',
      name: 'signup-complete',
      component: SignupCompleteView,
    },
    {
    path: '/login-complete',
    name: 'login-complete',
    component: LoginCompleteView,
    },
  ],
})

export default router