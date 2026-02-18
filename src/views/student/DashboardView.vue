<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-700 p-6 text-white">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-white/10"></div>
      
      <div class="relative flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
        <div class="relative">
          <div class="h-14 w-14 sm:h-16 sm:w-16 overflow-hidden rounded-2xl bg-white/20 backdrop-blur">
            <img 
              v-if="user?.avatar" 
              :src="user.avatar" 
              class="h-full w-full object-cover"
            />
            <div v-else class="flex h-full w-full items-center justify-center text-2xl font-bold">
              {{ user?.name?.charAt(0) || 'T' }}
            </div>
          </div>
          <div class="absolute -bottom-1 -right-1 h-5 w-5 rounded-full border-2 border-white bg-green-400"></div>
        </div>
        
        <div class="flex-1">
          <p class="text-blue-100">{{ t('dashboard.welcome') }}</p>
          <h1 class="text-xl sm:text-2xl font-bold">{{ user?.name || t('dashboard.studentDefault') }}</h1>
          <p class="mt-1 text-xs sm:text-sm text-blue-200">{{ currentGroup?.name }} {{ t('dashboard.groupSuffix') }}</p>
        </div>
        
        <div class="hidden sm:block text-right">
          <p class="text-sm text-blue-200">{{ formattedDate }}</p>
          <p class="text-lg font-medium">{{ formattedTime }}</p>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      <div class="rounded-2xl border border-slate-200 bg-white p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-green-100">
            <TrendingUp :size="20" class="text-green-600" />
          </div>
          <div>
            <p class="text-lg sm:text-2xl font-bold text-slate-800">{{ attendanceRate }}%</p>
            <p class="text-[10px] sm:text-xs text-slate-500">{{ t('dashboard.attendanceRate') }}</p>
          </div>
        </div>
      </div>
      
      <div class="rounded-2xl border border-slate-200 bg-white p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-blue-100">
            <BookOpen :size="20" class="text-blue-600" />
          </div>
          <div>
            <p class="text-lg sm:text-2xl font-bold text-slate-800">{{ todayLessons.length }}</p>
            <p class="text-[10px] sm:text-xs text-slate-500">{{ t('dashboard.todayLessons') }}</p>
          </div>
        </div>
      </div>
      
      <div class="rounded-2xl border border-slate-200 bg-white p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-purple-100">
            <Book :size="20" class="text-purple-600" />
          </div>
          <div>
            <p class="text-lg sm:text-2xl font-bold text-slate-800">{{ borrowedBooks }}</p>
            <p class="text-[10px] sm:text-xs text-slate-500">{{ t('dashboard.borrowedBooks') }}</p>
          </div>
        </div>
      </div>
      
      <div class="rounded-2xl border border-slate-200 bg-white p-3 sm:p-4 shadow-sm">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl bg-amber-100">
            <Bell :size="20" class="text-amber-600" />
          </div>
          <div>
            <p class="text-lg sm:text-2xl font-bold text-slate-800">{{ unreadNotifications }}</p>
            <p class="text-[10px] sm:text-xs text-slate-500">{{ t('dashboard.newMessages') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Birthday Card (guruh a'zolarining tug'ilgan kunlari) -->
    <div 
      v-if="todayBirthdays.length > 0 || tomorrowBirthdays.length > 0"
      class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-5 text-white shadow-lg"
    >
      <div class="absolute -right-6 -top-6 h-28 w-28 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-white/10"></div>
      
      <div class="relative">
        <!-- Bugungi tug'ilgan kunlar -->
        <div v-if="todayBirthdays.length > 0">
          <div class="flex items-center gap-3 mb-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <Cake :size="20" />
            </div>
            <h3 class="text-base font-bold flex items-center gap-1.5"><PartyPopper :size="18" class="text-yellow-300" /> {{ t('dashboard.todayBirthday') }}</h3>
          </div>
          
          <div class="space-y-2">
            <div 
              v-for="student in todayBirthdays" 
              :key="'today-' + student.id"
              class="flex items-center gap-3 rounded-xl bg-white/15 p-3 backdrop-blur border border-white/20"
            >
              <div class="relative flex h-11 w-11 items-center justify-center rounded-xl bg-white/20 text-lg font-bold">
                {{ student.name.charAt(0) }}
                <span class="absolute -top-1 -right-1"><Cake :size="14" class="text-pink-300" /></span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold truncate">{{ student.name }}</p>
                <p class="text-xs text-white/80">{{ student.age }} {{ t('dashboard.yearsOld') }}</p>
              </div>
              <button 
                @click="sendBirthdayCongrats(student)"
                :disabled="congratsSending[student.id]"
                class="flex items-center gap-1.5 rounded-lg bg-white/20 px-3 py-1.5 text-xs font-medium backdrop-blur transition-all hover:bg-white/30 disabled:opacity-50 shrink-0"
              >
                <Gift :size="14" />
                {{ congratsSent[student.id] ? '✓' : t('dashboard.sendCongrats') }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Ertangi tug'ilgan kunlar -->
        <div v-if="tomorrowBirthdays.length > 0" :class="{ 'mt-4 pt-4 border-t border-white/20': todayBirthdays.length > 0 }">
          <div class="flex items-center gap-3 mb-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <Calendar :size="20" />
            </div>
            <h3 class="text-base font-bold flex items-center gap-1.5"><Cake :size="18" class="text-pink-300" /> {{ t('dashboard.birthdayTomorrow') }}</h3>
          </div>
          
          <div class="space-y-2">
            <div 
              v-for="student in tomorrowBirthdays" 
              :key="'tmrw-' + student.id"
              class="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur"
            >
              <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-white/20 text-lg font-bold">
                {{ student.name.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold truncate">{{ student.name }}</p>
                <p class="text-xs text-white/80">{{ student.age }} {{ t('dashboard.willTurn') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid gap-6 lg:grid-cols-3">
      <!-- Today's Schedule -->
      <div class="lg:col-span-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">{{ t('dashboard.todaySchedule') }}</h2>
          <router-link to="/student/schedule" class="text-sm text-blue-500 hover:text-blue-600">
            {{ t('dashboard.viewAll') }}
          </router-link>
        </div>
        
        <div v-if="todayLessons.length === 0" class="flex flex-col items-center justify-center py-8 text-slate-400">
          <Calendar :size="48" class="mb-2 opacity-50" />
          <p>{{ t('dashboard.noLessonsToday') }}</p>
        </div>
        
        <div v-else class="space-y-3">
          <div
            v-for="lesson in todayLessons.slice(0, 4)"
            :key="lesson.id"
            class="flex items-center gap-4 rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex h-12 w-12 flex-col items-center justify-center rounded-xl bg-blue-500 text-white">
              <span class="text-xs">{{ lesson.time.split('-')[0].split(':')[0] }}</span>
              <span class="text-[10px] opacity-75">{{ lesson.time.split('-')[0].split(':')[1] }}</span>
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-800">{{ lesson.subject }}</p>
              <p class="text-sm text-slate-500">{{ lesson.room }} • {{ lesson.teacher }}</p>
            </div>
            <span 
              class="rounded-lg px-3 py-1 text-xs font-medium"
              :class="getLessonStatusClass(lesson)"
            >
              {{ getLessonStatus(lesson) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Section -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Recent Attendance -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">{{ t('dashboard.recentAttendance') }}</h2>
          <router-link to="/student/attendance" class="text-sm text-blue-500 hover:text-blue-600">
            {{ t('dashboard.viewAll') }}
          </router-link>
        </div>
        
        <div class="space-y-2">
          <div
            v-for="record in recentAttendance"
            :key="record.date"
            class="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3"
          >
            <div class="flex items-center gap-3">
              <div 
                class="flex h-10 w-10 items-center justify-center rounded-lg"
                :class="getAttendanceColor(record.status)"
              >
                <CheckCircle v-if="record.status === 'present'" :size="20" />
                <XCircle v-else-if="record.status === 'absent'" :size="20" />
                <Clock v-else :size="20" />
              </div>
              <div>
                <p class="text-sm font-medium text-slate-800">{{ formatDateShort(record.date) }}</p>
                <p class="text-xs text-slate-500">{{ record.subject }}</p>
              </div>
            </div>
            <span 
              class="rounded-lg px-3 py-1 text-xs font-medium"
              :class="getAttendanceBadge(record.status)"
            >
              {{ getAttendanceText(record.status) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Library Quick Access -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">{{ t('dashboard.libraryAccess') }}</h2>
          <router-link to="/student/library" class="text-sm text-blue-500 hover:text-blue-600">
            {{ t('dashboard.viewAll') }}
          </router-link>
        </div>
        
        <div class="mb-4 grid grid-cols-3 gap-3">
          <button
            @click="$router.push('/student/library?category=darslik')"
            class="flex flex-col items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-600 transition-all hover:bg-blue-100"
          >
            <GraduationCap :size="24" />
            <span class="text-xs">{{ t('dashboard.textbooks') }}</span>
          </button>
          <button
            @click="$router.push('/student/library?category=ilmiy')"
            class="flex flex-col items-center gap-2 rounded-xl bg-purple-50 p-3 text-purple-600 transition-all hover:bg-purple-100"
          >
            <FileText :size="24" />
            <span class="text-xs">{{ t('dashboard.scientific') }}</span>
          </button>
          <button
            @click="$router.push('/student/library?category=badiiy')"
            class="flex flex-col items-center gap-2 rounded-xl bg-amber-50 p-3 text-amber-600 transition-all hover:bg-amber-100"
          >
            <BookOpen :size="24" />
            <span class="text-xs">{{ t('dashboard.fiction') }}</span>
          </button>
        </div>
        
        <div class="rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 p-4 text-white">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
              <Book :size="24" />
            </div>
            <div>
              <p class="font-medium">KUAF Mutola</p>
              <p class="text-sm text-emerald-100">{{ totalBooks }}+ elektron kitob</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <router-link 
        to="/student/schedule"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-blue-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
          <Calendar :size="20" class="text-blue-600" />
        </div>
        <span class="font-medium text-slate-700">{{ t('layout.schedule') }}</span>
      </router-link>
      
      <router-link 
        to="/student/attendance"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-green-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
          <CheckCircle :size="20" class="text-green-600" />
        </div>
        <span class="font-medium text-slate-700">{{ t('layout.attendance') }}</span>
      </router-link>
      
      <router-link 
        to="/student/library"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-purple-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100">
          <Book :size="20" class="text-purple-600" />
        </div>
        <span class="font-medium text-slate-700">{{ t('layout.library') }}</span>
      </router-link>
      
      <router-link 
        to="/student/profile"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-amber-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
          <User :size="20" class="text-amber-600" />
        </div>
        <span class="font-medium text-slate-700">{{ t('common.profile') }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
/**
 * Student Dashboard - Real API Integration
 */
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import { useLanguageStore } from '@/stores/language'
import {
  Bell,
  Book,
  BookOpen,
  Cake,
  Calendar,
  CheckCircle,
  Clock,
  FileText,
  Gift,
  GraduationCap,
  PartyPopper,
  TrendingUp,
  User,
  XCircle
} from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'

const authStore = useAuthStore()
const dataStore = useDataStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const currentTime = ref(new Date())
const dashboardData = ref(null)
const scheduleList = ref([])
const attendanceList = ref([])

// Birthday state
const birthdayData = ref({ today: [], tomorrow: [] })
const congratsSending = ref({})
const congratsSent = ref({})

let timeInterval = null

// Load dashboard data
async function loadDashboard() {
  loading.value = true
  
  try {
    // Try student dashboard endpoint
    try {
      const response = await api.request('/dashboard/student')
      dashboardData.value = response
    } catch (e) {
      console.log('Student dashboard endpoint not available:', e.message)
    }
    
    // Load schedule for group
    const groupId = authStore.user?.groupId || authStore.user?.group_id
    if (groupId) {
      try {
        const dayMap = {
          'monday': 'Dushanba', 'tuesday': 'Seshanba', 'wednesday': 'Chorshanba',
          'thursday': 'Payshanba', 'friday': 'Juma', 'saturday': 'Shanba', 'sunday': 'Yakshanba'
        }
        const scheduleResp = await api.getScheduleByGroup(groupId)
        let items = []
        if (Array.isArray(scheduleResp)) {
          items = scheduleResp
        } else if (typeof scheduleResp === 'object') {
          // Week schedule format: { monday: [...], tuesday: [...] }
          for (const [eng, uz] of Object.entries(dayMap)) {
            if (scheduleResp[eng] && Array.isArray(scheduleResp[eng])) {
              scheduleResp[eng].forEach(s => {
                items.push({ ...s, day: uz })
              })
            }
          }
          // Also check for items/data arrays
          if (items.length === 0 && scheduleResp.items) items = scheduleResp.items
          if (items.length === 0 && scheduleResp.data) items = scheduleResp.data
        }
        scheduleList.value = items
          .filter(s => !s.is_cancelled)
          .map(s => {
          // Build time string: strip spaces and seconds
          let timeStr = s.time || s.time_range || (s.start_time && s.end_time ? `${s.start_time}-${s.end_time}` : '')
          timeStr = timeStr.replace(/\s/g, '').replace(/(\d{2}:\d{2}):\d{2}/g, '$1')
          return {
            id: s.id,
            day: s.day || dayMap[s.day_of_week] || s.day_of_week || '',
            time: timeStr,
            subject: s.subject || s.subject_name || '',
            teacher: s.teacher || s.teacher_name || '',
            room: s.room || s.classroom || s.location || ''
          }
        })
      } catch (e) {
        console.log('Schedule not available:', e.message)
      }
    }
    
    // Load attendance for current student
    const studentId = authStore.user?.studentDbId || authStore.user?.id
    if (studentId) {
      try {
        const attResp = await api.getStudentAttendance(studentId)
        if (Array.isArray(attResp)) {
          attendanceList.value = attResp.map(a => ({
            id: a.id,
            date: a.date,
            status: a.status,
            subject: a.subject || a.lesson_name || t('common.total'),
            student_id: a.student_id
          }))
        } else if (attResp?.data) {
          attendanceList.value = (attResp.data || []).map(a => ({
            id: a.id,
            date: a.date,
            status: a.status,
            subject: a.subject || a.lesson_name || 'Umumiy',
            student_id: a.student_id
          }))
        }
      } catch (e) {
        console.log('Attendance not available:', e.message)
      }
    }
    
    // Guruh a'zolarining tug'ilgan kunlarini yuklash
    const groupIdForBday = groupId || authStore.user?.groupId || authStore.user?.group_id
    if (groupIdForBday) {
      try {
        const bdayResp = await api.getUpcomingBirthdays({ group_id: groupIdForBday, days: 1 })
        birthdayData.value = {
          today: (bdayResp.today || []).filter(s => s.id !== (authStore.user?.studentDbId)),
          tomorrow: (bdayResp.tomorrow || []).filter(s => s.id !== (authStore.user?.studentDbId))
        }
      } catch (e) {
        console.log('Birthdays not available:', e.message)
      }
    }
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  timeInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
  
  loadDashboard()
})

onUnmounted(() => {
  clearInterval(timeInterval)
})

// Computed
const user = computed(() => authStore.user)

const currentGroup = computed(() => {
  return {
    name: authStore.user?.group || authStore.user?.group_name || t('common.unknown')
  }
})

const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('uz-UZ', {
    weekday: 'long',
    day: 'numeric',
    month: 'long'
  })
})

const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('uz-UZ', {
    hour: '2-digit',
    minute: '2-digit'
  })
})

// Birthday computed
const todayBirthdays = computed(() => birthdayData.value.today || [])
const tomorrowBirthdays = computed(() => birthdayData.value.tomorrow || [])

// Birthday congrats
async function sendBirthdayCongrats(student) {
  congratsSending.value[student.id] = true
  try {
    const senderName = authStore.user?.name || t('dashboard.groupMember')
    await api.createNotification({
      user_id: student.user_id,
      title: "🎂 Tug'ilgan kun tabrigi!",
      message: `🎉 Hurmatli ${student.name}!\n\nTug'ilgan kuningiz muborak bo'lsin! Sizga baxt, sog'lik va muvaffaqiyatlar tilaymiz!\n\nHurmat bilan, ${senderName}`,
      type: 'info',
      priority: 'normal'
    })
    congratsSent.value[student.id] = true
  } catch (e) {
    console.error('Tabrik yuborishda xatolik:', e)
  } finally {
    congratsSending.value[student.id] = false
  }
}

const todayLessons = computed(() => {
  const dayNames = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  const today = dayNames[new Date().getDay()]
  return scheduleList.value.filter(s => s.day === today)
})

const attendanceRate = computed(() => {
  if (dashboardData.value?.attendance?.attendance_rate) {
    return Math.round(dashboardData.value.attendance.attendance_rate)
  }
  if (attendanceList.value.length === 0) return 100
  const present = attendanceList.value.filter(a => 
    a.status === 'present' || a.status === 'late' || a.status === 'keldi' || a.status === 'kechikdi'
  ).length
  return Math.round((present / attendanceList.value.length) * 100)
})

const recentAttendance = computed(() => {
  return attendanceList.value
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
    .map(a => ({
      ...a,
      subject: a.subject || 'Umumiy'
    }))
})

const borrowedBooks = computed(() => dashboardData.value?.borrowed_books || dashboardData.value?.borrowedBooks || 0)
const unreadNotifications = computed(() => dashboardData.value?.unread_notifications || dashboardData.value?.unreadNotifications || 0)
const totalBooks = ref(5000)

// Methods
function getTashkentNow() {
  const now = new Date()
  return new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Tashkent' }))
}

function getLessonStatus(lesson) {
  const now = getTashkentNow()
  const timeStr = lesson.time || lesson.start_time || ''
  if (!timeStr.includes('-')) return t('schedule.upcoming')
  
  const [startHour, startMin] = timeStr.split('-')[0].split(':').map(Number)
  const [endHour, endMin] = timeStr.split('-')[1].split(':').map(Number)
  
  const startTime = new Date(now)
  startTime.setHours(startHour, startMin, 0, 0)
  
  const endTime = new Date(now)
  endTime.setHours(endHour, endMin, 0, 0)
  
  if (now < startTime) return t('schedule.upcoming')
  if (now > endTime) return t('schedule.finished')
  return t('schedule.ongoing')
}

function getLessonStatusClass(lesson) {
  const now = getTashkentNow()
  const timeStr = lesson.time || lesson.start_time || ''
  if (!timeStr.includes('-')) return 'bg-blue-100 text-blue-600'
  
  const [startHour, startMin] = timeStr.split('-')[0].split(':').map(Number)
  const [endHour, endMin] = timeStr.split('-')[1].split(':').map(Number)
  
  const startTime = new Date(now)
  startTime.setHours(startHour, startMin, 0, 0)
  
  const endTime = new Date(now)
  endTime.setHours(endHour, endMin, 0, 0)
  
  if (now > endTime) return 'bg-slate-100 text-slate-500'
  if (now >= startTime) return 'bg-green-100 text-green-600'
  return 'bg-blue-100 text-blue-600'
}

function getAttendanceColor(status) {
  if (status === 'present' || status === 'keldi') return 'bg-green-100 text-green-600'
  if (status === 'absent' || status === 'kelmadi') return 'bg-red-100 text-red-600'
  return 'bg-yellow-100 text-yellow-600'
}

function getAttendanceBadge(status) {
  if (status === 'present' || status === 'keldi') return 'bg-green-100 text-green-600'
  if (status === 'absent' || status === 'kelmadi') return 'bg-red-100 text-red-600'
  return 'bg-yellow-100 text-yellow-600'
}

function getAttendanceText(status) {
  if (status === 'present' || status === 'keldi') return t('attendance.present')
  if (status === 'absent' || status === 'kelmadi') return t('attendance.absent')
  return t('attendance.late')
}

function formatDateShort(date) {
  return new Date(date).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'short'
  })
}
</script>
