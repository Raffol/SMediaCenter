<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { errorText } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Тупик для временного пароля: guard в роутере не пускает никуда,
 * пока must_change_password не снят. Иначе человек сможет работать
 * в обход смены, а бэкенд всё равно вернёт 403 на каждый запрос.
 */
const auth = useAuthStore()
const router = useRouter()

const current = ref('')
const next = ref('')
const repeat = ref('')
const sending = ref(false)
const error = ref('')
const done = ref(false)

const forced = computed(() => auth.mustChangePassword)

const tooShort = computed(() => next.value.length > 0 && next.value.length < 8)
const mismatch = computed(() => repeat.value.length > 0 && next.value !== repeat.value)

async function submit() {
  error.value = ''

  if (next.value.length < 8) {
    error.value = 'Новый пароль должен быть не короче 8 символов'
    return
  }
  if (next.value !== repeat.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  if (next.value === current.value) {
    error.value = 'Новый пароль совпадает с текущим'
    return
  }

  sending.value = true
  try {
    await auth.changePassword(current.value, next.value)
    done.value = true
    setTimeout(() => router.push({ name: 'dashboard' }), 900)
  } catch (err) {
    error.value = errorText(err, 'Не удалось сменить пароль')
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <main class="section">
    <div class="shell wrap">
      <h1 class="title">{{ forced ? 'Задайте свой пароль' : 'Смена пароля' }}</h1>

      <p v-if="forced" class="lead">
        Вы вошли с временным паролем, который выдал администратор.
        Замените его, чтобы продолжить.
      </p>

      <p v-if="done" class="ok">
        <AppIcon name="check" :size="17" /> Пароль изменён. Открываем кабинет…
      </p>

      <template v-else>
        <div class="field">
          <label class="field__label" for="p-cur">
            {{ forced ? 'Временный пароль' : 'Текущий пароль' }}
          </label>
          <input
            id="p-cur"
            v-model="current"
            class="field__input"
            type="password"
            autocomplete="current-password"
          />
        </div>

        <div class="field">
          <label class="field__label" for="p-new">Новый пароль</label>
          <input
            id="p-new"
            v-model="next"
            class="field__input"
            type="password"
            autocomplete="new-password"
            :data-invalid="tooShort"
          />
          <p class="field__hint">
            Не короче 8 символов. Длинная фраза надёжнее короткого набора
            символов со звёздочками.
          </p>
        </div>

        <div class="field">
          <label class="field__label" for="p-rep">Повторите пароль</label>
          <input
            id="p-rep"
            v-model="repeat"
            class="field__input"
            type="password"
            autocomplete="new-password"
            :data-invalid="mismatch"
            @keyup.enter="submit"
          />
          <p v-if="mismatch" class="field__err">
            <AppIcon name="alert" :size="15" /> Пароли не совпадают
          </p>
        </div>

        <p v-if="error" class="alert">
          <AppIcon name="alert" :size="16" /> {{ error }}
        </p>

        <button class="submit" type="button" :disabled="sending" @click="submit">
          {{ sending ? 'Сохраняем…' : 'Сохранить пароль' }}
        </button>
      </template>
    </div>
  </main>
</template>

<style scoped>
.wrap {
  display: grid;
  gap: var(--space-3);
  max-width: 30rem;
}

.title {
  font-size: var(--step-2);
}

.lead {
  margin: 0;
  color: var(--ink-soft);
}

.field {
  display: grid;
  gap: var(--space-1);
}

.field__label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.field__input {
  min-height: 48px;
  padding: 0.7rem 0.85rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  font: inherit;
}

.field__input[data-invalid='true'] {
  border-color: var(--red);
  background: #fff5f6;
}

.field__hint {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}

.field__err,
.alert {
  display: flex;
  align-items: center;
  gap: 0.4em;
  margin: 0;
  font-size: var(--step--1);
  color: var(--red-dark);
}

.alert {
  padding: var(--space-2);
  border-left: 3px solid var(--red);
  background: #fff5f6;
}

.ok {
  display: flex;
  align-items: center;
  gap: 0.4em;
  margin: 0;
  padding: var(--space-3);
  background: #ddf3e4;
  color: #14663a;
  border-radius: var(--radius);
}

.submit {
  min-height: 52px;
  border: 0;
  border-radius: var(--radius);
  background: var(--red);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 800;
  font-size: var(--step-0);
  cursor: pointer;
}

.submit:hover:not(:disabled) {
  background: var(--red-dark);
}

.submit:disabled {
  background: var(--muted);
  cursor: progress;
}
</style>
