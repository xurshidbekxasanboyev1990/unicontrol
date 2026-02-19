<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-indigo-600 to-blue-600 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <CalendarClock :size="28" />
        <h1 class="text-xl font-bold">{{ t('teacher.workload') }}</h1>
      </div>
      <p class="text-indigo-100 text-sm">{{ t('teacher.workloadDescription') }}</p>
    </div>

    <!-- Search & Filter -->
    <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
      <div class="flex flex-wrap gap-3">
        <!-- Teacher search with autocomplete -->
        <div class="flex-1 min-w-[240px] relative" ref="searchContainerRef">
          <div class="relative">
            <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              v-model="searchQuery"
              type="text"
              class="w-full rounded-xl border border-gray-200 pl-10 pr-9 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              :placeholder="t('teacher.searchByName')"
              @input="onSearchInput"
              @keyup.enter="selectFirstSuggestion"
              @focus="showSuggestions = true"
            />
            <button v-if="searchQuery" @click="clearSearch" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <X :size="14" />
            </button>
          </div>
          <!-- Autocomplete dropdown -->
          <div v-if="showSuggestions && filteredTeachers.length > 0 && searchQuery.length >= 2"
            class="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-[240px] overflow-y-auto">
            <button
              v-for="teacher in filteredTeachers.slice(0, 15)"
              :key="teacher.name"
              class="w-full px-4 py-2.5 text-left hover:bg-indigo-50 flex items-center gap-3 border-b border-gray-50 last:border-0"
              @mousedown.prevent="selectTeacher(teacher)"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex-shrink-0">
                {{ teacher.name.charAt(0) }}
              </div>
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ teacher.name }}</p>
                <p class="text-xs text-gray-500 truncate">{{ teacher.department }}</p>
              </div>
              <span v-if="teacher.type" class="ml-auto text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full flex-shrink-0">{{ teacher.type }}</span>
            </button>
          </div>
        </div>

        <!-- Department filter -->
        <select
          v-model="selectedDepartment"
          class="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          @change="onDepartmentChange"
        >
          <option value="">{{ t('teacher.allDepartments') }}</option>
          <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-indigo-500" />
    </div>

    <!-- Selected Teacher Workload -->
    <div v-else-if="selectedTeacherData.length > 0" class="space-y-4">
      <!-- Back button -->
      <button @click="backToList" class="flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-700 font-medium">
        <ChevronLeft :size="16" />
        {{ t('common.back') || 'Orqaga' }}
      </button>

      <!-- Teacher Info Card -->
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-lg font-bold">
              {{ selectedTeacherName.charAt(0) }}
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ selectedTeacherName }}</h3>
              <p class="text-sm text-gray-500">
                <span v-if="selectedTeacherDept" class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full text-xs">{{ selectedTeacherDept }}</span>
                <span v-if="selectedTeacherType" class="ml-1 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">{{ selectedTeacherType }}</span>
              </p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold text-indigo-600">{{ selectedTeacherData.length }}</p>
            <p class="text-xs text-gray-500">{{ t('teacher.totalLessonsWeek') }}</p>
          </div>
        </div>

        <!-- Weekly Grid -->
        <div class="space-y-3">
          <div v-for="day in weekDays" :key="day.value">
            <div v-if="getDayLessons(day.value).length > 0" class="rounded-xl border border-gray-100 overflow-hidden">
              <div :class="['flex items-center gap-2 px-4 py-2', isToday(day.value) ? 'bg-indigo-50' : 'bg-gray-50']">
                <div :class="['flex h-7 w-7 items-center justify-center rounded-lg text-white text-xs font-bold', isToday(day.value) ? 'bg-indigo-600' : 'bg-gray-400']">
                  {{ day.short }}
                </div>
                <span :class="['text-sm font-semibold', isToday(day.value) ? 'text-indigo-700' : 'text-gray-700']">
                  {{ day.label }}
                </span>
                <span v-if="isToday(day.value)" class="text-[10px] bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded-full">{{ t('teacher.today') || 'Bugun' }}</span>
                <span class="ml-auto text-xs text-gray-400">{{ getDayLessons(day.value).length }} {{ t('teacher.lessons') || 'dars' }}</span>
              </div>
              <div class="divide-y divide-gray-50">
                <div
                  v-for="lesson in getDayLessons(day.value)"
                  :key="lesson.id"
                  :class="['flex items-center gap-3 px-4 py-2.5', lesson.is_busy ? 'bg-red-50' : 'hover:bg-gray-50']"
                >
                  <div class="flex flex-col items-center justify-center min-w-[52px]">
                    <span class="text-xs font-medium text-gray-700">{{ lesson.start_time }}</span>
                    <span class="text-[10px] text-gray-400">{{ lesson.end_time }}</span>
                  </div>
                  <div :class="['w-1 h-8 rounded-full', lesson.is_busy ? 'bg-red-400' : 'bg-indigo-400']"></div>
                  <div class="flex-1 min-w-0">
                    <p v-if="lesson.is_busy" class="text-sm font-medium text-red-600">BAND</p>
                    <p v-else class="text-sm font-medium text-gray-900 truncate">{{ lesson.groups }}</p>
                  </div>
                  <span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                    {{ lesson.lesson_number }}-{{ t('teacher.para') }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Teacher List (default view) -->
    <div v-else class="rounded-2xl bg-white shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <Users :size="16" />
          {{ t('teacher.allTeachersList') || "O'qituvchilar ro'yxati" }}
        </h3>
        <span class="text-xs text-gray-400">{{ filteredList.length }} {{ t('teacher.teachersCount') || "o'qituvchi" }}</span>
      </div>
      <div v-if="filteredList.length === 0 && !loading" class="px-5 py-12 text-center">
        <SearchX :size="40" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm text-gray-500">{{ t('teacher.noWorkloadFound') }}</p>
      </div>
      <div v-else class="divide-y divide-gray-50">
        <button
          v-for="teacher in displayedTeachers"
          :key="teacher.name"
          class="w-full px-5 py-3 text-left hover:bg-indigo-50 flex items-center gap-3 transition-colors"
          @click="selectTeacher(teacher)"
        >
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 text-sm font-bold flex-shrink-0">
            {{ teacher.name.charAt(0) }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">{{ teacher.name }}</p>
            <p class="text-xs text-gray-500 truncate">{{ teacher.department }}</p>
          </div>
          <span v-if="teacher.type" class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full flex-shrink-0">{{ teacher.type }}</span>
          <ChevronRight :size="14" class="text-gray-400 flex-shrink-0" />
        </button>
      </div>
      <!-- Numeric Pagination -->
      <div v-if="totalPages > 1" class="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
        <span class="text-xs text-gray-400">{{ (currentPage - 1) * perPage + 1 }}–{{ Math.min(currentPage * perPage, filteredList.length) }} / {{ filteredList.length }}</span>
        <div class="flex items-center gap-1">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            :class="['h-8 w-8 flex items-center justify-center rounded-lg text-sm transition-colors', currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100']"
          >
            <ChevronLeft :size="14" />
          </button>
          <template v-for="page in paginationPages" :key="page">
            <span v-if="page === '....'" class="h-8 w-8 flex items-center justify-center text-xs text-gray-400">...</span>
            <button
              v-else
              @click="goToPage(page)"
              :class="['h-8 w-8 flex items-center justify-center rounded-lg text-sm font-medium transition-colors', page === currentPage ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100']"
            >
              {{ page }}
            </button>
          </template>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            :class="['h-8 w-8 flex items-center justify-center rounded-lg text-sm transition-colors', currentPage === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100']"
          >
            <ChevronRight :size="14" />
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { CalendarClock, ChevronLeft, ChevronRight, Loader2, Search, SearchX, Users, X } from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(false)
const toast = ref(null)
const showSuggestions = ref(false)
const currentPage = ref(1)
const perPage = 20
const searchContainerRef = ref(null)

// All teachers list
const allTeachers = ref([])
const departments = ref([])

// Search
const searchQuery = ref('')
const selectedDepartment = ref('')

// Selected teacher workload
const selectedTeacherData = ref([])
const selectedTeacherName = ref('')
const selectedTeacherDept = ref('')
const selectedTeacherType = ref('')

const weekDays = [
  { value: 'monday', short: 'Du', label: t('schedule.monday') || 'Dushanba' },
  { value: 'tuesday', short: 'Se', label: t('schedule.tuesday') || 'Seshanba' },
  { value: 'wednesday', short: 'Ch', label: t('schedule.wednesday') || 'Chorshanba' },
  { value: 'thursday', short: 'Pa', label: t('schedule.thursday') || 'Payshanba' },
  { value: 'friday', short: 'Ju', label: t('schedule.friday') || 'Juma' },
  { value: 'saturday', short: 'Sh', label: t('schedule.saturday') || 'Shanba' },
]

const isToday = (dayValue) => {
  const dayMap = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
  return dayMap[new Date().getDay()] === dayValue
}

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const getDayLessons = (dayValue) => {
  return selectedTeacherData.value.filter(w => w.day_of_week === dayValue)
}

// Filtered teachers for autocomplete
const filteredTeachers = computed(() => {
  if (!searchQuery.value || searchQuery.value.length < 2) return []
  const q = searchQuery.value.toLowerCase()
  return allTeachers.value.filter(t =>
    t.name.toLowerCase().includes(q)
  )
})

// Filtered list (by department + search)
const filteredList = computed(() => {
  let list = allTeachers.value
  if (selectedDepartment.value) {
    list = list.filter(t => t.department === selectedDepartment.value)
  }
  if (searchQuery.value && searchQuery.value.length >= 2) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(t => t.name.toLowerCase().includes(q))
  }
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredList.value.length / perPage)))

// Paginated teachers
const displayedTeachers = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredList.value.slice(start, start + perPage)
})

// Smart pagination pages: 1 ... 4 5 6 ... 10
const paginationPages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = []
  pages.push(1)
  if (cur > 3) pages.push('....')
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) {
    pages.push(i)
  }
  if (cur < total - 2) pages.push('....')
  pages.push(total)
  return pages
})

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

const onSearchInput = () => {
  showSuggestions.value = true
  currentPage.value = 1
  if (selectedTeacherData.value.length > 0) {
    selectedTeacherData.value = []
    selectedTeacherName.value = ''
  }
}

const selectFirstSuggestion = () => {
  if (filteredTeachers.value.length > 0) {
    selectTeacher(filteredTeachers.value[0])
  }
}

const selectTeacher = async (teacher) => {
  showSuggestions.value = false
  searchQuery.value = teacher.name
  selectedTeacherName.value = teacher.name
  selectedTeacherDept.value = teacher.department || ''
  selectedTeacherType.value = teacher.type || ''

  loading.value = true
  try {
    const res = await api.request(`/teacher/workload?search=${encodeURIComponent(teacher.name)}`)
    selectedTeacherData.value = (res.items || []).filter(i => i.teacher_name === teacher.name)
  } catch (e) {
    console.error('Workload error:', e)
    showToast(t('common.error') || 'Xatolik', 'error')
  } finally {
    loading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  selectedTeacherData.value = []
  selectedTeacherName.value = ''
  showSuggestions.value = false
}

const backToList = () => {
  searchQuery.value = ''
  selectedTeacherData.value = []
  selectedTeacherName.value = ''
}

const onDepartmentChange = () => {
  selectedTeacherData.value = []
  selectedTeacherName.value = ''
  searchQuery.value = ''
  currentPage.value = 1
}

const loadTeachers = async () => {
  try {
    const res = await api.request('/teacher/workload/teachers')
    allTeachers.value = res.teachers || []
  } catch (e) {
    console.error('Teachers list error:', e)
  }
}

const loadDepartments = async () => {
  try {
    const res = await api.request('/teacher/workload/departments')
    departments.value = res.departments || []
  } catch (e) {
    console.error('Departments error:', e)
  }
}

// Try auto-detect my workload
const loadMyWorkload = async () => {
  try {
    const res = await api.request('/teacher/workload/my')
    if (res.items && res.items.length > 0) {
      selectedTeacherData.value = res.items
      selectedTeacherName.value = res.teacher_name || ''
      selectedTeacherDept.value = res.items[0]?.department || ''
      selectedTeacherType.value = res.items[0]?.teacher_type || ''
      searchQuery.value = res.teacher_name || ''
    }
  } catch (e) {
    // silently fail - not all users match a teacher
  }
}

// Close suggestions on outside click
const handleClickOutside = (e) => {
  if (searchContainerRef.value && !searchContainerRef.value.contains(e.target)) {
    showSuggestions.value = false
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([loadTeachers(), loadDepartments()])
  await loadMyWorkload()
  loading.value = false
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
