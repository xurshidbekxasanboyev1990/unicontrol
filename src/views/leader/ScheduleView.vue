<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <RefreshCw class="w-12 h-12 text-emerald-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-600">{{ $t('common.loading') }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6">
      <div class="flex items-center gap-3">
        <AlertCircle class="w-6 h-6 text-rose-500" />
        <div>
          <h3 class="font-semibold text-rose-700">{{ $t('dashboard.errorOccurred') }}</h3>
          <p class="text-rose-600 text-sm mt-1">{{ error }}</p>
        </div>
        <button @click="loadSchedule" class="ml-auto px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600">
          {{ $t('common.retry') }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Header with View Toggle -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('schedule.title') }}</h1>
          <p class="text-sm text-slate-500">{{ groupName }} {{ $t('schedule.groupSchedule') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <button 
            @click="loadSchedule"
            class="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            title="refresh"
          >
            <RefreshCw class="w-5 h-5 text-slate-500" />
          </button>
          <div class="flex items-center bg-slate-100 rounded-xl p-1">
            <button 
              @click="viewMode = 'week'"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="viewMode === 'week' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'"
            >
              {{ $t('schedule.weekly') }}
            </button>
            <button 
              @click="viewMode = 'today'"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="viewMode === 'today' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'"
            >
              {{ $t('schedule.today') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Today View -->
      <template v-if="viewMode === 'today'">
        <div class="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-emerald-100">{{ formattedDate }}</p>
              <h2 class="text-xl sm:text-2xl font-bold mt-1">{{ todayName }}</h2>
            </div>
            <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
              <CalendarDays class="w-7 h-7" />
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div 
            v-for="(lesson, index) in todayLessons" 
            :key="lesson.id"
            class="bg-white rounded-2xl border border-slate-200 p-5 flex items-center gap-4"
          >
            <div 
              class="w-14 h-14 rounded-xl flex items-center justify-center text-white font-bold"
              :class="subjectColors[index % subjectColors.length]"
            >
              {{ index + 1 }}
            </div>
            
            <div class="flex-1">
              <h3 class="font-semibold text-slate-800">{{ lesson.subject || lesson.subjectName }}</h3>
              <p class="text-sm text-slate-500 flex items-center gap-2 mt-1">
                <User class="w-4 h-4" />
                {{ lesson.teacher || lesson.teacherName || $t('schedule.noTeacher') }}
              </p>
            </div>

            <div class="text-right">
              <p class="font-medium text-slate-800 flex items-center gap-2">
                <Clock class="w-4 h-4 text-emerald-500" />
                {{ lesson.time || lesson.startTime }}
              </p>
              <p class="text-sm text-slate-500 flex items-center gap-2 mt-1">
                <MapPin class="w-4 h-4" />
                {{ lesson.room || lesson.roomNumber || 'N/A' }}
              </p>
            </div>

            <!-- Mark Attendance Button -->
            <router-link 
              :to="{ path: '/leader/attendance', query: { lessonId: lesson.id } }"
              class="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors flex items-center gap-2"
            >
              <CheckCircle class="w-4 h-4" />
              {{ $t('schedule.attendance') }}
            </router-link>
          </div>

          <div v-if="todayLessons.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
            <Coffee class="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p class="text-lg font-medium text-slate-600">{{ $t('schedule.noLessonsToday') }}</p>
            <p class="text-sm text-slate-400 mt-1">{{ $t('schedule.restAndPrepare') }}</p>
          </div>
        </div>
      </template>

      <!-- Week View -->
      <template v-else>
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden overflow-x-auto">
          <div class="grid grid-cols-6 border-b border-slate-100 min-w-[640px]">
            <div class="p-4 bg-slate-50"></div>
            <div 
              v-for="day in weekDays" 
              :key="day"
              class="p-4 text-center font-semibold text-slate-700 bg-slate-50"
              :class="isToday(day) ? 'bg-emerald-50 text-emerald-700' : ''"
            >
              {{ day }}
            </div>
          </div>

          <div 
            v-for="timeSlot in timeSlots" 
            :key="timeSlot"
            class="grid grid-cols-6 border-b border-slate-100 last:border-0 min-w-[640px]"
          >
            <div class="p-4 text-sm font-medium text-slate-500 bg-slate-50 flex items-center justify-center">
              {{ timeSlot }}
            </div>
            <div 
              v-for="day in weekDays" 
              :key="day + timeSlot"
              class="p-2 min-h-[80px]"
              :class="isToday(day) ? 'bg-emerald-50/30' : ''"
            >
              <div 
                v-if="getLessonAt(day, timeSlot)"
                class="p-2 rounded-lg text-white text-sm h-full cursor-pointer hover:opacity-90 transition-opacity"
                :class="getSubjectColor(getLessonAt(day, timeSlot).subject || getLessonAt(day, timeSlot).subjectName)"
                @click="selectLesson(getLessonAt(day, timeSlot))"
              >
                <p class="font-medium truncate">{{ getLessonAt(day, timeSlot).subject || getLessonAt(day, timeSlot).subjectName }}</p>
                <p class="text-xs opacity-80 truncate">{{ getLessonAt(day, timeSlot).room || getLessonAt(day, timeSlot).roomNumber }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Legend -->
        <div class="flex flex-wrap items-center gap-4 text-sm">
          <span class="text-slate-500">{{ $t('schedule.subjectsLegend') }}:</span>
          <div v-for="(color, subject) in subjectColorMap" :key="subject" class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full" :class="color"></span>
            <span class="text-slate-600">{{ subject }}</span>
          </div>
        </div>
      </template>

      <!-- Lesson Details Modal -->
      <div 
        v-if="selectedLesson" 
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        @click.self="selectedLesson = null"
      >
        <div class="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-800">{{ $t('schedule.lessonDetails') }}</h3>
            <button @click="selectedLesson = null" class="p-2 hover:bg-slate-100 rounded-lg">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <p class="text-sm text-slate-500">{{ $t('schedule.subjectLabel') }}</p>
              <p class="font-medium text-slate-800">{{ selectedLesson.subject || selectedLesson.subjectName }}</p>
            </div>
            <div>
              <p class="text-sm text-slate-500">{{ $t('schedule.teacherLabel') }}</p>
              <p class="font-medium text-slate-800">{{ selectedLesson.teacher || selectedLesson.teacherName || $t('schedule.notSpecified') }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-slate-500">{{ $t('schedule.dayLabel') }}</p>
                <p class="font-medium text-slate-800">{{ selectedLesson.day || selectedLesson.dayName }}</p>
              </div>
              <div>
                <p class="text-sm text-slate-500">{{ $t('schedule.timeLabel') }}</p>
                <p class="font-medium text-slate-800">{{ selectedLesson.time || selectedLesson.startTime }}</p>
              </div>
            </div>
            <div>
              <p class="text-sm text-slate-500">{{ $t('schedule.roomBuilding') }}</p>
              <p class="font-medium text-slate-800">{{ selectedLesson.room || selectedLesson.roomNumber || $t('schedule.notSpecified') }}</p>
            </div>
          </div>

          <div class="mt-6 flex gap-3">
            <router-link 
              :to="{ path: '/leader/attendance', query: { lessonId: selectedLesson.id } }"
              class="flex-1 px-4 py-3 bg-emerald-500 text-white rounded-xl font-medium text-center hover:bg-emerald-600 transition-colors"
            >
              {{ $t('schedule.takeAttendance') }}
            </router-link>
            <button 
              @click="selectedLesson = null"
              class="px-4 py-3 border border-slate-200 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              {{ $t('common.close') }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import {
    AlertCircle,
    CalendarDays,
    CheckCircle,
    Clock,
    Coffee,
    MapPin,
    RefreshCw,
    User,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useDataStore } from '../../stores/data'

const dataStore = useDataStore()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const viewMode = ref('week')
const schedule = ref([])
const selectedLesson = ref(null)
const groupInfo = ref(null)

const weekDays = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma']
const timeSlots = ['08:30', '10:00', '12:00', '13:30', '15:00']

const subjectColors = [
  'bg-gradient-to-br from-blue-500 to-blue-600',
  'bg-gradient-to-br from-violet-500 to-violet-600',
  'bg-gradient-to-br from-emerald-500 to-emerald-600',
  'bg-gradient-to-br from-orange-500 to-orange-600',
  'bg-gradient-to-br from-rose-500 to-rose-600'
]

// Computed
const groupName = computed(() => {
  return groupInfo.value?.name || authStore.user?.groupName || 'Guruh'
})

const subjectColorMap = computed(() => {
  const subjects = [...new Set(schedule.value.map(s => s.subject || s.subjectName))]
  const colors = ['bg-blue-500', 'bg-violet-500', 'bg-emerald-500', 'bg-orange-500', 'bg-rose-500']
  return subjects.reduce((acc, subject, index) => {
    if (subject) {
      acc[subject] = colors[index % colors.length]
    }
    return acc
  }, {})
})

const todayName = computed(() => {
  const days = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  return days[new Date().getDay()]
})

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
})

const todayLessons = computed(() => {
  const dayIndex = new Date().getDay()
  const dayNames = ['', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  const dayName = dayNames[dayIndex]
  
  return schedule.value
    .filter(s => (s.day || s.dayName) === dayName)
    .sort((a, b) => {
      const timeA = a.time || a.startTime || ''
      const timeB = b.time || b.startTime || ''
      return timeA.localeCompare(timeB)
    })
})

// Methods
async function loadSchedule() {
  loading.value = true
  error.value = null
  
  try {
    // First get group info from dashboard
    const dashboardResp = await api.request('/dashboard/leader')
    const groupId = dashboardResp?.group?.id
    groupInfo.value = dashboardResp?.group
    
    if (!groupId) {
      error.value = 'Guruh ma\'lumotlari topilmadi'
      return
    }
    
    // Try to get week schedule first
    try {
      const response = await api.request(`/schedule/group/${groupId}/week`)
      
      // Week schedule response format: { monday: [], tuesday: [], ... }
      const allLessons = []
      const dayMapping = {
        'monday': 'Dushanba',
        'tuesday': 'Seshanba', 
        'wednesday': 'Chorshanba',
        'thursday': 'Payshanba',
        'friday': 'Juma',
        'saturday': 'Shanba'
      }
      
      if (response && typeof response === 'object') {
        for (const [dayKey, lessons] of Object.entries(response)) {
          if (Array.isArray(lessons)) {
            lessons.forEach(lesson => {
              allLessons.push(normalizeScheduleItem({
                ...lesson,
                day: dayMapping[dayKey] || dayKey
              }))
            })
          }
        }
        schedule.value = allLessons
      } else if (Array.isArray(response)) {
        schedule.value = response.map(s => normalizeScheduleItem(s))
      }
    } catch (e) {
      // Fallback to list endpoint
      try {
        const response = await api.request(`/schedule?group_id=${groupId}`)
        if (response && response.items) {
          schedule.value = response.items.map(s => normalizeScheduleItem(s))
        } else if (Array.isArray(response)) {
          schedule.value = response.map(s => normalizeScheduleItem(s))
        }
      } catch (listError) {
        console.log('Schedule API not available, using store data')
        // Fallback to store
        await dataStore.fetchSchedule()
        schedule.value = dataStore.schedule || []
      }
    }
  } catch (e) {
    console.error('Load schedule error:', e)
    error.value = e.message || 'Jadval yuklanmadi'
  } finally {
    loading.value = false
  }
}

function normalizeScheduleItem(item) {
  // Build time string: strip spaces and seconds for consistent HH:MM-HH:MM format
  let timeRange = item.time_range || (item.start_time && item.end_time ? `${item.start_time}-${item.end_time}` : '')
  timeRange = timeRange.replace(/\s/g, '').replace(/(\d{2}:\d{2}):\d{2}/g, '$1')
  const startTime = item.start_time ? item.start_time.substring(0, 5) : (timeRange.split('-')[0] || '')
  // Build location: combine building + room
  const building = item.building || ''
  const room = item.room || item.room_number || item.roomNumber || ''
  const location = item.location || (building && room ? `${building}, ${room}` : building || room) || ''
  return {
    id: item.id,
    day: item.day || item.day_name || item.dayName,
    dayName: item.day || item.day_name || item.dayName,
    time: timeRange || item.time || item.start_time || item.startTime,
    startTime: startTime || item.startTime || timeRange,
    endTime: item.end_time ? item.end_time.substring(0, 5) : (item.endTime || ''),
    subject: item.subject || item.subject_name || item.subjectName,
    subjectName: item.subject || item.subject_name || item.subjectName,
    teacher: item.teacher_name || item.teacher || item.teacherName,
    teacherName: item.teacher_name || item.teacher || item.teacherName,
    room: location,
    roomNumber: location,
    building: building,
    type: item.schedule_type || item.type || item.lesson_type || 'lecture'
  }
}

const isToday = (day) => {
  const days = ['', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  return days[new Date().getDay()] === day
}

const getLessonAt = (day, time) => {
  return schedule.value.find(s => {
    const lessonDay = s.day || s.dayName
    const lessonTime = s.time || s.startTime || ''
    // Match start time: lessonTime could be "08:30" or "08:30-10:00"
    const startTime = lessonTime.split('-')[0]?.trim()
    return lessonDay === day && startTime === time
  })
}

const getSubjectColor = (subject) => {
  const subjects = [...new Set(schedule.value.map(s => s.subject || s.subjectName))]
  const index = subjects.indexOf(subject)
  const colors = [
    'bg-blue-500',
    'bg-violet-500', 
    'bg-emerald-500',
    'bg-orange-500',
    'bg-rose-500'
  ]
  return colors[index % colors.length]
}

function selectLesson(lesson) {
  selectedLesson.value = lesson
}

// Initialize
onMounted(() => {
  loadSchedule()
})
</script>
