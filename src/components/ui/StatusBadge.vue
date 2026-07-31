<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Статус текстом и иконкой, а не одним цветом.
 *
 * Цвет здесь дублирующий сигнал: дальтонизм плюс серый интерфейс на
 * плохом мониторе — и различие «в работе / отклонена» исчезает совсем.
 */
defineProps({
  label: { type: String, required: true },
  tone: { type: String, default: 'wait' }, // wait | live | ok | off
  icon: { type: String, default: '' },
})
</script>

<template>
  <span class="badge" :class="`badge--${tone}`">
    <AppIcon v-if="icon" :name="icon" :size="14" />
    {{ label }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35em;
  padding: 0.22em 0.6em;
  border-radius: var(--radius);
  font-family: var(--font-display);
  font-size: var(--step--1);
  font-weight: 700;
  line-height: 1.4;
  white-space: nowrap;
}

.badge--wait {
  background: #fff2d6;
  color: #8a5a00;
}

.badge--live {
  background: #e0eaff;
  color: #1a3f9e;
}

.badge--ok {
  background: #ddf3e4;
  color: #14663a;
}

.badge--off {
  background: #f0f0f0;
  color: var(--muted);
}
</style>
