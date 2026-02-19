<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25">
            <CalendarCheck :size="22" />
          </div>
          {{ t('exams.title') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ t('exams.description') }}
          <span v-if="groupName" class="ml-1 inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
            <Building2 :size="12" /> {{ groupName }}
          </span>
        </p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-3 gap-4">
      <div class="relative overflow-hidden rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="absolute top-0 right-0 h-20 w-20 -translate-y-4 translate-x-4 rounded-full bg-emerald-50"></div>
        <div class="relative">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 mb-3">
            <FileText :size="18" />
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ stats.total_exams }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ t('exams.totalExams') }}</p>
        </div>
      </div>
      <div class="relative overflow-hidden rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="absolute top-0 right-0 h-20 w-20 -translate-y-4 translate-x-4 rounded-full bg-amber-50"></div>
        <div class="relative">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-600 mb-3">
            <Clock :size="18" />
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ stats.upcoming_exams }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ t('exams.upcoming') }}</p>
        </div>
      </div>
      <div class="relative overflow-hidden rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="absolute top-0 right-0 h-20 w-20 -translate-y-4 translate-x-4 rounded-full bg-purple-50"></div>
        <div class="relative">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600 mb-3">
            <BookOpen :size="18" />
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ stats.subjects }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ t('exams.subjects') }}</p>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <select v-model="filterType" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" @change="loadExams">
        <option value="">{{ t('exams.allTypes') }}</option>
        <option value="exam">{{ t('exams.typeExam') }}</option>
        <option value="midterm">{{ t('exams.typeMidterm') }}</option>
        <option value="retake">{{ t('exams.typeRetake') }}</option>
        <option value="final">{{ t('exams.typeFinal') }}</option>
      </select>
      <input
        v-model="filterDateFrom"
        type="date"
        class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        @change="loadExams"
      />
      <span class="text-gray-400 text-sm">—</span>
      <input
        v-model="filterDateTo"
        type="date"
        class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        @change="loadExams"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <Loader2 :size="36" class="animate-spin text-emerald-500 mb-3" />
      <p class="text-sm text-gray-400">{{ t('common.loading') }}...</p>
    </div>

    <!-- Exams Timeline -->
    <div v-else-if="groupedExams.length > 0" class="space-y-8">
      <div v-for="group in groupedExams" :key="group.date" class="space-y-3">
        <!-- Date header -->
        <div class="flex items-center gap-4">
          <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-bold flex-col leading-none shadow-lg shadow-emerald-500/20">
            <span class="text-xl">{{ getDayNum(group.date) }}</span>
            <span class="text-[10px] uppercase opacity-90">{{ getMonthShort(group.date) }}</span>
          </div>
          <div>
            <p class="font-bold text-gray-900 text-lg">{{ formatDate(group.date) }}</p>
            <p class="text-sm text-gray-500">{{ getDayName(group.date) }} · {{ group.items.length }} {{ t('exams.examsCount') }}</p>
          </div>
          <div :class="['ml-auto rounded-full px-3 py-1 text-xs font-bold', isToday(group.date) ? 'bg-emerald-600 text-white animate-pulse' : isPast(group.date) ? 'bg-gray-100 text-gray-400' : 'bg-emerald-100 text-emerald-700']">
            {{ isToday(group.date) ? 'Bugun!' : isPast(group.date) ? 'O\'tgan' : getDaysLeft(group.date) + ' kun qoldi' }}
          </div>
        </div>

        <!-- Exam cards -->
        <div class="ml-7 border-l-2 border-emerald-200 pl-7 space-y-3">
          <div
            v-for="exam in group.items"
            :key="exam.id"
            :class="[
              'rounded-2xl bg-white p-5 shadow-sm border transition-all hover:shadow-md',
              isPast(group.date) ? 'border-gray-100 opacity-60' : 'border-gray-100 hover:border-emerald-200'
            ]"
          >
            <div class="flex items-start gap-4">
              <!-- Time badge -->
              <div class="flex flex-col items-center rounded-xl bg-gray-50 px-3 py-2 min-w-[60px]">
                <span class="text-sm font-bold text-gray-900">{{ exam.start_time }}</span>
                <span class="text-[10px] text-gray-400">{{ exam.end_time }}</span>
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <h4 class="font-bold text-gray-900 text-base">{{ exam.subject }}</h4>
                  <span :class="['rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider', examTypeClass(exam.exam_type)]">
                    {{ examTypeName(exam.exam_type) }}
                  </span>
                </div>
                <div class="flex flex-wrap gap-x-4 gap-y-1.5 text-sm text-gray-500">
                  <span v-if="exam.group_name" class="flex items-center gap-1.5">
                    <Building2 :size="14" class="text-gray-400" /> {{ exam.group_name }}
                  </span>
                  <span v-if="exam.room" class="flex items-center gap-1.5">
                    <DoorOpen :size="14" class="text-gray-400" />
                    {{ exam.room }}
                    <template v-if="exam.building">({{ exam.building }})</template>
                  </span>
                  <span v-if="exam.teacher_name" class="flex items-center gap-1.5">
                    <User :size="14" class="text-gray-400" /> {{ exam.teacher_name }}
                  </span>
                </div>
                <p v-if="exam.notes" class="mt-2 text-xs text-gray-400 italic bg-gray-50 rounded-lg px-3 py-1.5">
                  💬 {{ exam.notes }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
      <div class="flex h-20 w-20 items-center justify-center rounded-3xl bg-gray-100 mb-4">
        <CalendarCheck :size="40" class="opacity-40" />
      </div>
      <p class="text-base font-medium text-gray-500 mb-1">{{ t('exams.noExams') }}</p>
      <p class="text-sm text-gray-400">Imtihon jadvali hali e'lon qilinmagan</p>
    </div>
  </div>
</template>

<script setup>
import { BookOpen, Building2, CalendarCheck, Clock, DoorOpen, FileText, Loader2, User } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(false)
const exams = ref([])
const groupName = ref('')
const stats = ref({ total_exams: 0, upcoming_exams: 0, subjects: 0 })
const filterType = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')

const dayNames = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
const monthNames = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']

const getDayNum = (dateStr) => new Date(dateStr).getDate()
const getMonthShort = (dateStr) => monthNames[new Date(dateStr).getMonth()]
const getDayName = (dateStr) => dayNames[new Date(dateStr).getDay()]
const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return `${d.getDate()} ${monthNames[d.getMonth()]} ${d.getFullYear()}`
}

const isToday = (dateStr) => {
  const today = new Date()
  const d = new Date(dateStr)
  return today.toISOString().split('T')[0] === d.toISOString().split('T')[0]
}

const isPast = (dateStr) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return new Date(dateStr) < today
}

const getDaysLeft = (dateStr) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(dateStr)
  return Math.ceil((target - today) / (1000 * 60 * 60 * 24))
}

const groupedExams = computed(() => {
  const map = {}
  exams.value.forEach(e => {
    if (!map[e.exam_date]) map[e.exam_date] = { date: e.exam_date, items: [] }
    map[e.exam_date].items.push(e)
  })
  return Object.values(map).sort((a, b) => a.date.localeCompare(b.date))
})

const examTypeClass = (type) => {
  const classes = {
    exam: 'bg-emerald-100 text-emerald-700',
    midterm: 'bg-amber-100 text-amber-700',
    retake: 'bg-orange-100 text-orange-700',
    final: 'bg-red-100 text-red-700',
  }
  return classes[type] || 'bg-gray-100 text-gray-700'
}

const examTypeName = (type) => {
  const names = {
    exam: t('exams.typeExam'), midterm: t('exams.typeMidterm'),
    retake: t('exams.typeRetake'), final: t('exams.typeFinal'),
  }
  return names[type] || type
}

const loadExams = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterType.value) params.append('exam_type', filterType.value)
    if (filterDateFrom.value) params.append('date_from', filterDateFrom.value)
    if (filterDateTo.value) params.append('date_to', filterDateTo.value)

    const qs = params.toString() ? `?${params.toString()}` : ''
    const res = await api.request(`/rooms-exams/my-exams${qs}`)
    exams.value = res.items || []
    groupName.value = res.group_name || ''
    stats.value = res.stats || { total_exams: 0, upcoming_exams: 0, subjects: 0 }
  } catch (e) {
    console.error('Load exams error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadExams()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
