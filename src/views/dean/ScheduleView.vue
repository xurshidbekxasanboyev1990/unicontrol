<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Dars jadvali</h1>
        <p class="text-sm text-slate-500">Guruhlar bo'yicha dars jadvali (faqat ko'rish)</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Faculty filter -->
        <select v-model="filterFaculty" @change="onFacultyChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha fakultetlar</option>
          <option v-for="f in faculties" :key="f" :value="f">{{ f }}</option>
        </select>

        <!-- Course filter -->
        <select v-model="filterCourse" @change="onCourseChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha kurslar</option>
          <option v-for="c in courseYears" :key="c" :value="c">{{ c }}-kurs</option>
        </select>

        <!-- Group filter -->
        <select v-model="selectedGroupId" @change="loadSchedule" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Guruh tanlang</option>
          <option v-for="group in filteredGroups" :key="group.id" :value="group.id">{{ group.name }}</option>
        </select>

        <!-- Teacher search -->
        <div class="relative">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchTeacher"
            type="text"
            placeholder="O'qituvchi qidirish..."
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm"
            @input="debouncedSearch"
          />
        </div>
      </div>

      <!-- Active filters -->
      <div v-if="hasActiveFilters" class="mt-3 flex items-center gap-2 flex-wrap">
        <span class="text-xs text-slate-500">Filtrlar:</span>
        <span v-if="filterFaculty" class="inline-flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-xs">
          {{ filterFaculty }}
          <button @click="filterFaculty = ''; onFacultyChange()" class="hover:text-emerald-900">
            <X class="w-3 h-3" />
          </button>
        </span>
        <span v-if="filterCourse" class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs">
          {{ filterCourse }}-kurs
          <button @click="filterCourse = ''; onCourseChange()" class="hover:text-blue-900">
            <X class="w-3 h-3" />
          </button>
        </span>
        <span v-if="selectedGroupId" class="inline-flex items-center gap-1 px-2 py-1 bg-violet-100 text-violet-700 rounded-lg text-xs">
          {{ selectedGroupName }}
          <button @click="selectedGroupId = ''; loadSchedule()" class="hover:text-violet-900">
            <X class="w-3 h-3" />
          </button>
        </span>
        <button @click="clearAllFilters" class="text-xs text-rose-500 hover:text-rose-700 underline ml-2">Tozalash</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- No Group Selected -->
    <div v-else-if="!selectedGroupId" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <Calendar class="w-16 h-16 text-slate-300 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-slate-600 mb-2">Guruh tanlang</h3>
      <p class="text-sm text-slate-500">Jadvalni ko'rish uchun fakultet, kurs va guruhni tanlang</p>
    </div>

    <!-- Schedule Grid -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-4 border-b border-slate-100 bg-slate-50">
        <h3 class="font-semibold text-slate-700">{{ selectedGroupName }} — Dars jadvali</h3>
        <p class="text-xs text-slate-500 mt-0.5">{{ schedule.length }} ta dars topildi</p>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[900px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap w-20">Vaqt</th>
              <th v-for="day in weekDays" :key="day.key" class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap" :class="{ 'bg-emerald-50': isToday(day.key) }">
                {{ day.label }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="slot in timeSlots" :key="slot" class="hover:bg-slate-50/50 transition-colors">
              <td class="p-3 sm:p-4 text-sm font-medium text-slate-600 whitespace-nowrap">{{ slot }}</td>
              <td v-for="day in weekDays" :key="day.key" class="p-2" :class="{ 'bg-emerald-50/50': isToday(day.key) }">
                <div v-if="getLesson(day.key, slot)" class="p-2 rounded-xl text-xs" :class="lessonBg(getLesson(day.key, slot))">
                  <p class="font-semibold text-slate-800 truncate">{{ getLesson(day.key, slot).subject }}</p>
                  <p class="text-slate-500 mt-0.5 truncate">{{ getLesson(day.key, slot).teacher_name }}</p>
                  <p class="text-slate-400 mt-0.5">{{ getLesson(day.key, slot).room || '' }}</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="schedule.length === 0 && selectedGroupId" class="p-12 text-center">
        <Calendar class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Bu guruh uchun jadval topilmadi</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Calendar, Loader2, Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const allGroups = ref([])
const faculties = ref([])
const schedule = ref([])
const selectedGroupId = ref('')
const filterFaculty = ref('')
const filterCourse = ref('')
const searchTeacher = ref('')

const courseYears = [1, 2, 3, 4]

const weekDays = [
  { key: 'monday', label: 'Dushanba' },
  { key: 'tuesday', label: 'Seshanba' },
  { key: 'wednesday', label: 'Chorshanba' },
  { key: 'thursday', label: 'Payshanba' },
  { key: 'friday', label: 'Juma' },
  { key: 'saturday', label: 'Shanba' }
]

const timeSlots = [
  '08:30-09:50',
  '10:00-11:20',
  '11:30-12:50',
  '13:30-14:50',
  '15:00-16:20',
  '16:30-17:50'
]

// Filter groups based on selected faculty and course
const filteredGroups = computed(() => {
  let g = allGroups.value
  if (filterFaculty.value) {
    g = g.filter(gr => gr.faculty === filterFaculty.value)
  }
  if (filterCourse.value) {
    g = g.filter(gr => gr.course_year === Number(filterCourse.value))
  }
  return g
})

const selectedGroupName = computed(() => {
  if (!selectedGroupId.value) return ''
  const g = allGroups.value.find(gr => gr.id === Number(selectedGroupId.value))
  return g ? g.name : ''
})

const hasActiveFilters = computed(() => {
  return filterFaculty.value || filterCourse.value || selectedGroupId.value
})

const isToday = (dayKey) => {
  const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
  return days[new Date().getDay()] === dayKey
}

const lessonBg = (lesson) => {
  if (!lesson) return ''
  const types = {
    lecture: 'bg-blue-50 border border-blue-200',
    practice: 'bg-emerald-50 border border-emerald-200',
    lab: 'bg-violet-50 border border-violet-200',
    seminar: 'bg-amber-50 border border-amber-200'
  }
  return types[lesson.schedule_type] || 'bg-slate-50 border border-slate-200'
}

const getLesson = (dayKey, timeSlot) => {
  return schedule.value.find(s => {
    const dayMatch = s.day_of_week?.toLowerCase() === dayKey
    // Compare time_range with or without spaces around dash
    const normalizedTimeRange = (s.time_range || '').replace(/\s/g, '')
    const normalizedSlot = timeSlot.replace(/\s/g, '')
    const timeMatch = normalizedTimeRange === normalizedSlot ||
      (s.start_time && s.end_time && `${s.start_time}-${s.end_time}`.replace(/\s/g, '') === normalizedSlot)
    return dayMatch && timeMatch
  })
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadSchedule()
  }, 400)
}

const onFacultyChange = () => {
  selectedGroupId.value = ''
  schedule.value = []
}

const onCourseChange = () => {
  selectedGroupId.value = ''
  schedule.value = []
}

const clearAllFilters = () => {
  filterFaculty.value = ''
  filterCourse.value = ''
  selectedGroupId.value = ''
  searchTeacher.value = ''
  schedule.value = []
}

const loadSchedule = async () => {
  if (!selectedGroupId.value) {
    schedule.value = []
    return
  }
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('group_id', selectedGroupId.value)
    if (searchTeacher.value) params.append('teacher', searchTeacher.value)
    const resp = await api.get(`/dean/schedule?${params}`)
    schedule.value = resp.items || resp.schedule || resp || []
  } catch (err) {
    console.error('Dean schedule error:', err)
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  try {
    const resp = await api.get('/dean/groups')
    allGroups.value = resp.items || resp.groups || resp || []
  } catch (err) {
    console.error('Dean groups error:', err)
  }
}

const loadFaculties = async () => {
  try {
    const resp = await api.get('/dean/faculties')
    faculties.value = resp.faculties || resp || []
  } catch (err) {
    console.error('Dean faculties error:', err)
  }
}

onMounted(() => {
  loadGroups()
  loadFaculties()
})
</script>
