<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import CabinetNav from '@/components/cabinet/CabinetNav.vue'
import StaffBanner from '@/components/cabinet/StaffBanner.vue'
import RequestCard from '@/components/cabinet/RequestCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import { REQUEST_STATUS, SERVICE_TYPE, serviceType } from '@/constants/labels'

const auth = useAuthStore()

const items = ref([])
const total = ref(0)
const loading = ref(true)
const failed = ref(false)
const myServiceTypes = ref([])

const PAGE = 20

const filters = reactive({
  scope: 'all', // all | relevant | mine
  status: '',
  service_type: '',
  offset: 0,
})

const scopes = computed(() => [
  { value: 'all', label: 'Все' },
  { value: 'relevant', label: 'Подходят мне' },
  { value: 'mine', label: 'Назначены мне' },
])

const hasMore = computed(() => items.value.length < total.value)

/**
 * Фильтр «подходят мне» при пустом наборе пометок возвращает ничего,
 * а не всё — так решено на бэкенде. Значит здесь нужно объяснить,
 * почему список пуст, иначе человек решит, что заявок нет вообще.
 */
const noTags = computed(
  () => filters.scope === 'relevant' && myServiceTypes.value.length === 0,
)

async function load({ append = false } = {}) {
  loading.value = true
  failed.value = false

  try {
    const { data } = await api.get('/api/requests/', {
      params: {
        status: filters.status || undefined,
        service_type: filters.service_type || undefined,
        relevant: filters.scope === 'relevant' || undefined,
        mine: filters.scope === 'mine' || undefined,
        limit: PAGE,
        offset: filters.offset,
      },
    })
    items.value = append ? [...items.value, ...data.items] : data.items
    total.value = data.total
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

function reset() {
  filters.offset = 0
  load()
}

function more() {
  filters.offset += PAGE
  load({ append: true })
}

watch(() => [filters.scope, filters.status, filters.service_type], reset)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/tags/my/service-types/')
    myServiceTypes.value = data
  } catch {
    myServiceTypes.value = []
  }
  load()
})
</script>

<template>
  <StaffBanner />
  <CabinetNav />

  <main class="section">
    <div class="shell">
      <header class="head">
        <h1 class="head__title">Заявки</h1>
        <p v-if="!loading && !failed" class="head__count">
          Найдено: {{ total }}
        </p>
      </header>

      <div class="filters">
        <div class="seg" role="group" aria-label="Что показывать">
          <button
            v-for="s in scopes"
            :key="s.value"
            class="seg__btn"
            type="button"
            :aria-pressed="filters.scope === s.value"
            :class="{ 'seg__btn--on': filters.scope === s.value }"
            @click="filters.scope = s.value"
          >
            {{ s.label }}
          </button>
        </div>

        <label class="pick">
          <span class="pick__label">Статус</span>
          <select v-model="filters.status" class="pick__select">
            <option value="">любой</option>
            <option v-for="(v, k) in REQUEST_STATUS" :key="k" :value="k">
              {{ v.label }}
            </option>
          </select>
        </label>

        <label class="pick">
          <span class="pick__label">Вид</span>
          <select v-model="filters.service_type" class="pick__select">
            <option value="">любой</option>
            <option v-for="(v, k) in SERVICE_TYPE" :key="k" :value="k">
              {{ v.label }}
            </option>
          </select>
        </label>
      </div>

      <SkeletonCard v-if="loading && !items.length" :count="6" />

      <EmptyState
        v-else-if="failed"
        title="Не удалось загрузить заявки"
        hint="Проверьте соединение и обновите страницу."
      />

      <EmptyState
        v-else-if="noTags && !items.length"
        title="У вас не указаны пометки"
        hint="Подбор работает по пометкам вида съёмки. Попросите контент-менеджера
              добавить вам подходящие — после этого заявки появятся здесь."
      >
        <button class="link" type="button" @click="filters.scope = 'all'">
          Показать все заявки
        </button>
      </EmptyState>

      <EmptyState
        v-else-if="!items.length"
        title="Заявок по этим условиям нет"
        hint="Попробуйте снять фильтры или заглянуть позже."
      />

      <template v-else>
        <ul class="grid">
          <li v-for="r in items" :key="r.id">
            <RequestCard :request="r" />
          </li>
        </ul>

        <button
          v-if="hasMore"
          class="more"
          type="button"
          :disabled="loading"
          @click="more"
        >
          {{ loading ? 'Загружаем…' : 'Показать ещё' }}
        </button>
      </template>
    </div>
  </main>
</template>

<style scoped>
.head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.head__title {
  font-size: var(--step-3);
}

.head__count {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--line);
}

.seg {
  display: flex;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.seg__btn {
  min-height: 44px;
  padding-inline: var(--space-3);
  border: 0;
  background: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  color: var(--muted);
  cursor: pointer;
}

.seg__btn:hover {
  color: var(--ink);
}

.seg__btn--on {
  background: var(--ink);
  color: var(--paper);
}

.pick {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.pick__label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.pick__select {
  min-height: 44px;
  padding: 0.35rem 0.6rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font: inherit;
  font-size: var(--step--1);
}

.grid {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.more {
  display: block;
  margin: var(--space-4) auto 0;
  min-height: 48px;
  padding-inline: var(--space-4);
  border: 1.5px solid var(--ink);
  border-radius: var(--radius);
  background: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  cursor: pointer;
}

.more:hover:not(:disabled) {
  background: var(--ink);
  color: var(--paper);
}

.more:disabled {
  opacity: 0.5;
  cursor: progress;
}

.link {
  min-height: 44px;
  border: 0;
  background: none;
  font: inherit;
  color: var(--red);
  text-decoration: underline;
  cursor: pointer;
}
</style>
