import api from './api'

// Demo mode - backend yo'q bo'lganda ishlaydi
const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo foydalanuvchilar
const demoUsers = [
  {
    id: 1,
    login: 'student',
    password: '123',
    role: 'student',
    name: 'Aliyev Jasur',
    studentId: 'ST-2024-001',
    group: 'KI_25-04',
    phone: '+998 90 123 45 67',
    address: 'Toshkent sh., Chilonzor tumani',
    commute: 'Avtobus #45',
    avatar: null,
    email: 'jasur@uni.uz'
  },
  {
    id: 2,
    login: 'sardor',
    password: '123',
    role: 'leader',
    name: 'Karimov Sardor',
    studentId: 'ST-2024-002',
    group: 'KI_25-04',
    phone: '+998 91 234 56 78',
    address: 'Toshkent sh., Yunusobod tumani',
    commute: 'Metro',
    avatar: null,
    email: 'sardor@uni.uz',
    managedGroup: 'KI_25-04'
  },
  {
    id: 3,
    login: 'admin',
    password: '123',
    role: 'admin',
    name: 'Toshmatov Admin',
    phone: '+998 93 345 67 89',
    avatar: null,
    email: 'admin@uni.uz'
  },
  {
    id: 4,
    login: 'super',
    password: '123',
    role: 'superadmin',
    name: 'Super Administrator',
    phone: '+998 94 456 78 90',
    avatar: null,
    email: 'super@uni.uz'
  }
]

const authService = {
  /**
   * Login qilish
   * @param {Object} credentials - {login, password}
   * @returns {Promise<Object>} - {success, user, token}
   */
  async login(credentials) {
    // Demo mode
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 500)) // Simulate network delay
      
      const foundUser = demoUsers.find(
        u => u.login === credentials.login && u.password === credentials.password
      )
      
      if (foundUser) {
        const user = { ...foundUser }
        delete user.password
        const token = 'demo-token-' + Date.now()
        
        return { success: true, user, token }
      }
      
      throw { message: 'Login yoki parol noto\'g\'ri', status: 401 }
    }

    // Real API
    const response = await api.post('/auth/login', credentials)
    return response
  },

  /**
   * Logout qilish
   * @returns {Promise<void>}
   */
  async logout() {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      return { success: true }
    }

    try {
      await api.post('/auth/logout')
    } catch (error) {
      // Logout xatosi bo'lsa ham davom etamiz
      console.warn('Logout API error:', error)
    }
    
    return { success: true }
  },

  /**
   * Joriy foydalanuvchini olish
   * @returns {Promise<Object>} - user data
   */
  async getCurrentUser() {
    if (DEMO_MODE) {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        return JSON.parse(storedUser)
      }
      throw { message: 'Foydalanuvchi topilmadi', status: 401 }
    }

    const response = await api.get('/auth/me')
    return response.user || response
  },

  /**
   * Token yangilash
   * @returns {Promise<Object>} - {token}
   */
  async refreshToken() {
    if (DEMO_MODE) {
      const token = 'demo-token-refreshed-' + Date.now()
      return { token }
    }

    const response = await api.post('/auth/refresh')
    return response
  },

  /**
   * Profilni yangilash
   * @param {Object} updates - yangilanuvchi maydonlar
   * @returns {Promise<Object>} - yangilangan user
   */
  async updateProfile(updates) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
      const allowedFields = ['phone', 'address', 'commute', 'avatar']
      
      allowedFields.forEach(field => {
        if (updates[field] !== undefined) {
          storedUser[field] = updates[field]
        }
      })
      
      localStorage.setItem('user', JSON.stringify(storedUser))
      return { success: true, user: storedUser }
    }

    const response = await api.put('/auth/profile', updates)
    return response
  },

  /**
   * Parolni o'zgartirish
   * @param {Object} data - {currentPassword, newPassword}
   * @returns {Promise<Object>}
   */
  async changePassword(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      return { success: true, message: 'Parol muvaffaqiyatli o\'zgartirildi' }
    }

    const response = await api.post('/auth/change-password', data)
    return response
  },

  /**
   * Parolni tiklash so'rovi
   * @param {string} email
   * @returns {Promise<Object>}
   */
  async forgotPassword(email) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      return { success: true, message: 'Parolni tiklash havolasi yuborildi' }
    }

    const response = await api.post('/auth/forgot-password', { email })
    return response
  }
}

export default authService
