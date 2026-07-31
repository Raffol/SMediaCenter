import axios from 'axios'

export const api = axios.create({
  // Пусто по умолчанию: запросы идут относительными путями (/api/...),
  // их подхватывает прокси Vite и передаёт в Django. Браузер видит один
  // источник — cookie работает без CORS.
  baseURL: import.meta.env.VITE_API_URL ?? '',
  // Обязательно: без этого cookie сессии не уедет на бэкенд
  withCredentials: true,
  // Django ждёт токен CSRF в заголовке X-CSRFToken, а кладёт его в cookie
  // csrftoken. Axios переносит одно в другое сам, если указать имена.
  // Без этого любой POST вернёт 403 «CSRF Failed».
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

// Обработчик 401 подключается из main.js, чтобы не тянуть роутер и стор
// в этот модуль — иначе получится циклический импорт.
export function installAuthInterceptor(router, authStore) {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      const status = error.response?.status

      if (status === 401) {
        authStore.clear()
        if (router.currentRoute.value.meta.requiresAuth) {
          router.push({
            name: 'login',
            query: { redirect: router.currentRoute.value.fullPath },
          })
        }
      }

      if (status === 403 && error.response?.data?.detail?.includes('временный пароль')) {
        router.push({ name: 'change-password' })
      }

      return Promise.reject(error)
    },
  )
}

/** Достаёт текст ошибки из ответа FastAPI в пригодном для показа виде. */
export function errorText(error, fallback = 'Что-то пошло не так. Попробуйте ещё раз.') {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  // Ошибки валидации Pydantic приходят массивом объектов
  if (Array.isArray(detail) && detail.length) return detail[0].msg
  return fallback
}
