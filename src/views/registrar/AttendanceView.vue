<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Davomat</h1>
        <p class="text-sm text-slate-500 mt-1">Talabalar davomatini ko'rish (faqat o'qish)</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200/60 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Sanadan</label>
          <input
            v-model="dateFrom"
            @change="loadAttendance"
            type="date"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Sanagacha</label>
          <input
            v-model="dateTo"
            @change="loadAttendance"
            type="date"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Guruh</label>
          <select
            v-model="selectedGroup"
            @change="loadAttendance"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
          >
            <option :value="null">Barcha guruhlar</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Status</label>
          <select
            v-model="statusFilter"
            @change="loadAttendance"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
          >
            <option :value="null">Barcha status</option>
            <option value="present">Kelgan</option>
            <option value="absent">Kelmagan</option>
            <option value="late">Kechikkan</option>
            <option value="excused">Sababli</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Stats Row -->
    <div v-if="attendanceStats" class="grid grid-cols-2 sm:grid-cols-5 gap-3">
      <div class="bg-white rounded-xl border border-slate-200/60 p-3 text-center">
        <p class="text-lg font-bold text-slate-800">{{ attendanceStats.total }}</p>
        <p class="text-xs text-slate-500">Jami</p>
      </div>
      <div class="bg-white rounded-xl border border-emerald-200/60 p-3 text-center">
        <p class="text-lg font-bold text-emerald-600">{{ attendanceStats.present }}</p>
        <p class="text-xs text-slate-500">Kelgan</p>
      </div>
      <div class="bg-white rounded-xl border border-rose-200/60 p-3 text-center">
        <p class="text-lg font-bold text-rose-600">{{ attendanceStats.absent }}</p>
        <p class="text-xs text-slate-500">Kelmagan</p>
      </div>
      <div class="bg-white rounded-xl border border-amber-200/60 p-3 text-center">
        <p class="text-lg font-bold text-amber-600">{{ attendanceStats.late }}</p>
        <p class="text-xs text-slate-500">Kechikkan</p>
      </div>
      <div class="bg-white rounded-xl border border-blue-200/60 p-3 text-center">
        <p class="text-lg font-bold text-blue-600">{{ attendanceStats.excused }}</p>
        <p class="text-xs text-slate-500">Sababli</p>
      </div>
    </div>

    <!-- Attendance Table -->
    <div class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200">
              <th class="text-left px-4 py-3 font-semibold text-slate-600">#</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Talaba</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Guruh</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Fan</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Dars</th>
              <th class="text-center px-4 py-3 font-semibold text-slate-600">Status</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Vaqt</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(a, idx) in records"
              :key="a.id"
              class="border-b border-slate-100 hover:bg-slate-50/50 transition-colors"
            >
              <td class="px-4 py-3 text-slate-400 text-xs">{{ idx + 1 }}</td>
              <td class="px-4 py-3 font-medium text-slate-800">{{ a.student_name }}</td>
              <td class="px-4 py-3 text-slate-600">{{ a.group_name || '-' }}</td>
              <td class="px-4 py-3 text-slate-600">{{ a.subject || '-' }}</td>
              <td class="px-4 py-3 text-slate-600">{{ a.lesson_number || '-' }}-dars</td>
              <td class="px-4 py-3 text-center">
                <span :class="[
                  'inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full',
                  statusBadge(a.status)
                ]">
                  <span class="w-1.5 h-1.5 rounded-full" :class="statusDot(a.status)"></span>
                  {{ statusLabel(a.status) }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ a.check_in_time || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && records.length === 0" class="text-center py-16">
        <ClipboardCheck class="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-500">Bu sana uchun davomat ma'lumotlari yo'q</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="fixed inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  </div>
</template>

<script setup>
import { ClipboardCheck } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const records = ref([])
const groups = ref([])
const attendanceStats = ref(null)
const dateFrom = ref(new Date().toISOString().split('T')[0])
const dateTo = ref(new Date().toISOString().split('T')[0])
const selectedGroup = ref(null)
const statusFilter = ref(null)

const statusBadge = (status) => {
  const map = {
    present: 'bg-emerald-100 text-emerald-700',
    absent: 'bg-rose-100 text-rose-700',
    late: 'bg-amber-100 text-amber-700',
    excused: 'bg-blue-100 text-blue-700',
  }
  return map[status] || 'bg-slate-100 text-slate-600'
}

const statusDot = (status) => {
  const map = {
    present: 'bg-emerald-500',
    absent: 'bg-rose-500',
    late: 'bg-amber-500',
    excused: 'bg-blue-500',
  }
  return map[status] || 'bg-slate-400'
}

const statusLabel = (status) => {
  const map = {
    present: 'Kelgan',
    absent: 'Kelmagan',
    late: 'Kechikkan',
    excused: 'Sababli',
  }
  return map[status] || status
}

const loadAttendance = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    if (statusFilter.value) params.status_filter = statusFilter.value

    const resp = await api.get('/registrar/attendance', { params })
    records.value = resp.items || []
    attendanceStats.value = resp.stats || null
  } catch (err) {
    console.error('Attendance error:', err)
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  try {
    const resp = await api.get('/registrar/groups')
    groups.value = resp.items || []
  } catch (err) {
    console.error('Groups error:', err)
  }
}

onMounted(() => {
  loadAttendance()
  loadGroups()
})
</script>
