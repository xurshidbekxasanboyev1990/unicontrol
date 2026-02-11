<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('students.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('students.groupInfo', { group: groupName, specialty: specialty, count: students.length }) }}</p>
      </div>
      <div class="relative">
        <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          v-model="searchQuery"
          type="text"
          :placeholder="$t('common.search') + '...'"
          class="w-full sm:w-64 pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <div class="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-slate-500">{{ $t('common.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <UserX class="w-12 h-12 text-rose-400 mx-auto mb-4" />
      <p class="text-slate-500">{{ error }}</p>
      <button @click="loadStudents" class="mt-4 px-4 py-2 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600">
        {{ $t('common.retry') }}
      </button>
    </div>

    <!-- Students Grid -->
    <div v-else-if="filteredStudents.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="student in filteredStudents" 
        :key="student.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start gap-4">
          <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xl font-bold">
            {{ getInitials(student.name) }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-slate-800 truncate">{{ student.name }}</h3>
            <p class="text-sm text-slate-500">ID: {{ student.student_id || '-' }}</p>
          </div>
        </div>

        <div class="mt-4 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Phone class="w-4 h-4" />
              {{ $t('students.phone') }}
            </span>
            <span class="text-slate-700">{{ student.phone || '-' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <GraduationCap class="w-4 h-4" />
              {{ $t('students.faculty') }}
            </span>
            <span class="text-slate-700">{{ student.commute || student.faculty || '-' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Calendar class="w-4 h-4" />
              {{ $t('students.birthDate') }}
            </span>
            <span class="text-slate-700">{{ formatDate(student.birth_date) }}</span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-100 flex gap-2">
          <button 
            @click="viewStudent(student)"
            class="flex-1 px-3 py-2 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
          >
            <Eye class="w-4 h-4" />
            {{ $t('common.view') }}
          </button>
          <button 
            v-if="student.phone"
            @click="contactStudent(student)"
            class="flex-1 px-3 py-2 bg-emerald-100 text-emerald-700 rounded-xl text-sm font-medium hover:bg-emerald-200 transition-colors flex items-center justify-center gap-2"
          >
            <MessageCircle class="w-4 h-4" />
            {{ $t('students.contact') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <UserX class="w-12 h-12 text-slate-300 mx-auto mb-4" />
      <p class="text-slate-500">{{ $t('students.noStudents') }}</p>
    </div>

    <!-- Student Detail Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="selectedStudent" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selectedStudent = null">
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-bold text-slate-800">{{ $t('students.studentInfo') }}</h2>
              <button @click="selectedStudent = null" class="p-2 hover:bg-slate-100 rounded-xl">
                <X class="w-5 h-5 text-slate-500" />
              </button>
            </div>

            <div class="flex items-center gap-4 mb-6">
              <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-2xl font-bold">
                {{ getInitials(selectedStudent.name) }}
              </div>
              <div>
                <h3 class="text-lg font-semibold text-slate-800">{{ selectedStudent.name }}</h3>
                <p class="text-sm text-slate-500">ID: {{ selectedStudent.student_id || '-' }}</p>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <CreditCard class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">{{ $t('students.studentIdLabel') }}</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.student_id || $t('profile.notEntered') }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <Phone class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">{{ $t('students.phone') }}</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.phone || $t('profile.notEntered') }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <MapPin class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">{{ $t('students.address') }}</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.address || $t('profile.notEntered') }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <Calendar class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">{{ $t('students.birthDate') }}</p>
                  <p class="font-medium text-slate-800">{{ formatDate(selectedStudent.birth_date) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <GraduationCap class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">{{ $t('students.faculty') }}</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.commute || selectedStudent.faculty || $t('profile.notEntered') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { useLanguageStore } from '@/stores/language'
import {
    Calendar,
    CreditCard,
    Eye,
    GraduationCap,
    MapPin,
    MessageCircle,
    Phone,
    Search,
    UserX,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const langStore = useLanguageStore()
const { t } = langStore

const searchQuery = ref('')
const selectedStudent = ref(null)
const students = ref([])
const groupName = ref('')
const specialty = ref('')
const groupId = ref(null)
const loading = ref(true)
const error = ref(null)

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(s => 
    (s.name && s.name.toLowerCase().includes(query)) ||
    (s.student_id && s.student_id.toLowerCase().includes(query))
  )
})

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('uz-UZ')
  } catch {
    return dateStr
  }
}

const viewStudent = (student) => {
  selectedStudent.value = student
}

const contactStudent = (student) => {
  if (student.phone) {
    window.open(`tel:${student.phone}`)
  }
}

async function loadStudents() {
  loading.value = true
  error.value = null
  
  try {
    // Avval leader dashboard dan guruh ID olish
    const dashboardResp = await api.request('/dashboard/leader')
    
    if (dashboardResp.error) {
      error.value = dashboardResp.error
      return
    }
    
    if (dashboardResp.group) {
      groupId.value = dashboardResp.group.id
      groupName.value = dashboardResp.group.name
      specialty.value = dashboardResp.group.specialty || dashboardResp.group.faculty || ''
      
      // Guruh talabalarini yuklash
      const studentsResp = await api.getStudents({ 
        group_id: groupId.value, 
        page_size: 100 
      })
      
      students.value = studentsResp.items || studentsResp.data || []
    } else {
      error.value = t('students.noGroupAssigned')
    }
  } catch (e) {
    console.error('Failed to load students:', e)
    error.value = t('students.loadStudentsError')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStudents()
})
</script>
