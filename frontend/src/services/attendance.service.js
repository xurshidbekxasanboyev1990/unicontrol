import api from './api'

const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo ma'lumotlar
const demoAttendance = [
  { id: 1, studentId: 1, date: '2024-01-22', subject: 'Matematika', status: 'present', note: '' },
  { id: 2, studentId: 2, date: '2024-01-22', subject: 'Matematika', status: 'present', note: '' },
  { id: 3, studentId: 3, date: '2024-01-22', subject: 'Matematika', status: 'late', note: 'Transport muammosi' },
  { id: 4, studentId: 4, date: '2024-01-22', subject: 'Matematika', status: 'absent', note: '' },
  { id: 5, studentId: 5, date: '2024-01-22', subject: 'Matematika', status: 'present', note: '' },
  { id: 6, studentId: 1, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
  { id: 7, studentId: 2, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
  { id: 8, studentId: 3, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
  { id: 9, studentId: 4, date: '2024-01-22', subject: 'Dasturlash', status: 'absent', note: '' },
  { id: 10, studentId: 5, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
  { id: 11, studentId: 1, date: '2024-01-21', subject: 'Ingliz tili', status: 'present', note: '' },
  { id: 12, studentId: 2, date: '2024-01-21', subject: 'Ingliz tili', status: 'late', note: '' },
  { id: 13, studentId: 3, date: '2024-01-21', subject: 'Ingliz tili', status: 'present', note: '' },
  { id: 14, studentId: 4, date: '2024-01-21', subject: 'Ingliz tili', status: 'present', note: '' },
  { id: 15, studentId: 5, date: '2024-01-21', subject: 'Ingliz tili', status: 'absent', note: 'Kasallik' },
]

const STORAGE_KEY = 'unicontrol_demo_attendance'

const getDemoAttendance = () => {
  if (DEMO_MODE) {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : [...demoAttendance]
  }
  return []
}

const saveDemoAttendance = (records) => {
  if (DEMO_MODE) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records))
  }
}

const attendanceService = {
  /**
   * Davomat yozuvlarini olish
   * @param {Object} params - {date, groupId, studentId, subject, startDate, endDate}
   * @returns {Promise<Object>}
   */
  async getAll(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      let records = getDemoAttendance()
      
      if (params.date) {
        records = records.filter(r => r.date === params.date)
      }
      
      if (params.studentId) {
        records = records.filter(r => r.studentId === parseInt(params.studentId))
      }
      
      if (params.subject) {
        records = records.filter(r => r.subject === params.subject)
      }
      
      if (params.startDate && params.endDate) {
        records = records.filter(r => r.date >= params.startDate && r.date <= params.endDate)
      }
      
      return { data: records, total: records.length }
    }

    const response = await api.get('/attendance', { params })
    return response
  },

  /**
   * Talaba bo'yicha davomat
   * @param {number} studentId
   * @param {Object} params - {startDate, endDate}
   * @returns {Promise<Array>}
   */
  async getByStudent(studentId, params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      let records = getDemoAttendance().filter(r => r.studentId === parseInt(studentId))
      
      if (params.startDate && params.endDate) {
        records = records.filter(r => r.date >= params.startDate && r.date <= params.endDate)
      }
      
      return records
    }

    const response = await api.get(`/students/${studentId}/attendance`, { params })
    return response.data || response
  },

  /**
   * Guruh bo'yicha davomat (ma'lum sana)
   * @param {number} groupId
   * @param {string} date
   * @returns {Promise<Array>}
   */
  async getByGroupAndDate(groupId, date) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      // Guruh talabalarini olish kerak - bu demo uchun
      const records = getDemoAttendance().filter(r => r.date === date)
      return records
    }

    const response = await api.get(`/groups/${groupId}/attendance`, { params: { date } })
    return response.data || response
  },

  /**
   * Davomat yozuvi qo'shish
   * @param {Object} data - {studentId, date, subject, status, note}
   * @returns {Promise<Object>}
   */
  async create(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const records = getDemoAttendance()
      const newId = Math.max(...records.map(r => r.id), 0) + 1
      
      const newRecord = { ...data, id: newId }
      records.push(newRecord)
      saveDemoAttendance(records)
      
      return { success: true, data: newRecord }
    }

    const response = await api.post('/attendance', data)
    return response
  },

  /**
   * Ko'plab davomat yozuvlarini qo'shish (batch)
   * @param {Array} records - [{studentId, date, subject, status, note}]
   * @returns {Promise<Object>}
   */
  async createBatch(records) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const existingRecords = getDemoAttendance()
      let maxId = Math.max(...existingRecords.map(r => r.id), 0)
      
      const newRecords = records.map(record => ({
        ...record,
        id: ++maxId
      }))
      
      existingRecords.push(...newRecords)
      saveDemoAttendance(existingRecords)
      
      return { success: true, created: newRecords.length }
    }

    const response = await api.post('/attendance/batch', { records })
    return response
  },

  /**
   * Davomat yozuvini yangilash
   * @param {number} id
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async update(id, data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const records = getDemoAttendance()
      const index = records.findIndex(r => r.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Yozuv topilmadi', status: 404 }
      }
      
      records[index] = { ...records[index], ...data }
      saveDemoAttendance(records)
      
      return { success: true, data: records[index] }
    }

    const response = await api.put(`/attendance/${id}`, data)
    return response
  },

  /**
   * Davomat statistikasi
   * @param {Object} params - {groupId, startDate, endDate}
   * @returns {Promise<Object>}
   */
  async getStatistics(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const records = getDemoAttendance()
      
      const present = records.filter(r => r.status === 'present').length
      const absent = records.filter(r => r.status === 'absent').length
      const late = records.filter(r => r.status === 'late').length
      const total = records.length
      
      return {
        present,
        absent,
        late,
        total,
        attendanceRate: total > 0 ? Math.round((present + late) / total * 100) : 0
      }
    }

    const response = await api.get('/attendance/statistics', { params })
    return response
  }
}

export default attendanceService
