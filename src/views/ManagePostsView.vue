<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api, errorText } from '@/api/client'
import CabinetNav from '@/components/cabinet/CabinetNav.vue'
import StaffBanner from '@/components/cabinet/StaffBanner.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { formatDate } from '@/constants/labels'

const items = ref([])
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const creating = ref(false)

const draft = reactive({
  title: '',
  body: '',
  excerpt: '',
  category: 'news',
  cover_alt: '',
})

const coverFile = ref(null)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/posts/manage/all/', { params: { limit: 100 } })
    items.value = data.items
  } catch (err) {
    error.value = errorText(err, 'Не удалось загрузить публикации')
  } finally {
    loading.value = false
  }
}

function reset() {
  draft.title = ''
  draft.body = ''
  draft.excerpt = ''
  draft.category = 'news'
  draft.cover_alt = ''
  coverFile.value = null
  creating.value = false
}

async function create() {
  if (draft.title.trim().length < 3 || draft.body.trim().length < 10) {
    error.value = 'Заголовок и текст обязательны'
    return
  }
  // Alt обязателен для доступности: без него скринридер читает имя файла
  if (coverFile.value && !draft.cover_alt.trim()) {
    error.value = 'Опишите обложку в поле alt — это нужно для доступности'
    return
  }

  busy.value = true
  error.value = ''
  try {
    const { data } = await api.post('/api/posts/', {
      title: draft.title.trim(),
      body: draft.body.trim(),
      excerpt: draft.excerpt.trim() || null,
      category: draft.category,
      cover_alt: draft.cover_alt.trim() || null,
      is_published: false, // черновик: публикуем отдельным действием
    })

    if (coverFile.value) {
      const fd = new FormData()
      fd.append('file', coverFile.value)
      await api.put(`/api/posts/${data.id}/cover/`, fd)
    }

    reset()
    await load()
  } catch (err) {
    error.value = errorText(err, 'Не удалось создать публикацию')
  } finally {
    busy.value = false
  }
}

async function togglePublish(post) {
  busy.value = true
  error.value = ''
  try {
    await api.patch(`/api/posts/${post.id}/`, { is_published: !post.is_published })
    await load()
  } catch (err) {
    error.value = errorText(err, 'Не удалось изменить статус')
  } finally {
    busy.value = false
  }
}

async function remove(post) {
  if (!window.confirm(`Удалить «${post.title}»? Действие необратимо.`)) return

  busy.value = true
  try {
    await api.delete(`/api/posts/${post.id}/`)
    await load()
  } catch (err) {
    error.value = errorText(err, 'Не удалось удалить публикацию')
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <StaffBanner />
  <CabinetNav />

  <main class="section">
    <div class="shell">
      <header class="head">
        <h1 class="head__title">Публикации</h1>
        <button class="new" type="button" @click="creating = !creating">
          {{ creating ? 'Свернуть' : 'Добавить' }}
        </button>
      </header>

      <p v-if="error" class="alert">
        <AppIcon name="alert" :size="16" /> {{ error }}
      </p>

      <section v-if="creating" class="form">
        <div class="form__field">
          <label class="form__label" for="n-title">Заголовок</label>
          <input id="n-title" v-model="draft.title" class="form__input" type="text" />
        </div>

        <div class="form__field">
          <label class="form__label" for="n-cat">Категория</label>
          <select id="n-cat" v-model="draft.category" class="form__input">
            <option value="news">Новость</option>
            <option value="work">Работа в портфолио</option>
          </select>
        </div>

        <div class="form__field form__field--wide">
          <label class="form__label" for="n-exc">
            Короткое описание <span class="form__opt">— для карточки в ленте</span>
          </label>
          <input id="n-exc" v-model="draft.excerpt" class="form__input" type="text" maxlength="300" />
        </div>

        <div class="form__field form__field--wide">
          <label class="form__label" for="n-body">Текст</label>
          <textarea id="n-body" v-model="draft.body" class="form__input form__input--area" rows="8" />
        </div>

        <div class="form__field">
          <label class="form__label" for="n-cover">Обложка</label>
          <input
            id="n-cover"
            class="form__input"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            @change="coverFile = $event.target.files[0] ?? null"
          />
        </div>

        <div class="form__field">
          <label class="form__label" for="n-alt">
            Описание обложки <span class="form__opt">— alt для скринридеров</span>
          </label>
          <input id="n-alt" v-model="draft.cover_alt" class="form__input" type="text" maxlength="200" />
        </div>

        <div class="form__field form__field--wide">
          <button class="save" type="button" :disabled="busy" @click="create">
            {{ busy ? 'Сохраняем…' : 'Сохранить черновиком' }}
          </button>
          <p class="form__note">
            Публикация создаётся черновиком. Она появится на сайте только
            после нажатия «Опубликовать» в списке ниже.
          </p>
        </div>
      </section>

      <SkeletonCard v-if="loading" :count="4" />

      <EmptyState
        v-else-if="!items.length"
        title="Публикаций пока нет"
        hint="Добавьте первую — она сохранится черновиком, и вы сможете
              проверить её перед публикацией."
      />

      <ul v-else class="list">
        <li v-for="p in items" :key="p.id" class="row">
          <div class="row__thumb">
            <img
              v-if="p.cover_thumb_path"
              :src="p.cover_thumb_path"
              :alt="p.cover_alt || p.title"
              loading="lazy"
            />
          </div>

          <div class="row__body">
            <h2 class="row__title">{{ p.title }}</h2>
            <p class="row__meta">
              {{ p.category === 'work' ? 'Работа' : 'Новость' }}
              <span v-if="p.published_at"> · {{ formatDate(p.published_at) }}</span>
            </p>
          </div>

          <StatusBadge
            :label="p.is_published ? 'Опубликована' : 'Черновик'"
            :tone="p.is_published ? 'ok' : 'off'"
            :icon="p.is_published ? 'check' : 'clock'"
          />

          <div class="row__acts">
            <RouterLink
              v-if="p.is_published"
              class="row__btn"
              :to="{ name: 'post', params: { slug: p.slug } }"
            >
              Открыть
            </RouterLink>
            <button class="row__btn" type="button" :disabled="busy" @click="togglePublish(p)">
              {{ p.is_published ? 'Снять' : 'Опубликовать' }}
            </button>
            <button class="row__btn row__btn--danger" type="button" :disabled="busy" @click="remove(p)">
              Удалить
            </button>
          </div>
        </li>
      </ul>
    </div>
  </main>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.head__title {
  font-size: var(--step-3);
}

.new {
  min-height: 48px;
  padding-inline: var(--space-4);
  border: 0;
  border-radius: var(--radius);
  background: var(--ink);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  cursor: pointer;
}

.new:hover {
  background: var(--red);
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.4em;
  margin: 0 0 var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-left: 3px solid var(--red);
  background: #fff5f6;
  font-size: var(--step--1);
  color: var(--red-dark);
}

.form {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-4);
  margin-bottom: var(--space-5);
  background: var(--surface);
  border-radius: var(--radius-lg);
}

.form__field {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
}

.form__label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.form__opt {
  font-weight: 500;
  color: var(--muted);
}

.form__input {
  width: 100%;
  min-height: 48px;
  padding: 0.65rem 0.8rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font: inherit;
}

.form__input--area {
  min-height: 10rem;
  resize: vertical;
  line-height: 1.55;
}

.form__note {
  margin: var(--space-2) 0 0;
  font-size: var(--step--1);
  color: var(--muted);
}

.save {
  min-height: 52px;
  padding-inline: var(--space-4);
  border: 0;
  border-radius: var(--radius);
  background: var(--red);
  color: var(--paper);
  font-family: var(--font-display);
  font-weight: 800;
  cursor: pointer;
  justify-self: start;
}

.save:hover:not(:disabled) {
  background: var(--red-dark);
}

.save:disabled {
  background: var(--muted);
  cursor: progress;
}

.list {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}

.row {
  display: grid;
  gap: var(--space-2) var(--space-3);
  grid-template-columns: auto 1fr;
  align-items: center;
  padding: var(--space-2);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
}

.row__thumb {
  width: 84px;
  aspect-ratio: 3 / 2;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
}

.row__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row__title {
  font-size: var(--step-0);
  margin: 0;
}

.row__meta {
  margin: 0;
  font-size: var(--step--1);
  color: var(--muted);
}

.row__acts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  grid-column: 1 / -1;
}

.row__btn {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  padding-inline: var(--space-2);
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font: inherit;
  font-size: var(--step--1);
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.row__btn:hover:not(:disabled) {
  border-color: var(--ink);
}

.row__btn--danger {
  color: var(--red);
}

.row__btn:disabled {
  opacity: 0.5;
  cursor: progress;
}

@media (min-width: 760px) {
  .form {
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3) var(--space-4);
  }

  .form__field--wide {
    grid-column: 1 / -1;
  }

  .row {
    grid-template-columns: auto 1fr auto auto;
  }

  .row__acts {
    grid-column: auto;
  }
}
</style>
