import api from './api'

// Demo mode
const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo ma'lumotlar
const demoStudents = [
  {
    id: 1,
    studentId: 'ST-2024-001',
    name: 'Aliyev Jasur',
    phone: '+998 90 123 45 67',
    address: 'Toshkent sh., Chilonzor tumani',
    commute: 'Avtobus #45',
    groupId: 1,
    group: 'KI_25-04',
    contractPaid: 18411000,
    passport: 'AA 1234567',
    jshshir: '12345678901234',
    role: 'student',
    avatar: null,
    email: 'jasur@uni.uz'
  },
  {
    id: 2,
    studentId: 'ST-2024-002',
    name: 'Karimov Sardor',
    phone: '+998 91 234 56 78',
    address: 'Toshkent sh., Yunusobod tumani',
    commute: 'Metro',
    groupId: 1,
    group: 'KI_25-04',
    contractPaid: 18411000,
    passport: 'AB 2345678',
    jshshir: '23456789012345',
    role: 'leader',
    avatar: null,
    email: 'sardor@uni.uz'
  },
  {
    id: 3,
    studentId: 'ST-2024-003',
    name: 'Toshmatov Alisher',
    phone: '+998 92 345 67 89',
    address: 'Toshkent sh., Mirzo Ulug\'bek tumani',
    commute: 'Piyoda',
    groupId: 1,
    group: 'KI_25-04',
    contractPaid: 13808250,
    passport: 'AC 3456789',
    jshshir: '34567890123456',
    role: 'student',
    avatar: null,
    email: 'alisher@uni.uz'
  },
  {
    id: 4,
    studentId: 'ST-2024-004',
    name: 'Rahimov Bekzod',
    phone: '+998 93 456 78 90',
    address: 'Toshkent sh., Sergeli tumani',
    commute: 'Avtobus #67',
    groupId: 1,
    group: 'KI_25-04',
    contractPaid: 9205500,
    passport: 'AD 4567890',
    jshshir: '45678901234567',
    role: 'student',
    avatar: null,
    email: 'bekzod@uni.uz'
  },
  {
    id: 5,
    studentId: 'ST-2024-005',
    name: 'Xolmatov Ulug\'bek',
    phone: '+998 94 567 89 01',
    address: 'Toshkent sh., Olmazor tumani',
    commute: 'Tramvay',
    groupId: 1,
    group: 'KI_25-04',
    contractPaid: 20000000,
    passport: 'AE 5678901',
    jshshir: '56789012345678',
    role: 'student',
    avatar: null,
    email: 'ulugbek@uni.uz'
  },
  {
    id: 6,
    studentId: 'ST-2024-006',
    name: 'Normatov Amir',
    phone: '+998 95 678 90 12',
    address: 'Toshkent sh., Yakkasaroy tumani',
    commute: 'Metro',
    groupId: 2,
    group: 'DI_25-21',
    contractPaid: 18411000,
    passport: 'AF 6789012',
    jshshir: '67890123456789',
    role: 'student',
    avatar: null,
    email: 'amir@uni.uz'
  },
  {
    id: 7,
    studentId: 'ST-2024-007',
    name: 'Qodirov Shoxrux',
    phone: '+998 96 789 01 23',
    address: 'Toshkent sh., Bektemir tumani',
    commute: 'Avtobus #12',
    groupId: 2,
    group: 'DI_25-21',
    contractPaid: 14000000,
    passport: 'AG 7890123',
    jshshir: '78901234567890',
    role: 'student',
    avatar: null,
    email: 'shoxrux@uni.uz'
  },
  {
    id: 8,
    studentId: 'ST-2024-008',
    name: 'Yusupova Nilufar',
    phone: '+998 97 890 12 34',
    address: 'Toshkent sh., Shayxontohur tumani',
    commute: 'Piyoda',
    groupId: 3,
    group: 'FTO_24-03',
    contractPaid: 16500000,
    passport: 'AH 8901234',
    jshshir: '89012345678901',
    role: 'student',
    avatar: null,
    email: 'nilufar@uni.uz'
  }
]

// Local storage key for demo data persistence
const STORAGE_KEY = 'unicontrol_demo_students'

// Demo data ni localStorage dan olish yoki default ishlatish
const getDemoStudents = () => {
  if (DEMO_MODE) {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : [...demoStudents]
  }
  return []
}

// Demo data ni saqlash
const saveDemoStudents = (students) => {
  if (DEMO_MODE) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(students))
  }
}

const studentsService = {
  /**
   * Barcha talabalarni olish
   * @param {Object} params - {page, limit, search, groupId, sortBy, sortOrder}
   * @returns {Promise<Object>} - {data, total, page, limit}
   */
  async getAll(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      let students = getDemoStudents()
      
      // Filter by group
      if (params.groupId) {
        students = students.filter(s => s.groupId === parseInt(params.groupId))
      }
      
      // Search
      if (params.search) {
        const search = params.search.toLowerCase()
        students = students.filter(s => 
          s.name.toLowerCase().includes(search) ||
          s.studentId.toLowerCase().includes(search) ||
          s.email?.toLowerCase().includes(search)
        )
      }
      
      // Sort
      if (params.sortBy) {
        students.sort((a, b) => {
          const aVal = a[params.sortBy]
          const bVal = b[params.sortBy]
          const order = params.sortOrder === 'desc' ? -1 : 1
          return aVal > bVal ? order : -order
        })
      }
      
      const total = students.length
      const page = params.page || 1
      const limit = params.limit || 50
      const start = (page - 1) * limit
      const data = students.slice(start, start + limit)
      
      return { data, total, page, limit }
    }

    const response = await api.get('/students', { params })
    return response
  },

  /**
   * Bitta talabani olish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async getById(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const students = getDemoStudents()
      const student = students.find(s => s.id === parseInt(id))
      if (!student) {
        throw { message: 'Talaba topilmadi', status: 404 }
      }
      return student
    }

    const response = await api.get(`/students/${id}`)
    return response
  },

  /**
   * Guruh bo'yicha talabalarni olish
   * @param {number} groupId
   * @returns {Promise<Array>}
   */
  async getByGroup(groupId) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const students = getDemoStudents()
      return students.filter(s => s.groupId === parseInt(groupId))
    }

    const response = await api.get(`/groups/${groupId}/students`)
    return response.data || response
  },

  /**
   * Yangi talaba qo'shish
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async create(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const students = getDemoStudents()
      const newId = Math.max(...students.map(s => s.id), 0) + 1
      const newStudentId = `ST-2024-${String(newId).padStart(3, '0')}`
      
      const newStudent = {
        ...data,
        id: newId,
        studentId: newStudentId,
        role: 'student'
      }
      
      students.push(newStudent)
      saveDemoStudents(students)
      
      return { success: true, data: newStudent }
    }

    const response = await api.post('/students', data)
    return response
  },

  /**
   * Talabani yangilash
   * @param {number} id
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async update(id, data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const students = getDemoStudents()
      const index = students.findIndex(s => s.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Talaba topilmadi', status: 404 }
      }
      
      // studentId va id o'zgartirilmaydi
      const { studentId, id: _id, ...allowedUpdates } = data
      students[index] = { ...students[index], ...allowedUpdates }
      saveDemoStudents(students)
      
      return { success: true, data: students[index] }
    }

    const response = await api.put(`/students/${id}`, data)
    return response
  },

  /**
   * Talabani o'chirish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async delete(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const students = getDemoStudents()
      const index = students.findIndex(s => s.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Talaba topilmadi', status: 404 }
      }
      
      students.splice(index, 1)
      saveDemoStudents(students)
      
      return { success: true }
    }

    const response = await api.delete(`/students/${id}`)
    return response
  },

  /**
   * Excel dan import qilish
   * @param {FormData} formData
   * @returns {Promise<Object>}
   */
  async importFromExcel(formData) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 500))
      return { success: true, imported: 0, message: 'Demo rejimda import qilinmaydi' }
    }

    const response = await api.post('/students/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response
  },

  /**
   * Excel ga export qilish
   * @param {Object} params - filter params
   * @returns {Promise<Blob>}
   */
  async exportToExcel(params = {}) {
    if (DEMO_MODE) {
      throw { message: 'Demo rejimda export qilinmaydi', status: 400 }
    }

    const response = await api.get('/students/export', {
      params,
      responseType: 'blob'
    })
    return response
  }
}

export default studentsService
