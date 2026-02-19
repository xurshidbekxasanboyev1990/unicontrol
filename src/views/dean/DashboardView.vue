<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Dekanat paneli</h1>
        <p class="text-sm text-slate-500 mt-1">Talabalar, davomat, jadval va kontrakt ma'lumotlari</p>
      </div>
      <button @click="loadStats" class="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-500/25 transition-all text-sm font-medium">
        <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        Yangilash
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
            <Users class="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ stats.total_students }}</p>
            <p class="text-xs text-slate-500">Jami talabalar</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
            <Building2 class="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ stats.total_groups }}</p>
            <p class="text-xs text-slate-500">Jami guruhlar</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-teal-100 flex items-center justify-center">
            <ClipboardCheck class="w-6 h-6 text-teal-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-emerald-600">{{ stats.attendance_rate }}%</p>
            <p class="text-xs text-slate-500">Davomat foizi</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-rose-100 flex items-center justify-center">
            <CreditCard class="w-6 h-6 text-rose-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-rose-600">{{ stats.unpaid_contracts }}</p>
            <p class="text-xs text-slate-500">To'lanmagan kontrakt</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Second Row Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
            <Calendar class="w-6 h-6 text-violet-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ stats.total_lessons }}</p>
            <p class="text-xs text-slate-500">Bugungi darslar</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
            <FileCheck class="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-amber-600">{{ stats.active_nb_permits }}</p>
            <p class="text-xs text-slate-500">Faol NB ruxsatnomalar</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
            <FileSpreadsheet class="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ stats.total_contracts }}</p>
            <p class="text-xs text-slate-500">Jami kontraktlar</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Attendance Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-2xl border border-slate-200/60 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">Bugungi davomat</h3>
        <div class="flex items-center gap-6">
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-slate-600">Kelganlar</span>
              <span class="text-sm font-semibold text-emerald-600">{{ stats.today_present }}</span>
            </div>
            <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-emerald-500 rounded-full transition-all" :style="{ width: attendanceRate + '%' }"></div>
            </div>
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-slate-600">Kelmaganlar</span>
              <span class="text-sm font-semibold text-rose-600">{{ stats.today_absent }}</span>
            </div>
            <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-rose-500 rounded-full transition-all" :style="{ width: (100 - attendanceRate) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200/60 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">Kontrakt statistikasi</h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600">Jami kontraktlar</span>
            <span class="text-sm font-bold text-slate-800">{{ stats.total_contracts }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600">To'langan</span>
            <span class="text-sm font-bold text-emerald-600">{{ stats.paid_contracts }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600">To'lanmagan</span>
            <span class="text-sm font-bold text-rose-600">{{ stats.unpaid_contracts }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-2xl border border-slate-200/60 p-6">
      <h3 class="text-lg font-semibold text-slate-800 mb-4">Tezkor harakatlar</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <button @click="$router.push('/dean/students')" class="flex items-center gap-3 p-4 bg-slate-50 hover:bg-emerald-50 rounded-xl border border-slate-200 hover:border-emerald-200 transition-all group">
          <Users class="w-5 h-5 text-slate-400 group-hover:text-emerald-500" />
          <span class="text-sm font-medium text-slate-700 group-hover:text-emerald-700">Talabalar kontingenti</span>
        </button>
        <button @click="$router.push('/dean/attendance')" class="flex items-center gap-3 p-4 bg-slate-50 hover:bg-emerald-50 rounded-xl border border-slate-200 hover:border-emerald-200 transition-all group">
          <ClipboardCheck class="w-5 h-5 text-slate-400 group-hover:text-emerald-500" />
          <span class="text-sm font-medium text-slate-700 group-hover:text-emerald-700">Davomat ko'rish</span>
        </button>
        <button @click="$router.push('/dean/schedule')" class="flex items-center gap-3 p-4 bg-slate-50 hover:bg-emerald-50 rounded-xl border border-slate-200 hover:border-emerald-200 transition-all group">
          <Calendar class="w-5 h-5 text-slate-400 group-hover:text-emerald-500" />
          <span class="text-sm font-medium text-slate-700 group-hover:text-emerald-700">Dars jadvali</span>
        </button>
        <button @click="$router.push('/dean/contracts')" class="flex items-center gap-3 p-4 bg-slate-50 hover:bg-emerald-50 rounded-xl border border-slate-200 hover:border-emerald-200 transition-all group">
          <FileSpreadsheet class="w-5 h-5 text-slate-400 group-hover:text-emerald-500" />
          <span class="text-sm font-medium text-slate-700 group-hover:text-emerald-700">Kontrakt ma'lumotlari</span>
        </button>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  </div>
</template>

<script setup>
import { Building2, Calendar, ClipboardCheck, CreditCard, FileCheck, FileSpreadsheet, RefreshCw, Users } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const stats = ref({
  total_students: 0,
  total_groups: 0,
  attendance_rate: 0,
  today_present: 0,
  today_absent: 0,
  total_lessons: 0,
  active_nb_permits: 0,
  total_nb_permits: 0,
  total_contracts: 0,
  paid_contracts: 0,
  unpaid_contracts: 0
})

const attendanceRate = computed(() => {
  const total = stats.value.today_present + stats.value.today_absent
  if (total === 0) return 0
  return Math.round((stats.value.today_present / total) * 100)
})

const loadStats = async () => {
  loading.value = true
  try {
    const resp = await api.get('/dean/dashboard')
    stats.value = {
      total_students: resp.total_students || 0,
      total_groups: resp.total_groups || 0,
      attendance_rate: resp.attendance_rate || 0,
      today_present: resp.today_present || 0,
      today_absent: resp.today_absent || 0,
      total_lessons: resp.today_lessons || 0,
      active_nb_permits: resp.nb_stats?.active || 0,
      total_nb_permits: resp.nb_stats?.total || 0,
      total_contracts: resp.contract_stats?.total || 0,
      paid_contracts: resp.contract_stats?.paid || 0,
      unpaid_contracts: resp.contract_stats?.debt || 0
    }
  } catch (err) {
    console.error('Dean dashboard error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>
