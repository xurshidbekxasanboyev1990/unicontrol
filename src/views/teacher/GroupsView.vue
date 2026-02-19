<template>
  <div class="space-y-6">
    <!-- Groups list -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-blue-500" />
    </div>

    <div v-else-if="groups.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400">
      <Users :size="48" class="mb-3 opacity-50" />
      <p class="text-sm">{{ t('teacher.noGroupsAssigned') }}</p>
    </div>

    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="group in groups"
        :key="group.id"
        class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push(`/teacher/groups/${group.id}/students`)"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-blue-600 font-bold text-lg">
            {{ group.name.charAt(0) }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 truncate">{{ group.name }}</h3>
            <p v-if="group.faculty" class="text-xs text-gray-500 truncate">{{ group.faculty }}</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 mb-3">
          <div class="rounded-lg bg-gray-50 p-2.5 text-center">
            <p class="text-lg font-bold text-gray-900">{{ group.students_count }}</p>
            <p class="text-xs text-gray-500">{{ t('teacher.students') }}</p>
          </div>
          <div class="rounded-lg bg-gray-50 p-2.5 text-center">
            <p class="text-lg font-bold text-gray-900">{{ group.subjects?.length || 0 }}</p>
            <p class="text-xs text-gray-500">{{ t('teacher.subjects') }}</p>
          </div>
        </div>

        <div v-if="group.subjects?.length" class="flex flex-wrap gap-1.5">
          <span 
            v-for="subj in group.subjects.slice(0, 3)" 
            :key="subj"
            class="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-600"
          >
            {{ subj }}
          </span>
          <span v-if="group.subjects.length > 3" class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
            +{{ group.subjects.length - 3 }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Loader2, Users } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(true)
const groups = ref([])

const fetchGroups = async () => {
  loading.value = true
  try {
    const res = await api.request('/teacher/groups')
    groups.value = res.items || []
  } catch (err) {
    console.error('Groups error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchGroups()
})
</script>
