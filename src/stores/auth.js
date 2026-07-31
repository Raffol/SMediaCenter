import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/api/client'

// Уровни ролей повторяют ROLE_LEVEL на бэкенде.
// Проверки здесь — только для показа кнопок. Настоящая защита на сервере:
// скрытая кнопка ничего не защищает.
const ROLE_LEVEL = { member: 10, content_manager: 20, admin: 30 }

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const ready = ref(false) // сессия проверена, можно решать про редиректы

  const isAuthenticated = computed(() => user.value !== null)
  const mustChangePassword = computed(() => user.value?.must_change_password === true)
  const isStaff = computed(
    () => (ROLE_LEVEL[user.value?.role] ?? 0) >= ROLE_LEVEL.content_manager,
  )
  const isAdmin = computed(() => user.value?.role === 'admin')

  /**
   * Запрашивает cookie csrftoken.
   *
   * Django не выдаёт токен, пока его не попросят: без этого вызова
   * первый POST (вход, заявка с лендинга) вернёт 403 «CSRF Failed».
   * Вызывается один раз при загрузке приложения.
   */
  async function ensureCsrf() {
    try {
      await api.get('/api/auth/csrf/')
    } catch {
      // Не критично: если бэкенд недоступен, ошибка всплывёт на самом запросе
    }
  }

  async function fetchMe() {
    await ensureCsrf()
    try {
      const { data } = await api.get('/api/auth/me/')
      user.value = data
    } catch {
      user.value = null
    } finally {
      ready.value = true
    }
  }

  async function login(payload) {
    const { data } = await api.post('/api/auth/login/', payload)
    user.value = data
    return data
  }

  async function logout() {
    try {
      await api.post('/api/auth/logout/')
    } finally {
      user.value = null
    }
  }

  async function changePassword(currentPassword, newPassword) {
    await api.post('/api/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    if (user.value) user.value.must_change_password = false
  }

  function clear() {
    user.value = null
  }

  return {
    user, ready,
    isAuthenticated, mustChangePassword, isStaff, isAdmin,
    ensureCsrf, fetchMe, login, logout, changePassword, clear,
  }
})
