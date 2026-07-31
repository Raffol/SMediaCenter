<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Четыре услуги — те же категории, что и пометки участников
 * (Tag.service_type на бэкенде). Клик ведёт в форму с предвыбранным видом.
 *
 * Секция на чистом фоне намеренно: в третьем варианте макета фотография
 * была под каждым блоком, и ни один не выделялся.
 */
const services = [
  { icon: 'photo', label: 'Фотосъёмка', note: 'Мероприятия, портреты, репортаж' },
  { icon: 'video', label: 'Видеосъёмка', note: 'Ролики с событий, интервью, клипы' },
  { icon: 'article', label: 'Написание статей', note: 'Новости, интервью, посты' },
  { icon: 'design', label: 'Дизайн', note: 'Афиши, баннеры, оформление' },
]
</script>

<template>
  <section class="section services">
    <div class="shell">
      <h2 class="services__title drop-cap">Чем мы занимаемся</h2>
      <ul class="services__grid">
        <li v-for="s in services" :key="s.label" class="card">
          <AppIcon :name="s.icon" :size="34" />
          <h3 class="card__label">{{ s.label }}</h3>
          <p class="card__note">{{ s.note }}</p>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.services__title {
  font-size: var(--step-3);
  margin-bottom: var(--space-4);
}

.services__grid {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
}

.card {
  display: grid;
  gap: var(--space-2);
  align-content: start;
  padding: var(--space-4);
  background: var(--surface);
  border-radius: var(--radius-lg);
}

.card :deep(svg) {
  color: var(--red);
}

.card__label {
  font-size: var(--step-1);
  margin: 0;
}

.card__note {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}
</style>
