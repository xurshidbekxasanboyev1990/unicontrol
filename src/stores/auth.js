import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  // Rol turlari: 'student', 'leader', 'admin', 'superadmin'
  const roles = {
    STUDENT: 'student',
    LEADER: 'leader',
    ADMIN: 'admin',
    SUPERADMIN: 'superadmin'
  }

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

  // Computed
  const isStudent = computed(() => user.value?.role === roles.STUDENT)
  const isLeader = computed(() => user.value?.role === roles.LEADER)
  const isAdmin = computed(() => user.value?.role === roles.ADMIN)
  const isSuperAdmin = computed(() => user.value?.role === roles.SUPERADMIN)
  const canManageStudents = computed(() => ['leader', 'admin', 'superadmin'].includes(user.value?.role))
  const canManageGroups = computed(() => ['admin', 'superadmin'].includes(user.value?.role))
  const canSendNotifications = computed(() => user.value?.role === roles.SUPERADMIN)

  // Login
  const login = (credentials) => {
    const foundUser = demoUsers.find(
      u => u.login === credentials.login && u.password === credentials.password
    )
    
    if (foundUser) {
      user.value = { ...foundUser }
      delete user.value.password
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('isAuthenticated', 'true')
      return { success: true, user: user.value }
    }
    
    return { success: false, message: 'Login yoki parol noto\'g\'ri' }
  }

  // Logout
  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('user')
    localStorage.removeItem('isAuthenticated')
  }

  // Check auth
  const checkAuth = () => {
    const storedUser = localStorage.getItem('user')
    const storedAuth = localStorage.getItem('isAuthenticated')
    
    if (storedUser && storedAuth === 'true') {
      user.value = JSON.parse(storedUser)
      isAuthenticated.value = true
      return true
    }
    return false
  }

  // Update profile (faqat ruxsat etilgan maydonlar)
  const updateProfile = (updates) => {
    const allowedFields = ['phone', 'address', 'commute', 'password']
    
    allowedFields.forEach(field => {
      if (updates[field] !== undefined) {
        user.value[field] = updates[field]
      }
    })
    
    localStorage.setItem('user', JSON.stringify(user.value))
    return { success: true }
  }

  return {
    user,
    isAuthenticated,
    roles,
    demoUsers,
    isStudent,
    isLeader,
    isAdmin,
    isSuperAdmin,
    canManageStudents,
    canManageGroups,
    canSendNotifications,
    login,
    logout,
    checkAuth,
    updateProfile
  }
})
