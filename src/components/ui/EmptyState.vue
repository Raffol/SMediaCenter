<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Пустое состояние — приглашение к действию, а не сообщение о пустоте.
 * В макете их не было вовсе, и новый участник видел просто пустоту.
 */
defineProps({
  title: { type: String, required: true },
  hint: { type: String, default: '' },
})
</script>

<template>
  <div class="empty">
    <AppIcon name="alert" :size="28" />
    <p class="empty__title">{{ title }}</p>
    <p v-if="hint" class="empty__hint">{{ hint }}</p>
    <div class="empty__action"><slot /></div>
  </div>
</template>

<style scoped>
.empty {
  display: grid;
  justify-items: center;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-3);
  border: 1px dashed var(--line);
  border-radius: var(--radius-lg);
  text-align: center;
  color: var(--muted);
}

.empty :deep(svg) {
  color: var(--red);
}

.empty__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step-1);
  color: var(--ink);
}

.empty__hint {
  margin: 0;
  max-width: 42ch;
}

.empty__action:empty {
  display: none;
}
</style>
