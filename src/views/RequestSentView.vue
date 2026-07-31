<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Экрана не было вовсе: клиент нажимал кнопку и логика обрывалась.
 * Здесь номер заявки (на него человек ссылается при звонке) и честное
 * объяснение, что будет дальше — уведомлений на почту у нас нет,
 * поэтому не обещаем письмо.
 */
const route = useRoute()
const number = computed(() => route.params.number)
</script>

<template>
  <main class="done">
    <div class="shell done__inner">
      <span class="done__mark"><AppIcon name="check" :size="34" /></span>

      <h1 class="done__title">Заявка №{{ number }} принята</h1>

      <p class="done__lead">
        Мы позвоним по указанному номеру в течение рабочего дня и уточним
        детали. Письма не отправляем — связь только по телефону.
      </p>

      <div class="done__note">
        <p class="done__noteTitle">Запишите номер заявки</p>
        <p class="done__noteText">
          Отследить статус на сайте нельзя: аккаунт для этого не нужен.
          Если хотите что-то уточнить или отменить, позвоните и назовите
          номер <strong>{{ number }}</strong>.
        </p>
      </div>

      <div class="done__actions">
        <RouterLink class="done__primary" to="/">На главную</RouterLink>
        <a class="done__link" href="tel:+79991234567">Позвонить: +7 999 123-45-67</a>
      </div>
    </div>
  </main>
</template>

<style scoped>
.done {
  display: grid;
  align-content: center;
  min-height: 80vh;
  padding-block: var(--space-6);
}

.done__inner {
  display: grid;
  gap: var(--space-3);
  justify-items: start;
  max-width: 60ch;
}

.done__mark {
  display: grid;
  place-items: center;
  width: 62px;
  height: 62px;
  border-radius: 50%;
  background: var(--red);
  color: var(--paper);
}

.done__title {
  font-size: var(--step-3);
}

.done__lead {
  margin: 0;
  font-size: var(--step-1);
  color: var(--ink-soft);
}

.done__note {
  padding: var(--space-3);
  border-left: 3px solid var(--red);
  background: var(--surface);
}

.done__noteTitle {
  margin: 0 0 var(--space-1);
  font-family: var(--font-display);
  font-weight: 700;
}

.done__noteText {
  margin: 0;
  font-size: var(--step--1);
  color: var(--ink-soft);
}

.done__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.done__primary {
  display: inline-flex;
  align-items: center;
  min-height: 50px;
  padding-inline: var(--space-4);
  border-radius: var(--radius);
  background: var(--ink);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  text-decoration: none;
}

.done__primary:hover {
  background: var(--red);
}

.done__link {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  border-bottom: 1.5px solid var(--line);
}

.done__link:hover {
  border-color: var(--red);
}
</style>
