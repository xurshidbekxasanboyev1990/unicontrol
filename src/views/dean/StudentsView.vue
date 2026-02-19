<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Talabalar kontingenti</h1>
        <p class="text-sm text-slate-500">
          <span v-if="searching">Qidirilmoqda...</span>
          <span v-else>{{ totalItems }} ta talaba</span>
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <!-- Search -->
        <div class="relative lg:col-span-2">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Ism, ID, telefon..."
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm"
            @input="debouncedSearch"
          />
          <Loader2 v-if="searching" class="w-5 h-5 text-emerald-500 absolute right-3 top-1/2 -translate-y-1/2 animate-spin" />
        </div>

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
        <select v-model="filterGroupId" @change="onFilterChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha guruhlar</option>
          <option v-for="group in filteredGroups" :key="group.id" :value="group.id">{{ group.name }} ({{ group.students_count }})</option>
        </select>
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
        <span v-if="filterGroupId" class="inline-flex items-center gap-1 px-2 py-1 bg-violet-100 text-violet-700 rounded-lg text-xs">
          {{ selectedGroupName }}
          <button @click="filterGroupId = ''; onFilterChange()" class="hover:text-violet-900">
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

    <!-- Students Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">#</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Talaba</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">ID</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Guruh</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Telefon</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Kontrakt</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(student, idx) in students" :key="student.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-3 sm:p-4 text-sm text-slate-500">{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold">
                    {{ (student.name || 'T').charAt(0) }}
                  </div>
                  <span class="font-medium text-slate-800">{{ student.name }}</span>
                </div>
              </td>
              <td class="p-4 text-slate-600 text-sm">{{ student.student_id || '—' }}</td>
              <td class="p-4">
                <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium">
                  {{ student.group_name || '—' }}
                </span>
              </td>
              <td class="p-4 text-slate-600 text-sm">{{ student.phone || '—' }}</td>
              <td class="p-4">
                <span
                  class="px-3 py-1 rounded-lg text-sm font-medium"
                  :class="student.contract_paid > 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
                >
                  {{ student.contract_paid > 0 ? "To'langan" : "To'lanmagan" }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="students.length === 0" class="p-12 text-center">
        <UserX class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Talabalar topilmadi</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="p-3 sm:p-4 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div class="text-sm text-slate-500">
          {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalItems) }} / {{ totalItems }}
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          <template v-for="page in visiblePages" :key="page">
            <button
              @click="goToPage(page)"
              class="w-10 h-10 rounded-lg font-medium transition-colors"
              :class="currentPage === page ? 'bg-emerald-500 text-white' : 'hover:bg-slate-100'"
            >
              {{ page }}
            </button>
          </template>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight, Loader2, Search, UserX, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const searching = ref(false)
const students = ref([])
const allGroups = ref([])
const faculties = ref([])
const searchQuery = ref('')
const filterFaculty = ref('')
const filterCourse = ref('')
const filterGroupId = ref('')
const currentPage = ref(1)
const pageSize = 30
const totalItems = ref(0)

const courseYears = [1, 2, 3, 4]

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

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
  if (!filterGroupId.value) return ''
  const g = allGroups.value.find(gr => gr.id === Number(filterGroupId.value))
  return g ? g.name : ''
})

const hasActiveFilters = computed(() => {
  return filterFaculty.value || filterCourse.value || filterGroupId.value
})

let searchTimeout = null
const debouncedSearch = () => {
  searching.value = true
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadStudents()
  }, 400)
}

const onFacultyChange = () => {
  filterGroupId.value = ''
  currentPage.value = 1
  loadStudents()
}

const onCourseChange = () => {
  filterGroupId.value = ''
  currentPage.value = 1
  loadStudents()
}

const onFilterChange = () => {
  currentPage.value = 1
  loadStudents()
}

const clearAllFilters = () => {
  filterFaculty.value = ''
  filterCourse.value = ''
  filterGroupId.value = ''
  searchQuery.value = ''
  currentPage.value = 1
  loadStudents()
}

const loadStudents = async () => {
  loading.value = students.value.length === 0
  searching.value = true
  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('per_page', pageSize)
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterGroupId.value) params.append('group_id', filterGroupId.value)
    if (filterFaculty.value) params.append('faculty', filterFaculty.value)
    if (filterCourse.value) params.append('course_year', filterCourse.value)
    const resp = await api.get(`/dean/students?${params}`)
    students.value = resp.items || resp.students || []
    totalItems.value = resp.total || 0
  } catch (err) {
    console.error('Dean students error:', err)
  } finally {
    loading.value = false
    searching.value = false
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

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadStudents()
}

onMounted(() => {
  loadStudents()
  loadGroups()
  loadFaculties()
})
</script>
