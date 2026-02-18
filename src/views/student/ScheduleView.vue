<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('schedule.title') }}</h1>
        <p class="text-sm text-slate-500 mt-1">{{ $t('schedule.weekSchedule') }}</p>
      </div>
      <div class="flex items-center gap-2 bg-white rounded-xl p-1 border border-slate-200 shadow-sm">
        <button
          v-for="view in ['weekly', 'today']"
          :key="view"
          @click="activeView = view"
          :class="[
            'px-5 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200',
            activeView === view
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/30'
              : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
          ]"
        >
          {{ view === 'weekly' ? $t('schedule.weekly') : $t('schedule.today') }}
        </button>
      </div>
    </div>

    <!-- Holiday Banner -->
    <div v-for="holiday in activeHolidays" :key="holiday.id"
      class="bg-gradient-to-r from-amber-500 to-orange-500 rounded-2xl p-4 text-white relative overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-28 h-28 bg-white/10 rounded-full -translate-y-8 translate-x-8"></div>
      <div class="flex items-center gap-3 relative z-10">
        <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur flex-shrink-0">
          <PartyPopper class="w-5 h-5" />
        </div>
        <div class="min-w-0">
          <h3 class="font-bold text-base">{{ holiday.title }}</h3>
          <p v-if="holiday.description" class="text-white/80 text-sm mt-0.5 line-clamp-1">{{ holiday.description }}</p>
          <p class="text-white/70 text-xs mt-1">{{ holiday.start_date }} — {{ holiday.end_date }}</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">

      <div class="text-center">
        <div class="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-slate-500 font-medium">{{ $t('common.loading') }}</p>
      </div>
    </div>

    <template v-else>
      <!-- Today's Schedule (when Bugun selected) -->
      <div v-if="activeView === 'today'" class="space-y-4">
        <div class="bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 rounded-2xl p-6 text-white relative overflow-hidden">
          <div class="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-10 translate-x-10"></div>
          <div class="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-10 -translate-x-10"></div>
          <div class="relative z-10">
            <div class="flex items-center gap-3 mb-2">
              <CalendarDays class="w-5 h-5 opacity-80" />
              <span class="text-sm opacity-80">{{ todayFormatted }}</span>
            </div>
            <h2 class="text-2xl font-bold">{{ currentDayName }}</h2>
            <p class="text-emerald-100 mt-1">{{ todaySchedule.length }} {{ $t('schedule.lessonsCount') }}</p>
          </div>
        </div>

        <div v-if="todaySchedule.length > 0" class="space-y-3">
          <div
            v-for="(lesson, index) in todaySchedule"
            :key="lesson.id"
            class="group bg-white rounded-2xl border border-slate-200/80 hover:shadow-lg hover:shadow-slate-200/50 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
          >
            <div class="flex items-stretch">
              <!-- Color sidebar -->
              <div class="w-1.5 flex-shrink-0 rounded-l-2xl" :style="{ backgroundColor: getColor(lesson.subject).main }"></div>
              <div class="flex-1 p-4 flex items-start gap-4">
                <!-- Time block -->
                <div class="flex-shrink-0 w-[72px] text-center py-1">
                  <div class="text-base font-bold text-slate-800 leading-tight">{{ lesson.time.split('-')[0] }}</div>
                  <div class="text-[10px] text-slate-400 my-0.5">—</div>
                  <div class="text-xs text-slate-400 font-medium">{{ lesson.time.split('-')[1] }}</div>
                </div>

                <!-- Divider -->
                <div class="w-px bg-slate-200/80 self-stretch flex-shrink-0"></div>

                <!-- Lesson info -->
                <div class="flex-1 min-w-0 py-0.5">
                  <div class="flex items-center gap-2.5 mb-2">
                    <span class="w-2.5 h-2.5 rounded-full ring-2 ring-offset-1 flex-shrink-0"
                      :style="{ backgroundColor: getColor(lesson.subject).main, ringColor: getColor(lesson.subject).light }"
                    ></span>
                    <h3 class="font-bold text-slate-800 text-[15px] truncate">{{ lesson.subject }}</h3>
                  </div>
                  <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-500">
                    <span v-if="lesson.teacher" class="flex items-center gap-1.5">
                      <User class="w-3.5 h-3.5 text-slate-400" />
                      {{ lesson.teacher }}
                    </span>
                    <span v-if="lesson.room" class="flex items-center gap-1.5">
                      <MapPin class="w-3.5 h-3.5 text-slate-400" />
                      {{ lesson.room }}
                    </span>
                  </div>
                </div>

                <!-- Lesson number badge -->
                <div class="flex-shrink-0 self-center">
                  <div
                    class="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold"
                    :style="{
                      backgroundColor: getColor(lesson.subject).ultra,
                      color: getColor(lesson.subject).main
                    }"
                  >
                    {{ lesson.lessonNumber || (index + 1) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="bg-white rounded-2xl p-14 border border-slate-200 text-center">
          <div class="w-20 h-20 bg-slate-100 rounded-2xl mx-auto mb-5 flex items-center justify-center">
            <Coffee class="w-10 h-10 text-slate-300" />
          </div>
          <h3 class="font-bold text-slate-800 text-lg mb-1">{{ $t('dashboard.noLessonsToday') }}</h3>
          <p class="text-slate-400 text-sm">{{ $t('schedule.break') }}</p>
        </div>
      </div>

      <!-- Weekly Schedule -->
      <div v-else class="space-y-4">
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <div class="overflow-x-auto custom-scrollbar">
            <table class="w-full border-collapse" style="min-width: 900px;">
              <thead>
                <tr>
                  <th class="sticky left-0 z-10 bg-slate-50 px-4 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider w-[130px] border-b border-slate-200">
                    <div class="flex items-center gap-2">
                      <Clock class="w-4 h-4 text-slate-400" />
                      {{ $t('schedule.time') }}
                    </div>
                  </th>
                  <th
                    v-for="day in days"
                    :key="day"
                    :class="[
                      'px-3 py-4 text-center text-xs font-bold uppercase tracking-wider border-b border-l',
                      isToday(day)
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-slate-50 text-slate-500 border-slate-200'
                    ]"
                    style="min-width: 150px;"
                  >
                    <div class="flex flex-col items-center gap-1">
                      <span>{{ day }}</span>
                      <span v-if="isToday(day)" class="inline-flex items-center px-2 py-0.5 bg-emerald-500 text-white text-[10px] font-bold rounded-full">
                        {{ $t('common.today') }}
                      </span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(time, tIdx) in timeSlots" :key="time"
                  :class="tIdx % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'"
                >
                  <!-- Time cell -->
                  <td class="sticky left-0 z-10 px-4 py-4 border-b border-slate-100 font-semibold"
                    :class="tIdx % 2 === 0 ? 'bg-white' : 'bg-slate-50'"
                  >
                    <div class="flex flex-col items-start">
                      <span class="text-sm font-bold text-slate-700">{{ time.split('-')[0] }}</span>
                      <span class="text-[11px] text-slate-400">{{ time.split('-')[1] }}</span>
                    </div>
                    <div class="mt-1 inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 text-slate-500 rounded text-[10px] font-bold">
                      {{ tIdx + 1 }}-{{ $t('schedule.lessonPeriod') }}
                    </div>
                  </td>

                  <!-- Day cells -->
                  <td
                    v-for="day in days"
                    :key="day"
                    :class="[
                      'px-2 py-2 border-b border-l align-top',
                      isToday(day) ? 'border-emerald-100 bg-emerald-50/30' : 'border-slate-100'
                    ]"
                  >
                    <div
                      v-if="getLesson(day, time)"
                      class="rounded-xl p-3 h-full transition-all duration-200 hover:scale-[1.02] hover:shadow-md cursor-default relative overflow-hidden group"
                      :style="{
                        backgroundColor: getColor(getLesson(day, time).subject).ultra,
                        borderLeft: `3px solid ${getColor(getLesson(day, time).subject).main}`
                      }"
                    >
                      <!-- Decorative corner -->
                      <div class="absolute top-0 right-0 w-8 h-8 opacity-10 rounded-bl-xl"
                        :style="{ backgroundColor: getColor(getLesson(day, time).subject).main }"
                      ></div>

                      <p class="font-bold text-slate-800 text-[13px] leading-snug mb-2 pr-4">
                        {{ getLesson(day, time).subject }}
                      </p>
                      <div class="space-y-1">
                        <div v-if="getLesson(day, time).teacher" class="flex items-center gap-1.5 text-[11px] text-slate-500">
                          <User class="w-3 h-3 flex-shrink-0" :style="{ color: getColor(getLesson(day, time).subject).main }" />
                          <span class="truncate">{{ getLesson(day, time).teacher }}</span>
                        </div>
                        <div v-if="getLesson(day, time).room" class="flex items-center gap-1.5 text-[11px] text-slate-500">
                          <MapPin class="w-3 h-3 flex-shrink-0" :style="{ color: getColor(getLesson(day, time).subject).main }" />
                          <span class="truncate">{{ getLesson(day, time).room }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Empty cell indicator -->
                    <div v-else class="h-full min-h-[80px] flex items-center justify-center">
                      <div class="w-1.5 h-1.5 rounded-full bg-slate-200"></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Legend -->
        <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
          <div class="flex items-center gap-2 mb-4">
            <Palette class="w-4 h-4 text-slate-400" />
            <h3 class="text-sm font-bold text-slate-700">{{ $t('schedule.subject') }}</h3>
            <span class="text-xs text-slate-400 ml-1">({{ uniqueSubjects.length }} {{ $t('schedule.subjectsCount') }})</span>
          </div>
          <div class="flex flex-wrap gap-2.5">
            <div
              v-for="subject in uniqueSubjects"
              :key="subject"
              class="flex items-center gap-2 px-3 py-2 rounded-xl transition-colors hover:shadow-sm"
              :style="{ backgroundColor: getColor(subject).ultra }"
            >
              <span
                class="w-3 h-3 rounded-full flex-shrink-0 ring-1 ring-offset-1"
                :style="{
                  backgroundColor: getColor(subject).main,
                  ringColor: getColor(subject).light
                }"
              ></span>
              <span class="text-sm font-medium text-slate-700">{{ subject }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { CalendarDays, Clock, Coffee, MapPin, Palette, PartyPopper, User } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const authStore = useAuthStore()
const toast = useToastStore()
const { t } = useLanguageStore()

const activeView = ref('weekly')
const days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']

// Default time slots (used as fallback if no schedule data)
const DEFAULT_SLOTS = ['08:30-09:50', '10:00-11:20', '12:00-13:20', '13:30-14:50', '15:00-16:20', '16:30-17:50', '18:00-19:20']

const loading = ref(false)
const schedule = ref([])
const activeHolidays = ref([])

// Dynamic timeSlots: build from actual schedule data
const timeSlots = computed(() => {
  const slotSet = new Map() // key: startTime -> full range
  schedule.value.forEach(s => {
    if (!s.time) return
    const start = s.time.split('-')[0]?.trim()
    if (start && !slotSet.has(start)) {
      slotSet.set(start, s.time)
    }
  })
  if (slotSet.size === 0) return DEFAULT_SLOTS
  // Sort by start time
  return [...slotSet.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([, range]) => range)
})

// ============ DYNAMIC COLOR PALETTE ============
// 18 vivid, visually distinct colors for auto-assignment to any subject
const COLOR_PALETTE = [
  { main: '#10b981', light: '#a7f3d0', ultra: '#ecfdf5' }, // emerald
  { main: '#3b82f6', light: '#bfdbfe', ultra: '#eff6ff' }, // blue
  { main: '#8b5cf6', light: '#c4b5fd', ultra: '#f5f3ff' }, // violet
  { main: '#f59e0b', light: '#fde68a', ultra: '#fffbeb' }, // amber
  { main: '#ef4444', light: '#fca5a5', ultra: '#fef2f2' }, // red
  { main: '#06b6d4', light: '#a5f3fc', ultra: '#ecfeff' }, // cyan
  { main: '#ec4899', light: '#f9a8d4', ultra: '#fdf2f8' }, // pink
  { main: '#f97316', light: '#fdba74', ultra: '#fff7ed' }, // orange
  { main: '#6366f1', light: '#a5b4fc', ultra: '#eef2ff' }, // indigo
  { main: '#14b8a6', light: '#99f6e4', ultra: '#f0fdfa' }, // teal
  { main: '#84cc16', light: '#bef264', ultra: '#f7fee7' }, // lime
  { main: '#a855f7', light: '#d8b4fe', ultra: '#faf5ff' }, // purple
  { main: '#e11d48', light: '#fda4af', ultra: '#fff1f2' }, // rose
  { main: '#0ea5e9', light: '#7dd3fc', ultra: '#f0f9ff' }, // sky
  { main: '#d946ef', light: '#f0abfc', ultra: '#fdf4ff' }, // fuchsia
  { main: '#65a30d', light: '#a3e635', ultra: '#f7fee7' }, // green
  { main: '#0891b2', light: '#67e8f9', ultra: '#ecfeff' }, // dark cyan
  { main: '#c026d3', light: '#e879f9', ultra: '#fdf4ff' }, // magenta
]

const subjectColorMap = ref({})

const getColor = (subject) => {
  if (!subject) return COLOR_PALETTE[0]
  if (subjectColorMap.value[subject]) return subjectColorMap.value[subject]

  // Auto-assign next color from palette
  const usedCount = Object.keys(subjectColorMap.value).length
  const color = COLOR_PALETTE[usedCount % COLOR_PALETTE.length]
  subjectColorMap.value[subject] = color
  return color
}

// Load schedule on mount
onMounted(async () => {
  await loadSchedule()
  // Load active holidays
  try {
    activeHolidays.value = await api.getActiveHolidays() || []
  } catch (e) {
    console.error('Load holidays error:', e)
  }
})

async function loadSchedule() {
  loading.value = true
  
  // English -> Uzbek day mapping
  const dayMap = {
    'monday': 'Dushanba', 'tuesday': 'Seshanba', 'wednesday': 'Chorshanba',
    'thursday': 'Payshanba', 'friday': 'Juma', 'saturday': 'Shanba', 'sunday': 'Yakshanba'
  }
  
  try {
    const groupId = authStore.user?.groupId || authStore.user?.group_id
    if (groupId) {
      const response = await api.getScheduleByGroup(groupId)
      
      let items = []
      if (Array.isArray(response)) {
        items = response
      } else if (response?.data && Array.isArray(response.data)) {
        items = response.data
      } else if (response?.items && Array.isArray(response.items)) {
        items = response.items
      } else if (response?.schedule && Array.isArray(response.schedule)) {
        items = response.schedule
      } else if (typeof response === 'object') {
        for (const [eng, uz] of Object.entries(dayMap)) {
          if (response[eng] && Array.isArray(response[eng])) {
            response[eng].forEach(s => {
              items.push({ ...s, day: uz })
            })
          }
        }
      }
      
      schedule.value = items
        .filter(s => !s.is_cancelled)
        .map(s => {
        let timeStr = ''
        if (s.time_range) {
          timeStr = s.time_range.replace(/\s/g, '')
        } else if (s.time) {
          timeStr = s.time.replace(/\s/g, '')
        } else if (s.start_time && s.end_time) {
          const st = s.start_time.substring(0, 5)
          const et = s.end_time.substring(0, 5)
          timeStr = `${st}-${et}`
        }
        // Remove seconds if present (HH:MM:SS -> HH:MM)
        timeStr = timeStr.replace(/(\d{2}:\d{2}):\d{2}/g, '$1')

        // Build location: combine building + room
        const building = s.building || ''
        const room = s.room || s.classroom || ''
        const location = s.location || (building && room ? `${building}, ${room}` : building || room) || ''

        return {
          id: s.id,
          day: s.day || dayMap[s.day_of_week] || s.day_of_week || '',
          time: timeStr,
          subject: s.subject || s.subject_name || '',
          teacher: s.teacher || s.teacher_name || '',
          room: location,
          building: building,
          lessonNumber: s.lesson_number || null,
          groupId: s.group_id
        }
      })

      // Pre-assign colors in consistent order (sort subjects alphabetically)
      const subjects = [...new Set(schedule.value.map(s => s.subject).filter(Boolean))].sort()
      subjects.forEach(s => getColor(s))
    }
  } catch (err) {
    console.error('Load schedule error:', err)
    toast.error(t('schedule.loadError'))
  } finally {
    loading.value = false
  }
}

const currentDayName = computed(() => {
  const dayNames = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  return dayNames[new Date().getDay()]
})

const todayFormatted = computed(() => {
  return new Date().toLocaleDateString('uz-UZ', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
})

const todaySchedule = computed(() => {
  return schedule.value
    .filter(s => s.day === currentDayName.value)
    .sort((a, b) => {
      const tA = a.time.split('-')[0] || ''
      const tB = b.time.split('-')[0] || ''
      return tA.localeCompare(tB)
    })
})

const uniqueSubjects = computed(() => {
  return [...new Set(schedule.value.map(s => s.subject).filter(Boolean))].sort()
})

const isToday = (day) => day === currentDayName.value

const getLesson = (day, time) => {
  const slotStart = time.split('-')[0]?.trim()
  return schedule.value.find(s => {
    if (s.day !== day) return false
    const lessonStart = (s.time || '').split('-')[0]?.trim()
    return s.time === time || lessonStart === slotStart
  })
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
