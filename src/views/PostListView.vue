<script setup>
import { onMounted, ref, watch } from 'vue'
import { api } from '@/api/client'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import { formatDate } from '@/constants/labels'

const items = ref([])
const total = ref(0)
const loading = ref(true)
const category = ref('')
const offset = ref(0)
const PAGE = 12

const tabs = [
  { value: '', label: 'Всё' },
  { value: 'news', label: 'Новости' },
  { value: 'work', label: 'Работы' },
]

async function load({ append = false } = {}) {
  loading.value = true
  try {
    const { data } = await api.get('/api/posts/', {
      params: { category: category.value || undefined, limit: PAGE, offset: offset.value },
    })
    items.value = append ? [...items.value, ...data.items] : data.items
    total.value = data.total
  } catch {
    if (!append) items.value = []
  } finally {
    loading.value = false
  }
}

watch(category, () => {
  offset.value = 0
  load()
})

onMounted(load)
</script>

<template>
  <main class="section">
    <div class="shell">
      <h1 class="title drop-cap">Публикации</h1>

      <div class="tabs" role="group" aria-label="Категория">
        <button
          v-for="t in tabs"
          :key="t.value"
          class="tabs__btn"
          type="button"
          :aria-pressed="category === t.value"
          :class="{ 'tabs__btn--on': category === t.value }"
          @click="category = t.value"
        >
          {{ t.label }}
        </button>
      </div>

      <SkeletonCard v-if="loading && !items.length" :count="6" />

      <EmptyState
        v-else-if="!items.length"
        title="Здесь пока пусто"
        hint="Публикации появятся, как только контент-менеджер выпустит первый материал."
      />

      <template v-else>
        <ul class="grid">
          <li v-for="p in items" :key="p.id">
            <RouterLink class="post" :to="{ name: 'post', params: { slug: p.slug } }">
              <div class="post__cover">
                <img
                  v-if="p.cover_thumb_path"
                  :src="p.cover_thumb_path"
                  :alt="p.cover_alt || p.title"
                  loading="lazy"
                  decoding="async"
                />
              </div>
              <p class="post__date">{{ formatDate(p.published_at) }}</p>
              <h2 class="post__title">{{ p.title }}</h2>
              <p v-if="p.excerpt" class="post__excerpt">{{ p.excerpt }}</p>
            </RouterLink>
          </li>
        </ul>

        <button
          v-if="items.length < total"
          class="more"
          type="button"
          :disabled="loading"
          @click="offset += PAGE; load({ append: true })"
        >
          {{ loading ? 'Загружаем…' : 'Показать ещё' }}
        </button>
      </template>
    </div>
  </main>
</template>

<style scoped>
.title {
  font-size: var(--step-3);
  margin-bottom: var(--space-3);
}

.tabs {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
}

.tabs__btn {
  min-height: 44px;
  padding-inline: var(--space-3);
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  color: var(--muted);
  cursor: pointer;
}

.tabs__btn--on {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
}

.grid {
  display: grid;
  gap: var(--space-4) var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.post {
  display: grid;
  gap: var(--space-1);
  text-decoration: none;
  color: inherit;
}

.post__cover {
  aspect-ratio: 3 / 2;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.post__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s var(--ease);
}

.post:hover img {
  transform: scale(1.03);
}

.post__date {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}

.post__title {
  font-size: var(--step-1);
  margin: 0;
}

.post:hover .post__title {
  color: var(--red);
}

.post__excerpt {
  margin: 0;
  font-size: var(--step--1);
  color: var(--ink-soft);
}

.more {
  display: block;
  margin: var(--space-5) auto 0;
  min-height: 48px;
  padding-inline: var(--space-4);
  border: 1.5px solid var(--ink);
  border-radius: var(--radius);
  background: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  cursor: pointer;
}

.more:hover:not(:disabled) {
  background: var(--ink);
  color: var(--paper);
}
</style>
