<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Kontrakt ma'lumotlari</h1>
        <p class="text-sm text-slate-500">Talabalar kontrakt holati (faqat ko'rish)</p>
      </div>
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div class="relative">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Talaba qidirish..."
            class="w-full sm:w-64 pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
            @input="debouncedSearch"
          />
        </div>
        <select v-model="filterGroup" @change="loadContracts" class="px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none">
          <option value="">Barcha guruhlar</option>
          <option v-for="group in groups" :key="group.id" :value="group.name">{{ group.name }}</option>
        </select>
        <select v-model="filterDebt" @change="loadContracts" class="px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none">
          <option value="">Barchasi</option>
          <option value="true">Qarzdorlar</option>
          <option value="false">To'laganlar</option>
        </select>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
            <p class="text-xs text-slate-500">To'lanmagan</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- Contracts Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[800px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Talaba</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Guruh</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Kontrakt summasi</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">To'langan</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Qarz</th>
              <th class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Holat</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="contract in contracts" :key="contract.id" class="hover:bg-slate-50 transition-colors">
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
              <td class="p-4 text-right text-sm font-medium text-slate-800">{{ formatMoney(contract.amount) }}</td>
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
import { AlertCircle, CheckCircle, ChevronLeft, ChevronRight, FileSpreadsheet, Loader2, Search } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const contracts = ref([])
const groups = ref([])
const searchQuery = ref('')
const filterGroup = ref('')
const filterDebt = ref('')
const currentPage = ref(1)
const pageSize = 30
const totalItems = ref(0)
const contractStats = ref({ total: 0, paid: 0, unpaid: 0 })

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
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

const loadContracts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('page_size', pageSize)
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterGroup.value) params.append('group', filterGroup.value)
    if (filterDebt.value) params.append('has_debt', filterDebt.value)
    const resp = await api.get(`/dean/contracts?${params}`)
    contracts.value = resp.contracts || resp.items || []
    totalItems.value = resp.total || 0
    if (resp.stats) contractStats.value = resp.stats
  } catch (err) {
    console.error('Dean contracts error:', err)
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
  loadContracts()
}

onMounted(() => {
  loadContracts()
  loadGroups()
})
</script>
