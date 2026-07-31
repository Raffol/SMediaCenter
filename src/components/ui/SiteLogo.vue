<script setup>
/**
 * Треугольник play — отдельный знак перед названием, а не замена буквы.
 *
 * Раньше он стоял НА месте «С», и название читалось как «туденческий».
 * Идея из макета была в том, чтобы треугольник напоминал «С», но в
 * реальном шрифте это не работает: буква просто пропадает.
 *
 * mark=false убирает треугольник, если он где-то не нужен.
 */
defineProps({
  variant: { type: String, default: 'dark' }, // dark | light
  stacked: { type: Boolean, default: false },
  mark: { type: Boolean, default: true },
})
</script>

<template>
  <span class="logo" :class="[`logo--${variant}`, { 'logo--stacked': stacked }]">
    <svg
      v-if="mark"
      class="logo__mark"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M5 3.2 21 12 5 20.8Z" fill="currentColor" />
    </svg>

    <span class="logo__text">
      <span class="logo__line">Студенческий</span>
      <span class="logo__line">МедиаЦентр</span>
    </span>
  </span>
</template>

<style scoped>
.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  font-family: var(--font-display);
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.02em;
  text-decoration: none;
  white-space: nowrap;
}

.logo__mark {
  width: 0.78em;
  height: 0.78em;
  flex: none;
  color: var(--red);
  /* Оптическая посадка: треугольник кажется выше строки */
  transform: translateY(0.03em);
}

.logo__text {
  display: flex;
  gap: 0.3em;
}

.logo--stacked {
  align-items: center;
}

.logo--stacked .logo__text {
  flex-direction: column;
  gap: 0.08em;
}

/* В два ряда переносы внутри строк не нужны — они уже разбиты вручную */
.logo--stacked .logo__line {
  display: block;
}

.logo--dark {
  color: var(--ink);
}

.logo--light {
  color: var(--paper);
}
</style>