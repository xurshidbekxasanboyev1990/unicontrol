<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Hisobotlar</h1>
        <p class="text-sm text-slate-500">Fakultet statistikasi va tahlillari</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="selectedPeriod" class="flex-1 sm:flex-none px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-500 outline-none">
          <option value="week">Bu hafta</option>
          <option value="month">Bu oy</option>
          <option value="semester">Semestr</option>
          <option value="year">O'quv yili</option>
        </select>
        <button 
          @click="exportReport"
          class="px-4 py-2 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2"
        >
          <Download class="w-4 h-4" />
          <span class="hidden sm:inline">Eksport</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-emerald-600">{{ overallAttendance }}%</p>
            <p class="text-sm text-slate-500 mt-1">Umumiy davomat</p>
          </div>
          <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <TrendingUp class="w-6 h-6 text-emerald-600" />
          </div>
        </div>
        <div class="mt-3 flex items-center gap-1 text-sm">
          <ArrowUp class="w-4 h-4 text-emerald-500" />
          <span class="text-emerald-600 font-medium">+2.5%</span>
          <span class="text-slate-400">o'tgan oyga nisbatan</span>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-blue-600">{{ totalLessons }}</p>
            <p class="text-sm text-slate-500 mt-1">Jami darslar</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <BookOpen class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-violet-600">{{ excellentStudents }}</p>
            <p class="text-sm text-slate-500 mt-1">A'lochi talabalar</p>
          </div>
          <div class="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center">
            <Award class="w-6 h-6 text-violet-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-rose-600">{{ lowAttendanceCount }}</p>
            <p class="text-sm text-slate-500 mt-1">Ogohlantirish</p>
          </div>
          <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <AlertTriangle class="w-6 h-6 text-rose-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Weekly Trend -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-6">Haftalik trend</h2>
        <div class="flex items-end gap-3 h-48">
          <div 
            v-for="(day, index) in weeklyData" 
            :key="index"
            class="flex-1 flex flex-col items-center gap-2"
          >
            <div class="w-full bg-slate-100 rounded-t-lg relative" style="height: 160px;">
              <div 
                class="absolute bottom-0 w-full rounded-t-lg transition-all duration-500"
                :class="day.rate >= 85 ? 'bg-gradient-to-t from-emerald-500 to-emerald-400' : day.rate >= 70 ? 'bg-gradient-to-t from-amber-500 to-amber-400' : 'bg-gradient-to-t from-rose-500 to-rose-400'"
                :style="{ height: day.rate + '%' }"
              ></div>
            </div>
            <span class="text-xs font-medium text-slate-600">{{ day.name }}</span>
            <span class="text-xs text-slate-400">{{ day.rate }}%</span>
          </div>
        </div>
      </div>

      <!-- Group Comparison -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Guruhlar taqqoslash</h2>
        <div class="space-y-4">
          <div v-for="group in groupStats" :key="group.name">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-slate-700">{{ group.name }}</span>
              <div class="flex items-center gap-3">
                <span class="text-sm text-slate-500">{{ group.students }} talaba</span>
                <span 
                  class="font-semibold"
                  :class="group.rate >= 85 ? 'text-emerald-600' : group.rate >= 70 ? 'text-amber-600' : 'text-rose-600'"
                >
                  {{ group.rate }}%
                </span>
              </div>
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
    </div>

    <!-- Detailed Table -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800">Batafsil ma'lumotlar</h2>
        <div class="flex items-center gap-2">
          <button 
            @click="activeTab = 'groups'"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="activeTab === 'groups' ? 'bg-violet-100 text-violet-700' : 'text-slate-500 hover:bg-slate-100'"
          >
            Guruhlar
          </button>
          <button 
            @click="activeTab = 'students'"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="activeTab === 'students' ? 'bg-violet-100 text-violet-700' : 'text-slate-500 hover:bg-slate-100'"
          >
            Talabalar
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <template v-if="activeTab === 'groups'">
                <th class="text-left p-4 font-semibold text-slate-600">Guruh</th>
                <th class="text-left p-4 font-semibold text-slate-600">Talabalar</th>
                <th class="text-left p-4 font-semibold text-slate-600">Kelgan</th>
                <th class="text-left p-4 font-semibold text-slate-600">Kelmagan</th>
                <th class="text-left p-4 font-semibold text-slate-600">Davomat</th>
              </template>
              <template v-else>
                <th class="text-left p-4 font-semibold text-slate-600">Talaba</th>
                <th class="text-left p-4 font-semibold text-slate-600">Guruh</th>
                <th class="text-left p-4 font-semibold text-slate-600">Kelgan</th>
                <th class="text-left p-4 font-semibold text-slate-600">Kelmagan</th>
                <th class="text-left p-4 font-semibold text-slate-600">Davomat</th>
              </template>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <template v-if="activeTab === 'groups'">
              <tr v-for="group in groupStats" :key="group.name" class="hover:bg-slate-50">
                <td class="p-4 font-medium text-slate-800">{{ group.name }}</td>
                <td class="p-4 text-slate-600">{{ group.students }}</td>
                <td class="p-4 text-emerald-600">{{ group.present }}</td>
                <td class="p-4 text-rose-600">{{ group.absent }}</td>
                <td class="p-4">
                  <span 
                    class="px-3 py-1 rounded-lg text-sm font-semibold"
                    :class="group.rate >= 85 ? 'bg-emerald-100 text-emerald-700' : group.rate >= 70 ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'"
                  >
                    {{ group.rate }}%
                  </span>
                </td>
              </tr>
            </template>
            <template v-else>
              <tr v-for="student in studentStats" :key="student.id" class="hover:bg-slate-50">
                <td class="p-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                      {{ student.name.charAt(0) }}
                    </div>
                    <span class="font-medium text-slate-800">{{ student.name }}</span>
                  </div>
                </td>
                <td class="p-4 text-slate-600">{{ student.group }}</td>
                <td class="p-4 text-emerald-600">{{ student.present }}</td>
                <td class="p-4 text-rose-600">{{ student.absent }}</td>
                <td class="p-4">
                  <span 
                    class="px-3 py-1 rounded-lg text-sm font-semibold"
                    :class="student.rate >= 85 ? 'bg-emerald-100 text-emerald-700' : student.rate >= 70 ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'"
                  >
                    {{ student.rate }}%
                  </span>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../../stores/data'
import {
  Download,
  TrendingUp,
  ArrowUp,
  BookOpen,
  Award,
  AlertTriangle
} from 'lucide-vue-next'

const dataStore = useDataStore()
const selectedPeriod = ref('month')
const activeTab = ref('groups')

const overallAttendance = computed(() => {
  const records = dataStore.attendanceRecords
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 0
})

const totalLessons = computed(() => {
  return dataStore.schedule.length * 4
})

const excellentStudents = computed(() => {
  return dataStore.students.filter(s => {
    const records = dataStore.attendanceRecords.filter(r => r.studentId === s.id)
    const total = records.length
    const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = total > 0 ? Math.round((attended / total) * 100) : 100
    return rate >= 90
  }).length
})

const lowAttendanceCount = computed(() => {
  return dataStore.students.filter(s => {
    const records = dataStore.attendanceRecords.filter(r => r.studentId === s.id)
    const total = records.length
    const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = total > 0 ? Math.round((attended / total) * 100) : 100
    return rate < 70
  }).length
})

const weeklyData = computed(() => {
  const days = ['Du', 'Se', 'Cho', 'Pa', 'Ju', 'Sha', 'Ya']
  return days.map((name, index) => ({
    name,
    rate: Math.floor(Math.random() * 25) + 75
  }))
})

const groupStats = computed(() => {
  return dataStore.groups.map(group => {
    const groupStudents = dataStore.students.filter(s => s.group === group.name)
    const studentIds = groupStudents.map(s => s.id)
    const records = dataStore.attendanceRecords.filter(r => studentIds.includes(r.studentId))
    const total = records.length
    const present = records.filter(r => r.status === 'present' || r.status === 'late').length
    const absent = records.filter(r => r.status === 'absent').length
    const rate = total > 0 ? Math.round((present / total) * 100) : 0
    
    return {
      name: group.name,
      students: groupStudents.length,
      present,
      absent,
      rate
    }
  }).sort((a, b) => b.rate - a.rate)
})

const studentStats = computed(() => {
  return dataStore.students.map(student => {
    const records = dataStore.attendanceRecords.filter(r => r.studentId === student.id)
    const total = records.length
    const present = records.filter(r => r.status === 'present' || r.status === 'late').length
    const absent = records.filter(r => r.status === 'absent').length
    const rate = total > 0 ? Math.round((present / total) * 100) : 100
    
    return {
      ...student,
      present,
      absent,
      rate
    }
  }).sort((a, b) => b.rate - a.rate)
})

const exportReport = () => {
  alert('Hisobot yuklanmoqda...')
}
</script>
