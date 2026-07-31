<script setup>
/**
 * Пометка участника. Цвет приходит из базы, чтобы контент-менеджер
 * менял его в админке без правки кода.
 */
defineProps({
  name: { type: String, required: true },
  color: { type: String, default: '#E11D2E' },
})
</script>

<template>
  <span class="chip" :style="{ '--chip': color }">{{ name }}</span>
</template>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  padding: 0.2em 0.6em;
  border: 1.5px solid var(--chip);
  border-radius: 999px;
  font-family: var(--font-display);
  font-size: var(--step--1);
  font-weight: 700;
  line-height: 1.4;
  color: var(--chip);
  white-space: nowrap;
}
</style>
