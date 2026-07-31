<script setup>
import { onMounted, ref } from 'vue'
import { api } from '@/api/client'
import TagChip from '@/components/ui/TagChip.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

/**
 * Правки макета:
 *  — «lorem» заменён настоящими людьми из API;
 *  — вертикальное «Штатники» было продублировано и читалось как ошибка;
 *    теперь один горизонтальный заголовок;
 *  — под именем показываются пометки — так секция связана с системой
 *    профилей, а не просто набор картинок.
 */
const members = ref([])
const loading = ref(true)
const failed = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/members/')
    members.value = data
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section id="komanda" class="section team">
    <div class="shell">
      <h2 class="team__title drop-cap">Штатники</h2>
      <p class="team__lead">Кто снимает, монтирует и пишет.</p>

      <SkeletonCard v-if="loading" :count="4" />

      <EmptyState
        v-else-if="failed || !members.length"
        title="Список пока пуст"
        hint="Как только контент-менеджер добавит участников, они появятся здесь."
      />

      <ul v-else class="team__grid">
        <li v-for="m in members" :key="m.id" class="person">
          <RouterLink class="person__link" :to="{ name: 'member', params: { id: m.id } }">
            <div class="person__frame">
              <img
                v-if="m.avatar_path"
                class="person__photo"
                :src="m.avatar_path"
                :alt="`Портрет: ${m.full_name}`"
                loading="lazy"
                decoding="async"
              />
              <span v-else class="person__initials" aria-hidden="true">
                {{ m.full_name.slice(0, 1) }}
              </span>
            </div>
            <h3 class="person__name">{{ m.full_name }}</h3>
          </RouterLink>
          <ul v-if="m.tags.length" class="person__tags">
            <li v-for="t in m.tags.slice(0, 3)" :key="t.id">
              <TagChip :name="t.name" :color="t.color" />
            </li>
            <li v-if="m.tags.length > 3" class="person__more">+{{ m.tags.length - 3 }}</li>
          </ul>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.team {
  background: var(--paper);
}

.team__title {
  font-size: var(--step-3);
}

.team__lead {
  margin: var(--space-2) 0 var(--space-4);
  color: var(--muted);
}

.team__grid {
  display: grid;
  gap: var(--space-4) var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}

.person {
  display: grid;
  gap: var(--space-2);
  align-content: start;
}

.person__link {
  display: grid;
  gap: var(--space-2);
  text-decoration: none;
  color: inherit;
}

.person__frame {
  position: relative;
  aspect-ratio: 3 / 4;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  display: grid;
  place-items: center;
}

.person__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s var(--ease);
}

.person__link:hover .person__photo {
  transform: scale(1.03);
}

.person__initials {
  font-family: var(--font-display);
  font-size: var(--step-3);
  font-weight: 800;
  color: var(--line);
}

.person__name {
  font-size: var(--step-1);
  margin: 0;
}

.person__link:hover .person__name {
  color: var(--red);
}

.person__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin: 0;
  padding: 0;
  list-style: none;
}

.person__more {
  font-size: var(--step--1);
  color: var(--muted);
  align-self: center;
}
</style>
