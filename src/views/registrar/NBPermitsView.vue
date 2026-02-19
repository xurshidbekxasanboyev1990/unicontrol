<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">NB Ruxsatnomalar</h1>
        <p class="text-sm text-slate-500 mt-1">Akademik qarz (NB/Atrabotka) ruxsatnomalarini boshqarish</p>
      </div>
      <button
        @click="openCreateModal"
        class="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-500/25 transition-all text-sm font-medium"
      >
        <Plus class="w-4 h-4" />
        Yangi ruxsatnoma
      </button>
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
            placeholder="Kod yoki fan nomi bo'yicha qidirish..."
            class="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-300"
          />
        </div>
        <select
          v-model="statusFilter"
          @change="loadPermits"
          class="px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
        >
          <option :value="null">Barcha status</option>
          <option value="issued">Berilgan</option>
          <option value="pending">Kutilmoqda</option>
          <option value="in_progress">Jarayonda</option>
          <option value="approved">Tasdiqlangan</option>
          <option value="rejected">Rad etilgan</option>
          <option value="expired">Muddati tugagan</option>
          <option value="cancelled">Bekor qilingan</option>
        </select>
      </div>
    </div>

    <!-- Permits List -->
    <div class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200">
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Kod</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Talaba</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Fan</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">O'qituvchi</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Turi</th>
              <th class="text-center px-4 py-3 font-semibold text-slate-600">Status</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">Sana</th>
              <th class="text-center px-4 py-3 font-semibold text-slate-600">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in permits"
              :key="p.id"
              class="border-b border-slate-100 hover:bg-slate-50/50 transition-colors"
            >
              <td class="px-4 py-3">
                <span class="font-mono text-xs text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">{{ p.permit_code }}</span>
              </td>
              <td class="px-4 py-3">
                <p class="font-medium text-slate-800">{{ p.student_name }}</p>
                <p class="text-xs text-slate-400">{{ p.student_sid }} • {{ p.group_name }}</p>
              </td>
              <td class="px-4 py-3 text-slate-700">{{ p.subject_name }}</td>
              <td class="px-4 py-3 text-slate-600">{{ p.teacher_name || '-' }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-0.5 text-xs rounded-lg bg-slate-100 text-slate-600">
                  {{ p.nb_type === 'nb' ? 'NB' : 'Atrabotka' }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <span :class="['inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full', statusColor(p.status)]">
                  <span class="w-1.5 h-1.5 rounded-full" :class="statusDot(p.status)"></span>
                  {{ statusLabel(p.status) }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ p.issue_date }}</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button
                    @click="printPermit(p)"
                    class="p-1.5 text-slate-400 hover:text-emerald-500 hover:bg-emerald-50 rounded-lg transition-colors"
                    title="Chek chiqarish"
                  >
                    <Printer class="w-4 h-4" />
                  </button>
                  <button
                    @click="cancelPermit(p)"
                    v-if="p.status === 'issued' || p.status === 'pending'"
                    class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Bekor qilish"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty -->
      <div v-if="!loading && permits.length === 0" class="text-center py-16">
        <FileCheck class="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-500">Ruxsatnomalar topilmadi</p>
      </div>

      <!-- Pagination -->
      <div v-if="permits.length > 0" class="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <p class="text-xs text-slate-500">Jami: {{ total }}</p>
        <div class="flex items-center gap-2">
          <button @click="page > 1 && (page--, loadPermits())" :disabled="page <= 1" class="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50">Oldingi</button>
          <span class="text-xs text-slate-600">{{ page }} / {{ totalPages }}</span>
          <button @click="page < totalPages && (page++, loadPermits())" :disabled="page >= totalPages" class="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50">Keyingi</button>
        </div>
      </div>
    </div>

    <!-- ============ CREATE PERMIT MODAL ============ -->
    <Teleport to="body">
      <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showCreate = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
            <h3 class="text-lg font-bold text-slate-800">Yangi NB ruxsatnoma</h3>
            <button @click="showCreate = false" class="p-2 hover:bg-slate-100 rounded-xl">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <!-- Student Search -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Talaba *</label>
              <div class="relative">
                <input
                  v-model="createForm.studentSearch"
                  @input="searchStudents"
                  type="text"
                  placeholder="Ism yoki ID bo'yicha qidiring..."
                  class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                />
                <!-- Dropdown -->
                <div v-if="studentResults.length > 0 && !createForm.student_id" class="absolute top-full mt-1 left-0 right-0 bg-white border border-slate-200 rounded-xl shadow-lg z-10 max-h-40 overflow-y-auto">
                  <button
                    v-for="s in studentResults"
                    :key="s.id"
                    @click="selectStudent(s)"
                    class="w-full text-left px-4 py-2 text-sm hover:bg-emerald-50 transition-colors"
                  >
                    <span class="font-medium">{{ s.name }}</span>
                    <span class="text-slate-400 ml-2">{{ s.student_id }} • {{ s.group_name }}</span>
                  </button>
                </div>
              </div>
              <p v-if="createForm.student_id" class="mt-1 text-xs text-emerald-600">
                ✓ {{ createForm.selectedStudentName }} tanlandi
                <button @click="clearStudent" class="text-slate-400 hover:text-slate-600 ml-1">(o'zgartirish)</button>
              </p>
            </div>

            <!-- Subject -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Fan nomi *</label>
              <input
                v-model="createForm.subject_name"
                type="text"
                placeholder="Masalan: Oliy matematika"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              />
            </div>

            <!-- NB Type -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Turi</label>
              <select
                v-model="createForm.nb_type"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              >
                <option value="nb">NB (Akademik qarz)</option>
                <option value="atrabotka">Atrabotka (Qayta topshirish)</option>
              </select>
            </div>

            <!-- Teacher -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">O'qituvchi</label>
              <select
                v-model="createForm.teacher_id"
                @change="onTeacherSelect"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              >
                <option :value="null">Tanlanmagan</option>
                <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <!-- Semester -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Semestr</label>
                <select
                  v-model="createForm.semester"
                  class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                >
                  <option :value="1">1-semestr</option>
                  <option :value="2">2-semestr</option>
                </select>
              </div>
              <!-- Expiry Date -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Amal qilish muddati</label>
                <input
                  v-model="createForm.expiry_date"
                  type="date"
                  class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                />
              </div>
            </div>

            <!-- Reason -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Sabab / Izoh</label>
              <textarea
                v-model="createForm.reason"
                rows="2"
                placeholder="NB sababi..."
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"
              ></textarea>
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Registrator izohi</label>
              <textarea
                v-model="createForm.registrar_notes"
                rows="2"
                placeholder="Qo'shimcha izoh..."
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"
              ></textarea>
            </div>

            <!-- Error -->
            <p v-if="createError" class="text-sm text-rose-600">{{ createError }}</p>

            <!-- Submit -->
            <div class="flex items-center gap-3 pt-2">
              <button
                @click="showCreate = false"
                class="flex-1 px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="submitCreate"
                :disabled="creating"
                class="flex-1 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-emerald-500/25 transition-all disabled:opacity-50"
              >
                {{ creating ? 'Yaratilmoqda...' : 'Yaratish va Chek chiqarish' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ============ PRINT CHECK MODAL ============ -->
    <Teleport to="body">
      <div v-if="showPrint" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showPrint = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md">
          <div class="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
            <h3 class="text-lg font-bold text-slate-800">NB Ruxsatnoma cheki</h3>
            <div class="flex items-center gap-2">
              <button @click="doPrint" class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-medium hover:bg-emerald-600 transition-colors">
                <Printer class="w-3.5 h-3.5" />
                Chop etish
              </button>
              <button @click="showPrint = false" class="p-2 hover:bg-slate-100 rounded-xl">
                <X class="w-5 h-5 text-slate-500" />
              </button>
            </div>
          </div>

          <!-- Print Content -->
          <div ref="printArea" class="p-6">
            <div v-if="printData" class="border-2 border-slate-800 rounded-lg p-5 space-y-4 bg-white" id="nb-check">
              <!-- Header -->
              <div class="text-center border-b border-dashed border-slate-400 pb-3">
                <h2 class="text-lg font-bold text-slate-800">UNICONTROL</h2>
                <p class="text-xs text-slate-500">NB / ATRABOTKA RUXSATNOMASI</p>
                <div class="mt-2 flex items-center justify-center gap-2">
                  <span :class="[
                    'px-3 py-1 text-sm font-bold rounded-lg',
                    printData.status === 'approved' ? 'bg-emerald-500 text-white' : 
                    printData.status === 'rejected' ? 'bg-rose-500 text-white' : 
                    'bg-amber-100 text-amber-800'
                  ]">
                    {{ printData.status === 'approved' ? '✓ NB OQLANGAN' : 
                       printData.status === 'rejected' ? '✗ RAD ETILGAN' : 
                       '⏳ KUTILMOQDA' }}
                  </span>
                </div>
              </div>

              <!-- Permit Code -->
              <div class="text-center">
                <p class="text-xs text-slate-500">Ruxsatnoma kodi</p>
                <p class="text-lg font-mono font-bold text-emerald-700 tracking-wider">{{ printData.permit_code }}</p>
              </div>

              <!-- Student Info -->
              <div class="border border-slate-200 rounded-lg p-3 space-y-2">
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Talaba:</span>
                  <span class="font-semibold text-slate-800">{{ printData.student?.name }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Talaba ID:</span>
                  <span class="font-mono text-slate-700">{{ printData.student?.student_id }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Guruh:</span>
                  <span class="text-slate-700">{{ printData.student?.group_name }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Fakultet:</span>
                  <span class="text-slate-700">{{ printData.student?.faculty }}</span>
                </div>
              </div>

              <!-- Subject Details -->
              <div class="border border-slate-200 rounded-lg p-3 space-y-2">
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Fan:</span>
                  <span class="font-semibold text-slate-800">{{ printData.subject_name }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Turi:</span>
                  <span class="text-slate-700">{{ printData.nb_type === 'nb' ? 'NB (Akademik qarz)' : 'Atrabotka' }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Semestr:</span>
                  <span class="text-slate-700">{{ printData.semester }}-semestr ({{ printData.academic_year }})</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">O'qituvchi:</span>
                  <span class="text-slate-700">{{ printData.teacher_name || '-' }}</span>
                </div>
                <div v-if="printData.reason" class="flex justify-between text-xs">
                  <span class="text-slate-500">Sabab:</span>
                  <span class="text-slate-700">{{ printData.reason }}</span>
                </div>
              </div>

              <!-- Dates -->
              <div class="border border-slate-200 rounded-lg p-3 space-y-2">
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Berilgan sana:</span>
                  <span class="text-slate-700">{{ printData.issue_date }}</span>
                </div>
                <div v-if="printData.expiry_date" class="flex justify-between text-xs">
                  <span class="text-slate-500">Amal qilish:</span>
                  <span class="text-slate-700">{{ printData.expiry_date }}</span>
                </div>
                <div v-if="printData.completed_date" class="flex justify-between text-xs">
                  <span class="text-slate-500">Yakunlangan:</span>
                  <span class="font-semibold text-emerald-700">{{ printData.completed_date }}</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span class="text-slate-500">Bergan xodim:</span>
                  <span class="text-slate-700">{{ printData.issued_by_name }}</span>
                </div>
              </div>

              <!-- Result (if approved) -->
              <div v-if="printData.result_grade" class="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center">
                <p class="text-xs text-emerald-600">Natija / Baho</p>
                <p class="text-lg font-bold text-emerald-700">{{ printData.result_grade }}</p>
                <p v-if="printData.teacher_notes" class="text-xs text-emerald-600 mt-1">{{ printData.teacher_notes }}</p>
              </div>

              <!-- Verification -->
              <div class="border-t border-dashed border-slate-400 pt-3 text-center">
                <p class="text-[10px] text-slate-400">Tekshirish kodi (anti-forgery)</p>
                <p class="text-[10px] font-mono text-slate-500">{{ printData.verification_hash }}</p>
                <div class="mt-2 flex items-center justify-center gap-1">
                  <ShieldCheck v-if="printData.is_valid" class="w-4 h-4 text-emerald-500" />
                  <ShieldAlert v-else class="w-4 h-4 text-rose-500" />
                  <span :class="['text-xs font-medium', printData.is_valid ? 'text-emerald-600' : 'text-rose-600']">
                    {{ printData.is_valid ? 'Haqiqiy hujjat' : 'Tasdiqlanmagan!' }}
                  </span>
                </div>
                <p class="text-[9px] text-slate-400 mt-2">Chop etilgan: {{ printData.print_count }} marta</p>
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
import { FileCheck, Plus, Printer, Search, ShieldAlert, ShieldCheck, Trash2, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

const route = useRoute()

const loading = ref(false)
const permits = ref([])
const teachers = ref([])
const search = ref('')
const statusFilter = ref(null)
const page = ref(1)
const total = ref(0)
const limit = 50

const showCreate = ref(false)
const showPrint = ref(false)
const creating = ref(false)
const createError = ref('')
const printData = ref(null)
const printArea = ref(null)

const studentResults = ref([])
let studentSearchTimeout = null
let searchTimeout = null

const createForm = ref({
  student_id: null,
  selectedStudentName: '',
  studentSearch: '',
  subject_name: '',
  nb_type: 'nb',
  teacher_id: null,
  teacher_name: '',
  semester: 1,
  expiry_date: '',
  reason: '',
  registrar_notes: '',
})

const totalPages = computed(() => Math.ceil(total.value / limit) || 1)

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

const statusDot = (status) => {
  const map = {
    issued: 'bg-blue-500',
    pending: 'bg-amber-500',
    in_progress: 'bg-purple-500',
    approved: 'bg-emerald-500',
    rejected: 'bg-rose-500',
    expired: 'bg-slate-400',
    cancelled: 'bg-slate-400',
  }
  return map[status] || 'bg-slate-400'
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
    loadPermits()
  }, 400)
}

const openCreateModal = () => {
  createForm.value = {
    student_id: null,
    selectedStudentName: '',
    studentSearch: '',
    subject_name: '',
    nb_type: 'nb',
    teacher_id: null,
    teacher_name: '',
    semester: 1,
    expiry_date: '',
    reason: '',
    registrar_notes: '',
  }
  createError.value = ''

  // Check if coming from student page
  if (route.query.student_id) {
    createForm.value.student_id = parseInt(route.query.student_id)
    createForm.value.selectedStudentName = route.query.student_name || ''
    createForm.value.studentSearch = route.query.student_name || ''
  }

  showCreate.value = true
}

const searchStudents = () => {
  clearTimeout(studentSearchTimeout)
  if (createForm.value.student_id) return
  studentSearchTimeout = setTimeout(async () => {
    if (createForm.value.studentSearch.length < 2) {
      studentResults.value = []
      return
    }
    try {
      const resp = await api.get('/registrar/students', {
        params: { search: createForm.value.studentSearch, limit: 10 }
      })
      studentResults.value = resp.items || []
    } catch (err) {
      console.error('Student search error:', err)
    }
  }, 300)
}

const selectStudent = (student) => {
  createForm.value.student_id = student.id
  createForm.value.selectedStudentName = student.name
  createForm.value.studentSearch = student.name
  studentResults.value = []
}

const clearStudent = () => {
  createForm.value.student_id = null
  createForm.value.selectedStudentName = ''
  createForm.value.studentSearch = ''
  studentResults.value = []
}

const onTeacherSelect = () => {
  const teacher = teachers.value.find(t => t.id === createForm.value.teacher_id)
  createForm.value.teacher_name = teacher?.name || ''
}

const submitCreate = async () => {
  createError.value = ''

  if (!createForm.value.student_id) {
    createError.value = 'Talabani tanlang'
    return
  }
  if (!createForm.value.subject_name.trim()) {
    createError.value = 'Fan nomini kiriting'
    return
  }

  creating.value = true
  try {
    const payload = {
      student_id: createForm.value.student_id,
      subject_name: createForm.value.subject_name,
      nb_type: createForm.value.nb_type,
      teacher_id: createForm.value.teacher_id,
      teacher_name: createForm.value.teacher_name,
      semester: createForm.value.semester,
      reason: createForm.value.reason || null,
      registrar_notes: createForm.value.registrar_notes || null,
      expiry_date: createForm.value.expiry_date || null,
    }

    const resp = await api.post('/registrar/permits', payload)
    showCreate.value = false

    // Load the check for printing
    if (resp.id) {
      await printPermitById(resp.id)
    }

    loadPermits()
  } catch (err) {
    createError.value = err?.data?.detail || 'Xatolik yuz berdi'
  } finally {
    creating.value = false
  }
}

const loadPermits = async () => {
  loading.value = true
  try {
    const params = { page: page.value, limit }
    if (search.value) params.search = search.value
    if (statusFilter.value) params.status_filter = statusFilter.value

    const resp = await api.get('/registrar/permits', { params })
    permits.value = resp.items || []
    total.value = resp.total || 0
  } catch (err) {
    console.error('Permits error:', err)
  } finally {
    loading.value = false
  }
}

const loadTeachers = async () => {
  try {
    const resp = await api.get('/registrar/teachers')
    teachers.value = resp.items || []
  } catch (err) {
    console.error('Teachers error:', err)
  }
}

const printPermit = async (permit) => {
  await printPermitById(permit.id)
}

const printPermitById = async (id) => {
  try {
    const resp = await api.get(`/registrar/permits/${id}/check`)
    printData.value = resp
    showPrint.value = true
  } catch (err) {
    console.error('Print error:', err)
  }
}

const cancelPermit = async (permit) => {
  if (!confirm('Rostdan ham bu ruxsatnomani bekor qilmoqchimisiz?')) return
  try {
    await api.delete(`/registrar/permits/${permit.id}`)
    loadPermits()
  } catch (err) {
    console.error('Cancel error:', err)
  }
}

const doPrint = () => {
  const content = document.getElementById('nb-check')
  if (!content) return

  const win = window.open('', '_blank', 'width=400,height=700')
  win.document.write(`
    <html>
      <head>
        <title>NB Ruxsatnoma - ${printData.value?.permit_code}</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: 'Segoe UI', sans-serif; padding: 20px; background: #fff; }
          .check { border: 2px solid #1e293b; border-radius: 8px; padding: 20px; max-width: 350px; margin: 0 auto; }
          .header { text-align: center; border-bottom: 1px dashed #94a3b8; padding-bottom: 12px; margin-bottom: 12px; }
          .header h2 { font-size: 18px; color: #1e293b; }
          .header p { font-size: 10px; color: #64748b; margin-top: 2px; }
          .status-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 13px; margin-top: 8px; }
          .status-approved { background: #10b981; color: #fff; }
          .status-pending { background: #fef3c7; color: #92400e; }
          .status-rejected { background: #ef4444; color: #fff; }
          .code { text-align: center; margin: 12px 0; }
          .code p.label { font-size: 10px; color: #64748b; }
          .code p.value { font-size: 16px; font-family: monospace; font-weight: bold; color: #059669; letter-spacing: 2px; }
          .info-box { border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; margin-bottom: 10px; }
          .info-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
          .info-row .label { color: #64748b; }
          .info-row .value { color: #1e293b; font-weight: 500; }
          .result-box { background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px; padding: 10px; text-align: center; margin-bottom: 10px; }
          .result-box .grade { font-size: 18px; font-weight: bold; color: #059669; }
          .footer { border-top: 1px dashed #94a3b8; padding-top: 10px; text-align: center; }
          .footer .hash { font-size: 8px; font-family: monospace; color: #94a3b8; word-break: break-all; }
          .footer .valid { font-size: 11px; font-weight: 600; margin-top: 6px; }
          .footer .valid.ok { color: #059669; }
          .footer .valid.bad { color: #ef4444; }
          .footer .count { font-size: 8px; color: #94a3b8; margin-top: 4px; }
          @media print { body { padding: 0; } }
        </style>
      </head>
      <body>
        <div class="check">
          <div class="header">
            <h2>UNICONTROL</h2>
            <p>NB / ATRABOTKA RUXSATNOMASI</p>
            <span class="status-badge ${printData.value?.status === 'approved' ? 'status-approved' : printData.value?.status === 'rejected' ? 'status-rejected' : 'status-pending'}">
              ${printData.value?.status === 'approved' ? '✓ NB OQLANGAN' : printData.value?.status === 'rejected' ? '✗ RAD ETILGAN' : '⏳ KUTILMOQDA'}
            </span>
          </div>
          
          <div class="code">
            <p class="label">Ruxsatnoma kodi</p>
            <p class="value">${printData.value?.permit_code}</p>
          </div>

          <div class="info-box">
            <div class="info-row"><span class="label">Talaba:</span><span class="value">${printData.value?.student?.name}</span></div>
            <div class="info-row"><span class="label">Talaba ID:</span><span class="value">${printData.value?.student?.student_id}</span></div>
            <div class="info-row"><span class="label">Guruh:</span><span class="value">${printData.value?.student?.group_name}</span></div>
            <div class="info-row"><span class="label">Fakultet:</span><span class="value">${printData.value?.student?.faculty}</span></div>
          </div>

          <div class="info-box">
            <div class="info-row"><span class="label">Fan:</span><span class="value">${printData.value?.subject_name}</span></div>
            <div class="info-row"><span class="label">Turi:</span><span class="value">${printData.value?.nb_type === 'nb' ? 'NB (Akademik qarz)' : 'Atrabotka'}</span></div>
            <div class="info-row"><span class="label">Semestr:</span><span class="value">${printData.value?.semester}-semestr (${printData.value?.academic_year})</span></div>
            <div class="info-row"><span class="label">O'qituvchi:</span><span class="value">${printData.value?.teacher_name || '-'}</span></div>
            ${printData.value?.reason ? `<div class="info-row"><span class="label">Sabab:</span><span class="value">${printData.value.reason}</span></div>` : ''}
          </div>

          <div class="info-box">
            <div class="info-row"><span class="label">Berilgan sana:</span><span class="value">${printData.value?.issue_date}</span></div>
            ${printData.value?.expiry_date ? `<div class="info-row"><span class="label">Amal qilish:</span><span class="value">${printData.value.expiry_date}</span></div>` : ''}
            ${printData.value?.completed_date ? `<div class="info-row"><span class="label">Yakunlangan:</span><span class="value" style="color:#059669;font-weight:bold">${printData.value.completed_date}</span></div>` : ''}
            <div class="info-row"><span class="label">Bergan xodim:</span><span class="value">${printData.value?.issued_by_name}</span></div>
          </div>

          ${printData.value?.result_grade ? `
          <div class="result-box">
            <p style="font-size:10px;color:#059669">Natija / Baho</p>
            <p class="grade">${printData.value.result_grade}</p>
            ${printData.value?.teacher_notes ? `<p style="font-size:10px;color:#059669;margin-top:4px">${printData.value.teacher_notes}</p>` : ''}
          </div>
          ` : ''}

          <div class="footer">
            <p class="hash">${printData.value?.verification_hash}</p>
            <p class="valid ${printData.value?.is_valid ? 'ok' : 'bad'}">
              ${printData.value?.is_valid ? '🛡️ Haqiqiy hujjat' : '⚠️ Tasdiqlanmagan!'}
            </p>
            <p class="count">Chop etilgan: ${printData.value?.print_count} marta</p>
          </div>
        </div>
        <script>window.onload = function() { window.print(); }<\/script>
      </body>
    </html>
  `)
  win.document.close()
}

onMounted(() => {
  loadPermits()
  loadTeachers()

  // Auto-open create if query params exist
  if (route.query.student_id) {
    openCreateModal()
  }
})
</script>
