import api from './api'

/**
 * AI Analysis Service
 * OpenAI orqali AI tahlil funksiyalari
 */
const aiService = {
    /**
     * Talaba tahlili
     */
    async analyzeStudent(studentId, options = {}) {
        const response = await api.post('/ai/analyze/student', {
            student_id: studentId,
            include_attendance: options.includeAttendance ?? true,
            include_grades: options.includeGrades ?? true,
            include_behavior: options.includeBehavior ?? true
        })
        return response
    },

    /**
     * Guruh tahlili
     */
    async analyzeGroup(groupId, options = {}) {
        const response = await api.post('/ai/analyze/group', {
            group_id: groupId,
            semester: options.semester,
            include_attendance: options.includeAttendance ?? true,
            include_performance: options.includePerformance ?? true
        })
        return response
    },

    /**
     * Davomat bashorati
     */
    async predictAttendance(params = {}) {
        const response = await api.post('/ai/predict/attendance', {
            student_id: params.studentId,
            group_id: params.groupId,
            days_ahead: params.daysAhead || 7
        })
        return response
    },

    /**
     * AI chat
     */
    async chat(message, context = null, history = []) {
        const response = await api.post('/ai/chat', {
            message,
            context,
            conversation_history: history
        })
        return response
    },

    /**
     * Hisobot xulosa
     */
    async summarizeReport(reportId, language = 'uz') {
        const response = await api.post('/ai/summarize/report', {
            report_id: reportId,
            language
        })
        return response
    },

    /**
     * Dashboard insights
     */
    async getDashboardInsights() {
        const response = await api.get('/ai/insights/dashboard')
        return response
    },

    /**
     * Talaba uchun tavsiyalar
     */
    async getRecommendations(studentId) {
        const response = await api.get(`/ai/recommendations/${studentId}`)
        return response
    },

    /**
     * Bildirishnoma matni generatsiya
     */
    async generateNotificationText(context, tone = 'formal') {
        const response = await api.post('/ai/generate/notification-text', null, {
            params: { context, tone }
        })
        return response
    },

    /**
     * AI health check
     */
    async healthCheck() {
        const response = await api.get('/ai/health')
        return response
    }
}

export default aiService
