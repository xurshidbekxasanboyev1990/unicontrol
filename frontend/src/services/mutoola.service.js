import api from './api'

/**
 * Mutoola Service
 * KUAF Mutoola API integratsiyasi
 */
const mutoolaService = {
    /**
     * Ma'lumotlarni sinxronlashtirish
     */
    async syncData(entityType, groupId = null, force = false) {
        const response = await api.post('/mutoola/sync', {
            entity_type: entityType,
            group_id: groupId,
            force
        })
        return response
    },

    /**
     * Talabalarni sinxronlashtirish
     */
    async syncStudents(groupId = null, force = false) {
        const params = { force }
        if (groupId) params.group_id = groupId

        const response = await api.post('/mutoola/sync/students', null, { params })
        return response
    },

    /**
     * Guruhlarni sinxronlashtirish
     */
    async syncGroups(faculty = null, force = false) {
        const params = { force }
        if (faculty) params.faculty = faculty

        const response = await api.post('/mutoola/sync/groups', null, { params })
        return response
    },

    /**
     * Jadvallarni sinxronlashtirish
     */
    async syncSchedules(groupId = null, semester = null, force = false) {
        const params = { force }
        if (groupId) params.group_id = groupId
        if (semester) params.semester = semester

        const response = await api.post('/mutoola/sync/schedules', null, { params })
        return response
    },

    /**
     * Mutoola'dan talabalarni olish
     */
    async getMutoolaStudents(params = {}) {
        const response = await api.get('/mutoola/students', { params })
        return response
    },

    /**
     * Mutoola'dan guruhlarni olish
     */
    async getMutoolaGroups(faculty = null, course = null) {
        const params = {}
        if (faculty) params.faculty = faculty
        if (course) params.course = course

        const response = await api.get('/mutoola/groups', { params })
        return response
    },

    /**
     * Mutoola'dan talabani olish
     */
    async getMutoolaStudent(hemisId) {
        const response = await api.get(`/mutoola/student/${hemisId}`)
        return response
    },

    /**
     * Sinxronizatsiya tarixini olish
     */
    async getSyncHistory(params = {}) {
        const response = await api.get('/mutoola/sync/history', { params })
        return response
    },

    /**
     * Sinxronizatsiya tafsilotlarini olish
     */
    async getSyncDetails(syncId) {
        const response = await api.get(`/mutoola/sync/${syncId}`)
        return response
    },

    /**
     * Mutoola ulanishini tekshirish
     */
    async verifyConnection() {
        const response = await api.post('/mutoola/verify-connection')
        return response
    },

    /**
     * Fakultetlar ro'yxatini olish
     */
    async getFaculties() {
        const response = await api.get('/mutoola/faculties')
        return response
    },

    /**
     * Mutoola statistikasi
     */
    async getStats() {
        const response = await api.get('/mutoola/stats')
        return response
    }
}

export default mutoolaService
