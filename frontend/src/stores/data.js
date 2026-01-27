import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  studentsService,
  groupsService,
  attendanceService,
  scheduleService,
  notificationsService,
  reportsService
} from '../services'

export const useDataStore = defineStore('data', () => {
  // State
  const groups = ref([])
  const students = ref([])
  const schedule = ref([])
  const attendanceRecords = ref([])
  const reports = ref([])
  const notifications = ref([])
  
  // Loading states
  const isLoading = ref({
    groups: false,
    students: false,
    schedule: false,
    attendance: false,
    reports: false,
    notifications: false
  })
  
  // Error states
  const errors = ref({
    groups: null,
    students: null,
    schedule: null,
    attendance: null,
    reports: null,
    notifications: null
  })

  // ================== GURUHLAR ==================
  
  const fetchGroups = async (params = {}) => {
    isLoading.value.groups = true
    errors.value.groups = null
    
    try {
      const response = await groupsService.getAll(params)
      groups.value = response.data || response
      return groups.value
    } catch (err) {
      errors.value.groups = err.message
      throw err
    } finally {
      isLoading.value.groups = false
    }
  }

  const addGroup = async (group) => {
    try {
      const response = await groupsService.create(group)
      if (response.data) {
        groups.value.push(response.data)
      }
      return response
    } catch (err) {
      errors.value.groups = err.message
      throw err
    }
  }

  const updateGroup = async (id, updates) => {
    try {
      const response = await groupsService.update(id, updates)
      const index = groups.value.findIndex(g => g.id === id)
      if (index !== -1 && response.data) {
        groups.value[index] = response.data
      }
      return response
    } catch (err) {
      errors.value.groups = err.message
      throw err
    }
  }

  const deleteGroup = async (id) => {
    try {
      await groupsService.delete(id)
      const index = groups.value.findIndex(g => g.id === id)
      if (index !== -1) {
        groups.value.splice(index, 1)
      }
      return { success: true }
    } catch (err) {
      errors.value.groups = err.message
      throw err
    }
  }

  const assignGroupLeader = async (groupId, studentId) => {
    try {
      const response = await groupsService.assignLeader(groupId, studentId)
      
      // Local state yangilash
      const groupIndex = groups.value.findIndex(g => g.id === groupId)
      if (groupIndex !== -1) {
        groups.value[groupIndex].leaderId = studentId
      }
      
      const studentIndex = students.value.findIndex(s => s.id === studentId)
      if (studentIndex !== -1) {
        students.value[studentIndex].role = 'leader'
      }
      
      return response
    } catch (err) {
      errors.value.groups = err.message
      throw err
    }
  }

  const updateGroupContract = async (groupId, amount) => {
    try {
      await groupsService.updateContractAmount(groupId, amount)
      const index = groups.value.findIndex(g => g.id === groupId)
      if (index !== -1) {
        groups.value[index].contractAmount = amount
      }
      return { success: true }
    } catch (err) {
      errors.value.groups = err.message
      throw err
    }
  }

  // ================== TALABALAR ==================
  
  const fetchStudents = async (params = {}) => {
    isLoading.value.students = true
    errors.value.students = null
    
    try {
      const response = await studentsService.getAll(params)
      students.value = response.data || response
      return students.value
    } catch (err) {
      errors.value.students = err.message
      throw err
    } finally {
      isLoading.value.students = false
    }
  }

  const fetchStudentsByGroup = async (groupId) => {
    try {
      const data = await studentsService.getByGroup(groupId)
      return data
    } catch (err) {
      errors.value.students = err.message
      throw err
    }
  }

  const addStudent = async (student) => {
    try {
      const response = await studentsService.create(student)
      if (response.data) {
        students.value.push(response.data)
      }
      return response
    } catch (err) {
      errors.value.students = err.message
      throw err
    }
  }

  const updateStudent = async (id, updates) => {
    try {
      const response = await studentsService.update(id, updates)
      const index = students.value.findIndex(s => s.id === id)
      if (index !== -1 && response.data) {
        students.value[index] = response.data
      }
      return response
    } catch (err) {
      errors.value.students = err.message
      throw err
    }
  }

  // Leader tomonidan - cheklangan maydonlar
  const updateStudentLimited = async (id, updates) => {
    // Faqat ruxsat berilgan maydonlar
    const allowedFields = ['phone', 'address', 'commute', 'contractPaid']
    const filteredUpdates = {}
    allowedFields.forEach(field => {
      if (updates[field] !== undefined) {
        filteredUpdates[field] = updates[field]
      }
    })
    return updateStudent(id, filteredUpdates)
  }

  // Admin tomonidan - to'liq yangilash
  const updateStudentFull = async (id, updates) => {
    return updateStudent(id, updates)
  }

  const deleteStudent = async (id) => {
    try {
      await studentsService.delete(id)
      const index = students.value.findIndex(s => s.id === id)
      if (index !== -1) {
        students.value.splice(index, 1)
      }
      return { success: true }
    } catch (err) {
      errors.value.students = err.message
      throw err
    }
  }

  const importStudentsFromExcel = async (formData) => {
    try {
      const response = await studentsService.importFromExcel(formData)
      // Yangi ma'lumotlarni olish
      await fetchStudents()
      return response
    } catch (err) {
      errors.value.students = err.message
      throw err
    }
  }

  // ================== JADVAL ==================
  
  const fetchSchedule = async (params = {}) => {
    isLoading.value.schedule = true
    errors.value.schedule = null
    
    try {
      const response = await scheduleService.getAll(params)
      schedule.value = response.data || response
      return schedule.value
    } catch (err) {
      errors.value.schedule = err.message
      throw err
    } finally {
      isLoading.value.schedule = false
    }
  }

  const fetchScheduleByGroup = async (groupId) => {
    try {
      const data = await scheduleService.getByGroup(groupId)
      return data
    } catch (err) {
      errors.value.schedule = err.message
      throw err
    }
  }

  const fetchTodaySchedule = async (groupId) => {
    try {
      const data = await scheduleService.getToday(groupId)
      return data
    } catch (err) {
      errors.value.schedule = err.message
      throw err
    }
  }

  const addScheduleItem = async (item) => {
    try {
      const response = await scheduleService.create(item)
      if (response.data) {
        schedule.value.push(response.data)
      }
      return response
    } catch (err) {
      errors.value.schedule = err.message
      throw err
    }
  }

  const updateScheduleItem = async (id, updates) => {
    try {
      const response = await scheduleService.update(id, updates)
      const index = schedule.value.findIndex(s => s.id === id)
      if (index !== -1 && response.data) {
        schedule.value[index] = response.data
      }
      return response
    } catch (err) {
      errors.value.schedule = err.message
      throw err
    }
  }

  const deleteScheduleItem = async (id) => {
    try {
      await scheduleService.delete(id)
      const index = schedule.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schedule.value.splice(index, 1)
      }
      return { success: true }
    } catch (err) {
      errors.value.schedule = err.message
      throw err
    }
  }

  // ================== DAVOMAT ==================
  
  const fetchAttendance = async (params = {}) => {
    isLoading.value.attendance = true
    errors.value.attendance = null
    
    try {
      const response = await attendanceService.getAll(params)
      attendanceRecords.value = response.data || response
      return attendanceRecords.value
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    } finally {
      isLoading.value.attendance = false
    }
  }

  const fetchAttendanceByStudent = async (studentId, params = {}) => {
    try {
      return await attendanceService.getByStudent(studentId, params)
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    }
  }

  const fetchAttendanceByGroupAndDate = async (groupId, date) => {
    try {
      return await attendanceService.getByGroupAndDate(groupId, date)
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    }
  }

  const addAttendanceRecord = async (record) => {
    try {
      const response = await attendanceService.create(record)
      if (response.data) {
        attendanceRecords.value.push(response.data)
      }
      return response
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    }
  }

  const addAttendanceBatch = async (records) => {
    try {
      const response = await attendanceService.createBatch(records)
      // Ma'lumotlarni yangilash
      await fetchAttendance()
      return response
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    }
  }

  const updateAttendanceRecord = async (id, updates) => {
    try {
      const response = await attendanceService.update(id, updates)
      const index = attendanceRecords.value.findIndex(a => a.id === id)
      if (index !== -1 && response.data) {
        attendanceRecords.value[index] = response.data
      }
      return response
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    }
  }

  const getAttendanceStatistics = async (params = {}) => {
    try {
      return await attendanceService.getStatistics(params)
    } catch (err) {
      errors.value.attendance = err.message
      throw err
    }
  }

  // ================== BILDIRISHNOMALAR ==================
  
  const fetchNotifications = async (params = {}) => {
    isLoading.value.notifications = true
    errors.value.notifications = null
    
    try {
      const response = await notificationsService.getAll(params)
      notifications.value = response.data || response
      return notifications.value
    } catch (err) {
      errors.value.notifications = err.message
      throw err
    } finally {
      isLoading.value.notifications = false
    }
  }

  const getUnreadNotificationsCount = async () => {
    try {
      return await notificationsService.getUnreadCount()
    } catch (err) {
      errors.value.notifications = err.message
      throw err
    }
  }

  const markNotificationAsRead = async (id) => {
    try {
      await notificationsService.markAsRead(id)
      const index = notifications.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notifications.value[index].read = true
      }
      return { success: true }
    } catch (err) {
      errors.value.notifications = err.message
      throw err
    }
  }

  const markAllNotificationsAsRead = async () => {
    try {
      await notificationsService.markAllAsRead()
      notifications.value.forEach(n => n.read = true)
      return { success: true }
    } catch (err) {
      errors.value.notifications = err.message
      throw err
    }
  }

  const deleteNotification = async (id) => {
    try {
      await notificationsService.delete(id)
      const index = notifications.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notifications.value.splice(index, 1)
      }
      return { success: true }
    } catch (err) {
      errors.value.notifications = err.message
      throw err
    }
  }

  const sendNotification = async (data) => {
    try {
      const response = await notificationsService.send(data)
      if (response.data) {
        notifications.value.unshift(response.data)
      }
      return response
    } catch (err) {
      errors.value.notifications = err.message
      throw err
    }
  }

  const addNotification = sendNotification // Alias

  // ================== HISOBOTLAR ==================
  
  const fetchReports = async (params = {}) => {
    isLoading.value.reports = true
    errors.value.reports = null
    
    try {
      const response = await reportsService.getAll(params)
      reports.value = response.data || response
      return reports.value
    } catch (err) {
      errors.value.reports = err.message
      throw err
    } finally {
      isLoading.value.reports = false
    }
  }

  const addReport = async (report) => {
    try {
      const response = await reportsService.create(report)
      if (response.data) {
        reports.value.push(response.data)
      }
      return response
    } catch (err) {
      errors.value.reports = err.message
      throw err
    }
  }

  const deleteReport = async (id) => {
    try {
      await reportsService.delete(id)
      const index = reports.value.findIndex(r => r.id === id)
      if (index !== -1) {
        reports.value.splice(index, 1)
      }
      return { success: true }
    } catch (err) {
      errors.value.reports = err.message
      throw err
    }
  }

  const generateAttendanceReport = async (params) => {
    try {
      return await reportsService.generateAttendanceReport(params)
    } catch (err) {
      errors.value.reports = err.message
      throw err
    }
  }

  const generateContractReport = async (params) => {
    try {
      return await reportsService.generateContractReport(params)
    } catch (err) {
      errors.value.reports = err.message
      throw err
    }
  }

  // ================== COMPUTED ==================

  const getStudentsByGroup = computed(() => (groupId) => {
    return students.value.filter(s => s.groupId === groupId)
  })

  const getScheduleByGroup = computed(() => (groupId) => {
    return schedule.value.filter(s => s.groupId === groupId)
  })

  const getAttendanceByStudent = computed(() => (studentId) => {
    return attendanceRecords.value.filter(a => a.studentId === studentId)
  })

  const getAttendanceByDate = computed(() => (date, groupId) => {
    const groupStudents = students.value.filter(s => s.groupId === groupId).map(s => s.id)
    return attendanceRecords.value.filter(a => a.date === date && groupStudents.includes(a.studentId))
  })

  const calculateContractPercentage = (paidAmount, groupId) => {
    const group = groups.value.find(g => g.id === groupId)
    if (!group) return 0
    return Math.round((paidAmount / group.contractAmount) * 100)
  }

  // Statistikalar
  const getStatistics = computed(() => {
    const totalStudents = students.value.length
    const totalGroups = groups.value.length
    
    const presentCount = attendanceRecords.value.filter(a => a.status === 'present').length
    const totalRecords = attendanceRecords.value.length
    const attendanceRate = totalRecords > 0 ? Math.round((presentCount / totalRecords) * 100) : 0
    
    const totalContract = students.value.reduce((sum, s) => {
      const group = groups.value.find(g => g.id === s.groupId)
      return sum + (group?.contractAmount || 0)
    }, 0)
    
    const paidContract = students.value.reduce((sum, s) => sum + (s.contractPaid || 0), 0)
    const contractRate = totalContract > 0 ? Math.round((paidContract / totalContract) * 100) : 0

    return {
      totalStudents,
      totalGroups,
      attendanceRate,
      contractRate,
      totalContract,
      paidContract
    }
  })

  // ================== INITIALIZE ==================
  
  const initializeData = async () => {
    try {
      await Promise.all([
        fetchGroups(),
        fetchStudents(),
        fetchSchedule(),
        fetchAttendance(),
        fetchNotifications()
      ])
      return { success: true }
    } catch (err) {
      console.error('Data initialization error:', err)
      return { success: false, error: err.message }
    }
  }

  return {
    // State
    groups,
    students,
    schedule,
    attendanceRecords,
    reports,
    notifications,
    isLoading,
    errors,

    // Computed
    getStudentsByGroup,
    getScheduleByGroup,
    getAttendanceByStudent,
    getAttendanceByDate,
    getStatistics,
    
    // Utils
    calculateContractPercentage,

    // Guruhlar
    fetchGroups,
    addGroup,
    updateGroup,
    deleteGroup,
    assignGroupLeader,
    updateGroupContract,

    // Talabalar
    fetchStudents,
    fetchStudentsByGroup,
    addStudent,
    updateStudent,
    updateStudentLimited,
    updateStudentFull,
    deleteStudent,
    importStudentsFromExcel,

    // Jadval
    fetchSchedule,
    fetchScheduleByGroup,
    fetchTodaySchedule,
    addScheduleItem,
    updateScheduleItem,
    deleteScheduleItem,

    // Davomat
    fetchAttendance,
    fetchAttendanceByStudent,
    fetchAttendanceByGroupAndDate,
    addAttendanceRecord,
    addAttendanceBatch,
    updateAttendanceRecord,
    getAttendanceStatistics,

    // Bildirishnomalar
    fetchNotifications,
    getUnreadNotificationsCount,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    deleteNotification,
    sendNotification,
    addNotification,

    // Hisobotlar
    fetchReports,
    addReport,
    deleteReport,
    generateAttendanceReport,
    generateContractReport,

    // Initialize
    initializeData
  }
})
