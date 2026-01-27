import api from './api'

const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo ma'lumotlar
const demoNotifications = [
  { 
    id: 1, 
    title: 'Tizimga xush kelibsiz!', 
    message: 'Uni Control tizimiga muvaffaqiyatli kirdingiz.', 
    type: 'info',
    date: '2024-01-22', 
    read: false,
    createdAt: '2024-01-22T10:00:00Z'
  },
  { 
    id: 2, 
    title: 'Yangi e\'lon', 
    message: 'Ertaga soat 14:00 da umumiy yig\'ilish bo\'ladi.', 
    type: 'announcement',
    date: '2024-01-21', 
    read: true,
    createdAt: '2024-01-21T15:30:00Z'
  },
  { 
    id: 3, 
    title: 'Davomat eslatmasi', 
    message: 'Bugun 2 ta darsda qatnashmadingiz.', 
    type: 'warning',
    date: '2024-01-20', 
    read: true,
    createdAt: '2024-01-20T18:00:00Z'
  },
]

const STORAGE_KEY = 'unicontrol_demo_notifications'

const getDemoNotifications = () => {
  if (DEMO_MODE) {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : [...demoNotifications]
  }
  return []
}

const saveDemoNotifications = (items) => {
  if (DEMO_MODE) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }
}

const notificationsService = {
  /**
   * Barcha bildirishnomalarni olish
   * @param {Object} params - {page, limit, read, type}
   * @returns {Promise<Object>}
   */
  async getAll(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      let notifications = getDemoNotifications()
      
      if (params.read !== undefined) {
        notifications = notifications.filter(n => n.read === params.read)
      }
      
      if (params.type) {
        notifications = notifications.filter(n => n.type === params.type)
      }
      
      // Sort by date (newest first)
      notifications.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      
      const total = notifications.length
      const page = params.page || 1
      const limit = params.limit || 50
      const start = (page - 1) * limit
      const data = notifications.slice(start, start + limit)
      
      return { data, total, page, limit, unreadCount: notifications.filter(n => !n.read).length }
    }

    const response = await api.get('/notifications', { params })
    return response
  },

  /**
   * O'qilmagan bildirishnomalar soni
   * @returns {Promise<number>}
   */
  async getUnreadCount() {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 100))
      const notifications = getDemoNotifications()
      return notifications.filter(n => !n.read).length
    }

    const response = await api.get('/notifications/unread-count')
    return response.count || response
  },

  /**
   * Bildirishnomani o'qilgan deb belgilash
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async markAsRead(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 100))
      const notifications = getDemoNotifications()
      const index = notifications.findIndex(n => n.id === parseInt(id))
      
      if (index !== -1) {
        notifications[index].read = true
        saveDemoNotifications(notifications)
      }
      
      return { success: true }
    }

    const response = await api.put(`/notifications/${id}/read`)
    return response
  },

  /**
   * Barcha bildirishnomalarni o'qilgan deb belgilash
   * @returns {Promise<Object>}
   */
  async markAllAsRead() {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const notifications = getDemoNotifications()
      notifications.forEach(n => n.read = true)
      saveDemoNotifications(notifications)
      return { success: true }
    }

    const response = await api.put('/notifications/read-all')
    return response
  },

  /**
   * Bildirishnomani o'chirish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async delete(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const notifications = getDemoNotifications()
      const index = notifications.findIndex(n => n.id === parseInt(id))
      
      if (index !== -1) {
        notifications.splice(index, 1)
        saveDemoNotifications(notifications)
      }
      
      return { success: true }
    }

    const response = await api.delete(`/notifications/${id}`)
    return response
  },

  /**
   * Bildirishnoma yuborish (admin/superadmin)
   * @param {Object} data - {title, message, type, recipients}
   * @returns {Promise<Object>}
   */
  async send(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const notifications = getDemoNotifications()
      const newId = Math.max(...notifications.map(n => n.id), 0) + 1
      
      const newNotification = {
        ...data,
        id: newId,
        date: new Date().toISOString().split('T')[0],
        read: false,
        createdAt: new Date().toISOString()
      }
      
      notifications.unshift(newNotification)
      saveDemoNotifications(notifications)
      
      return { success: true, data: newNotification }
    }

    const response = await api.post('/notifications/send', data)
    return response
  },

  /**
   * Barcha foydalanuvchilarga bildirishnoma yuborish
   * @param {Object} data - {title, message, type}
   * @returns {Promise<Object>}
   */
  async broadcast(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      return { success: true, message: 'Bildirishnoma yuborildi (demo)' }
    }

    const response = await api.post('/notifications/broadcast', data)
    return response
  }
}

export default notificationsService
