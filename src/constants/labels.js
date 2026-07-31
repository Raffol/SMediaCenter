/**
 * Подписи для значений из app/core/enums.py.
 *
 * Держится синхронно с бэкендом вручную. Если добавите значение в enum
 * на сервере и забудете здесь — интерфейс покажет сырое «in_progress».
 * Поэтому фоллбэк ниже возвращает само значение, а не пустую строку:
 * лучше некрасиво, чем непонятно.
 */

export const REQUEST_STATUS = {
  new: { label: 'Новая', tone: 'wait', icon: 'alert' },
  in_progress: { label: 'В работе', tone: 'live', icon: 'clock' },
  done: { label: 'Выполнена', tone: 'ok', icon: 'check' },
  rejected: { label: 'Отклонена', tone: 'off', icon: 'close' },
}

export const RESPONSE_STATUS = {
  pending: { label: 'Ждёт решения', tone: 'wait', icon: 'clock' },
  accepted: { label: 'Принят', tone: 'ok', icon: 'check' },
  declined: { label: 'Отклонён', tone: 'off', icon: 'close' },
}

export const SERVICE_TYPE = {
  photo: { label: 'Фотосъёмка', icon: 'photo' },
  video: { label: 'Видеосъёмка', icon: 'video' },
  article: { label: 'Написание статей', icon: 'article' },
  design: { label: 'Дизайн', icon: 'design' },
}

export function requestStatus(value) {
  return REQUEST_STATUS[value] ?? { label: value, tone: 'wait', icon: 'alert' }
}

export function responseStatus(value) {
  return RESPONSE_STATUS[value] ?? { label: value, tone: 'wait', icon: 'alert' }
}

export function serviceType(value) {
  return SERVICE_TYPE[value] ?? { label: value, icon: 'alert' }
}

const dateFmt = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

const dateTimeFmt = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

export function formatDate(value) {
  return value ? dateFmt.format(new Date(value)) : ''
}

export function formatDateTime(value) {
  return value ? dateTimeFmt.format(new Date(value)) : ''
}

/** «3 отклика» вместо «3 отклик». */
export function plural(n, forms) {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return forms[0]
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return forms[1]
  return forms[2]
}
