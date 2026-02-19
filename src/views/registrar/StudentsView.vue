<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Talabalar</h1>
        <p class="text-sm text-slate-500 mt-1">Talabalar ro'yxati va ma'lumotlari</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200/60 p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            v-model="search"
            @input="debouncedSearch"
            type="text"
            placeholder="Ism, ID, telefon yoki passport bo'yicha qidirish..."
            class="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-300"
          />
        </div>
        <select
          v-model="selectedGroup"
          @change="loadStudents"
          class="px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
        >
          <option :value="null">Barcha guruhlar</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }} ({{ g.faculty }})</option>
        </select>
      </div>
    </div>

    <!-- Students Table -->
    <div class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200">
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Talaba</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">ID</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Guruh</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Telefon</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Passport</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Kontrakt</th>
              <th class="text-center px-4 py-3 font-semibold text-slate-600">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in students"
              :key="s.id"
              class="border-b border-slate-100 hover:bg-slate-50/50 transition-colors"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xs font-bold">
                    {{ s.name?.charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium text-slate-800">{{ s.name }}</p>
                    <p class="text-xs text-slate-400">{{ s.email || '-' }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-slate-600 font-mono text-xs">{{ s.student_id }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 bg-emerald-50 text-emerald-700 text-xs font-medium rounded-lg">
                  {{ s.group_name || '-' }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-600">{{ s.phone || '-' }}</td>
              <td class="px-4 py-3 text-slate-600 font-mono text-xs">{{ s.passport || '-' }}</td>
              <td class="px-4 py-3">
                <span :class="[
                  'text-xs font-medium',
                  s.contract_paid >= s.contract_amount ? 'text-emerald-600' : 'text-amber-600'
                ]">
                  {{ formatMoney(s.contract_paid) }} / {{ formatMoney(s.contract_amount) }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button
                    @click="viewStudent(s)"
                    class="p-1.5 text-slate-400 hover:text-emerald-500 hover:bg-emerald-50 rounded-lg transition-colors"
                    title="Batafsil ko'rish"
                  >
                    <Eye class="w-4 h-4" />
                  </button>
                  <button
                    @click="createPermitForStudent(s)"
                    class="p-1.5 text-slate-400 hover:text-teal-500 hover:bg-teal-50 rounded-lg transition-colors"
                    title="NB ruxsatnoma yaratish"
                  >
                    <FileCheck class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <p class="text-xs text-slate-500">
          Jami: {{ total }} talaba
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="page > 1 && (page--, loadStudents())"
            :disabled="page <= 1"
            class="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Oldingi
          </button>
          <span class="text-xs text-slate-600">{{ page }} / {{ totalPages }}</span>
          <button
            @click="page < totalPages && (page++, loadStudents())"
            :disabled="page >= totalPages"
            class="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Keyingi
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && students.length === 0" class="text-center py-16">
      <Users class="w-12 h-12 text-slate-300 mx-auto mb-3" />
      <p class="text-slate-500">Talabalar topilmadi</p>
    </div>

    <!-- Student Detail Modal -->
    <Teleport to="body">
      <div v-if="showDetail" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showDetail = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
            <h3 class="text-lg font-bold text-slate-800">Talaba ma'lumotlari</h3>
            <button @click="showDetail = false" class="p-2 hover:bg-slate-100 rounded-xl transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>
          <div v-if="detailData" class="p-6 space-y-6">
            <!-- Student Info -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-xs font-medium text-slate-500">To'liq ism</label>
                <p class="text-sm font-semibold text-slate-800">{{ detailData.student.name }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">Talaba ID</label>
                <p class="text-sm font-mono text-slate-800">{{ detailData.student.student_id }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">Guruh</label>
                <p class="text-sm text-slate-800">{{ detailData.student.group_name }} ({{ detailData.student.faculty }})</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">Kurs</label>
                <p class="text-sm text-slate-800">{{ detailData.student.course_year }}-kurs</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">Telefon</label>
                <p class="text-sm text-slate-800">{{ detailData.student.phone || '-' }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">Passport</label>
                <p class="text-sm font-mono text-slate-800">{{ detailData.student.passport || '-' }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">JSHSHIR</label>
                <p class="text-sm font-mono text-slate-800">{{ detailData.student.jshshir || '-' }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-slate-500">Tug'ilgan sana</label>
                <p class="text-sm text-slate-800">{{ detailData.student.birth_date || '-' }}</p>
              </div>
            </div>

            <!-- Attendance Stats -->
            <div class="bg-slate-50 rounded-xl p-4">
              <h4 class="text-sm font-semibold text-slate-700 mb-3">Davomat statistikasi</h4>
              <div class="grid grid-cols-3 gap-4">
                <div class="text-center">
                  <p class="text-xl font-bold text-slate-800">{{ detailData.attendance.total_days }}</p>
                  <p class="text-xs text-slate-500">Jami darslar</p>
                </div>
                <div class="text-center">
                  <p class="text-xl font-bold text-emerald-600">{{ detailData.attendance.present_days }}</p>
                  <p class="text-xs text-slate-500">Kelgan</p>
                </div>
                <div class="text-center">
                  <p class="text-xl font-bold text-rose-600">{{ detailData.attendance.absent_days }}</p>
                  <p class="text-xs text-slate-500">Kelmagan</p>
                </div>
              </div>
              <div class="mt-3">
                <div class="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-500 rounded-full" :style="{ width: detailData.attendance.attendance_rate + '%' }"></div>
                </div>
                <p class="text-xs text-slate-500 mt-1 text-right">{{ detailData.attendance.attendance_rate }}% davomat</p>
              </div>
            </div>

            <!-- NB Permits -->
            <div v-if="detailData.permits.length > 0">
              <h4 class="text-sm font-semibold text-slate-700 mb-3">NB Ruxsatnomalar</h4>
              <div class="space-y-2">
                <div
                  v-for="p in detailData.permits"
                  :key="p.id"
                  class="flex items-center justify-between p-3 bg-slate-50 rounded-xl"
                >
                  <div>
                    <p class="text-sm font-medium text-slate-800">{{ p.subject_name }}</p>
                    <p class="text-xs text-slate-500">{{ p.permit_code }} • {{ p.issue_date }}</p>
                  </div>
                  <span :class="[
                    'px-2 py-1 text-xs font-medium rounded-lg',
                    statusColor(p.status)
                  ]">
                    {{ statusLabel(p.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Loading -->
    <div v-if="loading" class="fixed inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  </div>
</template>

<script setup>
import { Eye, FileCheck, Search, Users, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(false)
const students = ref([])
const groups = ref([])
const search = ref('')
const selectedGroup = ref(null)
const page = ref(1)
const total = ref(0)
const limit = 50

const showDetail = ref(false)
const detailData = ref(null)

let searchTimeout = null

const totalPages = computed(() => Math.ceil(total.value / limit) || 1)

const formatMoney = (val) => {
  if (!val) return '0'
  return Number(val).toLocaleString('uz-UZ')
}

const statusColor = (status) => {
  const map = {
    issued: 'bg-blue-100 text-blue-700',
    pending: 'bg-amber-100 text-amber-700',
    in_progress: 'bg-purple-100 text-purple-700',
    approved: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-rose-100 text-rose-700',
    expired: 'bg-slate-100 text-slate-600',
    cancelled: 'bg-slate-100 text-slate-500',
  }
  return map[status] || 'bg-slate-100 text-slate-600'
}

const statusLabel = (status) => {
  const map = {
    issued: 'Berilgan',
    pending: 'Kutilmoqda',
    in_progress: 'Jarayonda',
    approved: 'Tasdiqlangan ✓',
    rejected: 'Rad etilgan',
    expired: 'Muddati tugagan',
    cancelled: 'Bekor qilingan',
  }
  return map[status] || status
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadStudents()
  }, 400)
}

const loadStudents = async () => {
  loading.value = true
  try {
    const params = { page: page.value, limit }
    if (search.value) params.search = search.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    
    const resp = await api.get('/registrar/students', { params })
    students.value = resp.items || []
    total.value = resp.total || 0
  } catch (err) {
    console.error('Students error:', err)
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

const viewStudent = async (student) => {
  try {
    const resp = await api.get(`/registrar/students/${student.id}`)
    detailData.value = resp
    showDetail.value = true
  } catch (err) {
    console.error('Student detail error:', err)
  }
}

const createPermitForStudent = (student) => {
  router.push({ path: '/registrar/nb-permits', query: { student_id: student.id, student_name: student.name } })
}

onMounted(() => {
  loadStudents()
  loadGroups()
})
</script>
