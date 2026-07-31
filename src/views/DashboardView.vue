<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import CabinetNav from '@/components/cabinet/CabinetNav.vue'
import StaffBanner from '@/components/cabinet/StaffBanner.vue'
import RequestCard from '@/components/cabinet/RequestCard.vue'
import TagChip from '@/components/ui/TagChip.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'

const auth = useAuthStore()

const loading = ref(true)
const mine = ref([])
const suggested = ref([])
const newCount = ref(0)

/**
 * Сводка отвечает на один вопрос: что от меня ждут прямо сейчас.
 * Участнику — назначенные заявки и подходящие по пометкам,
 * персоналу — сколько новых заявок без исполнителя.
 */
onMounted(async () => {
  const calls = [api.get('/api/requests/', { params: { mine: true, limit: 4 } })]

  if (auth.isStaff) {
    calls.push(api.get('/api/requests/', { params: { status: 'new', limit: 6 } }))
  } else {
    calls.push(
      api.get('/api/requests/', { params: { relevant: true, status: 'new', limit: 4 } }),
    )
  }

  const [mineRes, otherRes] = await Promise.allSettled(calls)

  if (mineRes.status === 'fulfilled') mine.value = mineRes.value.data.items
  if (otherRes.status === 'fulfilled') {
    suggested.value = otherRes.value.data.items
    newCount.value = otherRes.value.data.total
  }

  loading.value = false
})

const greeting = computed(() => {
  const name = auth.user?.full_name?.split(' ')[0] ?? ''
  return name ? `Привет, ${name}` : 'Личный кабинет'
})
</script>

<template>
  <StaffBanner />
  <CabinetNav />

  <main class="section">
    <div class="shell">
      <h1 class="title">{{ greeting }}</h1>

      <div class="me">
        <ul v-if="auth.user?.tags?.length" class="me__tags">
          <li v-for="t in auth.user.tags" :key="t.id">
            <TagChip :name="t.name" :color="t.color" />
          </li>
        </ul>
        <p v-else class="me__none">
          Пометок нет — подбор заявок по виду съёмки пока не работает.
          Попросите контент-менеджера добавить их.
        </p>
      </div>

      <SkeletonCard v-if="loading" :count="3" />

      <template v-else>
        <section class="block">
          <h2 class="block__title">
            Назначены мне
            <RouterLink class="block__all" :to="{ name: 'requests', query: { scope: 'mine' } }">
              все
            </RouterLink>
          </h2>

          <EmptyState
            v-if="!mine.length"
            title="Пока ничего не назначено"
            hint="Откликнитесь на подходящую заявку — если контент-менеджер выберет
                  вас, она появится здесь."
          />

          <ul v-else class="grid">
            <li v-for="r in mine" :key="r.id"><RequestCard :request="r" /></li>
          </ul>
        </section>

        <section class="block">
          <h2 class="block__title">
            {{ auth.isStaff ? `Новые заявки — ${newCount}` : 'Подходят вам' }}
            <RouterLink class="block__all" :to="{ name: 'requests' }">все</RouterLink>
          </h2>

          <EmptyState
            v-if="!suggested.length"
            :title="auth.isStaff ? 'Новых заявок нет' : 'Подходящих заявок нет'"
            :hint="
              auth.isStaff
                ? 'Все заявки разобраны или ещё не поступили.'
                : 'Заглядывайте позже — или посмотрите все заявки целиком.'
            "
          />

          <ul v-else class="grid">
            <li v-for="r in suggested" :key="r.id"><RequestCard :request="r" /></li>
          </ul>
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
.title {
  font-size: var(--step-3);
  margin-bottom: var(--space-2);
}

.me {
  margin-bottom: var(--space-5);
}

.me__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin: 0;
  padding: 0;
  list-style: none;
}

.me__none {
  margin: 0;
  max-width: 60ch;
  font-size: var(--step--1);
  color: var(--muted);
}

.block {
  margin-bottom: var(--space-5);
}

.block__title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: var(--step-1);
  margin-bottom: var(--space-3);
}

.block__all {
  font-family: var(--font-body);
  font-size: var(--step--1);
  font-weight: 400;
  color: var(--red);
}

.grid {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
</style>
