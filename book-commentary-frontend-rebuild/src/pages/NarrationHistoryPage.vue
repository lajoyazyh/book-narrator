<template>
  <div class="page">
    <header class="header">
      <div>
        <p class="eyebrow">Narration Archive</p>
        <h1>Narration History</h1>
        <p>Search, review, favorite, rename, and reuse previous narration tasks.</p>
      </div>

      <div class="header-actions">
        <RouterLink class="nav-btn" to="/">Home</RouterLink>
        <RouterLink class="nav-btn" to="/book-narrator">Create Task</RouterLink>
        <RouterLink class="nav-btn" to="/favorites">Favorites</RouterLink>
      </div>
    </header>

    <section class="toolbar">
      <input
          v-model="keyword"
          placeholder="Search by task name, book title, script, or note..."
          @keyup.enter="loadHistory"
      />

      <button @click="loadHistory">Search</button>
      <button class="secondary" @click="resetSearch">Reset</button>
    </section>

    <section v-if="loading" class="empty">
      Loading narration history...
    </section>

    <section v-else-if="historyList.length === 0" class="empty">
      No narration history yet.
    </section>

    <section v-else class="list">
      <article
          v-for="item in historyList"
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
          <span>Mode: {{ modeText(item.mode) }}</span>
          <span>Reading: {{ readingModeText(item.reading_mode) }}</span>
          <span>Output: {{ languageText(item.output_language) }}</span>
          <span>Style: {{ styleText(item.style) }}</span>
          <span>Voice: {{ voiceText(item.voice) }}</span>
        </div>

        <div class="meta">
          <span v-if="item.book_title">Book: {{ item.book_title }}</span>
          <span v-if="item.filename">File: {{ item.filename }}</span>
          <span v-if="item.start_page && item.end_page">
            Pages: {{ item.start_page }}–{{ item.end_page }}
          </span>
          <span v-if="item.chapter_title">Chapter: {{ item.chapter_title }}</span>
          <span v-if="item.created_at">Created: {{ item.created_at }}</span>
        </div>

        <p v-if="item.error_message" class="error-text">
          {{ item.error_message }}
        </p>

        <div class="actions">
          <button class="small-btn" @click="toggleFavorite(item)">
            {{ item.favorite ? 'Remove Favorite' : 'Add Favorite' }}
          </button>

          <button class="small-btn secondary" @click="refillTask(item)">
            Refill Creation Form
          </button>

          <button class="small-btn secondary" @click="toggleDetail(item.task_id)">
            {{ expandedTaskId === item.task_id ? 'Hide Details' : 'View Details' }}
          </button>

          <button class="small-btn danger" @click="removeHistory(item)">
            Delete
          </button>
        </div>

        <div v-if="expandedTaskId === item.task_id" class="detail">
          <h3>Task Requirement</h3>
          <pre>{{ item.task_instruction || 'No extra task requirement saved.' }}</pre>

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

          <h3>Notes</h3>
          <textarea
              v-model="remarkDraft[item.task_id]"
              rows="3"
              placeholder="Add notes for this task"
          ></textarea>

          <button class="small-btn" @click="saveRemark(item)">
            Save Notes
          </button>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { API_BASE_URL } from '@/api/request'
import {
  deleteNarrationHistory,
  getNarrationHistory,
  updateNarrationHistory,
  type NarrationHistoryItem
} from '@/api/narrationHistory'

const router = useRouter()

const loading = ref(false)
const keyword = ref('')
const historyList = ref<NarrationHistoryItem[]>([])
const expandedTaskId = ref('')
const editingTaskId = ref('')
const editingTaskName = ref('')
const remarkDraft = reactive<Record<string, string>>({})

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

function modeText(mode?: string) {
  if (mode === 'page') return 'Page Range'
  if (mode === 'chapter') return 'Chapter'
  if (mode === 'custom') return 'Custom Text'
  return mode || '-'
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

async function loadHistory() {
  loading.value = true

  try {
    const response = await getNarrationHistory({
      keyword: keyword.value || undefined
    })

    const res = response.data

    if (!isSuccess(res)) {
      historyList.value = []
      return
    }

    historyList.value = res.data || []

    historyList.value.forEach((item) => {
      remarkDraft[item.task_id] = item.remark || ''
    })
  } catch (error) {
    console.error(error)
    historyList.value = []
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  keyword.value = ''
  loadHistory()
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

async function saveRemark(item: NarrationHistoryItem) {
  const response = await updateNarrationHistory(item.task_id, {
    remark: remarkDraft[item.task_id] || ''
  })

  const res = response.data

  if (isSuccess(res)) {
    item.remark = remarkDraft[item.task_id] || ''
    alert('Notes saved.')
  } else {
    alert(res.message || 'Failed to save notes.')
  }
}

function toggleDetail(taskId: string) {
  expandedTaskId.value = expandedTaskId.value === taskId ? '' : taskId
}

async function removeHistory(item: NarrationHistoryItem) {
  const confirmed = window.confirm(`Delete "${displayTaskName(item)}"?`)
  if (!confirmed) return

  const response = await deleteNarrationHistory(item.task_id)
  const res = response.data

  if (isSuccess(res)) {
    historyList.value = historyList.value.filter(
        (history) => history.task_id !== item.task_id
    )
  }
}

function refillTask(item: NarrationHistoryItem) {
  router.push({
    path: '/book-narrator',
    query: {
      task_name: item.task_name || '',
      book_id: item.book_id || '',
      style: item.style || '短视频',
      voice: item.voice || 'Ava',
      reading_mode: item.reading_mode || 'quick',
      output_language: item.output_language || 'en',
      mode: item.mode || 'page',
      start_page: item.start_page || '',
      end_page: item.end_page || '',
      chapter_number: item.chapter_number || '',
      task_instruction: item.task_instruction || '',
      custom_text: item.custom_text || ''
    }
  })
}

onMounted(() => {
  loadHistory()
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

.toolbar {
  max-width: 1180px;
  margin: 0 auto 20px;
  display: flex;
  gap: 10px;
  padding: 14px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 16px 44px rgba(15, 23, 42, 0.07);
}

.toolbar input {
  flex: 1;
}

input,
textarea {
  padding: 11px 12px;
  border: 1px solid #dbe3ef;
  border-radius: 12px;
  box-sizing: border-box;
  outline: none;
}

input:focus,
textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
}

.toolbar button,
.small-btn {
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  background: #111827;
  color: white;
  font-weight: 900;
  cursor: pointer;
}

.toolbar button.secondary,
.small-btn.secondary {
  background: #e5e7eb;
  color: #111827;
}

.small-btn.danger {
  background: #dc2626;
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

.detail textarea {
  width: 100%;
  margin-bottom: 10px;
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

.error-text {
  color: #dc2626;
}
</style>