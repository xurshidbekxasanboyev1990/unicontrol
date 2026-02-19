<template>
  <div class="space-y-6">
    <!-- Back + Group info header -->
    <div class="flex items-center gap-3">
      <button @click="$router.push('/teacher/groups')" class="flex h-9 w-9 items-center justify-center rounded-xl bg-gray-100 hover:bg-gray-200 transition-colors">
        <ArrowLeft :size="18" />
      </button>
      <div>
        <h2 class="text-lg font-semibold text-gray-900">{{ t('teacher.groupStudents') }}</h2>
        <p class="text-sm text-gray-500">{{ t('teacher.group') }}: {{ groupId }}</p>
      </div>
    </div>

    <!-- Students list -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-blue-500" />
    </div>

    <div v-else-if="students.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400">
      <Users :size="48" class="mb-3 opacity-50" />
      <p class="text-sm">{{ t('teacher.noStudents') }}</p>
    </div>

    <div v-else>
      <!-- Search -->
      <div class="mb-4">
        <div class="relative">
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="t('common.search') + '...'"
            class="w-full rounded-xl border border-gray-200 bg-white py-2.5 pl-10 pr-4 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-hidden rounded-2xl bg-white shadow-sm border border-gray-100">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50/50">
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">№</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">{{ t('common.name') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">{{ t('teacher.hemisId') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">{{ t('common.phone') }}</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500">{{ t('teacher.attendanceRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(student, index) in filteredStudents" 
                :key="student.id"
                class="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
              >
                <td class="px-4 py-3 text-sm text-gray-500">{{ index + 1 }}</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 text-blue-600 text-xs font-medium">
                      {{ student.name?.charAt(0) || '?' }}
                    </div>
                    <span class="text-sm font-medium text-gray-900">{{ student.name }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ student.hemis_id || student.student_id || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ student.phone || '-' }}</td>
                <td class="px-4 py-3 text-center">
                  <span 
                    v-if="student.attendance_rate !== null"
                    :class="[
                      'inline-flex rounded-full px-2 py-0.5 text-xs font-medium',
                      student.attendance_rate >= 80 ? 'bg-green-100 text-green-700' :
                      student.attendance_rate >= 60 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    ]"
                  >
                    {{ student.attendance_rate }}%
                  </span>
                  <span v-else class="text-xs text-gray-400">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft, Loader2, Search, Users } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()
const route = useRoute()

const groupId = computed(() => route.params.id)
const loading = ref(true)
const students = ref([])
const searchQuery = ref('')

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  const q = searchQuery.value.toLowerCase()
  return students.value.filter(s =>
    s.name?.toLowerCase().includes(q) ||
    s.hemis_id?.toLowerCase().includes(q) ||
    s.student_id?.toLowerCase().includes(q) ||
    s.phone?.includes(q)
  )
})

const fetchStudents = async () => {
  loading.value = true
  try {
    const res = await api.request(`/teacher/groups/${groupId.value}/students`)
    students.value = res.items || []
  } catch (err) {
    console.error('Students error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStudents()
})
</script>
