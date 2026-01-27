import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useDataStore } from './data'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loginError = ref(null)

  // Rol turlari: 'student', 'leader', 'admin', 'superadmin'
  const roles = {
    STUDENT: 'student',
    LEADER: 'leader',
    ADMIN: 'admin',
    SUPERADMIN: 'superadmin'
  }

  // Admin va superadmin foydalanuvchilari (tizim administratorlari)
  const adminUsers = ref([
    {
      id: 1001,
      login: 'admin',
      password: '123',
      role: 'admin',
      name: 'Toshmatov Admin',
      phone: '+998 93 345 67 89',
      avatar: null,
      email: 'admin@uni.uz'
    },
    {
      id: 1002,
      login: 'super',
      password: '123',
      role: 'superadmin',
      name: 'Super Administrator',
      phone: '+998 94 456 78 90',
      avatar: null,
      email: 'super@uni.uz'
    }
  ])

  // Computed
  const isStudent = computed(() => user.value?.role === roles.STUDENT)
  const isLeader = computed(() => user.value?.role === roles.LEADER)
  const isAdmin = computed(() => user.value?.role === roles.ADMIN)
  const isSuperAdmin = computed(() => user.value?.role === roles.SUPERADMIN)
  const canManageStudents = computed(() => ['leader', 'admin', 'superadmin'].includes(user.value?.role))
  const canManageGroups = computed(() => ['admin', 'superadmin'].includes(user.value?.role))
  const canSendNotifications = computed(() => user.value?.role === roles.SUPERADMIN)

  // Login - dinamik (dataStore'dan talabalarni tekshiradi)
  const login = (credentials) => {
    loginError.value = null
    const dataStore = useDataStore()
    
    // 1. Admin/SuperAdmin tekshirish
    const adminUser = adminUsers.value.find(
      u => u.login === credentials.login && u.password === credentials.password
    )
    
    if (adminUser) {
      user.value = { ...adminUser }
      delete user.value.password
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('isAuthenticated', 'true')
      return { success: true, user: user.value }
    }
    
    // 2. Talaba/Sardor tekshirish (studentId bilan login)
    const student = dataStore.students.find(
      s => s.studentId === credentials.login && s.password === credentials.password
    )
    
    if (student) {
      // Guruh holatini tekshirish
      const group = dataStore.groups.find(g => g.name === student.group)
      
      if (!group || !group.isActive) {
        loginError.value = 'blocked'
        return { 
          success: false, 
          blocked: true,
          message: 'Guruhingiz ruxsatga ega emas. Iltimos, adminga murojaat qiling.' 
        }
      }
      
      // Talabaning hozirgi roli (sardor yoki oddiy talaba)
      const role = student.role || 'student'
      
      user.value = {
        id: student.id,
        login: student.studentId,
        role: role,
        name: student.name,
        studentId: student.studentId,
        groupId: student.groupId,
        group: student.group,
        phone: student.phone,
        address: student.address,
        commute: student.commute,
        avatar: student.avatar,
        email: student.email,
        managedGroup: role === 'leader' ? student.group : null
      }
      
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('isAuthenticated', 'true')
      return { success: true, user: user.value }
    }
    
    return { success: false, message: 'Talaba ID yoki parol noto\'g\'ri' }
  }

  // Logout
  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    loginError.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('isAuthenticated')
  }

  // Check auth
  const checkAuth = () => {
    const storedUser = localStorage.getItem('user')
    const storedAuth = localStorage.getItem('isAuthenticated')
    
    if (storedUser && storedAuth === 'true') {
      const parsedUser = JSON.parse(storedUser)
      
      // Agar talaba yoki sardor bo'lsa, roli yangilangan bo'lishi mumkin
      if (parsedUser.studentId) {
        const dataStore = useDataStore()
        const student = dataStore.students.find(s => s.studentId === parsedUser.studentId)
        
        if (student) {
          // Guruh holatini tekshirish
          const group = dataStore.groups.find(g => g.name === student.group)
          if (!group || !group.isActive) {
            logout()
            return false
          }
          
          // Rolni yangilash (sardor bo'lsa leader, aks holda student)
          parsedUser.role = student.role || 'student'
          parsedUser.managedGroup = student.role === 'leader' ? student.group : null
        }
      }
      
      user.value = parsedUser
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(user.value))
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

  // Foydalanuvchi rolini yangilash
  const refreshUserRole = () => {
    if (user.value?.studentId) {
      const dataStore = useDataStore()
      const student = dataStore.students.find(s => s.studentId === user.value.studentId)
      
      if (student) {
        user.value.role = student.role || 'student'
        user.value.managedGroup = student.role === 'leader' ? student.group : null
        localStorage.setItem('user', JSON.stringify(user.value))
      }
    }
  }

  return {
    user,
    isAuthenticated,
    loginError,
    roles,
    adminUsers,
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
    updateProfile,
    refreshUserRole
  }
})
