<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import TagChip from '@/components/ui/TagChip.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'

const route = useRoute()
const member = ref(null)
const loading = ref(true)
const notFound = ref(false)

async function load(id) {
  loading.value = true
  notFound.value = false
  try {
    const { data } = await api.get(`/api/members/${id}/`)
    member.value = data
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.params.id))
watch(() => route.params.id, load)
</script>

<template>
  <main class="section">
    <div class="shell">
      <SkeletonCard v-if="loading" :count="1" />

      <EmptyState
        v-else-if="notFound"
        title="Участник не найден"
        hint="Возможно, профиль скрыт или ссылка устарела."
      />

      <template v-else-if="member">
        <div class="head">
          <div class="head__frame">
            <img
              v-if="member.avatar_path"
              :src="member.avatar_path"
              :alt="`Портрет: ${member.full_name}`"
              decoding="async"
            />
          </div>

          <div class="head__body">
            <h1 class="head__name">{{ member.full_name }}</h1>

            <ul v-if="member.tags.length" class="head__tags">
              <li v-for="t in member.tags" :key="t.id">
                <TagChip :name="t.name" :color="t.color" />
              </li>
            </ul>

            <p v-if="member.bio" class="head__bio">{{ member.bio }}</p>

            <p v-if="member.completed_count" class="head__count">
              Выполнено заявок: <strong>{{ member.completed_count }}</strong>
            </p>
          </div>
        </div>

        <section class="works">
          <h2 class="works__title">Работы</h2>

          <EmptyState
            v-if="!member.works.length"
            title="Работ пока нет"
            hint="Здесь появятся публикации, отмеченные как работа в портфолио."
          />

          <ul v-else class="works__grid">
            <li v-for="w in member.works" :key="w.id">
              <RouterLink class="work" :to="{ name: 'post', params: { slug: w.slug } }">
                <div class="work__cover">
                  <img
                    v-if="w.cover_thumb_path"
                    :src="w.cover_thumb_path"
                    :alt="w.cover_alt || w.title"
                    loading="lazy"
                    decoding="async"
                  />
                </div>
                <h3 class="work__title">{{ w.title }}</h3>
              </RouterLink>
            </li>
          </ul>
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
.head {
  display: grid;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.head__frame {
  width: 180px;
  aspect-ratio: 1;
  border-radius: 50%;
  overflow: hidden;
  background: var(--surface);
}

.head__frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.head__body {
  display: grid;
  gap: var(--space-2);
  align-content: start;
}

.head__name {
  font-size: var(--step-3);
}

.head__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin: 0;
  padding: 0;
  list-style: none;
}

.head__bio {
  margin: 0;
  max-width: 60ch;
  color: var(--ink-soft);
}

.head__count {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}

.works__title {
  font-size: var(--step-2);
  margin-bottom: var(--space-3);
}

.works__grid {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.work {
  display: grid;
  gap: var(--space-2);
  text-decoration: none;
  color: inherit;
}

.work__cover {
  aspect-ratio: 3 / 2;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
}

.work__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.work__title {
  font-size: var(--step-0);
  margin: 0;
}

.work:hover .work__title {
  color: var(--red);
}

@media (min-width: 760px) {
  .head {
    grid-template-columns: auto 1fr;
    align-items: start;
    gap: var(--space-5);
  }
}
</style>
