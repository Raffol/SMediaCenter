<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { errorText } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Правки макета:
 *  — карточка была почти прозрачной: заголовок лежал на волосах человека
 *    с фотографии. Стекло плотнее, есть рамка и тень;
 *  — фон нужен без лиц в центре (см. public/img/README.md): взгляд уходил
 *    на человека, а не на кнопку;
 *  — карточка была на 300px выше содержимого, между заголовком и кнопкой
 *    зияла пустота. Высота теперь по контенту;
 *  — вместо входа через Вконтакте — логин и пароль: OAuth требует
 *    callback-адреса из интернета, а сайт живёт в локальной сети.
 */

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const login = ref('')
const password = ref('')
const remember = ref(false)
const showPassword = ref(false)
const sending = ref(false)
const error = ref('')

async function submit() {
  if (!login.value || !password.value) {
    error.value = 'Заполните логин и пароль'
    return
  }

  error.value = ''
  sending.value = true
  try {
    const user = await auth.login({
      login: login.value.trim(),
      password: password.value,
      remember: remember.value,
    })

    if (user.must_change_password) {
      router.push({ name: 'change-password' })
    } else {
      router.push(route.query.redirect || { name: 'dashboard' })
    }
  } catch (err) {
    // Один текст на любую неудачу — бэкенд намеренно не различает
    // «нет логина» и «неверный пароль»
    error.value = errorText(err, 'Неверный логин или пароль')
    password.value = ''
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <main class="gate">
    <img
      class="gate__bg"
      src="/img/login.jpg"
      alt=""
      aria-hidden="true"
      decoding="async"
    />
    <div class="gate__scrim" />

    <div class="card">
      <h1 class="card__title">Личный кабинет</h1>
      <p class="card__lead">Войдите, чтобы откликаться на заявки.</p>

      <div class="card__field">
        <label class="card__label" for="l-login">Логин</label>
        <input
          id="l-login"
          v-model="login"
          class="card__input"
          type="text"
          autocomplete="username"
          autocapitalize="off"
          spellcheck="false"
          @keyup.enter="submit"
        />
      </div>

      <div class="card__field">
        <label class="card__label" for="l-pass">Пароль</label>
        <div class="card__wrap">
          <input
            id="l-pass"
            v-model="password"
            class="card__input"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            @keyup.enter="submit"
          />
          <button
            class="card__peek tap"
            type="button"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? 'Скрыть' : 'Показать' }}
          </button>
        </div>
      </div>

      <label class="card__remember">
        <input v-model="remember" type="checkbox" />
        <span>Запомнить меня</span>
      </label>

      <p v-if="error" class="card__error">
        <AppIcon name="alert" :size="16" /> {{ error }}
      </p>

      <button class="card__submit" type="button" :disabled="sending" @click="submit">
        {{ sending ? 'Входим…' : 'Войти' }}
      </button>

      <!-- Экрана «Забыли пароль» нет намеренно: SMTP в локальной сети
           отсутствует, автоматический сброс невозможен -->
      <p class="card__help">
        Забыли пароль? Обратитесь к администратору:
        <a href="mailto:media@example.ru">media@example.ru</a>
      </p>
    </div>
  </main>
</template>

<style scoped>
.gate {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: var(--space-6) var(--space-3) var(--space-5);
  isolation: isolate;
}

.gate__bg,
.gate__scrim {
  position: absolute;
  inset: 0;
  z-index: -1;
}

.gate__bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gate__scrim {
  background: var(--scrim-hard);
}

.card {
  display: grid;
  gap: var(--space-3);
  width: 100%;
  max-width: 27rem;
  padding: var(--space-4);
  /* Плотнее, чем в макете: прозрачная карточка не читалась как карточка */
  background: rgba(255, 255, 255, 0.13);
  backdrop-filter: blur(22px);
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  color: var(--paper);
}

.card__title {
  font-size: var(--step-2);
}

.card__lead {
  margin: calc(var(--space-2) * -1) 0 0;
  font-size: var(--step--1);
  color: rgba(255, 255, 255, 0.78);
}

.card__field {
  display: grid;
  gap: var(--space-1);
}

.card__label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.card__wrap {
  position: relative;
  display: flex;
}

.card__input {
  width: 100%;
  min-height: 48px;
  padding: 0.7rem 0.85rem;
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  border-radius: var(--radius);
  background: rgba(0, 0, 0, 0.35);
  font: inherit;
  color: var(--paper);
}

.card__input:hover {
  border-color: rgba(255, 255, 255, 0.6);
}

.card__peek {
  position: absolute;
  right: 0.35rem;
  top: 50%;
  transform: translateY(-50%);
  padding-inline: 0.6rem;
  border: 0;
  background: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: var(--step--1);
  cursor: pointer;
}

.card__peek:hover {
  color: var(--paper);
}

.card__remember {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 44px;
  font-size: var(--step--1);
  cursor: pointer;
}

.card__error {
  display: flex;
  align-items: center;
  gap: 0.4em;
  margin: 0;
  padding: var(--space-2);
  border-left: 3px solid var(--red);
  background: rgba(225, 29, 46, 0.18);
  font-size: var(--step--1);
}

.card__submit {
  min-height: 54px;
  border: 0;
  border-radius: var(--radius);
  background: var(--red);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 800;
  font-size: var(--step-1);
  cursor: pointer;
  transition: background 0.2s var(--ease);
}

.card__submit:hover:not(:disabled) {
  background: var(--red-dark);
}

.card__submit:disabled {
  background: rgba(255, 255, 255, 0.3);
  cursor: progress;
}

.card__help {
  margin: 0;
  font-size: var(--step--1);
  color: rgba(255, 255, 255, 0.7);
}

.card__help a {
  color: var(--paper);
}
</style>
