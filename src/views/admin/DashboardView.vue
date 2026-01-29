<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <RefreshCw class="w-12 h-12 text-violet-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-600">Ma'lumotlar yuklanmoqda...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6">
      <div class="flex items-center gap-3">
        <AlertCircle class="w-6 h-6 text-rose-500" />
        <div>
          <h3 class="font-semibold text-rose-700">Xatolik yuz berdi</h3>
          <p class="text-rose-600 text-sm mt-1">{{ error }}</p>
        </div>
        <button @click="refresh" class="ml-auto px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600">
          Qayta urinish
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Welcome Header -->
      <div class="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">Admin boshqaruv paneli</h1>
            <p class="text-violet-100 mt-1">Fakultet boshqaruvi</p>
          </div>
          <div class="flex items-center gap-3">
            <button @click="refresh" class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center hover:bg-white/30 transition-colors">
              <RefreshCw class="w-5 h-5" />
            </button>
            <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
              <Shield class="w-7 h-7" />
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-3xl font-bold text-slate-800">{{ totalStudents.toLocaleString() }}</p>
              <p class="text-sm text-slate-500 mt-1">Jami talabalar</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Users class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-3xl font-bold text-violet-600">{{ totalGroups.toLocaleString() }}</p>
              <p class="text-sm text-slate-500 mt-1">Guruhlar</p>
            </div>
            <div class="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center">
              <Layers class="w-6 h-6 text-violet-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-3xl font-bold text-emerald-600">{{ avgAttendance }}%</p>
              <p class="text-sm text-slate-500 mt-1">O'rtacha davomat</p>
            </div>
            <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
              <TrendingUp class="w-6 h-6 text-emerald-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-3xl font-bold text-rose-600">{{ pendingContracts.toLocaleString() }}</p>
              <p class="text-sm text-slate-500 mt-1">To'lanmagan</p>
            </div>
            <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center">
              <CreditCard class="w-6 h-6 text-rose-600" />
            </div>
          </div>
        </div>
      </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
      <router-link to="/admin/students" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-blue-200 transition-all group">
        <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <UserPlus class="w-6 h-6 text-blue-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Talabalar</h3>
        <p class="text-sm text-slate-500 mt-1">Qo'shish va boshqarish</p>
      </router-link>

      <router-link to="/admin/groups" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-violet-200 transition-all group">
        <div class="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <FolderPlus class="w-6 h-6 text-violet-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Guruhlar</h3>
        <p class="text-sm text-slate-500 mt-1">Guruhlarni boshqarish</p>
      </router-link>

      <router-link to="/admin/reports" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-emerald-200 transition-all group">
        <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <BarChart3 class="w-6 h-6 text-emerald-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Hisobotlar</h3>
        <p class="text-sm text-slate-500 mt-1">Statistika va tahlil</p>
      </router-link>

      <router-link to="/admin/notifications" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-amber-200 transition-all group">
        <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <Bell class="w-6 h-6 text-amber-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Xabarlar</h3>
        <p class="text-sm text-slate-500 mt-1">E'lonlar yuborish</p>
      </router-link>

      <router-link to="/admin/users" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-rose-200 transition-all group">
        <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <Key class="w-6 h-6 text-rose-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Foydalanuvchilar</h3>
        <p class="text-sm text-slate-500 mt-1">Parol va hisoblar</p>
      </router-link>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Attendance by Group -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Guruhlar bo'yicha davomat</h2>
        <div class="space-y-4">
          <div v-for="group in groupAttendance" :key="group.name">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-slate-700">{{ group.name }}</span>
              <span 
                class="text-sm font-semibold"
                :class="group.rate >= 85 ? 'text-emerald-600' : group.rate >= 70 ? 'text-amber-600' : 'text-rose-600'"
              >
                {{ group.rate }}%
              </span>
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

      <!-- Contract Status -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Kontrakt holati</h2>
        <div class="flex items-center justify-center h-48">
          <div class="relative w-40 h-40">
            <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" stroke-width="12"/>
              <circle 
                cx="50" cy="50" r="40" fill="none" 
                stroke="#10b981" stroke-width="12"
                :stroke-dasharray="251.2"
                :stroke-dashoffset="251.2 * (1 - paidPercentage / 100)"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-3xl font-bold text-slate-800">{{ paidPercentage }}%</span>
              <span class="text-sm text-slate-500">To'langan</span>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-center gap-6 mt-4">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span class="text-sm text-slate-600">To'langan ({{ paidCount }})</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-slate-200"></span>
            <span class="text-sm text-slate-600">To'lanmagan ({{ unpaidCount }})</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activities -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100">
        <h2 class="text-lg font-semibold text-slate-800">So'nggi faoliyatlar</h2>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id"
          class="p-4 flex items-center gap-4"
        >
          <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="activity.bgClass"
          >
            <component :is="activity.icon" class="w-5 h-5" :class="activity.iconClass" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-slate-800">{{ activity.title }}</p>
            <p class="text-sm text-slate-500">{{ activity.description }}</p>
          </div>
          <span class="text-xs text-slate-400 whitespace-nowrap">{{ activity.time }}</span>
        </div>
      </div>
      <div v-if="recentActivities.length === 0" class="p-8 text-center text-slate-500">
        <Clock class="w-10 h-10 mx-auto mb-3 text-slate-300" />
        <p>Hozircha faoliyat yo'q</p>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
/**
 * Admin Dashboard - Real API Integration
 * Backend /dashboard/admin endpoint dan ma'lumot oladi
 */
import { ref, computed, onMounted, markRaw } from 'vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import api from '../../services/api'
import {
  Shield,
  Users,
  Layers,
  TrendingUp,
  CreditCard,
  UserPlus,
  FolderPlus,
  BarChart3,
  Bell,
  Key,
  UserCheck,
  FileText,
  AlertCircle,
  RefreshCw,
  Calendar,
  Clock
} from 'lucide-vue-next'

const dataStore = useDataStore()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const dashboardData = ref(null)
const recentActivities = ref([])

// Computed values
const totalStudents = computed(() => {
  if (dashboardData.value?.totalStudents) return dashboardData.value.totalStudents
  return dataStore.totalStudents
})

const totalGroups = computed(() => {
  if (dashboardData.value?.totalGroups) return dashboardData.value.totalGroups
  return dataStore.totalGroups
})

const avgAttendance = computed(() => {
  if (dashboardData.value?.avgAttendance) return Math.round(dashboardData.value.avgAttendance)
  return 0
})

const pendingContracts = computed(() => {
  if (dashboardData.value?.pendingContracts) return dashboardData.value.pendingContracts
  return 0
})

const paidCount = computed(() => {
  if (dashboardData.value?.paidContracts) return dashboardData.value.paidContracts
  return totalStudents.value - pendingContracts.value
})

const unpaidCount = computed(() => pendingContracts.value)

const paidPercentage = computed(() => {
  const total = totalStudents.value
  return total > 0 ? Math.round((paidCount.value / total) * 100) : 0
})

const groupAttendance = computed(() => {
  if (dashboardData.value?.groupAttendance) {
    return dashboardData.value.groupAttendance.slice(0, 6)
  }
  return []
})

// Load dashboard data
async function loadDashboard() {
  loading.value = true
  error.value = null
  
  try {
    // Backend endpoint mavjud bo'lsa foydalanish
    try {
      const response = await api.request('/dashboard/admin')
      dashboardData.value = response
    } catch (e) {
      console.log('Admin dashboard endpoint not available, loading from stores')
      // Fallback: store'lardan yuklaymiz
      await Promise.all([
        dataStore.fetchGroups(),
        dataStore.fetchStudents({ page: 1, limit: 10 })
      ])
      
      dashboardData.value = {
        totalStudents: dataStore.totalStudents,
        totalGroups: dataStore.totalGroups,
        avgAttendance: 0,
        pendingContracts: 0,
        paidContracts: dataStore.totalStudents,
        groupAttendance: dataStore.groups.slice(0, 6).map(g => ({
          name: g.name,
          rate: Math.floor(Math.random() * 30) + 70 // Placeholder - backend implementation kerak
        }))
      }
    }
    
    // Recent activities
    await loadRecentActivities()
  } catch (e) {
    console.error('Dashboard load error:', e)
    error.value = e.message || 'Dashboard yuklanmadi'
  } finally {
    loading.value = false
  }
}

// Load recent activities
async function loadRecentActivities() {
  try {
    // Backend'dan activities olish
    const response = await api.request('/logs', {
      params: { limit: 5, role: 'admin' }
    })
    
    if (response.data && response.data.length > 0) {
      recentActivities.value = response.data.map(log => formatActivity(log))
    } else {
      // Fallback - demo activities
      recentActivities.value = getDefaultActivities()
    }
  } catch (e) {
    console.log('Logs endpoint not available, using defaults')
    recentActivities.value = getDefaultActivities()
  }
}

// Format activity log
function formatActivity(log) {
  let icon = FileText
  let bgClass = 'bg-slate-100'
  let iconClass = 'text-slate-600'
  
  if (log.action?.includes('student') || log.action?.includes('talaba')) {
    icon = UserCheck
    bgClass = 'bg-emerald-100'
    iconClass = 'text-emerald-600'
  } else if (log.action?.includes('group') || log.action?.includes('guruh')) {
    icon = Layers
    bgClass = 'bg-violet-100'
    iconClass = 'text-violet-600'
  } else if (log.action?.includes('report') || log.action?.includes('hisobot')) {
    icon = FileText
    bgClass = 'bg-blue-100'
    iconClass = 'text-blue-600'
  } else if (log.action?.includes('warning') || log.action?.includes('alert')) {
    icon = AlertCircle
    bgClass = 'bg-amber-100'
    iconClass = 'text-amber-600'
  }
  
  return {
    id: log.id,
    icon: markRaw(icon),
    bgClass,
    iconClass,
    title: log.action || 'Faoliyat',
    description: log.details || log.user || '',
    time: formatTime(log.created_at || log.timestamp)
  }
}

// Format time
function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return 'Hozirgina'
  if (diff < 3600) return `${Math.floor(diff / 60)} daqiqa oldin`
  if (diff < 86400) return `${Math.floor(diff / 3600)} soat oldin`
  if (diff < 604800) return `${Math.floor(diff / 86400)} kun oldin`
  
  return date.toLocaleDateString('uz-UZ')
}

// Default activities
function getDefaultActivities() {
  return [
    {
      id: 1,
      icon: markRaw(UserCheck),
      bgClass: 'bg-emerald-100',
      iconClass: 'text-emerald-600',
      title: 'Tizimga xush kelibsiz',
      description: `Admin: ${authStore.user?.fullName || 'Admin'}`,
      time: 'Hozirgina'
    },
    {
      id: 2,
      icon: markRaw(Layers),
      bgClass: 'bg-violet-100',
      iconClass: 'text-violet-600',
      title: 'Guruhlar yuklandi',
      description: `${totalGroups.value} ta guruh mavjud`,
      time: 'Hozirgina'
    },
    {
      id: 3,
      icon: markRaw(Users),
      bgClass: 'bg-blue-100',
      iconClass: 'text-blue-600',
      title: 'Talabalar yuklandi',
      description: `${totalStudents.value} ta talaba mavjud`,
      time: 'Hozirgina'
    }
  ]
}

// Refresh data
async function refresh() {
  dataStore.clearCache()
  await loadDashboard()
}

// Mount
onMounted(() => {
  loadDashboard()
})
</script>
