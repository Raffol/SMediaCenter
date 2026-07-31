<script setup>
/** Скелетон вместо спиннера: воспринимается быстрее и не дёргает вёрстку. */
defineProps({ count: { type: Number, default: 3 } })
</script>

<template>
  <div class="skel">
    <div v-for="n in count" :key="n" class="skel__card">
      <div class="skel__cover" />
      <div class="skel__line skel__line--wide" />
      <div class="skel__line" />
    </div>
  </div>
</template>

<style scoped>
.skel {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.skel__card {
  display: grid;
  gap: var(--space-2);
}

.skel__cover,
.skel__line {
  background: linear-gradient(90deg, var(--surface) 25%, #e8e8e8 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
  border-radius: var(--radius);
}

.skel__cover {
  aspect-ratio: 3 / 2;
}

.skel__line {
  height: 0.9rem;
  width: 60%;
}

.skel__line--wide {
  width: 90%;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
