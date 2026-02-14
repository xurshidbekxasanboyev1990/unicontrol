// API Service - Backend bilan aloqa
// Use relative /api/v1 so requests go through nginx proxy (same-origin, no CORS)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Inactivity timeout - 24 soat (production) - uzoq vaqtdan keyin ham ishlashi kerak
const INACTIVITY_TIMEOUT = 24 * 60 * 60 * 1000 // 24 soat
const ACTIVITY_CHECK_INTERVAL = 60 * 1000 // Har 1 daqiqada tekshirish

// URLSearchParams uchun undefined/null qiymatlarni tozalash
function cleanParams(params) {
    const cleaned = {}
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== '' && value !== 'undefined') {
            cleaned[key] = value
        }
    }
    return cleaned
}

// Query string yaratish
function buildQuery(params) {
    const cleaned = cleanParams(params)
    if (Object.keys(cleaned).length === 0) return ''
    return '?' + new URLSearchParams(cleaned).toString()
}

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL
        this.refreshPromise = null // Refresh qilish jarayonida bo'lsa, bir xil promiseni qaytarish
        this.tokenRefreshThreshold = 3 * 60 * 1000 // 3 daqiqa oldin refresh qilish

        // Har 30 daqiqada token holatini tekshirish
        this.startTokenRefreshTimer()

        // Faollik kuzatuvchi - 1 soat faollik bo'lmasa logout
        this.initActivityTracker()
    }

    // ===== FAOLLIK KUZATUVCHI =====

    // Oxirgi faollik vaqtini yangilash
    updateLastActivity() {
        localStorage.setItem('last_activity', Date.now().toString())
    }

    // Oxirgi faollik vaqtini olish
    getLastActivity() {
        const timestamp = localStorage.getItem('last_activity')
        return timestamp ? parseInt(timestamp) : Date.now()
    }

    // Faollik kuzatuvchini ishga tushirish
    initActivityTracker() {
        // Faqat browser muhitida ishlaydi
        if (typeof window === 'undefined') return

        // Boshlang'ich faollik vaqtini belgilash
        this.updateLastActivity()

        // Foydalanuvchi harakatlari - faollik sifatida hisoblanadi
        const activityEvents = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click']

        // Throttle - juda ko'p event bo'lmasligi uchun
        let lastUpdate = 0
        const throttleMs = 30000 // Har 30 sekundda bir marta yangilash

        const handleActivity = () => {
            const now = Date.now()
            if (now - lastUpdate > throttleMs) {
                lastUpdate = now
                this.updateLastActivity()
            }
        }

        // Event listenerlarni qo'shish
        activityEvents.forEach(event => {
            window.addEventListener(event, handleActivity, { passive: true })
        })

        // Faolsizlik tekshiruvi
        setInterval(() => {
            this.checkInactivity()
        }, ACTIVITY_CHECK_INTERVAL)
    }

    // Faolsizlikni tekshirish
    checkInactivity() {
        const token = this.getToken()
        if (!token) return

        const lastActivity = this.getLastActivity()
        const inactiveTime = Date.now() - lastActivity

        if (inactiveTime >= INACTIVITY_TIMEOUT) {
            this.autoLogout()
        }
    }

    // Avtomatik logout
    autoLogout() {
        this.clearTokens()
        localStorage.removeItem('user')
        localStorage.removeItem('isAuthenticated')
        localStorage.setItem('logout_reason', 'inactivity')

        if (typeof window !== 'undefined') {
            window.location.href = '/login'
        }
    }

    // Token olish
    getToken() {
        return localStorage.getItem('access_token')
    }


    // Token saqlash
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
        // Token vaqtini ham saqlash
        localStorage.setItem('token_timestamp', Date.now().toString())
    }

    // Tokenlarni tozalash
    clearTokens() {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('token_timestamp')
        localStorage.removeItem('last_activity')
    }

    // Token expire bo'lishiga yaqinmi tekshirish
    isTokenExpiringSoon() {
        const timestamp = localStorage.getItem('token_timestamp')
        if (!timestamp) return true

        const tokenAge = Date.now() - parseInt(timestamp)
        const tokenLifetime = 480 * 60 * 1000 // 480 daqiqa = 8 soat (backend ACCESS_TOKEN_EXPIRE_MINUTES bilan mos)

        return tokenAge > (tokenLifetime - this.tokenRefreshThreshold)
    }

    // Proaktiv token refresh timer
    startTokenRefreshTimer() {
        setInterval(async () => {
            const token = this.getToken()
            if (token && this.isTokenExpiringSoon()) {
                await this.refreshToken()
            }
        }, 60 * 1000) // Har 1 daqiqada tekshirish
    }

    // Headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        }
        if (includeAuth) {
            const token = this.getToken()
            if (token) {
                headers['Authorization'] = `Bearer ${token}`
            }
        }
        return headers
    }

    // Umumiy request
    async request(endpoint, options = {}) {
        // Har bir API so'rov faollik hisoblanadi
        if (options.auth !== false) {
            this.updateLastActivity()
        }

        const url = `${this.baseUrl}${endpoint}`
        const isBlob = options.responseType === 'blob'
        const isFormData = options.body instanceof FormData
        const config = {
            headers: this.getHeaders(options.auth !== false),
            ...options
        }

        // Remove custom options so fetch doesn't complain
        delete config.responseType
        delete config.auth
        delete config.isFormData

        // FormData: let browser set Content-Type with boundary; don't stringify
        if (isFormData) {
            delete config.headers['Content-Type']
        } else if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body)
        }

        try {
            const response = await fetch(url, config)

            // 401 - Token expired, try refresh
            if (response.status === 401 && options.auth !== false) {
                const refreshed = await this.refreshToken()
                if (refreshed) {
                    config.headers = this.getHeaders(true)
                    const retryResponse = await fetch(url, config)
                    return isBlob ? this.handleBlobResponse(retryResponse) : this.handleResponse(retryResponse)
                } else {
                    this.clearTokens()
                    window.location.href = '/login'
                    throw new Error('Session expired')
                }
            }

            return isBlob ? this.handleBlobResponse(response) : this.handleResponse(response)
        } catch (error) {
            console.error('API Error:', error)
            throw error
        }
    }

    async handleBlobResponse(response) {
        if (!response.ok) {
            const data = await response.json().catch(() => null)
            const error = new Error(data?.detail || data?.message || 'Download failed')
            error.status = response.status
            error.data = data
            throw error
        }
        return response.blob()
    }

    async handleResponse(response) {
        const data = await response.json().catch(() => null)

        if (!response.ok) {
            const error = new Error(data?.detail || data?.message || 'Request failed')
            error.status = response.status
            error.data = data
            throw error
        }

        return data
    }

    // Token yangilash - concurrent so'rovlar uchun optimallashtirilgan
    async refreshToken() {
        // Agar allaqachon refresh qilinayotgan bo'lsa, shu promise'ni kutish
        if (this.refreshPromise) {
            return this.refreshPromise
        }

        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
            return false
        }

        this.refreshPromise = (async () => {
            try {
                const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken })
                })

                if (response.ok) {
                    const data = await response.json()
                    this.setTokens(data.access_token, data.refresh_token)
                    return true
                }
                return false
            } catch (err) {
                return false
            } finally {
                this.refreshPromise = null
            }
        })()

        return this.refreshPromise
    }

    // ===== AUTH =====
    async login(login, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: { login, password },
            auth: false
        })
        this.setTokens(data.access_token, data.refresh_token)
        this.updateLastActivity() // Login paytida faollik vaqtini yangilash
        return data
    }

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' })
        } finally {
            this.clearTokens()
            localStorage.removeItem('user')
            localStorage.removeItem('isAuthenticated')
        }
    }

    async getMe() {
        return this.request('/auth/me')
    }

    async changePassword(currentPassword, newPassword) {
        return this.request('/auth/me/password', {
            method: 'PUT',
            body: { current_password: currentPassword, new_password: newPassword }
        })
    }

    // ===== GROUPS =====
    async getGroups(params = {}) {
        return this.request(`/groups${buildQuery(params)}`)
    }

    async getGroup(id) {
        return this.request(`/groups/${id}`)
    }

    async createGroup(data) {
        return this.request('/groups', {
            method: 'POST',
            body: data
        })
    }

    async updateGroup(id, data) {
        return this.request(`/groups/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteGroup(id) {
        return this.request(`/groups/${id}`, { method: 'DELETE' })
    }

    async toggleGroupStatus(id) {
        return this.request(`/groups/${id}/toggle-status`, { method: 'PATCH' })
    }

    async assignGroupLeader(groupId, studentId) {
        // Backend leader_id ni query parameter sifatida kutadi
        return this.request(`/groups/${groupId}/set-leader?leader_id=${studentId}`, {
            method: 'POST'
        })
    }

    async removeGroupLeader(groupId) {
        // leader_id bo'lmasa, sardor olib tashlanadi
        return this.request(`/groups/${groupId}/set-leader`, {
            method: 'POST'
        })
    }

    async getGroupStudents(groupId) {
        return this.request(`/groups/${groupId}/students`)
    }

    async getGroupStatistics(groupId) {
        return this.request(`/groups/${groupId}/statistics`)
    }

    // ===== STUDENTS =====
    async getStudents(params = {}) {
        return this.request(`/students${buildQuery(params)}`)
    }

    async getStudent(id) {
        return this.request(`/students/${id}`)
    }

    async createStudent(data) {
        return this.request('/students', {
            method: 'POST',
            body: data
        })
    }

    async updateStudent(id, data) {
        return this.request(`/students/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteStudent(id) {
        return this.request(`/students/${id}`, { method: 'DELETE' })
    }

    async resetStudentPassword(id, newPassword) {
        // Backend uses /users/{user_id}/reset-password with query param
        return this.request(`/users/${id}/reset-password?new_password=${encodeURIComponent(newPassword)}`, {
            method: 'POST'
        })
    }

    async setStudentAsLeader(studentId) {
        // Bu endpoint talabani sardor qilib belgilaydi va user account yaratadi
        return this.request(`/students/${studentId}/set-leader`, {
            method: 'POST'
        })
    }

    async updateStudentContract(id, paidAmount) {
        return this.request(`/students/${id}/contract`, {
            method: 'PATCH',
            body: { paid_amount: paidAmount }
        })
    }

    async getStudentAttendance(studentId, dateFrom = null, dateTo = null) {
        const params = {}
        if (dateFrom) params.date_from = dateFrom
        if (dateTo) params.date_to = dateTo
        return this.request(`/attendance/student/${studentId}${buildQuery(params)}`)
    }

    // ===== SCHEDULE =====
    async getSchedules(params = {}) {
        return this.request(`/schedule${buildQuery(params)}`)
    }

    async getSchedule(id) {
        return this.request(`/schedule/${id}`)
    }

    async createSchedule(data) {
        return this.request('/schedule', {
            method: 'POST',
            body: data
        })
    }

    async updateSchedule(id, data) {
        return this.request(`/schedule/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteSchedule(id) {
        return this.request(`/schedule/${id}`, { method: 'DELETE' })
    }

    async getScheduleByGroup(groupId) {
        return this.request(`/schedule/group/${groupId}/week`)
    }

    async getTodaySchedule(groupId) {
        return this.request(`/schedule/today${groupId ? '?group_id=' + groupId : ''}`)
    }

    async getGroupDaySchedule(groupId, targetDate = null) {
        const params = targetDate ? `?target_date=${targetDate}` : ''
        return this.request(`/schedule/group/${groupId}/day${params}`)
    }

    // ===== ATTENDANCE =====
    async getAttendance(params = {}) {
        return this.request(`/attendance${buildQuery(params)}`)
    }

    async createAttendance(data) {
        return this.request('/attendance', {
            method: 'POST',
            body: data
        })
    }

    async updateAttendance(id, data) {
        return this.request(`/attendance/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async bulkCreateAttendance(records) {
        return this.request('/attendance/batch', {
            method: 'POST',
            body: records
        })
    }

    async getAttendanceByDate(date, groupId) {
        return this.request(`/attendance/date/${date}?group_id=${groupId}`)
    }

    async getAttendanceStatistics(groupId, startDate, endDate) {
        return this.request(`/attendance/statistics/${groupId}?start_date=${startDate}&end_date=${endDate}`)
    }

    async getAttendanceDailySummary(date = null, groupId = null) {
        const params = new URLSearchParams()
        if (date) params.append('target_date', date)
        if (groupId) params.append('group_id', groupId)
        return this.request(`/attendance/daily-summary${params.toString() ? '?' + params.toString() : ''}`)
    }

    async getGroupAttendanceSummary(groupId, dateFrom, dateTo) {
        return this.request(`/attendance/group/${groupId}/summary?date_from=${dateFrom}&date_to=${dateTo}`)
    }

    // ===== REPORTS =====
    async getReports(params = {}) {
        return this.request(`/reports${buildQuery(params)}`)
    }

    async createReport(data) {
        return this.request('/reports', {
            method: 'POST',
            body: data
        })
    }

    async getReport(id) {
        return this.request(`/reports/${id}`)
    }

    async updateReport(id, data) {
        return this.request(`/reports/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteReport(id) {
        return this.request(`/reports/${id}`, { method: 'DELETE' })
    }

    async generateReport(type, groupId, startDate, endDate) {
        return this.request('/reports/generate', {
            method: 'POST',
            body: { type, group_id: groupId, start_date: startDate, end_date: endDate }
        })
    }

    // ===== BIRTHDAYS =====
    async getUpcomingBirthdays(params = {}) {
        return this.request(`/students/birthdays/upcoming${buildQuery(params)}`)
    }

    // ===== NOTIFICATIONS =====
    async getNotifications(params = {}) {
        return this.request(`/notifications${buildQuery(params)}`)
    }

    async createNotification(data) {
        return this.request('/notifications', {
            method: 'POST',
            body: data
        })
    }

    async markNotificationRead(id) {
        return this.request(`/notifications/${id}/read`, { method: 'POST' })
    }

    async markAllNotificationsRead() {
        return this.request('/notifications/read-all', { method: 'POST' })
    }

    async deleteNotification(id) {
        return this.request(`/notifications/${id}`, { method: 'DELETE' })
    }

    async sendBulkNotification(data) {
        return this.request('/notifications/bulk', {
            method: 'POST',
            body: data
        })
    }

    async broadcastNotification(data) {
        return this.request('/notifications/broadcast', {
            method: 'POST',
            body: data
        })
    }

    async getUnreadNotificationCount() {
        return this.request('/notifications/unread-count')
    }

    // ===== EXCEL =====
    async importFromExcel(file, groupId = null) {
        const formData = new FormData()
        formData.append('file', file)
        if (groupId) formData.append('group_id', groupId)

        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}/excel/import`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        })
        return this.handleResponse(response)
    }

    async exportToExcel(type, params = {}) {
        const token = this.getToken()

        const response = await fetch(`${this.baseUrl}/excel/export/${type}${buildQuery(params)}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        })

        if (!response.ok) {
            throw new Error('Export failed')
        }

        return response.blob()
    }

    async importSchedulesFromExcel(file, academicYear = '2025-2026', semester = 2, clearExisting = true) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('academic_year', academicYear)
        formData.append('semester', semester.toString())
        formData.append('clear_existing', clearExisting.toString())

        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}/excel/import/schedules`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        })
        return this.handleResponse(response)
    }

    async downloadExcelTemplate(type) {
        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}/excel/templates/${type}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        })
        if (!response.ok) {
            throw new Error('Template download failed')
        }
        return response.blob()
    }

    // ===== LIBRARY =====
    async getBooks(params = {}) {
        return this.request(`/library/books${buildQuery(params)}`)
    }

    async getBook(bookId) {
        return this.request(`/library/books/${bookId}`)
    }

    async createBook(data) {
        return this.request('/library/books', {
            method: 'POST',
            body: data
        })
    }

    async updateBook(bookId, data) {
        return this.request(`/library/books/${bookId}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteBook(bookId) {
        return this.request(`/library/books/${bookId}`, { method: 'DELETE' })
    }

    async borrowBook(data) {
        return this.request('/library/borrow', {
            method: 'POST',
            body: data
        })
    }

    async returnBook(data) {
        return this.request('/library/return', {
            method: 'POST',
            body: data
        })
    }

    async getMyBorrows(params = {}) {
        return this.request(`/library/borrows${buildQuery(params)}`)
    }

    async getAllBorrows(params = {}) {
        return this.request(`/library/borrows/all${buildQuery(params)}`)
    }

    async getBookReviews(bookId) {
        return this.request(`/library/books/${bookId}/reviews`)
    }

    async createBookReview(bookId, data) {
        return this.request(`/library/books/${bookId}/reviews`, {
            method: 'POST',
            body: data
        })
    }

    async getStudentAttendanceStats(studentId, dateFrom = null, dateTo = null) {
        const params = {}
        if (dateFrom) params.date_from = dateFrom
        if (dateTo) params.date_to = dateTo
        return this.request(`/attendance/student/${studentId}/stats${buildQuery(params)}`)
    }

    // ===== STATISTICS =====
    async getDashboardStats() {
        return this.request('/statistics/dashboard')
    }

    async getAttendanceStats(params = {}) {
        return this.request(`/statistics/attendance${buildQuery(params)}`)
    }

    async getContractStats(params = {}) {
        return this.request(`/statistics/contracts${buildQuery(params)}`)
    }

    // ===== USERS =====
    async getUsers(params = {}) {
        return this.request(`/users${buildQuery(params)}`)
    }

    async getUser(id) {
        return this.request(`/users/${id}`)
    }

    async createUser(data) {
        return this.request('/users', {
            method: 'POST',
            body: data
        })
    }

    async updateUser(id, data) {
        return this.request(`/users/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteUser(id) {
        return this.request(`/users/${id}`, { method: 'DELETE' })
    }

    async resetUserPassword(userId, newPassword) {
        return this.request(`/users/${userId}/reset-password?new_password=${encodeURIComponent(newPassword)}`, {
            method: 'POST'
        })
    }

    // ===== ADMINS (SuperAdmin only) =====
    async getAdmins() {
        // Backend endpoint: GET /users/roles/admins
        return this.request('/users/roles/admins')
    }

    async createAdmin(data) {
        // Create user with admin role via /users
        return this.request('/users', {
            method: 'POST',
            body: { ...data, role: data.role || 'admin' }
        })
    }

    async updateAdmin(id, data) {
        // Update user via /users/{id}
        return this.request(`/users/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteAdmin(id) {
        // Delete user via /users/{id} (superadmin only)
        return this.request(`/users/${id}`, { method: 'DELETE' })
    }

    async activateUser(id) {
        return this.request(`/users/${id}/activate`, { method: 'POST' })
    }

    async deactivateUser(id) {
        return this.request(`/users/${id}/deactivate`, { method: 'POST' })
    }

    // ===== LOGS (SuperAdmin only) =====
    async getLogs(params = {}) {
        return this.request(`/logs${buildQuery(params)}`)
    }

    // ===== SETTINGS =====
    async getSettings() {
        return this.request('/settings')
    }

    async updateSettings(data) {
        return this.request('/settings', {
            method: 'PUT',
            body: data
        })
    }

    // ===== LANDING PAGE SETTINGS =====
    async getLandingPublic() {
        return this.request('/landing/public', { auth: false })
    }

    async getLandingSettings() {
        return this.request('/landing')
    }

    async updateLandingSettings(data) {
        return this.request('/landing', {
            method: 'PUT',
            body: data
        })
    }

    async updateLandingSocialLinks(data) {
        return this.request('/landing/social-links', {
            method: 'PUT',
            body: data
        })
    }

    async updateLandingTeamMembers(data) {
        return this.request('/landing/team-members', {
            method: 'PUT',
            body: data
        })
    }

    async updateLandingFeatureCards(data) {
        return this.request('/landing/feature-cards', {
            method: 'PUT',
            body: data
        })
    }

    async updateLandingContactInfo(data) {
        return this.request('/landing/contact-info', {
            method: 'PUT',
            body: data
        })
    }

    async updateLandingHeroStats(data) {
        return this.request('/landing/hero-stats', {
            method: 'PUT',
            body: data
        })
    }

    async updateLandingAboutStats(data) {
        return this.request('/landing/about-stats', {
            method: 'PUT',
            body: data
        })
    }

    // ===== CLUBS =====
    async getClubs(params = {}) {
        return this.request(`/clubs${buildQuery(params)}`)
    }

    async createClub(data) {
        return this.request('/clubs', {
            method: 'POST',
            body: data
        })
    }

    async updateClub(id, data) {
        return this.request(`/clubs/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteClub(id) {
        return this.request(`/clubs/${id}`, { method: 'DELETE' })
    }

    async toggleClubStatus(id) {
        return this.request(`/clubs/${id}/toggle-status`, { method: 'PATCH' })
    }

    // ===== SUBJECTS =====
    async getSubjects(params = {}) {
        return this.request(`/subjects${buildQuery(params)}`)
    }

    async createSubject(data) {
        return this.request('/subjects', {
            method: 'POST',
            body: data
        })
    }

    async updateSubject(id, data) {
        return this.request(`/subjects/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteSubject(id) {
        return this.request(`/subjects/${id}`, { method: 'DELETE' })
    }

    // ===== DIRECTIONS =====
    async getDirections(params = {}) {
        return this.request(`/directions${buildQuery(params)}`)
    }

    async createDirection(data) {
        return this.request('/directions', {
            method: 'POST',
            body: data
        })
    }

    async updateDirection(id, data) {
        return this.request(`/directions/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteDirection(id) {
        return this.request(`/directions/${id}`, { method: 'DELETE' })
    }

    async toggleDirectionStatus(id) {
        return this.request(`/directions/${id}/toggle-status`, { method: 'PATCH' })
    }

    async updateDirectionSubjects(directionId, subjectIds) {
        return this.request(`/directions/${directionId}/subjects`, {
            method: 'PUT',
            body: { subject_ids: subjectIds }
        })
    }

    // ===== TOURNAMENTS =====
    async getTournaments(params = {}) {
        return this.request(`/tournaments${buildQuery(params)}`)
    }

    async createTournament(data) {
        return this.request('/tournaments', {
            method: 'POST',
            body: data
        })
    }

    async updateTournament(id, data) {
        return this.request(`/tournaments/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteTournament(id) {
        return this.request(`/tournaments/${id}`, { method: 'DELETE' })
    }

    async toggleTournamentStatus(id) {
        return this.request(`/tournaments/${id}/toggle-status`, { method: 'PATCH' })
    }

    async getTournamentParticipants(tournamentId) {
        return this.request(`/tournaments/${tournamentId}/participants`)
    }

    async getMyTournamentRegistrations() {
        return this.request('/tournaments/my-registrations')
    }

    async registerForTournament(tournamentId, studentId) {
        return this.request(`/tournaments/${tournamentId}/register`, {
            method: 'POST',
            body: { student_id: studentId }
        })
    }

    async unregisterFromTournament(tournamentId, studentId) {
        return this.request(`/tournaments/${tournamentId}/unregister`, {
            method: 'POST',
            body: { student_id: studentId }
        })
    }

    async updateRegistrationStatus(tournamentId, registrationId, status) {
        return this.request(`/tournaments/${tournamentId}/registrations/${registrationId}/status?status=${status}`, {
            method: 'PATCH'
        })
    }

    // ===== HELP/FAQ =====
    async getFaqs(params = {}) {
        return this.request(`/faqs${buildQuery(params)}`)
    }

    async createFaq(data) {
        return this.request('/faqs', {
            method: 'POST',
            body: data
        })
    }

    async updateFaq(id, data) {
        return this.request(`/faqs/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteFaq(id) {
        return this.request(`/faqs/${id}`, { method: 'DELETE' })
    }

    async getContactInfo() {
        return this.request('/contact-info')
    }

    async updateContactInfo(data) {
        return this.request('/contact-info', {
            method: 'PUT',
            body: data
        })
    }

    async getSupportMessages(params = {}) {
        return this.request(`/support-messages${buildQuery(params)}`)
    }

    async replySupportMessage(id, reply) {
        return this.request(`/support-messages/${id}/reply`, {
            method: 'POST',
            body: { reply }
        })
    }

    async updateSupportMessageStatus(id, status) {
        return this.request(`/support-messages/${id}/status`, {
            method: 'PATCH',
            body: { status }
        })
    }

    // ===== FILE MANAGER =====

    // Fayl yuklash (multipart/form-data)
    async uploadFile(file, folderId = null, groupId = null, description = '', isPublic = false) {
        const formData = new FormData()
        formData.append('file', file)

        let url = '/files/upload?'
        if (folderId) url += `folder_id=${folderId}&`
        if (groupId) url += `group_id=${groupId}&`
        if (description) url += `description=${encodeURIComponent(description)}&`
        url += `is_public=${isPublic}`

        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}${url}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        })

        return this.handleResponse(response)
    }

    // Fayllar ro'yxati
    async getFiles(params = {}) {
        const query = new URLSearchParams()
        if (params.folder_id !== undefined) query.append('folder_id', params.folder_id)
        if (params.file_type) query.append('file_type', params.file_type)
        if (params.search) query.append('search', params.search)
        if (params.page) query.append('page', params.page)
        if (params.page_size) query.append('page_size', params.page_size)

        const queryStr = query.toString()
        return this.request(`/files${queryStr ? '?' + queryStr : ''}`)
    }

    // File Manager data (folders + files)
    async getFileManager(folderId = null) {
        const url = folderId ? `/files/manager?folder_id=${folderId}` : '/files/manager'
        return this.request(url)
    }

    // Storage statistikasi
    async getStorageStats() {
        return this.request('/files/stats')
    }

    // Fayl ma'lumotlari
    async getFile(id) {
        return this.request(`/files/${id}`)
    }

    // Fayl yuklab olish URL
    getFileDownloadUrl(id) {
        const token = this.getToken()
        return `${this.baseUrl}/files/${id}/download?token=${token}`
    }

    // Fayl yangilash
    async updateFile(id, data) {
        return this.request(`/files/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    // Fayl o'chirish
    async deleteFile(id) {
        return this.request(`/files/${id}`, { method: 'DELETE' })
    }

    // Papka yaratish
    async createFolder(data) {
        return this.request('/files/folders', {
            method: 'POST',
            body: data
        })
    }

    // Papkalar ro'yxati
    async getFolders(parentId = null) {
        const url = parentId !== null ? `/files/folders?parent_id=${parentId}` : '/files/folders'
        return this.request(url)
    }

    // Papka ma'lumotlari
    async getFolder(id) {
        return this.request(`/files/folders/${id}`)
    }

    // Papka yangilash
    async updateFolder(id, data) {
        return this.request(`/files/folders/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    // Papka o'chirish
    async deleteFolder(id) {
        return this.request(`/files/folders/${id}`, { method: 'DELETE' })
    }

    // ===== CANTEEN (OSHXONA) =====

    // Menyu kategoriyalari
    async getCanteenCategories() {
        return this.request('/canteen/categories')
    }

    // Kategoriya yaratish (admin)
    async createCanteenCategory(data) {
        return this.request('/canteen/categories', {
            method: 'POST',
            body: data
        })
    }

    // Menyu elementlari
    async getCanteenMenu(params = {}) {
        const query = new URLSearchParams()
        if (params.category_id) query.append('category_id', params.category_id)
        if (params.is_available !== undefined) query.append('is_available', params.is_available)
        if (params.search) query.append('search', params.search)

        const queryStr = query.toString()
        return this.request(`/canteen/menu${queryStr ? '?' + queryStr : ''}`)
    }

    // Menyu elementi yaratish (admin)
    async createMenuItem(data) {
        return this.request('/canteen/menu', {
            method: 'POST',
            body: data
        })
    }

    // Menyu elementi yangilash (admin)
    async updateMenuItem(id, data) {
        return this.request(`/canteen/menu/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    // Menyu elementi o'chirish (admin)
    async deleteMenuItem(id) {
        return this.request(`/canteen/menu/${id}`, { method: 'DELETE' })
    }

    // Buyurtma berish
    async createCanteenOrder(data) {
        return this.request('/canteen/orders', {
            method: 'POST',
            body: data
        })
    }

    // O'z buyurtmalarim
    async getMyCanteenOrders(params = {}) {
        return this.request(`/canteen/orders/my${buildQuery(params)}`)
    }

    // Barcha buyurtmalar (admin)
    async getAllCanteenOrders(params = {}) {
        return this.request(`/canteen/orders${buildQuery(params)}`)
    }

    // Buyurtma holatini yangilash (admin)
    async updateCanteenOrderStatus(id, status) {
        return this.request(`/canteen/orders/${id}/status`, {
            method: 'PATCH',
            body: { status }
        })
    }

    // Kunlik statistika (admin)
    async getCanteenStats() {
        return this.request('/canteen/stats')
    }

    // ===== SUBSCRIPTIONS (Obuna) =====
    async getSubscriptionPlans() {
        return this.request('/subscriptions/plans')
    }

    async createSubscriptionPlan(data) {
        return this.request('/subscriptions/plans', {
            method: 'POST',
            body: data
        })
    }

    async updateSubscriptionPlan(planId, data) {
        return this.request(`/subscriptions/plans/${planId}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteSubscriptionPlan(planId) {
        return this.request(`/subscriptions/plans/${planId}`, {
            method: 'DELETE'
        })
    }

    async getMyGroupSubscription() {
        return this.request('/subscriptions/my-group')
    }

    async checkGroupSubscription(groupId) {
        return this.request(`/subscriptions/check/${groupId}`)
    }

    async purchaseSubscription(formData) {
        // FormData: group_id, plan_type, receipt (file)
        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}/subscriptions/purchase`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        })
        const data = await response.json()
        if (!response.ok) {
            throw new Error(data?.detail || 'To\'lov xatolik')
        }
        return data
    }

    async getSubscriptionPayments(params = {}) {
        return this.request(`/subscriptions/payments${buildQuery(params)}`)
    }

    async actionPayment(paymentId, data) {
        return this.request(`/subscriptions/payments/${paymentId}`, {
            method: 'PATCH',
            body: data
        })
    }

    async getSubscriptionSettings() {
        return this.request('/subscriptions/settings')
    }

    async updateSubscriptionSettings(data) {
        return this.request('/subscriptions/settings', {
            method: 'PUT',
            body: data
        })
    }

    async activateTrial() {
        return this.request('/subscriptions/activate-trial', { method: 'POST' })
    }

    async getAllSubscriptions(params = {}) {
        return this.request(`/subscriptions/all${buildQuery(params)}`)
    }

    async updateSubscriptionStatus(subId, data) {
        return this.request(`/subscriptions/subscriptions/${subId}/status`, {
            method: 'PATCH',
            body: data
        })
    }

    async adminAssignSubscription(groupId, planId) {
        return this.request('/subscriptions/admin-assign', {
            method: 'POST',
            body: { group_id: groupId, plan_id: planId }
        })
    }

    async getReceiptUrl(paymentId) {
        return `${this.baseUrl}/subscriptions/receipt/${paymentId}`
    }

    // ===== AI =====

    // ===== HOLIDAYS (Bayramlar / Dam olish kunlari) =====
    async getHolidays(params = {}) {
        const query = params.active_only !== undefined ? `?active_only=${params.active_only}` : ''
        return this.request(`/holidays${query}`)
    }

    async getActiveHolidays() {
        return this.request('/holidays/active')
    }

    async checkDateHoliday(checkDate) {
        const query = checkDate ? `?check_date=${checkDate}` : ''
        return this.request(`/holidays/check${query}`)
    }

    async createHoliday(data) {
        return this.request('/holidays', { method: 'POST', body: data })
    }

    async updateHoliday(id, data) {
        return this.request(`/holidays/${id}`, { method: 'PUT', body: data })
    }

    async deleteHoliday(id) {
        return this.request(`/holidays/${id}`, { method: 'DELETE' })
    }

    // ===== AI =====

    async aiGetUsage() {
        return this.request('/ai/usage')
    }

    async aiAnalyzeStudent(data) {
        return this.request('/ai/analyze/student', { method: 'POST', body: data })
    }

    async aiAnalyzeGroup(data) {
        return this.request('/ai/analyze/group', { method: 'POST', body: data })
    }

    async aiPredictAttendance(data) {
        return this.request('/ai/predict/attendance', { method: 'POST', body: data })
    }

    async aiChat(data) {
        return this.request('/ai/chat', { method: 'POST', body: data })
    }

    async aiSummarizeReport(data) {
        return this.request('/ai/summarize/report', { method: 'POST', body: data })
    }

    async aiDashboardInsights() {
        return this.request('/ai/insights/dashboard')
    }

    async aiStudentRecommendations(studentId) {
        return this.request(`/ai/recommendations/${studentId}`)
    }

    async aiGenerateNotificationText(data) {
        return this.request('/ai/generate/notification-text', { method: 'POST', body: data })
    }

    async aiHealthCheck() {
        return this.request('/ai/health')
    }

    // ===== CONTRACTS (Kontrakt ma'lumotlari) =====
    async getContracts(params = {}) {
        return this.request(`/contracts${buildQuery(params)}`)
    }

    async getContract(id) {
        return this.request(`/contracts/${id}`)
    }

    async createContract(data) {
        return this.request('/contracts', { method: 'POST', body: data })
    }

    async updateContract(id, data) {
        return this.request(`/contracts/${id}`, { method: 'PUT', body: data })
    }

    async deleteContract(id) {
        return this.request(`/contracts/${id}`, { method: 'DELETE' })
    }

    async getContractStatistics(params = {}) {
        return this.request(`/contracts/statistics${buildQuery(params)}`)
    }

    async getContractAcademicYears() {
        return this.request('/contracts/academic-years')
    }

    async getContractFilters() {
        return this.request('/contracts/filters')
    }

    async importContracts(file, academicYear = '2025-2026', updateExisting = true) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('academic_year', academicYear)
        formData.append('update_existing', updateExisting)

        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}/contracts/import`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            body: formData
        })
        return this.handleResponse(response)
    }

    async exportContracts(params = {}) {
        const token = this.getToken()
        const response = await fetch(`${this.baseUrl}/contracts/export/excel${buildQuery(params)}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        })
        if (!response.ok) throw new Error('Export failed')
        return response.blob()
    }

    async deleteContractsByYear(academicYear) {
        return this.request(`/contracts/year/${academicYear}`, { method: 'DELETE' })
    }

    async getMyContract(academicYear = '2025-2026') {
        return this.request(`/contracts/my?academic_year=${academicYear}`)
    }

    async getGroupContracts(groupId, params = {}) {
        return this.request(`/contracts/group/${groupId}${buildQuery(params)}`)
    }
}

export const api = new ApiService()
export default api
