import api from './api'

const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo ma'lumotlar
const demoGroups = [
  { id: 1, name: 'KI_25-04', faculty: 'Kompyuter injiniringi', year: 1, leaderId: 2, leaderName: 'Karimov Sardor', contractAmount: 18411000 },
  { id: 2, name: 'DI_25-21', faculty: 'Dasturiy injiniring', year: 1, leaderId: null, leaderName: '', contractAmount: 18411000 },
  { id: 3, name: 'FTO_24-03', faculty: 'Fizika-texnika', year: 2, leaderId: null, leaderName: '', contractAmount: 16500000 },
  { id: 4, name: 'SE_25-01', faculty: 'Dasturiy injiniring', year: 1, leaderId: null, leaderName: '', contractAmount: 18411000 },
]

const STORAGE_KEY = 'unicontrol_demo_groups'

const getDemoGroups = () => {
  if (DEMO_MODE) {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : [...demoGroups]
  }
  return []
}

const saveDemoGroups = (groups) => {
  if (DEMO_MODE) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(groups))
  }
}

const groupsService = {
  /**
   * Barcha guruhlarni olish
   * @param {Object} params - {page, limit, search, faculty, year}
   * @returns {Promise<Object>}
   */
  async getAll(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      let groups = getDemoGroups()
      
      if (params.faculty) {
        groups = groups.filter(g => g.faculty === params.faculty)
      }
      
      if (params.year) {
        groups = groups.filter(g => g.year === parseInt(params.year))
      }
      
      if (params.search) {
        const search = params.search.toLowerCase()
        groups = groups.filter(g => 
          g.name.toLowerCase().includes(search) ||
          g.faculty.toLowerCase().includes(search)
        )
      }
      
      return { data: groups, total: groups.length }
    }

    const response = await api.get('/groups', { params })
    return response
  },

  /**
   * Bitta guruhni olish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async getById(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const groups = getDemoGroups()
      const group = groups.find(g => g.id === parseInt(id))
      if (!group) {
        throw { message: 'Guruh topilmadi', status: 404 }
      }
      return group
    }

    const response = await api.get(`/groups/${id}`)
    return response
  },

  /**
   * Yangi guruh qo'shish
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async create(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const groups = getDemoGroups()
      const newId = Math.max(...groups.map(g => g.id), 0) + 1
      
      const newGroup = {
        ...data,
        id: newId,
        leaderId: null,
        leaderName: ''
      }
      
      groups.push(newGroup)
      saveDemoGroups(groups)
      
      return { success: true, data: newGroup }
    }

    const response = await api.post('/groups', data)
    return response
  },

  /**
   * Guruhni yangilash
   * @param {number} id
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async update(id, data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const groups = getDemoGroups()
      const index = groups.findIndex(g => g.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Guruh topilmadi', status: 404 }
      }
      
      groups[index] = { ...groups[index], ...data }
      saveDemoGroups(groups)
      
      return { success: true, data: groups[index] }
    }

    const response = await api.put(`/groups/${id}`, data)
    return response
  },

  /**
   * Guruhni o'chirish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async delete(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const groups = getDemoGroups()
      const index = groups.findIndex(g => g.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Guruh topilmadi', status: 404 }
      }
      
      groups.splice(index, 1)
      saveDemoGroups(groups)
      
      return { success: true }
    }

    const response = await api.delete(`/groups/${id}`)
    return response
  },

  /**
   * Guruh sardorini tayinlash
   * @param {number} groupId
   * @param {number} studentId
   * @returns {Promise<Object>}
   */
  async assignLeader(groupId, studentId) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 300))
      const groups = getDemoGroups()
      const index = groups.findIndex(g => g.id === parseInt(groupId))
      
      if (index === -1) {
        throw { message: 'Guruh topilmadi', status: 404 }
      }
      
      groups[index].leaderId = studentId
      saveDemoGroups(groups)
      
      return { success: true, data: groups[index] }
    }

    const response = await api.post(`/groups/${groupId}/assign-leader`, { studentId })
    return response
  },

  /**
   * Kontrakt summasini yangilash
   * @param {number} groupId
   * @param {number} amount
   * @returns {Promise<Object>}
   */
  async updateContractAmount(groupId, amount) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const groups = getDemoGroups()
      const index = groups.findIndex(g => g.id === parseInt(groupId))
      
      if (index !== -1) {
        groups[index].contractAmount = amount
        saveDemoGroups(groups)
      }
      
      return { success: true }
    }

    const response = await api.put(`/groups/${groupId}/contract`, { amount })
    return response
  }
}

export default groupsService
