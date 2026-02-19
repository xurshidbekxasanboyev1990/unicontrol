/**
 * ============================================
 * UNI CONTROL - Autentifikatsiya Store (Real API)
 * ============================================
 * 
 * Bu store foydalanuvchi autentifikatsiyasini backend API orqali boshqaradi.
 * 
 * FEATURES:
 * ---------
 * - Real JWT authentication (access + refresh tokens)
 * - Token auto-refresh mechanism
 * - Persistent login state
 * - Role-based access control
 * - Error handling with user-friendly messages
 * 
 * ENDPOINTS USED:
 * ---------------
 * POST /auth/login     - Login
 * POST /auth/logout    - Logout
 * POST /auth/refresh   - Token refresh
 * GET  /auth/me        - Get current user
 * POST /auth/change-password - Password change
 * 
 * Author: UniControl Team
 * Version: 2.0.0 (Real API)
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // ===== STATE =====

  /** 
   * Joriy foydalanuvchi ma'lumotlari
   * null = login qilinmagan
   */
  const user = ref(null)

  /** Login holatimi? */
  const isAuthenticated = ref(false)

  /** Yuklanish holati */
  const loading = ref(false)

  /** Xato xabari */
  const error = ref(null)

  /** Login xatosi turi: 'blocked' | 'invalid' | 'network' | null */
  const loginError = ref(null)

  // Rol konstantalari
  const roles = {
    STUDENT: 'student',
    LEADER: 'leader',
    TEACHER: 'teacher',
    ACADEMIC_AFFAIRS: 'academic_affairs',
    REGISTRAR_OFFICE: 'registrar_office',
    DEAN: 'dean',
    ADMIN: 'admin',
    SUPERADMIN: 'superadmin'
  }

  // ===== COMPUTED (GETTERS) =====

  /** Talabami? */
  const isStudent = computed(() => user.value?.role === roles.STUDENT)

  /** Sardormi? */
  const isLeader = computed(() => user.value?.role === roles.LEADER)

  /** O'qituvchimi? */
  const isTeacher = computed(() => user.value?.role === roles.TEACHER)

  /** Akademik ishlar bo'limimi? */
  const isAcademicAffairs = computed(() => user.value?.role === roles.ACADEMIC_AFFAIRS)

  /** Registrator ofisimi? */
  const isRegistrarOffice = computed(() => user.value?.role === roles.REGISTRAR_OFFICE)

  /** Dekanatmi? */
  const isDean = computed(() => user.value?.role === roles.DEAN)

  /** Adminmi? */
  const isAdmin = computed(() => user.value?.role === roles.ADMIN)

  /** Super Adminmi? */
  const isSuperAdmin = computed(() => user.value?.role === roles.SUPERADMIN)

  /** Talabalarni boshqara oladimi? (leader, teacher, academic_affairs, admin, superadmin) */
  const canManageStudents = computed(() =>
    ['leader', 'teacher', 'academic_affairs', 'admin', 'superadmin'].includes(user.value?.role)
  )

  /** Guruhlarni boshqara oladimi? (admin, superadmin) */
  const canManageGroups = computed(() =>
    ['admin', 'superadmin'].includes(user.value?.role)
  )

  /** Bildirishnoma jo'nata oladimi? (superadmin) */
  const canSendNotifications = computed(() =>
    user.value?.role === roles.SUPERADMIN
  )

  /** Foydalanuvchi to'liq ismi */
  const fullName = computed(() => user.value?.name || user.value?.full_name || '')

  /** Foydalanuvchi roli (o'zbek tilida) */
  const roleLabel = computed(() => {
    const labels = {
      student: 'Talaba',
      leader: 'Guruh sardori',
      teacher: 'O\'qituvchi',
      academic_affairs: 'Akademik ishlar',
      registrar_office: 'Registrator ofisi',
      dean: 'Dekanat',
      admin: 'Administrator',
      superadmin: 'Super Administrator'
    }
    return labels[user.value?.role] || 'Noma\'lum'
  })

  // ===== ACTIONS =====

  /**
   * Tizimga kirish (Login)
   * Backend /auth/login endpoint ga so'rov yuboradi
   * 
   * @param {Object} credentials - { login, password }
   * @returns {Object} - { success, user?, message? }
   */
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    loginError.value = null

    try {
      // Backend API ga login so'rovi
      const response = await api.login(credentials.login, credentials.password)

      // User ma'lumotlarini olish
      const userData = await api.getMe()

      // Userning rolini backend format dan frontend format ga o'girish
      const roleMap = {
        'student': 'student',
        'leader': 'leader',
        'teacher': 'teacher',
        'academic_affairs': 'academic_affairs',
        'registrar_office': 'registrar_office',
        'dean': 'dean',
        'admin': 'admin',
        'superadmin': 'superadmin'
      }

      // User obyektini shakllantirish
      user.value = {
        id: userData.id,
        login: userData.login || userData.username,
        role: roleMap[userData.role] || userData.role,
        name: userData.name || userData.full_name,
        full_name: userData.full_name || userData.name,
        email: userData.email,
        phone: userData.phone,
        avatar: userData.avatar,
        studentId: userData.student_id || userData.studentId,
        studentDbId: userData.student_db_id || userData.studentDbId,
        groupId: userData.group_id || userData.groupId,
        group: userData.group_name || userData.group,
        managedGroup: userData.managed_group,
        // Qo'shimcha ma'lumotlar
        hemis_id: userData.hemis_id,
        address: userData.address,
        commute: userData.commute,
        created_at: userData.created_at
      }

      isAuthenticated.value = true

      // LocalStorage ga saqlash (refresh uchun)
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('isAuthenticated', 'true')

      return {
        success: true,
        user: user.value
      }

    } catch (err) {
      console.error('Login error:', err)

      // Xato turini aniqlash
      if (err.status === 401) {
        loginError.value = 'invalid'
        error.value = 'Login yoki parol noto\'g\'ri'
      } else if (err.status === 403) {
        loginError.value = 'blocked'
        error.value = 'Sizning hisobingiz bloklangan. Adminga murojaat qiling.'
      } else if (err.message?.includes('network') || !navigator.onLine) {
        loginError.value = 'network'
        error.value = 'Internet aloqasi yo\'q'
      } else {
        loginError.value = 'error'
        error.value = err.data?.detail || err.message || 'Tizimda xatolik yuz berdi'
      }

      return {
        success: false,
        message: error.value,
        blocked: loginError.value === 'blocked'
      }

    } finally {
      loading.value = false
    }
  }

  /**
   * Tizimdan chiqish (Logout)
   * Backend ga logout so'rovi yuborib, tokenlarni tozalaydi
   */
  const logout = async () => {
    loading.value = true

    try {
      // Backend ga logout so'rovi
      await api.logout()
    } catch (err) {
      // Logout xatosi bo'lsa ham, mahalliy holatni tozalaymiz
      console.warn('Logout API error (ignored):', err)
    } finally {
      // Holatni tozalash
      user.value = null
      isAuthenticated.value = false
      error.value = null
      loginError.value = null

      // LocalStorage tozalash
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')

      loading.value = false
    }
  }

  /**
   * Autentifikatsiyani tekshirish
   * Sahifa yuklanganda chaqiriladi
   * Token bor bo'lsa, user ma'lumotlarini yangilaydi
   * 
   * @returns {boolean} - Autentifikatsiya muvaffaqiyatlimi?
   */
  const checkAuth = async () => {
    // LocalStorage dan tekshirish
    const storedAuth = localStorage.getItem('isAuthenticated')
    const storedUser = localStorage.getItem('user')
    const token = localStorage.getItem('access_token')

    // Token yoki auth yo'q bo'lsa
    if (!token || storedAuth !== 'true') {
      user.value = null
      isAuthenticated.value = false
      return false
    }

    // JWT tokenning exp vaqtini tekshirish (client-side)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const now = Math.floor(Date.now() / 1000)
      if (payload.exp && payload.exp < now) {
        // Access token expired — refresh orqali yangilashga harakat
        const refreshed = await api.refreshToken()
        if (!refreshed) {
          user.value = null
          isAuthenticated.value = false
          localStorage.removeItem('user')
          localStorage.removeItem('isAuthenticated')
          return false
        }
      }
    } catch (e) {
      // Token decode xatosi — davom etamiz, backend tekshiradi
    }

    // Oldingi user ma'lumotlarini yuklash (tez ko'rsatish uchun)
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
        isAuthenticated.value = true
      } catch (e) {
        console.warn('Stored user parse error:', e)
      }
    }

    // Backend dan yangi ma'lumotlarni olish
    try {
      const userData = await api.getMe()

      // Userning rolini yangilash
      const roleMap = {
        'student': 'student',
        'leader': 'leader',
        'teacher': 'teacher',
        'academic_affairs': 'academic_affairs',
        'registrar_office': 'registrar_office',
        'dean': 'dean',
        'admin': 'admin',
        'superadmin': 'superadmin'
      }

      user.value = {
        id: userData.id,
        login: userData.login || userData.username,
        role: roleMap[userData.role] || userData.role,
        name: userData.name || userData.full_name,
        full_name: userData.full_name || userData.name,
        email: userData.email,
        phone: userData.phone,
        avatar: userData.avatar,
        studentId: userData.student_id || userData.studentId,
        studentDbId: userData.student_db_id || userData.studentDbId,
        groupId: userData.group_id || userData.groupId,
        group: userData.group_name || userData.group,
        managedGroup: userData.managed_group,
        hemis_id: userData.hemis_id,
        address: userData.address,
        commute: userData.commute,
        created_at: userData.created_at
      }

      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(user.value))

      return true

    } catch (err) {
      console.error('Auth check error:', err)

      // 401 bo'lsa, token expired
      if (err.status === 401) {
        user.value = null
        isAuthenticated.value = false
        localStorage.removeItem('user')
        localStorage.removeItem('isAuthenticated')
        return false
      }

      // Boshqa xatolar uchun oldingi holatni saqlab qolish
      return isAuthenticated.value
    }
  }

  /**
   * Profil ma'lumotlarini yangilash
   * 
   * @param {Object} updates - Yangilanayotgan maydonlar
   * @returns {Object} - { success, message? }
   */
  const updateProfile = async (updates) => {
    loading.value = true
    error.value = null

    try {
      // Backend ga yangilanishlarni yuborish
      const response = await api.request('/auth/profile', {
        method: 'PATCH',
        body: updates
      })

      // Local state ni yangilash
      Object.keys(updates).forEach(key => {
        if (user.value && key in user.value) {
          user.value[key] = updates[key]
        }
      })

      localStorage.setItem('user', JSON.stringify(user.value))

      return { success: true }

    } catch (err) {
      error.value = err.message || 'Profil yangilashda xatolik'
      return { success: false, message: error.value }

    } finally {
      loading.value = false
    }
  }

  /**
   * Parolni o'zgartirish
   * 
   * @param {string} currentPassword - Joriy parol
   * @param {string} newPassword - Yangi parol
   * @returns {Object} - { success, message? }
   */
  const changePassword = async (currentPassword, newPassword) => {
    loading.value = true
    error.value = null

    try {
      await api.changePassword(currentPassword, newPassword)
      return { success: true, message: 'Parol muvaffaqiyatli o\'zgartirildi' }

    } catch (err) {
      error.value = err.data?.detail || err.message || 'Parol o\'zgartirishda xatolik'
      return { success: false, message: error.value }

    } finally {
      loading.value = false
    }
  }

  /**
   * Foydalanuvchi rolini yangilash
   * Sardor tayinlanganda yoki olib tashlanganda chaqiriladi
   */
  const refreshUserRole = async () => {
    if (!isAuthenticated.value) return

    try {
      const userData = await api.getMe()

      if (user.value) {
        user.value.role = userData.role
        user.value.managedGroup = userData.managed_group
        localStorage.setItem('user', JSON.stringify(user.value))
      }
    } catch (err) {
      console.error('Role refresh error:', err)
    }
  }

  /**
   * Xato xabarini tozalash
   */
  const clearError = () => {
    error.value = null
    loginError.value = null
  }

  // ===== RETURN =====
  return {
    // State
    user,
    isAuthenticated,
    loading,
    error,
    loginError,
    roles,

    // Computed
    isStudent,
    isLeader,
    isTeacher,
    isAcademicAffairs,
    isRegistrarOffice,
    isDean,
    isAdmin,
    isSuperAdmin,
    canManageStudents,
    canManageGroups,
    canSendNotifications,
    fullName,
    roleLabel,

    // Actions
    login,
    logout,
    checkAuth,
    updateProfile,
    changePassword,
    refreshUserRole,
    clearError
  }
})
