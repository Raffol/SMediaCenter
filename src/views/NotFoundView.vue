<script setup></script>

<template>
  <main class="nf">
    <div class="shell nf__inner">
      <p class="eyebrow">Ошибка 404</p>
      <h1 class="nf__title">Такой страницы нет</h1>
      <!-- Ошибка объясняет, что делать, и не извиняется -->
      <p class="nf__text">
        Ссылка могла устареть или в адресе опечатка. Начните с главной или
        посмотрите публикации.
      </p>
      <div class="nf__actions">
        <RouterLink class="nf__primary" to="/">На главную</RouterLink>
        <RouterLink class="nf__link" :to="{ name: 'posts' }">Публикации</RouterLink>
      </div>
    </div>
  </main>
</template>

<style scoped>
.nf {
  display: grid;
  align-content: center;
  min-height: 70vh;
}

.nf__inner {
  display: grid;
  gap: var(--space-2);
  justify-items: start;
  max-width: 52ch;
}

.nf__title {
  font-size: var(--step-3);
}

.nf__text {
  margin: 0;
  color: var(--ink-soft);
}

.nf__actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  margin-top: var(--space-2);
}

.nf__primary {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
  padding-inline: var(--space-4);
  border-radius: var(--radius);
  background: var(--ink);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  text-decoration: none;
}

.nf__primary:hover {
  background: var(--red);
}

.nf__link {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  border-bottom: 1.5px solid var(--line);
}
</style>
