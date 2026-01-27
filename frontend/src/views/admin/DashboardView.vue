<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div class="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold">Admin boshqaruv paneli</h1>
          <p class="text-violet-100 mt-1">Fakultet boshqaruvi</p>
        </div>
        <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
          <Shield class="w-7 h-7" />
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
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
            <p class="text-3xl font-bold text-rose-600">{{ pendingContracts }}</p>
            <p class="text-sm text-slate-500 mt-1">To'lanmagan</p>
          </div>
          <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <CreditCard class="w-6 h-6 text-rose-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
    </div>
  </div>
</template>

<script setup>
import { computed, markRaw } from 'vue'
import { useDataStore } from '../../stores/data'
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
  UserCheck,
  FileText,
  AlertCircle
} from 'lucide-vue-next'

const dataStore = useDataStore()

const totalStudents = computed(() => dataStore.students.length)
const totalGroups = computed(() => dataStore.groups.length)

const avgAttendance = computed(() => {
  const records = dataStore.attendanceRecords
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 0
})

const pendingContracts = computed(() => {
  return dataStore.students.filter(s => !s.contractPaid).length
})

const paidCount = computed(() => dataStore.students.filter(s => s.contractPaid).length)
const unpaidCount = computed(() => dataStore.students.filter(s => !s.contractPaid).length)
const paidPercentage = computed(() => {
  const total = dataStore.students.length
  return total > 0 ? Math.round((paidCount.value / total) * 100) : 0
})

const groupAttendance = computed(() => {
  return dataStore.groups.map(group => {
    const groupStudents = dataStore.students.filter(s => s.group === group.name)
    const studentIds = groupStudents.map(s => s.id)
    const records = dataStore.attendanceRecords.filter(r => studentIds.includes(r.studentId))
    const total = records.length
    const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = total > 0 ? Math.round((attended / total) * 100) : 0
    
    return { name: group.name, rate }
  }).sort((a, b) => b.rate - a.rate)
})

const recentActivities = computed(() => [
  {
    id: 1,
    icon: markRaw(UserCheck),
    bgClass: 'bg-emerald-100',
    iconClass: 'text-emerald-600',
    title: 'Yangi talaba qo\'shildi',
    description: 'Ali Valiyev SE-401 guruhiga qo\'shildi',
    time: '5 daqiqa oldin'
  },
  {
    id: 2,
    icon: markRaw(FileText),
    bgClass: 'bg-blue-100',
    iconClass: 'text-blue-600',
    title: 'Hisobot yaratildi',
    description: 'Mart oyi uchun davomat hisoboti',
    time: '1 soat oldin'
  },
  {
    id: 3,
    icon: markRaw(AlertCircle),
    bgClass: 'bg-amber-100',
    iconClass: 'text-amber-600',
    title: 'Past davomat ogohlantirishi',
    description: '3 ta talabaning davomati 70% dan past',
    time: '2 soat oldin'
  }
])
</script>
