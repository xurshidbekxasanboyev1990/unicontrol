<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Kontrakt ma'lumotlari</h1>
        <p class="text-sm text-slate-500">
          <span v-if="loading">Yuklanmoqda...</span>
          <span v-else>{{ totalItems }} ta kontrakt</span>
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4 space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Search -->
        <div class="relative lg:col-span-2">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Talaba ismi yoki ID..."
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm"
            @input="debouncedSearch"
          />
          <Loader2 v-if="loading" class="w-5 h-5 text-emerald-500 absolute right-3 top-1/2 -translate-y-1/2 animate-spin" />
        </div>

        <!-- Faculty (Yo'nalish - from groups) -->
        <select v-model="filterFaculty" @change="onFacultyChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha yo'nalishlar</option>
          <option v-for="f in filterOptions.faculties" :key="f" :value="f">{{ f }}</option>
        </select>

        <!-- Debt filter -->
        <select v-model="filterDebt" @change="onFilterChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barchasi</option>
          <option value="true">Qarzdorlar</option>
          <option value="false">To'laganlar</option>
        </select>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Course -->
        <select v-model="filterCourse" @change="onFilterChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha kurslar</option>
          <option v-for="c in filterOptions.courses" :key="c" :value="c">{{ c }}</option>
        </select>

        <!-- Education form -->
        <select v-model="filterEducationForm" @change="onFilterChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha ta'lim shakllari</option>
          <option v-for="ef in filterOptions.education_forms" :key="ef" :value="ef">{{ ef }}</option>
        </select>

        <!-- Group -->
        <select v-model="filterGroupId" @change="onFilterChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm lg:col-span-2">
          <option value="">Barcha guruhlar</option>
          <option v-for="group in filteredGroups" :key="group.id" :value="group.id">{{ group.name }} ({{ group.students_count }})</option>
        </select>
      </div>

      <!-- Active filters -->
      <div v-if="hasActiveFilters" class="flex items-center gap-2 flex-wrap">
        <span class="text-xs text-slate-500">Filtrlar:</span>
        <span v-if="filterFaculty" class="inline-flex items-center gap-1 px-2 py-1 bg-teal-100 text-teal-700 rounded-lg text-xs">
          {{ filterFaculty }}
          <button @click="filterFaculty = ''; onFacultyChange()" class="hover:text-teal-900"><X class="w-3 h-3" /></button>
        </span>
        <span v-if="filterCourse" class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs">
          {{ filterCourse }}
          <button @click="filterCourse = ''; onFilterChange()" class="hover:text-blue-900"><X class="w-3 h-3" /></button>
        </span>
        <span v-if="filterEducationForm" class="inline-flex items-center gap-1 px-2 py-1 bg-violet-100 text-violet-700 rounded-lg text-xs">
          {{ filterEducationForm }}
          <button @click="filterEducationForm = ''; onFilterChange()" class="hover:text-violet-900"><X class="w-3 h-3" /></button>
        </span>
        <span v-if="filterGroupId" class="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-lg text-xs">
          {{ selectedGroupName }}
          <button @click="filterGroupId = ''; onFilterChange()" class="hover:text-amber-900"><X class="w-3 h-3" /></button>
        </span>
        <span v-if="filterDebt" class="inline-flex items-center gap-1 px-2 py-1 bg-rose-100 text-rose-700 rounded-lg text-xs">
          {{ filterDebt === 'true' ? 'Qarzdorlar' : "To'laganlar" }}
          <button @click="filterDebt = ''; onFilterChange()" class="hover:text-rose-900"><X class="w-3 h-3" /></button>
        </span>
        <button @click="clearAllFilters" class="text-xs text-rose-500 hover:text-rose-700 underline ml-2">Tozalash</button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200/60 p-5">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
            <FileSpreadsheet class="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ contractStats.total }}</p>
            <p class="text-xs text-slate-500">Jami kontraktlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200/60 p-5">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
            <CheckCircle class="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-emerald-600">{{ contractStats.paid }}</p>
            <p class="text-xs text-slate-500">To'langan</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200/60 p-5">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-rose-100 flex items-center justify-center">
            <AlertCircle class="w-6 h-6 text-rose-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-rose-600">{{ contractStats.unpaid }}</p>
            <p class="text-xs text-slate-500">Qarzdor</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200/60 p-5">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
            <Banknote class="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p class="text-lg font-bold text-blue-600">{{ contractStats.payment_percentage || 0 }}%</p>
            <p class="text-xs text-slate-500">To'lov foizi</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading && contracts.length === 0" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- Contracts Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[900px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">#</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Talaba</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Guruh</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Kurs</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Ta'lim shakli</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Kontrakt</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">To'langan</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Qarz</th>
              <th class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Holat</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(contract, idx) in contracts" :key="contract.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-3 sm:p-4 text-sm text-slate-500">{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-sm">
                    {{ (contract.student_name || 'T').charAt(0) }}
                  </div>
                  <span class="font-medium text-slate-800">{{ contract.student_name }}</span>
                </div>
              </td>
              <td class="p-4">
                <span class="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-sm">{{ contract.group_name || '—' }}</span>
              </td>
              <td class="p-4 text-sm text-slate-600">{{ contract.course || '—' }}</td>
              <td class="p-4 text-sm text-slate-600">{{ contract.education_form || '—' }}</td>
              <td class="p-4 text-right text-sm font-medium text-slate-800">{{ formatMoney(contract.contract_amount) }}</td>
              <td class="p-4 text-right text-sm font-medium text-emerald-600">{{ formatMoney(contract.paid_amount) }}</td>
              <td class="p-4 text-right text-sm font-medium text-rose-600">{{ formatMoney(contract.debt) }}</td>
              <td class="p-4 text-center">
                <span
                  class="px-3 py-1 rounded-lg text-xs font-medium"
                  :class="contract.is_paid ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
                >
                  {{ contract.is_paid ? "To'langan" : "Qarzdor" }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="contracts.length === 0" class="p-12 text-center">
        <FileSpreadsheet class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Kontrakt ma'lumotlari topilmadi</p>
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
  </div>
</template>

<script setup>
import { AlertCircle, Banknote, CheckCircle, ChevronLeft, ChevronRight, FileSpreadsheet, Loader2, Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const contracts = ref([])
const allGroups = ref([])
const filterOptions = ref({ faculties: [], directions: [], education_forms: [], courses: [], academic_years: [] })
const searchQuery = ref('')
const filterFaculty = ref('')
const filterCourse = ref('')
const filterEducationForm = ref('')
const filterGroupId = ref('')
const filterDebt = ref('')
const currentPage = ref(1)
const pageSize = 30
const totalItems = ref(0)
const contractStats = ref({ total: 0, paid: 0, unpaid: 0, payment_percentage: 0 })

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// Filter groups by selected faculty
const filteredGroups = computed(() => {
  let g = allGroups.value
  if (filterFaculty.value) {
    g = g.filter(gr => gr.faculty === filterFaculty.value)
  }
  return g
})

const selectedGroupName = computed(() => {
  if (!filterGroupId.value) return ''
  const g = allGroups.value.find(gr => gr.id === Number(filterGroupId.value))
  return g ? g.name : ''
})

const hasActiveFilters = computed(() => {
  return filterFaculty.value || filterCourse.value || filterEducationForm.value || filterGroupId.value || filterDebt.value
})

const formatMoney = (val) => {
  if (!val && val !== 0) return '—'
  return Number(val).toLocaleString('uz-UZ') + ' so\'m'
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadContracts()
  }, 400)
}

const onFacultyChange = () => {
  filterGroupId.value = ''
  currentPage.value = 1
  loadContracts()
}

const onFilterChange = () => {
  currentPage.value = 1
  loadContracts()
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filterFaculty.value = ''
  filterCourse.value = ''
  filterEducationForm.value = ''
  filterGroupId.value = ''
  filterDebt.value = ''
  currentPage.value = 1
  loadContracts()
}

const loadContracts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('per_page', pageSize)
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterGroupId.value) params.append('group_id', filterGroupId.value)
    if (filterFaculty.value) params.append('faculty', filterFaculty.value)
    if (filterCourse.value) params.append('course', filterCourse.value)
    if (filterEducationForm.value) params.append('education_form', filterEducationForm.value)
    if (filterDebt.value) params.append('has_debt', filterDebt.value)
    const resp = await api.get(`/dean/contracts?${params}`)
    contracts.value = resp.items || []
    totalItems.value = resp.total || 0
    if (resp.stats) contractStats.value = resp.stats
  } catch (err) {
    console.error('Dean contracts error:', err)
  } finally {
    loading.value = false
  }
}

const loadFilterOptions = async () => {
  try {
    const resp = await api.get('/dean/contracts/filters')
    filterOptions.value = resp || { faculties: [], directions: [], education_forms: [], courses: [], academic_years: [] }
  } catch (err) {
    console.error('Dean contracts filters error:', err)
  }
}

const loadGroups = async () => {
  try {
    const resp = await api.get('/dean/groups')
    allGroups.value = resp.items || []
  } catch (err) {
    console.error('Dean groups error:', err)
  }
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadContracts()
}

onMounted(() => {
  loadContracts()
  loadFilterOptions()
  loadGroups()
})
</script>
