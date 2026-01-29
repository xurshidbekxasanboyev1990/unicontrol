/**
 * ============================================
 * UNI CONTROL - Asosiy Ma'lumotlar Store (Real API)
 * ============================================
 * 
 * Bu store barcha asosiy ma'lumotlarni backend API orqali boshqaradi.
 * 
 * FEATURES:
 * ---------
 * - Real-time data from backend
 * - Caching for performance
 * - Pagination support
 * - Search & filter capabilities
 * - Error handling
 * 
 * ENDPOINTS USED:
 * ---------------
 * /groups     - Guruhlar CRUD
 * /students   - Talabalar CRUD
 * /attendance - Davomat
 * /schedule   - Dars jadvali
 * /reports    - Hisobotlar
 * /notifications - Bildirishnomalar
 * /dashboard  - Statistika
 * /excel      - Import/Export
 * 
 * Author: UniControl Team
 * Version: 2.0.0 (Real API)
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../services/api'

export const useDataStore = defineStore('data', () => {
  // ============================================================
  // STATE - Reactive data containers
  // ============================================================

  // === GROUPS ===
  const groups = ref([])
  const groupsLoading = ref(false)
  const groupsError = ref(null)
  const groupsPagination = ref({
    page: 1,
    pageSize: 100,
    total: 0,
    totalPages: 0
  })

  // === STUDENTS ===
  const students = ref([])
  const studentsLoading = ref(false)
  const studentsError = ref(null)
  const studentsPagination = ref({
    page: 1,
    pageSize: 100,
    total: 0,
    totalPages: 0
  })

  // === ATTENDANCE ===
  const attendanceRecords = ref([])
  const attendanceLoading = ref(false)
  const attendanceError = ref(null)

  // === SCHEDULE ===
  const schedules = ref([])
  const schedulesLoading = ref(false)

  // === NOTIFICATIONS ===
  const notifications = ref([])
  const notificationsLoading = ref(false)
  const unreadCount = ref(0)

  // === REPORTS ===
  const reports = ref([])
  const reportsLoading = ref(false)

  // === CLUBS ===
  const clubs = ref([])
  const clubsLoading = ref(false)
  const clubsError = ref(null)

  // === SUBJECTS ===
  const subjects = ref([])
  const subjectsLoading = ref(false)
  const subjectsError = ref(null)

  // === DIRECTIONS ===
  const directions = ref([])
  const directionsLoading = ref(false)
  const directionsError = ref(null)

  // === TOURNAMENTS ===
  const tournaments = ref([])
  const tournamentsLoading = ref(false)
  const tournamentsError = ref(null)

  // === DASHBOARD STATS ===
  const dashboardStats = ref(null)
  const statsLoading = ref(false)

  // === CACHE ===
  const cache = ref({
    groups: { data: null, timestamp: null, ttl: 60000 }, // 1 minute
    students: { data: null, timestamp: null, ttl: 60000 },
    stats: { data: null, timestamp: null, ttl: 30000 }  // 30 seconds
  })

  // ============================================================
  // COMPUTED - Derived data
  // ============================================================

  /** Faol guruhlar */
  const activeGroups = computed(() =>
    groups.value.filter(g => g.is_active !== false)
  )

  /** Faol talabalar */
  const activeStudents = computed(() =>
    students.value.filter(s => s.is_active !== false)
  )

  /** O'qilmagan bildirishnomalar */
  const unreadNotifications = computed(() =>
    notifications.value.filter(n => !n.is_read)
  )

  /** Guruhlar soni */
  const groupsCount = computed(() => groupsPagination.value.total)

  /** Talabalar soni */
  const studentsCount = computed(() => studentsPagination.value.total)

  // ============================================================
  // GROUPS - Guruhlar bilan ishlash
  // ============================================================

  /**
   * Guruhlarni yuklash
   * @param {Object} params - { page, pageSize, search, is_active, course_year, faculty }
   * @param {boolean} forceReload - Cache ni e'tiborsiz qoldirish
   */
  const fetchGroups = async (params = {}, forceReload = false) => {
    // Cache tekshirish
    const cacheEntry = cache.value.groups
    if (!forceReload && cacheEntry.data &&
      Date.now() - cacheEntry.timestamp < cacheEntry.ttl) {
      return cacheEntry.data
    }

    groupsLoading.value = true
    groupsError.value = null

    try {
      const response = await api.getGroups({
        page: params.page || 1,
        page_size: params.pageSize || params.page_size || 500,
        search: params.search,
        is_active: params.is_active,
        course_year: params.course_year,
        faculty: params.faculty
      })

      // Response formatini tekshirish
      if (response.items) {
        groups.value = response.items.map(normalizeGroup)
        groupsPagination.value = {
          page: response.page,
          pageSize: response.page_size,
          total: response.total,
          totalPages: response.total_pages
        }
      } else if (Array.isArray(response)) {
        groups.value = response.map(normalizeGroup)
        groupsPagination.value.total = response.length
      }

      // Cache yangilash
      cache.value.groups = {
        data: groups.value,
        timestamp: Date.now(),
        ttl: 60000
      }

      return groups.value

    } catch (err) {
      console.error('Groups fetch error:', err)
      groupsError.value = err.message || 'Guruhlarni yuklashda xatolik'
      throw err
    } finally {
      groupsLoading.value = false
    }
  }

  /**
   * Bitta guruhni olish
   * @param {number} id - Guruh ID
   */
  const getGroup = async (id) => {
    try {
      const response = await api.getGroup(id)
      return normalizeGroup(response)
    } catch (err) {
      console.error('Get group error:', err)
      throw err
    }
  }

  /**
   * Guruh qo'shish
   * @param {Object} data - Guruh ma'lumotlari
   */
  const addGroup = async (data) => {
    groupsLoading.value = true
    try {
      const response = await api.createGroup({
        name: data.name,
        faculty: data.faculty,
        course_year: data.course_year || data.courseYear,
        education_type: data.education_type || data.educationType || 'kunduzgi',
        contract_amount: data.contract_amount || data.contractAmount || 0,
        is_active: data.is_active !== false
      })

      const newGroup = normalizeGroup(response)
      groups.value.push(newGroup)
      groupsPagination.value.total++

      // Cache invalidate
      cache.value.groups.timestamp = null

      return newGroup
    } catch (err) {
      console.error('Add group error:', err)
      throw err
    } finally {
      groupsLoading.value = false
    }
  }

  /**
   * Guruhni yangilash
   * @param {number} id - Guruh ID
   * @param {Object} data - Yangilanadigan ma'lumotlar
   */
  const updateGroup = async (id, data) => {
    try {
      const response = await api.updateGroup(id, {
        name: data.name,
        faculty: data.faculty,
        course_year: data.course_year || data.courseYear,
        education_type: data.education_type || data.educationType,
        contract_amount: data.contract_amount || data.contractAmount,
        is_active: data.is_active
      })

      const updatedGroup = normalizeGroup(response)
      const index = groups.value.findIndex(g => g.id === id)
      if (index !== -1) {
        groups.value[index] = updatedGroup
      }

      cache.value.groups.timestamp = null
      return updatedGroup
    } catch (err) {
      console.error('Update group error:', err)
      throw err
    }
  }

  /**
   * Guruhni o'chirish
   * @param {number} id - Guruh ID
   */
  const deleteGroup = async (id) => {
    try {
      await api.deleteGroup(id)
      groups.value = groups.value.filter(g => g.id !== id)
      groupsPagination.value.total--
      cache.value.groups.timestamp = null
      return true
    } catch (err) {
      console.error('Delete group error:', err)
      throw err
    }
  }

  /**
   * Guruh holatini o'zgartirish (faol/bloklangan)
   * @param {number} id - Guruh ID
   */
  const toggleGroupStatus = async (id) => {
    try {
      const group = groups.value.find(g => g.id === id)
      if (!group) throw new Error('Guruh topilmadi')

      const response = await api.updateGroup(id, {
        is_active: !group.isActive
      })

      const updatedGroup = normalizeGroup(response)
      const index = groups.value.findIndex(g => g.id === id)
      if (index !== -1) {
        groups.value[index] = updatedGroup
      }

      return updatedGroup
    } catch (err) {
      console.error('Toggle group status error:', err)
      throw err
    }
  }

  /**
   * Guruhga sardor tayinlash
   * @param {number} groupId - Guruh ID
   * @param {number} studentId - Talaba ID (null = sardorni olib tashlash)
   */
  const assignGroupLeader = async (groupId, studentId = null) => {
    try {
      const response = await api.assignGroupLeader(groupId, studentId)

      // Guruhni yangilash
      const updatedGroup = normalizeGroup(response)
      const groupIndex = groups.value.findIndex(g => g.id === groupId)
      if (groupIndex !== -1) {
        groups.value[groupIndex] = updatedGroup
      }

      // Talabani ham yangilash (agar mavjud bo'lsa)
      if (studentId) {
        const studentIndex = students.value.findIndex(s => s.id === studentId)
        if (studentIndex !== -1) {
          students.value[studentIndex].role = 'leader'
        }
      }

      return updatedGroup
    } catch (err) {
      console.error('Assign leader error:', err)
      throw err
    }
  }

  // ============================================================
  // STUDENTS - Talabalar bilan ishlash
  // ============================================================

  /**
   * Talabalarni yuklash
   * @param {Object} params - { page, pageSize, search, group_id, is_active }
   * @param {boolean} forceReload - Cache ni e'tiborsiz qoldirish
   */
  const fetchStudents = async (params = {}, forceReload = false) => {
    // Cache tekshirish
    const cacheEntry = cache.value.students
    if (!forceReload && cacheEntry.data &&
      Date.now() - cacheEntry.timestamp < cacheEntry.ttl &&
      !params.search && !params.group_id) {
      return cacheEntry.data
    }

    studentsLoading.value = true
    studentsError.value = null

    try {
      const response = await api.getStudents({
        page: params.page || 1,
        page_size: params.pageSize || params.page_size || 10000,
        search: params.search,
        group_id: params.group_id || params.groupId,
        is_active: params.is_active
      })

      if (response.items) {
        students.value = response.items.map(normalizeStudent)
        studentsPagination.value = {
          page: response.page,
          pageSize: response.page_size,
          total: response.total,
          totalPages: response.total_pages
        }
      } else if (Array.isArray(response)) {
        students.value = response.map(normalizeStudent)
        studentsPagination.value.total = response.length
      }

      // Cache yangilash (faqat filtrsiz so'rovlar uchun)
      if (!params.search && !params.group_id) {
        cache.value.students = {
          data: students.value,
          timestamp: Date.now(),
          ttl: 60000
        }
      }

      return students.value

    } catch (err) {
      console.error('Students fetch error:', err)
      studentsError.value = err.message || 'Talabalarni yuklashda xatolik'
      throw err
    } finally {
      studentsLoading.value = false
    }
  }

  /**
   * Bitta talabani olish
   * @param {number} id - Talaba ID
   */
  const getStudent = async (id) => {
    try {
      const response = await api.getStudent(id)
      return normalizeStudent(response)
    } catch (err) {
      console.error('Get student error:', err)
      throw err
    }
  }

  /**
   * Talaba qo'shish
   * @param {Object} data - Talaba ma'lumotlari
   */
  const addStudent = async (data) => {
    studentsLoading.value = true
    try {
      const response = await api.createStudent({
        full_name: data.full_name || data.name,
        hemis_id: data.hemis_id || data.studentId,
        group_id: data.group_id || data.groupId,
        phone: data.phone,
        email: data.email,
        address: data.address,
        birth_date: data.birth_date,
        contract_amount: data.contract_amount || data.contractAmount || 0,
        is_active: data.is_active !== false
      })

      const newStudent = normalizeStudent(response)
      students.value.push(newStudent)
      studentsPagination.value.total++

      cache.value.students.timestamp = null
      return newStudent
    } catch (err) {
      console.error('Add student error:', err)
      throw err
    } finally {
      studentsLoading.value = false
    }
  }

  /**
   * Talabani yangilash
   * @param {number} id - Talaba ID
   * @param {Object} data - Yangilanadigan ma'lumotlar
   */
  const updateStudent = async (id, data) => {
    try {
      const response = await api.updateStudent(id, {
        full_name: data.full_name || data.name,
        hemis_id: data.hemis_id || data.studentId,
        group_id: data.group_id || data.groupId,
        phone: data.phone,
        email: data.email,
        address: data.address,
        birth_date: data.birth_date,
        contract_amount: data.contract_amount,
        paid_amount: data.paid_amount,
        is_active: data.is_active
      })

      const updatedStudent = normalizeStudent(response)
      const index = students.value.findIndex(s => s.id === id)
      if (index !== -1) {
        students.value[index] = updatedStudent
      }

      cache.value.students.timestamp = null
      return updatedStudent
    } catch (err) {
      console.error('Update student error:', err)
      throw err
    }
  }

  /**
   * Talabani o'chirish
   * @param {number} id - Talaba ID
   */
  const deleteStudent = async (id) => {
    try {
      await api.deleteStudent(id)
      students.value = students.value.filter(s => s.id !== id)
      studentsPagination.value.total--
      cache.value.students.timestamp = null
      return true
    } catch (err) {
      console.error('Delete student error:', err)
      throw err
    }
  }

  /**
   * Talaba parolini tiklash
   * @param {number} id - Talaba ID
   * @param {string} newPassword - Yangi parol
   */
  const resetStudentPassword = async (id, newPassword) => {
    try {
      await api.resetStudentPassword(id, newPassword)
      return true
    } catch (err) {
      console.error('Reset password error:', err)
      throw err
    }
  }

  // ============================================================
  // ATTENDANCE - Davomat bilan ishlash
  // ============================================================

  /**
   * Davomatni yuklash
   * @param {Object} params - { date, group_id }
   */
  const fetchAttendance = async (params = {}) => {
    attendanceLoading.value = true
    attendanceError.value = null

    try {
      const response = await api.getAttendance(params)

      if (response.items) {
        attendanceRecords.value = response.items.map(normalizeAttendance)
      } else if (Array.isArray(response)) {
        attendanceRecords.value = response.map(normalizeAttendance)
      }

      return attendanceRecords.value
    } catch (err) {
      console.error('Attendance fetch error:', err)
      attendanceError.value = err.message
      throw err
    } finally {
      attendanceLoading.value = false
    }
  }

  /**
   * Kun bo'yicha davomatni olish
   * @param {string} date - Sana (YYYY-MM-DD)
   * @param {number} groupId - Guruh ID
   */
  const getAttendanceByDate = async (date, groupId) => {
    try {
      const response = await api.getAttendanceByDate(date, groupId)
      return Array.isArray(response) ? response.map(normalizeAttendance) : []
    } catch (err) {
      console.error('Get attendance by date error:', err)
      throw err
    }
  }

  /**
   * Davomat qo'shish/yangilash
   * @param {Object} data - { student_id, date, status, reason }
   */
  const saveAttendance = async (data) => {
    try {
      const response = await api.createAttendance({
        student_id: data.student_id || data.studentId,
        date: data.date,
        status: data.status,
        reason: data.reason
      })
      return normalizeAttendance(response)
    } catch (err) {
      console.error('Save attendance error:', err)
      throw err
    }
  }

  /**
   * Ko'p talabaga davomat qo'shish
   * @param {Array} records - Davomat yozuvlari
   */
  const bulkSaveAttendance = async (records) => {
    try {
      const response = await api.bulkCreateAttendance(records.map(r => ({
        student_id: r.student_id || r.studentId,
        date: r.date,
        status: r.status,
        reason: r.reason
      })))
      return response
    } catch (err) {
      console.error('Bulk save attendance error:', err)
      throw err
    }
  }

  /**
   * Kunlik davomat xulosasi
   * @param {string} date - Sana
   * @param {number} groupId - Guruh ID (ixtiyoriy)
   */
  const getDailySummary = async (date = null, groupId = null) => {
    try {
      const response = await api.getAttendanceDailySummary(date, groupId)
      return response
    } catch (err) {
      console.error('Get daily summary error:', err)
      throw err
    }
  }

  /**
   * Guruh davomat statistikasi
   * @param {number} groupId - Guruh ID
   * @param {string} dateFrom - Boshlanish sanasi
   * @param {string} dateTo - Tugash sanasi
   */
  const getGroupAttendanceStats = async (groupId, dateFrom, dateTo) => {
    try {
      const response = await api.getGroupAttendanceSummary(groupId, dateFrom, dateTo)
      return response
    } catch (err) {
      console.error('Get group attendance stats error:', err)
      throw err
    }
  }

  // ============================================================
  // SCHEDULE - Dars jadvali bilan ishlash
  // ============================================================

  /**
   * Dars jadvalini yuklash
   * @param {number} groupId - Guruh ID
   */
  const fetchSchedule = async (groupId = null) => {
    schedulesLoading.value = true

    try {
      const params = groupId ? { group_id: groupId } : {}
      const response = await api.getSchedules(params)

      if (response.items) {
        schedules.value = response.items
      } else if (Array.isArray(response)) {
        schedules.value = response
      }

      return schedules.value
    } catch (err) {
      console.error('Schedule fetch error:', err)
      throw err
    } finally {
      schedulesLoading.value = false
    }
  }

  /**
   * Bugungi dars jadvalini olish
   * @param {number} groupId - Guruh ID
   */
  const getTodaySchedule = async (groupId) => {
    try {
      const response = await api.getTodaySchedule(groupId)
      return response
    } catch (err) {
      console.error('Get today schedule error:', err)
      throw err
    }
  }

  /**
   * Dars qo'shish
   * @param {Object} data - Dars ma'lumotlari
   */
  const addSchedule = async (data) => {
    try {
      const response = await api.createSchedule(data)
      schedules.value.push(response)
      return response
    } catch (err) {
      console.error('Add schedule error:', err)
      throw err
    }
  }

  /**
   * Darsni yangilash
   * @param {number} id - Dars ID
   * @param {Object} data - Yangilanadigan ma'lumotlar
   */
  const updateSchedule = async (id, data) => {
    try {
      const response = await api.updateSchedule(id, data)
      const index = schedules.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schedules.value[index] = response
      }
      return response
    } catch (err) {
      console.error('Update schedule error:', err)
      throw err
    }
  }

  /**
   * Darsni o'chirish
   * @param {number} id - Dars ID
   */
  const deleteSchedule = async (id) => {
    try {
      await api.deleteSchedule(id)
      schedules.value = schedules.value.filter(s => s.id !== id)
      return true
    } catch (err) {
      console.error('Delete schedule error:', err)
      throw err
    }
  }

  // ============================================================
  // NOTIFICATIONS - Bildirishnomalar bilan ishlash
  // ============================================================

  /**
   * Bildirishnomalarni yuklash
   * @param {Object} params - { page, page_size, is_read }
   */
  const fetchNotifications = async (params = {}) => {
    notificationsLoading.value = true

    try {
      const response = await api.getNotifications(params)

      if (response.items) {
        notifications.value = response.items
      } else if (Array.isArray(response)) {
        notifications.value = response
      }

      // O'qilmaganlarni hisoblash
      unreadCount.value = notifications.value.filter(n => !n.is_read).length

      return notifications.value
    } catch (err) {
      console.error('Notifications fetch error:', err)
      throw err
    } finally {
      notificationsLoading.value = false
    }
  }

  /**
   * Bildirishnomani o'qilgan deb belgilash
   * @param {number} id - Bildirishnoma ID
   */
  const markNotificationRead = async (id) => {
    try {
      await api.markNotificationRead(id)
      const index = notifications.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notifications.value[index].is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      return true
    } catch (err) {
      console.error('Mark notification read error:', err)
      throw err
    }
  }

  /**
   * Barcha bildirishnomalarni o'qilgan deb belgilash
   */
  const markAllNotificationsRead = async () => {
    try {
      await api.markAllNotificationsRead()
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
      return true
    } catch (err) {
      console.error('Mark all notifications read error:', err)
      throw err
    }
  }

  /**
   * Bildirishnoma yaratish
   * @param {Object} data - Bildirishnoma ma'lumotlari
   */
  const createNotification = async (data) => {
    try {
      const response = await api.createNotification(data)
      notifications.value.unshift(response)
      return response
    } catch (err) {
      console.error('Create notification error:', err)
      throw err
    }
  }

  /**
   * Ko'pchilikka bildirishnoma yuborish
   * @param {Object} data - { title, message, recipient_type, recipient_ids }
   */
  const sendBulkNotification = async (data) => {
    try {
      const response = await api.sendBulkNotification(data)
      return response
    } catch (err) {
      console.error('Send bulk notification error:', err)
      throw err
    }
  }

  // ============================================================
  // REPORTS - Hisobotlar bilan ishlash
  // ============================================================

  /**
   * Hisobotlarni yuklash
   * @param {Object} params - Filtrlar
   */
  const fetchReports = async (params = {}) => {
    reportsLoading.value = true

    try {
      const response = await api.getReports(params)

      if (response.items) {
        reports.value = response.items
      } else if (Array.isArray(response)) {
        reports.value = response
      }

      return reports.value
    } catch (err) {
      console.error('Reports fetch error:', err)
      throw err
    } finally {
      reportsLoading.value = false
    }
  }

  /**
   * Hisobot yaratish
   * @param {Object} data - Hisobot ma'lumotlari
   */
  const createReport = async (data) => {
    try {
      const response = await api.createReport(data)
      reports.value.unshift(response)
      return response
    } catch (err) {
      console.error('Create report error:', err)
      throw err
    }
  }

  /**
   * Hisobotni o'chirish
   * @param {number} id - Hisobot ID
   */
  const deleteReport = async (id) => {
    try {
      await api.deleteReport(id)
      reports.value = reports.value.filter(r => r.id !== id)
      return true
    } catch (err) {
      console.error('Delete report error:', err)
      throw err
    }
  }

  /**
   * Hisobot generatsiya qilish
   * @param {string} type - Hisobot turi
   * @param {number} groupId - Guruh ID
   * @param {string} startDate - Boshlanish sanasi
   * @param {string} endDate - Tugash sanasi
   */
  const generateReport = async (type, groupId, startDate, endDate) => {
    try {
      const response = await api.generateReport(type, groupId, startDate, endDate)
      return response
    } catch (err) {
      console.error('Generate report error:', err)
      throw err
    }
  }

  // ============================================================
  // DASHBOARD STATS - Statistika
  // ============================================================

  /**
   * Dashboard statistikasini yuklash
   */
  const fetchDashboardStats = async () => {
    // Cache tekshirish
    const cacheEntry = cache.value.stats
    if (cacheEntry.data && Date.now() - cacheEntry.timestamp < cacheEntry.ttl) {
      return cacheEntry.data
    }

    statsLoading.value = true

    try {
      const response = await api.getDashboardStats()
      dashboardStats.value = response

      // Cache saqlash
      cache.value.stats = {
        data: response,
        timestamp: Date.now(),
        ttl: 30000
      }

      return response
    } catch (err) {
      console.error('Dashboard stats fetch error:', err)
      throw err
    } finally {
      statsLoading.value = false
    }
  }

  // ============================================================
  // EXCEL - Import/Export
  // ============================================================

  /**
   * Exceldan import qilish
   * @param {File} file - Excel fayl
   * @param {number} groupId - Guruh ID (ixtiyoriy)
   */
  const importFromExcel = async (file, groupId = null) => {
    try {
      const response = await api.importFromExcel(file, groupId)

      // Cache invalidate
      cache.value.students.timestamp = null
      cache.value.groups.timestamp = null

      // Refresh data
      await fetchStudents({}, true)
      if (!groupId) {
        await fetchGroups({}, true)
      }

      return response
    } catch (err) {
      console.error('Excel import error:', err)
      throw err
    }
  }

  /**
   * Excelga export qilish
   * @param {string} type - 'students' | 'groups' | 'attendance'
   * @param {Object} params - Qo'shimcha parametrlar
   */
  const exportToExcel = async (type, params = {}) => {
    try {
      const blob = await api.exportToExcel(type, params)

      // Faylni yuklab olish
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      return true
    } catch (err) {
      console.error('Excel export error:', err)
      throw err
    }
  }

  // ============================================================
  // HELPER FUNCTIONS - Yordamchi funksiyalar
  // ============================================================

  /**
   * Backend guruh formatini frontend formatiga o'girish
   */
  function normalizeGroup(data) {
    return {
      id: data.id,
      name: data.name,
      faculty: data.faculty,
      courseYear: data.course_year,
      course_year: data.course_year,
      educationType: data.education_type,
      education_type: data.education_type,
      contractAmount: data.contract_amount || 0,
      contract_amount: data.contract_amount || 0,
      isActive: data.is_active !== false,
      is_active: data.is_active !== false,
      leaderId: data.leader_id,
      leader_id: data.leader_id,
      leaderName: data.leader_name,
      leader_name: data.leader_name,
      studentsCount: data.students_count || 0,
      students_count: data.students_count || 0,
      created_at: data.created_at,
      updated_at: data.updated_at
    }
  }

  /**
   * Backend talaba formatini frontend formatiga o'girish
   */
  function normalizeStudent(data) {
    return {
      id: data.id,
      name: data.full_name || data.name,
      full_name: data.full_name || data.name,
      studentId: data.hemis_id || data.student_id,
      hemis_id: data.hemis_id,
      groupId: data.group_id,
      group_id: data.group_id,
      group: data.group_name || data.group,
      group_name: data.group_name,
      phone: data.phone,
      email: data.email,
      address: data.address,
      birthDate: data.birth_date,
      birth_date: data.birth_date,
      role: data.role || 'student',
      isActive: data.is_active !== false,
      is_active: data.is_active !== false,
      contractAmount: data.contract_amount || 0,
      contract_amount: data.contract_amount || 0,
      paidAmount: data.paid_amount || 0,
      paid_amount: data.paid_amount || 0,
      user_id: data.user_id,
      created_at: data.created_at,
      updated_at: data.updated_at
    }
  }

  /**
   * Backend davomat formatini frontend formatiga o'girish
   */
  function normalizeAttendance(data) {
    return {
      id: data.id,
      studentId: data.student_id,
      student_id: data.student_id,
      studentName: data.student_name,
      student_name: data.student_name,
      date: data.date,
      status: data.status,
      reason: data.reason,
      created_by: data.created_by,
      created_at: data.created_at
    }
  }

  /**
   * Guruh ID bo'yicha talabalarni olish
   * @param {number} groupId - Guruh ID
   */
  const getStudentsByGroup = (groupId) => {
    return students.value.filter(s => s.groupId === groupId || s.group_id === groupId)
  }

  /**
   * Guruh ID bo'yicha guruhni olish (local)
   * @param {number} id - Guruh ID
   */
  const getGroupById = (id) => {
    return groups.value.find(g => g.id === id)
  }

  /**
   * Talaba ID bo'yicha talabani olish (local)
   * @param {number} id - Talaba ID
   */
  const getStudentById = (id) => {
    return students.value.find(s => s.id === id)
  }

  /**
   * Cache ni tozalash
   */
  const clearCache = () => {
    cache.value.groups.timestamp = null
    cache.value.students.timestamp = null
    cache.value.stats.timestamp = null
  }

  /**
   * Barcha ma'lumotlarni qayta yuklash
   */
  const refreshAll = async () => {
    clearCache()
    await Promise.all([
      fetchGroups({}, true),
      fetchStudents({}, true),
      fetchDashboardStats()
    ])
  }

  // ============================================================
  // CLUBS - To'garaklar bilan ishlash
  // ============================================================

  /**
   * To'garaklarni yuklash
   */
  const fetchClubs = async (params = {}) => {
    clubsLoading.value = true
    clubsError.value = null
    try {
      const response = await api.getClubs(params)
      if (response?.items) {
        clubs.value = response.items
      } else if (Array.isArray(response)) {
        clubs.value = response
      }
      return clubs.value
    } catch (err) {
      console.error('Clubs fetch error:', err)
      clubsError.value = err.message || 'To\'garaklarni yuklashda xatolik'
      throw err
    } finally {
      clubsLoading.value = false
    }
  }

  /**
   * To'garak qo'shish
   */
  const addClub = async (data) => {
    try {
      const response = await api.createClub(data)
      clubs.value.push(response)
      return response
    } catch (err) {
      console.error('Add club error:', err)
      throw err
    }
  }

  /**
   * To'garakni yangilash
   */
  const updateClub = async (id, data) => {
    try {
      const response = await api.updateClub(id, data)
      const index = clubs.value.findIndex(c => c.id === id)
      if (index !== -1) {
        clubs.value[index] = { ...clubs.value[index], ...response }
      }
      return response
    } catch (err) {
      console.error('Update club error:', err)
      throw err
    }
  }

  /**
   * To'garakni o'chirish
   */
  const deleteClub = async (id) => {
    try {
      await api.deleteClub(id)
      clubs.value = clubs.value.filter(c => c.id !== id)
    } catch (err) {
      console.error('Delete club error:', err)
      throw err
    }
  }

  /**
   * To'garak statusini o'zgartirish
   */
  const toggleClubStatus = async (id) => {
    try {
      const response = await api.toggleClubStatus(id)
      const index = clubs.value.findIndex(c => c.id === id)
      if (index !== -1) {
        clubs.value[index].isActive = !clubs.value[index].isActive
      }
      return response
    } catch (err) {
      console.error('Toggle club status error:', err)
      throw err
    }
  }

  // ============================================================
  // SUBJECTS - Fanlar bilan ishlash
  // ============================================================

  /**
   * Fanlarni yuklash
   */
  const fetchSubjects = async (params = {}) => {
    subjectsLoading.value = true
    subjectsError.value = null
    try {
      const response = await api.getSubjects(params)
      if (response?.items) {
        subjects.value = response.items
      } else if (Array.isArray(response)) {
        subjects.value = response
      }
      return subjects.value
    } catch (err) {
      console.error('Subjects fetch error:', err)
      subjectsError.value = err.message || 'Fanlarni yuklashda xatolik'
      throw err
    } finally {
      subjectsLoading.value = false
    }
  }

  /**
   * Fan qo'shish
   */
  const addSubject = async (data) => {
    try {
      const response = await api.createSubject(data)
      subjects.value.push(response)
      return response
    } catch (err) {
      console.error('Add subject error:', err)
      throw err
    }
  }

  /**
   * Fanni yangilash
   */
  const updateSubject = async (id, data) => {
    try {
      const response = await api.updateSubject(id, data)
      const index = subjects.value.findIndex(s => s.id === id)
      if (index !== -1) {
        subjects.value[index] = { ...subjects.value[index], ...response }
      }
      return response
    } catch (err) {
      console.error('Update subject error:', err)
      throw err
    }
  }

  /**
   * Fanni o'chirish
   */
  const deleteSubject = async (id) => {
    try {
      await api.deleteSubject(id)
      subjects.value = subjects.value.filter(s => s.id !== id)
    } catch (err) {
      console.error('Delete subject error:', err)
      throw err
    }
  }

  /**
   * Fan ID bo'yicha fanni olish
   */
  const getSubjectById = (id) => {
    return subjects.value.find(s => s.id === id)
  }

  // ============================================================
  // DIRECTIONS - Yo'nalishlar bilan ishlash
  // ============================================================

  /**
   * Yo'nalishlarni yuklash
   */
  const fetchDirections = async (params = {}) => {
    directionsLoading.value = true
    directionsError.value = null
    try {
      const response = await api.getDirections(params)
      if (response?.items) {
        directions.value = response.items
      } else if (Array.isArray(response)) {
        directions.value = response
      }
      return directions.value
    } catch (err) {
      console.error('Directions fetch error:', err)
      directionsError.value = err.message || 'Yo\'nalishlarni yuklashda xatolik'
      throw err
    } finally {
      directionsLoading.value = false
    }
  }

  /**
   * Yo'nalish qo'shish
   */
  const addDirection = async (data) => {
    try {
      const response = await api.createDirection(data)
      directions.value.push(response)
      return response
    } catch (err) {
      console.error('Add direction error:', err)
      throw err
    }
  }

  /**
   * Yo'nalishni yangilash
   */
  const updateDirection = async (id, data) => {
    try {
      const response = await api.updateDirection(id, data)
      const index = directions.value.findIndex(d => d.id === id)
      if (index !== -1) {
        directions.value[index] = { ...directions.value[index], ...response }
      }
      return response
    } catch (err) {
      console.error('Update direction error:', err)
      throw err
    }
  }

  /**
   * Yo'nalishni o'chirish
   */
  const deleteDirection = async (id) => {
    try {
      await api.deleteDirection(id)
      directions.value = directions.value.filter(d => d.id !== id)
    } catch (err) {
      console.error('Delete direction error:', err)
      throw err
    }
  }

  /**
   * Yo'nalish statusini o'zgartirish
   */
  const toggleDirectionStatus = async (id) => {
    try {
      const response = await api.toggleDirectionStatus(id)
      const index = directions.value.findIndex(d => d.id === id)
      if (index !== -1) {
        directions.value[index].isActive = !directions.value[index].isActive
      }
      return response
    } catch (err) {
      console.error('Toggle direction status error:', err)
      throw err
    }
  }

  /**
   * Yo'nalish uchun fanlarni yangilash
   */
  const updateDirectionSubjects = async (directionId, subjectIds) => {
    try {
      const response = await api.updateDirectionSubjects(directionId, subjectIds)
      const index = directions.value.findIndex(d => d.id === directionId)
      if (index !== -1) {
        directions.value[index].subjectIds = subjectIds
      }
      return response
    } catch (err) {
      console.error('Update direction subjects error:', err)
      throw err
    }
  }

  /**
   * Guruh ID bo'yicha yo'nalishni olish
   */
  const getDirectionByGroupId = (groupId) => {
    const group = groups.value.find(g => g.id === groupId)
    if (group?.direction_id) {
      return directions.value.find(d => d.id === group.direction_id)
    }
    return null
  }

  // ============================================================
  // TOURNAMENTS - Turnirlar bilan ishlash
  // ============================================================

  /**
   * Turnirlarni yuklash
   */
  const fetchTournaments = async (params = {}) => {
    tournamentsLoading.value = true
    tournamentsError.value = null
    try {
      const response = await api.getTournaments(params)
      if (response?.items) {
        tournaments.value = response.items
      } else if (Array.isArray(response)) {
        tournaments.value = response
      }
      return tournaments.value
    } catch (err) {
      console.error('Tournaments fetch error:', err)
      tournamentsError.value = err.message || 'Turnirlarni yuklashda xatolik'
      throw err
    } finally {
      tournamentsLoading.value = false
    }
  }

  /**
   * Turnir qo'shish
   */
  const addTournament = async (data) => {
    try {
      const response = await api.createTournament(data)
      tournaments.value.push(response)
      return response
    } catch (err) {
      console.error('Add tournament error:', err)
      throw err
    }
  }

  /**
   * Turnirni yangilash
   */
  const updateTournament = async (id, data) => {
    try {
      const response = await api.updateTournament(id, data)
      const index = tournaments.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tournaments.value[index] = { ...tournaments.value[index], ...response }
      }
      return response
    } catch (err) {
      console.error('Update tournament error:', err)
      throw err
    }
  }

  /**
   * Turnir statusini o'zgartirish (faol/nofaol)
   */
  const toggleTournamentStatus = async (id) => {
    try {
      const response = await api.toggleTournamentStatus(id)
      const index = tournaments.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tournaments.value[index] = { ...tournaments.value[index], ...response }
      }
      return response
    } catch (err) {
      console.error('Toggle tournament status error:', err)
      throw err
    }
  }

  /**
   * Turnirni o'chirish
   */
  const deleteTournament = async (id) => {
    try {
      await api.deleteTournament(id)
      tournaments.value = tournaments.value.filter(t => t.id !== id)
    } catch (err) {
      console.error('Delete tournament error:', err)
      throw err
    }
  }

  /**
   * Turnirga ro'yxatdan o'tish
   */
  const registerForTournament = async (tournamentId, studentId) => {
    try {
      const response = await api.registerForTournament(tournamentId, studentId)
      const tournament = tournaments.value.find(t => t.id === tournamentId)
      if (tournament && !tournament.registrations) {
        tournament.registrations = []
      }
      if (tournament) {
        tournament.registrations.push({ student_id: studentId })
      }
      return response
    } catch (err) {
      console.error('Register for tournament error:', err)
      throw err
    }
  }

  /**
   * Turnirdan chiqish
   */
  const unregisterFromTournament = async (tournamentId, studentId) => {
    try {
      const response = await api.unregisterFromTournament(tournamentId, studentId)
      const tournament = tournaments.value.find(t => t.id === tournamentId)
      if (tournament?.registrations) {
        tournament.registrations = tournament.registrations.filter(r => r.student_id !== studentId)
      }
      return response
    } catch (err) {
      console.error('Unregister from tournament error:', err)
      throw err
    }
  }

  /**
   * Talaba turnirga ro'yxatdan o'tganmi tekshirish
   */
  const isStudentRegistered = (tournamentId, studentId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    return tournament?.registrations?.some(r => r.student_id === studentId) || false
  }

  /**
   * Talabaning barcha ro'yxatlarini olish
   */
  const getStudentRegistrations = (studentId) => {
    return tournaments.value.filter(t =>
      t.registrations?.some(r => r.student_id === studentId)
    )
  }

  /**
   * Turnir qatnashish qoidalari mavjudmi
   */
  const hasParticipationRules = (tournamentId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    return !!tournament?.rules?.length
  }

  /**
   * Talaba uchun qatnashish qoidasini olish
   */
  const getParticipationRuleForStudent = (tournamentId, studentId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    return tournament?.rules?.find(r => r.student_id === studentId) || null
  }

  // ============================================================
  // RETURN - Eksport qilinadigan qiymatlar
  // ============================================================

  return {
    // === State ===
    groups,
    groupsLoading,
    groupsError,
    groupsPagination,
    students,
    studentsLoading,
    studentsError,
    studentsPagination,
    attendanceRecords,
    attendanceLoading,
    attendanceError,
    schedules,
    schedulesLoading,
    notifications,
    notificationsLoading,
    unreadCount,
    reports,
    reportsLoading,
    dashboardStats,
    statsLoading,

    // === Computed ===
    activeGroups,
    activeStudents,
    unreadNotifications,
    groupsCount,
    studentsCount,

    // === Groups ===
    fetchGroups,
    getGroup,
    addGroup,
    updateGroup,
    deleteGroup,
    toggleGroupStatus,
    assignGroupLeader,
    getGroupById,

    // === Students ===
    fetchStudents,
    getStudent,
    addStudent,
    updateStudent,
    deleteStudent,
    resetStudentPassword,
    getStudentById,
    getStudentsByGroup,

    // === Attendance ===
    fetchAttendance,
    getAttendanceByDate,
    saveAttendance,
    bulkSaveAttendance,
    getDailySummary,
    getGroupAttendanceStats,

    // === Schedule ===
    fetchSchedule,
    getTodaySchedule,
    addSchedule,
    updateSchedule,
    deleteSchedule,

    // === Notifications ===
    fetchNotifications,
    markNotificationRead,
    markAllNotificationsRead,
    createNotification,
    sendBulkNotification,

    // === Reports ===
    fetchReports,
    createReport,
    deleteReport,
    generateReport,

    // === Stats ===
    fetchDashboardStats,

    // === Excel ===
    importFromExcel,
    exportToExcel,

    // === Clubs ===
    clubs,
    clubsLoading,
    clubsError,
    fetchClubs,
    addClub,
    updateClub,
    deleteClub,
    toggleClubStatus,

    // === Subjects ===
    subjects,
    subjectsLoading,
    subjectsError,
    fetchSubjects,
    addSubject,
    updateSubject,
    deleteSubject,
    getSubjectById,

    // === Directions ===
    directions,
    directionsLoading,
    directionsError,
    fetchDirections,
    addDirection,
    updateDirection,
    deleteDirection,
    toggleDirectionStatus,
    updateDirectionSubjects,
    getDirectionByGroupId,

    // === Tournaments ===
    tournaments,
    tournamentsLoading,
    tournamentsError,
    fetchTournaments,
    addTournament,
    updateTournament,
    deleteTournament,
    toggleTournamentStatus,
    registerForTournament,
    unregisterFromTournament,
    isStudentRegistered,
    getStudentRegistrations,
    hasParticipationRules,
    getParticipationRuleForStudent,

    // === Helpers ===
    clearCache,
    refreshAll
  }
})
