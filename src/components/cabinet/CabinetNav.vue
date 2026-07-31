<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

async function signOut() {
  await auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <nav class="nav">
    <div class="shell nav__inner">
      <RouterLink class="nav__link tap" :to="{ name: 'dashboard' }">Сводка</RouterLink>
      <RouterLink class="nav__link tap" :to="{ name: 'requests' }">Заявки</RouterLink>
      <RouterLink
        v-if="auth.isStaff"
        class="nav__link tap"
        :to="{ name: 'manage-posts' }"
      >
        Публикации
      </RouterLink>

      <a
        v-if="auth.isStaff"
        class="nav__link tap"
        href="/admin/"
        target="_blank"
        rel="noopener"
      >
        Админка
      </a>

      <span class="nav__spacer" />

      <span class="nav__who">{{ auth.user?.full_name }}</span>
      <button class="nav__out tap" type="button" @click="signOut">Выйти</button>
    </div>
  </nav>
</template>

<style scoped>
.nav {
  border-bottom: 1px solid var(--line);
  background: var(--paper);
}

.nav__inner {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-wrap: wrap;
  min-height: 3.5rem;
}

.nav__link {
  padding-inline: var(--space-2);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  color: var(--muted);
  text-decoration: none;
  border-bottom: 2px solid transparent;
}

.nav__link:hover {
  color: var(--ink);
}

.nav__link.router-link-active {
  color: var(--ink);
  border-color: var(--red);
}

.nav__spacer {
  flex: 1;
}

.nav__who {
  font-size: var(--step--1);
  color: var(--muted);
}

.nav__out {
  min-height: 44px;
  padding-inline: var(--space-2);
  border: 0;
  background: none;
  font: inherit;
  font-size: var(--step--1);
  color: var(--red);
  cursor: pointer;
}

.nav__out:hover {
  text-decoration: underline;
}
</style>
