<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('students.title') }}</h1>
        <p class="text-sm text-slate-500">
          <span v-if="searching">{{ $t('common.loading') }}</span>
          <span v-else>{{ totalItems }} {{ $t('students.studentCount') }}</span>
        </p>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center justify-center gap-2"
      >
        <UserPlus class="w-5 h-5" />
        <span class="sm:inline hidden">{{ $t('students.addStudent') }}</span>
        <span class="sm:hidden">{{ $t('common.add') }}</span>
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4 space-y-3">
      <!-- Faculty tabs -->
      <div class="flex flex-wrap items-center gap-2">
        <label class="text-sm font-medium text-slate-600 whitespace-nowrap">Yo'nalish:</label>
        <button
          @click="selectFaculty('')"
          :class="[
            'rounded-lg px-3 py-1.5 text-sm font-medium transition-all border',
            !selectedFaculty
              ? 'bg-violet-600 text-white border-violet-600 shadow-sm'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
          ]"
        >
          Barchasi
          <span class="ml-1 text-xs opacity-70">({{ totalStudentCount }})</span>
        </button>
        <button
          v-for="fac in facultiesList"
          :key="fac.name"
          @click="selectFaculty(fac.name)"
          :class="[
            'rounded-lg px-3 py-1.5 text-sm font-medium transition-all border',
            selectedFaculty === fac.name
              ? 'bg-violet-600 text-white border-violet-600 shadow-sm'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
          ]"
        >
          {{ fac.short_name }}
          <span class="ml-1 text-xs opacity-70">({{ fac.students_count }})</span>
        </button>
      </div>

      <!-- Search + Course + Group -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="relative lg:col-span-2">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('common.search')"
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none text-sm"
            @input="debouncedSearch"
          />
          <Loader2 v-if="searching" class="w-5 h-5 text-violet-500 absolute right-3 top-1/2 -translate-y-1/2 animate-spin" />
        </div>

        <select v-model="filterCourse" @change="onCourseChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none text-sm">
          <option value="">Barcha kurslar</option>
          <option v-for="c in availableCourses" :key="c" :value="c">{{ c }}-kurs</option>
        </select>

        <select v-model="filterGroupId" @change="onFilterChange" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none text-sm">
          <option value="">{{ $t('common.all') }} guruhlar</option>
          <option v-for="group in filteredGroups" :key="group.id" :value="group.id">{{ group.name }} ({{ group.students_count || '' }})</option>
        </select>
      </div>

      <!-- Active filters -->
      <div v-if="hasActiveFilters" class="flex items-center gap-2 flex-wrap">
        <span class="text-xs text-slate-500">Filtrlar:</span>
        <span v-if="selectedFaculty" class="inline-flex items-center gap-1 px-2 py-1 bg-violet-100 text-violet-700 rounded-lg text-xs">
          {{ selectedFaculty }}
          <button @click="selectFaculty('')" class="hover:text-violet-900"><X class="w-3 h-3" /></button>
        </span>
        <span v-if="filterCourse" class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs">
          {{ filterCourse }}-kurs
          <button @click="filterCourse = ''; onCourseChange()" class="hover:text-blue-900"><X class="w-3 h-3" /></button>
        </span>
        <span v-if="filterGroupId" class="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-lg text-xs">
          {{ selectedGroupName }}
          <button @click="filterGroupId = ''; onFilterChange()" class="hover:text-amber-900"><X class="w-3 h-3" /></button>
        </span>
        <button @click="clearAllFilters" class="text-xs text-rose-500 hover:text-rose-700 underline ml-2">Tozalash</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
    </div>

    <!-- Students Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">#</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('students.student') }}</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">ID</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('students.group') }}</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('common.phone') }}</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('students.contract') }}</th>
              <th class="text-right p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(student, idx) in students" :key="student.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-3 sm:p-4 text-sm text-slate-500">{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white font-bold">
                    {{ (student.name || 'T').charAt(0) }}
                  </div>
                  <span class="font-medium text-slate-800">{{ student.name }}</span>
                </div>
              </td>
              <td class="p-4 text-slate-600">{{ student.studentId }}</td>
              <td class="p-4">
                <span class="px-3 py-1 bg-violet-100 text-violet-700 rounded-lg text-sm font-medium">
                  {{ student.group }}
                </span>
              </td>
              <td class="p-4 text-slate-600">{{ student.phone || '—' }}</td>
              <td class="p-4">
                <span
                  class="px-3 py-1 rounded-lg text-sm font-medium"
                  :class="student.contractPaid ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
                >
                  {{ student.contractPaid ? $t('students.paid') : $t('students.unpaid') }}
                </span>
              </td>
              <td class="p-4">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="openModal(student)"
                    class="p-2 text-slate-400 hover:text-violet-500 hover:bg-violet-50 rounded-lg transition-colors"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    @click="confirmDelete(student)"
                    class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="students.length === 0" class="p-12 text-center">
        <UserX class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">{{ $t('common.noResults') }}</p>
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
              :class="currentPage === page ? 'bg-violet-500 text-white' : 'hover:bg-slate-100'"
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

    <!-- Add/Edit Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800">
              {{ editingStudent ? $t('students.editStudent') : $t('students.addStudent') }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveStudent" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('students.name') }}</label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                :placeholder="$t('students.name')"
              />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('students.studentIdLabel') }}</label>
                <input
                  v-model="form.studentId"
                  type="text"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="S12345"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('students.group') }}</label>
                <select
                  v-model="form.group"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                >
                  <option value="">{{ $t('students.selectGroup') }}</option>
                  <option v-for="group in allGroups" :key="group.id" :value="group.name">
                    {{ group.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('common.phone') }}</label>
                <input
                  v-model="form.phone"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="+998..."
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('students.address') || 'Manzil' }}</label>
                <input
                  v-model="form.address"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                />
              </div>
            </div>
            <div class="flex items-center gap-3">
              <input v-model="form.contractPaid" type="checkbox" id="contractPaid" class="w-5 h-5 text-violet-500 border-slate-300 rounded focus:ring-violet-500/20" />
              <label for="contractPaid" class="text-sm text-slate-700">{{ $t('students.contractPaid') || "Kontrakt to'langan" }}</label>
            </div>
            <div class="flex justify-end gap-3 pt-4">
              <button type="button" @click="showModal = false" class="px-6 py-3 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors">
                {{ $t('common.cancel') }}
              </button>
              <button type="submit" class="px-6 py-3 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors">
                {{ $t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Delete Confirmation -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showDeleteConfirm = false"
      >
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 text-center">
          <AlertTriangle class="w-12 h-12 text-rose-500 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-slate-800 mb-2">{{ $t('students.deleteConfirm') || "O'chirilsinmi?" }}</h3>
          <p class="text-sm text-slate-500 mb-6">{{ deletingStudent?.name }}</p>
          <div class="flex justify-center gap-3">
            <button @click="showDeleteConfirm = false" class="px-6 py-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors">
              {{ $t('common.cancel') }}
            </button>
            <button @click="deleteStudent" class="px-6 py-2.5 bg-rose-500 text-white rounded-xl font-medium hover:bg-rose-600 transition-colors">
              {{ $t('common.delete') || "O'chirish" }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {
    AlertTriangle,
    ChevronLeft,
    ChevronRight,
    Loader2,
    Pencil,
    Search,
    Trash2,
    UserPlus,
    UserX,
    X
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useLanguageStore } from '../../stores/language'

const langStore = useLanguageStore()
const { t } = langStore
const dataStore = useDataStore()

const loading = ref(false)
const searching = ref(false)
const students = ref([])
const allGroups = ref([])
const facultiesList = ref([])
const selectedFaculty = ref('')
const searchQuery = ref('')
const filterCourse = ref('')
const filterGroupId = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingStudent = ref(null)
const deletingStudent = ref(null)

const currentPage = ref(1)
const pageSize = 50
const totalItems = ref(0)

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))
const totalStudentCount = computed(() => facultiesList.value.reduce((sum, f) => sum + f.students_count, 0))

const visiblePages = computed(() => {
  const pages = []
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const availableCourses = computed(() => {
  const courses = new Set()
  let g = allGroups.value
  if (selectedFaculty.value) g = g.filter(gr => gr.faculty === selectedFaculty.value)
  g.forEach(gr => { if (gr.course_year) courses.add(gr.course_year) })
  return [...courses].sort()
})

const filteredGroups = computed(() => {
  let g = allGroups.value
  if (selectedFaculty.value) g = g.filter(gr => gr.faculty === selectedFaculty.value)
  if (filterCourse.value) g = g.filter(gr => gr.course_year === Number(filterCourse.value))
  return g
})

const selectedGroupName = computed(() => {
  if (!filterGroupId.value) return ''
  const g = allGroups.value.find(gr => gr.id === Number(filterGroupId.value))
  return g ? g.name : ''
})

const hasActiveFilters = computed(() => selectedFaculty.value || filterCourse.value || filterGroupId.value)

function normalizeStudent(data) {
  return {
    id: data.id,
    name: data.full_name || data.name || t('common.unknown'),
    studentId: data.hemis_id || data.student_id || '',
    group: data.group_name || data.group || '',
    groupId: data.group_id,
    phone: data.phone,
    email: data.email,
    address: data.address,
    contractPaid: data.is_contract_paid || false,
    contractAmount: data.contract_amount || 0,
    isActive: data.is_active !== false
  }
}

const selectFaculty = (name) => {
  selectedFaculty.value = name
  filterGroupId.value = ''
  currentPage.value = 1
  loadStudents()
}

let searchTimer = null
const debouncedSearch = () => {
  searching.value = true
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadStudents()
  }, 400)
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
  selectedFaculty.value = ''
  filterCourse.value = ''
  filterGroupId.value = ''
  searchQuery.value = ''
  currentPage.value = 1
  loadStudents()
}

async function loadStudents(page) {
  loading.value = students.value.length === 0
  searching.value = true
  try {
    const params = {
      page: page || currentPage.value,
      page_size: pageSize
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (filterGroupId.value) params.group_id = filterGroupId.value
    if (selectedFaculty.value) params.faculty = selectedFaculty.value
    if (filterCourse.value) params.course_year = filterCourse.value

    const response = await api.getStudents(params)
    if (response.items) {
      students.value = response.items.map(normalizeStudent)
      totalItems.value = response.total
      currentPage.value = response.page || currentPage.value
    }
  } catch (err) {
    console.error('Failed to load students:', err)
  } finally {
    loading.value = false
    searching.value = false
  }
}

async function loadGroups() {
  try {
    await dataStore.fetchGroups({}, true)
    allGroups.value = dataStore.groups || []
  } catch (err) {
    console.error('Failed to load groups:', err)
  }
}

async function loadFaculties() {
  try {
    const resp = await api.request('/students/faculties')
    facultiesList.value = (resp.faculty_counts || []).map(f => ({
      ...f,
      short_name: f.name.length > 25 ? f.name.substring(0, 22) + '...' : f.name,
    }))
  } catch (err) {
    console.error('Failed to load faculties:', err)
  }
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadStudents(page)
}

onMounted(async () => {
  loading.value = true
  loadGroups()
  loadFaculties()
  loadStudents(1)
})

const form = reactive({
  name: '',
  studentId: '',
  group: '',
  phone: '',
  address: '',
  contractPaid: false
})

const openModal = (student = null) => {
  if (student) {
    editingStudent.value = student
    form.name = student.name
    form.studentId = student.studentId
    form.group = student.group
    form.phone = student.phone || ''
    form.address = student.address || ''
    form.contractPaid = student.contractPaid
  } else {
    editingStudent.value = null
    form.name = ''
    form.studentId = ''
    form.group = ''
    form.phone = ''
    form.address = ''
    form.contractPaid = false
  }
  showModal.value = true
}

const saveStudent = async () => {
  try {
    const group = allGroups.value.find(g => g.name === form.group)
    const groupId = group?.id

    const studentData = {
      full_name: form.name,
      hemis_id: form.studentId,
      group_id: groupId,
      phone: form.phone,
      address: form.address,
      is_contract_paid: form.contractPaid
    }

    if (editingStudent.value) {
      await api.updateStudent(editingStudent.value.id, studentData)
      const index = students.value.findIndex(s => s.id === editingStudent.value.id)
      if (index !== -1) {
        students.value[index] = {
          ...students.value[index],
          name: form.name,
          studentId: form.studentId,
          group: form.group,
          groupId: groupId,
          phone: form.phone,
          address: form.address,
          contractPaid: form.contractPaid
        }
      }
    } else {
      const response = await api.createStudent(studentData)
      const newStudent = normalizeStudent(response)
      students.value.push(newStudent)
      totalItems.value++
    }
    showModal.value = false
  } catch (err) {
    console.error('Save student error:', err)
    alert(err.message || t('common.error'))
  }
}

const confirmDelete = (student) => {
  deletingStudent.value = student
  showDeleteConfirm.value = true
}

const deleteStudent = async () => {
  if (!deletingStudent.value) return
  try {
    await api.deleteStudent(deletingStudent.value.id)
    students.value = students.value.filter(s => s.id !== deletingStudent.value.id)
    totalItems.value--
  } catch (err) {
    console.error('Delete student error:', err)
    alert(err.message || t('common.error'))
  }
  showDeleteConfirm.value = false
  deletingStudent.value = null
}
</script>
