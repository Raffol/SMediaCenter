<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppIcon from '@/components/ui/AppIcon.vue'
import SiteLogo from '@/components/ui/SiteLogo.vue'

/**
 * Правки из разбора макета:
 *  — шапка липкая (лендинг высокий, за «Личным кабинетом» приходилось
 *    крутить наверх);
 *  — слева логотип, раньше там было пусто;
 *  — «Личный кабинет» оформлен кнопкой, а не такой же ссылкой, как
 *    остальные пункты: это единственное действие в шапке;
 *  — активный пункт подсвечивается при скролле, иначе на длинной
 *    странице непонятно, где ты.
 */

const auth = useAuthStore()
const route = useRoute()

const scrolled = ref(false)
const menuOpen = ref(false)
const activeAnchor = ref('')

const anchors = [
  { id: 'komanda', label: 'Команда' },
  { id: 'o-nas', label: 'О нас' },
  { id: 'raboty', label: 'Работы' },
  { id: 'zayavka', label: 'Заявка' },
]

const onLanding = computed(() => route.name === 'home')

let observer = null

function onScroll() {
  scrolled.value = window.scrollY > 24
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })

  // IntersectionObserver вместо расчёта смещений на каждом кадре скролла
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
      if (visible) activeAnchor.value = visible.target.id
    },
    { rootMargin: '-30% 0px -55% 0px', threshold: [0.1, 0.5] },
  )

  anchors.forEach(({ id }) => {
    const el = document.getElementById(id)
    if (el) observer.observe(el)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  observer?.disconnect()
})

function href(id) {
  return onLanding.value ? `#${id}` : `/#${id}`
}
</script>

<template>
  <header class="bar" :class="{ 'bar--solid': scrolled || menuOpen }">
    <div class="shell bar__inner">
      <RouterLink to="/" class="bar__logo tap" @click="menuOpen = false">
        <SiteLogo variant="light" />
      </RouterLink>

      <button
        class="bar__burger tap"
        type="button"
        :aria-expanded="menuOpen"
        aria-controls="site-nav"
        @click="menuOpen = !menuOpen"
      >
        <AppIcon :name="menuOpen ? 'close' : 'menu'" :size="26" />
        <span class="visually-hidden">{{ menuOpen ? 'Закрыть меню' : 'Открыть меню' }}</span>
      </button>

      <nav id="site-nav" class="bar__nav" :class="{ 'bar__nav--open': menuOpen }">
        <a
          v-for="item in anchors"
          :key="item.id"
          class="bar__link tap"
          :class="{ 'bar__link--active': onLanding && activeAnchor === item.id }"
          :href="href(item.id)"
          @click="menuOpen = false"
        >
          {{ item.label }}
        </a>

        <a
          class="bar__link tap"
          href="https://vk.com"
          target="_blank"
          rel="noopener noreferrer"
        >
          Вконтакте
        </a>

        <RouterLink
          :to="auth.isAuthenticated ? { name: 'dashboard' } : { name: 'login' }"
          class="bar__cta tap"
          @click="menuOpen = false"
        >
          {{ auth.isAuthenticated ? 'Кабинет' : 'Личный кабинет' }}
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.bar {
  position: sticky;
  top: 0;
  z-index: 50;
  /* Градиент вместо прозрачности: белые пункты меню лежали прямо
     на листве и почти не читались. */
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0));
  transition: background 0.25s var(--ease), backdrop-filter 0.25s var(--ease);
}

.bar--solid {
  background: rgba(14, 14, 14, 0.9);
  backdrop-filter: blur(14px);
}

.bar__inner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 4.5rem;
}

.bar__logo {
  font-size: var(--step-0);
  text-decoration: none;
  margin-right: auto;
}

.bar__burger {
  color: var(--paper);
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.bar__nav {
  display: none;
}

.bar__nav--open {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--space-1);
  position: absolute;
  inset: 4.5rem 0 auto;
  padding: var(--space-3);
  background: rgba(14, 14, 14, 0.97);
  backdrop-filter: blur(14px);
}

.bar__link {
  /* Базовая линия выровнена для всех пунктов: в макете «Группа
     Вконтакте» сидела ниже соседей, а промежутки были неравными. */
  justify-content: flex-start;
  padding-inline: var(--space-2);
  font-size: var(--step-0);
  color: rgba(255, 255, 255, 0.88);
  text-decoration: none;
  position: relative;
}

.bar__link:hover {
  color: var(--paper);
}

.bar__link--active::after {
  content: '';
  position: absolute;
  left: var(--space-2);
  right: var(--space-2);
  bottom: 0.55rem;
  height: 2px;
  background: var(--red);
}

.bar__cta {
  justify-content: center;
  padding: 0.55rem var(--space-3);
  border: 1.5px solid rgba(255, 255, 255, 0.55);
  border-radius: var(--radius);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  letter-spacing: 0.02em;
  color: var(--paper);
  text-decoration: none;
  transition: background 0.2s var(--ease), border-color 0.2s var(--ease);
}

.bar__cta:hover {
  background: var(--red);
  border-color: var(--red);
}

@media (min-width: 900px) {
  .bar__burger {
    display: none;
  }

  .bar__nav,
  .bar__nav--open {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: var(--space-1);
    position: static;
    inset: auto;
    padding: 0;
    background: none;
    backdrop-filter: none;
  }

  .bar__cta {
    margin-left: var(--space-3);
  }
}
</style>
