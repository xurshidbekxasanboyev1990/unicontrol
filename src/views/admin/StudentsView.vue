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
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div class="relative">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input 
            v-model="searchQuery"
            type="text"
            :placeholder="$t('common.search')"
            class="w-full sm:w-64 pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
          />
          <Loader2 v-if="searching" class="w-5 h-5 text-violet-500 absolute right-3 top-1/2 -translate-y-1/2 animate-spin" />
        </div>
        <select v-model="filterGroup" class="px-4 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none">
          <option value="">{{ $t('common.all') }} {{ $t('layout.groups').toLowerCase() }}</option>
          <option v-for="group in dataStore.groups" :key="group.id" :value="group.name">
            {{ group.name }}
          </option>
        </select>
        <button 
          @click="openModal()"
          class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center justify-center gap-2"
        >
          <UserPlus class="w-5 h-5" />
          <span class="sm:inline hidden">{{ $t('students.addStudent') }}</span>
          <span class="sm:hidden">{{ $t('common.add') }}</span>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
    </div>

    <!-- Students Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('students.student') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">ID</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('students.group') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('common.phone') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('students.contract') }}</th>
              <th class="text-right p-4 font-semibold text-slate-600">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="student in displayedStudents" :key="student.id" class="hover:bg-slate-50 transition-colors">
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

      <div v-if="displayedStudents.length === 0" class="p-12 text-center">
        <UserX class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">{{ $t('common.noResults') }}</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1 && !searchQuery" class="p-4 border-t border-slate-100 flex items-center justify-between">
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
          
          <template v-for="page in Math.min(5, totalPages)" :key="page">
            <button 
              v-if="getPageNumber(page) > 0"
              @click="goToPage(getPageNumber(page))"
              class="w-10 h-10 rounded-lg font-medium transition-colors"
              :class="currentPage === getPageNumber(page) ? 'bg-violet-500 text-white' : 'hover:bg-slate-100'"
            >
              {{ getPageNumber(page) }}
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
            <div class="grid grid-cols-2 gap-4">
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
                  <option v-for="group in dataStore.groups" :key="group.id" :value="group.name">
                    {{ group.name }}
                  </option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('students.phone') }}</label>
              <input 
                v-model="form.phone"
                type="text"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="+998 90 123 45 67"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('students.address') }}</label>
              <input 
                v-model="form.address"
                type="text"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                :placeholder="$t('students.address')"
              />
            </div>
            <div class="flex items-center gap-3">
              <input 
                v-model="form.contractPaid"
                type="checkbox"
                id="contractPaid"
                class="w-5 h-5 rounded border-slate-300 text-violet-500 focus:ring-violet-500"
              />
              <label for="contractPaid" class="text-sm text-slate-700">{{ $t('students.contractPaid') }}</label>
            </div>
            <div class="flex gap-3 pt-4">
              <button 
                type="button"
                @click="showModal = false"
                class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button 
                type="submit"
                class="flex-1 px-4 py-3 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors"
              >
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
          <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle class="w-8 h-8 text-rose-500" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 mb-2">{{ $t('students.confirmDeleteTitle') }}</h3>
          <p class="text-slate-500 mb-6">
            {{ deletingStudent?.name }} ni o'chirmoqchimisiz? Bu amalni qaytarib bo'lmaydi.
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              @click="deleteStudent"
              class="flex-1 px-4 py-3 bg-rose-500 text-white rounded-xl font-medium hover:bg-rose-600 transition-colors"
            >
              {{ $t('common.delete') }}
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useLanguageStore } from '../../stores/language'

const langStore = useLanguageStore()
const { t } = langStore
const dataStore = useDataStore()
const searchQuery = ref('')
const filterGroup = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingStudent = ref(null)
const deletingStudent = ref(null)
const loading = ref(false)
const searching = ref(false)

// Pagination
const currentPage = ref(1)
const pageSize = ref(50)
const totalItems = ref(0)
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

// Local students data (for current view)
const students = ref([])

// Debounce timer for search
let searchTimer = null

// Load students with pagination
async function loadStudents(page = 1) {
  loading.value = true
  try {
    const params = {
      page: page,
      page_size: pageSize.value
    }
    
    if (filterGroup.value) {
      // Find group_id by name
      const group = dataStore.groups.find(g => g.name === filterGroup.value)
      if (group) params.group_id = group.id
    }
    
    const response = await api.getStudents(params)
    
    if (response.items) {
      students.value = response.items.map(normalizeStudent)
      totalItems.value = response.total
      currentPage.value = response.page
    }
    
    // Prefetch next page
    if (page < totalPages.value) {
      prefetchPage(page + 1)
    }
  } catch (err) {
    console.error('Failed to load students:', err)
  } finally {
    loading.value = false
  }
}

// Prefetch page (in background)
const prefetchedPages = new Map()
async function prefetchPage(page) {
  if (prefetchedPages.has(page)) return
  
  try {
    const params = {
      page: page,
      page_size: pageSize.value
    }
    
    if (filterGroup.value) {
      const group = dataStore.groups.find(g => g.name === filterGroup.value)
      if (group) params.group_id = group.id
    }
    
    const response = await api.getStudents(params)
    if (response.items) {
      prefetchedPages.set(page, response.items.map(normalizeStudent))
    }
  } catch (err) {
    // Silent fail for prefetch
  }
}

// Search students from backend (full search)
async function searchStudents(query) {
  if (!query || query.length < 2) {
    // Reset to paginated view
    loadStudents(1)
    return
  }
  
  searching.value = true
  try {
    const response = await api.getStudents({
      search: query,
      page_size: 100 // Limit search results
    })
    
    if (response.items) {
      students.value = response.items.map(normalizeStudent)
      totalItems.value = response.total
      currentPage.value = 1
    }
  } catch (err) {
    console.error('Search failed:', err)
  } finally {
    searching.value = false
  }
}

// Normalize student data
function normalizeStudent(data) {
  return {
    id: data.id,
    name: data.full_name || data.name || 'Ism kiritilmagan',
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

// Watch search query with debounce
watch(searchQuery, (newVal) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    if (newVal && newVal.length >= 2) {
      searchStudents(newVal)
    } else if (!newVal) {
      loadStudents(1)
    }
  }, 300) // 300ms debounce
})

// Watch filter group
watch(filterGroup, () => {
  prefetchedPages.clear()
  loadStudents(1)
})

// Page change
function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  
  // Check prefetched data
  if (prefetchedPages.has(page)) {
    students.value = prefetchedPages.get(page)
    currentPage.value = page
    // Prefetch next
    if (page < totalPages.value) {
      prefetchPage(page + 1)
    }
    if (page > 1) {
      prefetchPage(page - 1)
    }
  } else {
    loadStudents(page)
  }
}

// Computed for display
const displayedStudents = computed(() => students.value)

// Load on mount
onMounted(async () => {
  loading.value = true
  try {
    await dataStore.fetchGroups({}, true)
    await loadStudents(1)
  } catch (err) {
    console.error('Failed to load data:', err)
  } finally {
    loading.value = false
  }
})

const form = reactive({
  name: '',
  studentId: '',
  group: '',
  phone: '',
  address: '',
  contractPaid: false
})

// Calculate page number for pagination display
function getPageNumber(index) {
  if (totalPages.value <= 5) {
    return index
  }
  
  // Show pages around current page
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + 4)
  
  if (end - start < 4) {
    start = Math.max(1, end - 4)
  }
  
  return start + index - 1
}

const getAttendanceRate = (studentId) => {
  const records = dataStore.attendanceRecords.filter(r => r.studentId === studentId)
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 100
}

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
    // Find group_id from group name
    const group = dataStore.groups.find(g => g.name === form.group)
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
      // Update local list
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
