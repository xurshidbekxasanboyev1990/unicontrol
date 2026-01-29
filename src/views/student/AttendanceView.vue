<template>
  <div class="space-y-6">
    <!-- Stats Overview -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.total }}</p>
            <p class="text-sm text-slate-500 mt-1">Jami darslar</p>
          </div>
          <div class="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
            <CalendarDays class="w-6 h-6 text-slate-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-emerald-600">{{ stats.present }}</p>
            <p class="text-sm text-slate-500 mt-1">Qatnashgan</p>
          </div>
          <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <CheckCircle class="w-6 h-6 text-emerald-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-amber-600">{{ stats.late }}</p>
            <p class="text-sm text-slate-500 mt-1">Kechikkan</p>
          </div>
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <Clock class="w-6 h-6 text-amber-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-rose-600">{{ stats.absent }}</p>
            <p class="text-sm text-slate-500 mt-1">Kelmagan</p>
          </div>
          <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <XCircle class="w-6 h-6 text-rose-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Attendance Rate -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-slate-800">Davomat foizi</h2>
          <p class="text-sm text-slate-500">Umumiy ko'rsatkich</p>
        </div>
        <div 
          class="text-4xl font-bold"
          :class="stats.rate >= 85 ? 'text-emerald-500' : stats.rate >= 70 ? 'text-amber-500' : 'text-rose-500'"
        >
          {{ stats.rate }}%
        </div>
      </div>
      
      <div class="h-4 bg-slate-100 rounded-full overflow-hidden">
        <div 
          class="h-full rounded-full transition-all duration-500"
          :class="stats.rate >= 85 ? 'bg-emerald-500' : stats.rate >= 70 ? 'bg-amber-500' : 'bg-rose-500'"
          :style="{ width: stats.rate + '%' }"
        ></div>
      </div>

      <div class="flex items-center justify-between mt-4 text-sm">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
          <span class="text-slate-600">85%+ — A'lo</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-amber-500"></span>
          <span class="text-slate-600">70-84% — Yaxshi</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-rose-500"></span>
          <span class="text-slate-600">&lt;70% — Yomon</span>
        </div>
      </div>
    </div>

    <!-- Recent Records -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100">
        <h2 class="text-lg font-semibold text-slate-800">So'nggi davomat yozuvlari</h2>
      </div>
      
      <div class="divide-y divide-slate-100">
        <div
          v-for="record in recentRecords"
          :key="record.id"
          class="p-4 flex items-center gap-4"
        >
          <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="getStatusBgClass(record.status)"
          >
            <component :is="getStatusIcon(record.status)" class="w-5 h-5" :class="getStatusTextClass(record.status)" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-slate-800">{{ record.subject }}</p>
            <p class="text-sm text-slate-500">{{ formatDate(record.date) }}</p>
          </div>
          <span 
            class="px-3 py-1 rounded-lg text-sm font-medium"
            :class="getStatusBadgeClass(record.status)"
          >
            {{ getStatusText(record.status) }}
          </span>
        </div>
      </div>

      <div v-if="recentRecords.length === 0" class="p-12 text-center">
        <ClipboardList class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Davomat yozuvlari topilmadi</p>
      </div>
    </div>

    <!-- By Subject -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <h2 class="text-lg font-semibold text-slate-800 mb-4">Fanlar bo'yicha davomat</h2>
      
      <div class="space-y-4">
        <div v-for="subject in subjectStats" :key="subject.name">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-slate-700">{{ subject.name }}</span>
            <span 
              class="text-sm font-semibold"
              :class="subject.rate >= 85 ? 'text-emerald-600' : subject.rate >= 70 ? 'text-amber-600' : 'text-rose-600'"
            >
              {{ subject.rate }}%
            </span>
          </div>
          <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-500"
              :class="subject.rate >= 85 ? 'bg-emerald-500' : subject.rate >= 70 ? 'bg-amber-500' : 'bg-rose-500'"
              :style="{ width: subject.rate + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import api from '../../services/api'
import {
  CalendarDays,
  CheckCircle,
  Clock,
  XCircle,
  ClipboardList,
  FileText
} from 'lucide-vue-next'

const authStore = useAuthStore()
const toast = useToastStore()

const loading = ref(false)
const error = ref(null)
const records = ref([])

// Load attendance on mount
onMounted(async () => {
  await loadAttendance()
})

async function loadAttendance() {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.getStudentAttendance(authStore.user?.studentId || authStore.user?.id)
    
    if (Array.isArray(response)) {
      records.value = response.map(r => ({
        id: r.id,
        studentId: r.student_id,
        date: r.date,
        subject: r.subject || 'Fan',
        status: r.status || 'present'
      }))
    } else if (response?.data) {
      records.value = response.data.map(r => ({
        id: r.id,
        studentId: r.student_id,
        date: r.date,
        subject: r.subject || 'Fan',
        status: r.status || 'present'
      }))
    }
  } catch (err) {
    console.error('Load attendance error:', err)
    error.value = err.message || 'Davomat yuklanmadi'
    toast.error('Davomat yuklanmadi')
  } finally {
    loading.value = false
  }
}

const recentRecords = computed(() => {
  return [...records.value]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 10)
})

const stats = computed(() => {
  const total = records.value.length
  const present = records.value.filter(r => r.status === 'present').length
  const late = records.value.filter(r => r.status === 'late').length
  const absent = records.value.filter(r => r.status === 'absent').length
  const rate = total > 0 ? Math.round(((present + late) / total) * 100) : 0

  return { total, present, late, absent, rate }
})

const subjectStats = computed(() => {
  const subjects = [...new Set(records.value.map(r => r.subject))]
  
  return subjects.map(subject => {
    const subjectRecords = records.value.filter(r => r.subject === subject)
    const total = subjectRecords.length
    const attended = subjectRecords.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = total > 0 ? Math.round((attended / total) * 100) : 0
    
    return { name: subject, total, attended, rate }
  }).sort((a, b) => b.rate - a.rate)
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const getStatusIcon = (status) => {
  const icons = {
    present: markRaw(CheckCircle),
    late: markRaw(Clock),
    absent: markRaw(XCircle),
    excused: markRaw(FileText)
  }
  return icons[status] || markRaw(CheckCircle)
}

const getStatusBgClass = (status) => {
  const classes = {
    present: 'bg-emerald-100',
    late: 'bg-amber-100',
    absent: 'bg-rose-100',
    excused: 'bg-blue-100'
  }
  return classes[status] || 'bg-slate-100'
}

const getStatusTextClass = (status) => {
  const classes = {
    present: 'text-emerald-600',
    late: 'text-amber-600',
    absent: 'text-rose-600',
    excused: 'text-blue-600'
  }
  return classes[status] || 'text-slate-600'
}

const getStatusBadgeClass = (status) => {
  const classes = {
    present: 'bg-emerald-100 text-emerald-700',
    late: 'bg-amber-100 text-amber-700',
    absent: 'bg-rose-100 text-rose-700',
    excused: 'bg-blue-100 text-blue-700'
  }
  return classes[status] || 'bg-slate-100 text-slate-700'
}

const getStatusText = (status) => {
  const texts = {
    present: 'Kelgan',
    late: 'Kechikkan',
    absent: 'Kelmagan',
    excused: 'Sababli'
  }
  return texts[status] || status
}
</script>
