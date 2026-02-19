<template>
  <div class="space-y-6">
    <!-- Statistikalar -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
            <Users :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_groups }}</p>
        <p class="text-sm text-gray-500">{{ t('teacher.myGroups') }}</p>
      </div>

      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100 text-green-600">
            <GraduationCap :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_students }}</p>
        <p class="text-sm text-gray-500">{{ t('teacher.totalStudents') }}</p>
      </div>

      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
            <BookOpen :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.today_lessons }}</p>
        <p class="text-sm text-gray-500">{{ t('teacher.todayLessons') }}</p>
      </div>

      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-100 text-orange-600">
            <ClipboardCheck :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.today_attendance_rate }}%</p>
        <p class="text-sm text-gray-500">{{ t('teacher.attendanceRate') }}</p>
      </div>
    </div>

    <!-- Bugungi darslar -->
    <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">{{ t('teacher.todaySchedule') }}</h3>
        <button @click="$router.push('/teacher/schedule')" class="text-sm text-blue-600 hover:text-blue-700 font-medium">
          {{ t('common.viewAll') }}
        </button>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-8">
        <Loader2 :size="24" class="animate-spin text-blue-500" />
      </div>

      <div v-else-if="stats.today_schedule && stats.today_schedule.length > 0" class="space-y-3">
        <div 
          v-for="lesson in stats.today_schedule" 
          :key="lesson.id"
          class="flex items-center gap-4 rounded-xl border border-gray-100 p-4 hover:bg-gray-50 transition-colors cursor-pointer"
          @click="goToAttendance(lesson)"
        >
          <div class="flex flex-col items-center justify-center rounded-lg bg-blue-50 px-3 py-2 min-w-[60px]">
            <span class="text-xs text-blue-600 font-medium">{{ lesson.start_time }}</span>
            <span class="text-[10px] text-blue-400">{{ lesson.end_time }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 truncate">{{ lesson.subject }}</p>
            <p class="text-sm text-gray-500">
              {{ lesson.group_name }}
              <span v-if="lesson.room" class="ml-2">• {{ lesson.room }}</span>
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="lesson.schedule_type" class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
              {{ lesson.schedule_type }}
            </span>
            <ChevronRight :size="16" class="text-gray-400" />
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-8 text-gray-400">
        <Coffee :size="40" class="mb-3 opacity-50" />
        <p class="text-sm">{{ t('teacher.noLessonsToday') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BookOpen, ChevronRight, ClipboardCheck, Coffee, GraduationCap, Loader2, Users } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const router = useRouter()
const { t } = useLanguageStore()

const loading = ref(true)
const stats = ref({
  total_groups: 0,
  total_students: 0,
  today_lessons: 0,
  weekly_lessons: 0,
  today_attendance_rate: 0,
  today_schedule: []
})

const fetchDashboard = async () => {
  loading.value = true
  try {
    const res = await api.request('/teacher/dashboard')
    stats.value = res
  } catch (err) {
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
}

const goToAttendance = (lesson) => {
  router.push({
    path: '/teacher/attendance',
    query: { group_id: lesson.group_id, subject: lesson.subject, lesson_number: lesson.lesson_number }
  })
}

onMounted(() => {
  fetchDashboard()
})
</script>
