<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between rounded-2xl bg-white p-4 shadow-sm border border-gray-100">
      <div class="flex items-center gap-3">
        <Users :size="22" class="text-blue-600" />
        <h1 class="text-lg font-bold text-gray-900">{{ t('academic.manageGroups') }}</h1>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="filterFaculty" class="rounded-xl border border-gray-200 px-3 py-2 text-sm">
          <option value="">{{ t('academic.allFaculties') }}</option>
          <option v-for="f in faculties" :key="f" :value="f">{{ f }}</option>
        </select>
        <select v-model="filterCourse" class="rounded-xl border border-gray-200 px-3 py-2 text-sm">
          <option :value="null">{{ t('academic.allCourses') }}</option>
          <option v-for="c in [1,2,3,4,5,6]" :key="c" :value="c">{{ c }}-{{ t('academic.course') }}</option>
        </select>
        <input v-model="search" type="text" class="rounded-xl border border-gray-200 px-3 py-2 text-sm" :placeholder="t('common.search')" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-blue-500" />
    </div>

    <!-- Groups grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="g in filteredGroups"
        :key="g.id"
        class="rounded-2xl bg-white p-4 shadow-sm border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all cursor-pointer"
        @click="goToGroup(g.id)"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900 text-sm">{{ g.name }}</h3>
          <span :class="[
            'px-2 py-0.5 rounded-full text-[10px] font-medium',
            g.schedule_count > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          ]">
            {{ g.schedule_count > 0 ? `${g.schedule_count} ${t('academic.lessons')}` : t('academic.noSchedule') }}
          </span>
        </div>
        <div class="space-y-1.5">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <Building2 :size="12" />
            <span>{{ g.faculty || '-' }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <GraduationCap :size="12" />
            <span>{{ g.course_year }}-{{ t('academic.course') }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <Users :size="12" />
            <span>{{ g.student_count || 0 }} {{ t('academic.students') }}</span>
          </div>
        </div>
        <div class="mt-3 flex gap-2">
          <button
            @click.stop="goToGroup(g.id)"
            class="flex-1 rounded-xl bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-100 flex items-center justify-center gap-1"
          >
            <Calendar :size="12" />
            {{ t('academic.viewSchedule') }}
          </button>
          <button
            @click.stop="clearGroupSchedule(g.id, g.name)"
            v-if="g.schedule_count > 0"
            class="rounded-xl bg-red-50 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-100 flex items-center justify-center gap-1"
          >
            <Trash2 :size="12" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!loading && filteredGroups.length === 0" class="flex flex-col items-center justify-center py-16 text-gray-400">
      <Users :size="48" class="mb-3 opacity-50" />
      <p class="text-sm">{{ t('academic.noGroups') }}</p>
    </div>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { Building2, Calendar, GraduationCap, Loader2, Trash2, Users } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()
const router = useRouter()

const loading = ref(false)
const toast = ref(null)
const groups = ref([])
const faculties = ref([])
const filterFaculty = ref('')
const filterCourse = ref(null)
const search = ref('')

const filteredGroups = computed(() => {
  return groups.value.filter(g => {
    if (filterFaculty.value && g.faculty !== filterFaculty.value) return false
    if (filterCourse.value && g.course_year !== filterCourse.value) return false
    if (search.value && !g.name.toLowerCase().includes(search.value.toLowerCase())) return false
    return true
  })
})

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const loadGroups = async () => {
  loading.value = true
  try {
    const res = await api.request('/academic/groups')
    groups.value = res.items || []
    // Extract unique faculties
    const facs = new Set(groups.value.map(g => g.faculty).filter(Boolean))
    faculties.value = Array.from(facs)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goToGroup = (groupId) => {
  router.push({ path: '/academic/schedule-editor', query: { group: groupId } })
}

const clearGroupSchedule = async (groupId, groupName) => {
  if (!confirm(`${groupName} ${t('academic.confirmClear')}`)) return
  try {
    await api.request(`/academic/schedules/group/${groupId}`, { method: 'DELETE' })
    showToast(t('academic.scheduleCleared'))
    await loadGroups()
  } catch (e) {
    showToast(e.data?.detail || t('common.error'), 'error')
  }
}

onMounted(loadGroups)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
