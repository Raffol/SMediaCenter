<script setup>
import MediaPanel from '@/components/ui/MediaPanel.vue'
import SiteLogo from '@/components/ui/SiteLogo.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
</script>

<template>
  <MediaPanel
    src="/img/hero.jpg"
    alt="Команда медиацентра снимает мероприятие на улице"
    scrim="scrim"
    grayscale
    min-height="min(88vh, 780px)"
  >
    <div class="shell hero">
      <p class="eyebrow hero__eyebrow">Иркутск · с 2019 года</p>
      <h1 class="hero__title">
        <SiteLogo variant="light" stacked />
      </h1>
      <p class="hero__lead">
        Снимаем события, монтируем ролики и пишем тексты для студенческих
        проектов и подразделений вуза.
      </p>
      <div class="hero__actions">
        <a class="hero__cta" href="#zayavka">
          Оставить заявку
          <AppIcon name="arrow-right" :size="20" />
        </a>
        <a class="hero__link" href="#raboty">Смотреть работы</a>
      </div>
    </div>
  </MediaPanel>
</template>

<style scoped>
.hero {
  display: grid;
  gap: var(--space-3);
  justify-items: start;
}

.hero__eyebrow {
  color: rgba(255, 255, 255, 0.7);
}

.hero__title {
  font-size: var(--step-4);
  margin: 0;
}

.hero__lead {
  max-width: 38ch;
  margin: 0;
  font-size: var(--step-1);
  color: rgba(255, 255, 255, 0.92);
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.hero__cta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 52px;
  padding-inline: var(--space-4);
  border-radius: var(--radius);
  background: var(--red);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 800;
  text-decoration: none;
  transition: background 0.2s var(--ease);
}

.hero__cta:hover {
  background: var(--red-dark);
}

.hero__link {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  color: var(--paper);
  text-decoration: none;
  border-bottom: 1.5px solid rgba(255, 255, 255, 0.45);
}

.hero__link:hover {
  border-color: var(--red);
}
</style>
