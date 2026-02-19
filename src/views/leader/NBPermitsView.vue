<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600 p-6 text-white">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-white/10"></div>
      <div class="relative">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
            <FileCheck :size="24" />
          </div>
          <div>
            <h1 class="text-xl font-bold">Guruh NB Ruxsatnomalari</h1>
            <p class="text-sm text-white/80">{{ groupName ? groupName + ' guruhi' : 'Guruhingiz' }} talabalarining ruxsatnomalari</p>
          </div>
        </div>
        <div class="mt-4 flex flex-wrap gap-3">
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ permits.length }}</p>
            <p class="text-xs text-white/80">Jami</p>
          </div>
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ activeCount }}</p>
            <p class="text-xs text-white/80">Faol</p>
          </div>
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ approvedCount }}</p>
            <p class="text-xs text-white/80">Tasdiqlangan</p>
          </div>
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ rejectedCount }}</p>
            <p class="text-xs text-white/80">Rad etilgan</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
      <span class="ml-3 text-slate-500">Yuklanmoqda...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="permits.length === 0" class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
        <FileCheck :size="32" class="text-slate-400" />
      </div>
      <h3 class="mt-4 text-lg font-semibold text-slate-800">NB ruxsatnomalar yo'q</h3>
      <p class="mt-2 text-sm text-slate-500">Guruhingiz talabalariga hali NB ruxsatnomasi berilmagan</p>
    </div>

    <!-- Content -->
    <div v-else class="space-y-4">
      <!-- Filters -->
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex gap-2 overflow-x-auto pb-1 flex-1">
          <button
            v-for="f in statusFilters"
            :key="f.value"
            @click="activeFilter = f.value"
            :class="[
              'whitespace-nowrap rounded-xl px-4 py-2 text-sm font-medium transition-all',
              activeFilter === f.value
                ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            ]"
          >
            {{ f.label }}
            <span v-if="f.count > 0" class="ml-1.5 rounded-full bg-white/20 px-1.5 py-0.5 text-xs">{{ f.count }}</span>
          </button>
        </div>
        <!-- Search -->
        <div class="relative">
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Talaba yoki fan qidirish..."
            class="w-full sm:w-64 rounded-xl border border-slate-200 bg-white pl-9 pr-4 py-2 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
          />
        </div>
      </div>

      <!-- Table (desktop) -->
      <div class="hidden lg:block rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Talaba</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Fan</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Turi</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">O'qituvchi</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Sana</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Holat</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Baho</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="permit in filteredPermits" :key="permit.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-4 py-3">
                <div>
                  <p class="font-medium text-slate-800 text-sm">{{ permit.student_name }}</p>
                  <p class="text-xs text-slate-400">{{ permit.student_sid }}</p>
                </div>
              </td>
              <td class="px-4 py-3">
                <p class="text-sm text-slate-700">{{ permit.subject_name }}</p>
                <p class="text-xs text-slate-400">{{ permit.semester }}-sem • {{ permit.academic_year }}</p>
              </td>
              <td class="px-4 py-3">
                <span :class="[
                  'rounded-lg px-2 py-1 text-xs font-medium',
                  permit.nb_type === 'nb' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                ]">
                  {{ permit.nb_type === 'nb' ? 'NB' : 'Atrabotka' }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ permit.teacher_name || '—' }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ formatDate(permit.issue_date) }}</td>
              <td class="px-4 py-3">
                <span :class="[
                  'rounded-lg px-2.5 py-1 text-xs font-semibold',
                  statusColors[permit.status]?.badge || 'bg-slate-100 text-slate-600'
                ]">
                  {{ statusLabels[permit.status] || permit.status }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span v-if="permit.result_grade" class="rounded bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">
                  {{ permit.result_grade }}
                </span>
                <span v-else class="text-xs text-slate-400">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cards (mobile) -->
      <div class="lg:hidden space-y-3">
        <div v-for="permit in filteredPermits" :key="permit.id"
          class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="font-semibold text-slate-800">{{ permit.student_name }}</p>
              <p class="text-xs text-slate-400">{{ permit.student_sid }}</p>
            </div>
            <span :class="[
              'flex-shrink-0 rounded-lg px-2.5 py-1 text-xs font-semibold',
              statusColors[permit.status]?.badge || 'bg-slate-100 text-slate-600'
            ]">
              {{ statusLabels[permit.status] || permit.status }}
            </span>
          </div>
          <div class="mt-3 space-y-1.5 text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500">Fan:</span>
              <span class="font-medium text-slate-700">{{ permit.subject_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Turi:</span>
              <span :class="permit.nb_type === 'nb' ? 'text-red-600 font-medium' : 'text-orange-600 font-medium'">
                {{ permit.nb_type === 'nb' ? 'NB' : 'Atrabotka' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">O'qituvchi:</span>
              <span class="text-slate-700">{{ permit.teacher_name || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Sana:</span>
              <span class="text-slate-700">{{ formatDate(permit.issue_date) }}</span>
            </div>
            <div v-if="permit.result_grade" class="flex justify-between">
              <span class="text-slate-500">Baho:</span>
              <span class="font-bold text-emerald-600">{{ permit.result_grade }}</span>
            </div>
          </div>

          <!-- Result info -->
          <div v-if="permit.status === 'approved'" class="mt-3 rounded-lg bg-green-50 border border-green-200 p-2.5">
            <div class="flex items-center gap-2">
              <CheckCircle :size="14" class="text-green-600" />
              <span class="text-xs font-medium text-green-800">NB oqlangan</span>
            </div>
            <p v-if="permit.teacher_notes" class="mt-1 text-xs text-green-700">{{ permit.teacher_notes }}</p>
          </div>
          <div v-if="permit.status === 'rejected'" class="mt-3 rounded-lg bg-red-50 border border-red-200 p-2.5">
            <div class="flex items-center gap-2">
              <XCircle :size="14" class="text-red-600" />
              <span class="text-xs font-medium text-red-800">Rad etilgan</span>
            </div>
            <p v-if="permit.teacher_notes" class="mt-1 text-xs text-red-700">{{ permit.teacher_notes }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { CheckCircle, FileCheck, Search, XCircle } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const permits = ref([])
const groupName = ref('')
const loading = ref(true)
const activeFilter = ref('all')
const searchQuery = ref('')

const statusLabels = {
  issued: 'Berilgan',
  pending: 'Kutilmoqda',
  in_progress: 'Jarayonda',
  approved: 'Tasdiqlangan',
  rejected: 'Rad etilgan',
  expired: 'Muddati tugagan',
  cancelled: "Bekor qilingan"
}

const statusColors = {
  issued: { badge: 'bg-blue-100 text-blue-700' },
  pending: { badge: 'bg-amber-100 text-amber-700' },
  in_progress: { badge: 'bg-indigo-100 text-indigo-700' },
  approved: { badge: 'bg-green-100 text-green-700' },
  rejected: { badge: 'bg-red-100 text-red-700' },
  expired: { badge: 'bg-slate-100 text-slate-600' },
  cancelled: { badge: 'bg-slate-100 text-slate-500' }
}

const activeCount = computed(() => permits.value.filter(p => ['issued', 'pending', 'in_progress'].includes(p.status)).length)
const approvedCount = computed(() => permits.value.filter(p => p.status === 'approved').length)
const rejectedCount = computed(() => permits.value.filter(p => p.status === 'rejected').length)

const statusFilters = computed(() => [
  { label: 'Barchasi', value: 'all', count: permits.value.length },
  { label: 'Faol', value: 'active', count: activeCount.value },
  { label: 'Tasdiqlangan', value: 'approved', count: approvedCount.value },
  { label: 'Rad etilgan', value: 'rejected', count: rejectedCount.value }
])

const filteredPermits = computed(() => {
  let result = permits.value
  if (activeFilter.value === 'active') result = result.filter(p => ['issued', 'pending', 'in_progress'].includes(p.status))
  else if (activeFilter.value !== 'all') result = result.filter(p => p.status === activeFilter.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      (p.student_name || '').toLowerCase().includes(q) ||
      (p.subject_name || '').toLowerCase().includes(q) ||
      (p.student_sid || '').toLowerCase().includes(q)
    )
  }
  return result
})

const formatDate = (d) => {
  if (!d) return '—'
  const dt = new Date(d)
  return dt.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const loadPermits = async () => {
  loading.value = true
  try {
    const data = await api.get('/registrar/group-permits')
    permits.value = data.items || []
    groupName.value = data.group_name || ''
  } catch (e) {
    console.error('Error loading group permits:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadPermits)
</script>
