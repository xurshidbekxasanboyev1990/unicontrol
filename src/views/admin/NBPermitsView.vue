<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-violet-600 p-6 text-white">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-white/10"></div>
      <div class="relative">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <FileCheck :size="24" />
            </div>
            <div>
              <h1 class="text-xl font-bold">NB Ruxsatnomalar</h1>
              <p class="text-sm text-white/80">Barcha NB/Atrabotka ruxsatnomalari boshqaruvi</p>
            </div>
          </div>
        </div>
        <div class="mt-4 flex flex-wrap gap-3">
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ stats.total }}</p>
            <p class="text-xs text-white/80">Jami</p>
          </div>
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ stats.active }}</p>
            <p class="text-xs text-white/80">Faol</p>
          </div>
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ stats.approved }}</p>
            <p class="text-xs text-white/80">Tasdiqlangan</p>
          </div>
          <div class="rounded-lg bg-white/15 px-4 py-2 backdrop-blur">
            <p class="text-2xl font-bold">{{ stats.rejected }}</p>
            <p class="text-xs text-white/80">Rad etilgan</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex gap-2 overflow-x-auto flex-1">
          <button
            v-for="f in statusFilters"
            :key="f.value"
            @click="activeFilter = f.value; loadPermits()"
            :class="[
              'whitespace-nowrap rounded-xl px-4 py-2 text-sm font-medium transition-all',
              activeFilter === f.value
                ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
            ]"
          >
            {{ f.label }}
          </button>
        </div>
        <div class="relative">
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Kod, fan yoki talaba..."
            class="w-full sm:w-64 rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-4 py-2 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
          />
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
      <span class="ml-3 text-slate-500">Yuklanmoqda...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="permits.length === 0" class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
      <FileCheck :size="40" class="mx-auto text-slate-300 mb-3" />
      <h3 class="text-lg font-semibold text-slate-700">Ruxsatnomalar topilmadi</h3>
      <p class="text-sm text-slate-500 mt-1">Hozircha NB ruxsatnomalari yo'q</p>
    </div>

    <!-- Table -->
    <div v-else class="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Kod</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Talaba</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Guruh</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Fan</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Turi</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">O'qituvchi</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Chiqargan</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Sana</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Holat</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Baho</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Amallar</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="p in permits" :key="p.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-4 py-3">
                <code class="text-xs font-mono text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">{{ p.permit_code }}</code>
              </td>
              <td class="px-4 py-3">
                <p class="text-sm font-medium text-slate-800">{{ p.student_name }}</p>
                <p class="text-xs text-slate-400">{{ p.student_sid }}</p>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ p.group_name || '—' }}</td>
              <td class="px-4 py-3">
                <p class="text-sm text-slate-700">{{ p.subject_name }}</p>
                <p class="text-xs text-slate-400">{{ p.semester }}-sem • {{ p.academic_year }}</p>
              </td>
              <td class="px-4 py-3">
                <span :class="[
                  'rounded-lg px-2 py-0.5 text-xs font-medium',
                  p.nb_type === 'nb' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                ]">{{ p.nb_type === 'nb' ? 'NB' : 'Atrabotka' }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ p.teacher_name || '—' }}</td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ p.issued_by_name || '—' }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ formatDate(p.issue_date) }}</td>
              <td class="px-4 py-3">
                <span :class="['rounded-lg px-2.5 py-1 text-xs font-semibold', statusBadge(p.status)]">
                  {{ statusLabel(p.status) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span v-if="p.result_grade" class="rounded bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">{{ p.result_grade }}</span>
                <span v-else class="text-xs text-slate-400">—</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button @click="viewCheck(p)" class="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors" title="Ko'rish">
                    <Eye :size="16" />
                  </button>
                  <button @click="printCheck(p)" class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="Print">
                    <Printer :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-slate-200 bg-slate-50">
        <p class="text-xs text-slate-500">Jami: {{ total }} ta ruxsatnoma</p>
        <div class="flex gap-1">
          <button
            v-for="pg in totalPages"
            :key="pg"
            @click="page = pg; loadPermits()"
            :class="[
              'px-3 py-1 text-xs rounded-lg font-medium transition-colors',
              page === pg ? 'bg-emerald-500 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
            ]"
          >{{ pg }}</button>
        </div>
      </div>
    </div>

    <!-- ============ CHECK PREVIEW MODAL ============ -->
    <Teleport to="body">
      <div v-if="showCheckModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showCheckModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white px-6 py-4 border-b border-slate-200 rounded-t-2xl flex items-center justify-between z-10">
            <h3 class="text-lg font-bold text-slate-800">NB Ruxsatnoma cheki</h3>
            <div class="flex items-center gap-2">
              <button
                @click="printFromPreview"
                class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500 text-white rounded-lg text-sm font-medium hover:bg-emerald-600 transition-colors"
              >
                <Printer class="w-4 h-4" />
                Print
              </button>
              <button @click="showCheckModal = false" class="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100">
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>
          <div class="p-6">
            <div v-if="checkData" class="border-2 border-slate-800 rounded-xl p-5 space-y-4">
              <div class="text-center border-b border-dashed border-slate-300 pb-3">
                <h2 class="text-lg font-bold text-slate-800">UNICONTROL</h2>
                <p class="text-[10px] text-slate-500 uppercase tracking-widest">NB / Atrabotka Ruxsatnomasi</p>
                <span :class="[
                  'inline-block mt-2 px-3 py-1 rounded-lg text-xs font-bold',
                  checkData.status === 'approved' ? 'bg-emerald-500 text-white' :
                  checkData.status === 'rejected' ? 'bg-red-500 text-white' :
                  'bg-amber-100 text-amber-800'
                ]">
                  {{ checkData.status === 'approved' ? '✓ NB OQLANGAN' : checkData.status === 'rejected' ? '✗ RAD ETILGAN' : '⏳ KUTILMOQDA' }}
                </span>
              </div>
              <div class="text-center">
                <p class="text-[10px] text-slate-500">Ruxsatnoma kodi</p>
                <p class="text-base font-mono font-bold text-emerald-600">{{ checkData.permit_code }}</p>
              </div>
              <div class="border border-slate-200 rounded-lg p-3 space-y-1.5">
                <div class="flex justify-between text-xs"><span class="text-slate-500">Talaba:</span><span class="text-slate-800 font-medium">{{ checkData.student?.name }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">ID:</span><span class="text-slate-800 font-medium">{{ checkData.student?.student_id }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Guruh:</span><span class="text-slate-800 font-medium">{{ checkData.student?.group_name }}</span></div>
                <div v-if="checkData.student?.faculty" class="flex justify-between text-xs"><span class="text-slate-500">Fakultet:</span><span class="text-slate-800 font-medium">{{ checkData.student?.faculty }}</span></div>
              </div>
              <div class="border border-slate-200 rounded-lg p-3 space-y-1.5">
                <div class="flex justify-between text-xs"><span class="text-slate-500">Fan:</span><span class="text-slate-800 font-medium">{{ checkData.subject_name }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Turi:</span><span class="text-slate-800 font-medium">{{ checkData.nb_type === 'nb' ? 'NB' : 'Atrabotka' }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Semestr:</span><span class="text-slate-800 font-medium">{{ checkData.semester }}-semestr • {{ checkData.academic_year }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">O'qituvchi:</span><span class="text-slate-800 font-medium">{{ checkData.teacher_name || '—' }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Berilgan:</span><span class="text-slate-800 font-medium">{{ checkData.issue_date }}</span></div>
                <div v-if="checkData.expiry_date" class="flex justify-between text-xs"><span class="text-slate-500">Muddat:</span><span class="text-slate-800 font-medium">{{ checkData.expiry_date }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Chiqargan:</span><span class="text-slate-800 font-medium">{{ checkData.issued_by_name }}</span></div>
              </div>
              <div v-if="checkData.result_grade" class="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center">
                <p class="text-[10px] text-emerald-600">Baho / Natija</p>
                <p class="text-xl font-bold text-emerald-700">{{ checkData.result_grade }}</p>
              </div>
              <div v-if="checkData.teacher_notes" class="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <p class="text-[10px] text-slate-500 mb-1">O'qituvchi izohi:</p>
                <p class="text-xs text-slate-700">{{ checkData.teacher_notes }}</p>
              </div>
              <div class="border-t border-dashed border-slate-300 pt-3 text-center space-y-1">
                <p class="font-mono text-[8px] text-slate-400">{{ checkData.verification_hash }}</p>
                <p :class="['text-xs font-semibold', checkData.is_valid ? 'text-emerald-600' : 'text-red-500']">
                  {{ checkData.is_valid ? '🛡️ Haqiqiy hujjat' : '⚠️ Tasdiqlanmagan' }}
                </p>
                <p class="text-[9px] text-slate-400">Print: {{ checkData.print_count }} marta</p>
              </div>
            </div>
            <div v-else class="flex items-center justify-center py-12">
              <div class="h-8 w-8 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { Eye, FileCheck, Printer, Search, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const permits = ref([])
const loading = ref(true)
const total = ref(0)
const page = ref(1)
const limit = 30
const activeFilter = ref('')
const searchQuery = ref('')
const showCheckModal = ref(false)
const checkData = ref(null)

let searchTimeout = null

const statusFilters = [
  { label: 'Barchasi', value: '' },
  { label: 'Berilgan', value: 'issued' },
  { label: 'Kutilmoqda', value: 'pending' },
  { label: 'Jarayonda', value: 'in_progress' },
  { label: 'Tasdiqlangan', value: 'approved' },
  { label: 'Rad etilgan', value: 'rejected' },
  { label: 'Muddati o\'tgan', value: 'expired' },
  { label: 'Bekor qilingan', value: 'cancelled' }
]

const stats = computed(() => {
  const all = permits.value
  return {
    total: total.value,
    active: all.filter(p => ['issued', 'pending', 'in_progress'].includes(p.status)).length,
    approved: all.filter(p => p.status === 'approved').length,
    rejected: all.filter(p => p.status === 'rejected').length
  }
})

const totalPages = computed(() => Math.ceil(total.value / limit))

const statusLabel = (s) => {
  const m = { issued: 'Berilgan', pending: 'Kutilmoqda', in_progress: 'Jarayonda', approved: 'Tasdiqlangan', rejected: 'Rad etilgan', expired: 'Muddati o\'tgan', cancelled: 'Bekor qilingan' }
  return m[s] || s
}

const statusBadge = (s) => {
  const m = { issued: 'bg-blue-100 text-blue-700', pending: 'bg-amber-100 text-amber-700', in_progress: 'bg-indigo-100 text-indigo-700', approved: 'bg-green-100 text-green-700', rejected: 'bg-red-100 text-red-700', expired: 'bg-slate-100 text-slate-600', cancelled: 'bg-slate-100 text-slate-500' }
  return m[s] || 'bg-slate-100 text-slate-600'
}

const formatDate = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { page.value = 1; loadPermits() }, 400)
}

const loadPermits = async () => {
  loading.value = true
  try {
    let url = `/registrar/permits?page=${page.value}&limit=${limit}`
    if (activeFilter.value) url += `&status_filter=${activeFilter.value}`
    if (searchQuery.value) url += `&search=${encodeURIComponent(searchQuery.value)}`
    const data = await api.get(url)
    permits.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('Error loading permits:', e)
  } finally {
    loading.value = false
  }
}

const viewCheck = async (permit) => {
  checkData.value = null
  showCheckModal.value = true
  try {
    const resp = await api.get(`/registrar/permits/${permit.id}/check`)
    checkData.value = resp
  } catch (e) {
    console.error('Check error:', e)
    showCheckModal.value = false
  }
}

const buildCheckHtml = (resp) => `
  <html>
    <head>
      <title>NB Ruxsatnoma - ${resp.permit_code}</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .check { border: 2px solid #1e293b; border-radius: 8px; padding: 20px; max-width: 350px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 1px dashed #94a3b8; padding-bottom: 12px; margin-bottom: 12px; }
        .header h2 { font-size: 18px; } .header p { font-size: 10px; color: #64748b; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 13px; margin-top: 8px; }
        .approved { background: #10b981; color: #fff; } .pending { background: #fef3c7; color: #92400e; } .rejected { background: #ef4444; color: #fff; }
        .code { text-align: center; margin: 12px 0; }
        .code .val { font-size: 16px; font-family: monospace; font-weight: bold; color: #059669; }
        .box { border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; margin-bottom: 10px; }
        .row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
        .row .l { color: #64748b; } .row .v { color: #1e293b; font-weight: 500; }
        .footer { border-top: 1px dashed #94a3b8; padding-top: 10px; text-align: center; }
        .hash { font-size: 8px; font-family: monospace; color: #94a3b8; }
        @media print { body { padding: 0; } }
      </style>
    </head>
    <body>
      <div class="check">
        <div class="header">
          <h2>UNICONTROL</h2>
          <p>NB / ATRABOTKA RUXSATNOMASI</p>
          <span class="status ${resp.status === 'approved' ? 'approved' : resp.status === 'rejected' ? 'rejected' : 'pending'}">
            ${resp.status === 'approved' ? '✓ NB OQLANGAN' : resp.status === 'rejected' ? '✗ RAD ETILGAN' : '⏳ KUTILMOQDA'}
          </span>
        </div>
        <div class="code"><p style="font-size:10px;color:#64748b">Ruxsatnoma kodi</p><p class="val">${resp.permit_code}</p></div>
        <div class="box">
          <div class="row"><span class="l">Talaba:</span><span class="v">${resp.student?.name}</span></div>
          <div class="row"><span class="l">ID:</span><span class="v">${resp.student?.student_id}</span></div>
          <div class="row"><span class="l">Guruh:</span><span class="v">${resp.student?.group_name}</span></div>
        </div>
        <div class="box">
          <div class="row"><span class="l">Fan:</span><span class="v">${resp.subject_name}</span></div>
          <div class="row"><span class="l">O'qituvchi:</span><span class="v">${resp.teacher_name || '-'}</span></div>
          <div class="row"><span class="l">Chiqargan:</span><span class="v">${resp.issued_by_name || '-'}</span></div>
          <div class="row"><span class="l">Sana:</span><span class="v">${resp.issue_date}</span></div>
        </div>
        ${resp.result_grade ? '<div style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:6px;padding:10px;text-align:center;margin-bottom:10px"><p style="font-size:10px;color:#059669">Baho</p><p style="font-size:18px;font-weight:bold;color:#059669">' + resp.result_grade + '</p></div>' : ''}
        <div class="footer">
          <p class="hash">${resp.verification_hash}</p>
          <p style="font-size:11px;font-weight:600;margin-top:6px;color:${resp.is_valid ? '#059669' : '#ef4444'}">${resp.is_valid ? '🛡️ Haqiqiy hujjat' : '⚠️ Tasdiqlanmagan'}</p>
        </div>
      </div>
      <script>window.onload = function() { window.print(); }<\/script>
    </body>
  </html>
`

const printFromPreview = () => {
  if (!checkData.value) return
  const win = window.open('', '_blank', 'width=400,height=700')
  win.document.write(buildCheckHtml(checkData.value))
  win.document.close()
}

const printCheck = async (permit) => {
  try {
    const resp = await api.get(`/registrar/permits/${permit.id}/check`)
    const win = window.open('', '_blank', 'width=400,height=700')
    win.document.write(buildCheckHtml(resp))
    win.document.close()
  } catch (e) {
    console.error('Print error:', e)
  }
}

onMounted(loadPermits)
</script>
