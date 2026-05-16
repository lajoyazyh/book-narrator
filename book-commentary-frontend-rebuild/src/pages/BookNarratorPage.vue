<template>
  <div class="page">
    <header class="app-header">
      <div>
        <p class="eyebrow">Narration Workspace</p>
        <h1>Book Narrator Agent</h1>
        <p>Upload a PDF, configure a section, choose an output language, and generate narration with audio.</p>
      </div>

      <nav class="top-nav">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/narration-history">History</RouterLink>
        <RouterLink to="/favorites">Favorites</RouterLink>
      </nav>
    </header>

    <main class="workspace">
      <section class="sidebar">
        <div class="panel">
          <div class="panel-title">
            <span>01</span>
            <div>
              <h2>Upload PDF</h2>
              <p>Add a new source file.</p>
            </div>
          </div>

          <div class="upload-box">
            <input
                id="book-file-input"
                class="file-input"
                type="file"
                accept="application/pdf"
                @change="handleFileChange"
            />

            <label class="file-button" for="book-file-input">
              Choose PDF
            </label>

            <div class="file-meta">
              <strong>{{ selectedFile ? selectedFile.name : 'No file selected' }}</strong>
              <span>Only PDF files are supported.</span>
            </div>
          </div>

          <button
              class="primary-btn full"
              :disabled="!selectedFile || uploading"
              @click="handleUpload"
          >
            {{ uploading ? 'Uploading...' : 'Upload Book' }}
          </button>

          <p v-if="uploadMessage" class="message">{{ uploadMessage }}</p>
        </div>

        <div class="panel">
          <div class="panel-title">
            <span>02</span>
            <div>
              <h2>Select Book</h2>
              <p>Choose an existing PDF.</p>
            </div>
          </div>

          <button class="secondary-btn full" @click="loadBooks">
            Refresh Book List
          </button>

          <p class="message">{{ bookListMessage }}</p>

          <select v-model="selectedBookId" @change="handleBookChange">
            <option value="">Select a book</option>
            <option
                v-for="book in books"
                :key="book.book_id"
                :value="book.book_id"
            >
              {{ book.title || book.filename || book.book_id }}
            </option>
          </select>

          <div v-if="currentBook" class="book-card">
            <div>
              <span>Current Book</span>
              <strong>{{ currentBook.filename }}</strong>
            </div>
            <div>
              <span>Book ID</span>
              <strong>{{ currentBook.book_id }}</strong>
            </div>
            <div>
              <span>Storage</span>
              <strong>{{ currentBook.storage_label }}</strong>
            </div>
            <div>
              <span>Total Pages</span>
              <strong>{{ totalPages || 'Unknown' }}</strong>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">
            <span>03</span>
            <div>
              <h2>Task Settings</h2>
              <p>Control the narration output.</p>
            </div>
          </div>

          <label>Task Name</label>
          <input
              v-model="form.task_name"
              type="text"
              placeholder="Optional, for example: pages 50-100 narration"
          />

          <label>Narration Style</label>
          <select v-model="form.style">
            <option value="短视频">Short-video Style</option>
            <option value="睡前故事">Bedtime Story</option>
            <option value="电影解说">Film Commentary</option>
          </select>

          <label>Reading Mode</label>
          <select v-model="form.reading_mode">
            <option value="quick">Quick Reading · Concise overview</option>
            <option value="deep">Deep Reading · Richer details</option>
          </select>

          <label>Output Language</label>
          <select v-model="form.output_language">
            <option value="en">English</option>
            <option value="zh">Chinese</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
            <option value="ru">Russian</option>
            <option value="ar">Arabic</option>
          </select>

          <label>Voice</label>
          <select v-model="form.voice">
            <optgroup label="English">
              <option value="Ava">Ava · English female voice</option>
              <option value="Jenny">Jenny · English female voice</option>
              <option value="Guy">Guy · English male voice</option>
              <option value="Brian">Brian · English male voice</option>
            </optgroup>

            <optgroup label="Chinese">
              <option value="Xiaoxiao">Xiaoxiao · Chinese female voice</option>
              <option value="Yunxi">Yunxi · Chinese male voice</option>
              <option value="Yunyang">Yunyang · Chinese male voice</option>
              <option value="Xiaoyi">Xiaoyi · Chinese female voice</option>
            </optgroup>

            <optgroup label="French">
              <option value="Denise">Denise · French female voice</option>
              <option value="Henri">Henri · French male voice</option>
            </optgroup>

            <optgroup label="Spanish">
              <option value="Elvira">Elvira · Spanish female voice</option>
              <option value="Alvaro">Alvaro · Spanish male voice</option>
            </optgroup>

            <optgroup label="Russian">
              <option value="Svetlana">Svetlana · Russian female voice</option>
              <option value="Dmitry">Dmitry · Russian male voice</option>
            </optgroup>

            <optgroup label="Arabic">
              <option value="Zariyah">Zariyah · Arabic female voice</option>
              <option value="Hamed">Hamed · Arabic male voice</option>
            </optgroup>
          </select>

          <label>Narration Mode</label>
          <select v-model="form.mode">
            <option value="page">By Page Range</option>
            <option value="chapter">By Chapter</option>
            <option value="custom">Custom Text</option>
          </select>

          <div v-if="form.mode === 'page'" class="two-col">
            <div>
              <label>Start Page</label>
              <input
                  type="number"
                  min="1"
                  :max="totalPages || undefined"
                  v-model.number="form.start_page"
              />
            </div>

            <div>
              <label>End Page</label>
              <input
                  type="number"
                  min="1"
                  :max="totalPages || undefined"
                  v-model.number="form.end_page"
              />
            </div>
          </div>

          <p v-if="form.mode === 'page' && totalPages" class="hint">
            This PDF has {{ totalPages }} pages.
          </p>

          <p v-if="pageRangeError" class="error-text">
            {{ pageRangeError }}
          </p>

          <div v-if="form.mode === 'chapter'">
            <label>Chapter</label>
            <select v-model.number="form.chapter_number">
              <option :value="0">Select a chapter</option>
              <option
                  v-for="chapter in outlineChapters"
                  :key="chapter.chapter_number"
                  :value="chapter.chapter_number"
              >
                Chapter {{ chapter.chapter_number }}: {{ chapter.title }}
              </option>
            </select>
          </div>

          <label>Extra Task Requirement</label>
          <textarea
              v-model="form.task_instruction"
              rows="4"
              placeholder="Example: After the narration, analyze the writing style and character personalities."
          ></textarea>

          <div v-if="form.mode === 'custom'">
            <label>Custom Source Text</label>
            <textarea
                v-model="form.custom_text"
                rows="8"
                placeholder="Paste the original source text here."
            ></textarea>
          </div>

          <button
              class="primary-btn full generate-btn"
              :disabled="generating || !canGenerate"
              @click="handleGenerate"
          >
            {{ generating ? 'Generating...' : 'Generate Narration' }}
          </button>
        </div>
      </section>

      <section class="main-area">
        <div class="status-panel">
          <div>
            <p class="eyebrow dark">Generation Status</p>
            <h2>{{ statusText }}</h2>
          </div>

          <div v-if="currentTaskId" class="status-meta">
            <div>
              <span>Current Task ID</span>
              <strong>{{ currentTaskId }}</strong>
            </div>

            <div v-if="currentTaskName">
              <span>Current Task Name</span>
              <strong>{{ currentTaskName }}</strong>
            </div>

            <div class="status-actions">
              <button v-if="generating" class="danger-btn" @click="handleCancelTask">
                Cancel Task
              </button>
              <button class="secondary-btn" @click="clearCurrentTask">
                Clear State
              </button>
            </div>
          </div>
        </div>

        <div class="result-grid">
          <div class="result-card">
            <div class="card-heading">
              <div>
                <p class="eyebrow dark">Audio</p>
                <h2>Playback</h2>
              </div>
            </div>

            <div v-if="audioUrls.length === 0" class="empty-state">
              No audio available yet.
            </div>

            <div
                v-for="(url, index) in audioUrls"
                :key="url"
                class="audio-item"
            >
              <div class="audio-title">Audio Segment {{ index + 1 }}</div>
              <audio controls :src="fullAudioUrl(url)"></audio>
              <a :href="fullAudioUrl(url)" target="_blank">Open Audio</a>
            </div>
          </div>

          <div class="result-card script-card">
            <div class="card-heading">
              <div>
                <p class="eyebrow dark">Output</p>
                <h2>Narration Script</h2>
              </div>

              <button
                  class="secondary-btn"
                  :disabled="!script"
                  @click="copyScript"
              >
                Copy
              </button>
            </div>

            <pre class="script-box">{{ script || 'No narration script yet.' }}</pre>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { API_BASE_URL } from '@/api/request'
import {
  uploadBook,
  getBooks,
  getBookOutline,
  narrateBook,
  cancelNarrationTask,
  type OutputLanguage
} from '@/api/bookNarrator'
import { getNarrationHistoryDetail } from '@/api/narrationHistory'

interface BookItem {
  book_id: string
  filename: string
  title: string
  path: string
  storage_label: string
}

interface OutlineChapter {
  chapter_number: number
  title: string
}

interface BookOutline {
  page_count?: number
  pages?: number
  chapters?: OutlineChapter[]
}

const route = useRoute()
const TASK_STORAGE_KEY = 'current_narration_task_id'

const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const generating = ref(false)

const uploadMessage = ref('')
const statusText = ref('Ready')
const bookListMessage = ref('Loading books from shared/books...')

const books = ref<BookItem[]>([])
const selectedBookId = ref('')
const outline = ref<BookOutline | null>(null)

const script = ref('')
const audioUrls = ref<string[]>([])
const currentTaskId = ref('')
const currentTaskName = ref('')

let pollTimer: number | null = null

const form = reactive({
  task_name: '',
  style: '短视频',
  voice: 'Ava',
  reading_mode: 'quick',
  output_language: 'en' as OutputLanguage,
  mode: 'page',
  start_page: 1,
  end_page: 3,
  chapter_number: 0,
  custom_text: '',
  task_instruction: ''
})

const defaultVoiceByLanguage: Record<OutputLanguage, string> = {
  en: 'Ava',
  zh: 'Xiaoxiao',
  fr: 'Denise',
  es: 'Elvira',
  ru: 'Svetlana',
  ar: 'Zariyah'
}

watch(
    () => form.output_language,
    (language) => {
      form.voice = defaultVoiceByLanguage[language as OutputLanguage] || 'Ava'
    }
)

function isSuccess(res: any) {
  return res && (
      res.code === 0 ||
      res.code === 200 ||
      res.status === 0 ||
      res.status === 200 ||
      res.message === 'ok' ||
      res.message === 'success' ||
      res.message === '上传成功' ||
      res.message === '任务已中止' ||
      res.message === '任务已经中止' ||
      res.message === 'Task created'
  )
}

function normalizeBooksResponse(res: any) {
  if (Array.isArray(res)) return res
  if (res && Array.isArray(res.data)) return res.data
  if (res && res.data && Array.isArray(res.data.data)) return res.data.data
  return []
}

function normalizeApiData(res: any) {
  if (!res) return null
  if (res.data !== undefined) return res.data
  return res
}

function normalizeBookItem(item: any): BookItem {
  const path = item.path || ''
  const filename = item.filename || item.file_name || item.name || ''
  const title = item.title || filename || item.name || item.book_id || ''

  let storageLabel = item.storage || 'Backend Book Directory'

  if (path.includes('/shared/books') || path.includes('\\shared\\books')) {
    storageLabel = 'shared/books Directory'
  }

  return {
    book_id: item.book_id || item.bookId || item.id || '',
    filename,
    title,
    path,
    storage_label: storageLabel
  }
}

const currentBook = computed(() => {
  return books.value.find((item) => item.book_id === selectedBookId.value)
})

const outlineChapters = computed(() => {
  return outline.value?.chapters || []
})

const totalPages = computed(() => {
  return outline.value?.page_count || outline.value?.pages || 0
})

const pageRangeError = computed(() => {
  if (form.mode !== 'page') return ''

  if (!selectedBookId.value) return 'Please select a book first.'
  if (form.start_page < 1) return 'Start page cannot be less than 1.'
  if (form.end_page < 1) return 'End page cannot be less than 1.'
  if (form.end_page < form.start_page) return 'End page cannot be smaller than start page.'

  if (totalPages.value && form.end_page > totalPages.value) {
    return `End page cannot exceed the total page count. This book has ${totalPages.value} pages.`
  }

  return ''
})

const canGenerate = computed(() => {
  if (form.mode === 'custom') return form.custom_text.trim().length > 0
  if (!selectedBookId.value) return false
  if (form.mode === 'page') return !pageRangeError.value
  if (form.mode === 'chapter') return form.chapter_number > 0
  return false
})

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    selectedFile.value = null
    return
  }

  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert('Please upload a PDF file.')
    selectedFile.value = null
    return
  }

  selectedFile.value = file
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  uploadMessage.value = 'Uploading PDF to shared/books...'

  try {
    const response = await uploadBook(selectedFile.value)
    const res = response.data

    if (!isSuccess(res)) {
      uploadMessage.value = res.message || 'Upload failed.'
      return
    }

    const uploadData: any = normalizeApiData(res)
    uploadMessage.value = `Uploaded: ${uploadData?.filename || selectedFile.value.name}`

    await loadBooks()

    if (uploadData?.book_id) {
      selectedBookId.value = uploadData.book_id
      await handleBookChange()
    }
  } catch (error) {
    console.error(error)
    uploadMessage.value = 'Upload failed. Please check whether the backend API is running.'
  } finally {
    uploading.value = false
  }
}

async function loadBooks() {
  bookListMessage.value = 'Loading books from shared/books...'

  try {
    const response = await getBooks()
    const res = response.data

    const rawBooks = normalizeBooksResponse(res)
    const normalizedBooks = rawBooks
        .map(normalizeBookItem)
        .filter((item: BookItem) => item.book_id)

    books.value = normalizedBooks

    if (books.value.length > 0) {
      bookListMessage.value = `${books.value.length} book(s) loaded from shared/books.`

      if (!selectedBookId.value) {
        selectedBookId.value = books.value[0].book_id
        await handleBookChange()
      }
    } else {
      bookListMessage.value = 'Backend responded, but no books were found in shared/books.'
    }
  } catch (error) {
    console.error(error)
    books.value = []
    bookListMessage.value = 'Failed to load books from shared/books. Please check the backend.'
  }
}

async function handleBookChange() {
  if (!selectedBookId.value) {
    outline.value = null
    return
  }

  try {
    const response = await getBookOutline(selectedBookId.value)
    const res = response.data

    if (isSuccess(res)) {
      outline.value = normalizeApiData(res) as BookOutline

      if (form.mode === 'page' && totalPages.value) {
        form.start_page = 1
        form.end_page = Math.min(3, totalPages.value)
      }
    } else {
      outline.value = null
    }
  } catch (error) {
    console.error(error)
    outline.value = null
  }
}

async function handleGenerate() {
  if (pageRangeError.value) {
    statusText.value = pageRangeError.value
    return
  }

  if (!canGenerate.value) return

  generating.value = true
  statusText.value = 'Creating background narration task...'
  script.value = ''
  audioUrls.value = []
  currentTaskName.value = ''

  try {
    const payload = {
      task_name: form.task_name,
      book_id: selectedBookId.value,
      style: form.style,
      voice: form.voice,
      reading_mode: form.reading_mode,
      output_language: form.output_language,
      mode: form.mode,
      start_page: form.start_page,
      end_page: form.end_page,
      chapter_number: form.chapter_number,
      custom_text: form.custom_text,
      task_instruction: form.task_instruction
    }

    const response = await narrateBook(payload)
    const res = response.data

    if (!isSuccess(res)) {
      statusText.value = res.message || 'Generation failed.'
      generating.value = false
      return
    }

    const data: any = normalizeApiData(res)

    if (data?.status === 'running' && data?.task_id) {
      currentTaskId.value = data.task_id
      currentTaskName.value = data.task_name || data.task_id
      localStorage.setItem(TASK_STORAGE_KEY, data.task_id)
      statusText.value = `Task created: ${data.task_name || data.task_id}, generating in the background...`
      startPollingTask(data.task_id)
      return
    }

    statusText.value = `Generation completed. Task ID: ${data?.task_id || 'Unknown'}`
    script.value = data?.script || ''
    audioUrls.value = data?.audio_urls || []
    generating.value = false
  } catch (error: any) {
    console.error(error)
    statusText.value =
        error?.response?.data?.detail ||
        'Generation failed. Please check whether the backend and Agent service are running.'
    generating.value = false
  }
}

function startPollingTask(taskId: string) {
  stopPollingTask()
  currentTaskId.value = taskId
  generating.value = true

  pollTimer = window.setInterval(async () => {
    await fetchTaskStatus(taskId)
  }, 2000)

  fetchTaskStatus(taskId)
}

function stopPollingTask() {
  if (pollTimer !== null) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function fetchTaskStatus(taskId: string) {
  try {
    const response = await getNarrationHistoryDetail(taskId)
    const res = response.data

    if (!isSuccess(res)) {
      statusText.value = res.message || `Task ${taskId} query failed.`
      return
    }

    const item: any = normalizeApiData(res)
    if (!item) return

    currentTaskName.value = item.task_name || item.book_title || item.filename || taskId

    if (item.status === 'running') {
      statusText.value = `Task ${currentTaskName.value} is generating in the background. Please wait...`
      generating.value = true
      return
    }

    if (item.status === 'cancelled' || item.status === 'canceled') {
      statusText.value = item.error_message || `Task ${currentTaskName.value} was cancelled.`
      generating.value = false
      currentTaskId.value = ''
      currentTaskName.value = ''
      localStorage.removeItem(TASK_STORAGE_KEY)
      stopPollingTask()
      return
    }

    if (item.status === 'success') {
      script.value = item.script || ''
      audioUrls.value = item.audio_urls || []
      statusText.value = `Task completed: ${currentTaskName.value}`
      generating.value = false
      currentTaskId.value = ''
      currentTaskName.value = ''
      localStorage.removeItem(TASK_STORAGE_KEY)
      stopPollingTask()
      return
    }

    if (item.status === 'failed') {
      statusText.value = item.error_message || `Task ${currentTaskName.value} failed.`
      generating.value = false
      currentTaskId.value = ''
      currentTaskName.value = ''
      localStorage.removeItem(TASK_STORAGE_KEY)
      stopPollingTask()
    }
  } catch (error) {
    console.error(error)
    statusText.value = `Task ${taskId} status query failed. Retrying...`
  }
}

async function handleCancelTask() {
  if (!currentTaskId.value) return

  const taskId = currentTaskId.value

  try {
    statusText.value = `Cancelling task ${currentTaskName.value || taskId}...`

    const response = await cancelNarrationTask(taskId)
    const res = response.data

    if (!isSuccess(res)) {
      statusText.value = res.message || 'Failed to cancel task.'
      return
    }

    stopPollingTask()
    generating.value = false
    currentTaskId.value = ''
    currentTaskName.value = ''
    localStorage.removeItem(TASK_STORAGE_KEY)
    statusText.value = `Task ${taskId} cancelled.`
  } catch (error: any) {
    console.error(error)
    statusText.value =
        error?.response?.data?.detail ||
        'Failed to cancel task. Please check the backend API.'
  }
}

function clearCurrentTask() {
  stopPollingTask()
  generating.value = false
  currentTaskId.value = ''
  currentTaskName.value = ''
  localStorage.removeItem(TASK_STORAGE_KEY)
  statusText.value = 'Current task state cleared.'
}

async function applyRouteQueryToForm() {
  const query = route.query

  if (typeof query.book_id === 'string') {
    selectedBookId.value = query.book_id
    await handleBookChange()
  }

  if (typeof query.task_name === 'string') form.task_name = query.task_name
  if (typeof query.style === 'string') form.style = query.style
  if (typeof query.voice === 'string') form.voice = query.voice
  if (typeof query.reading_mode === 'string') form.reading_mode = query.reading_mode
  if (typeof query.output_language === 'string') {
    form.output_language = query.output_language as OutputLanguage
  }
  if (typeof query.mode === 'string') form.mode = query.mode
  if (typeof query.start_page === 'string') form.start_page = Number(query.start_page) || 1
  if (typeof query.end_page === 'string') form.end_page = Number(query.end_page) || 3
  if (typeof query.chapter_number === 'string') form.chapter_number = Number(query.chapter_number) || 0
  if (typeof query.task_instruction === 'string') form.task_instruction = query.task_instruction
  if (typeof query.custom_text === 'string') form.custom_text = query.custom_text

  if (Object.keys(query).length > 0) {
    statusText.value = 'Task parameters were loaded from history. You can generate again.'
  }
}

function fullAudioUrl(url: string) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

async function copyScript() {
  if (!script.value) return
  await navigator.clipboard.writeText(script.value)
  statusText.value = 'Narration script copied.'
}

onMounted(async () => {
  await loadBooks()
  await applyRouteQueryToForm()

  const savedTaskId = localStorage.getItem(TASK_STORAGE_KEY)

  if (savedTaskId) {
    currentTaskId.value = savedTaskId
    statusText.value = `Unfinished task detected: ${savedTaskId}, restoring...`
    startPollingTask(savedTaskId)
  }
})

onBeforeUnmount(() => {
  stopPollingTask()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 28px;
  background:
      radial-gradient(circle at 8% 0%, rgba(79, 70, 229, 0.15), transparent 30%),
      radial-gradient(circle at 92% 10%, rgba(14, 165, 233, 0.14), transparent 32%),
      linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  color: #0f172a;
}

.app-header {
  max-width: 1320px;
  margin: 0 auto 22px;
  padding: 30px;
  border-radius: 32px;
  color: white;
  background:
      linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.96)),
      radial-gradient(circle at top right, rgba(59, 130, 246, 0.35), transparent 40%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  box-shadow: 0 28px 76px rgba(15, 23, 42, 0.26);
}

.eyebrow {
  margin: 0 0 8px;
  color: #93c5fd;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 900;
}

.eyebrow.dark {
  color: #4f46e5;
}

.app-header h1 {
  margin: 0;
  font-size: 34px;
  letter-spacing: -0.04em;
}

.app-header p {
  margin: 8px 0 0;
  color: #cbd5e1;
  line-height: 1.7;
}

.top-nav {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.top-nav a {
  padding: 10px 15px;
  border-radius: 999px;
  color: white;
  text-decoration: none;
  font-weight: 900;
  background: rgba(255, 255, 255, 0.13);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.workspace {
  max-width: 1320px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 430px 1fr;
  gap: 22px;
  align-items: start;
}

.panel,
.status-panel,
.result-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 28px;
  padding: 22px;
  margin-bottom: 16px;
  box-shadow: 0 20px 52px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(12px);
}

.panel-title {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.panel-title span {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 900;
}

.panel-title h2 {
  margin: 0;
  letter-spacing: -0.025em;
}

.panel-title p {
  margin: 4px 0 0;
  color: #64748b;
}

label {
  display: block;
  margin-top: 14px;
  margin-bottom: 6px;
  color: #334155;
  font-weight: 900;
}

input,
select,
textarea {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #dbe3ef;
  border-radius: 14px;
  box-sizing: border-box;
  outline: none;
  background: white;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
}

textarea {
  resize: vertical;
}

.upload-box {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-top: 16px;
  padding: 16px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid #dbe3ef;
}

.file-input {
  display: none;
}

.file-button {
  flex-shrink: 0;
  padding: 11px 18px;
  border-radius: 14px;
  color: white;
  background: linear-gradient(135deg, #4f46e5, #2563eb);
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(79, 70, 229, 0.24);
}

.file-meta {
  min-width: 0;
}

.file-meta strong {
  display: block;
  color: #0f172a;
  word-break: break-all;
}

.file-meta span {
  display: block;
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
}

.primary-btn,
.secondary-btn,
.danger-btn {
  border: none;
  border-radius: 14px;
  padding: 11px 14px;
  cursor: pointer;
  font-weight: 900;
  transition: transform 0.16s ease, box-shadow 0.16s ease, opacity 0.16s ease;
}

.primary-btn {
  color: white;
  background: linear-gradient(135deg, #4f46e5, #2563eb);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.22);
}

.secondary-btn {
  color: #0f172a;
  background: #eef2f7;
}

.danger-btn {
  color: white;
  background: #dc2626;
}

.primary-btn:hover,
.secondary-btn:hover,
.danger-btn:hover {
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.full {
  width: 100%;
  margin-top: 14px;
}

.generate-btn {
  margin-top: 18px;
}

.message,
.hint {
  color: #64748b;
  line-height: 1.75;
}

.error-text {
  color: #dc2626;
  font-weight: 800;
}

.book-card {
  margin-top: 14px;
  display: grid;
  gap: 10px;
  padding: 15px;
  border-radius: 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.book-card div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.book-card span {
  color: #64748b;
}

.book-card strong {
  text-align: right;
  word-break: break-all;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.status-panel {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.status-panel h2 {
  margin: 0;
  font-size: 22px;
  letter-spacing: -0.025em;
}

.status-meta {
  min-width: 280px;
  padding: 15px;
  border-radius: 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.status-meta div {
  margin-bottom: 8px;
}

.status-meta span {
  display: block;
  color: #64748b;
  font-size: 13px;
}

.status-meta strong {
  word-break: break-all;
}

.status-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.result-grid {
  display: grid;
  grid-template-columns: 0.78fr 1.22fr;
  gap: 18px;
}

.card-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.card-heading h2 {
  margin: 0;
  letter-spacing: -0.025em;
}

.empty-state {
  margin-top: 16px;
  padding: 22px;
  border-radius: 20px;
  color: #64748b;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  text-align: center;
}

.audio-item {
  margin-top: 14px;
  padding: 14px;
  border-radius: 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.audio-title {
  margin-bottom: 8px;
  font-weight: 900;
}

.audio-item audio {
  width: 100%;
}

.audio-item a {
  display: inline-block;
  margin-top: 8px;
  color: #2563eb;
  font-weight: 900;
  text-decoration: none;
}

.script-box {
  white-space: pre-wrap;
  line-height: 1.9;
  min-height: 460px;
  max-height: 700px;
  overflow-y: auto;
  margin-top: 14px;
  padding: 18px;
  border-radius: 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #1e293b;
}

@media (max-width: 1080px) {
  .workspace,
  .result-grid {
    grid-template-columns: 1fr;
  }

  .app-header,
  .status-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .two-col {
    grid-template-columns: 1fr;
  }
}
</style>