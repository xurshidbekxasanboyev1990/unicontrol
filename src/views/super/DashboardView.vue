<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div class="bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold">Super Admin Panel</h1>
          <p class="text-amber-100 mt-1">Tizim boshqaruvi va monitoring</p>
        </div>
        <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
          <Crown class="w-7 h-7" />
        </div>
      </div>
    </div>

    <!-- System Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-slate-800">{{ totalStudents }}</p>
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
            <p class="text-3xl font-bold text-violet-600">{{ totalGroups }}</p>
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
      <div class="divide-y divide-slate-100">
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
  </div>
</template>

<script setup>
import { computed, markRaw } from 'vue'
import { useDataStore } from '../../stores/data'
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
  Trash
} from 'lucide-vue-next'

const dataStore = useDataStore()

const totalStudents = computed(() => dataStore.students.length)
const totalGroups = computed(() => dataStore.groups.length)
const totalAdmins = 3
const systemHealth = 95
const totalRecords = computed(() => dataStore.attendanceRecords.length)
const totalNotifications = computed(() => dataStore.notifications.length)

const recentLogs = computed(() => [
  {
    id: 1,
    icon: markRaw(UserPlus),
    bgClass: 'bg-emerald-100',
    iconClass: 'text-emerald-600',
    action: 'Yangi talaba qo\'shildi',
    user: 'Admin',
    time: '2 daqiqa oldin'
  },
  {
    id: 2,
    icon: markRaw(LogIn),
    bgClass: 'bg-blue-100',
    iconClass: 'text-blue-600',
    action: 'Tizimga kirish',
    user: 'Super Admin',
    time: '15 daqiqa oldin'
  },
  {
    id: 3,
    icon: markRaw(FileEdit),
    bgClass: 'bg-amber-100',
    iconClass: 'text-amber-600',
    action: 'Guruh ma\'lumoti yangilandi',
    user: 'Admin',
    time: '1 soat oldin'
  },
  {
    id: 4,
    icon: markRaw(Trash),
    bgClass: 'bg-rose-100',
    iconClass: 'text-rose-600',
    action: 'Bildirishnoma o\'chirildi',
    user: 'Admin',
    time: '2 soat oldin'
  }
])
</script>
