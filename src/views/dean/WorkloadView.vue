<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">O'qituvchi bandligi</h1>
        <p class="text-sm text-slate-500">
          <span v-if="loading">Yuklanmoqda...</span>
          <span v-else>{{ workload.length }} ta yozuv</span>
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Search -->
        <div class="relative lg:col-span-2">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="O'qituvchi ismi..."
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm"
            @input="debouncedSearch"
          />
          <Loader2 v-if="searching" class="w-5 h-5 text-emerald-500 absolute right-3 top-1/2 -translate-y-1/2 animate-spin" />
        </div>

        <!-- Department filter -->
        <select v-model="filterDepartment" @change="loadWorkload" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha kafedralar</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>

        <!-- Day filter -->
        <select v-model="filterDay" @change="loadWorkload" class="px-3 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm">
          <option value="">Barcha kunlar</option>
          <option v-for="day in weekDays" :key="day.key" :value="day.key">{{ day.label }}</option>
        </select>
      </div>

      <!-- Active filters -->
      <div v-if="hasActiveFilters" class="mt-3 flex items-center gap-2 flex-wrap">
        <span class="text-xs text-slate-500">Filtrlar:</span>
        <span v-if="filterDepartment" class="inline-flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-xs">
          {{ filterDepartment }}
          <button @click="filterDepartment = ''; loadWorkload()" class="hover:text-emerald-900">
            <X class="w-3 h-3" />
          </button>
        </span>
        <span v-if="filterDay" class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs">
          {{ weekDays.find(d => d.key === filterDay)?.label }}
          <button @click="filterDay = ''; loadWorkload()" class="hover:text-blue-900">
            <X class="w-3 h-3" />
          </button>
        </span>
        <button @click="clearAllFilters" class="text-xs text-rose-500 hover:text-rose-700 underline ml-2">Tozalash</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- Workload Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[800px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">#</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">O'qituvchi</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Kafedra</th>
              <th class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Kun</th>
              <th class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Para</th>
              <th class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Vaqt</th>
              <th class="text-left p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Guruhlar</th>
              <th class="text-center p-3 sm:p-4 font-semibold text-slate-600 whitespace-nowrap">Holat</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(item, idx) in filteredWorkload" :key="item.id || idx" class="hover:bg-slate-50 transition-colors">
              <td class="p-3 sm:p-4 text-sm text-slate-500">{{ idx + 1 }}</td>
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-sm">
                    {{ (item.teacher_name || 'O').charAt(0) }}
                  </div>
                  <div>
                    <span class="font-medium text-slate-800">{{ item.teacher_name }}</span>
                    <p v-if="item.teacher_type" class="text-xs text-slate-500">{{ item.teacher_type }}</p>
                  </div>
                </div>
              </td>
              <td class="p-4 text-sm text-slate-600">{{ item.department || '—' }}</td>
              <td class="p-4 text-center text-sm text-slate-600">{{ item.day_name_uz || item.day_of_week || '—' }}</td>
              <td class="p-4 text-center">
                <span class="px-2 py-1 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium">
                  {{ item.lesson_number || '—' }}
                </span>
              </td>
              <td class="p-4 text-center text-sm text-slate-500">
                {{ item.start_time && item.end_time ? `${item.start_time}-${item.end_time}` : '—' }}
              </td>
              <td class="p-4 text-sm text-slate-600">{{ item.groups || '—' }}</td>
              <td class="p-4 text-center">
                <span
                  class="px-3 py-1 rounded-lg text-xs font-medium"
                  :class="item.is_busy ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'"
                >
                  {{ item.is_busy ? 'Band' : 'Bo\'sh' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredWorkload.length === 0" class="p-12 text-center">
        <CalendarClock class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Bandlik ma'lumotlari topilmadi</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { CalendarClock, Loader2, Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const searching = ref(false)
const workload = ref([])
const departments = ref([])
const searchQuery = ref('')
const filterDepartment = ref('')
const filterDay = ref('')

const weekDays = [
  { key: 'monday', label: 'Dushanba' },
  { key: 'tuesday', label: 'Seshanba' },
  { key: 'wednesday', label: 'Chorshanba' },
  { key: 'thursday', label: 'Payshanba' },
  { key: 'friday', label: 'Juma' },
  { key: 'saturday', label: 'Shanba' }
]

const hasActiveFilters = computed(() => {
  return filterDepartment.value || filterDay.value
})

// Client-side day filter for workload items
const filteredWorkload = computed(() => {
  if (!filterDay.value) return workload.value
  return workload.value.filter(w => w.day_of_week?.toLowerCase() === filterDay.value)
})

let searchTimeout = null
const debouncedSearch = () => {
  searching.value = true
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadWorkload()
  }, 400)
}

const clearAllFilters = () => {
  filterDepartment.value = ''
  filterDay.value = ''
  searchQuery.value = ''
  loadWorkload()
}

const loadWorkload = async () => {
  loading.value = true
  searching.value = true
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterDepartment.value) params.append('department', filterDepartment.value)
    const resp = await api.get(`/dean/workload?${params}`)
    workload.value = resp.items || resp.workload || resp || []
  } catch (err) {
    console.error('Dean workload error:', err)
  } finally {
    loading.value = false
    searching.value = false
  }
}

const loadDepartments = async () => {
  try {
    const resp = await api.get('/dean/workload/departments')
    departments.value = resp.departments || resp || []
  } catch (err) {
    console.error('Dean departments error:', err)
  }
}

onMounted(() => {
  loadWorkload()
  loadDepartments()
})
</script>
