// API Service - Backend bilan aloqa
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Inactivity timeout - 30 daqiqa (production)
const INACTIVITY_TIMEOUT = 30 * 60 * 1000 // 30 daqiqa
const ACTIVITY_CHECK_INTERVAL = 60 * 1000 // Har 1 daqiqada tekshirish

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL
        this.refreshPromise = null // Refresh qilish jarayonida bo'lsa, bir xil promiseni qaytarish
        this.tokenRefreshThreshold = 5 * 60 * 1000 // 5 daqiqa oldin refresh qilish

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
        const tokenLifetime = 8 * 60 * 60 * 1000 // 8 soat (backend bilan mos)

        return tokenAge > (tokenLifetime - this.tokenRefreshThreshold)
    }

    // Proaktiv token refresh timer
    startTokenRefreshTimer() {
        setInterval(async () => {
            const token = this.getToken()
            if (token && this.isTokenExpiringSoon()) {
                await this.refreshToken()
            }
        }, 5 * 60 * 1000)
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
        const config = {
            headers: this.getHeaders(options.auth !== false),
            ...options
        }

        if (config.body && typeof config.body === 'object') {
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
                    return this.handleResponse(retryResponse)
                } else {
                    this.clearTokens()
                    window.location.href = '/login'
                    throw new Error('Session expired')
                }
            }

            return this.handleResponse(response)
        } catch (error) {
            console.error('API Error:', error)
            throw error
        }
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
        return this.request('/auth/change-password', {
            method: 'POST',
            body: { current_password: currentPassword, new_password: newPassword }
        })
    }

    // ===== GROUPS =====
    async getGroups(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/groups${query ? '?' + query : ''}`)
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/students${query ? '?' + query : ''}`)
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
        return this.request(`/students/${id}/reset-password`, {
            method: 'PATCH',
            body: { new_password: newPassword }
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

    async getStudentAttendance(id) {
        return this.request(`/students/${id}/attendance`)
    }

    // ===== SCHEDULE =====
    async getSchedules(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/schedule${query ? '?' + query : ''}`)
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
        return this.request(`/schedule/group/${groupId}`)
    }

    async getTodaySchedule(groupId) {
        return this.request(`/schedule/today/${groupId}`)
    }

    // ===== ATTENDANCE =====
    async getAttendance(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/attendance${query ? '?' + query : ''}`)
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
        return this.request('/attendance/bulk', {
            method: 'POST',
            body: { records }
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/reports${query ? '?' + query : ''}`)
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

    // ===== NOTIFICATIONS =====
    async getNotifications(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/notifications${query ? '?' + query : ''}`)
    }

    async createNotification(data) {
        return this.request('/notifications', {
            method: 'POST',
            body: data
        })
    }

    async markNotificationRead(id) {
        return this.request(`/notifications/${id}/read`, { method: 'PATCH' })
    }

    async markAllNotificationsRead() {
        return this.request('/notifications/read-all', { method: 'PATCH' })
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
        const query = new URLSearchParams(params).toString()
        const token = this.getToken()

        const response = await fetch(`${this.baseUrl}/excel/export/${type}${query ? '?' + query : ''}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        })

        if (!response.ok) {
            throw new Error('Export failed')
        }

        return response.blob()
    }

    // ===== STATISTICS =====
    async getDashboardStats() {
        return this.request('/statistics/dashboard')
    }

    async getAttendanceStats(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/statistics/attendance${query ? '?' + query : ''}`)
    }

    async getContractStats(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/statistics/contracts${query ? '?' + query : ''}`)
    }

    // ===== ADMINS (SuperAdmin only) =====
    async getAdmins() {
        return this.request('/admins')
    }

    async createAdmin(data) {
        return this.request('/admins', {
            method: 'POST',
            body: data
        })
    }

    async updateAdmin(id, data) {
        return this.request(`/admins/${id}`, {
            method: 'PUT',
            body: data
        })
    }

    async deleteAdmin(id) {
        return this.request(`/admins/${id}`, { method: 'DELETE' })
    }

    // ===== LOGS (SuperAdmin only) =====
    async getLogs(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/logs${query ? '?' + query : ''}`)
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

    // ===== CLUBS =====
    async getClubs(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/clubs${query ? '?' + query : ''}`)
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/subjects${query ? '?' + query : ''}`)
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/directions${query ? '?' + query : ''}`)
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/tournaments${query ? '?' + query : ''}`)
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

    // ===== HELP/FAQ =====
    async getFaqs(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/faqs${query ? '?' + query : ''}`)
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/support-messages${query ? '?' + query : ''}`)
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
        const query = new URLSearchParams(params).toString()
        return this.request(`/canteen/orders/my${query ? '?' + query : ''}`)
    }

    // Barcha buyurtmalar (admin)
    async getAllCanteenOrders(params = {}) {
        const query = new URLSearchParams(params).toString()
        return this.request(`/canteen/orders${query ? '?' + query : ''}`)
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
}

export const api = new ApiService()
export default api
