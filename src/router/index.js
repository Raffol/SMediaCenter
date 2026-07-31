import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // --- публичное ---
  { path: '/', name: 'home', component: () => import('@/views/LandingView.vue') },
  {
    path: '/zayavka/otpravlena/:number',
    name: 'request-sent',
    component: () => import('@/views/RequestSentView.vue'),
  },
  { path: '/novosti', name: 'posts', component: () => import('@/views/PostListView.vue') },
  {
    path: '/komanda/:id',
    name: 'member',
    component: () => import('@/views/MemberView.vue'),
  },
  { path: '/novosti/:slug', name: 'post', component: () => import('@/views/PostView.vue') },
  {
    path: '/vhod',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true },
  },

  // --- личный кабинет ---
  {
    path: '/smena-parolya',
    name: 'change-password',
    component: () => import('@/views/ChangePasswordView.vue'),
    meta: { requiresAuth: true, allowWithTempPassword: true },
  },
  {
    path: '/kabinet',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/kabinet/zayavki',
    name: 'requests',
    component: () => import('@/views/RequestListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/kabinet/zayavki/:id',
    name: 'request',
    component: () => import('@/views/RequestDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/kabinet/publikacii',
    name: 'manage-posts',
    component: () => import('@/views/ManagePostsView.vue'),
    meta: { requiresAuth: true, requiresStaff: true },
  },

  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to) => (to.hash ? { el: to.hash, behavior: 'smooth' } : { top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // При первой загрузке проверяем сессию — иначе guard отправит
  // на вход уже вошедшего пользователя.
  if (!auth.ready) await auth.fetchMe()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  // Временный пароль — тупик: везде, кроме экрана смены, разворачиваем назад
  if (auth.mustChangePassword && to.meta.requiresAuth && !to.meta.allowWithTempPassword) {
    return { name: 'change-password' }
  }

  if (to.meta.requiresStaff && !auth.isStaff) {
    return { name: 'dashboard' }
  }

  return true
})
