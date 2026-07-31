<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { formatDate } from '@/constants/labels'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const notFound = ref(false)

async function load(slug) {
  loading.value = true
  notFound.value = false
  try {
    const { data } = await api.get(`/api/posts/${slug}/`)
    post.value = data
    document.title = `${data.title} — Студенческий МедиаЦентр`
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.params.slug))
watch(() => route.params.slug, load)
</script>

<template>
  <main class="section">
    <div class="shell narrow">
      <SkeletonCard v-if="loading" :count="1" />

      <EmptyState
        v-else-if="notFound"
        title="Публикация не найдена"
        hint="Возможно, её сняли с публикации или ссылка устарела."
      >
        <RouterLink class="link" :to="{ name: 'posts' }">Все публикации</RouterLink>
      </EmptyState>

      <article v-else-if="post">
        <RouterLink class="back" :to="{ name: 'posts' }">
          <AppIcon name="arrow-right" :size="16" /> Все публикации
        </RouterLink>

        <p class="meta">
          {{ formatDate(post.published_at) }}
          <span v-if="post.author"> · {{ post.author.full_name }}</span>
        </p>

        <h1 class="title">{{ post.title }}</h1>

        <img
          v-if="post.cover_path"
          class="cover"
          :src="post.cover_path"
          :alt="post.cover_alt || post.title"
          decoding="async"
        />

        <div class="body">{{ post.body }}</div>
      </article>
    </div>
  </main>
</template>

<style scoped>
.narrow {
  max-width: 46rem;
}

.back {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  min-height: 44px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  color: var(--muted);
  text-decoration: none;
}

.back :deep(svg) {
  transform: rotate(180deg);
}

.back:hover {
  color: var(--ink);
}

.meta {
  margin: var(--space-2) 0 var(--space-1);
  font-size: var(--step--1);
  color: var(--muted);
}

.title {
  font-size: var(--step-3);
  margin-bottom: var(--space-4);
}

.cover {
  width: 100%;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

/* Текст приходит как обычная строка. Если контент-менеджеру понадобится
   разметка, подключите санитайзер (DOMPurify) — v-html без него
   открывает XSS через тело поста. */
.body {
  white-space: pre-line;
  font-size: var(--step-1);
  line-height: 1.7;
  color: var(--ink-soft);
}

.link {
  color: var(--red);
}
</style>
