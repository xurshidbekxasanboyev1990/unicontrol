<template>
  <div class="space-y-6">
    <!-- Header with View Toggle -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Dars jadvali</h1>
        <p class="text-slate-500">SE-401 guruh jadvali</p>
      </div>
      <div class="flex items-center bg-slate-100 rounded-xl p-1">
        <button 
          @click="viewMode = 'week'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="viewMode === 'week' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'"
        >
          Haftalik
        </button>
        <button 
          @click="viewMode = 'today'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="viewMode === 'today' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'"
        >
          Bugungi
        </button>
      </div>
    </div>

    <!-- Today View -->
    <template v-if="viewMode === 'today'">
      <div class="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-emerald-100">{{ formattedDate }}</p>
            <h2 class="text-2xl font-bold mt-1">{{ todayName }}</h2>
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
            <h3 class="font-semibold text-slate-800">{{ lesson.subject }}</h3>
            <p class="text-sm text-slate-500 flex items-center gap-2 mt-1">
              <User class="w-4 h-4" />
              {{ lesson.teacher }}
            </p>
          </div>

          <div class="text-right">
            <p class="font-medium text-slate-800 flex items-center gap-2">
              <Clock class="w-4 h-4 text-emerald-500" />
              {{ lesson.time }}
            </p>
            <p class="text-sm text-slate-500 flex items-center gap-2 mt-1">
              <MapPin class="w-4 h-4" />
              {{ lesson.room }}
            </p>
          </div>
        </div>

        <div v-if="todayLessons.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <Coffee class="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p class="text-lg font-medium text-slate-600">Bugun dars yo'q</p>
          <p class="text-sm text-slate-400 mt-1">Dam oling va keyingi kunga tayyorlaning</p>
        </div>
      </div>
    </template>

    <!-- Week View -->
    <template v-else>
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="grid grid-cols-6 border-b border-slate-100">
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
          class="grid grid-cols-6 border-b border-slate-100 last:border-0"
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
              class="p-2 rounded-lg text-white text-sm h-full"
              :class="getSubjectColor(getLessonAt(day, timeSlot).subject)"
            >
              <p class="font-medium truncate">{{ getLessonAt(day, timeSlot).subject }}</p>
              <p class="text-xs opacity-80 truncate">{{ getLessonAt(day, timeSlot).room }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap items-center gap-4 text-sm">
        <span class="text-slate-500">Fanlar:</span>
        <div v-for="(color, subject) in subjectColorMap" :key="subject" class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full" :class="color"></span>
          <span class="text-slate-600">{{ subject }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../../stores/data'
import {
  CalendarDays,
  User,
  Clock,
  MapPin,
  Coffee
} from 'lucide-vue-next'

const dataStore = useDataStore()
const viewMode = ref('week')

const weekDays = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma']
const timeSlots = ['08:30', '10:00', '11:30', '14:00', '15:30']

const subjectColors = [
  'bg-gradient-to-br from-blue-500 to-blue-600',
  'bg-gradient-to-br from-violet-500 to-violet-600',
  'bg-gradient-to-br from-emerald-500 to-emerald-600',
  'bg-gradient-to-br from-orange-500 to-orange-600',
  'bg-gradient-to-br from-rose-500 to-rose-600'
]

const subjectColorMap = computed(() => {
  const subjects = [...new Set(dataStore.schedule.map(s => s.subject))]
  const colors = ['bg-blue-500', 'bg-violet-500', 'bg-emerald-500', 'bg-orange-500', 'bg-rose-500']
  return subjects.reduce((acc, subject, index) => {
    acc[subject] = colors[index % colors.length]
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
  
  return dataStore.schedule.filter(s => s.day === dayName).sort((a, b) => {
    return a.time.localeCompare(b.time)
  })
})

const isToday = (day) => {
  const days = ['', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  return days[new Date().getDay()] === day
}

const getLessonAt = (day, time) => {
  return dataStore.schedule.find(s => s.day === day && s.time === time)
}

const getSubjectColor = (subject) => {
  const subjects = [...new Set(dataStore.schedule.map(s => s.subject))]
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
</script>
