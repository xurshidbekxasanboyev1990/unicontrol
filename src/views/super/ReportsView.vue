<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('reports.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('reports.allReportsDesc') }}</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="selectedPeriod" class="px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-500 outline-none text-sm">
          <option value="week">{{ $t('reports.thisWeek') }}</option>
          <option value="month">{{ $t('reports.thisMonth') }}</option>
          <option value="semester">{{ $t('reports.thisSemester') }}</option>
          <option value="year">{{ $t('reports.thisYear') }}</option>
        </select>
        <button 
          @click="exportReport"
          class="px-4 py-2 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2"
        >
          <Download class="w-4 h-4" />
          <span class="hidden sm:inline">{{ $t('reports.exportLabel') }}</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-violet-600">{{ reportStats.total }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.totalReports') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-violet-100 rounded-xl flex items-center justify-center">
            <FileText class="w-5 h-5 sm:w-6 sm:h-6 text-violet-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-amber-600">{{ reportStats.by_status?.pending || 0 }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.pendingStatus') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <Clock class="w-5 h-5 sm:w-6 sm:h-6 text-amber-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-emerald-600">{{ reportStats.by_status?.approved || 0 }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.approvedStatus') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <CheckCircle class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-rose-600">{{ reportStats.by_status?.rejected || 0 }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.rejectedStatus') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <XCircle class="w-5 h-5 sm:w-6 sm:h-6 text-rose-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-blue-600">{{ reportStats.approval_rate }}%</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.approvalRate') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <TrendingUp class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 border-b border-slate-200 pb-0 overflow-x-auto">
      <button
        @click="activeTab = 'all'"
        class="px-4 sm:px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px whitespace-nowrap"
        :class="activeTab === 'all' ? 'border-violet-500 text-violet-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        {{ $t('reports.allReportsTab') }}
      </button>
      <button
        @click="activeTab = 'pending'"
        class="px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px flex items-center gap-2"
        :class="activeTab === 'pending' ? 'border-amber-500 text-amber-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        {{ $t('reports.pendingApproval') }}
        <span v-if="reportStats.by_status?.pending > 0" class="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full font-bold">
          {{ reportStats.by_status.pending }}
        </span>
      </button>
      <button
        @click="activeTab = 'stats'"
        class="px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === 'stats' ? 'border-blue-500 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        {{ $t('reports.statisticsTab') }}
      </button>
    </div>

    <!-- All Reports Tab -->
    <div v-if="activeTab === 'all' || activeTab === 'pending'" class="space-y-4">
      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="filterGroup" class="px-3 py-2 rounded-xl border border-slate-200 text-sm">
          <option :value="null">{{ $t('reports.allGroupsFilter') }}</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
        </select>
        <select v-model="filterType" class="px-3 py-2 rounded-xl border border-slate-200 text-sm">
          <option :value="null">{{ $t('reports.allTypesFilter') }}</option>
          <option value="attendance">{{ $t('attendance.title') }}</option>
          <option value="payment">{{ $t('reports.paymentType') }}</option>
          <option value="students">{{ $t('common.students') }}</option>
          <option value="groups">{{ $t('common.groups') }}</option>
          <option value="analytics">{{ $t('reports.analyticsType') }}</option>
          <option value="ai_analysis">{{ $t('ai.title') }}</option>
          <option value="custom">{{ $t('reports.otherType') }}</option>
        </select>
        <select v-if="activeTab === 'all'" v-model="filterStatus" class="px-3 py-2 rounded-xl border border-slate-200 text-sm">
          <option :value="null">{{ $t('reports.allStatusFilter') }}</option>
          <option value="pending">{{ $t('reports.pendingStatus') }}</option>
          <option value="approved">{{ $t('reports.approvedStatus') }}</option>
          <option value="rejected">{{ $t('reports.rejectedStatus') }}</option>
          <option value="completed">{{ $t('reports.completedStatus') }}</option>
          <option value="failed">{{ $t('reports.failedStatus') }}</option>
        </select>
      </div>

      <!-- Reports table -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full min-w-[700px]">
            <thead>
              <tr class="border-b border-slate-100 bg-slate-50">
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">ID</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('reports.reportName') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('reports.reportType') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('reports.reportCreator') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('reports.reportDate') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('reports.reportStatus') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('reports.reportActions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="report in filteredReports" :key="report.id" class="hover:bg-slate-50 transition-colors">
                <td class="p-4 text-sm text-slate-500">#{{ report.id }}</td>
                <td class="p-4">
                  <p class="font-medium text-slate-800 text-sm">{{ report.name }}</p>
                  <p class="text-xs text-slate-400 mt-0.5">{{ report.description?.substring(0, 60) }}</p>
                </td>
                <td class="p-4">
                  <span class="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-700">
                    {{ formatReportType(report.report_type) }}
                  </span>
                </td>
                <td class="p-4 text-sm text-slate-600">{{ report.created_by_name || `ID: ${report.created_by}` }}</td>
                <td class="p-4 text-sm text-slate-500">{{ formatDate(report.created_at) }}</td>
                <td class="p-4">
                  <span 
                    class="px-2.5 py-1 rounded-lg text-xs font-medium"
                    :class="getStatusClass(report.status)"
                  >
                    {{ getStatusLabel(report.status) }}
                  </span>
                </td>
                <td class="p-4">
                  <div class="flex items-center gap-1">
                    <button 
                      v-if="report.status !== 'approved'"
                      @click="approveReport(report)"
                      class="p-2 rounded-lg text-emerald-600 hover:bg-emerald-50 transition-colors"
                      :title="$t('common.approve')"
                    >
                      <Check class="w-4 h-4" />
                    </button>
                    <button 
                      v-if="report.status !== 'rejected'"
                      @click="openRejectModal(report)"
                      class="p-2 rounded-lg text-rose-600 hover:bg-rose-50 transition-colors"
                      :title="$t('common.reject')"
                    >
                      <X class="w-4 h-4" />
                    </button>
                    <button 
                      @click="downloadReport(report)"
                      class="p-2 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
                      :title="$t('common.download')"
                    >
                      <Download class="w-4 h-4" />
                    </button>
                    <button 
                      @click="deleteReport(report)"
                      class="p-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                      :title="$t('common.delete')"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty state -->
        <div v-if="filteredReports.length === 0" class="p-12 text-center">
          <FileText class="w-12 h-12 mx-auto text-slate-300 mb-3" />
          <p class="text-slate-500">{{ $t('reports.noReportsTable') }}</p>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-4 border-t border-slate-100">
          <span class="text-sm text-slate-500">{{ $t('common.total') }}: {{ totalReports }}</span>
          <div class="flex gap-1 flex-wrap">
            <button 
              v-for="p in totalPages" :key="p"
              @click="currentPage = p; loadReports()"
              class="px-3 py-1.5 rounded-lg text-sm transition-colors"
              :class="currentPage === p ? 'bg-violet-500 text-white' : 'text-slate-600 hover:bg-slate-100'"
            >
              {{ p }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Tab -->
    <div v-if="activeTab === 'stats'" class="space-y-6">
      <!-- Report types distribution -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4">{{ $t('reports.reportTypes') }}</h2>
          <div class="space-y-3">
            <div v-for="(count, type) in reportStats.by_type" :key="type" class="flex items-center gap-3">
              <span class="w-24 text-sm text-slate-600 font-medium">{{ formatReportType(type) }}</span>
              <div class="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full bg-violet-500 transition-all"
                  :style="{ width: `${reportStats.total > 0 ? (count / reportStats.total * 100) : 0}%` }"
                ></div>
              </div>
              <span class="text-sm font-bold text-slate-700 w-8 text-right">{{ count }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4">{{ $t('reports.statusDistribution') }}</h2>
          <div class="grid grid-cols-2 gap-3 sm:gap-4">
            <div class="rounded-xl bg-amber-50 p-3 sm:p-4 text-center">
              <p class="text-xl sm:text-3xl font-bold text-amber-600">{{ reportStats.by_status?.pending || 0 }}</p>
              <p class="text-xs sm:text-sm text-amber-600/70">{{ $t('reports.pendingStatus') }}</p>
            </div>
            <div class="rounded-xl bg-emerald-50 p-3 sm:p-4 text-center">
              <p class="text-xl sm:text-3xl font-bold text-emerald-600">{{ reportStats.by_status?.approved || 0 }}</p>
              <p class="text-xs sm:text-sm text-emerald-600/70">{{ $t('reports.approvedStatus') }}</p>
            </div>
            <div class="rounded-xl bg-rose-50 p-3 sm:p-4 text-center">
              <p class="text-xl sm:text-3xl font-bold text-rose-600">{{ reportStats.by_status?.rejected || 0 }}</p>
              <p class="text-xs sm:text-sm text-rose-600/70">{{ $t('reports.rejectedStatus') }}</p>
            </div>
            <div class="rounded-xl bg-blue-50 p-3 sm:p-4 text-center">
              <p class="text-xl sm:text-3xl font-bold text-blue-600">{{ reportStats.by_status?.completed || 0 }}</p>
              <p class="text-xs sm:text-sm text-blue-600/70">{{ $t('reports.completedStatus') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Faculty attendance overview (real API) -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">{{ $t('reports.groupStats') }}</h2>
        <div class="space-y-4">
          <div v-for="group in groupStats" :key="group.name">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-slate-700">{{ group.name }}</span>
              <div class="flex items-center gap-3">
                <span class="text-sm text-slate-500">{{ group.students }} talaba</span>
                <span 
                  class="font-semibold"
                  :class="group.rate >= 85 ? 'text-emerald-600' : group.rate >= 70 ? 'text-amber-600' : 'text-rose-600'"
                >
                  {{ group.rate }}%
                </span>
              </div>
            </div>
            <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
              <div 
                class="h-full rounded-full transition-all"
                :class="group.rate >= 85 ? 'bg-emerald-500' : group.rate >= 70 ? 'bg-amber-500' : 'bg-rose-500'"
                :style="{ width: group.rate + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div 
      v-if="showRejectModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="showRejectModal = false"
    >
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h3 class="text-lg font-bold text-slate-800 mb-4">{{ $t('reports.rejectTitle') }}</h3>
        <textarea
          v-model="rejectReason"
          rows="4"
          :placeholder="$t('reports.rejectPlaceholder')"
          class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-rose-500 focus:outline-none"
        ></textarea>
        <div class="flex justify-end gap-3 mt-4">
          <button 
            @click="showRejectModal = false"
            class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100"
          >
            {{ $t('common.cancel') }}
          </button>
          <button 
            @click="confirmReject"
            :disabled="rejectReason.length < 5"
            class="px-4 py-2 rounded-xl bg-rose-500 text-white font-medium hover:bg-rose-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('reports.rejectConfirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Super Admin Reports - Full Control Panel
 * Superadmin barcha hisobotlarni boshqarish, tasdiqlash, rad etish, o'chirish
 * va tizim bo'ylab statistika ko'rish imkoniyatiga ega.
 */
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import {
    Check,
    CheckCircle,
    Clock,
    Download,
    FileText,
    Trash2,
    TrendingUp,
    X,
    XCircle,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const dataStore = useDataStore()
const toast = useToastStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const selectedPeriod = ref('month')
const activeTab = ref('all')
const currentPage = ref(1)
const pageSize = 20
const totalReports = ref(0)
const allReports = ref([])
const reportStats = ref({
  total: 0,
  by_status: {},
  by_type: {},
  approval_rate: 0,
})

// Filters
const filterGroup = ref(null)
const filterType = ref(null)
const filterStatus = ref(null)

// Reject modal
const showRejectModal = ref(false)
const rejectingReport = ref(null)
const rejectReason = ref('')

// Groups
const groups = computed(() => dataStore.groups || [])

const totalPages = computed(() => Math.ceil(totalReports.value / pageSize))

// Load reports from API
async function loadReports() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('page_size', pageSize)

    if (activeTab.value === 'pending') {
      params.append('report_status', 'pending')
    } else if (filterStatus.value) {
      params.append('report_status', filterStatus.value)
    }
    if (filterType.value) params.append('report_type', filterType.value)
    if (filterGroup.value) params.append('group_id', filterGroup.value)

    const response = await api.request(`/reports?${params.toString()}`)
    if (response?.items) {
      allReports.value = response.items
      totalReports.value = response.total || 0
    }
  } catch (err) {
    console.error('Load reports error:', err)
    toast.error(t('reports.loadError'))
  } finally {
    loading.value = false
  }
}

// Load stats
async function loadStats() {
  try {
    const resp = await api.request('/reports/stats/summary')
    if (resp) {
      reportStats.value = resp
    }
  } catch (err) {
    console.error('Load stats error:', err)
  }
}

// Filtered reports
const filteredReports = computed(() => allReports.value)

// Group stats (from dataStore)
const groupStats = computed(() => {
  return (dataStore.groups || []).map(group => {
    const studentCount = group.students_count || group.studentCount || group.student_count || 0
    const rate = group.attendance_rate || group.attendanceRate || 0
    return {
      name: group.name,
      students: studentCount,
      rate,
    }
  }).sort((a, b) => b.rate - a.rate)
})

// Actions
async function approveReport(report) {
  try {
    await api.request(`/reports/${report.id}/approve`, { method: 'POST' })
    toast.success(t('reports.reportApproved'))
    await Promise.all([loadReports(), loadStats()])
  } catch (err) {
    console.error('Approve error:', err)
    toast.error(t('reports.approveError'))
  }
}

function openRejectModal(report) {
  rejectingReport.value = report
  rejectReason.value = ''
  showRejectModal.value = true
}

async function confirmReject() {
  if (rejectReason.value.length < 5) return
  try {
    await api.request(`/reports/${rejectingReport.value.id}/reject?reason=${encodeURIComponent(rejectReason.value)}`, { method: 'POST' })
    toast.success(t('reports.reportRejected'))
    showRejectModal.value = false
    await Promise.all([loadReports(), loadStats()])
  } catch (err) {
    console.error('Reject error:', err)
    toast.error(t('reports.rejectError'))
  }
}

async function downloadReport(report, format = 'pdf') {
  try {
    toast.info(t('reports.downloading'))
    const blob = await api.request(`/reports/${report.id}/download?format=${format}`, { responseType: 'blob' })
    const extensions = { pdf: 'pdf', excel: 'xlsx', csv: 'csv' }
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `report_${report.id}.${extensions[format] || 'pdf'}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    toast.success(t('reports.downloaded'))
  } catch (err) {
    console.error('Download error:', err)
    toast.error(t('reports.downloadError'))
  }
}

async function deleteReport(report) {
  if (!confirm(t('reports.deleteConfirm', { name: report.name }))) return
  try {
    await api.request(`/reports/${report.id}`, { method: 'DELETE' })
    toast.success(t('reports.reportDeleted'))
    await Promise.all([loadReports(), loadStats()])
  } catch (err) {
    console.error('Delete error:', err)
    toast.error(t('reports.deleteError'))
  }
}

// Export PDF
const exportReport = async () => {
  toast.info(t('reports.preparingReport'))
  try {
    const doc = new jsPDF('p', 'mm', 'a4')
    const pageWidth = doc.internal.pageSize.getWidth()
    let y = 20

    doc.setFontSize(20)
    doc.setTextColor(30, 41, 59)
    doc.text(t('reports.systemReport'), pageWidth / 2, y, { align: 'center' })
    y += 10

    doc.setFontSize(12)
    doc.setTextColor(100, 116, 139)
    doc.text(`${t('reports.date')}: ${new Date().toLocaleDateString('uz-UZ')}`, pageWidth / 2, y, { align: 'center' })
    y += 15

    // Stats
    autoTable(doc, {
      startY: y,
      head: [[t('reports.indicator'), t('reports.value')]],
      body: [
        [t('reports.totalReports'), reportStats.value.total.toString()],
        [t('reports.statusPending'), (reportStats.value.by_status?.pending || 0).toString()],
        [t('reports.statusApproved'), (reportStats.value.by_status?.approved || 0).toString()],
        [t('reports.statusRejected'), (reportStats.value.by_status?.rejected || 0).toString()],
        [t('reports.approvalRate'), `${reportStats.value.approval_rate}%`],
      ],
      theme: 'striped',
      headStyles: { fillColor: [139, 92, 246] },
    })

    y = doc.lastAutoTable.finalY + 15

    // Reports list
    if (allReports.value.length > 0) {
      doc.setFontSize(14)
      doc.text(t('reports.reportsList'), 20, y)
      y += 5

      autoTable(doc, {
        startY: y,
        head: [['ID', t('reports.name'), t('reports.type'), t('reports.statusLabel'), t('reports.date')]],
        body: allReports.value.slice(0, 30).map(r => [
          `#${r.id}`,
          r.name,
          formatReportType(r.report_type),
          getStatusLabel(r.status),
          formatDate(r.created_at),
        ]),
        theme: 'striped',
        headStyles: { fillColor: [139, 92, 246] },
        styles: { fontSize: 9 },
      })
    }

    // Footer
    const pageCount = doc.internal.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFontSize(9)
      doc.setTextColor(148, 163, 184)
      doc.text('UniControl - SuperAdmin Panel', pageWidth / 2, 285, { align: 'center' })
    }

    doc.save(`superadmin_hisobot_${new Date().toISOString().split('T')[0]}.pdf`)
    toast.success(t('reports.reportDownloaded'))
  } catch (err) {
    console.error('Export error:', err)
    toast.error(t('reports.exportError'))
  }
}

// Helpers
function formatReportType(type) {
  const labels = {
    attendance: t('reports.attendance'),
    payment: t('reports.payment'),
    students: t('reports.students'),
    groups: t('reports.groups'),
    analytics: t('reports.analyticsType'),
    ai_analysis: t('reports.aiAnalysis'),
    custom: t('reports.other'),
  }
  return labels[type] || type
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
}

function getStatusClass(status) {
  const classes = {
    pending: 'bg-amber-100 text-amber-700',
    approved: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-rose-100 text-rose-700',
    completed: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700',
    processing: 'bg-violet-100 text-violet-700',
  }
  return classes[status] || 'bg-slate-100 text-slate-700'
}

function getStatusLabel(status) {
  const labels = {
    pending: t('reports.statusPending'),
    approved: t('reports.statusApproved'),
    rejected: t('reports.statusRejected'),
    completed: t('reports.statusCompleted'),
    failed: t('reports.statusFailed'),
    processing: t('reports.statusProcessing'),
  }
  return labels[status] || status
}

// Watch for filter changes
watch([filterGroup, filterType, filterStatus], () => {
  currentPage.value = 1
  loadReports()
})

watch(activeTab, () => {
  currentPage.value = 1
  loadReports()
})

// Init
onMounted(async () => {
  await dataStore.fetchGroups()
  await Promise.all([loadReports(), loadStats()])
})
</script>
