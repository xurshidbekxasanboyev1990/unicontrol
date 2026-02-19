<template>
  <div class="space-y-6">
    <!-- Stats cards -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-5">
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
            <Building2 :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_groups }}</p>
        <p class="text-sm text-gray-500">{{ t('academic.groups') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100 text-green-600">
            <Calendar :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_schedules }}</p>
        <p class="text-sm text-gray-500">{{ t('academic.totalSchedules') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
            <BookOpen :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_subjects }}</p>
        <p class="text-sm text-gray-500">{{ t('academic.subjects') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-100 text-orange-600">
            <Users :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_teachers }}</p>
        <p class="text-sm text-gray-500">{{ t('academic.teachers') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-100 text-red-600">
            <AlertTriangle :size="20" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.groups_without_schedule }}</p>
        <p class="text-sm text-gray-500">{{ t('academic.noSchedule') }}</p>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <button
        @click="$router.push('/academic/schedule-editor')"
        class="flex items-center gap-4 rounded-2xl bg-gradient-to-r from-blue-500 to-blue-600 p-5 text-white shadow-lg hover:from-blue-600 hover:to-blue-700 transition-all"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
          <Table2 :size="24" />
        </div>
        <div class="text-left">
          <p class="font-semibold">{{ t('academic.scheduleEditor') }}</p>
          <p class="text-sm text-blue-100">{{ t('academic.editScheduleDesc') }}</p>
        </div>
      </button>

      <button
        @click="$router.push('/academic/ai-generate')"
        class="flex items-center gap-4 rounded-2xl bg-gradient-to-r from-purple-500 to-indigo-600 p-5 text-white shadow-lg hover:from-purple-600 hover:to-indigo-700 transition-all"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
          <Brain :size="24" />
        </div>
        <div class="text-left">
          <p class="font-semibold">{{ t('academic.aiGenerate') }}</p>
          <p class="text-sm text-purple-100">{{ t('academic.aiGenerateDesc') }}</p>
        </div>
      </button>

      <button
        @click="$router.push('/academic/groups')"
        class="flex items-center gap-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-green-600 p-5 text-white shadow-lg hover:from-emerald-600 hover:to-green-700 transition-all"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
          <Building2 :size="24" />
        </div>
        <div class="text-left">
          <p class="font-semibold">{{ t('academic.manageGroups') }}</p>
          <p class="text-sm text-emerald-100">{{ t('academic.manageGroupsDesc') }}</p>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { AlertTriangle, BookOpen, Brain, Building2, Calendar, Table2, Users } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const stats = ref({
  total_groups: 0,
  total_schedules: 0,
  total_subjects: 0,
  total_teachers: 0,
  groups_without_schedule: 0,
})

onMounted(async () => {
  try {
    const res = await api.request('/academic/dashboard')
    stats.value = res
  } catch (e) {
    console.error('Dashboard error:', e)
  }
})
</script>
