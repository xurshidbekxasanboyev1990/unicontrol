<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Davomat</h1>
        <p class="text-sm text-slate-500">Talabalar davomati (faqat ko'rish)</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="exportAttendance"
          :disabled="exporting"
          class="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all text-sm font-medium disabled:opacity-50"
        >
          <FileSpreadsheet class="w-4 h-4" />
          {{ exporting ? 'Yuklanmoqda...' : 'Excel export' }}
        </button>
        <button
          @click="showImportModal = true"
          class="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-500/25 transition-all text-sm font-medium"
        >
          <Upload class="w-4 h-4" />
          Excel import
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Sanadan</label>
          <input
            v-model="filterDateFrom"
            type="date"
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm"
            @change="loadAttendance"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Sanagacha</label>
          <input
            v-model="filterDateTo"
            type="date"
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm"
            @change="loadAttendance"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Guruh</label>
          <select v-model="filterGroup" @change="loadAttendance" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
            <option value="">Barcha guruhlar</option>
            <option v-for="group in groups" :key="group.id" :value="group.name">{{ group.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Holat</label>
          <select v-model="filterStatus" @change="loadAttendance" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
            <option value="">Barcha holatlar</option>
            <option value="present">Kelgan</option>
            <option value="absent">Kelmagan</option>
            <option value="late">Kechikkan</option>
            <option value="excused">Sababli</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- Attendance Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Talaba</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Guruh</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Sana</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Fan</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Holat</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="record in attendance" :key="record.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-xs">
                    {{ (record.student_name || 'T').charAt(0) }}
                  </div>
                  <span class="font-medium text-slate-800">{{ record.student_name }}</span>
                </div>
              </td>
              <td class="p-4">
                <span class="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-sm">{{ record.group_name || '—' }}</span>
              </td>
              <td class="p-4 text-slate-600 text-sm">{{ record.date }}</td>
              <td class="p-4 text-slate-600 text-sm">{{ record.subject || '—' }}</td>
              <td class="p-4">
                <span
                  class="px-3 py-1 rounded-lg text-xs font-medium"
                  :class="statusClass(record.status)"
                >
                  {{ statusLabel(record.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="attendance.length === 0" class="p-12 text-center">
        <ClipboardCheck class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Davomat ma'lumotlari topilmadi</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="p-3 sm:p-4 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div class="text-sm text-slate-500">
          {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalItems) }} / {{ totalItems }}
        </div>
        <div class="flex items-center gap-2">
          <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed">
            <ChevronLeft class="w-5 h-5" />
          </button>
          <template v-for="page in visiblePages" :key="page">
            <button @click="goToPage(page)" class="w-10 h-10 rounded-lg font-medium transition-colors" :class="currentPage === page ? 'bg-emerald-500 text-white' : 'hover:bg-slate-100'">{{ page }}</button>
          </template>
          <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed">
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <Transition enter-active-class="transition-all duration-300" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition-all duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="showImportModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="showImportModal = false">
        <div class="bg-white rounded-2xl w-full max-w-lg p-6 shadow-2xl">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-slate-800">Davomatni Excel'dan import qilish</h2>
            <button @click="showImportModal = false" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- File Upload Area -->
          <div
            class="border-2 border-dashed rounded-2xl p-8 text-center transition-colors"
            :class="isDragging ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200 hover:border-emerald-300'"
            @dragenter.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <Upload class="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p class="text-slate-600 mb-2">Excel faylni bu yerga tashlang</p>
            <p class="text-slate-400 text-sm mb-4">yoki</p>
            <label class="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors cursor-pointer text-sm font-medium">
              <FileUp class="w-4 h-4" />
              Fayl tanlash
              <input type="file" accept=".xlsx,.xls" class="hidden" @change="handleFileSelect" />
            </label>
          </div>

          <!-- Selected File -->
          <div v-if="importFile" class="mt-4 flex items-center gap-3 p-3 bg-emerald-50 rounded-xl border border-emerald-200">
            <FileSpreadsheet class="w-5 h-5 text-emerald-600" />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-800 truncate">{{ importFile.name }}</p>
              <p class="text-xs text-slate-500">{{ (importFile.size / 1024).toFixed(1) }} KB</p>
            </div>
            <button @click="importFile = null" class="p-1 text-slate-400 hover:text-rose-500">
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Import Hints -->
          <div class="mt-4 p-4 bg-slate-50 rounded-xl">
            <h4 class="text-sm font-semibold text-slate-700 mb-2">Excel fayl formati:</h4>
            <ul class="text-xs text-slate-500 space-y-1">
              <li>• <strong>Talaba ismi</strong> (ism/familiya) ustuni bo'lishi kerak</li>
              <li>• <strong>Guruh</strong> ustuni (guruh nomi)</li>
              <li>• <strong>Sana</strong> ustuni (YYYY-MM-DD format)</li>
              <li>• <strong>Holat</strong> ustuni (kelgan/kelmagan/kechikkan/sababli)</li>
              <li>• Fan ustuni (ixtiyoriy)</li>
            </ul>
          </div>

          <!-- Import Result -->
          <div v-if="importResult" class="mt-4 p-4 rounded-xl" :class="importResult.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-rose-50 border border-rose-200'">
            <p class="text-sm font-medium" :class="importResult.success ? 'text-emerald-700' : 'text-rose-700'">{{ importResult.message }}</p>
            <div v-if="importResult.details" class="mt-2 text-xs space-y-1" :class="importResult.success ? 'text-emerald-600' : 'text-rose-600'">
              <p v-if="importResult.details.created">✅ {{ importResult.details.created }} ta yangi yozuv</p>
              <p v-if="importResult.details.updated">📝 {{ importResult.details.updated }} ta yangilangan</p>
              <p v-if="importResult.details.errors">⚠️ {{ importResult.details.errors }} ta xato</p>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-6 flex justify-end gap-3">
            <button @click="showImportModal = false" class="px-4 py-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors text-sm font-medium">
              Bekor qilish
            </button>
            <button
              @click="importAttendance"
              :disabled="!importFile || importing"
              class="flex items-center gap-2 px-4 py-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Loader2 v-if="importing" class="w-4 h-4 animate-spin" />
              <Upload v-else class="w-4 h-4" />
              {{ importing ? 'Import qilinmoqda...' : 'Import qilish' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight, ClipboardCheck, FileSpreadsheet, FileUp, Loader2, Upload, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const attendance = ref([])
const groups = ref([])
const filterDateFrom = ref(new Date().toISOString().split('T')[0])
const filterDateTo = ref(new Date().toISOString().split('T')[0])
const filterGroup = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = 50
const totalItems = ref(0)

// Import state
const showImportModal = ref(false)
const importFile = ref(null)
const importing = ref(false)
const isDragging = ref(false)
const importResult = ref(null)
const exporting = ref(false)

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const statusClass = (status) => {
  const classes = {
    present: 'bg-emerald-100 text-emerald-700',
    absent: 'bg-rose-100 text-rose-700',
    late: 'bg-amber-100 text-amber-700',
    excused: 'bg-blue-100 text-blue-700'
  }
  return classes[status] || 'bg-slate-100 text-slate-700'
}

const statusLabel = (status) => {
  const labels = {
    present: 'Kelgan',
    absent: 'Kelmagan',
    late: 'Kechikkan',
    excused: 'Sababli'
  }
  return labels[status] || status
}

const loadAttendance = async () => {
  loading.value = attendance.value.length === 0
  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('page_size', pageSize)
    if (filterDateFrom.value) params.append('date_from', filterDateFrom.value)
    if (filterDateTo.value) params.append('date_to', filterDateTo.value)
    if (filterGroup.value) params.append('group', filterGroup.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    const resp = await api.get(`/dean/attendance?${params}`)
    attendance.value = resp.records || resp.items || []
    totalItems.value = resp.total || 0
  } catch (err) {
    console.error('Dean attendance error:', err)
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  try {
    const resp = await api.get('/dean/groups')
    groups.value = resp.groups || resp || []
  } catch (err) {
    console.error('Dean groups error:', err)
  }
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadAttendance()
}

// File handling
const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    importFile.value = file
    importResult.value = null
  }
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    importFile.value = file
    importResult.value = null
  }
}

const importAttendance = async () => {
  if (!importFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    const resp = await api.request('/dean/attendance/import', {
      method: 'POST',
      body: formData,
      isFormData: true
    })
    importResult.value = {
      success: true,
      message: resp.message || 'Davomat muvaffaqiyatli import qilindi!',
      details: resp
    }
    // Reload attendance after import
    loadAttendance()
  } catch (err) {
    importResult.value = {
      success: false,
      message: err.data?.detail || err.message || 'Import qilishda xatolik yuz berdi'
    }
  } finally {
    importing.value = false
  }
}

const exportAttendance = async () => {
  exporting.value = true
  try {
    const params = new URLSearchParams()
    if (filterDateFrom.value) params.append('date_from', filterDateFrom.value)
    if (filterDateTo.value) params.append('date_to', filterDateTo.value)
    if (filterGroup.value) {
      // Resolve group_id from group name
      const grp = groups.value.find(g => g.name === filterGroup.value)
      if (grp) params.append('group_id', grp.id)
    }
    if (filterStatus.value) params.append('status_filter', filterStatus.value)

    const resp = await fetch(`${api.baseUrl}/dean/attendance/export?${params}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    })
    if (!resp.ok) throw new Error('Export xatolik')
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `davomat_${filterDateFrom.value || 'all'}_${filterDateTo.value || ''}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Export error:', err)
    alert('Excel export qilishda xatolik yuz berdi')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadAttendance()
  loadGroups()
})
</script>
