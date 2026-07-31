<script setup>
import { computed, ref } from 'vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import TagChip from '@/components/ui/TagChip.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { formatDateTime, responseStatus } from '@/constants/labels'

const props = defineProps({
  response: { type: Object, required: true },
  canDecide: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
})

const emit = defineEmits(['decide'])

const status = computed(() => responseStatus(props.response.status))
const commenting = ref(false)
const comment = ref('')

function decide(accept) {
  emit('decide', {
    id: props.response.id,
    accept,
    comment: comment.value.trim() || null,
  })
  commenting.value = false
  comment.value = ''
}
</script>

<template>
  <article class="resp" :class="{ 'resp--off': response.status === 'declined' }">
    <header class="resp__head">
      <div class="resp__who">
        <RouterLink
          class="resp__name"
          :to="{ name: 'member', params: { id: response.member.id } }"
        >
          {{ response.member.full_name }}
        </RouterLink>
        <ul v-if="response.member.tags?.length" class="resp__tags">
          <li v-for="t in response.member.tags.slice(0, 3)" :key="t.id">
            <TagChip :name="t.name" :color="t.color" />
          </li>
        </ul>
      </div>
      <StatusBadge :label="status.label" :tone="status.tone" :icon="status.icon" />
    </header>

    <p class="resp__msg">{{ response.message }}</p>

    <p v-if="response.decision_comment" class="resp__comment">
      <AppIcon name="arrow-right" :size="15" />
      {{ response.decision_comment }}
    </p>

    <footer class="resp__foot">
      <span class="resp__date">{{ formatDateTime(response.created_at) }}</span>

      <div v-if="canDecide && response.status === 'pending'" class="resp__acts">
        <button
          class="resp__btn resp__btn--yes"
          type="button"
          :disabled="busy"
          @click="decide(true)"
        >
          Принять
        </button>
        <button
          class="resp__btn"
          type="button"
          :disabled="busy"
          @click="commenting = !commenting"
        >
          Отклонить
        </button>
      </div>
    </footer>

    <div v-if="commenting" class="resp__reject">
      <label class="resp__label" :for="`c-${response.id}`">
        Причина <span class="resp__opt">— необязательно, но её увидит участник</span>
      </label>
      <textarea
        :id="`c-${response.id}`"
        v-model="comment"
        class="resp__area"
        rows="2"
        maxlength="500"
        placeholder="Например: на эту дату уже назначен другой человек"
      />
      <div class="resp__acts">
        <button class="resp__btn" type="button" :disabled="busy" @click="decide(false)">
          Отклонить отклик
        </button>
        <button class="resp__btn resp__btn--ghost" type="button" @click="commenting = false">
          Отмена
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.resp {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--paper);
}

.resp--off {
  opacity: 0.65;
}

.resp__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.resp__who {
  display: grid;
  gap: var(--space-1);
}

.resp__name {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step-0);
  text-decoration: none;
}

.resp__name:hover {
  color: var(--red);
}

.resp__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin: 0;
  padding: 0;
  list-style: none;
}

.resp__msg {
  margin: 0;
  white-space: pre-line;
  color: var(--ink-soft);
}

.resp__comment {
  display: flex;
  align-items: flex-start;
  gap: 0.4em;
  margin: 0;
  padding: var(--space-2);
  background: var(--surface);
  border-radius: var(--radius);
  font-size: var(--step--1);
}

.resp__comment :deep(svg) {
  flex: none;
  margin-top: 0.2em;
  color: var(--red);
}

.resp__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.resp__date {
  font-size: var(--step--1);
  color: var(--muted);
}

.resp__acts {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.resp__btn {
  min-height: 44px;
  padding-inline: var(--space-3);
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
  cursor: pointer;
}

.resp__btn:hover:not(:disabled) {
  border-color: var(--ink);
}

.resp__btn--yes {
  background: var(--red);
  border-color: var(--red);
  color: var(--paper);
}

.resp__btn--yes:hover:not(:disabled) {
  background: var(--red-dark);
  border-color: var(--red-dark);
}

.resp__btn--ghost {
  border-color: transparent;
  color: var(--muted);
}

.resp__btn:disabled {
  opacity: 0.5;
  cursor: progress;
}

.resp__reject {
  display: grid;
  gap: var(--space-1);
  padding-top: var(--space-2);
  border-top: 1px solid var(--line);
}

.resp__label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--step--1);
}

.resp__opt {
  font-weight: 500;
  color: var(--muted);
}

.resp__area {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  font: inherit;
  resize: vertical;
}
</style>
