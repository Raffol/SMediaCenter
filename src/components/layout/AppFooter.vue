<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'
import SiteLogo from '@/components/ui/SiteLogo.vue'

/**
 * В макете подвал лежал прямо на фотографии — адрес и режим работы
 * не читались вообще. Здесь он на плотном фоне, а контакты кликабельны:
 * с телефона звонок в одно касание.
 */
const contacts = {
  address: 'г. Иркутск, ул. Лермонтова, 83',
  addressNote: 'корпус и кабинет — уточните перед визитом',
  hours: 'Пн–Пт, 9:30–17:30',
  phone: '+7 999 123-45-67',
  phoneHref: 'tel:+79991234567',
  email: 'media@example.ru',
}
</script>

<template>
  <footer class="foot">
    <div class="shell foot__inner">
      <div class="foot__brand">
        <SiteLogo variant="light" stacked />
      </div>

      <ul class="foot__list">
        <li class="foot__item">
          <AppIcon name="pin" :size="18" />
          <span>
            {{ contacts.address }}
            <small class="foot__note">{{ contacts.addressNote }}</small>
          </span>
        </li>
        <li class="foot__item">
          <AppIcon name="clock" :size="18" />
          <span>{{ contacts.hours }}</span>
        </li>
        <li class="foot__item">
          <AppIcon name="phone" :size="18" />
          <a :href="contacts.phoneHref">{{ contacts.phone }}</a>
        </li>
        <li class="foot__item">
          <AppIcon name="mail" :size="18" />
          <a :href="`mailto:${contacts.email}`">{{ contacts.email }}</a>
        </li>
      </ul>

      <div class="foot__side">
        <a
          class="foot__vk tap"
          href="https://vk.com"
          target="_blank"
          rel="noopener noreferrer"
        >
          Группа Вконтакте
          <AppIcon name="arrow-right" :size="18" />
        </a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.foot {
  background: var(--night);
  color: rgba(255, 255, 255, 0.82);
  padding-block: var(--space-5);
  font-size: var(--step--1);
}

.foot__inner {
  display: grid;
  gap: var(--space-4);
}

.foot__brand {
  font-size: var(--step-1);
}

.foot__list {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}

.foot__item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
}

.foot__item :deep(svg) {
  flex: none;
  margin-top: 0.15em;
  color: var(--red);
}

.foot__item a {
  color: var(--paper);
  text-decoration: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.foot__item a:hover {
  border-color: var(--red);
}

.foot__note {
  display: block;
  color: rgba(255, 255, 255, 0.5);
}

.foot__vk {
  display: inline-flex;
  gap: var(--space-2);
  justify-content: flex-start;
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--paper);
  text-decoration: none;
}

.foot__vk:hover {
  color: var(--red);
}

@media (min-width: 900px) {
  .foot__inner {
    grid-template-columns: 1fr 1.4fr auto;
    align-items: start;
    gap: var(--space-5);
  }
}
</style>
