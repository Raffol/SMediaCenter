import { ref } from 'vue'

/**
 * Маска +7 (999) 123-45-67.
 *
 * Нормализация повторяет логику бэкенда (RequestCreate.normalise_phone):
 * ведущая 8 меняется на 7, наружу уходит +7XXXXXXXXXX. Если правила
 * разъедутся, форма начнёт показывать телефон валидным, а сервер —
 * отклонять его, и причина будет неочевидна.
 */
export function usePhoneMask(initial = '') {
  const display = ref(format(initial))

  function digitsOf(value) {
    let digits = value.replace(/\D/g, '')
    if (digits.startsWith('8')) digits = '7' + digits.slice(1)
    if (digits && !digits.startsWith('7')) digits = '7' + digits
    return digits.slice(0, 11)
  }

  function format(value) {
    const d = digitsOf(value)
    if (!d) return ''

    const parts = ['+7']
    if (d.length > 1) parts.push(` (${d.slice(1, 4)}`)
    if (d.length >= 4) parts.push(') ')
    if (d.length > 4) parts.push(d.slice(4, 7))
    if (d.length > 7) parts.push(`-${d.slice(7, 9)}`)
    if (d.length > 9) parts.push(`-${d.slice(9, 11)}`)
    return parts.join('')
  }

  function onInput(event) {
    display.value = format(event.target.value)
  }

  function isValid() {
    return digitsOf(display.value).length === 11
  }

  /** То, что уходит на сервер. */
  function raw() {
    const d = digitsOf(display.value)
    return d ? `+${d}` : ''
  }

  return { display, onInput, isValid, raw }
}
