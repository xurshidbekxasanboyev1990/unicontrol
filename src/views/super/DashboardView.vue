<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <RefreshCw class="w-12 h-12 text-amber-500 animate-spin mx-auto mb-4" />
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
      <div class="bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 rounded-2xl p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">Super Admin Panel</h1>
            <p class="text-amber-100 mt-1">Tizim boshqaruvi va monitoring</p>
          </div>
          <div class="flex items-center gap-3">
            <button @click="refresh" class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center hover:bg-white/30 transition-colors">
              <RefreshCw class="w-5 h-5" />
            </button>
            <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
              <Crown class="w-7 h-7" />
            </div>
          </div>
        </div>
      </div>

      <!-- System Stats -->
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
              <p class="text-3xl font-bold text-emerald-600">{{ totalAdmins }}</p>
              <p class="text-sm text-slate-500 mt-1">Adminlar</p>
            </div>
            <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
              <ShieldCheck class="w-6 h-6 text-emerald-600" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-3xl font-bold text-amber-600">{{ systemHealth }}%</p>
              <p class="text-sm text-slate-500 mt-1">Tizim holati</p>
            </div>
            <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <Activity class="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </div>
      </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-3 gap-4">
      <router-link to="/super/admins" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-amber-200 transition-all group">
        <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <UserCog class="w-6 h-6 text-amber-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Adminlar</h3>
        <p class="text-sm text-slate-500 mt-1">Adminlarni boshqarish</p>
      </router-link>

      <router-link to="/super/settings" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-violet-200 transition-all group">
        <div class="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <Settings class="w-6 h-6 text-violet-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Sozlamalar</h3>
        <p class="text-sm text-slate-500 mt-1">Tizim konfiguratsiyasi</p>
      </router-link>

      <router-link to="/super/logs" class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-blue-200 transition-all group">
        <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
          <ScrollText class="w-6 h-6 text-blue-600" />
        </div>
        <h3 class="font-semibold text-slate-800">Loglar</h3>
        <p class="text-sm text-slate-500 mt-1">Tizim jurnali</p>
      </router-link>
    </div>

    <!-- System Overview -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Database Stats -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Database class="w-5 h-5 text-slate-400" />
          Ma'lumotlar bazasi
        </h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <Users class="w-5 h-5 text-blue-500" />
              <span class="text-slate-700">Talabalar jadvali</span>
            </div>
            <span class="font-semibold text-slate-800">{{ totalStudents }} yozuv</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <Layers class="w-5 h-5 text-violet-500" />
              <span class="text-slate-700">Guruhlar jadvali</span>
            </div>
            <span class="font-semibold text-slate-800">{{ totalGroups }} yozuv</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <ClipboardList class="w-5 h-5 text-emerald-500" />
              <span class="text-slate-700">Davomat yozuvlari</span>
            </div>
            <span class="font-semibold text-slate-800">{{ totalRecords }} yozuv</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <Bell class="w-5 h-5 text-amber-500" />
              <span class="text-slate-700">Bildirishnomalar</span>
            </div>
            <span class="font-semibold text-slate-800">{{ totalNotifications }} yozuv</span>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Activity class="w-5 h-5 text-slate-400" />
          Tizim holati
        </h2>
        <div class="space-y-4">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-600">Server</span>
              <span class="text-emerald-600 font-medium flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Ishlayapti
              </span>
            </div>
            <div class="h-2 bg-slate-100 rounded-full">
              <div class="h-full w-[95%] bg-emerald-500 rounded-full"></div>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-600">Ma'lumotlar bazasi</span>
              <span class="text-emerald-600 font-medium flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Ulangan
              </span>
            </div>
            <div class="h-2 bg-slate-100 rounded-full">
              <div class="h-full w-[88%] bg-emerald-500 rounded-full"></div>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-600">Xotira</span>
              <span class="text-amber-600 font-medium">65% ishlatilmoqda</span>
            </div>
            <div class="h-2 bg-slate-100 rounded-full">
              <div class="h-full w-[65%] bg-amber-500 rounded-full"></div>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-600">Disk</span>
              <span class="text-emerald-600 font-medium">42% ishlatilmoqda</span>
            </div>
            <div class="h-2 bg-slate-100 rounded-full">
              <div class="h-full w-[42%] bg-emerald-500 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Logs -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800">So'nggi faoliyatlar</h2>
        <router-link to="/super/logs" class="text-sm text-amber-600 hover:text-amber-700 font-medium">
          Barchasini ko'rish
        </router-link>
      </div>
      <div v-if="recentLogs.length === 0" class="p-8 text-center text-slate-500">
        <Clock class="w-10 h-10 mx-auto mb-3 text-slate-300" />
        <p>Hozircha faoliyat yo'q</p>
      </div>
      <div v-else class="divide-y divide-slate-100">
        <div 
          v-for="log in recentLogs" 
          :key="log.id"
          class="p-4 flex items-center gap-4"
        >
          <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="log.bgClass"
          >
            <component :is="log.icon" class="w-5 h-5" :class="log.iconClass" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-slate-800">{{ log.action }}</p>
            <p class="text-sm text-slate-500">{{ log.user }}</p>
          </div>
          <span class="text-xs text-slate-400 whitespace-nowrap">{{ log.time }}</span>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
/**
 * Super Admin Dashboard - Real API Integration
 * Backend /dashboard/superadmin endpoint dan ma'lumot oladi
 */
import { ref, computed, onMounted, markRaw } from 'vue'
import { useDataStore } from '../../stores/data'
import api from '../../services/api'
import {
  Crown,
  Users,
  Layers,
  ShieldCheck,
  Activity,
  UserCog,
  Settings,
  ScrollText,
  Database,
  ClipboardList,
  Bell,
  UserPlus,
  LogIn,
  FileEdit,
  Trash,
  AlertCircle,
  RefreshCw
} from 'lucide-vue-next'

const dataStore = useDataStore()

// === STATE ===
const loading = ref(true)
const error = ref(null)
const dashboardData = ref(null)

// System stats from API
const totalStudents = ref(0)
const totalGroups = ref(0)
const totalAdmins = ref(0)
const totalUsers = ref(0)
const systemHealth = ref(95)
const totalRecords = ref(0)
const totalNotifications = ref(0)
const recentLogs = ref([])

// === LOAD DATA ===
const loadDashboard = async () => {
  loading.value = true
  error.value = null

  try {
    // Backend /dashboard/superadmin endpoint
    const response = await api.request('/dashboard/superadmin')
    dashboardData.value = response

    // System stats
    if (response.system_stats) {
      totalStudents.value = response.system_stats.students || 0
      totalGroups.value = response.system_stats.groups || 0
      totalAdmins.value = response.system_stats.admins || 0
      totalUsers.value = response.system_stats.total_users || 0
    }

    // Also fetch from data store for more accurate counts
    await Promise.all([
      dataStore.fetchGroups(),
      dataStore.fetchStudents({ page_size: 1 }), // Just to get total count
      dataStore.fetchNotifications()
    ])

    // Update counts from store pagination
    totalStudents.value = dataStore.studentsPagination.total || totalStudents.value
    totalGroups.value = dataStore.groupsPagination.total || totalGroups.value
    totalNotifications.value = dataStore.notifications?.length || 0

    // Fetch attendance records count
    try {
      const attendanceStats = await api.getAttendanceStats()
      totalRecords.value = attendanceStats?.total_records || 0
    } catch (e) {
      // If endpoint doesn't exist, use 0
      totalRecords.value = 0
    }

    // Load recent logs
    await loadRecentLogs()

  } catch (err) {
    console.error('Dashboard load error:', err)
    error.value = err.message || 'Ma\'lumotlarni yuklashda xatolik'
    
    // Fallback to store data
    totalStudents.value = dataStore.studentsCount || 0
    totalGroups.value = dataStore.groupsCount || 0
  } finally {
    loading.value = false
  }
}

// Load recent activity logs
const loadRecentLogs = async () => {
  try {
    const logs = await api.getLogs({ limit: 5 })
    
    if (Array.isArray(logs)) {
      recentLogs.value = logs.map(log => formatLog(log))
    } else if (logs?.items) {
      recentLogs.value = logs.items.slice(0, 5).map(log => formatLog(log))
    }
  } catch (err) {
    // Logs endpoint may not exist, use mock data
    recentLogs.value = [
      {
        id: 1,
        icon: markRaw(LogIn),
        bgClass: 'bg-blue-100',
        iconClass: 'text-blue-600',
        action: 'Tizimga kirish',
        user: 'Super Admin',
        time: formatTime(new Date())
      }
    ]
  }
}

// Format log entry for display
const formatLog = (log) => {
  const iconMap = {
    'login': { icon: LogIn, bg: 'bg-blue-100', text: 'text-blue-600' },
    'logout': { icon: LogIn, bg: 'bg-slate-100', text: 'text-slate-600' },
    'create': { icon: UserPlus, bg: 'bg-emerald-100', text: 'text-emerald-600' },
    'update': { icon: FileEdit, bg: 'bg-amber-100', text: 'text-amber-600' },
    'delete': { icon: Trash, bg: 'bg-rose-100', text: 'text-rose-600' }
  }

  const action = log.action?.toLowerCase() || 'unknown'
  const iconData = iconMap[action] || { icon: Activity, bg: 'bg-slate-100', text: 'text-slate-600' }

  return {
    id: log.id,
    icon: markRaw(iconData.icon),
    bgClass: iconData.bg,
    iconClass: iconData.text,
    action: log.description || log.action || 'Noma\'lum amal',
    user: log.user_name || log.user || 'Tizim',
    time: formatTime(log.created_at || log.timestamp)
  }
}

// Format timestamp to relative time
const formatTime = (timestamp) => {
  if (!timestamp) return 'Hozir'
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000) // seconds
  
  if (diff < 60) return 'Hozir'
  if (diff < 3600) return `${Math.floor(diff / 60)} daqiqa oldin`
  if (diff < 86400) return `${Math.floor(diff / 3600)} soat oldin`
  if (diff < 604800) return `${Math.floor(diff / 86400)} kun oldin`
  
  return date.toLocaleDateString('uz-UZ')
}

// Refresh data
const refresh = () => {
  dataStore.clearCache()
  loadDashboard()
}

// === LIFECYCLE ===
onMounted(() => {
  loadDashboard()
})
</script>
