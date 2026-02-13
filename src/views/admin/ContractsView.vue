<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Kontrakt ma'lumotlari</h1>
        <p class="text-sm text-slate-500">
          Jami: {{ totalContracts }} ta kontrakt
          <span v-if="selectedYear"> · {{ selectedYear }} o'quv yili</span>
        </p>
      </div>
      <button 
        @click="exportToExcel"
        :disabled="exporting"
        class="px-4 py-2.5 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-colors flex items-center gap-2 disabled:opacity-50"
      >
        <Download class="w-5 h-5" />
        {{ exporting ? 'Yuklanmoqda...' : 'Excel export' }}
      </button>
    </div>

    <!-- Statistics Cards -->
    <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">Jami kontraktlar</p>
        <p class="text-lg font-bold text-slate-800">{{ formatNumber(stats.total_contracts) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">Kontrakt summasi</p>
        <p class="text-lg font-bold text-blue-600">{{ formatMoney(stats.total_contract_amount) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">To'langan</p>
        <p class="text-lg font-bold text-emerald-600">{{ formatMoney(stats.total_paid) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">Qarzdorlik</p>
        <p class="text-lg font-bold text-red-600">{{ formatMoney(Math.abs(stats.total_debt)) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">Grant summasi</p>
        <p class="text-lg font-bold text-purple-600">{{ formatMoney(stats.total_grant_amount) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">To'lov %</p>
        <p class="text-lg font-bold text-amber-600">{{ stats.payment_percentage?.toFixed(1) }}%</p>
      </div>
    </div>

    <!-- Summary row -->
    <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="rounded-xl border border-emerald-100 bg-emerald-50 p-3">
        <p class="text-xs text-emerald-600 mb-1">To'liq to'langan</p>
        <p class="text-lg font-bold text-emerald-700">{{ stats.fully_paid_count }}</p>
      </div>
      <div class="rounded-xl border border-red-100 bg-red-50 p-3">
        <p class="text-xs text-red-600 mb-1">Qarzdorlar</p>
        <p class="text-lg font-bold text-red-700">{{ stats.with_debt_count }}</p>
      </div>
      <div class="rounded-xl border border-blue-100 bg-blue-50 p-3">
        <p class="text-xs text-blue-600 mb-1">Kunduzgi</p>
        <p class="text-lg font-bold text-blue-700">{{ stats.kunduzgi_count }}</p>
      </div>
      <div class="rounded-xl border border-orange-100 bg-orange-50 p-3">
        <p class="text-xs text-orange-600 mb-1">O'qimoqda</p>
        <p class="text-lg font-bold text-orange-700">{{ stats.studying_count }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
          <Filter :size="20" class="text-blue-600" />
        </div>
        <h2 class="font-semibold text-slate-800">Filter va qidiruv</h2>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div class="relative lg:col-span-2">
          <Search class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Ism, JSHSHIR, passport..."
            class="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/20"
            @input="onSearchInput"
          />
        </div>
        <select v-model="selectedYear" class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-blue-400 focus:outline-none" @change="loadData">
          <option value="">Barcha yillar</option>
          <option v-for="year in filterOptions.academic_years" :key="year" :value="year">{{ year }}</option>
        </select>
        <select v-model="selectedGroup" class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-blue-400 focus:outline-none" @change="loadData">
          <option value="">Barcha guruhlar</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <select v-model="selectedDebtFilter" class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-blue-400 focus:outline-none" @change="loadData">
          <option value="">Barchasi</option>
          <option value="true">Qarzdorlar</option>
          <option value="false">Qarzsizlar</option>
        </select>
      </div>
      <div class="mt-3 flex items-center justify-end gap-2">
        <button @click="resetFilters" class="px-3 py-2 text-sm text-slate-600 hover:text-slate-800 rounded-lg hover:bg-slate-100">Tozalash</button>
        <span class="text-sm text-slate-400">{{ totalContracts }} ta natija</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading && !contracts.length" class="flex items-center justify-center py-16">
      <Loader2 class="w-8 h-8 text-blue-500 animate-spin" />
      <span class="ml-3 text-slate-600">Yuklanmoqda...</span>
    </div>

    <!-- Table -->
    <div v-else class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div class="border-b border-slate-100 bg-slate-50 p-4 flex items-center justify-between">
        <h3 class="font-semibold text-slate-700">Kontrakt ma'lumotlari</h3>
        <div v-if="loading" class="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 class="w-4 h-4 animate-spin" />
        </div>
      </div>

      <div v-if="contracts.length === 0 && !loading" class="p-12 text-center">
        <FileSpreadsheet :size="48" class="mx-auto mb-4 text-slate-300" />
        <p class="text-slate-500">Kontrakt ma'lumotlari topilmadi</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm min-w-[850px]">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">#</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">F.I.O</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">Guruh</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">Kurs</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">Yo'nalish</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">Kontrakt</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">To'langan</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">Qarz</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">Grant</th>
              <th class="text-center px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">To'lov %</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(c, idx) in contracts" 
              :key="c.id" 
              class="border-b border-slate-100 hover:bg-blue-50/30 transition-colors cursor-pointer"
              @click="openDetail(c)"
            >
              <td class="px-3 py-2.5 text-slate-500">{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
              <td class="px-3 py-2.5 font-medium text-slate-800 whitespace-nowrap">{{ c.student_name || '—' }}</td>
              <td class="px-3 py-2.5">
                <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium">{{ c.group_name || '—' }}</span>
              </td>
              <td class="px-3 py-2.5 text-slate-600">{{ c.course || '—' }}</td>
              <td class="px-3 py-2.5 text-slate-600 max-w-[200px] truncate">{{ c.direction || '—' }}</td>
              <td class="px-3 py-2.5 text-right font-medium text-slate-800 whitespace-nowrap">{{ formatMoney(c.contract_amount) }}</td>
              <td class="px-3 py-2.5 text-right font-medium text-emerald-600 whitespace-nowrap">{{ formatMoney(c.total_paid) }}</td>
              <td class="px-3 py-2.5 text-right font-medium whitespace-nowrap" :class="Number(c.debt_amount) < 0 ? 'text-red-600' : 'text-slate-500'">
                {{ formatMoney(c.debt_amount) }}
              </td>
              <td class="px-3 py-2.5 text-right text-purple-600 whitespace-nowrap">
                {{ Number(c.grant_amount) > 0 ? formatMoney(c.grant_amount) : '—' }}
              </td>
              <td class="px-3 py-2.5 text-center">
                <span 
                  class="px-2 py-0.5 rounded-lg text-xs font-medium"
                  :class="(c.payment_percentage || 0) >= 1 ? 'bg-emerald-100 text-emerald-700' : (c.payment_percentage || 0) >= 0.5 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'"
                >
                  {{ ((c.payment_percentage || 0) * 100).toFixed(0) }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="border-t border-slate-100 bg-slate-50 px-3 sm:px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <p class="text-sm text-slate-500">{{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, totalContracts) }} / {{ totalContracts }}</p>
        <div class="flex items-center gap-1 flex-wrap">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1" class="px-3 py-1.5 text-sm rounded-lg border border-slate-200 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed">←</button>
          <template v-for="p in visiblePages" :key="p">
            <button v-if="p !== '...'" @click="changePage(p)" class="px-3 py-1.5 text-sm rounded-lg border transition-colors" :class="p === currentPage ? 'bg-blue-500 text-white border-blue-500' : 'border-slate-200 hover:bg-white'">{{ p }}</button>
            <span v-else class="px-2 text-slate-400">...</span>
          </template>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages" class="px-3 py-1.5 text-sm rounded-lg border border-slate-200 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed">→</button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="showDetailModal && selectedContract" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-2 sm:p-4" @click.self="showDetailModal = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
        <div class="bg-blue-50 px-6 py-4 border-b border-blue-100 flex justify-between items-center">
          <div>
            <h3 class="text-lg font-bold text-blue-800">Kontrakt tafsilotlari</h3>
            <p class="text-sm text-blue-600">{{ selectedContract.student_name }}</p>
          </div>
          <button @click="showDetailModal = false" class="p-1 text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-4 sm:p-6 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div>
              <p class="text-xs text-slate-500 mb-1">F.I.O</p>
              <p class="font-medium text-slate-800">{{ selectedContract.student_name || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">JSHSHIR</p>
              <p class="font-mono text-sm text-slate-800">{{ selectedContract.student_jshshir || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Guruh</p>
              <p class="font-medium text-slate-800">{{ selectedContract.group_name || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">O'quv yili</p>
              <p class="font-medium text-slate-800">{{ selectedContract.academic_year }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Kurs</p>
              <p class="text-slate-800">{{ selectedContract.course || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Holat</p>
              <span class="px-2 py-0.5 rounded-lg text-xs font-medium" :class="getStatusClass(selectedContract.student_status)">
                {{ selectedContract.student_status || '—' }}
              </span>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Yo'nalish</p>
              <p class="text-slate-800">{{ selectedContract.direction || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Ta'lim shakli</p>
              <p class="text-slate-800">{{ selectedContract.education_form || '—' }}</p>
            </div>
          </div>
          
          <hr class="border-slate-100" />
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div>
              <p class="text-xs text-slate-500 mb-1">Kontrakt summasi</p>
              <p class="text-base sm:text-lg font-bold text-slate-800">{{ formatMoney(selectedContract.contract_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">To'langan summa</p>
              <p class="text-lg font-bold text-emerald-600">{{ formatMoney(selectedContract.total_paid) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Qarzdorlik</p>
              <p class="text-lg font-bold" :class="Number(selectedContract.debt_amount) < 0 ? 'text-red-600' : 'text-slate-600'">
                {{ formatMoney(selectedContract.debt_amount) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">To'lov foizi</p>
              <p class="text-lg font-bold text-amber-600">{{ ((selectedContract.payment_percentage || 0) * 100).toFixed(1) }}%</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Grant (foizda)</p>
              <p class="text-slate-800">{{ selectedContract.grant_percentage ? (selectedContract.grant_percentage * 100).toFixed(1) + '%' : '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Grant (summada)</p>
              <p class="text-purple-600 font-medium">{{ formatMoney(selectedContract.grant_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Qaytarilgan</p>
              <p class="text-slate-800">{{ formatMoney(selectedContract.refund_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Yil yakuniga qoldiq</p>
              <p class="font-medium" :class="Number(selectedContract.year_end_balance) < 0 ? 'text-red-600' : 'text-slate-800'">
                {{ formatMoney(selectedContract.year_end_balance) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Download, FileSpreadsheet, Filter, Loader2, Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const contracts = ref([])
const totalContracts = ref(0)
const totalPages = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const loading = ref(false)
const stats = ref(null)
const groups = ref([])

const searchQuery = ref('')
const selectedYear = ref('2025-2026')
const selectedGroup = ref('')
const selectedDebtFilter = ref('')
const filterOptions = ref({ academic_years: ['2025-2026'], education_forms: [], student_statuses: [] })

const showDetailModal = ref(false)
const selectedContract = ref(null)
const exporting = ref(false)

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { currentPage.value = 1; loadData() }, 400)
}

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  if (total <= 7) { for (let i = 1; i <= total; i++) pages.push(i) }
  else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadData()
}

const formatNumber = (n) => n == null ? '0' : Number(n).toLocaleString('uz-UZ')
const formatMoney = (amount) => {
  if (amount == null || amount === 0) return '0'
  const num = Number(amount)
  if (num === 0) return '0'
  const absNum = Math.abs(num)
  const sign = num < 0 ? '-' : ''
  if (absNum >= 1_000_000_000) return sign + (absNum / 1_000_000_000).toFixed(1) + ' mlrd'
  if (absNum >= 1_000_000) return sign + (absNum / 1_000_000).toFixed(1) + ' mln'
  if (absNum >= 1_000) return sign + (absNum / 1_000).toFixed(0) + ' ming'
  return num.toLocaleString('uz-UZ')
}

const getStatusClass = (status) => {
  if (!status) return 'bg-slate-100 text-slate-600'
  const s = status.toLowerCase()
  if (s.includes("o'qimoqda")) return 'bg-emerald-100 text-emerald-700'
  if (s.includes('akademik')) return 'bg-amber-100 text-amber-700'
  if (s.includes('chetlash')) return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-600'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    if (selectedDebtFilter.value) params.has_debt = selectedDebtFilter.value
    if (searchQuery.value) params.search = searchQuery.value
    const res = await api.getContracts(params)
    contracts.value = res.items || []
    totalContracts.value = res.total || 0
    totalPages.value = res.total_pages || 0
  } catch (e) { console.error('Error loading contracts:', e) }
  finally { loading.value = false }
}

const loadStats = async () => {
  try {
    const params = {}
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    stats.value = await api.getContractStatistics(params)
  } catch (e) { console.error('Error loading stats:', e) }
}

const loadFilters = async () => {
  try { filterOptions.value = await api.getContractFilters() } catch (e) { console.error(e) }
}

const loadGroups = async () => {
  try {
    const res = await api.getGroups({ page_size: 1000 })
    groups.value = (res.items || res || []).sort((a, b) => a.name.localeCompare(b.name))
  } catch (e) { console.error(e) }
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedYear.value = ''
  selectedGroup.value = ''
  selectedDebtFilter.value = ''
  currentPage.value = 1
  loadData()
  loadStats()
}

const openDetail = (contract) => {
  selectedContract.value = contract
  showDetailModal.value = true
}

const exportToExcel = async () => {
  exporting.value = true
  try {
    const params = {}
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    const blob = await api.exportContracts(params)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `kontrakt_malumotlari${selectedYear.value ? '_' + selectedYear.value : ''}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) { console.error('Export error:', e) }
  finally { exporting.value = false }
}

onMounted(async () => {
  await Promise.all([loadFilters(), loadGroups()])
  await Promise.all([loadData(), loadStats()])
})
</script>
