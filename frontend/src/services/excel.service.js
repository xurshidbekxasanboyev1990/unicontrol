import api from './api'

/**
 * Excel Service
 * Excel import/export funksiyalari
 */
const excelService = {
    // ============= IMPORT =============

    /**
     * Talabalarni import qilish
     */
    async importStudents(file, groupId = null, updateExisting = false) {
        const formData = new FormData()
        formData.append('file', file)
        if (groupId) formData.append('group_id', groupId)
        formData.append('update_existing', updateExisting)

        const response = await api.post('/excel/import/students', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return response
    },

    /**
     * Guruhlarni import qilish
     */
    async importGroups(file, updateExisting = false) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('update_existing', updateExisting)

        const response = await api.post('/excel/import/groups', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return response
    },

    /**
     * Davomatni import qilish
     */
    async importAttendance(file, groupId, attendanceDate) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('group_id', groupId)
        formData.append('attendance_date', attendanceDate)

        const response = await api.post('/excel/import/attendance', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return response
    },

    /**
     * Jadvallarni import qilish
     */
    async importSchedules(file, groupId, semester, academicYear) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('group_id', groupId)
        formData.append('semester', semester)
        formData.append('academic_year', academicYear)

        const response = await api.post('/excel/import/schedules', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return response
    },

    // ============= EXPORT =============

    /**
     * Talabalarni export qilish
     */
    async exportStudents(groupId = null, isActive = null) {
        const params = {}
        if (groupId) params.group_id = groupId
        if (isActive !== null) params.is_active = isActive

        const response = await api.get('/excel/export/students', {
            params,
            responseType: 'blob'
        })

        this._downloadFile(response, 'students.xlsx')
        return response
    },

    /**
     * Guruhlarni export qilish
     */
    async exportGroups(faculty = null, course = null) {
        const params = {}
        if (faculty) params.faculty = faculty
        if (course) params.course = course

        const response = await api.get('/excel/export/groups', {
            params,
            responseType: 'blob'
        })

        this._downloadFile(response, 'groups.xlsx')
        return response
    },

    /**
     * Davomatni export qilish
     */
    async exportAttendance(groupId, startDate, endDate) {
        const response = await api.get('/excel/export/attendance', {
            params: {
                group_id: groupId,
                start_date: startDate,
                end_date: endDate
            },
            responseType: 'blob'
        })

        this._downloadFile(response, `attendance_${startDate}_${endDate}.xlsx`)
        return response
    },

    /**
     * Jadvallarni export qilish
     */
    async exportSchedules(groupId, semester = null) {
        const params = { group_id: groupId }
        if (semester) params.semester = semester

        const response = await api.get('/excel/export/schedules', {
            params,
            responseType: 'blob'
        })

        this._downloadFile(response, 'schedule.xlsx')
        return response
    },

    /**
     * Hisobotni export qilish
     */
    async exportReport(reportId) {
        const response = await api.get(`/excel/export/report/${reportId}`, {
            responseType: 'blob'
        })

        this._downloadFile(response, `report_${reportId}.xlsx`)
        return response
    },

    // ============= TEMPLATES =============

    /**
     * Talabalar shabloni yuklab olish
     */
    async downloadStudentsTemplate() {
        const response = await api.get('/excel/templates/students', {
            responseType: 'blob'
        })

        this._downloadFile(response, 'students_template.xlsx')
        return response
    },

    /**
     * Guruhlar shabloni yuklab olish
     */
    async downloadGroupsTemplate() {
        const response = await api.get('/excel/templates/groups', {
            responseType: 'blob'
        })

        this._downloadFile(response, 'groups_template.xlsx')
        return response
    },

    /**
     * Davomat shabloni yuklab olish
     */
    async downloadAttendanceTemplate(groupId) {
        const response = await api.get('/excel/templates/attendance', {
            params: { group_id: groupId },
            responseType: 'blob'
        })

        this._downloadFile(response, 'attendance_template.xlsx')
        return response
    },

    /**
     * Jadval shabloni yuklab olish
     */
    async downloadSchedulesTemplate() {
        const response = await api.get('/excel/templates/schedules', {
            responseType: 'blob'
        })

        this._downloadFile(response, 'schedules_template.xlsx')
        return response
    },

    // ============= HELPER =============

    /**
     * Faylni yuklab olish
     */
    _downloadFile(data, filename) {
        const blob = data instanceof Blob ? data : new Blob([data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    }
}

export default excelService
