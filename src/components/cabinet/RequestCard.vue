<script setup>
import { computed } from 'vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import {
  formatDate,
  formatDateTime,
  plural,
  requestStatus,
  serviceType,
} from '@/constants/labels'

/**
 * Из списка без открытия должны читаться четыре вещи: статус, число
 * откликов, срок и вид услуги. Именно этого не хватало в макете —
 * карточки выглядели одинаково и не подсказывали, где ждут действия.
 */
const props = defineProps({
  request: { type: Object, required: true },
})

const status = computed(() => requestStatus(props.request.status))
const service = computed(() => serviceType(props.request.service_type))

const responsesLabel = computed(() => {
  const n = props.request.responses_count
  if (!n) return 'Откликов нет'
  return `${n} ${plural(n, ['отклик', 'отклика', 'откликов'])}`
})
</script>

<template>
  <RouterLink
    class="card"
    :to="{ name: 'request', params: { id: request.id } }"
    :class="{ 'card--quiet': request.status === 'rejected' }"
  >
    <div class="card__top">
      <span class="card__num">№{{ request.public_number }}</span>
      <StatusBadge :label="status.label" :tone="status.tone" :icon="status.icon" />
    </div>

    <h3 class="card__service">
      <AppIcon :name="service.icon" :size="20" />
      {{ service.label }}
    </h3>

    <p class="card__client">{{ request.client_name }}</p>

    <dl class="card__meta">
      <div class="card__row">
        <dt><AppIcon name="clock" :size="15" /><span class="visually-hidden">Дата съёмки</span></dt>
        <dd>{{ request.event_date ? formatDate(request.event_date) : 'дата не указана' }}</dd>
      </div>
      <div class="card__row">
        <dt><AppIcon name="arrow-right" :size="15" /><span class="visually-hidden">Отклики</span></dt>
        <dd :class="{ 'card__zero': !request.responses_count }">{{ responsesLabel }}</dd>
      </div>
    </dl>

    <p class="card__created">Создана {{ formatDateTime(request.created_at) }}</p>
  </RouterLink>
</template>

<style scoped>
.card {
  display: grid;
  gap: var(--space-2);
  align-content: start;
  padding: var(--space-3);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--paper);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s var(--ease), transform 0.15s var(--ease);
}

.card:hover {
  border-color: var(--ink);
  transform: translateY(-2px);
}

.card--quiet {
  opacity: 0.62;
}

.card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.card__num {
  font-family: var(--font-display);
  font-size: var(--step--1);
  font-weight: 700;
  color: var(--muted);
}

.card__service {
  display: flex;
  align-items: center;
  gap: 0.45em;
  margin: 0;
  font-size: var(--step-1);
}

.card__service :deep(svg) {
  color: var(--red);
  flex: none;
}

.card__client {
  margin: 0;
  color: var(--ink-soft);
}

.card__meta {
  display: grid;
  gap: var(--space-1);
  margin: 0;
  font-size: var(--step--1);
}

.card__row {
  display: flex;
  align-items: center;
  gap: 0.45em;
}

.card__row dt,
.card__row dd {
  margin: 0;
  display: flex;
  align-items: center;
}

.card__row dt :deep(svg) {
  color: var(--muted);
}

.card__zero {
  color: var(--muted);
}

.card__created {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}
</style>
