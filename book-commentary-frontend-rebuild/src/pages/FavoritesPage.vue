<template>
  <div class="page">
    <header class="header">
      <div>
        <p class="eyebrow">Saved Tasks</p>
        <h1>Favorites</h1>
        <p>Review and manage your favorite narration tasks.</p>
      </div>

      <div class="header-actions">
        <RouterLink class="nav-btn" to="/">Home</RouterLink>
        <RouterLink class="nav-btn" to="/book-narrator">Create Task</RouterLink>
        <RouterLink class="nav-btn" to="/narration-history">History</RouterLink>
      </div>
    </header>

    <section v-if="loading" class="empty">
      Loading favorite tasks...
    </section>

    <section v-else-if="favorites.length === 0" class="empty">
      No favorite tasks yet.
    </section>

    <section v-else class="list">
      <article
          v-for="item in favorites"
          :key="item.task_id"
          class="card"
      >
        <div class="title-row">
          <template v-if="editingTaskId === item.task_id">
            <input
                v-model="editingTaskName"
                class="task-name-input"
                placeholder="Enter a task name"
            />

            <button class="small-btn" @click="saveTaskName(item)">
              Save
            </button>

            <button class="small-btn secondary" @click="cancelEditTaskName">
              Cancel
            </button>
          </template>

          <template v-else>
            <div>
              <h2>{{ displayTaskName(item) }}</h2>
              <p class="task-subtitle">{{ item.book_title || item.filename || 'Untitled book' }}</p>
            </div>

            <button class="small-btn secondary" @click="startEditTaskName(item)">
              Rename
            </button>
          </template>
        </div>

        <div class="meta">
          <span>Task ID: {{ item.task_id }}</span>
          <span>Status: {{ statusText(item.status) }}</span>
          <span>Output: {{ languageText(item.output_language) }}</span>
          <span>Reading: {{ readingModeText(item.reading_mode) }}</span>
          <span>Style: {{ styleText(item.style) }}</span>
          <span>Voice: {{ voiceText(item.voice) }}</span>
          <span v-if="item.start_page && item.end_page">
            Pages: {{ item.start_page }}–{{ item.end_page }}
          </span>
        </div>

        <div class="actions">
          <button class="small-btn" @click="toggleFavorite(item)">
            Remove Favorite
          </button>

          <button class="small-btn secondary" @click="toggleDetail(item.task_id)">
            {{ expandedTaskId === item.task_id ? 'Hide Details' : 'View Details' }}
          </button>
        </div>

        <div v-if="expandedTaskId === item.task_id" class="detail">
          <h3>Narration Script</h3>
          <pre>{{ item.script || 'No narration script yet.' }}</pre>

          <h3>Audio</h3>
          <div v-if="!item.audio_urls || item.audio_urls.length === 0" class="muted">
            No audio available.
          </div>

          <div
              v-for="url in item.audio_urls || []"
              :key="url"
              class="audio-line"
          >
            <audio controls :src="fullAudioUrl(url)"></audio>
            <a :href="fullAudioUrl(url)" target="_blank">Open Audio</a>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API_BASE_URL } from '@/api/request'
import {
  getNarrationHistory,
  updateNarrationHistory,
  type NarrationHistoryItem
} from '@/api/narrationHistory'

const loading = ref(false)
const allItems = ref<NarrationHistoryItem[]>([])
const expandedTaskId = ref('')
const editingTaskId = ref('')
const editingTaskName = ref('')

const favorites = computed(() => {
  return allItems.value.filter((item) => item.favorite)
})

function isSuccess(res: any) {
  return res && (
      res.code === 200 ||
      res.code === 0 ||
      res.message === 'ok' ||
      res.message === 'success'
  )
}

function displayTaskName(item: NarrationHistoryItem) {
  return item.task_name || item.book_title || item.filename || item.task_id
}

function statusText(status?: string) {
  if (status === 'running') return 'Running'
  if (status === 'success') return 'Completed'
  if (status === 'failed') return 'Failed'
  if (status === 'cancelled' || status === 'canceled') return 'Cancelled'
  return status || '-'
}

function styleText(style?: string) {
  const map: Record<string, string> = {
    '短视频': 'Short-video Style',
    '睡前故事': 'Bedtime Story',
    '电影解说': 'Film Commentary'
  }

  if (!style) return '-'
  return map[style] || style
}

function voiceText(voice?: string) {
  const map: Record<string, string> = {
    '晓晓': 'Xiaoxiao',
    '云希': 'Yunxi',
    '云扬': 'Yunyang',
    '晓伊': 'Xiaoyi'
  }

  if (!voice) return '-'
  return map[voice] || voice
}

function readingModeText(readingMode?: string) {
  if (readingMode === 'deep') return 'Deep Reading'
  if (readingMode === 'quick') return 'Quick Reading'
  return readingMode || '-'
}

function languageText(language?: string) {
  const map: Record<string, string> = {
    ar: 'Arabic',
    zh: 'Chinese',
    en: 'English',
    fr: 'French',
    ru: 'Russian',
    es: 'Spanish'
  }

  if (!language) return 'English'
  return map[language] || language
}

function fullAudioUrl(url: string) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

async function loadFavorites() {
  loading.value = true

  try {
    const response = await getNarrationHistory()
    const res = response.data

    if (!isSuccess(res)) {
      allItems.value = []
      return
    }

    allItems.value = res.data || []
  } catch (error) {
    console.error(error)
    allItems.value = []
  } finally {
    loading.value = false
  }
}

function startEditTaskName(item: NarrationHistoryItem) {
  editingTaskId.value = item.task_id
  editingTaskName.value = displayTaskName(item)
}

function cancelEditTaskName() {
  editingTaskId.value = ''
  editingTaskName.value = ''
}

async function saveTaskName(item: NarrationHistoryItem) {
  const name = editingTaskName.value.trim()

  if (!name) {
    alert('Task name cannot be empty.')
    return
  }

  const response = await updateNarrationHistory(item.task_id, {
    task_name: name
  })

  const res = response.data

  if (isSuccess(res)) {
    item.task_name = name
    editingTaskId.value = ''
    editingTaskName.value = ''
  } else {
    alert(res.message || 'Failed to rename the task.')
  }
}

async function toggleFavorite(item: NarrationHistoryItem) {
  const response = await updateNarrationHistory(item.task_id, {
    favorite: !item.favorite
  })

  const res = response.data

  if (isSuccess(res)) {
    item.favorite = !item.favorite
  }
}

function toggleDetail(taskId: string) {
  expandedTaskId.value = expandedTaskId.value === taskId ? '' : taskId
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 28px;
  background:
      radial-gradient(circle at top left, rgba(79, 70, 229, 0.14), transparent 30%),
      radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.12), transparent 30%),
      linear-gradient(180deg, #f8fafc, #eef2f7);
}

.header {
  max-width: 1180px;
  margin: 0 auto 20px;
  padding: 30px;
  border-radius: 30px;
  background: linear-gradient(135deg, #0f172a, #1e293b 55%, #334155);
  color: white;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 26px 70px rgba(15, 23, 42, 0.24);
}

.eyebrow {
  margin: 0 0 8px;
  color: #93c5fd;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 900;
}

.header h1 {
  margin: 0;
  font-size: 34px;
  letter-spacing: -0.035em;
}

.header p {
  margin: 8px 0 0;
  color: #cbd5e1;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.nav-btn {
  color: white;
  text-decoration: none;
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.16);
  font-weight: 900;
}

.list {
  max-width: 1180px;
  margin: 0 auto;
}

.card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 24px;
  padding: 22px;
  margin-bottom: 16px;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
}

.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.title-row h2 {
  margin: 0;
  font-size: 21px;
}

.task-subtitle {
  margin: 6px 0 0;
  color: #64748b;
}

.task-name-input {
  min-width: 280px;
  padding: 11px 12px;
  border: 1px solid #dbe3ef;
  border-radius: 12px;
}

.meta {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  color: #64748b;
  font-size: 14px;
}

.meta span {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.small-btn {
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  background: #111827;
  color: white;
  font-weight: 900;
  cursor: pointer;
}

.small-btn.secondary {
  background: #e5e7eb;
  color: #111827;
}

.detail {
  margin-top: 18px;
  padding: 16px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.detail pre {
  white-space: pre-wrap;
  line-height: 1.85;
  max-height: 360px;
  overflow-y: auto;
  background: white;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}

.audio-line {
  margin-bottom: 10px;
  padding: 12px;
  border-radius: 14px;
  background: white;
  border: 1px solid #e2e8f0;
}

.audio-line audio {
  width: 100%;
}

.audio-line a {
  display: inline-block;
  margin-top: 6px;
  color: #2563eb;
  font-weight: 800;
  text-decoration: none;
}

.empty {
  max-width: 1180px;
  margin: 0 auto;
  padding: 30px;
  text-align: center;
  color: #64748b;
}

.muted {
  color: #64748b;
}
</style>