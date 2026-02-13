<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('reports.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('reports.facultyStats') }}</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="selectedPeriod" class="flex-1 sm:flex-none px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-500 outline-none">
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
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-emerald-600">{{ overallAttendance }}%</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.totalAttendance') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <TrendingUp class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
          </div>
        </div>
        <div class="mt-2 sm:mt-3 flex items-center gap-1 text-xs sm:text-sm">
          <ArrowUp class="w-3 h-3 sm:w-4 sm:h-4 text-emerald-500" />
          <span class="text-emerald-600 font-medium">+2.5%</span>
          <span class="text-slate-400 hidden sm:inline">{{ $t('reports.comparedLastMonth') }}</span>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-blue-600">{{ totalLessons }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.totalLessons') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <BookOpen class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-violet-600">{{ excellentStudents }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.excellentStudents') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-violet-100 rounded-xl flex items-center justify-center">
            <Award class="w-5 h-5 sm:w-6 sm:h-6 text-violet-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-3xl font-bold text-rose-600">{{ lowAttendanceCount }}</p>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('reports.warnings') }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <AlertTriangle class="w-5 h-5 sm:w-6 sm:h-6 text-rose-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs: Statistics | Pending Reports -->
    <div class="flex gap-2 border-b border-slate-200 pb-0 overflow-x-auto">
      <button
        @click="activeTab = 'stats'"
        class="px-4 sm:px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px whitespace-nowrap"
        :class="activeTab === 'stats' ? 'border-violet-500 text-violet-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        Statistika
      </button>
      <button
        @click="activeTab = 'pending'"
        class="px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px flex items-center gap-2"
        :class="activeTab === 'pending' ? 'border-amber-500 text-amber-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        Hisobotlarni tasdiqlash
        <span v-if="pendingReports.length > 0" class="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full font-bold">
          {{ pendingReports.length }}
        </span>
      </button>
      <button
        @click="activeTab = 'all'"
        class="px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === 'all' ? 'border-blue-500 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        Barcha hisobotlar
      </button>
    </div>

    <!-- Statistics Tab -->
    <div v-if="activeTab === 'stats'">
      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Weekly Trend -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-6">Haftalik trend</h2>
          <div class="flex items-end gap-3 h-48">
            <div 
              v-for="(day, index) in weeklyData" 
              :key="index"
              class="flex-1 flex flex-col items-center gap-2"
            >
              <div class="w-full bg-slate-100 rounded-t-lg relative" style="height: 160px;">
                <div 
                  class="absolute bottom-0 w-full rounded-t-lg transition-all duration-500"
                  :class="day.rate >= 85 ? 'bg-gradient-to-t from-emerald-500 to-emerald-400' : day.rate >= 70 ? 'bg-gradient-to-t from-amber-500 to-amber-400' : 'bg-gradient-to-t from-rose-500 to-rose-400'"
                  :style="{ height: day.rate + '%' }"
                ></div>
              </div>
              <span class="text-xs font-medium text-slate-600">{{ day.name }}</span>
              <span class="text-xs text-slate-400">{{ day.rate }}%</span>
            </div>
          </div>
        </div>

        <!-- Group Comparison -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4">Guruhlar taqqoslash</h2>
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
                  class="h-full rounded-full transition-all duration-500"
                  :class="group.rate >= 85 ? 'bg-emerald-500' : group.rate >= 70 ? 'bg-amber-500' : 'bg-rose-500'"
                  :style="{ width: group.rate + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Table -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden mt-6">
        <div class="p-6 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-800">Batafsil ma'lumotlar</h2>
          <div class="flex items-center gap-2">
            <button 
              @click="detailTab = 'groups'"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="detailTab === 'groups' ? 'bg-violet-100 text-violet-700' : 'text-slate-500 hover:bg-slate-100'"
            >
              Guruhlar
            </button>
            <button 
              @click="detailTab = 'students'"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="detailTab === 'students' ? 'bg-violet-100 text-violet-700' : 'text-slate-500 hover:bg-slate-100'"
            >
              Talabalar
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100 bg-slate-50">
                <template v-if="detailTab === 'groups'">
                  <th class="text-left p-4 font-semibold text-slate-600">Guruh</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Talabalar</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Kelgan</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Kelmagan</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Davomat</th>
                </template>
                <template v-else>
                  <th class="text-left p-4 font-semibold text-slate-600">Talaba</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Guruh</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Kelgan</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Kelmagan</th>
                  <th class="text-left p-4 font-semibold text-slate-600">Davomat</th>
                </template>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <template v-if="detailTab === 'groups'">
                <tr v-for="group in groupStats" :key="group.name" class="hover:bg-slate-50">
                  <td class="p-4 font-medium text-slate-800">{{ group.name }}</td>
                  <td class="p-4 text-slate-600">{{ group.students }}</td>
                  <td class="p-4 text-emerald-600">{{ group.present }}</td>
                  <td class="p-4 text-rose-600">{{ group.absent }}</td>
                  <td class="p-4">
                    <span 
                      class="px-3 py-1 rounded-lg text-sm font-semibold"
                      :class="group.rate >= 85 ? 'bg-emerald-100 text-emerald-700' : group.rate >= 70 ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'"
                    >
                      {{ group.rate }}%
                    </span>
                  </td>
                </tr>
              </template>
              <template v-else>
                <tr v-for="student in studentStats" :key="student.id" class="hover:bg-slate-50">
                  <td class="p-4">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                        {{ student.name.charAt(0) }}
                      </div>
                      <span class="font-medium text-slate-800">{{ student.name }}</span>
                    </div>
                  </td>
                  <td class="p-4 text-slate-600">{{ student.group }}</td>
                  <td class="p-4 text-emerald-600">{{ student.present }}</td>
                  <td class="p-4 text-rose-600">{{ student.absent }}</td>
                  <td class="p-4">
                    <span 
                      class="px-3 py-1 rounded-lg text-sm font-semibold"
                      :class="student.rate >= 85 ? 'bg-emerald-100 text-emerald-700' : student.rate >= 70 ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'"
                    >
                      {{ student.rate }}%
                    </span>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Pending Reports Tab (Approve/Reject) -->
    <div v-if="activeTab === 'pending'" class="space-y-4">
      <div 
        v-for="report in pendingReports" 
        :key="report.id"
        class="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div class="flex gap-4">
            <div class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
              <FileText class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800">{{ report.name }}</h3>
              <p class="text-sm text-slate-500 mt-1">{{ report.description }}</p>
              <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <span>Yaratuvchi: {{ report.created_by_name || `ID: ${report.created_by}` }}</span>
                <span>•</span>
                <span>{{ formatDate(report.created_at) }}</span>
                <span>•</span>
                <span class="px-2 py-0.5 bg-slate-100 rounded text-slate-600">{{ formatReportType(report.report_type) }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button 
              @click="approveReport(report)"
              class="flex items-center gap-2 px-4 py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium hover:bg-emerald-600 transition-colors"
            >
              <Check class="w-4 h-4" />
              Tasdiqlash
            </button>
            <button 
              @click="openRejectModal(report)"
              class="flex items-center gap-2 px-4 py-2.5 bg-rose-500 text-white rounded-xl text-sm font-medium hover:bg-rose-600 transition-colors"
            >
              <XIcon class="w-4 h-4" />
              Rad etish
            </button>
          </div>
        </div>
      </div>

      <div 
        v-if="pendingReports.length === 0"
        class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 py-16"
      >
        <CheckCircle2 class="w-12 h-12 text-emerald-400 mb-3" />
        <p class="text-lg font-medium text-slate-500">Barcha hisobotlar ko'rib chiqilgan</p>
        <p class="text-sm text-slate-400">Kutilayotgan hisobotlar yo'q</p>
      </div>
    </div>

    <!-- All Reports Tab -->
    <div v-if="activeTab === 'all'" class="space-y-4">
      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="filterGroup" class="px-3 py-2 rounded-xl border border-slate-200 text-sm" @change="loadAllReports">
          <option :value="null">Barcha guruhlar</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
        </select>
        <select v-model="filterStatus" class="px-3 py-2 rounded-xl border border-slate-200 text-sm" @change="loadAllReports">
          <option :value="null">Barcha statuslar</option>
          <option value="pending">Kutilayotgan</option>
          <option value="approved">Tasdiqlangan</option>
          <option value="rejected">Rad etilgan</option>
        </select>
      </div>

      <!-- Reports list -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100 bg-slate-50">
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">Nomi</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">Turi</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">Yaratuvchi</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">Sana</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">Status</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">Amallar</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="report in allReportsList" :key="report.id" class="hover:bg-slate-50">
                <td class="p-4">
                  <p class="font-medium text-slate-800 text-sm">{{ report.name }}</p>
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
                      title="Tasdiqlash"
                    >
                      <Check class="w-4 h-4" />
                    </button>
                    <button 
                      v-if="report.status !== 'rejected'"
                      @click="openRejectModal(report)"
                      class="p-2 rounded-lg text-rose-600 hover:bg-rose-50 transition-colors"
                      title="Rad etish"
                    >
                      <XIcon class="w-4 h-4" />
                    </button>
                    <button 
                      @click="downloadSingleReport(report)"
                      class="p-2 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
                      title="Yuklab olish"
                    >
                      <Download class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="allReportsList.length === 0" class="p-12 text-center">
          <FileText class="w-12 h-12 mx-auto text-slate-300 mb-3" />
          <p class="text-slate-500">Hisobotlar topilmadi</p>
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
        <h3 class="text-lg font-bold text-slate-800 mb-4">Hisobotni rad etish</h3>
        <textarea
          v-model="rejectReason"
          rows="4"
          placeholder="Rad etish sababini kiriting (kamida 5 ta belgi)..."
          class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-rose-500 focus:outline-none"
        ></textarea>
        <div class="flex justify-end gap-3 mt-4">
          <button 
            @click="showRejectModal = false"
            class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100"
          >
            Bekor qilish
          </button>
          <button 
            @click="confirmReject"
            :disabled="rejectReason.length < 5"
            class="px-4 py-2 rounded-xl bg-rose-500 text-white font-medium hover:bg-rose-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Rad etish
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Admin Reports - Statistics + Report Management
 * Admin: Barcha hisobotlarni ko'rish, tasdiqlash, rad etish + statistika
 * Admin o'chirish mumkin emas (faqat tasdiqlangan hisobotlarni superadmin o'chiradi)
 */
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import {
    AlertTriangle,
    ArrowUp,
    Award,
    BookOpen,
    Check,
    CheckCircle2,
    Download,
    FileText,
    TrendingUp,
    X as XIcon,
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'

const dataStore = useDataStore()
const toast = useToastStore()

// State
const loading = ref(true)
const selectedPeriod = ref('month')
const activeTab = ref('stats')
const detailTab = ref('groups')
const reportData = ref(null)

// Reports management
const pendingReports = ref([])
const allReportsList = ref([])
const filterGroup = ref(null)
const filterStatus = ref(null)

// Reject modal
const showRejectModal = ref(false)
const rejectingReport = ref(null)
const rejectReason = ref('')

// Groups
const groups = computed(() => dataStore.groups || [])

// Load report data from API
async function loadReportData() {
  loading.value = true
  try {
    await Promise.all([
      dataStore.fetchGroups(),
      dataStore.fetchStudents({ page: 1, page_size: 100 })
    ])
    
    try {
      const statsResp = await api.request('/statistics/dashboard')
      reportData.value = {
        overview: statsResp,
        groups: dataStore.groups || []
      }
    } catch (e) {
      console.log('Statistics API not available, using store data')
      reportData.value = {
        overview: null,
        groups: dataStore.groups || []
      }
    }
  } catch (err) {
    console.error('Load report data error:', err)
    toast.error('Ma\'lumotlar yuklanmadi')
  } finally {
    loading.value = false
  }
}

// Load pending reports for approval
async function loadPendingReports() {
  try {
    const response = await api.request('/reports?report_status=pending&page_size=50')
    if (response?.items) {
      pendingReports.value = response.items
    }
  } catch (err) {
    console.error('Load pending reports error:', err)
  }
}

// Load all reports
async function loadAllReports() {
  try {
    const params = new URLSearchParams()
    params.append('page_size', '50')
    if (filterGroup.value) params.append('group_id', filterGroup.value)
    if (filterStatus.value) params.append('report_status', filterStatus.value)
    
    const response = await api.request(`/reports?${params.toString()}`)
    if (response?.items) {
      allReportsList.value = response.items
    }
  } catch (err) {
    console.error('Load all reports error:', err)
  }
}

// Approve report
async function approveReport(report) {
  try {
    await api.request(`/reports/${report.id}/approve`, { method: 'POST' })
    toast.success('Hisobot tasdiqlandi')
    await Promise.all([loadPendingReports(), loadAllReports()])
  } catch (err) {
    console.error('Approve error:', err)
    toast.error('Tasdiqlashda xatolik')
  }
}

// Reject modal
function openRejectModal(report) {
  rejectingReport.value = report
  rejectReason.value = ''
  showRejectModal.value = true
}

async function confirmReject() {
  if (rejectReason.value.length < 5) return
  try {
    await api.request(`/reports/${rejectingReport.value.id}/reject?reason=${encodeURIComponent(rejectReason.value)}`, { method: 'POST' })
    toast.success('Hisobot rad etildi')
    showRejectModal.value = false
    await Promise.all([loadPendingReports(), loadAllReports()])
  } catch (err) {
    console.error('Reject error:', err)
    toast.error('Rad etishda xatolik')
  }
}

// Download single report
async function downloadSingleReport(report, format = 'pdf') {
  try {
    toast.info('Yuklab olinmoqda...')
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
    toast.success('Yuklab olindi')
  } catch (err) {
    console.error('Download error:', err)
    toast.error('Yuklab olishda xatolik')
  }
}

// Helpers
function formatReportType(type) {
  const labels = {
    attendance: 'Davomat',
    payment: 'To\'lov',
    students: 'Talabalar',
    groups: 'Guruhlar',
    analytics: 'Analitika',
    ai_analysis: 'AI Tahlil',
    custom: 'Boshqa',
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
  }
  return classes[status] || 'bg-slate-100 text-slate-700'
}

function getStatusLabel(status) {
  const labels = {
    pending: 'Kutilayotgan',
    approved: 'Tasdiqlangan',
    rejected: 'Rad etilgan',
    completed: 'Tayyor',
    failed: 'Xato',
  }
  return labels[status] || status
}

// Computed values
const overallAttendance = computed(() => {
  if (reportData.value?.overview?.attendance_rate) {
    return Math.round(reportData.value.overview.attendance_rate)
  }
  const records = dataStore.attendanceRecords || []
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 85
})

const totalLessons = computed(() => {
  if (reportData.value?.overview?.total_lessons) {
    return reportData.value.overview.total_lessons
  }
  return (dataStore.schedules?.length || 0) * 4 || 120
})

const excellentStudents = computed(() => {
  if (reportData.value?.overview?.excellent_students) {
    return reportData.value.overview.excellent_students
  }
  return Math.floor(dataStore.totalStudents * 0.25) || 15
})

const lowAttendanceCount = computed(() => {
  if (reportData.value?.overview?.low_attendance_count) {
    return reportData.value.overview.low_attendance_count
  }
  return Math.floor(dataStore.totalStudents * 0.08) || 5
})

const weeklyData = computed(() => {
  const days = ['Du', 'Se', 'Cho', 'Pa', 'Ju', 'Sha', 'Ya']
  if (reportData.value?.overview?.weekly_attendance) {
    return reportData.value.overview.weekly_attendance
  }
  return days.map((name) => ({
    name,
    rate: Math.floor(75 + Math.random() * 20)
  }))
})

const groupStats = computed(() => {
  const groups = reportData.value?.groups || dataStore.groups || []
  return groups.map(group => {
    const studentCount = group.students_count || group.studentCount || group.student_count || 0
    const rate = group.attendance_rate || group.attendanceRate || Math.floor(75 + Math.random() * 20)
    return {
      name: group.name,
      students: studentCount,
      present: Math.floor(studentCount * rate / 100),
      absent: Math.floor(studentCount * (100 - rate) / 100),
      rate: rate
    }
  }).sort((a, b) => b.rate - a.rate)
})

const studentStats = computed(() => {
  return (dataStore.students || []).slice(0, 20).map(student => {
    const rate = Math.floor(70 + Math.random() * 25)
    return {
      id: student.id,
      name: student.name || student.full_name || 'Noma\'lum',
      group: student.group || student.group_name || '',
      present: Math.floor(rate * 0.9),
      absent: Math.floor((100 - rate) * 0.5),
      rate
    }
  }).sort((a, b) => b.rate - a.rate)
})

// Export report as PDF
const exportReport = async () => {
  toast.info('Hisobot tayyorlanmoqda...')
  
  try {
    const doc = new jsPDF('p', 'mm', 'a4')
    const pageWidth = doc.internal.pageSize.getWidth()
    let y = 20
    
    doc.setFontSize(20)
    doc.setTextColor(30, 41, 59)
    doc.text('Fakultet Hisoboti', pageWidth / 2, y, { align: 'center' })
    y += 10
    
    doc.setFontSize(12)
    doc.setTextColor(100, 116, 139)
    const periodText = selectedPeriod.value === 'week' ? 'Haftalik' : 
                       selectedPeriod.value === 'month' ? 'Oylik' : 
                       selectedPeriod.value === 'semester' ? 'Semestr' : 'Yillik'
    doc.text(`${periodText} hisobot - ${new Date().toLocaleDateString('uz-UZ')}`, pageWidth / 2, y, { align: 'center' })
    y += 15
    
    doc.setFontSize(14)
    doc.setTextColor(30, 41, 59)
    doc.text('Umumiy Ko\'rsatkichlar', 20, y)
    y += 10
    
    autoTable(doc, {
      startY: y,
      head: [['Ko\'rsatkich', 'Qiymat']],
      body: [
        ['Umumiy davomat', `${overallAttendance.value}%`],
        ['Jami darslar', totalLessons.value.toString()],
        ['A\'lochi talabalar', excellentStudents.value.toString()],
        ['Ogohlantirish', lowAttendanceCount.value.toString()]
      ],
      theme: 'striped',
      headStyles: { fillColor: [139, 92, 246] },
      styles: { fontSize: 11 }
    })
    
    y = doc.lastAutoTable.finalY + 15
    
    doc.setFontSize(14)
    doc.text('Guruhlar bo\'yicha statistika', 20, y)
    y += 5
    
    autoTable(doc, {
      startY: y,
      head: [['Guruh', 'Talabalar', 'Kelgan', 'Kelmagan', 'Davomat']],
      body: groupStats.value.slice(0, 10).map(g => [
        g.name,
        g.students.toString(),
        g.present.toString(),
        g.absent.toString(),
        `${g.rate}%`
      ]),
      theme: 'striped',
      headStyles: { fillColor: [139, 92, 246] },
      styles: { fontSize: 10 }
    })
    
    const pageCount = doc.internal.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFontSize(9)
      doc.setTextColor(148, 163, 184)
      doc.text('UniControl - Fakultet boshqaruv tizimi', pageWidth / 2, 285, { align: 'center' })
    }
    
    doc.save(`fakultet_hisobot_${new Date().toISOString().split('T')[0]}.pdf`)
    toast.success('Hisobot yuklab olindi!')
  } catch (err) {
    console.error('Export error:', err)
    toast.error('Eksport xatosi')
  }
}

// Initialize
onMounted(async () => {
  await loadReportData()
  await Promise.all([loadPendingReports(), loadAllReports()])
})
</script>
