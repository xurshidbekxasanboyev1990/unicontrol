<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 p-6 text-white">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-white/10"></div>
      <div class="relative">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
            <FileCheck :size="24" />
          </div>
          <div>
            <h1 class="text-xl font-bold">NB Ruxsatnomalarim</h1>
            <p class="text-sm text-white/80">Sizga berilgan NB/atrabotka ruxsatnomalari</p>
          </div>
        </div>
        <div class="mt-4 flex gap-4">
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
      <p class="mt-2 text-sm text-slate-500">Sizga hali NB/atrabotka ruxsatnomasi berilmagan</p>
    </div>

    <!-- Permits List -->
    <div v-else class="space-y-4">
      <!-- Filter -->
      <div class="flex gap-2 overflow-x-auto pb-2">
        <button
          v-for="f in filters"
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

      <!-- Cards -->
      <div v-for="permit in filteredPermits" :key="permit.id" 
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md"
      >
        <div class="flex flex-col sm:flex-row sm:items-start gap-4">
          <!-- Status Icon -->
          <div :class="[
            'flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl',
            statusColors[permit.status]?.bg || 'bg-slate-100'
          ]">
            <component :is="statusIcons[permit.status]" :size="22" :class="statusColors[permit.status]?.text || 'text-slate-500'" />
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h3 class="font-semibold text-slate-800">{{ permit.subject_name }}</h3>
                <p class="mt-0.5 text-sm text-slate-500">
                  {{ permit.nb_type === 'nb' ? 'NB' : 'Atrabotka' }} • {{ permit.semester }}-semestr • {{ permit.academic_year }}
                </p>
              </div>
              <span :class="[
                'flex-shrink-0 rounded-lg px-3 py-1 text-xs font-semibold',
                statusColors[permit.status]?.badge || 'bg-slate-100 text-slate-600'
              ]">
                {{ statusLabels[permit.status] || permit.status }}
              </span>
            </div>

            <div class="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
              <div class="flex items-center gap-2 text-slate-500">
                <User :size="14" class="text-slate-400" />
                <span>O'qituvchi: <strong class="text-slate-700">{{ permit.teacher_name || '—' }}</strong></span>
              </div>
              <div class="flex items-center gap-2 text-slate-500">
                <Calendar :size="14" class="text-slate-400" />
                <span>Berilgan: <strong class="text-slate-700">{{ formatDate(permit.issue_date) }}</strong></span>
              </div>
              <div v-if="permit.expiry_date" class="flex items-center gap-2 text-slate-500">
                <Clock :size="14" class="text-slate-400" />
                <span>Muddat: <strong class="text-slate-700">{{ formatDate(permit.expiry_date) }}</strong></span>
              </div>
            </div>

            <!-- Result -->
            <div v-if="permit.status === 'approved'" class="mt-3 rounded-lg bg-green-50 border border-green-200 p-3">
              <div class="flex items-center gap-2">
                <CheckCircle :size="16" class="text-green-600" />
                <span class="text-sm font-medium text-green-800">NB oqlangan!</span>
                <span v-if="permit.result_grade" class="ml-auto rounded bg-green-200 px-2 py-0.5 text-xs font-bold text-green-800">
                  Baho: {{ permit.result_grade }}
                </span>
              </div>
              <p v-if="permit.teacher_notes" class="mt-1.5 text-xs text-green-700">{{ permit.teacher_notes }}</p>
              <p v-if="permit.completed_date" class="mt-1 text-xs text-green-600">Tasdiqlangan: {{ formatDate(permit.completed_date) }}</p>
            </div>

            <div v-if="permit.status === 'rejected'" class="mt-3 rounded-lg bg-red-50 border border-red-200 p-3">
              <div class="flex items-center gap-2">
                <XCircle :size="16" class="text-red-600" />
                <span class="text-sm font-medium text-red-800">Rad etilgan</span>
              </div>
              <p v-if="permit.teacher_notes" class="mt-1.5 text-xs text-red-700">{{ permit.teacher_notes }}</p>
            </div>

            <!-- Permit Code -->
            <div class="mt-3 flex items-center gap-2">
              <code class="rounded bg-slate-100 px-2 py-1 text-xs font-mono text-slate-600">{{ permit.permit_code }}</code>
              <span class="text-xs text-slate-400">Chiqargan: {{ permit.issued_by_name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, Calendar, CheckCircle, Clock, FileCheck, FileText, Loader, User, XCircle } from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'
import api from '../../services/api'

const permits = ref([])
const loading = ref(true)
const activeFilter = ref('all')

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
  issued: { bg: 'bg-blue-100', text: 'text-blue-600', badge: 'bg-blue-100 text-blue-700' },
  pending: { bg: 'bg-amber-100', text: 'text-amber-600', badge: 'bg-amber-100 text-amber-700' },
  in_progress: { bg: 'bg-indigo-100', text: 'text-indigo-600', badge: 'bg-indigo-100 text-indigo-700' },
  approved: { bg: 'bg-green-100', text: 'text-green-600', badge: 'bg-green-100 text-green-700' },
  rejected: { bg: 'bg-red-100', text: 'text-red-600', badge: 'bg-red-100 text-red-700' },
  expired: { bg: 'bg-slate-100', text: 'text-slate-500', badge: 'bg-slate-100 text-slate-600' },
  cancelled: { bg: 'bg-slate-100', text: 'text-slate-400', badge: 'bg-slate-100 text-slate-500' }
}

const statusIcons = {
  issued: markRaw(FileText),
  pending: markRaw(Clock),
  in_progress: markRaw(Loader),
  approved: markRaw(CheckCircle),
  rejected: markRaw(XCircle),
  expired: markRaw(AlertCircle),
  cancelled: markRaw(XCircle)
}

const activeCount = computed(() => permits.value.filter(p => ['issued', 'pending', 'in_progress'].includes(p.status)).length)
const approvedCount = computed(() => permits.value.filter(p => p.status === 'approved').length)

const filters = computed(() => [
  { label: 'Barchasi', value: 'all', count: permits.value.length },
  { label: 'Faol', value: 'active', count: activeCount.value },
  { label: 'Tasdiqlangan', value: 'approved', count: approvedCount.value },
  { label: 'Rad etilgan', value: 'rejected', count: permits.value.filter(p => p.status === 'rejected').length }
])

const filteredPermits = computed(() => {
  if (activeFilter.value === 'all') return permits.value
  if (activeFilter.value === 'active') return permits.value.filter(p => ['issued', 'pending', 'in_progress'].includes(p.status))
  return permits.value.filter(p => p.status === activeFilter.value)
})

const formatDate = (d) => {
  if (!d) return '—'
  const dt = new Date(d)
  return dt.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const loadPermits = async () => {
  loading.value = true
  try {
    const data = await api.get('/registrar/my-permits')
    permits.value = data.items || []
  } catch (e) {
    console.error('Error loading permits:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadPermits)
</script>
