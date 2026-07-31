<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Правки макета:
 *  — сетка разъезжалась: пять позиций в раскладке 3+2, крайняя правая
 *    обрезалась краем секции. Теперь auto-fit с равными колонками;
 *  — под каждой ценой строка условий: «2000 руб/час» вызывало больше
 *    вопросов, чем отвечало, и каждая заявка всё равно шла в переписку;
 *  — иконки из одного набора и одного цвета;
 *  — секция на чёрном фоне без фотографии: деньги отделены от остального,
 *    а на фото здания цифры не читались.
 */
const items = [
  {
    icon: 'photo',
    title: 'Фотосессия',
    price: '2000 ₽/час',
    terms: 'До 50 обработанных кадров, отдаём за 5 рабочих дней',
  },
  {
    icon: 'video',
    title: 'Видеоролик с мероприятия',
    price: 'от 7000 ₽',
    terms: 'До 3 минут, монтаж и цветокоррекция включены',
  },
  {
    icon: 'article',
    title: 'Написание текста',
    price: '800 ₽',
    terms: 'До 3000 знаков, одна правка по замечаниям',
  },
  {
    icon: 'design',
    title: 'Афиша или баннер',
    price: 'от 2500 ₽',
    terms: 'Два макета на выбор, исходники по запросу',
  },
  {
    icon: 'video',
    title: 'Музыкальный клип',
    price: 'от 8000 ₽',
    terms: 'Съёмочный день, сценарий обсуждаем отдельно',
  },
]

const notes = [
  'Бронируйте не позднее чем за 5 дней до съёмки.',
  'Для студенческих объединений вуза — по договорённости.',
  'Отмена без потерь — за сутки до съёмки.',
]
</script>

<template>
  <section class="section price">
    <div class="shell">
      <h2 class="price__title drop-cap">Прайс-лист</h2>

      <ul class="price__grid">
        <li v-for="item in items" :key="item.title" class="row">
          <AppIcon :name="item.icon" :size="28" />
          <h3 class="row__title">{{ item.title }}</h3>
          <p class="row__price">{{ item.price }}</p>
          <p class="row__terms">{{ item.terms }}</p>
        </li>
      </ul>

      <ul class="price__notes">
        <li v-for="note in notes" :key="note">{{ note }}</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.price {
  background: var(--night);
  color: rgba(255, 255, 255, 0.9);
}

.price__title {
  font-size: var(--step-3);
  color: var(--paper);
  margin-bottom: var(--space-4);
}

.price__grid {
  display: grid;
  gap: var(--space-3);
  margin: 0 0 var(--space-4);
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
}

.row {
  display: grid;
  gap: var(--space-1);
  align-content: start;
  padding: var(--space-3);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: var(--radius-lg);
}

.row :deep(svg) {
  color: var(--red);
  margin-bottom: var(--space-1);
}

.row__title {
  font-size: var(--step-0);
  color: var(--paper);
  margin: 0;
}

.row__price {
  margin: 0;
  font-family: var(--font-display);
  font-size: var(--step-2);
  font-weight: 800;
  color: var(--paper);
}

.row__terms {
  margin: 0;
  font-size: var(--step--1);
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.6);
}

.price__notes {
  display: grid;
  gap: var(--space-1);
  margin: 0;
  padding-left: 1.1em;
  font-size: var(--step--1);
  color: rgba(255, 255, 255, 0.62);
}
</style>
