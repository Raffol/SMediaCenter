<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api, errorText } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import CabinetNav from '@/components/cabinet/CabinetNav.vue'
import StaffBanner from '@/components/cabinet/StaffBanner.vue'
import ResponseItem from '@/components/cabinet/ResponseItem.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import {
  REQUEST_STATUS,
  formatDate,
  formatDateTime,
  requestStatus,
  serviceType,
} from '@/constants/labels'

/**
 * Один URL, но два разных экрана.
 *
 * Персонал видит все отклики и может принять один из них. Участник —
 * только свой отклик и его статус; чужие бэкенд ему просто не отдаёт.
 * Это не косметика: видя чужие предложения, люди начинают сравнивать
 * себя друг с другом, и это ссорит команду.
 *
 * Разделение сделано двумя ветками шаблона, а не набором v-if внутри
 * одного блока — иначе логика прав расползается по вёрстке.
 */

const route = useRoute()
const auth = useAuthStore()

const request = ref(null)
const loading = ref(true)
const notFound = ref(false)
const busy = ref(false)
const error = ref('')

const draft = ref('')
const sending = ref(false)

const status = computed(() => requestStatus(request.value?.status))
const service = computed(() => serviceType(request.value?.service_type))

const openForResponses = computed(
  () => request.value && ['new', 'in_progress'].includes(request.value.status),
)

const phoneVisible = computed(
  () => request.value?.client_phone && !request.value.client_phone.startsWith('скрыт'),
)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/api/requests/${route.params.id}/`)
    request.value = data
  } catch (err) {
    notFound.value = err.response?.status === 404
    error.value = notFound.value ? '' : errorText(err)
  } finally {
    loading.value = false
  }
}

async function sendResponse() {
  if (draft.value.trim().length < 5) {
    error.value = 'Напишите хотя бы пару слов о том, почему берёте заявку'
    return
  }

  error.value = ''
  sending.value = true
  try {
    await api.post(`/api/requests/${route.params.id}/responses/`, {
      message: draft.value.trim(),
    })
    draft.value = ''
    await load()
  } catch (err) {
    error.value = errorText(err, 'Не удалось отправить отклик')
  } finally {
    sending.value = false
  }
}

async function decide({ id, accept, comment }) {
  busy.value = true
  error.value = ''
  try {
    await api.patch(`/api/requests/responses/${id}/`, { accept, comment })
    await load()
  } catch (err) {
    error.value = errorText(err, 'Не удалось сохранить решение')
  } finally {
    busy.value = false
  }
}

async function changeStatus(next) {
  let reason = null
  if (next === 'rejected') {
    reason = window.prompt('Причина отклонения заявки:')
    if (reason === null) return
    if (!reason.trim()) {
      error.value = 'Причина обязательна при отклонении'
      return
    }
  }

  busy.value = true
  error.value = ''
  try {
    await api.patch(`/api/requests/${route.params.id}/status/`, {
      status: next,
      reject_reason: reason,
    })
    await load()
  } catch (err) {
    error.value = errorText(err, 'Не удалось изменить статус')
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <StaffBanner />
  <CabinetNav />

  <main class="section">
    <div class="shell">
      <SkeletonCard v-if="loading" :count="1" />

      <EmptyState
        v-else-if="notFound"
        title="Заявка не найдена"
        hint="Возможно, её удалили или ссылка устарела."
      >
        <RouterLink class="link" :to="{ name: 'requests' }">Ко всем заявкам</RouterLink>
      </EmptyState>

      <template v-else-if="request">
        <RouterLink class="back" :to="{ name: 'requests' }">
          <AppIcon name="arrow-right" :size="16" /> Все заявки
        </RouterLink>

        <header class="head">
          <div>
            <p class="head__num">Заявка №{{ request.public_number }}</p>
            <h1 class="head__title">
              <AppIcon :name="service.icon" :size="26" />
              {{ service.label }}
            </h1>
          </div>
          <StatusBadge :label="status.label" :tone="status.tone" :icon="status.icon" />
        </header>

        <p v-if="error" class="alert">
          <AppIcon name="alert" :size="16" /> {{ error }}
        </p>

        <div class="layout">
          <!-- ------------------------------------------ суть заявки -->
          <section class="panel">
            <h2 class="panel__title">Задача</h2>
            <p class="panel__text">{{ request.description }}</p>

            <dl class="facts">
              <div class="facts__row">
                <dt>Дата</dt>
                <dd>{{ request.event_date ? formatDate(request.event_date) : 'не указана' }}</dd>
              </div>
              <div class="facts__row">
                <dt>Место</dt>
                <dd>{{ request.location || 'не указано' }}</dd>
              </div>
              <div class="facts__row">
                <dt>Создана</dt>
                <dd>{{ formatDateTime(request.created_at) }}</dd>
              </div>
              <div v-if="request.assignee" class="facts__row">
                <dt>Исполнитель</dt>
                <dd>
                  <RouterLink :to="{ name: 'member', params: { id: request.assignee.id } }">
                    {{ request.assignee.full_name }}
                  </RouterLink>
                </dd>
              </div>
            </dl>

            <div v-if="request.reject_reason" class="reject">
              <p class="reject__title">Причина отклонения</p>
              <p class="reject__text">{{ request.reject_reason }}</p>
            </div>
          </section>

          <!-- ------------------------------------------ контакты -->
          <aside class="panel panel--side">
            <h2 class="panel__title">Клиент</h2>
            <p class="panel__name">{{ request.client_name }}</p>

            <!-- Телефон отдаётся только назначенному исполнителю
                 и персоналу: это решение бэкенда, здесь лишь
                 объясняем, почему поля не видно -->
            <p v-if="phoneVisible" class="contact">
              <AppIcon name="phone" :size="17" />
              <a :href="`tel:${request.client_phone.replace(/\s/g, '')}`">
                {{ request.client_phone }}
              </a>
            </p>
            <p v-else class="contact contact--hidden">
              <AppIcon name="alert" :size="17" />
              Телефон откроется, когда вас назначат исполнителем
            </p>

            <p v-if="request.client_contact_extra" class="contact">
              <AppIcon name="mail" :size="17" />
              {{ request.client_contact_extra }}
            </p>

            <div v-if="auth.isStaff" class="staff-acts">
              <p class="staff-acts__label">Сменить статус</p>
              <div class="staff-acts__row">
                <button
                  v-for="(v, k) in REQUEST_STATUS"
                  :key="k"
                  class="chip-btn"
                  type="button"
                  :disabled="busy || request.status === k"
                  @click="changeStatus(k)"
                >
                  {{ v.label }}
                </button>
              </div>
            </div>
          </aside>
        </div>

        <!-- ============================ ВЗГЛЯД ПЕРСОНАЛА ============ -->
        <section v-if="auth.isStaff" class="panel">
          <h2 class="panel__title">
            Отклики
            <span class="panel__count">{{ request.responses.length }}</span>
          </h2>

          <EmptyState
            v-if="!request.responses.length"
            title="Никто ещё не откликнулся"
            hint="Если заявка срочная, назначьте исполнителя вручную — это можно
                  сделать в админке или через API."
          />

          <ul v-else class="resp-list">
            <li v-for="r in request.responses" :key="r.id">
              <ResponseItem :response="r" :can-decide="true" :busy="busy" @decide="decide" />
            </li>
          </ul>
        </section>

        <!-- ============================ ВЗГЛЯД УЧАСТНИКА ============ -->
        <section v-else class="panel">
          <h2 class="panel__title">Ваш отклик</h2>

          <ResponseItem v-if="request.my_response" :response="request.my_response" />

          <template v-else-if="openForResponses">
            <p class="hint">
              Опишите, почему берёте эту заявку: свободны ли на дату, что
              планируете сделать. Решение принимает контент-менеджер.
            </p>
            <textarea
              v-model="draft"
              class="draft"
              rows="4"
              maxlength="2000"
              placeholder="Свободен в эту дату, снимал похожее мероприятие в марте"
            />
            <button class="send" type="button" :disabled="sending" @click="sendResponse">
              {{ sending ? 'Отправляем…' : 'Откликнуться' }}
            </button>
          </template>

          <EmptyState
            v-else
            title="Заявка закрыта для откликов"
            hint="Она уже выполнена или отклонена."
          />
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
.back {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  min-height: 44px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  color: var(--muted);
  text-decoration: none;
}

.back:hover {
  color: var(--ink);
}

.back :deep(svg) {
  transform: rotate(180deg);
}

.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}

.head__num {
  margin: 0 0 var(--space-1);
  font-family: var(--font-display);
  font-size: var(--step--1);
  font-weight: 700;
  color: var(--muted);
}

.head__title {
  display: flex;
  align-items: center;
  gap: 0.45em;
  font-size: var(--step-3);
}

.head__title :deep(svg) {
  color: var(--red);
  flex: none;
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.4em;
  margin: 0 0 var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-left: 3px solid var(--red);
  background: #fff5f6;
  font-size: var(--step--1);
  color: var(--red-dark);
}

.layout {
  display: grid;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.panel {
  padding: var(--space-4);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
}

.panel--side {
  background: var(--surface);
  margin-bottom: 0;
}

.layout .panel {
  margin-bottom: 0;
}

.panel__title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--step-1);
  margin-bottom: var(--space-3);
}

.panel__count {
  padding: 0.1em 0.5em;
  border-radius: 999px;
  background: var(--surface);
  font-size: var(--step--1);
  color: var(--muted);
}

.panel__text {
  margin: 0 0 var(--space-3);
  white-space: pre-line;
  color: var(--ink-soft);
}

.panel__name {
  margin: 0 0 var(--space-2);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step-1);
}

.facts {
  display: grid;
  gap: var(--space-1);
  margin: 0;
  font-size: var(--step--1);
}

.facts__row {
  display: flex;
  gap: var(--space-2);
}

.facts__row dt {
  min-width: 8rem;
  color: var(--muted);
}

.facts__row dd {
  margin: 0;
}

.reject {
  margin-top: var(--space-3);
  padding: var(--space-3);
  border-left: 3px solid var(--muted);
  background: var(--surface);
}

.reject__title {
  margin: 0 0 var(--space-1);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.reject__text {
  margin: 0;
  font-size: var(--step--1);
  color: var(--ink-soft);
}

.contact {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin: 0 0 var(--space-2);
  font-size: var(--step--1);
}

.contact :deep(svg) {
  flex: none;
  color: var(--red);
}

.contact--hidden {
  color: var(--muted);
}

.contact--hidden :deep(svg) {
  color: var(--muted);
}

.staff-acts {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--line);
}

.staff-acts__label {
  margin: 0 0 var(--space-2);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.staff-acts__row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.chip-btn {
  min-height: 40px;
  padding-inline: var(--space-2);
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font: inherit;
  font-size: var(--step--1);
  cursor: pointer;
}

.chip-btn:hover:not(:disabled) {
  border-color: var(--ink);
}

.chip-btn:disabled {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
  cursor: default;
}

.resp-list {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}

.hint {
  margin: 0 0 var(--space-2);
  font-size: var(--step--1);
  color: var(--muted);
}

.draft {
  width: 100%;
  padding: 0.7rem 0.85rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  font: inherit;
  resize: vertical;
  margin-bottom: var(--space-3);
}

.send {
  min-height: 50px;
  padding-inline: var(--space-4);
  border: 0;
  border-radius: var(--radius);
  background: var(--red);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 800;
  cursor: pointer;
}

.send:hover:not(:disabled) {
  background: var(--red-dark);
}

.send:disabled {
  background: var(--muted);
  cursor: progress;
}

.link {
  color: var(--red);
}

@media (min-width: 900px) {
  .layout {
    grid-template-columns: 1.6fr 1fr;
    align-items: start;
  }
}
</style>
