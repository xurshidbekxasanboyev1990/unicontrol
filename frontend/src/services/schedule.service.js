import api from './api'

const DEMO_MODE = !import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_DEMO_MODE === 'true'

// Demo ma'lumotlar
const demoSchedule = [
  { id: 1, day: 'Dushanba', time: '08:30-09:50', subject: 'Matematika', teacher: 'Karimov A.', room: 'A-401', groupId: 1 },
  { id: 2, day: 'Dushanba', time: '10:00-11:20', subject: 'Dasturlash', teacher: 'Toshmatov I.', room: 'B-302', groupId: 1 },
  { id: 3, day: 'Dushanba', time: '11:30-12:50', subject: 'Fizika', teacher: 'Raximov S.', room: 'C-201', groupId: 1 },
  { id: 4, day: 'Seshanba', time: '08:30-09:50', subject: 'Ingliz tili', teacher: 'Johnson M.', room: 'D-105', groupId: 1 },
  { id: 5, day: 'Seshanba', time: '10:00-11:20', subject: 'Algoritm', teacher: 'Karimov A.', room: 'A-401', groupId: 1 },
  { id: 6, day: 'Chorshanba', time: '08:30-09:50', subject: 'Ma\'lumotlar bazasi', teacher: 'Normatov U.', room: 'B-302', groupId: 1 },
  { id: 7, day: 'Chorshanba', time: '10:00-11:20', subject: 'Web dasturlash', teacher: 'Toshmatov I.', room: 'B-303', groupId: 1 },
  { id: 8, day: 'Payshanba', time: '08:30-09:50', subject: 'Matematika', teacher: 'Karimov A.', room: 'A-401', groupId: 1 },
  { id: 9, day: 'Payshanba', time: '10:00-11:20', subject: 'Jismoniy tarbiya', teacher: 'Salimov B.', room: 'Sport zal', groupId: 1 },
  { id: 10, day: 'Juma', time: '08:30-09:50', subject: 'Dasturlash', teacher: 'Toshmatov I.', room: 'B-302', groupId: 1 },
  { id: 11, day: 'Juma', time: '10:00-11:20', subject: 'Falsafa', teacher: 'Xolmatov R.', room: 'C-401', groupId: 1 },
]

const STORAGE_KEY = 'unicontrol_demo_schedule'

const getDemoSchedule = () => {
  if (DEMO_MODE) {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : [...demoSchedule]
  }
  return []
}

const saveDemoSchedule = (items) => {
  if (DEMO_MODE) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }
}

const scheduleService = {
  /**
   * Jadvalni olish
   * @param {Object} params - {groupId, day}
   * @returns {Promise<Object>}
   */
  async getAll(params = {}) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      let schedule = getDemoSchedule()
      
      if (params.groupId) {
        schedule = schedule.filter(s => s.groupId === parseInt(params.groupId))
      }
      
      if (params.day) {
        schedule = schedule.filter(s => s.day === params.day)
      }
      
      return { data: schedule, total: schedule.length }
    }

    const response = await api.get('/schedule', { params })
    return response
  },

  /**
   * Guruh jadvali
   * @param {number} groupId
   * @returns {Promise<Array>}
   */
  async getByGroup(groupId) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      return getDemoSchedule().filter(s => s.groupId === parseInt(groupId))
    }

    const response = await api.get(`/groups/${groupId}/schedule`)
    return response.data || response
  },

  /**
   * Bugungi darslar
   * @param {number} groupId
   * @returns {Promise<Array>}
   */
  async getToday(groupId) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const days = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
      const today = days[new Date().getDay()]
      
      return getDemoSchedule().filter(s => 
        s.groupId === parseInt(groupId) && s.day === today
      )
    }

    const response = await api.get(`/groups/${groupId}/schedule/today`)
    return response.data || response
  },

  /**
   * Jadval elementi qo'shish
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async create(data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const schedule = getDemoSchedule()
      const newId = Math.max(...schedule.map(s => s.id), 0) + 1
      
      const newItem = { ...data, id: newId }
      schedule.push(newItem)
      saveDemoSchedule(schedule)
      
      return { success: true, data: newItem }
    }

    const response = await api.post('/schedule', data)
    return response
  },

  /**
   * Jadval elementini yangilash
   * @param {number} id
   * @param {Object} data
   * @returns {Promise<Object>}
   */
  async update(id, data) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const schedule = getDemoSchedule()
      const index = schedule.findIndex(s => s.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Jadval elementi topilmadi', status: 404 }
      }
      
      schedule[index] = { ...schedule[index], ...data }
      saveDemoSchedule(schedule)
      
      return { success: true, data: schedule[index] }
    }

    const response = await api.put(`/schedule/${id}`, data)
    return response
  },

  /**
   * Jadval elementini o'chirish
   * @param {number} id
   * @returns {Promise<Object>}
   */
  async delete(id) {
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 200))
      const schedule = getDemoSchedule()
      const index = schedule.findIndex(s => s.id === parseInt(id))
      
      if (index === -1) {
        throw { message: 'Jadval elementi topilmadi', status: 404 }
      }
      
      schedule.splice(index, 1)
      saveDemoSchedule(schedule)
      
      return { success: true }
    }

    const response = await api.delete(`/schedule/${id}`)
    return response
  }
}

export default scheduleService
