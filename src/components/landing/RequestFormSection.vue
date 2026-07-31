<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, errorText } from '@/api/client'
import { usePhoneMask } from '@/composables/usePhoneMask'
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Правки из разбора макета:
 *  — появилась кнопка отправки (в макете форма обрывалась на «Виде съёмки»);
 *  — добавлены дата, место и описание: по имени, телефону и виду съёмки
 *    невозможно решить, брать заявку, и каждая превращалась в звонок;
 *  — placeholder'ы больше не дублируют подписи, а показывают формат;
 *  — кнопка блокируется на время отправки, иначе двойной клик создаёт дубль.
 */

const router = useRouter()

const services = [
  { value: 'photo', label: 'Фотосъёмка', icon: 'photo' },
  { value: 'video', label: 'Видеосъёмка', icon: 'video' },
  { value: 'article', label: 'Написание статей', icon: 'article' },
  { value: 'design', label: 'Дизайн', icon: 'design' },
]

const form = reactive({
  client_name: '',
  service_type: '',
  event_date: '',
  location: '',
  description: '',
  client_contact_extra: '',
})

const phone = usePhoneMask()
const errors = reactive({})
const sending = ref(false)
const serverError = ref('')

const today = new Date().toISOString().slice(0, 10)

const descriptionLeft = computed(() => 4000 - form.description.length)

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])

  if (form.client_name.trim().length < 2) {
    errors.client_name = 'Укажите имя, чтобы мы знали, к кому обращаться'
  }
  if (!phone.isValid()) {
    errors.client_phone = 'Введите телефон полностью: +7 999 123-45-67'
  }
  if (!form.service_type) {
    errors.service_type = 'Выберите, что нужно снять или сделать'
  }
  if (form.description.trim().length < 10) {
    errors.description = 'Опишите задачу хотя бы в одном предложении'
  }
  if (form.event_date && form.event_date < today) {
    errors.event_date = 'Дата не может быть в прошлом'
  }

  return Object.keys(errors).length === 0
}

async function submit() {
  serverError.value = ''
  if (!validate()) {
    // Фокус на первое проблемное поле: иначе на длинной форме
    // человек не поймёт, где ошибка.
    document.querySelector('[data-invalid="true"]')?.focus()
    return
  }

  sending.value = true
  try {
    const { data } = await api.post('/api/requests/', {
      client_name: form.client_name.trim(),
      client_phone: phone.raw(),
      client_contact_extra: form.client_contact_extra.trim() || null,
      service_type: form.service_type,
      description: form.description.trim(),
      event_date: form.event_date || null,
      location: form.location.trim() || null,
    })
    router.push({ name: 'request-sent', params: { number: data.public_number } })
  } catch (error) {
    serverError.value = errorText(error, 'Не удалось отправить заявку. Позвоните нам.')
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <section id="zayavka" class="section form-block">
    <div class="shell form-block__inner">
      <div class="form-block__intro">
        <h2 class="form-block__title drop-cap">Оставить заявку</h2>
        <p class="form-block__lead">
          Расскажите, что нужно снять или сделать. Мы позвоним в течение
          рабочего дня и уточним детали.
        </p>
      </div>

      <!-- form не используем: submit по Enter в поле даты ведёт себя
           непредсказуемо, а обработчик всё равно один -->
      <div class="fields">
        <div class="field">
          <label class="field__label" for="f-name">Ваше имя</label>
          <input
            id="f-name"
            v-model="form.client_name"
            class="field__input"
            type="text"
            autocomplete="name"
            placeholder="Иванов Иван"
            :data-invalid="!!errors.client_name"
            :aria-invalid="!!errors.client_name"
            aria-describedby="e-name"
          />
          <p v-if="errors.client_name" id="e-name" class="field__error">
            <AppIcon name="alert" :size="15" /> {{ errors.client_name }}
          </p>
        </div>

        <div class="field">
          <label class="field__label" for="f-phone">Телефон</label>
          <input
            id="f-phone"
            :value="phone.display.value"
            class="field__input"
            type="tel"
            inputmode="tel"
            autocomplete="tel"
            placeholder="+7 999 123-45-67"
            :data-invalid="!!errors.client_phone"
            :aria-invalid="!!errors.client_phone"
            aria-describedby="e-phone"
            @input="phone.onInput"
          />
          <p v-if="errors.client_phone" id="e-phone" class="field__error">
            <AppIcon name="alert" :size="15" /> {{ errors.client_phone }}
          </p>
        </div>

        <fieldset class="field field--wide">
          <legend class="field__label">Что нужно сделать</legend>
          <div class="picker">
            <label v-for="s in services" :key="s.value" class="picker__option">
              <input
                v-model="form.service_type"
                type="radio"
                name="service"
                :value="s.value"
                class="picker__input"
              />
              <span class="picker__box">
                <AppIcon :name="s.icon" :size="26" />
                {{ s.label }}
              </span>
            </label>
          </div>
          <p v-if="errors.service_type" class="field__error">
            <AppIcon name="alert" :size="15" /> {{ errors.service_type }}
          </p>
        </fieldset>

        <div class="field">
          <label class="field__label" for="f-date">
            Дата <span class="field__opt">— если уже известна</span>
          </label>
          <input
            id="f-date"
            v-model="form.event_date"
            class="field__input"
            type="date"
            :min="today"
            :data-invalid="!!errors.event_date"
          />
          <p v-if="errors.event_date" class="field__error">
            <AppIcon name="alert" :size="15" /> {{ errors.event_date }}
          </p>
        </div>

        <div class="field">
          <label class="field__label" for="f-place">
            Место <span class="field__opt">— необязательно</span>
          </label>
          <input
            id="f-place"
            v-model="form.location"
            class="field__input"
            type="text"
            placeholder="Корпус К, актовый зал"
          />
        </div>

        <div class="field field--wide">
          <label class="field__label" for="f-desc">Опишите задачу</label>
          <textarea
            id="f-desc"
            v-model="form.description"
            class="field__input field__input--area"
            rows="4"
            maxlength="4000"
            placeholder="Что за событие, сколько человек, что должно получиться в итоге"
            :data-invalid="!!errors.description"
            :aria-invalid="!!errors.description"
          />
          <div class="field__meta">
            <p v-if="errors.description" class="field__error">
              <AppIcon name="alert" :size="15" /> {{ errors.description }}
            </p>
            <span v-else class="field__counter">осталось {{ descriptionLeft }}</span>
          </div>
        </div>

        <div class="field field--wide">
          <label class="field__label" for="f-extra">
            Другой способ связи <span class="field__opt">— необязательно</span>
          </label>
          <input
            id="f-extra"
            v-model="form.client_contact_extra"
            class="field__input"
            type="text"
            placeholder="Телеграм, почта или ссылка на Вконтакте"
          />
        </div>

        <div class="field field--wide">
          <p v-if="serverError" class="field__error field__error--box">
            <AppIcon name="alert" :size="16" /> {{ serverError }}
          </p>

          <button class="submit" type="button" :disabled="sending" @click="submit">
            {{ sending ? 'Отправляем…' : 'Отправить заявку' }}
            <AppIcon v-if="!sending" name="arrow-right" :size="20" />
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.form-block {
  background: var(--surface);
}

.form-block__inner {
  display: grid;
  gap: var(--space-5);
}

.form-block__title {
  font-size: var(--step-3);
}

.form-block__lead {
  margin: var(--space-3) 0 0;
  max-width: 34ch;
  color: var(--ink-soft);
}

.fields {
  display: grid;
  gap: var(--space-3);
}

.field {
  display: grid;
  gap: var(--space-1);
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}

.field__label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  padding: 0;
}

.field__opt {
  font-weight: 500;
  color: var(--muted);
}

.field__input {
  width: 100%;
  min-height: 48px;
  padding: 0.7rem 0.85rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font: inherit;
  color: var(--ink);
  transition: border-color 0.15s var(--ease);
}

.field__input:hover {
  border-color: #c9c9c9;
}

.field__input[data-invalid='true'] {
  border-color: var(--red);
  background: #fff5f6;
}

.field__input--area {
  min-height: 7rem;
  resize: vertical;
  line-height: 1.5;
}

.field__meta {
  display: flex;
  justify-content: flex-end;
  min-height: 1.25rem;
}

.field__counter {
  font-size: var(--step--1);
  color: var(--muted);
}

/* Ошибка под полем, а не общим алертом сверху: иначе непонятно,
   какое из семи полей заполнено неверно. */
.field__error {
  display: flex;
  align-items: center;
  gap: 0.35em;
  margin: 0;
  margin-right: auto;
  font-size: var(--step--1);
  color: var(--red-dark);
}

.field__error--box {
  padding: var(--space-2);
  border-left: 3px solid var(--red);
  background: #fff5f6;
  margin-bottom: var(--space-2);
}

.picker {
  display: grid;
  gap: var(--space-2);
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.picker__input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.picker__box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
  height: 100%;
  padding: var(--space-3);
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  cursor: pointer;
  transition: border-color 0.15s var(--ease), color 0.15s var(--ease);
}

.picker__box:hover {
  border-color: var(--ink);
}

.picker__input:checked + .picker__box {
  border-color: var(--red);
  color: var(--red);
}

/* Фокус живёт на скрытом input, поэтому рамку рисуем на видимой части */
.picker__input:focus-visible + .picker__box {
  outline: 3px solid var(--red);
  outline-offset: 3px;
}

.submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  min-height: 54px;
  padding-inline: var(--space-4);
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

.submit:hover:not(:disabled) {
  background: var(--red-dark);
}

.submit:disabled {
  background: var(--muted);
  cursor: progress;
}

@media (min-width: 720px) {
  .fields {
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3) var(--space-4);
  }

  .field--wide {
    grid-column: 1 / -1;
  }

  .submit {
    justify-self: start;
  }
}

@media (min-width: 1000px) {
  .form-block__inner {
    grid-template-columns: 0.8fr 1.2fr;
    gap: var(--space-6);
    align-items: start;
  }
}
</style>
