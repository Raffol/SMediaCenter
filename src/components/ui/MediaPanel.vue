<script setup>
/**
 * Фотография с затемнением под текстом.
 *
 * Главная правка макета: белый текст лежал прямо на листве, контраст
 * местами падал до 1.5:1. Здесь затемнение обязательно и берётся из
 * токенов, поэтому одинаково во всех секциях.
 *
 * alt обязателен: без него скринридер читает имя файла.
 */
defineProps({
  src: { type: String, required: true },
  alt: { type: String, required: true },
  scrim: { type: String, default: 'scrim' }, // scrim-soft | scrim | scrim-hard
  grayscale: { type: Boolean, default: false },
  minHeight: { type: String, default: '60vh' },
})
</script>

<template>
  <div class="media" :style="{ '--panel-min': minHeight }">
    <img
      class="media__img"
      :class="{ 'media__img--gray': grayscale }"
      :src="src"
      :alt="alt"
      loading="lazy"
      decoding="async"
    />
    <div class="media__scrim" :style="{ background: `var(--${scrim})` }" />
    <div class="media__body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.media {
  position: relative;
  display: grid;
  min-height: var(--panel-min);
  isolation: isolate;
}

.media__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -2;
}

.media__img--gray {
  filter: grayscale(1) contrast(1.05);
}

.media__scrim {
  position: absolute;
  inset: 0;
  z-index: -1;
}

.media__body {
  display: grid;
  align-content: center;
  width: 100%;
  padding-block: var(--space-6);
  color: var(--paper);
}
</style>
