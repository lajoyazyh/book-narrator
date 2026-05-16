import request from '@/api/request'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface NarrationHistoryItem {
  task_id: string
  task_name?: string

  book_id?: string
  book_title?: string
  filename?: string

  mode?: 'page' | 'chapter' | 'custom' | string
  style?: string
  voice?: string
  reading_mode?: 'quick' | 'deep' | string
  output_language?: 'ar' | 'zh' | 'en' | 'fr' | 'ru' | 'es' | string

  start_page?: number
  end_page?: number
  chapter_number?: number
  chapter_title?: string

  task_instruction?: string
  custom_text?: string

  script?: string
  audio_urls?: string[]

  source_info?: string
  status?: string
  error_message?: string

  remark?: string
  favorite?: boolean

  created_at?: string
  updated_at?: string
}

export interface NarrationHistoryUpdateRequest {
  task_name?: string
  remark?: string
  favorite?: boolean
}

export function getNarrationHistory(params?: {
  keyword?: string
  book_id?: string
}) {
  return request.get<ApiResponse<NarrationHistoryItem[]>>(
      '/agent/narration-history',
      { params }
  )
}

export function getNarrationHistoryDetail(taskId: string) {
  return request.get<ApiResponse<NarrationHistoryItem>>(
      `/agent/narration-history/${taskId}`
  )
}

export function updateNarrationHistory(
    taskId: string,
    data: NarrationHistoryUpdateRequest
) {
  return request.put<ApiResponse<NarrationHistoryItem>>(
      `/agent/narration-history/${taskId}`,
      data
  )
}

export function deleteNarrationHistory(taskId: string) {
  return request.delete<ApiResponse<boolean>>(
      `/agent/narration-history/${taskId}`
  )
}