import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let nextId = 1

  const addToast = (toast) => {
    const id = nextId++
    const newToast = {
      id,
      type: toast.type || 'info',
      title: toast.title,
      message: toast.message,
      duration: toast.duration || 4000,
      closable: toast.closable !== false
    }
    
    toasts.value.push(newToast)

    if (newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }

    return id
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

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
