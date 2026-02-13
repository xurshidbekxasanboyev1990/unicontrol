<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">{{ $t('attendance.management') }}</h1>
        <p class="text-slate-500">{{ $t('attendance.managementDesc') }}</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="exportToExcel" class="px-4 py-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors flex items-center gap-2">
          <Download class="w-4 h-4" />
          Excel
        </button>
        <button @click="loadAttendance" class="p-2.5 hover:bg-slate-100 rounded-xl transition-colors">
          <RefreshCw class="w-5 h-5 text-slate-500" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-5">
      <div class="flex items-center gap-3 mb-4">
        <Filter class="w-5 h-5 text-slate-400" />
        <h3 class="font-semibold text-slate-700">{{ $t('attendance.filters') }}</h3>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <!-- Group Select -->
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">{{ $t('attendance.group') }}</label>
          <select v-model="filters.groupId" @change="loadAttendance" class="w-full px-3 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
            <option :value="null">{{ $t('attendance.allGroups') }}</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
          </select>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">{{ $t('attendance.statusLabel') }}</label>
          <select v-model="filters.status" @change="loadAttendance" class="w-full px-3 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
            <option :value="null">{{ $t('attendance.allStatuses') }}</option>
            <option value="present">✅ {{ $t('attendance.statusPresent') }}</option>
            <option value="absent">❌ {{ $t('attendance.statusAbsent') }}</option>
            <option value="late">⚠️ {{ $t('attendance.statusLate') }}</option>
            <option value="excused">📋 {{ $t('attendance.statusExcused') }}</option>
          </select>
        </div>

        <!-- Date From -->
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">{{ $t('attendance.dateFrom') }}</label>
          <input v-model="filters.dateFrom" type="date" @change="loadAttendance" class="w-full px-3 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm" />
        </div>

        <!-- Date To -->
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">{{ $t('attendance.dateTo') }}</label>
          <input v-model="filters.dateTo" type="date" @change="loadAttendance" class="w-full px-3 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm" />
        </div>

        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">{{ $t('common.search') }}</label>
          <div class="relative">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input v-model="searchQuery" type="text" :placeholder="$t('attendance.searchStudent')" class="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm" />
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
      <div class="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-2xl p-3 sm:p-5 border border-slate-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xl sm:text-2xl font-bold text-slate-700">{{ stats.total }}</p>
            <p class="text-xs sm:text-sm text-slate-500 font-medium">{{ $t('attendance.total') }}</p>
          </div>
          <div class="w-10 h-10 bg-slate-200/50 rounded-xl flex items-center justify-center">
            <Users class="w-5 h-5 text-slate-500" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-5 border border-emerald-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-emerald-600">{{ stats.present }}</p>
            <p class="text-sm text-emerald-700 font-medium">{{ $t('attendance.statusPresent') }}</p>
          </div>
          <div class="w-10 h-10 bg-emerald-200/50 rounded-xl flex items-center justify-center">
            <CheckCircle class="w-5 h-5 text-emerald-500" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-rose-50 to-rose-100/50 rounded-2xl p-5 border border-rose-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-rose-600">{{ stats.absent }}</p>
            <p class="text-sm text-rose-700 font-medium">{{ $t('attendance.statusAbsent') }}</p>
          </div>
          <div class="w-10 h-10 bg-rose-200/50 rounded-xl flex items-center justify-center">
            <XCircle class="w-5 h-5 text-rose-500" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-2xl p-5 border border-amber-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-amber-600">{{ stats.late }}</p>
            <p class="text-sm text-amber-700 font-medium">{{ $t('attendance.statusLate') }}</p>
          </div>
          <div class="w-10 h-10 bg-amber-200/50 rounded-xl flex items-center justify-center">
            <Clock class="w-5 h-5 text-amber-500" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-5 border border-blue-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-blue-600">{{ stats.excused }}</p>
            <p class="text-sm text-blue-700 font-medium">{{ $t('attendance.statusExcused') }}</p>
          </div>
          <div class="w-10 h-10 bg-blue-200/50 rounded-xl flex items-center justify-center">
            <FileText class="w-5 h-5 text-blue-500" />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="text-center">
        <RefreshCw class="w-10 h-10 text-emerald-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-500">{{ $t('attendance.loadingText') }}</p>
      </div>
    </div>

    <!-- Attendance Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200">
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">#</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableStudent') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableGroup') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableDate') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableSubject') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tablePeriod') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableStatus') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableDelay') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableNote') }}</th>
              <th class="text-left px-3 sm:px-5 py-3 sm:py-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('attendance.tableActions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(record, index) in filteredRecords" :key="record.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-3 sm:px-5 py-3 sm:py-4 text-slate-400 font-medium">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="px-3 sm:px-5 py-3 sm:py-4">
                <div class="flex items-center gap-2 sm:gap-3">
                  <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center flex-shrink-0">
                    <User class="w-4 h-4 text-slate-500" />
                  </div>
                  <span class="font-medium text-slate-800 whitespace-nowrap">{{ record.student_name || $t('attendance.unknownStudent') }}</span>
                </div>
              </td>
              <td class="px-3 sm:px-5 py-3 sm:py-4 text-slate-600 whitespace-nowrap">{{ getGroupName(record) }}</td>
              <td class="px-3 sm:px-5 py-3 sm:py-4 text-slate-600 whitespace-nowrap">{{ formatDate(record.date) }}</td>
              <td class="px-3 sm:px-5 py-3 sm:py-4 text-slate-600 whitespace-nowrap">{{ record.subject || '-' }}</td>
              <td class="px-3 sm:px-5 py-3 sm:py-4 text-slate-600">{{ record.lesson_number || '-' }}</td>
              <td class="px-5 py-4">
                <span :class="getStatusClasses(record.status)" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium">
                  {{ getStatusEmoji(record.status) }} {{ getStatusText(record.status) }}
                </span>
              </td>
              <td class="px-5 py-4 text-slate-600">
                <span v-if="record.status === 'late' && record.late_minutes > 0" class="text-amber-600 font-medium">
                  {{ record.late_minutes }} {{ $t('attendance.delayMinutes') }}
                </span>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="px-5 py-4 text-slate-600 max-w-[200px] truncate" :title="record.note || record.excuse_reason || ''">
                {{ record.note || record.excuse_reason || '-' }}
              </td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-2">
                  <button
                    @click="openEditModal(record)"
                    :disabled="!record.is_editable && !isSuperAdmin"
                    :class="[
                      'p-2 rounded-lg transition-colors',
                      record.is_editable || isSuperAdmin
                        ? 'text-blue-500 hover:bg-blue-50'
                        : 'text-slate-300 cursor-not-allowed'
                    ]"
                    :title="record.is_editable || isSuperAdmin ? $t('common.edit') : $t('attendance.editBlocked')"
                  >
                    <Edit3 class="w-4 h-4" />
                  </button>
                  <button
                    v-if="isSuperAdmin"
                    @click="deleteRecord(record)"
                    class="p-2 text-rose-400 hover:bg-rose-50 rounded-lg transition-colors"
                    :title="$t('common.delete')"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                  <div v-if="!record.is_editable && !isSuperAdmin" class="flex items-center gap-1 text-slate-400" title="24 soatdan oshgan">
                    <Lock class="w-3.5 h-3.5" />
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="filteredRecords.length === 0 && !loading" class="p-12 text-center">
        <ClipboardList class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-lg font-medium text-slate-600">{{ $t('attendance.noRecordsTitle') }}</p>
        <p class="text-sm text-slate-400 mt-1">{{ $t('attendance.noRecordsDesc') }}</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-4 sm:px-5 py-3 sm:py-4 border-t border-slate-100">
        <p class="text-sm text-slate-500">
          Jami {{ totalRecords }} ta yozuv, {{ currentPage }}/{{ totalPages }} sahifa
        </p>
        <div class="flex items-center gap-1 sm:gap-2 flex-wrap">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="px-3 py-2 rounded-lg text-sm border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <template v-for="page in visiblePages" :key="page">
            <button @click="changePage(page)" :class="[
              'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              page === currentPage ? 'bg-emerald-500 text-white' : 'border border-slate-200 hover:bg-slate-50 text-slate-600'
            ]">
              {{ page }}
            </button>
          </template>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="px-3 py-2 rounded-lg text-sm border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <Teleport to="body">
      <div v-if="editModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="editModal.show = false">
        <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden">
          <div class="bg-gradient-to-r from-blue-500 to-indigo-500 p-6 text-white">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-xl font-bold">{{ $t('attendance.editTitle') }}</h3>
                <p class="text-blue-100 text-sm mt-1">{{ editModal.record?.student_name }}</p>
              </div>
              <button @click="editModal.show = false" class="p-2 hover:bg-white/20 rounded-xl transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>
          <div class="p-6 space-y-5">
            <!-- Status -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('attendance.statusLabel') }}</label>
              <div class="grid grid-cols-4 gap-2">
                <button v-for="st in statusOptions" :key="st.value" @click="editModal.form.status = st.value"
                  :class="[
                    'flex flex-col items-center gap-1.5 p-3 rounded-xl text-sm font-medium transition-all border-2',
                    editModal.form.status === st.value
                      ? st.activeClass
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  ]">
                  <span class="text-lg">{{ st.emoji }}</span>
                  <span class="text-xs">{{ st.label }}</span>
                </button>
              </div>
            </div>

            <!-- Late Minutes -->
            <div v-if="editModal.form.status === 'late'">
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('attendance.delayLabel') }}</label>
              <input v-model.number="editModal.form.late_minutes" type="number" min="1" max="90" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm" />
            </div>

            <!-- Note -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('attendance.noteLabel') }}</label>
              <textarea v-model="editModal.form.note" rows="2" :placeholder="$t('attendance.notePlaceholder')" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm resize-none"></textarea>
            </div>

            <!-- Excuse Reason -->
            <div v-if="editModal.form.status === 'excused' || editModal.form.status === 'absent'">
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('attendance.reasonLabel') }}</label>
              <textarea v-model="editModal.form.excuse_reason" rows="2" :placeholder="$t('attendance.reasonPlaceholder')" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm resize-none"></textarea>
            </div>
          </div>
          <div class="px-6 pb-6 flex gap-3">
            <button @click="editModal.show = false" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">
              {{ $t('attendance.cancelBtn') }}
            </button>
            <button @click="saveEdit" :disabled="editModal.saving" class="flex-1 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-xl font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
              <RefreshCw v-if="editModal.saving" class="w-4 h-4 animate-spin" />
              {{ $t('attendance.saveBtn') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import {
    CheckCircle,
    ChevronLeft,
    ChevronRight,
    ClipboardList,
    Clock,
    Download,
    Edit3,
    FileText,
    Filter,
    Lock,
    RefreshCw,
    Search,
    Trash2,
    User,
    Users,
    X,
    XCircle
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'

const authStore = useAuthStore()
const toast = useToastStore()

// State
const loading = ref(true)
const attendanceRecords = ref([])
const groups = ref([])
const totalRecords = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const searchQuery = ref('')

const filters = reactive({
  groupId: null,
  status: null,
  dateFrom: new Date().toISOString().split('T')[0],
  dateTo: new Date().toISOString().split('T')[0]
})

const editModal = reactive({
  show: false,
  saving: false,
  record: null,
  form: {
    status: 'present',
    late_minutes: 0,
    note: '',
    excuse_reason: ''
  }
})

const statusOptions = [
  { value: 'present', label: 'Keldi', emoji: '✅', activeClass: 'border-emerald-500 bg-emerald-50 text-emerald-700' },
  { value: 'absent', label: 'Kelmadi', emoji: '❌', activeClass: 'border-rose-500 bg-rose-50 text-rose-700' },
  { value: 'late', label: 'Kech qoldi', emoji: '⚠️', activeClass: 'border-amber-500 bg-amber-50 text-amber-700' },
  { value: 'excused', label: 'Sababli', emoji: '📋', activeClass: 'border-blue-500 bg-blue-50 text-blue-700' }
]

// Computed
const isSuperAdmin = computed(() => authStore.isSuperAdmin)

const totalPages = computed(() => Math.ceil(totalRecords.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const filteredRecords = computed(() => {
  if (!searchQuery.value) return attendanceRecords.value
  const q = searchQuery.value.toLowerCase()
  return attendanceRecords.value.filter(r =>
    (r.student_name || '').toLowerCase().includes(q) ||
    (r.subject || '').toLowerCase().includes(q) ||
    (r.note || '').toLowerCase().includes(q)
  )
})

const stats = computed(() => {
  const records = attendanceRecords.value
  return {
    total: totalRecords.value,
    present: records.filter(r => r.status === 'present').length,
    absent: records.filter(r => r.status === 'absent').length,
    late: records.filter(r => r.status === 'late').length,
    excused: records.filter(r => r.status === 'excused').length
  }
})

// Methods
async function loadGroups() {
  try {
    const resp = await api.getGroups({ page_size: 200 })
    groups.value = (resp.items || resp.data || []).sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  } catch (e) {
    console.error('Load groups error:', e)
  }
}

async function loadAttendance() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filters.groupId) params.group_id = filters.groupId
    if (filters.status) params.status = filters.status
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo

    const resp = await api.getAttendance(params)
    attendanceRecords.value = resp.items || resp.data || []
    totalRecords.value = resp.total || attendanceRecords.value.length
  } catch (e) {
    console.error('Load attendance error:', e)
    toast.error('Davomatni yuklashda xatolik')
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadAttendance()
}

function getGroupName(record) {
  // Try to find group name from groups list by student
  if (record.group_name) return record.group_name
  return '-'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr + 'T12:00:00').toLocaleDateString('uz-UZ', {
      day: 'numeric',
      month: 'short'
    })
  } catch {
    return dateStr
  }
}

function getStatusEmoji(status) {
  const map = { present: '✅', absent: '❌', late: '⚠️', excused: '📋' }
  return map[status] || '❓'
}

function getStatusText(status) {
  const map = { present: 'Keldi', absent: 'Kelmadi', late: 'Kech qoldi', excused: 'Sababli' }
  return map[status] || status
}

function getStatusClasses(status) {
  const map = {
    present: 'bg-emerald-100 text-emerald-700',
    absent: 'bg-rose-100 text-rose-700',
    late: 'bg-amber-100 text-amber-700',
    excused: 'bg-blue-100 text-blue-700'
  }
  return map[status] || 'bg-slate-100 text-slate-700'
}

function openEditModal(record) {
  if (!record.is_editable && !isSuperAdmin.value) {
    toast.warning('Bu davomatni tahrirlash vaqti tugagan (24 soatdan oshgan)')
    return
  }
  editModal.record = record
  editModal.form = {
    status: record.status,
    late_minutes: record.late_minutes || 0,
    note: record.note || '',
    excuse_reason: record.excuse_reason || ''
  }
  editModal.show = true
}

async function saveEdit() {
  editModal.saving = true
  try {
    const data = {
      status: editModal.form.status,
      late_minutes: editModal.form.status === 'late' ? editModal.form.late_minutes : 0,
      note: editModal.form.note || null,
      excuse_reason: editModal.form.excuse_reason || null
    }

    await api.request(`/attendance/${editModal.record.id}`, {
      method: 'PUT',
      body: data
    })

    toast.success('Davomat yangilandi')
    editModal.show = false
    await loadAttendance()
  } catch (e) {
    console.error('Save edit error:', e)
    const msg = e?.response?.data?.detail || e?.message || 'Xatolik yuz berdi'
    if (msg.includes('24 soat')) {
      toast.error('24 soatdan oshgan — tahrirlash bloklangan')
    } else {
      toast.error(msg)
    }
  } finally {
    editModal.saving = false
  }
}

async function deleteRecord(record) {
  if (!confirm(`${record.student_name} - ${record.date} davomatini o'chirmoqchimisiz?`)) return

  try {
    await api.request(`/attendance/${record.id}`, { method: 'DELETE' })
    toast.success('Davomat o\'chirildi')
    await loadAttendance()
  } catch (e) {
    console.error('Delete error:', e)
    toast.error('O\'chirishda xatolik')
  }
}

function exportToExcel() {
  // Simple CSV export
  const headers = ['Talaba', 'Sana', 'Fan', 'Para', 'Holat', 'Kechikish (daq)', 'Izoh', 'Sabab']
  const rows = filteredRecords.value.map(r => [
    r.student_name || '',
    r.date || '',
    r.subject || '',
    r.lesson_number || '',
    getStatusText(r.status),
    r.late_minutes || 0,
    r.note || '',
    r.excuse_reason || ''
  ])

  const csv = [headers.join(','), ...rows.map(r => r.map(c => `"${c}"`).join(','))].join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `davomat_${filters.dateFrom || 'all'}.csv`
  link.click()
}

// Init
onMounted(async () => {
  await loadGroups()
  await loadAttendance()
})
</script>
