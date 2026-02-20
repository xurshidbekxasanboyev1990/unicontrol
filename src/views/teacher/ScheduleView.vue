<template>
  <div class="space-y-6">
    <!-- Filter -->
    <div class="flex flex-wrap items-center gap-3">
      <select 
        v-model="selectedGroup" 
        class="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
      >
        <option :value="null">{{ t('teacher.allGroups') }}</option>
        <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>

    <!-- Weekly schedule -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-blue-500" />
    </div>

    <div v-else class="space-y-4">
      <div v-for="day in weekDays" :key="day.value" class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-3">
          <div :class="['flex h-9 w-9 items-center justify-center rounded-lg text-white text-sm font-medium', isToday(day.value) ? 'bg-blue-600' : 'bg-gray-400']">
            {{ day.short }}
          </div>
          <h3 :class="['font-semibold', isToday(day.value) ? 'text-blue-600' : 'text-gray-900']">
            {{ day.label }}
            <span v-if="isToday(day.value)" class="ml-2 text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">{{ t('teacher.today') }}</span>
          </h3>
          <span class="ml-auto text-xs text-gray-400">{{ getDayLessonsCount(day.value) }} {{ t('teacher.lessons') }}</span>
        </div>

        <div v-if="getDayLessons(day.value).length > 0" class="space-y-2">
          <div 
            v-for="lesson in getDayLessons(day.value)" 
            :key="lesson.id"
            class="flex items-center gap-3 rounded-xl bg-gray-50 p-3"
          >
            <div class="flex flex-col items-center justify-center rounded-lg bg-white px-2.5 py-1.5 min-w-[56px] text-center border border-gray-100">
              <span class="text-xs font-medium text-gray-700">{{ lesson.start_time }}</span>
              <span class="text-[10px] text-gray-400">{{ lesson.end_time }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5">
                <p class="text-sm font-medium text-gray-900 truncate">{{ lesson.subject }}</p>
                <span v-if="lesson.week_type === 'odd'" class="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700">Toq</span>
                <span v-else-if="lesson.week_type === 'even'" class="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-orange-700">Juft</span>
              </div>
              <p class="text-xs text-gray-500">
                {{ lesson.group_name }}
                <span v-if="lesson.room" class="ml-1">• {{ lesson.room }}</span>
                <span v-if="lesson.building" class="ml-1">• {{ lesson.building }}</span>
              </p>
            </div>
            <span v-if="lesson.schedule_type" class="rounded-full bg-white border border-gray-200 px-2 py-0.5 text-xs text-gray-500">
              {{ lesson.schedule_type }}
            </span>
          </div>
        </div>

        <div v-else class="py-3 text-center text-sm text-gray-400">
          {{ t('teacher.noLessons') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Loader2 } from 'lucide-vue-next'
import { onMounted, ref, watch } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(true)
const scheduleItems = ref([])
const groups = ref([])
const selectedGroup = ref(null)

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

const getDayLessons = (dayValue) => {
  return scheduleItems.value.filter(s => s.day_of_week === dayValue)
}

const getDayLessonsCount = (dayValue) => {
  return getDayLessons(dayValue).length
}

const fetchSchedule = async () => {
  loading.value = true
  try {
    const params = selectedGroup.value ? `?group_id=${selectedGroup.value}` : ''
    const res = await api.request(`/teacher/schedule${params}`)
    scheduleItems.value = res.items || []
  } catch (err) {
    console.error('Schedule error:', err)
  } finally {
    loading.value = false
  }
}

const fetchGroups = async () => {
  try {
    const res = await api.request('/teacher/groups')
    groups.value = res.items || []
  } catch (err) {
    console.error('Groups error:', err)
  }
}

watch(selectedGroup, () => {
  fetchSchedule()
})

onMounted(() => {
  fetchGroups()
  fetchSchedule()
})
</script>
