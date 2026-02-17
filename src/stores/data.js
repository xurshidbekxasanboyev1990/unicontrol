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
  // Alias for backward compatibility
  const schedule = computed(() => schedules.value)

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

  // === DIRECTION-SUBJECTS MAPPING ===
  const directionSubjects = ref([])

  // === TOURNAMENTS ===
  const tournaments = ref([])
  const tournamentsLoading = ref(false)
  const tournamentsError = ref(null)

  // === DASHBOARD STATS ===
  const dashboardStats = ref(null)
  const statsLoading = ref(false)

  // === CACHE ===
  const POLLING_INTERVAL = 60000 // 60 sekund (1 daqiqa)
  const NOTIFICATION_POLL_INTERVAL = 30000 // 30 sekund — faqat bildirishnomalar uchun
  const cache = ref({
    groups: { data: null, timestamp: null, ttl: 120000 },    // 2 daqiqa
    students: { data: null, timestamp: null, ttl: 120000 },  // 2 daqiqa
    stats: { data: null, timestamp: null, ttl: 60000 },      // 1 daqiqa
    notifications: { data: null, timestamp: null, ttl: 30000 } // 30 sekund
  })

  // === REAL-TIME POLLING ===
  let pollingTimer = null
  let notifPollingTimer = null
  let visibilityHandler = null
  const pollingActive = ref(false)
  // Qaysi data turlarini kuzatish kerakligini saqlaydi
  const activeSubscriptions = ref(new Set())

  /**
   * Faqat bildirishnomalar sonini tekshirish (yengil so'rov)
   */
  const pollNotificationsOnly = async () => {
    try {
      const result = await api.getUnreadNotificationCount()
      if (typeof result === 'number') {
        unreadCount.value = result
      } else if (result && typeof result.count === 'number') {
        unreadCount.value = result.count
      }
    } catch { /* silent */ }
  }

  /**
   * Real-time polling ni ishga tushirish
   * Sahifa ochilganda chaqiriladi
   * - Og'ir ma'lumotlar (groups, students, stats) har 60 sekundda
   * - Bildirishnomalar har 30 sekundda (yengil endpoint)
   * @param {Array<string>} dataTypes - kuzatish kerak bo'lgan turlar
   */
  const startPolling = (dataTypes = ['groups', 'students', 'stats', 'notifications']) => {
    // Avval eski polling ni to'xtatish
    stopPolling()

    dataTypes.forEach(t => activeSubscriptions.value.add(t))
    pollingActive.value = true

    // Birinchi marta darhol yuklash
    pollOnce()

    // Og'ir ma'lumotlar uchun sekin interval (60s)
    pollingTimer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        pollOnce()
      }
    }, POLLING_INTERVAL)

    // Bildirishnomalar uchun tezroq interval (30s) — yengil endpoint
    if (dataTypes.includes('notifications')) {
      notifPollingTimer = setInterval(() => {
        if (document.visibilityState === 'visible') {
          pollNotificationsOnly()
        }
      }, NOTIFICATION_POLL_INTERVAL)
    }

    // Tab ko'rinishida bo'lsa refresh
    visibilityHandler = () => {
      if (document.visibilityState === 'visible') {
        pollOnce()
      }
    }
    document.addEventListener('visibilitychange', visibilityHandler)
  }

  /**
   * Polling ni to'xtatish - sahifadan chiqayotganda chaqiriladi
   */
  const stopPolling = () => {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
    if (notifPollingTimer) {
      clearInterval(notifPollingTimer)
      notifPollingTimer = null
    }
    if (visibilityHandler) {
      document.removeEventListener('visibilitychange', visibilityHandler)
      visibilityHandler = null
    }
    pollingActive.value = false
    activeSubscriptions.value.clear()
  }

  /**
   * Bir martalik poll — barcha active subscriptions ni yangilaydi
   * Loading indikatori ko'rsatmaydi (background refresh)
   * Cache TTL ni hurmat qiladi — agar cache hali yangi bo'lsa, skip qiladi
   */
  const pollOnce = async () => {
    const subs = activeSubscriptions.value
    const promises = []
    const now = Date.now()

    // Cache bor turlar — faqat TTL tugaganda yuklaydi
    const shouldFetch = (type) => {
      const c = cache.value[type]
      return !c || !c.data || !c.timestamp || (now - c.timestamp >= (c.ttl || 60000))
    }

    if (subs.has('groups') && shouldFetch('groups')) promises.push(fetchGroups({}, true).catch(() => { }))
    if (subs.has('students') && shouldFetch('students')) promises.push(fetchStudents({}, true).catch(() => { }))
    if (subs.has('stats') && shouldFetch('stats')) promises.push(fetchDashboardStats().catch(() => { }))
    if (subs.has('notifications') && shouldFetch('notifications')) promises.push(fetchNotifications().catch(() => { }))
    if (subs.has('attendance')) promises.push(fetchAttendance().catch(() => { }))
    if (subs.has('schedule')) promises.push(fetchSchedule().catch(() => { }))
    if (subs.has('clubs')) promises.push(fetchClubs().catch(() => { }))
    if (subs.has('subjects')) promises.push(fetchSubjects().catch(() => { }))
    if (subs.has('directions')) promises.push(fetchDirections().catch(() => { }))
    if (subs.has('tournaments')) promises.push(fetchTournaments().catch(() => { }))
    if (subs.has('reports')) promises.push(fetchReports().catch(() => { }))

    if (promises.length > 0) {
      await Promise.allSettled(promises)
    }
  }

  /**
   * CRUD operatsiyadan keyin tegishli ma'lumotlarni darhol yangilash
   * @param {Array<string>} dataTypes - yangilanishi kerak bo'lgan turlar
   */
  const invalidateAndRefresh = async (...dataTypes) => {
    dataTypes.forEach(type => {
      if (cache.value[type]) {
        cache.value[type].timestamp = null
      }
    })
    // Agar polling faol bo'lsa, shunchaki cache invalidate qilish yetarli
    // Polling keyingi tsiklda yangilab beradi
    // Lekin tezroq ko'rsatish uchun darhol pollOnce
    const oldSubs = new Set(activeSubscriptions.value)
    dataTypes.forEach(t => activeSubscriptions.value.add(t))
    await pollOnce()
    // Eski subscriptions ni qaytarish
    activeSubscriptions.value = oldSubs
  }

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
        page_size: params.pageSize || params.page_size || 100,
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
        ttl: 120000
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

      // Real-time: yangilash
      cache.value.groups.timestamp = null
      invalidateAndRefresh('groups', 'stats')

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
      invalidateAndRefresh('groups', 'stats')
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
      invalidateAndRefresh('groups', 'stats')
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
        page_size: params.pageSize || params.page_size || 200,
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
          ttl: 120000
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
      invalidateAndRefresh('students', 'stats', 'groups')
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
      invalidateAndRefresh('students', 'stats')
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
      invalidateAndRefresh('students', 'stats', 'groups')
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
      invalidateAndRefresh('attendance', 'stats')
      return normalizeAttendance(response)
    } catch (err) {
      console.error('Save attendance error:', err)
      throw err
    }
  }

  /**
   * Ko'p talabaga davomat qo'shish
   * @param {Object|Array} data - AttendanceBatch ({date, subject, lesson_number, attendances}) yoki legacy array
   */
  const bulkSaveAttendance = async (data) => {
    try {
      // Agar array kelsa, legacy formatni AttendanceBatch ga o'girish
      let batchData = data
      if (Array.isArray(data)) {
        batchData = {
          date: data[0]?.date || new Date().toISOString().split('T')[0],
          subject: data[0]?.subject || null,
          lesson_number: data[0]?.lesson_number || null,
          attendances: data.map(r => ({
            student_id: r.student_id || r.studentId,
            status: r.status || 'absent',
            note: r.reason || r.note || null,
            late_minutes: r.late_minutes || 0
          }))
        }
      }
      const response = await api.bulkCreateAttendance(batchData)
      invalidateAndRefresh('attendance', 'stats')
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
  const mapSchedule = (s) => ({
    ...s,
    groupId: s.group_id ?? s.groupId,
    groupName: s.group_name ?? s.groupName,
    subjectCode: s.subject_code ?? s.subjectCode,
    subjectName: s.subject ?? s.subjectName,
    scheduleType: s.schedule_type ?? s.scheduleType,
    dayOfWeek: s.day_of_week ?? s.dayOfWeek,
    day: s.day_of_week ?? s.dayOfWeek ?? s.day,
    specificDate: s.specific_date ?? s.specificDate,
    startTime: s.start_time ?? s.startTime,
    endTime: s.end_time ?? s.endTime,
    time: s.time_range ?? (s.time || `${s.start_time ?? s.startTime ?? ''} - ${s.end_time ?? s.endTime ?? ''}`),
    lessonNumber: s.lesson_number ?? s.lessonNumber,
    roomNumber: s.room ?? s.roomNumber,
    teacherName: s.teacher_name ?? s.teacherName,
    teacherId: s.teacher_id ?? s.teacherId,
    teacher: s.teacher_name ?? s.teacherName ?? s.teacher,
    isActive: s.is_active ?? s.isActive ?? true,
    isCancelled: s.is_cancelled ?? s.isCancelled ?? false,
    cancellationReason: s.cancellation_reason ?? s.cancellationReason,
    academicYear: s.academic_year ?? s.academicYear,
    durationMinutes: s.duration_minutes ?? s.durationMinutes,
    createdAt: s.created_at ?? s.createdAt,
    updatedAt: s.updated_at ?? s.updatedAt,
  })

  const fetchSchedule = async (groupId = null) => {
    schedulesLoading.value = true

    try {
      const params = groupId ? { group_id: groupId } : {}
      const response = await api.getSchedules(params)

      if (response.items) {
        schedules.value = response.items.map(mapSchedule)
      } else if (Array.isArray(response)) {
        schedules.value = response.map(mapSchedule)
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
      schedules.value.push(mapSchedule(response))
      invalidateAndRefresh('schedule')
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
        schedules.value[index] = mapSchedule(response)
      }
      invalidateAndRefresh('schedule')
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
      invalidateAndRefresh('schedule')
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
  const mapNotification = (n) => ({
    ...n,
    read: n.is_read ?? n.read ?? false,
    isRead: n.is_read ?? n.isRead ?? false,
    readAt: n.read_at ?? n.readAt,
    action: n.action_url ?? n.action,
    actionUrl: n.action_url ?? n.actionUrl,
    actionText: n.action_text ?? n.actionText,
    senderId: n.sender_id ?? n.senderId,
    senderName: n.sender_name ?? n.senderName,
    pushSent: n.push_sent ?? n.pushSent ?? false,
    emailSent: n.email_sent ?? n.emailSent ?? false,
    expiresAt: n.expires_at ?? n.expiresAt,
    createdAt: n.created_at ?? n.createdAt,
    date: n.created_at ?? n.createdAt ?? n.date,
    time: n.created_at ? new Date(n.created_at).toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' }) : (n.time || ''),
    userId: n.user_id ?? n.userId,
  })

  const fetchNotifications = async (params = {}, forceReload = false) => {
    // Cache tekshirish
    const cacheEntry = cache.value.notifications
    if (!forceReload && cacheEntry && cacheEntry.data &&
      cacheEntry.timestamp && Date.now() - cacheEntry.timestamp < cacheEntry.ttl) {
      return cacheEntry.data
    }

    notificationsLoading.value = true

    try {
      const response = await api.getNotifications(params)

      if (response.items) {
        notifications.value = response.items.map(mapNotification)
        // Use unread_count from backend response if available
        if (typeof response.unread_count === 'number') {
          unreadCount.value = response.unread_count
        } else {
          unreadCount.value = notifications.value.filter(n => !n.read && !n.isRead).length
        }
      } else if (Array.isArray(response)) {
        notifications.value = response.map(mapNotification)
        unreadCount.value = notifications.value.filter(n => !n.read && !n.isRead).length
      }

      // Cache yangilash
      cache.value.notifications = {
        data: notifications.value,
        timestamp: Date.now(),
        ttl: 30000
      }

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
        notifications.value[index].read = true
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
      notifications.value.forEach(n => { n.is_read = true; n.read = true })
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
      notifications.value.unshift(mapNotification(response))
      invalidateAndRefresh('notifications')
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
      invalidateAndRefresh('notifications')
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
  const mapReport = (r) => ({
    ...r,
    reportType: r.report_type ?? r.reportType,
    dateFrom: r.date_from ?? r.dateFrom,
    dateTo: r.date_to ?? r.dateTo,
    groupId: r.group_id ?? r.groupId,
    groupName: r.group_name ?? r.groupName,
    createdBy: r.created_by ?? r.createdBy,
    createdByName: r.created_by_name ?? r.createdByName,
    filePath: r.file_path ?? r.filePath,
    fileSize: r.file_size ?? r.fileSize,
    downloadUrl: r.download_url ?? r.downloadUrl,
    startedAt: r.started_at ?? r.startedAt,
    completedAt: r.completed_at ?? r.completedAt,
    processingTime: r.processing_time ?? r.processingTime,
    errorMessage: r.error_message ?? r.errorMessage,
    aiResult: r.ai_result ?? r.aiResult,
    downloadCount: r.download_count ?? r.downloadCount ?? 0,
    expiresAt: r.expires_at ?? r.expiresAt,
    createdAt: r.created_at ?? r.createdAt,
    updatedAt: r.updated_at ?? r.updatedAt,
  })

  const fetchReports = async (params = {}) => {
    reportsLoading.value = true

    try {
      const response = await api.getReports(params)

      if (response.items) {
        reports.value = response.items.map(mapReport)
      } else if (Array.isArray(response)) {
        reports.value = response.map(mapReport)
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
      invalidateAndRefresh('reports')
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
      invalidateAndRefresh('reports')
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
        ttl: 60000
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
      await invalidateAndRefresh('students', 'groups', 'stats')

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
      studentCount: data.students_count || 0,
      students_count: data.students_count || 0,
      created_at: data.created_at,
      updated_at: data.updated_at
    }
  }

  /**
   * Backend talaba formatini frontend formatiga o'girish
   */
  function normalizeStudent(data) {
    const studentName = data.full_name || data.name || 'Ism kiritilmagan'
    return {
      id: data.id,
      name: studentName,
      full_name: studentName,
      studentId: data.hemis_id || data.student_id || '',
      student_id: data.student_id || data.hemis_id || '',
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
      faculty: data.faculty,
      commute: data.commute,
      role: data.role || 'student',
      isActive: data.is_active !== false,
      is_active: data.is_active !== false,
      contractAmount: data.contract_amount || 0,
      contract_amount: data.contract_amount || 0,
      contractPaid: data.contract_paid ?? data.contractPaid ?? false,
      contract_paid: data.contract_paid ?? data.contractPaid ?? false,
      paidAmount: data.paid_amount || 0,
      paid_amount: data.paid_amount || 0,
      user_id: data.user_id,
      createdAt: data.created_at,
      created_at: data.created_at,
      updatedAt: data.updated_at,
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
    cache.value.notifications.timestamp = null
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
  const mapClub = (c) => ({
    ...c,
    isActive: c.is_active ?? c.isActive ?? true,
    maxMembers: c.max_members ?? c.maxMembers ?? 30,
    membersCount: c.members_count ?? c.membersCount ?? 0,
    createdAt: c.created_at ?? c.createdAt,
    updatedAt: c.updated_at ?? c.updatedAt,
  })

  const fetchClubs = async (params = {}) => {
    clubsLoading.value = true
    clubsError.value = null
    try {
      const response = await api.getClubs(params)
      if (response?.items) {
        clubs.value = response.items.map(mapClub)
      } else if (Array.isArray(response)) {
        clubs.value = response.map(mapClub)
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
      clubs.value.push(mapClub(response))
      invalidateAndRefresh('clubs')
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
        clubs.value[index] = { ...clubs.value[index], ...mapClub(response) }
      }
      invalidateAndRefresh('clubs')
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
      invalidateAndRefresh('clubs')
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
  const mapSubject = (s) => ({
    ...s,
    isActive: s.is_active ?? s.isActive ?? true,
    hoursPerWeek: s.hours_per_week ?? s.hoursPerWeek ?? 2,
    createdAt: s.created_at ?? s.createdAt,
    updatedAt: s.updated_at ?? s.updatedAt,
  })

  const fetchSubjects = async (params = {}) => {
    subjectsLoading.value = true
    subjectsError.value = null
    try {
      const response = await api.getSubjects(params)
      if (response?.items) {
        subjects.value = response.items.map(mapSubject)
      } else if (Array.isArray(response)) {
        subjects.value = response.map(mapSubject)
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
      subjects.value.push(mapSubject(response))
      invalidateAndRefresh('subjects')
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
        subjects.value[index] = { ...subjects.value[index], ...mapSubject(response) }
      }
      invalidateAndRefresh('subjects')
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
      invalidateAndRefresh('subjects')
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
  const mapDirection = (d) => ({
    ...d,
    isActive: d.is_active ?? d.isActive ?? true,
    durationYears: d.duration_years ?? d.durationYears ?? 4,
    subjectIds: d.subject_ids ?? d.subjectIds ?? [],
    createdAt: d.created_at ?? d.createdAt,
    updatedAt: d.updated_at ?? d.updatedAt,
  })

  const fetchDirections = async (params = {}) => {
    directionsLoading.value = true
    directionsError.value = null
    try {
      const response = await api.getDirections(params)
      if (response?.items) {
        directions.value = response.items.map(mapDirection)
      } else if (Array.isArray(response)) {
        directions.value = response.map(mapDirection)
      }
      // directionSubjects mapping ni yangilash
      directionSubjects.value = directions.value
        .filter(d => d.subjectIds && d.subjectIds.length > 0)
        .map(d => ({ directionId: d.id, subjectIds: d.subjectIds || [] }))
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
      directions.value.push(mapDirection(response))
      invalidateAndRefresh('directions')
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
        directions.value[index] = { ...directions.value[index], ...mapDirection(response) }
      }
      invalidateAndRefresh('directions')
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
      invalidateAndRefresh('directions')
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
      // directionSubjects mapping ni yangilash
      const dsIndex = directionSubjects.value.findIndex(ds => ds.directionId === directionId)
      if (dsIndex !== -1) {
        directionSubjects.value[dsIndex].subjectIds = subjectIds
      } else {
        directionSubjects.value.push({ directionId, subjectIds })
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

  /**
   * ID bo'yicha yo'nalishni olish
   */
  const getDirectionById = (id) => {
    return directions.value.find(d => d.id === id)
  }

  /**
   * Turnir ro'yxatdagi talaba statusini yangilash
   */
  const updateRegistrationStatus = (tournamentId, regId, status) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    if (tournament?.registrations) {
      const reg = tournament.registrations.find(r => r.id === regId)
      if (reg) {
        reg.status = status
      }
    }
  }

  // ============================================================
  // TOURNAMENTS - Turnirlar bilan ishlash
  // ============================================================

  /**
   * Turnirlarni yuklash
   */
  const mapTournament = (t) => ({
    ...t,
    title: t.name || t.title,
    isActive: t.is_active ?? t.isActive ?? true,
    startDate: t.start_date ?? t.startDate,
    endDate: t.end_date ?? t.endDate,
    registrationDeadline: t.registration_deadline ?? t.registrationDeadline,
    maxParticipants: t.max_participants ?? t.maxParticipants ?? 100,
    registrationsCount: t.registrations_count ?? t.registrationsCount ?? 0,
    createdAt: t.created_at ?? t.createdAt,
    updatedAt: t.updated_at ?? t.updatedAt,
  })

  const fetchTournaments = async (params = {}) => {
    tournamentsLoading.value = true
    tournamentsError.value = null
    try {
      const response = await api.getTournaments(params)
      if (response?.items) {
        tournaments.value = response.items.map(mapTournament)
      } else if (Array.isArray(response)) {
        tournaments.value = response.map(mapTournament)
      }
      // Load student's existing registrations
      try {
        const myRegs = await api.getMyTournamentRegistrations()
        if (Array.isArray(myRegs)) {
          myRegs.forEach(reg => {
            studentTournamentRegistrations.value[reg.tournament_id] = reg
          })
        }
      } catch (e) {
        // Ignore - not a student or no registrations
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
      tournaments.value.push(mapTournament(response))
      invalidateAndRefresh('tournaments')
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
        tournaments.value[index] = { ...tournaments.value[index], ...mapTournament(response) }
      }
      invalidateAndRefresh('tournaments')
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
      invalidateAndRefresh('tournaments')
    } catch (err) {
      console.error('Delete tournament error:', err)
      throw err
    }
  }

  /**
   * Turnirga ro'yxatdan o'tish
   */
  const registerForTournament = async (tournamentId, data) => {
    try {
      // data bo'lishi mumkin: integer (studentId) yoki object ({ studentId, studentDbId, ... })
      let studentId
      if (typeof data === 'object') {
        studentId = data.studentDbId || data.student_db_id || data.studentId || data.student_id || data.id
      } else {
        studentId = data
      }
      // studentId raqam ekanligini tekshirish
      studentId = parseInt(studentId)
      if (!studentId || isNaN(studentId)) {
        throw new Error('Student ID topilmadi')
      }
      const response = await api.registerForTournament(tournamentId, studentId)
      const tournament = tournaments.value.find(t => t.id === tournamentId)
      if (tournament) {
        tournament.registrationsCount = (tournament.registrationsCount || 0) + 1
      }
      // Track student registration locally
      studentTournamentRegistrations.value[tournamentId] = response || { student_id: studentId, status: 'registered' }
      return { success: true, data: response }
    } catch (err) {
      console.error('Register for tournament error:', err)
      // If already registered (409), mark locally and return friendly message
      const errMsg = err?.message || err?.detail || ''
      if (errMsg.includes('allaqachon') || errMsg.includes('409')) {
        studentTournamentRegistrations.value[tournamentId] = { student_id: studentId, status: 'registered' }
        return { success: false, message: "Siz bu turnirga allaqachon ro'yxatdan o'tgansiz ✅", alreadyRegistered: true }
      }
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
      if (tournament) {
        tournament.registrationsCount = Math.max(0, (tournament.registrationsCount || 0) - 1)
      }
      delete studentTournamentRegistrations.value[tournamentId]
      return response
    } catch (err) {
      console.error('Unregister from tournament error:', err)
      throw err
    }
  }

  /**
   * Talaba turnirga ro'yxatdan o'tganmi tekshirish
   */
  // Talabaning ro'yxatdan o'tgan turnir ID lari (backenddan yuklanganda to'ldiriladi)
  const studentTournamentRegistrations = ref({})

  const isStudentRegistered = (tournamentId, studentId) => {
    return !!studentTournamentRegistrations.value[tournamentId]
  }

  /**
   * Talabaning barcha ro'yxatlarini olish
   */
  const getStudentRegistrations = (studentId) => {
    const results = []
    Object.entries(studentTournamentRegistrations.value).forEach(([tid, reg]) => {
      const tournament = tournaments.value.find(t => t.id === parseInt(tid))
      if (tournament) {
        results.push({ tournament, registration: reg })
      }
    })
    return results
  }

  /**
   * Turnir ishtirokchilarini backenddan yuklash
   */
  const fetchTournamentParticipants = async (tournamentId) => {
    try {
      const response = await api.getTournamentParticipants(tournamentId)
      return Array.isArray(response) ? response : []
    } catch (err) {
      console.error('Fetch participants error:', err)
      return []
    }
  }

  /**
   * Turnir qatnashish qoidalari mavjudmi
   */
  const hasParticipationRules = (tournamentId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    return Array.isArray(tournament?.participationRules) && tournament.participationRules.length > 0
  }

  /**
   * Talaba uchun qatnashish qoidasini olish
   */
  const getParticipationRuleForStudent = (tournamentId, groupId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    if (!Array.isArray(tournament?.participationRules)) return null
    return tournament.participationRules.find(r => r.groupId === groupId || r.group_id === groupId) || null
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
    schedule, // alias for backward compatibility
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
    directionSubjects,
    fetchDirections,
    addDirection,
    updateDirection,
    deleteDirection,
    toggleDirectionStatus,
    updateDirectionSubjects,
    getDirectionByGroupId,
    getDirectionById,

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
    updateRegistrationStatus,
    isStudentRegistered,
    getStudentRegistrations,
    fetchTournamentParticipants,
    studentTournamentRegistrations,
    hasParticipationRules,
    getParticipationRuleForStudent,

    // === Helpers ===
    clearCache,
    refreshAll,

    // === Real-time Polling ===
    startPolling,
    stopPolling,
    pollOnce,
    invalidateAndRefresh,
    pollingActive
  }
})
