<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Guruh kontrakt ma'lumotlari</h1>
        <p class="text-sm text-slate-500">
          {{ groupName }} guruhi
          <span v-if="totalContracts"> · {{ totalContracts }} ta talaba</span>
        </p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">Talabalar</p>
        <p class="text-lg font-bold text-slate-800">{{ stats.total_contracts }}</p>
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
        <p class="text-xs text-slate-500 mb-1">Grant</p>
        <p class="text-lg font-bold text-purple-600">{{ formatMoney(stats.total_grant_amount) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">To'lov %</p>
        <p class="text-lg font-bold text-amber-600">{{ stats.payment_percentage?.toFixed(1) }}%</p>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="stats" class="grid grid-cols-3 gap-2 sm:gap-3">
      <div class="rounded-xl border border-emerald-100 bg-emerald-50 p-2 sm:p-3 text-center">
        <p class="text-lg sm:text-2xl font-bold text-emerald-700">{{ stats.fully_paid_count }}</p>
        <p class="text-[10px] sm:text-xs text-emerald-600">To'liq to'langan</p>
      </div>
      <div class="rounded-xl border border-red-100 bg-red-50 p-2 sm:p-3 text-center">
        <p class="text-lg sm:text-2xl font-bold text-red-700">{{ stats.with_debt_count }}</p>
        <p class="text-[10px] sm:text-xs text-red-600">Qarzdorlar</p>
      </div>
      <div class="rounded-xl border border-blue-100 bg-blue-50 p-2 sm:p-3 text-center">
        <p class="text-lg sm:text-2xl font-bold text-blue-700">{{ stats.studying_count }}</p>
        <p class="text-[10px] sm:text-xs text-blue-600">O'qimoqda</p>
      </div>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
      <input 
        v-model="searchQuery"
        type="text"
        placeholder="Talaba qidirish..."
        class="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
        @input="onSearchInput"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading && !contracts.length" class="flex items-center justify-center py-16">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
      <span class="ml-3 text-slate-600">Yuklanmoqda...</span>
    </div>

    <!-- Students Cards -->
    <div v-else-if="contracts.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div 
        v-for="c in contracts" 
        :key="c.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start gap-4 mb-4">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-lg font-bold flex-shrink-0">
            {{ c.student_name?.charAt(0) || '?' }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-slate-800 truncate">{{ c.student_name }}</h3>
            <p class="text-xs text-slate-500">{{ c.course || '' }} · {{ c.education_form || '' }}</p>
          </div>
          <span 
            class="px-2 py-0.5 rounded-lg text-xs font-medium flex-shrink-0"
            :class="Number(c.debt_amount) < 0 ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'"
          >
            {{ Number(c.debt_amount) < 0 ? 'Qarzdor' : 'To\'langan' }}
          </span>
        </div>

        <!-- Finance info -->
        <div class="grid grid-cols-2 gap-3 mb-3">
          <div class="p-3 bg-slate-50 rounded-xl">
            <p class="text-xs text-slate-500">Kontrakt</p>
            <p class="text-sm font-bold text-slate-800">{{ formatMoney(c.contract_amount) }}</p>
          </div>
          <div class="p-3 bg-emerald-50 rounded-xl">
            <p class="text-xs text-slate-500">To'langan</p>
            <p class="text-sm font-bold text-emerald-600">{{ formatMoney(c.total_paid) }}</p>
          </div>
          <div class="p-3 bg-rose-50 rounded-xl">
            <p class="text-xs text-slate-500">Qarz</p>
            <p class="text-sm font-bold text-rose-600">{{ formatMoney(Math.abs(Number(c.debt_amount) || 0)) }}</p>
          </div>
          <div class="p-3 bg-purple-50 rounded-xl">
            <p class="text-xs text-slate-500">Grant</p>
            <p class="text-sm font-bold text-purple-600">{{ Number(c.grant_amount) > 0 ? formatMoney(c.grant_amount) : '—' }}</p>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
          <div 
            class="h-full rounded-full transition-all duration-500"
            :class="(c.payment_percentage || 0) >= 1 ? 'bg-emerald-500' : (c.payment_percentage || 0) >= 0.5 ? 'bg-amber-500' : 'bg-red-500'"
            :style="{ width: Math.min((c.payment_percentage || 0) * 100, 100) + '%' }"
          ></div>
        </div>
        <p class="text-xs text-right text-slate-500 mt-1">{{ ((c.payment_percentage || 0) * 100).toFixed(0) }}% to'langan</p>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <FileSpreadsheet :size="48" class="mx-auto mb-4 text-slate-300" />
      <p class="text-slate-500">Guruh uchun kontrakt ma'lumotlari topilmadi</p>
    </div>
  </div>
</template>

<script setup>
import { FileSpreadsheet, Loader2, Search } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const contracts = ref([])
const totalContracts = ref(0)
const stats = ref(null)
const loading = ref(false)
const searchQuery = ref('')
const groupName = ref('')
const groupId = ref(null)

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => loadData(), 400)
}

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

const loadData = async () => {
  if (!groupId.value) return
  loading.value = true
  try {
    const params = { academic_year: '2025-2026', page_size: 200 }
    if (searchQuery.value) params.search = searchQuery.value
    const res = await api.getGroupContracts(groupId.value, params)
    contracts.value = res.items || []
    totalContracts.value = res.total || 0
    stats.value = res.stats || null
  } catch (e) { console.error('Error loading group contracts:', e) }
  finally { loading.value = false }
}

onMounted(async () => {
  // Get leader's group
  try {
    const me = await api.getMe()
    groupId.value = me.group_id
    groupName.value = me.group_name || 'Guruh'
    if (groupId.value) {
      await loadData()
    }
  } catch (e) {
    console.error('Error getting user info:', e)
  }
})
</script>
