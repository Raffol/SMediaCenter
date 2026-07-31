<script setup>
/**
 * Один набор иконок на весь проект.
 *
 * В макете иконки были из разных источников: фото/видео/статьи чёрные
 * контурные, «Дизайн» — сиреневый монитор явно откуда-то ещё, в прайсе
 * часть красная, часть белая. Здесь все нарисованы одним штрихом и
 * наследуют currentColor, поэтому цвет задаётся снаружи.
 */
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 24 },
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <template v-if="name === 'photo'">
      <path d="M3 8.5A2 2 0 0 1 5 6.5h1.6l1.2-2h8.4l1.2 2H19a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
      <circle cx="12" cy="13" r="3.6" />
    </template>

    <template v-else-if="name === 'video'">
      <rect x="2.5" y="6.5" width="13" height="11" rx="2" />
      <path d="M15.5 11l6-3v8l-6-3z" />
    </template>

    <template v-else-if="name === 'article'">
      <path d="M5 3.5h9l5 5v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-16a1 1 0 0 1 1-1Z" />
      <path d="M14 3.5v5h5M8 13h8M8 17h5" />
    </template>

    <template v-else-if="name === 'design'">
      <rect x="2.5" y="4.5" width="19" height="12" rx="2" />
      <path d="M9 20.5h6M12 16.5v4M8 11l2.5 2.5L16 8" />
    </template>

    <template v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </template>

    <template v-else-if="name === 'pin'">
      <path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11Z" />
      <circle cx="12" cy="10" r="2.6" />
    </template>

    <template v-else-if="name === 'phone'">
      <path d="M6 3.5h3l1.5 4-2 1.5a11 11 0 0 0 6 6l1.5-2 4 1.5v3a2 2 0 0 1-2 2A16 16 0 0 1 4 5.5a2 2 0 0 1 2-2Z" />
    </template>

    <template v-else-if="name === 'mail'">
      <rect x="2.5" y="5.5" width="19" height="13" rx="2" />
      <path d="M3 7l9 6 9-6" />
    </template>

    <template v-else-if="name === 'arrow-up'">
      <path d="M12 19V5M6 11l6-6 6 6" />
    </template>

    <template v-else-if="name === 'arrow-right'">
      <path d="M4 12h15M13 6l6 6-6 6" />
    </template>

    <template v-else-if="name === 'menu'">
      <path d="M4 7h16M4 12h16M4 17h16" />
    </template>

    <template v-else-if="name === 'close'">
      <path d="M6 6l12 12M18 6L6 18" />
    </template>

    <template v-else-if="name === 'check'">
      <path d="M4 12.5l5 5L20 6.5" />
    </template>

    <template v-else-if="name === 'alert'">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 8v4.5M12 15.8v.2" />
    </template>
  </svg>
</template>
