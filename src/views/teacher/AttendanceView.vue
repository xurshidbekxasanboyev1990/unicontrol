<template>
  <div class="space-y-6">
    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <select 
        v-model="selectedGroup" 
        class="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        @change="onGroupChange"
      >
        <option :value="null" disabled>{{ t('teacher.selectGroup') }}</option>
        <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>

      <select 
        v-if="subjects.length > 0"
        v-model="selectedSubject" 
        class="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
      >
        <option :value="null">{{ t('teacher.allSubjects') }}</option>
        <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
      </select>

      <input
        v-model="selectedDate"
        type="date"
        class="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
      />
    </div>

    <!-- No group selected -->
    <div v-if="!selectedGroup" class="flex flex-col items-center justify-center py-12 text-gray-400">
      <ClipboardList :size="48" class="mb-3 opacity-50" />
      <p class="text-sm">{{ t('teacher.selectGroupFirst') }}</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-blue-500" />
    </div>

    <!-- Attendance form -->
    <div v-else-if="students.length > 0" class="space-y-4">
      <div class="rounded-2xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div class="border-b border-gray-100 bg-gray-50/50 px-5 py-3 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-gray-700">
            {{ t('teacher.markAttendance') }} — {{ selectedDate }}
          </h3>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500"></span>{{ presentCount }}</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500"></span>{{ absentCount }}</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-yellow-500"></span>{{ lateCount }}</span>
          </div>
        </div>

        <div class="divide-y divide-gray-50">
          <div 
            v-for="(student, index) in students" 
            :key="student.id"
            class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50/50"
          >
            <span class="text-xs text-gray-400 w-6">{{ index + 1 }}</span>
            
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 text-blue-600 text-xs font-medium flex-shrink-0">
              {{ student.name?.charAt(0) || '?' }}
            </div>
            
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ student.name }}</p>
            </div>

            <div class="flex items-center gap-1.5">
              <button
                v-for="status in statuses"
                :key="status.value"
                @click="setStatus(student.id, status.value)"
                :class="[
                  'flex h-8 w-8 items-center justify-center rounded-lg text-xs font-medium transition-all border',
                  attendanceMap[student.id] === status.value
                    ? status.activeClass
                    : 'bg-white border-gray-200 text-gray-400 hover:bg-gray-50'
                ]"
                :title="status.label"
              >
                {{ status.icon }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Save button -->
      <div class="flex justify-end gap-3">
        <button
          @click="markAllPresent"
          class="rounded-xl bg-green-50 px-4 py-2.5 text-sm font-medium text-green-600 hover:bg-green-100 transition-colors"
        >
          {{ t('teacher.markAllPresent') }}
        </button>
        <button
          @click="saveAttendance"
          :disabled="saving"
          class="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <Loader2 v-if="saving" :size="16" class="animate-spin" />
          {{ t('common.save') }}
        </button>
      </div>
    </div>

    <!-- No students -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-gray-400">
      <Users :size="48" class="mb-3 opacity-50" />
      <p class="text-sm">{{ t('teacher.noStudents') }}</p>
    </div>

    <!-- Success toast -->
    <Transition name="fade">
      <div v-if="showSuccess" class="fixed bottom-6 right-6 z-50 rounded-xl bg-green-600 px-5 py-3 text-white shadow-lg flex items-center gap-2">
        <Check :size="18" />
        {{ successMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { Check, ClipboardList, Loader2, Users } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()
const route = useRoute()

const loading = ref(false)
const saving = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

const groups = ref([])
const subjects = ref([])
const students = ref([])

const selectedGroup = ref(route.query.group_id ? Number(route.query.group_id) : null)
const selectedSubject = ref(route.query.subject || null)
const selectedDate = ref(new Date().toISOString().split('T')[0])

const attendanceMap = reactive({})

const statuses = [
  { value: 'present', label: 'Keldi', icon: '✓', activeClass: 'bg-green-100 border-green-300 text-green-700' },
  { value: 'absent', label: 'Kelmadi', icon: '✗', activeClass: 'bg-red-100 border-red-300 text-red-700' },
  { value: 'late', label: 'Kechikdi', icon: '⏰', activeClass: 'bg-yellow-100 border-yellow-300 text-yellow-700' },
  { value: 'excused', label: 'Sababli', icon: '📋', activeClass: 'bg-blue-100 border-blue-300 text-blue-700' },
]

const presentCount = computed(() => Object.values(attendanceMap).filter(v => v === 'present').length)
const absentCount = computed(() => Object.values(attendanceMap).filter(v => v === 'absent').length)
const lateCount = computed(() => Object.values(attendanceMap).filter(v => v === 'late').length)

const setStatus = (studentId, status) => {
  attendanceMap[studentId] = status
}

const markAllPresent = () => {
  students.value.forEach(s => {
    attendanceMap[s.id] = 'present'
  })
}

const onGroupChange = () => {
  const group = groups.value.find(g => g.id === selectedGroup.value)
  subjects.value = group?.subjects || []
  selectedSubject.value = null
  fetchStudents()
}

const fetchGroups = async () => {
  try {
    const res = await api.request('/teacher/groups')
    groups.value = res.items || []
    if (selectedGroup.value) {
      const group = groups.value.find(g => g.id === selectedGroup.value)
      subjects.value = group?.subjects || []
    }
  } catch (err) {
    console.error('Groups error:', err)
  }
}

const fetchStudents = async () => {
  if (!selectedGroup.value) return
  loading.value = true
  try {
    const res = await api.request(`/teacher/groups/${selectedGroup.value}/students`)
    students.value = res.items || []
    // Set default: all present
    students.value.forEach(s => {
      if (!attendanceMap[s.id]) {
        attendanceMap[s.id] = 'present'
      }
    })
  } catch (err) {
    console.error('Students error:', err)
  } finally {
    loading.value = false
  }
}

const saveAttendance = async () => {
  if (!selectedGroup.value || students.value.length === 0) return
  saving.value = true
  try {
    const attendances = students.value.map(s => ({
      student_id: s.id,
      status: attendanceMap[s.id] || 'present',
      note: null,
      late_minutes: 0
    }))

    const res = await api.request('/teacher/attendance', {
      method: 'POST',
      body: {
        group_id: selectedGroup.value,
        date: selectedDate.value,
        subject: selectedSubject.value,
        lesson_number: route.query.lesson_number ? Number(route.query.lesson_number) : null,
        attendances
      }
    })

    successMessage.value = res.message || t('teacher.attendanceSaved')
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 3000)
  } catch (err) {
    console.error('Save error:', err)
    alert(err.data?.detail || t('common.error'))
  } finally {
    saving.value = false
  }
}

watch(selectedGroup, () => {
  if (selectedGroup.value) fetchStudents()
})

onMounted(() => {
  fetchGroups()
  if (selectedGroup.value) fetchStudents()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
