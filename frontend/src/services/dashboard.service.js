import api from './api'

/**
 * Dashboard Service
 * Dashboard ma'lumotlarini olish
 */
const dashboardService = {
    /**
     * Talaba dashboardi
     */
    async getStudentDashboard() {
        const response = await api.get('/dashboard/student')
        return response
    },

    /**
     * Lider dashboardi
     */
    async getLeaderDashboard() {
        const response = await api.get('/dashboard/leader')
        return response
    },

    /**
     * Admin dashboardi
     */
    async getAdminDashboard() {
        const response = await api.get('/dashboard/admin')
        return response
    },

    /**
     * Superadmin dashboardi
     */
    async getSuperadminDashboard() {
        const response = await api.get('/dashboard/superadmin')
        return response
    },

    /**
     * Avtomatik rol bo'yicha dashboard
     */
    async getDashboard() {
        const response = await api.get('/dashboard/summary')
        return response
    }
}

export default dashboardService
