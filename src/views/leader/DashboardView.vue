<template>
  <div class="space-y-6">
    <!-- Birthday Card (agar ertaga tug'ilgan kun bo'lsa) -->
    <div 
      v-if="tomorrowBirthdays.length > 0"
      class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-6 text-white shadow-lg"
    >
      <div class="absolute -right-6 -top-6 h-32 w-32 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-white/10"></div>
      
      <div class="relative">
        <div class="flex items-center gap-3 mb-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
            <Cake :size="24" />
          </div>
          <div>
            <h3 class="text-lg font-bold">🎂 Ertangi tug'ilgan kun!</h3>
            <p class="text-sm text-white/80">{{ tomorrowDateFormatted }}</p>
          </div>
        </div>
        
        <div class="space-y-3">
          <div 
            v-for="student in tomorrowBirthdays" 
            :key="student.id"
            class="flex items-center gap-4 rounded-xl bg-white/10 p-4 backdrop-blur"
          >
            <div class="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20 text-2xl font-bold">
              {{ student.name.charAt(0) }}
            </div>
            <div class="flex-1">
              <p class="font-semibold text-lg">{{ student.name }}</p>
              <p class="text-sm text-white/80">
                {{ student.birthDate }} yilda tug'ilgan
              </p>
            </div>
            <div class="text-right">
              <p class="text-3xl font-bold">{{ calculateAge(student.birthDate) }}</p>
              <p class="text-xs text-white/70">yoshga to'ladi</p>
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex gap-3">
          <button class="flex items-center gap-2 rounded-xl bg-white/20 px-4 py-2 text-sm font-medium backdrop-blur transition-all hover:bg-white/30">
            <Gift :size="18" />
            Tabriklamoqchiman
          </button>
          <button class="flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-purple-600 transition-all hover:bg-white/90">
            <Send :size="18" />
            Xabar yuborish
          </button>
        </div>
      </div>
    </div>

    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 md:text-3xl">Dashboard</h1>
        <p class="text-slate-500">{{ currentGroup?.name }} - Bugungi holat</p>
      </div>
      
      <div class="flex items-center gap-3">
        <span class="text-sm text-slate-400">
          {{ new Date().toLocaleDateString('uz-UZ', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}
        </span>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Davomat foizi -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">Davomat foizi</p>
            <p class="mt-1 text-3xl font-bold text-slate-800">{{ attendanceRate }}%</p>
            <p class="mt-1 text-xs text-slate-400">Bu oy</p>
          </div>
          <div class="rounded-lg bg-green-100 p-2.5">
            <CheckCircle :size="24" class="text-green-600" />
          </div>
        </div>
      </div>

      <!-- Darslar -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">Darslar</p>
            <p class="mt-1 text-3xl font-bold text-slate-800">{{ todayLessons.length }}</p>
            <p class="mt-1 text-xs text-slate-400">Bugun</p>
          </div>
          <div class="rounded-lg bg-purple-100 p-2.5">
            <BookOpen :size="24" class="text-purple-600" />
          </div>
        </div>
      </div>

      <!-- Davomat xulosasi (mini) -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">Bugungi davomat</p>
            <p class="mt-1 text-3xl font-bold text-slate-800">{{ presentToday }}/{{ groupStudents.length }}</p>
            <p class="mt-1 text-xs text-slate-400">Kelganlar</p>
          </div>
          <div class="rounded-lg bg-blue-100 p-2.5">
            <Users :size="24" class="text-blue-600" />
          </div>
        </div>
      </div>

      <!-- Tezkor statistika -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">Kelmagan</p>
            <p class="mt-1 text-3xl font-bold text-slate-800">{{ absentToday }}</p>
            <p class="mt-1 text-xs text-slate-400">Bugun</p>
          </div>
          <div class="rounded-lg bg-red-100 p-2.5">
            <XCircle :size="24" class="text-red-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Bugungi jadval -->
      <div class="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">Bugungi darslar</h3>
          <Calendar :size="18" class="text-slate-400" />
        </div>
        
        <div v-if="todayLessons.length === 0" class="flex flex-col items-center justify-center py-8 text-slate-400">
          <Calendar :size="40" class="mb-2 opacity-50" />
          <p class="text-sm">Bugun darslar yo'q</p>
        </div>
        
        <div v-else class="space-y-3">
          <div
            v-for="lesson in todayLessons"
            :key="lesson.id"
            class="flex items-center gap-4 rounded-lg bg-slate-50 p-4"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <BookOpen :size="20" class="text-blue-600" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-slate-800">{{ lesson.subject }}</p>
              <p class="text-sm text-slate-500">{{ lesson.time }} • {{ lesson.room }}</p>
            </div>
            <span 
              class="rounded-lg px-3 py-1.5 text-xs font-medium"
              :class="getLessonStatusClass(lesson)"
            >
              {{ getLessonStatus(lesson) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tezkor amallar -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">Tezkor amallar</h3>
          <Zap :size="18" class="text-yellow-500" />
        </div>
        
        <div class="grid grid-cols-2 gap-3">
          <button
            @click="navigateTo('/leader/attendance')"
            class="flex flex-col items-center gap-3 rounded-xl bg-blue-50 p-4 text-blue-600 transition-all hover:bg-blue-100"
          >
            <CheckCircle :size="28" />
            <span class="text-sm font-medium">Davomat</span>
          </button>
          <button
            @click="navigateTo('/leader/students')"
            class="flex flex-col items-center gap-3 rounded-xl bg-purple-50 p-4 text-purple-600 transition-all hover:bg-purple-100"
          >
            <Users :size="28" />
            <span class="text-sm font-medium">Talabalar</span>
          </button>
          <button
            @click="navigateTo('/leader/schedule')"
            class="flex flex-col items-center gap-3 rounded-xl bg-green-50 p-4 text-green-600 transition-all hover:bg-green-100"
          >
            <Calendar :size="28" />
            <span class="text-sm font-medium">Jadval</span>
          </button>
          <button
            @click="navigateTo('/leader/analytics')"
            class="flex flex-col items-center gap-3 rounded-xl bg-orange-50 p-4 text-orange-600 transition-all hover:bg-orange-100"
          >
            <TrendingUp :size="28" />
            <span class="text-sm font-medium">Statistika</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Davomat xulosasi (to'liq) -->
    <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="font-semibold text-slate-800">Bugungi davomat xulosasi</h3>
        <span class="text-sm text-slate-500">{{ groupStudents.length }} talaba</span>
      </div>
      
      <div class="grid grid-cols-3 gap-4 mb-4">
        <div class="rounded-xl bg-green-50 p-4 text-center">
          <p class="text-3xl font-bold text-green-600">{{ presentToday }}</p>
          <p class="text-sm text-green-600/70">Keldi</p>
        </div>
        <div class="rounded-xl bg-red-50 p-4 text-center">
          <p class="text-3xl font-bold text-red-600">{{ absentToday }}</p>
          <p class="text-sm text-red-600/70">Kelmadi</p>
        </div>
        <div class="rounded-xl bg-yellow-50 p-4 text-center">
          <p class="text-3xl font-bold text-yellow-600">{{ lateToday }}</p>
          <p class="text-sm text-yellow-600/70">Kechikdi</p>
        </div>
      </div>
      
      <div class="h-3 overflow-hidden rounded-full bg-slate-100">
        <div class="flex h-full">
          <div 
            class="bg-green-500 transition-all" 
            :style="{ width: presentPercent + '%' }"
          ></div>
          <div 
            class="bg-yellow-500 transition-all" 
            :style="{ width: latePercent + '%' }"
          ></div>
          <div 
            class="bg-red-500 transition-all" 
            :style="{ width: absentPercent + '%' }"
          ></div>
        </div>
      </div>
      
      <p class="mt-3 text-center text-sm text-slate-500">
        {{ Math.round((presentToday + lateToday) / (groupStudents.length || 1) * 100) }}% davomat
      </p>
    </div>
  </div>
</template>

<script setup>
/**
 * Leader Dashboard - Real API Integration
 * Guruh sardorining boshqaruv paneli
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { 
  Users, BookOpen, Calendar, TrendingUp,
  CheckCircle, XCircle, Zap, Cake, Gift, Send,
  RefreshCw, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const dataStore = useDataStore()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const dashboardData = ref(null)
const groupStudentsList = ref([])
const scheduleList = ref([])
const attendanceToday = ref([])

// Load dashboard data
async function loadDashboard() {
  loading.value = true
  error.value = null
  
  try {
    // Leader dashboard endpoint mavjud bo'lsa
    try {
      const response = await api.request('/dashboard/leader')
      dashboardData.value = response
    } catch (e) {
      console.log('Leader dashboard endpoint not available')
    }
    
    // Guruh talabalarini yuklash
    const groupId = authStore.user?.groupId || authStore.user?.managed_group_id
    if (groupId) {
      try {
        const studentsResp = await api.getStudents({ group_id: groupId, limit: 100 })
        groupStudentsList.value = studentsResp.data?.map(s => ({
          id: s.id,
          name: s.full_name,
          studentId: s.student_id,
          groupId: s.group_id,
          phone: s.phone,
          birthDate: s.birth_date
        })) || []
      } catch (e) {
        console.log('Could not load group students')
      }
      
      // Jadval yuklash
      try {
        const scheduleResp = await api.getSchedule({ group_id: groupId })
        scheduleList.value = scheduleResp.data || []
      } catch (e) {
        console.log('Could not load schedule')
      }
      
      // Bugungi davomat
      try {
        const today = new Date().toISOString().split('T')[0]
        const attResp = await api.getAttendance({ 
          group_id: groupId, 
          date: today 
        })
        attendanceToday.value = attResp.data || []
      } catch (e) {
        console.log('Could not load today attendance')
      }
    }
  } catch (e) {
    console.error('Dashboard load error:', e)
    error.value = e.message || 'Ma\'lumotlar yuklanmadi'
  } finally {
    loading.value = false
  }
}

// Computed
const currentGroup = computed(() => {
  const groupId = authStore.user?.groupId || authStore.user?.managed_group_id
  const groupName = authStore.user?.group || authStore.user?.managedGroup
  return {
    id: groupId,
    name: groupName || authStore.user?.group_name || 'Noma\'lum guruh'
  }
})

const groupStudents = computed(() => groupStudentsList.value)

// Ertangi tug'ilgan kunlar
const tomorrowBirthdays = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowDay = tomorrow.getDate()
  const tomorrowMonth = tomorrow.getMonth() + 1
  
  return groupStudents.value.filter(student => {
    if (!student.birthDate) return false
    let day, month
    if (student.birthDate.includes('.')) {
      const parts = student.birthDate.split('.')
      day = parseInt(parts[0])
      month = parseInt(parts[1])
    } else if (student.birthDate.includes('-')) {
      const parts = student.birthDate.split('-')
      month = parseInt(parts[1])
      day = parseInt(parts[2])
    } else {
      return false
    }
    return day === tomorrowDay && month === tomorrowMonth
  })
})

const tomorrowDateFormatted = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toLocaleDateString('uz-UZ', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
})

function calculateAge(birthDate) {
  if (!birthDate) return 0
  let year
  if (birthDate.includes('.')) {
    year = parseInt(birthDate.split('.')[2])
  } else if (birthDate.includes('-')) {
    year = parseInt(birthDate.split('-')[0])
  } else {
    return 0
  }
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.getFullYear() - year
}

const todayLessons = computed(() => {
  const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
  const today = days[new Date().getDay()]
  return scheduleList.value.filter(s => 
    s.day?.toLowerCase() === today
  )
})

// Attendance stats
const presentToday = computed(() => {
  return attendanceToday.value.filter(a => a.status === 'present' || a.status === 'keldi').length
})

const absentToday = computed(() => {
  return attendanceToday.value.filter(a => a.status === 'absent' || a.status === 'kelmadi').length
})

const lateToday = computed(() => {
  return attendanceToday.value.filter(a => a.status === 'late' || a.status === 'kechikdi').length
})

const attendanceRate = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round(((presentToday.value + lateToday.value) / total) * 100)
})

const presentPercent = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round((presentToday.value / total) * 100)
})

const latePercent = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round((lateToday.value / total) * 100)
})

const absentPercent = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round((absentToday.value / total) * 100)
})

// Methods
function navigateTo(path) {
  router.push(path)
}

function getLessonStatus(lesson) {
  const now = new Date()
  const timeStr = lesson.time || lesson.start_time || ''
  if (!timeStr.includes('-')) return 'Kutilmoqda'
  
  const [startHour, startMin] = timeStr.split('-')[0].split(':').map(Number)
  const [endHour, endMin] = timeStr.split('-')[1].split(':').map(Number)
  
  const startTime = new Date()
  startTime.setHours(startHour, startMin, 0)
  
  const endTime = new Date()
  endTime.setHours(endHour, endMin, 0)
  
  if (now < startTime) return 'Kutilmoqda'
  if (now > endTime) return 'Tugadi'
  return 'Davom etmoqda'
}

function getLessonStatusClass(lesson) {
  const status = getLessonStatus(lesson)
  if (status === 'Davom etmoqda') return 'bg-green-100 text-green-600'
  if (status === 'Tugadi') return 'bg-slate-200 text-slate-500'
  return 'bg-blue-100 text-blue-600'
}

// Refresh
async function refresh() {
  await loadDashboard()
}

// Mount
onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
/* Minimal styles */
</style>
