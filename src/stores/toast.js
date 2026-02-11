/**
 * ============================================
 * UNI CONTROL - Toast Xabarlar Store
 * ============================================
 * 
 * Bu store global toast (popup) xabarlarni boshqaradi.
 * ToastContainer.vue komponenti bilan ishlaydi.
 * 
 * FOYDALANISH:
 * ------------
 * import { useToastStore } from '@/stores/toast'
 * const toast = useToastStore()
 * 
 * toast.success('Muvaffaqiyat!', 'Ma\'lumotlar saqlandi')
 * toast.error('Xatolik!', 'Nimadir noto\'g\'ri ketdi')
 * toast.warning('Ogohlantirish', 'Diqqat!')
 * toast.info('Ma\'lumot', 'Yangi xabar')
 * 
 * TOAST TURLARI:
 * --------------
 * - success: Yashil rang, muvaffaqiyat
 * - error: Qizil rang, xatolik (6 sekund)
 * - warning: Sariq rang, ogohlantirish
 * - info: Ko'k rang, ma'lumot
 * 
 * XUSUSIYATLAR:
 * -------------
 * - Avtomatik yopilish (default: 4 sekund, error: 6 sekund)
 * - X tugmasi bilan qo'lda yopish
 * - Bir vaqtda bir nechta toast ko'rsatish mumkin
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  // ===== STATE =====
  const toasts = ref([])  // Toast xabarlar ro'yxati
  let nextId = 1          // ID generator

  /**
   * Yangi toast qo'shish
   * @param {Object} toast - { type, title, message, duration, closable }
   * @returns {number} Toast ID
   */
  const addToast = (toast) => {
    const id = nextId++
    const newToast = {
      id,
      type: toast.type || 'info',       // success | error | warning | info
      title: toast.title,               // Sarlavha
      message: toast.message,           // Xabar matni
      duration: toast.duration || 4000, // Millisekund (0 = avtomatik yopilmaydi)
      closable: toast.closable !== false
    }
    
    toasts.value.push(newToast)

    // Avtomatik yopish
    if (newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }

    return id
  }

  /**
   * Toast o'chirish
   */
  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  // ===== SHORTCUT METODLAR =====
  const success = (title, message = '') => {
    return addToast({ type: 'success', title, message })
  }

  const error = (title, message = '') => {
    return addToast({ type: 'error', title, message, duration: 6000 })
  }

  const warning = (title, message = '') => {
    return addToast({ type: 'warning', title, message })
  }

  const info = (title, message = '') => {
    return addToast({ type: 'info', title, message })
  }

  /**
   * Barcha toastlarni tozalash
   */
  const clearAll = () => {
    toasts.value = []
  }

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
    clearAll
  }
})
