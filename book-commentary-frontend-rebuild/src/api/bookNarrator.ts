import request from '@/api/request'

export type OutputLanguage = 'ar' | 'zh' | 'en' | 'fr' | 'ru' | 'es'

export interface NarrateBookRequest {
  task_name?: string
  book_id?: string
  style?: string
  voice?: string
  reading_mode?: string
  output_language?: OutputLanguage
  mode?: string
  start_page?: number
  end_page?: number
  chapter_number?: number
  custom_text?: string
  task_instruction?: string
}

export function uploadBook(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post('/agent/books/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getBooks() {
  return request.get('/agent/books')
}

export function getBookOutline(bookId: string) {
  return request.get(`/agent/books/${bookId}/outline`)
}

export function narrateBook(data: NarrateBookRequest) {
  return request.post('/agent/book-narrate', data)
}

export function cancelNarrationTask(taskId: string) {
  return request.post(`/agent/narration-history/${taskId}/cancel`)
}