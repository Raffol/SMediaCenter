<script setup>
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

/**
 * Секции не было в макете вовсе, хотя работы — главный аргумент
 * медиацентра. Стоит до прайса: сначала показываем, что умеем,
 * потом называем цену.
 */
const posts = ref([])
const loading = ref(true)

const dateFmt = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

function formatDate(value) {
  return value ? dateFmt.format(new Date(value)) : ''
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/posts/', { params: { limit: 3 } })
    posts.value = data.items
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section id="raboty" class="section feed">
    <div class="shell">
      <div class="feed__head">
        <h2 class="feed__title drop-cap">Последние работы</h2>
        <RouterLink class="feed__all" :to="{ name: 'posts' }">
          Все публикации
          <AppIcon name="arrow-right" :size="18" />
        </RouterLink>
      </div>

      <SkeletonCard v-if="loading" :count="3" />

      <EmptyState
        v-else-if="!posts.length"
        title="Публикаций пока нет"
        hint="Здесь появятся съёмки и материалы, как только выйдет первая публикация."
      />

      <ul v-else class="feed__grid">
        <li v-for="p in posts" :key="p.id" class="post">
          <RouterLink class="post__link" :to="{ name: 'post', params: { slug: p.slug } }">
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
            <h3 class="post__title">{{ p.title }}</h3>
            <p v-if="p.excerpt" class="post__excerpt">{{ p.excerpt }}</p>
          </RouterLink>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.feed {
  background: var(--surface);
}

.feed__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.feed__title {
  font-size: var(--step-3);
}

.feed__all {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  min-height: 44px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  text-decoration: none;
}

.feed__all:hover {
  color: var(--red);
}

.feed__grid {
  display: grid;
  gap: var(--space-4) var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.post__link {
  display: grid;
  gap: var(--space-1);
  text-decoration: none;
  color: inherit;
}

.post__cover {
  aspect-ratio: 3 / 2;
  background: #e6e6e6;
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

.post__link:hover img {
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

.post__link:hover .post__title {
  color: var(--red);
}

.post__excerpt {
  margin: 0;
  font-size: var(--step--1);
  color: var(--ink-soft);
}
</style>
