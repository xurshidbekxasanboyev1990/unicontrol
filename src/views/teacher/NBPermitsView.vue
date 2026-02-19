<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">NB Ruxsatnomalar</h1>
        <p class="text-sm text-slate-500 mt-1">Sizga yuborilgan NB/Atrabotka ruxsatnomalari</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200/60 p-4">
      <div class="flex gap-3">
        <select
          v-model="statusFilter"
          @change="loadPermits"
          class="px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
        >
          <option :value="null">Barcha status</option>
          <option value="issued">Yangi</option>
          <option value="pending">Kutilmoqda</option>
          <option value="in_progress">Jarayonda</option>
          <option value="approved">Tasdiqlangan</option>
          <option value="rejected">Rad etilgan</option>
        </select>
      </div>
    </div>

    <!-- Permits Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="p in permits"
        :key="p.id"
        class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <span class="font-mono text-xs text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">{{ p.permit_code }}</span>
            <span :class="['ml-2 px-2 py-0.5 text-xs font-medium rounded-full', statusColor(p.status)]">
              {{ statusLabel(p.status) }}
            </span>
          </div>
          <span class="text-xs text-slate-400">{{ p.issue_date }}</span>
        </div>

        <h3 class="text-lg font-semibold text-slate-800 mb-1">{{ p.subject_name }}</h3>
        <p class="text-sm text-slate-600 mb-3">
          {{ p.student_name }} 
          <span class="text-slate-400">• {{ p.student_sid }}</span>
          <span class="text-slate-400">• {{ p.group_name }}</span>
        </p>
        <p class="text-xs text-slate-500 mb-4">
          {{ p.nb_type === 'nb' ? 'NB (Akademik qarz)' : 'Atrabotka' }} • {{ p.semester }}-semestr
        </p>

        <!-- Action Buttons -->
        <div v-if="p.status === 'issued' || p.status === 'pending' || p.status === 'in_progress'" class="flex gap-2">
          <button
            @click="approvePermit(p)"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium hover:bg-emerald-600 transition-colors"
          >
            <CheckCircle class="w-4 h-4" />
            Tasdiqlash
          </button>
          <button
            @click="rejectPermit(p)"
            class="px-4 py-2 bg-rose-50 text-rose-600 rounded-xl text-sm font-medium hover:bg-rose-100 transition-colors"
          >
            Rad etish
          </button>
        </div>

        <!-- Already processed -->
        <div v-else-if="p.status === 'approved'" class="bg-emerald-50 rounded-xl p-3 text-center">
          <p class="text-sm font-semibold text-emerald-700">✓ Tasdiqlangan</p>
          <p v-if="p.result_grade" class="text-xs text-emerald-600 mt-1">Baho: {{ p.result_grade }}</p>
          <p v-if="p.teacher_notes" class="text-xs text-emerald-600">{{ p.teacher_notes }}</p>
        </div>
        <div v-else-if="p.status === 'rejected'" class="bg-rose-50 rounded-xl p-3 text-center">
          <p class="text-sm font-semibold text-rose-700">✗ Rad etilgan</p>
          <p v-if="p.teacher_notes" class="text-xs text-rose-600 mt-1">{{ p.teacher_notes }}</p>
        </div>

        <!-- View / Print -->
        <div class="mt-3 flex gap-2">
          <button
            @click="viewPermitCheck(p)"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-slate-50 text-slate-600 rounded-xl text-sm hover:bg-slate-100 transition-colors"
          >
            <Eye class="w-4 h-4" />
            Chekni ko'rish
          </button>
          <button
            @click="printPermit(p)"
            class="flex items-center justify-center gap-2 px-4 py-2 bg-slate-50 text-slate-600 rounded-xl text-sm hover:bg-slate-100 transition-colors"
          >
            <Printer class="w-4 h-4" />
            Print
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!loading && permits.length === 0" class="text-center py-16">
      <FileCheck class="w-12 h-12 text-slate-300 mx-auto mb-3" />
      <p class="text-slate-500">Sizga yuborilgan ruxsatnomalar yo'q</p>
    </div>

    <!-- ============ APPROVE MODAL ============ -->
    <Teleport to="body">
      <div v-if="showApproveModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showApproveModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
          <div class="px-6 py-4 border-b border-slate-200">
            <h3 class="text-lg font-bold text-slate-800">NB ni tasdiqlash</h3>
            <p class="text-sm text-slate-500 mt-1">{{ selectedPermit?.subject_name }} - {{ selectedPermit?.student_name }}</p>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Baho / Natija</label>
              <input
                v-model="approvalForm.result_grade"
                type="text"
                placeholder="Masalan: 60, yoki O'tdi"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Izoh</label>
              <textarea
                v-model="approvalForm.teacher_notes"
                rows="2"
                placeholder="Izoh qoldirish (ixtiyoriy)"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"
              ></textarea>
            </div>
            <div class="flex gap-3 pt-2">
              <button
                @click="showApproveModal = false"
                class="flex-1 px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200"
              >
                Bekor
              </button>
              <button
                @click="submitApproval('approved')"
                :disabled="submitting"
                class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium hover:bg-emerald-600 disabled:opacity-50"
              >
                {{ submitting ? 'Yuklanmoqda...' : 'Tasdiqlash' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ============ REJECT MODAL ============ -->
    <Teleport to="body">
      <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showRejectModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
          <div class="px-6 py-4 border-b border-slate-200">
            <h3 class="text-lg font-bold text-slate-800">NB ni rad etish</h3>
            <p class="text-sm text-slate-500 mt-1">{{ selectedPermit?.subject_name }} - {{ selectedPermit?.student_name }}</p>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Sabab</label>
              <textarea
                v-model="approvalForm.teacher_notes"
                rows="3"
                placeholder="Rad etish sababini kiriting..."
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/20 resize-none"
              ></textarea>
            </div>
            <div class="flex gap-3 pt-2">
              <button
                @click="showRejectModal = false"
                class="flex-1 px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200"
              >
                Bekor
              </button>
              <button
                @click="submitApproval('rejected')"
                :disabled="submitting"
                class="flex-1 px-4 py-2.5 bg-rose-500 text-white rounded-xl text-sm font-medium hover:bg-rose-600 disabled:opacity-50"
              >
                {{ submitting ? 'Yuklanmoqda...' : 'Rad etish' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Loading -->
    <div v-if="loading" class="fixed inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- ============ CHECK PREVIEW MODAL ============ -->
    <Teleport to="body">
      <div v-if="showCheckModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showCheckModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          <!-- Modal Header -->
          <div class="sticky top-0 bg-white px-6 py-4 border-b border-slate-200 rounded-t-2xl flex items-center justify-between">
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
          <!-- Check Content -->
          <div class="p-6">
            <div v-if="checkData" class="border-2 border-slate-800 rounded-xl p-5 space-y-4">
              <!-- Header -->
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
              <!-- Permit Code -->
              <div class="text-center">
                <p class="text-[10px] text-slate-500">Ruxsatnoma kodi</p>
                <p class="text-base font-mono font-bold text-emerald-600">{{ checkData.permit_code }}</p>
              </div>
              <!-- Student Info -->
              <div class="border border-slate-200 rounded-lg p-3 space-y-1.5">
                <div class="flex justify-between text-xs"><span class="text-slate-500">Talaba:</span><span class="text-slate-800 font-medium">{{ checkData.student?.name }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">ID:</span><span class="text-slate-800 font-medium">{{ checkData.student?.student_id }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Guruh:</span><span class="text-slate-800 font-medium">{{ checkData.student?.group_name }}</span></div>
                <div v-if="checkData.student?.faculty" class="flex justify-between text-xs"><span class="text-slate-500">Fakultet:</span><span class="text-slate-800 font-medium">{{ checkData.student?.faculty }}</span></div>
              </div>
              <!-- Subject Info -->
              <div class="border border-slate-200 rounded-lg p-3 space-y-1.5">
                <div class="flex justify-between text-xs"><span class="text-slate-500">Fan:</span><span class="text-slate-800 font-medium">{{ checkData.subject_name }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Turi:</span><span class="text-slate-800 font-medium">{{ checkData.nb_type === 'nb' ? 'NB' : 'Atrabotka' }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Semestr:</span><span class="text-slate-800 font-medium">{{ checkData.semester }}-semestr • {{ checkData.academic_year }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">O'qituvchi:</span><span class="text-slate-800 font-medium">{{ checkData.teacher_name || '—' }}</span></div>
                <div class="flex justify-between text-xs"><span class="text-slate-500">Berilgan:</span><span class="text-slate-800 font-medium">{{ checkData.issue_date }}</span></div>
                <div v-if="checkData.expiry_date" class="flex justify-between text-xs"><span class="text-slate-500">Muddat:</span><span class="text-slate-800 font-medium">{{ checkData.expiry_date }}</span></div>
              </div>
              <!-- Grade -->
              <div v-if="checkData.result_grade" class="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center">
                <p class="text-[10px] text-emerald-600">Baho / Natija</p>
                <p class="text-xl font-bold text-emerald-700">{{ checkData.result_grade }}</p>
              </div>
              <!-- Teacher notes -->
              <div v-if="checkData.teacher_notes" class="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <p class="text-[10px] text-slate-500 mb-1">O'qituvchi izohi:</p>
                <p class="text-xs text-slate-700">{{ checkData.teacher_notes }}</p>
              </div>
              <!-- Footer -->
              <div class="border-t border-dashed border-slate-300 pt-3 text-center space-y-1">
                <p class="text-xs text-slate-500">Chiqargan: {{ checkData.issued_by_name }}</p>
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
import { CheckCircle, Eye, FileCheck, Printer, X } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const submitting = ref(false)
const permits = ref([])
const statusFilter = ref(null)

const showApproveModal = ref(false)
const showRejectModal = ref(false)
const showCheckModal = ref(false)
const selectedPermit = ref(null)
const checkData = ref(null)
const approvalForm = ref({ result_grade: '', teacher_notes: '' })

const statusColor = (status) => {
  const map = {
    issued: 'bg-blue-100 text-blue-700',
    pending: 'bg-amber-100 text-amber-700',
    in_progress: 'bg-purple-100 text-purple-700',
    approved: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-rose-100 text-rose-700',
  }
  return map[status] || 'bg-slate-100 text-slate-600'
}

const statusLabel = (status) => {
  const map = {
    issued: 'Yangi',
    pending: 'Kutilmoqda',
    in_progress: 'Jarayonda',
    approved: 'Tasdiqlangan ✓',
    rejected: 'Rad etilgan',
  }
  return map[status] || status
}

const loadPermits = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status_filter = statusFilter.value
    const resp = await api.get('/registrar/teacher-permits', { params })
    permits.value = resp.items || []
  } catch (err) {
    console.error('Teacher permits error:', err)
  } finally {
    loading.value = false
  }
}

const approvePermit = (permit) => {
  selectedPermit.value = permit
  approvalForm.value = { result_grade: '', teacher_notes: '' }
  showApproveModal.value = true
}

const rejectPermit = (permit) => {
  selectedPermit.value = permit
  approvalForm.value = { result_grade: '', teacher_notes: '' }
  showRejectModal.value = true
}

const submitApproval = async (status) => {
  submitting.value = true
  try {
    await api.put(`/registrar/teacher-permits/${selectedPermit.value.id}`, {
      status,
      result_grade: approvalForm.value.result_grade || null,
      teacher_notes: approvalForm.value.teacher_notes || null,
    })
    showApproveModal.value = false
    showRejectModal.value = false
    loadPermits()
  } catch (err) {
    console.error('Approval error:', err)
  } finally {
    submitting.value = false
  }
}

const viewPermitCheck = async (permit) => {
  checkData.value = null
  showCheckModal.value = true
  try {
    const resp = await api.get(`/registrar/permits/${permit.id}/check`)
    checkData.value = resp
  } catch (err) {
    console.error('Check view error:', err)
    showCheckModal.value = false
  }
}

const printFromPreview = () => {
  if (!checkData.value) return
  const resp = checkData.value
  const win = window.open('', '_blank', 'width=400,height=700')
  win.document.write(buildCheckHtml(resp))
  win.document.close()
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
        .header h2 { font-size: 18px; }
        .header p { font-size: 10px; color: #64748b; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 13px; margin-top: 8px; }
        .approved { background: #10b981; color: #fff; }
        .pending { background: #fef3c7; color: #92400e; }
        .rejected { background: #ef4444; color: #fff; }
        .code { text-align: center; margin: 12px 0; }
        .code .val { font-size: 16px; font-family: monospace; font-weight: bold; color: #059669; }
        .box { border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; margin-bottom: 10px; }
        .row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
        .row .l { color: #64748b; }
        .row .v { color: #1e293b; font-weight: 500; }
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
          <div class="row"><span class="l">Sana:</span><span class="v">${resp.issue_date}</span></div>
        </div>
        ${resp.result_grade ? `<div style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:6px;padding:10px;text-align:center;margin-bottom:10px"><p style="font-size:10px;color:#059669">Baho</p><p style="font-size:18px;font-weight:bold;color:#059669">${resp.result_grade}</p></div>` : ''}
        <div class="footer">
          <p class="hash">${resp.verification_hash}</p>
          <p style="font-size:11px;font-weight:600;margin-top:6px;color:${resp.is_valid ? '#059669' : '#ef4444'}">${resp.is_valid ? '🛡️ Haqiqiy hujjat' : '⚠️ Tasdiqlanmagan'}</p>
        </div>
      </div>
      <script>window.onload = function() { window.print(); }<\/script>
    </body>
  </html>
`

const printPermit = async (permit) => {
  try {
    const resp = await api.get(`/registrar/permits/${permit.id}/check`)
    const win = window.open('', '_blank', 'width=400,height=700')
    win.document.write(buildCheckHtml(resp))
    win.document.close()
  } catch (err) {
    console.error('Print error:', err)
  }
}

onMounted(() => {
  loadPermits()
})
</script>
