<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Dars jadvali</h1>
        <p class="text-slate-500 mt-1">Haftalik dars jadvalingiz</p>
      </div>
      <div class="flex items-center gap-2 bg-white rounded-xl p-1 border border-slate-200">
        <button
          v-for="view in ['Hafta', 'Bugun']"
          :key="view"
          @click="activeView = view"
          :class="[
            'px-4 py-2 text-sm font-medium rounded-lg transition-all',
            activeView === view
              ? 'bg-emerald-500 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          ]"
        >
          {{ view }}
        </button>
      </div>
    </div>

    <!-- Today's Schedule (when Bugun selected) -->
    <div v-if="activeView === 'Bugun'" class="space-y-4">
      <div class="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
        <div class="flex items-center gap-3 mb-2">
          <CalendarDays class="w-5 h-5 opacity-80" />
          <span class="text-sm opacity-80">{{ todayFormatted }}</span>
        </div>
        <h2 class="text-2xl font-bold">{{ currentDayName }}</h2>
        <p class="text-emerald-100 mt-1">{{ todaySchedule.length }} ta dars</p>
      </div>

      <div v-if="todaySchedule.length > 0" class="space-y-3">
        <div
          v-for="(lesson, index) in todaySchedule"
          :key="lesson.id"
          class="bg-white rounded-xl p-4 border border-slate-200 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 w-16 text-center">
              <div class="text-lg font-bold text-slate-800">{{ lesson.time.split('-')[0] }}</div>
              <div class="text-xs text-slate-400">{{ lesson.time.split('-')[1] }}</div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span
                  class="w-2 h-2 rounded-full"
                  :class="getSubjectColor(lesson.subject)"
                ></span>
                <h3 class="font-semibold text-slate-800">{{ lesson.subject }}</h3>
              </div>
              <div class="flex items-center gap-4 text-sm text-slate-500">
                <span class="flex items-center gap-1">
                  <User class="w-4 h-4" />
                  {{ lesson.teacher }}
                </span>
                <span class="flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ lesson.room }}
                </span>
              </div>
            </div>
            <div
              class="px-3 py-1.5 rounded-lg text-xs font-medium"
              :class="index === 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'"
            >
              {{ index === 0 ? 'Keyingi' : `${index + 1}-dars` }}
            </div>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-xl p-12 border border-slate-200 text-center">
        <Coffee class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <h3 class="font-semibold text-slate-800 mb-1">Bugun dars yo'q</h3>
        <p class="text-slate-500 text-sm">Dam oling va keyingi darsga tayyorlaning</p>
      </div>
    </div>

    <!-- Weekly Schedule -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50">
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider w-24">
                Vaqt
              </th>
              <th
                v-for="day in days"
                :key="day"
                :class="[
                  'px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider min-w-[140px]',
                  isToday(day) ? 'text-emerald-600 bg-emerald-50' : 'text-slate-500'
                ]"
              >
                {{ day }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="time in timeSlots" :key="time">
              <td class="px-4 py-3 text-sm text-slate-500 font-medium whitespace-nowrap">
                {{ time }}
              </td>
              <td
                v-for="day in days"
                :key="day"
                :class="[
                  'px-2 py-2',
                  isToday(day) ? 'bg-emerald-50/50' : ''
                ]"
              >
                <div
                  v-if="getLesson(day, time)"
                  :class="[
                    'rounded-xl p-3 text-sm',
                    getLessonBgColor(getLesson(day, time).subject)
                  ]"
                >
                  <p class="font-semibold text-slate-800 mb-1">{{ getLesson(day, time).subject }}</p>
                  <div class="flex items-center gap-1 text-xs text-slate-500">
                    <User class="w-3 h-3" />
                    {{ getLesson(day, time).teacher }}
                  </div>
                  <div class="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                    <MapPin class="w-3 h-3" />
                    {{ getLesson(day, time).room }}
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Legend -->
    <div class="bg-white rounded-xl p-4 border border-slate-200">
      <h3 class="text-sm font-semibold text-slate-700 mb-3">Fanlar bo'yicha</h3>
      <div class="flex flex-wrap gap-3">
        <div v-for="subject in uniqueSubjects" :key="subject" class="flex items-center gap-2">
          <span
            class="w-3 h-3 rounded-full"
            :class="getSubjectColor(subject)"
          ></span>
          <span class="text-sm text-slate-600">{{ subject }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import api from '../../services/api'
import { CalendarDays, User, MapPin, Coffee } from 'lucide-vue-next'

const authStore = useAuthStore()
const toast = useToastStore()

const activeView = ref('Hafta')
const days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
const timeSlots = ['08:30-09:50', '10:00-11:20', '11:30-12:50', '14:00-15:20', '15:30-16:50']

const loading = ref(false)
const schedule = ref([])

// Load schedule on mount
onMounted(async () => {
  await loadSchedule()
})

async function loadSchedule() {
  loading.value = true
  try {
    // Try to get group's schedule
    const groupId = authStore.user?.groupId || authStore.user?.group_id
    if (groupId) {
      const response = await api.request(`/schedule/group/${groupId}`)
      if (Array.isArray(response)) {
        schedule.value = response.map(s => ({
          id: s.id,
          day: s.day,
          time: s.time,
          subject: s.subject,
          teacher: s.teacher,
          room: s.room,
          groupId: s.group_id
        }))
      } else if (response?.data) {
        schedule.value = response.data.map(s => ({
          id: s.id,
          day: s.day,
          time: s.time,
          subject: s.subject,
          teacher: s.teacher,
          room: s.room,
          groupId: s.group_id
        }))
      }
    }
  } catch (err) {
    console.error('Load schedule error:', err)
    // Fallback to general schedule
    try {
      const response = await api.getSchedule()
      if (Array.isArray(response)) {
        schedule.value = response
      } else if (response?.data) {
        schedule.value = response.data
      }
    } catch (e) {
      toast.error('Jadval yuklanmadi')
    }
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
  return schedule.value.filter(s => s.day === currentDayName.value)
})

const uniqueSubjects = computed(() => {
  return [...new Set(schedule.value.map(s => s.subject))]
})

const isToday = (day) => day === currentDayName.value

const getLesson = (day, time) => {
  return schedule.value.find(s => s.day === day && s.time === time)
}

const subjectColors = {
  'Matematika': 'bg-blue-500',
  'Dasturlash': 'bg-emerald-500',
  'Fizika': 'bg-purple-500',
  'Ingliz tili': 'bg-amber-500',
  'Algoritm': 'bg-rose-500',
  'Ma\'lumotlar bazasi': 'bg-cyan-500',
  'Web dasturlash': 'bg-indigo-500',
  'Jismoniy tarbiya': 'bg-orange-500',
  'Falsafa': 'bg-slate-500'
}

const subjectBgColors = {
  'Matematika': 'bg-blue-50 border border-blue-100',
  'Dasturlash': 'bg-emerald-50 border border-emerald-100',
  'Fizika': 'bg-purple-50 border border-purple-100',
  'Ingliz tili': 'bg-amber-50 border border-amber-100',
  'Algoritm': 'bg-rose-50 border border-rose-100',
  'Ma\'lumotlar bazasi': 'bg-cyan-50 border border-cyan-100',
  'Web dasturlash': 'bg-indigo-50 border border-indigo-100',
  'Jismoniy tarbiya': 'bg-orange-50 border border-orange-100',
  'Falsafa': 'bg-slate-100 border border-slate-200'
}

const getSubjectColor = (subject) => subjectColors[subject] || 'bg-slate-500'
const getLessonBgColor = (subject) => subjectBgColors[subject] || 'bg-slate-50 border border-slate-100'
</script>
