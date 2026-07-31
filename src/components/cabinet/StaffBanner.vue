<script setup>
import { useAuthStore } from '@/stores/auth'

/**
 * Явный признак, что человек смотрит с повышенными правами.
 *
 * Без него случайные удаления неизбежны: экраны у контент-менеджера
 * те же, что у участника, просто с дополнительными кнопками.
 */
const auth = useAuthStore()
</script>

<template>
  <div v-if="auth.isStaff" class="staff">
    <span class="staff__dot" aria-hidden="true" />
    {{ auth.isAdmin ? 'Режим администратора' : 'Режим контент-менеджера' }}
    <span class="staff__hint">— вам доступны действия модерации</span>
  </div>
</template>

<style scoped>
.staff {
  display: flex;
  align-items: center;
  gap: 0.5em;
  padding: 0.45rem var(--space-3);
  background: var(--ink);
  color: var(--paper);
  font-family: var(--font-display);
  font-size: var(--step--1);
  font-weight: 700;
}

.staff__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--red);
  flex: none;
}

.staff__hint {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
}

@media (max-width: 560px) {
  .staff__hint {
    display: none;
  }
}
</style>
