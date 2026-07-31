<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

// Кнопка «наверх» после второго экрана: лендинг высокий
const showTop = ref(false)

function onScroll() {
  showTop.value = window.scrollY > window.innerHeight * 1.5
}

function toTop() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' })
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <AppHeader />
  <RouterView />
  <AppFooter />

  <Transition name="fade">
    <button v-if="showTop" class="top" type="button" @click="toTop">
      <AppIcon name="arrow-up" :size="22" />
      <span class="visually-hidden">Наверх</span>
    </button>
  </Transition>
</template>

<style scoped>
.top {
  position: fixed;
  right: var(--space-3);
  bottom: var(--space-3);
  z-index: 40;
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 0;
  border-radius: 50%;
  background: var(--ink);
  color: var(--paper);
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.top:hover {
  background: var(--red);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s var(--ease);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
