<script setup>
import MediaPanel from '@/components/ui/MediaPanel.vue'
</script>

<template>
  <section id="o-nas">
    <MediaPanel
      src="/img/team.jpg"
      alt="Участники медиацентра на групповом снимке во дворе"
      scrim="scrim-hard"
      min-height="min(70vh, 620px)"
    >
      <div class="shell about">
        <h2 class="about__title drop-cap">Кто мы</h2>
        <!-- В макете: «объединение, дарящая эмоции». Объединение среднего
             рода — «дарящее». Для тех, кто продаёт тексты, такая опечатка
             самая дорогая на странице. -->
        <p class="about__text">
          Студенческое объединение с дружеской атмосферой, дарящее эмоции
          через фотографию, видеоролики и красивые тексты.
        </p>
      </div>
    </MediaPanel>
  </section>
</template>

<style scoped>
.about {
  display: grid;
  gap: var(--space-3);
  max-width: 60ch;
}

.about__title {
  font-size: var(--step-3);
}

.about__text {
  margin: 0;
  font-size: var(--step-2);
  font-family: var(--font-display);
  font-weight: 600;
  line-height: 1.3;
}
</style>
