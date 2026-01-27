import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import authService from '../services/auth.service'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref(null)

  // Rol turlari: 'student', 'leader', 'admin', 'superadmin'
  const roles = {
    STUDENT: 'student',
    LEADER: 'leader',
    ADMIN: 'admin',
    SUPERADMIN: 'superadmin'
  }

  // Computed
  const isStudent = computed(() => user.value?.role === roles.STUDENT)
  const isLeader = computed(() => user.value?.role === roles.LEADER)
  const isAdmin = computed(() => user.value?.role === roles.ADMIN)
  const isSuperAdmin = computed(() => user.value?.role === roles.SUPERADMIN)
  const canManageStudents = computed(() => ['leader', 'admin', 'superadmin'].includes(user.value?.role))
  const canManageGroups = computed(() => ['admin', 'superadmin'].includes(user.value?.role))
  const canSendNotifications = computed(() => user.value?.role === roles.SUPERADMIN)

  // Login
  const login = async (credentials) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authService.login(credentials)

      // Backend response: {access_token, refresh_token, token_type, expires_in, user}
      // Demo response: {success, user, token}
      const accessToken = response.access_token || response.token
      const userData = response.user

      if (userData) {
        user.value = userData
        token.value = accessToken
        isAuthenticated.value = true

        // Token va user ni saqlash
        if (accessToken) {
          localStorage.setItem('token', accessToken)
        }
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token)
        }
        localStorage.setItem('user', JSON.stringify(userData))
        localStorage.setItem('isAuthenticated', 'true')

        return { success: true, user: userData }
      }

      return { success: false, message: response.message || 'Login yoki parol noto\'g\'ri' }
    } catch (err) {
      error.value = err.message || 'Xatolik yuz berdi'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Logout
  const logout = async () => {
    isLoading.value = true

    try {
      await authService.logout()
    } catch (err) {
      console.warn('Logout error:', err)
    } finally {
      // Har qanday holatda tozalash
      user.value = null
      token.value = null
      isAuthenticated.value = false
      error.value = null

      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')

      isLoading.value = false
    }
  }

  // Check auth - sahifa yuklanganda chaqiriladi
  const checkAuth = async () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    const storedAuth = localStorage.getItem('isAuthenticated')

    if (storedUser && storedAuth === 'true') {
      user.value = JSON.parse(storedUser)
      token.value = storedToken
      isAuthenticated.value = true

      // Token bor bo'lsa, serverdan user ma'lumotlarini yangilash
      if (storedToken) {
        try {
          const freshUser = await authService.getCurrentUser()
          if (freshUser) {
            user.value = freshUser
            localStorage.setItem('user', JSON.stringify(freshUser))
          }
        } catch (err) {
          // Token eskirgan bo'lishi mumkin
          if (err.status === 401) {
            await logout()
            return false
          }
        }
      }

      return true
    }

    return false
  }

  // Update profile
  const updateProfile = async (updates) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authService.updateProfile(updates)

      if (response.success || response.user) {
        // Local user ni yangilash
        const allowedFields = ['phone', 'address', 'commute', 'avatar']
        allowedFields.forEach(field => {
          if (updates[field] !== undefined) {
            user.value[field] = updates[field]
          }
        })

        localStorage.setItem('user', JSON.stringify(user.value))
        return { success: true, user: user.value }
      }

      return { success: false, message: response.message || 'Yangilashda xatolik' }
    } catch (err) {
      error.value = err.message || 'Xatolik yuz berdi'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Change password
  const changePassword = async (data) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authService.changePassword(data)
      return { success: true, message: response.message || 'Parol o\'zgartirildi' }
    } catch (err) {
      error.value = err.message || 'Xatolik yuz berdi'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    roles,

    // Computed
    isStudent,
    isLeader,
    isAdmin,
    isSuperAdmin,
    canManageStudents,
    canManageGroups,
    canSendNotifications,

    // Actions
    login,
    logout,
    checkAuth,
    updateProfile,
    changePassword,
    clearError
  }
})
