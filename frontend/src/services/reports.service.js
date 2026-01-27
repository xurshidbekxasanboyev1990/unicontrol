import api from './api'

const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo ma'lumotlar
const demoReports = [
  { id: 1, title: 'Yanvar oyi davomat hisoboti', type: 'attendance', groupId: 1, createdBy: 2, date: '2024-01-31', status: 'completed' },
  { id: 2, title: 'KI_25-04 guruh haftalik hisoboti', type: 'weekly', groupId: 1, createdBy: 2, date: '2024-01-28', status: 'completed' },
  { id: 3, title: 'Dekabr oyi yakuniy hisobot', type: 'monthly', groupId: 1, createdBy: 2, date: '2024-12-31', status: 'completed' },
]

const STORAGE_KEY = 'unicontrol_demo_reports'

const getDemoReports = () => {
  if (DEMO_MODE) {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : [...demoReports]
  }
  return []
}

const saveDemoReports = (items) => {
  if (DEMO_MODE) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }
}

const reportsService = {
  /**
   * Barcha hisobotlarni olish
   * @param {Object} params - {page, limit, type, groupId, status}
   * @returns {Promise<Object>}
   */
  async getAll(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      let reports = getDemoReports()
      
      if (params.type) {
        reports = reports.filter(r => r.type === params.type)
      }
      
      if (params.groupId) {
        reports = reports.filter(r => r.groupId === parseInt(params.groupId))
      }
      
      if (params.status) {
        reports = reports.filter(r => r.status === params.status)
      }
      
      // Sort by date (newest first)
      reports.sort((a, b) => new Date(b.date) - new Date(a.date))
      
      return { data: reports, total: reports.length }
    }

    const response = await api.get('/reports', { params })
    return response
  },

  /**
   * Bitta hisobotni olish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async getById(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const reports = getDemoReports()
      const report = reports.find(r => r.id === parseInt(id))
      
      if (!report) {
        throw { message: 'Hisobot topilmadi', status: 404 }
      }
      
      return report
    }

    const response = await api.get(`/reports/${id}`)
    return response
  },

  /**
   * Yangi hisobot yaratish
   * @param {Object} data - {title, type, groupId, content}
   * @returns {Promise<Object>}
   */
  async create(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const reports = getDemoReports()
      const newId = Math.max(...reports.map(r => r.id), 0) + 1
      
      const newReport = {
        ...data,
        id: newId,
        date: new Date().toISOString().split('T')[0],
        status: 'completed',
        createdAt: new Date().toISOString()
      }
      
      reports.push(newReport)
      saveDemoReports(reports)
      
      return { success: true, data: newReport }
    }

    const response = await api.post('/reports', data)
    return response
  },

  /**
   * Hisobotni o'chirish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async delete(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const reports = getDemoReports()
      const index = reports.findIndex(r => r.id === parseInt(id))
      
      if (index !== -1) {
        reports.splice(index, 1)
        saveDemoReports(reports)
      }
      
      return { success: true }
    }

    const response = await api.delete(`/reports/${id}`)
    return response
  },

  /**
   * Hisobotni PDF ga eksport qilish
   * @param {number} id
   * @returns {Promise<Blob>}
   */
  async exportPdf(id) {
    if (DEMO_MODE) {
      throw { message: 'Demo rejimda eksport qilinmaydi', status: 400 }
    }

    const response = await api.get(`/reports/${id}/export/pdf`, {
      responseType: 'blob'
    })
    return response
  },

  /**
   * Davomat hisobotini generatsiya qilish
   * @param {Object} params - {groupId, startDate, endDate}
   * @returns {Promise<Object>}
   */
  async generateAttendanceReport(params) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 500))
      return {
        success: true,
        data: {
          totalStudents: 5,
          totalDays: 30,
          averageAttendance: 87,
          details: []
        }
      }
    }

    const response = await api.post('/reports/attendance', params)
    return response
  },

  /**
   * Kontrakt hisobotini generatsiya qilish
   * @param {Object} params - {groupId}
   * @returns {Promise<Object>}
   */
  async generateContractReport(params) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 500))
      return {
        success: true,
        data: {
          totalAmount: 92055000,
          paidAmount: 79835750,
          unpaidAmount: 12219250,
          paidPercentage: 87,
          details: []
        }
      }
    }

    const response = await api.post('/reports/contract', params)
    return response
  }
}

export default reportsService
