<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Davomat olish</h1>
        <p class="text-slate-500">Bugungi dars uchun davomat yozish</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="selectedDate" class="px-4 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all">
          <option v-for="date in recentDates" :key="date" :value="date">
            {{ formatDate(date) }}
          </option>
        </select>
        <select v-model="selectedSubject" class="px-4 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all">
          <option value="">Barcha fanlar</option>
          <option v-for="subject in subjects" :key="subject" :value="subject">
            {{ subject }}
          </option>
        </select>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-5 border border-emerald-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-emerald-600">{{ presentCount }}</p>
            <p class="text-sm text-emerald-700 font-medium">Kelgan</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
            <CheckCircle class="w-6 h-6 text-emerald-600" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-2xl p-5 border border-amber-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-amber-600">{{ lateCount }}</p>
            <p class="text-sm text-amber-700 font-medium">Kechikkan</p>
          </div>
          <div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
            <Clock class="w-6 h-6 text-amber-600" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-rose-50 to-rose-100/50 rounded-2xl p-5 border border-rose-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-rose-600">{{ absentCount }}</p>
            <p class="text-sm text-rose-700 font-medium">Kelmagan</p>
          </div>
          <div class="w-12 h-12 bg-rose-500/20 rounded-xl flex items-center justify-center">
            <XCircle class="w-6 h-6 text-rose-600" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-5 border border-blue-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-blue-600">{{ excusedCount }}</p>
            <p class="text-sm text-blue-700 font-medium">Sababli</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
            <FileText class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <span class="text-sm font-medium text-slate-600">Tez harakatlar:</span>
        <button @click="markAllAs('present')" class="px-4 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-xl text-sm font-medium transition-colors flex items-center gap-2">
          <CheckCircle class="w-4 h-4" />
          Barchasini keldi
        </button>
        <button @click="markAllAs('absent')" class="px-4 py-2 bg-rose-100 hover:bg-rose-200 text-rose-700 rounded-xl text-sm font-medium transition-colors flex items-center gap-2">
          <XCircle class="w-4 h-4" />
          Barchasini kelmadi
        </button>
        <button @click="resetAll" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-medium transition-colors flex items-center gap-2">
          <RotateCcw class="w-4 h-4" />
          Tozalash
        </button>
      </div>
    </div>

    <!-- Students List -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-lg font-semibold text-slate-800">Talabalar ro'yxati</h2>
          <p class="text-sm text-slate-500">Jami: {{ groupStudents.length }} ta talaba</p>
        </div>
        <button 
          @click="saveAttendance"
          :disabled="saving"
          class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save v-if="!saving" class="w-5 h-5" />
          <Loader2 v-else class="w-5 h-5 animate-spin" />
          <span>{{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}</span>
        </button>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="(student, index) in groupStudents" 
          :key="student.id"
          class="p-4 lg:p-5 hover:bg-slate-50/50 transition-colors"
        >
          <div class="flex flex-col lg:flex-row lg:items-center gap-4">
            <!-- Student Info -->
            <div class="flex items-center gap-4 flex-1">
              <span class="w-8 h-8 flex items-center justify-center text-sm font-bold text-slate-400 bg-slate-100 rounded-lg">{{ index + 1 }}</span>
              
              <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                <User class="w-5 h-5 text-slate-500" />
              </div>

              <div class="flex-1 min-w-0">
                <p class="font-semibold text-slate-800">{{ student.name }}</p>
                <p class="text-sm text-slate-500">{{ student.studentId }}</p>
              </div>
            </div>

            <!-- Status Buttons -->
            <div class="flex items-center gap-2 flex-wrap">
              <!-- Keldi -->
              <button
                @click="setStatus(student.id, 'present')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'present' 
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30 scale-105' 
                    : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 hover:scale-105'
                ]"
              >
                <CheckCircle class="w-4 h-4" />
                <span class="hidden sm:inline">Keldi</span>
              </button>
              <!-- Kelmadi -->
              <button
                @click="setStatus(student.id, 'absent')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'absent' 
                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30 scale-105' 
                    : 'bg-rose-100 text-rose-700 hover:bg-rose-200 hover:scale-105'
                ]"
              >
                <XCircle class="w-4 h-4" />
                <span class="hidden sm:inline">Kelmadi</span>
              </button>
              <!-- Kech qoldi -->
              <button
                @click="setStatus(student.id, 'late')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'late' 
                    ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/30 scale-105' 
                    : 'bg-amber-100 text-amber-700 hover:bg-amber-200 hover:scale-105'
                ]"
              >
                <Clock class="w-4 h-4" />
                <span class="hidden sm:inline">Kech qoldi</span>
              </button>
              <!-- Sababli -->
              <button
                @click="setStatus(student.id, 'excused')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'excused' 
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30 scale-105' 
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200 hover:scale-105'
                ]"
              >
                <FileText class="w-4 h-4" />
                <span class="hidden sm:inline">Sababli</span>
              </button>
            </div>
          </div>

          <!-- Kelmadi sababi input -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="attendance[student.id]?.status === 'absent' || attendance[student.id]?.status === 'excused'" class="mt-4 ml-12 lg:ml-20">
              <div class="flex items-center gap-3 p-4 bg-rose-50 rounded-xl border border-rose-200">
                <MessageSquare class="w-5 h-5 text-rose-500 flex-shrink-0" />
                <div class="flex-1">
                  <label class="block text-sm font-medium text-rose-700 mb-1.5">Kelmaganlik sababi</label>
                  <input
                    v-model="attendance[student.id].reason"
                    type="text"
                    placeholder="Masalan: Kasallik, oilaviy sabab..."
                    class="w-full px-4 py-2.5 rounded-lg border border-rose-200 bg-white focus:border-rose-400 focus:ring-2 focus:ring-rose-400/20 outline-none text-sm transition-all"
                  />
                </div>
              </div>
            </div>
          </Transition>

          <!-- Kechikish input -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="attendance[student.id]?.status === 'late'" class="mt-4 ml-12 lg:ml-20">
              <div class="flex items-center gap-3 p-4 bg-amber-50 rounded-xl border border-amber-200">
                <Timer class="w-5 h-5 text-amber-500 flex-shrink-0" />
                <div class="flex-1 flex flex-col sm:flex-row sm:items-center gap-3">
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-amber-700 mb-1.5">Necha daqiqa kechikdi?</label>
                    <div class="flex items-center gap-2">
                      <input
                        v-model.number="attendance[student.id].lateMinutes"
                        type="number"
                        min="1"
                        max="90"
                        placeholder="0"
                        class="w-24 px-4 py-2.5 rounded-lg border border-amber-200 bg-white focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm text-center transition-all"
                      />
                      <span class="text-sm text-amber-600 font-medium">daqiqa</span>
                    </div>
                  </div>
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-amber-700 mb-1.5">Sabab (ixtiyoriy)</label>
                    <input
                      v-model="attendance[student.id].reason"
                      type="text"
                      placeholder="Masalan: Transport muammosi..."
                      class="w-full px-4 py-2.5 rounded-lg border border-amber-200 bg-white focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm transition-all"
                    />
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Summary Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showSummary" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="showSummary = false">
        <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden">
          <div class="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 text-white text-center">
            <div class="w-16 h-16 bg-white/20 rounded-2xl mx-auto flex items-center justify-center mb-4">
              <CheckCircle class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold">Davomat saqlandi!</h3>
            <p class="text-emerald-100 mt-1">{{ formatDate(selectedDate) }}</p>
          </div>
          <div class="p-6 space-y-4">
            <div class="flex items-center justify-between p-3 bg-emerald-50 rounded-xl">
              <span class="text-emerald-700 font-medium">Kelgan</span>
              <span class="text-2xl font-bold text-emerald-600">{{ presentCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-amber-50 rounded-xl">
              <span class="text-amber-700 font-medium">Kechikkan</span>
              <span class="text-2xl font-bold text-amber-600">{{ lateCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-rose-50 rounded-xl">
              <span class="text-rose-700 font-medium">Kelmagan</span>
              <span class="text-2xl font-bold text-rose-600">{{ absentCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-blue-50 rounded-xl">
              <span class="text-blue-700 font-medium">Sababli</span>
              <span class="text-2xl font-bold text-blue-600">{{ excusedCount }}</span>
            </div>
          </div>
          <div class="px-6 pb-6">
            <button @click="showSummary = false" class="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">Yopish</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  User,
  Users,
  CheckCircle,
  Clock,
  XCircle,
  FileText,
  Save,
  Loader2,
  MessageSquare,
  Timer,
  RotateCcw
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

const saving = ref(false)
const showSummary = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedSubject = ref('')

const groupStudents = computed(() => {
  return dataStore.students.filter(s => s.groupId === 1)
})

const subjects = computed(() => {
  return [...new Set(dataStore.schedule.filter(s => s.groupId === 1).map(s => s.subject))]
})

const recentDates = computed(() => {
  const dates = []
  for (let i = 0; i < 14; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
  }
  return dates
})

const attendance = reactive({})

const initializeAttendance = () => {
  groupStudents.value.forEach(student => {
    const existing = dataStore.attendanceRecords.find(
      r => r.studentId === student.id && r.date === selectedDate.value
    )
    if (existing) {
      attendance[student.id] = {
        status: existing.status,
        reason: existing.note || '',
        lateMinutes: existing.lateMinutes || 0
      }
    } else {
      attendance[student.id] = {
        status: 'present',
        reason: '',
        lateMinutes: 0
      }
    }
  })
}

watch(selectedDate, () => initializeAttendance())
onMounted(() => initializeAttendance())

const setStatus = (studentId, status) => {
  attendance[studentId] = {
    ...attendance[studentId],
    status,
    reason: status === 'present' ? '' : attendance[studentId]?.reason || '',
    lateMinutes: status === 'late' ? (attendance[studentId]?.lateMinutes || 5) : 0
  }
}

const markAllAs = (status) => {
  groupStudents.value.forEach(student => setStatus(student.id, status))
  toast.info('Hammasi belgilandi', `Barcha talabalar "${status === 'present' ? 'Keldi' : 'Kelmadi'}" deb belgilandi`)
}

const resetAll = () => {
  initializeAttendance()
  toast.info('Tozalandi', 'Barcha belgilar boshlang\'ich holatga qaytarildi')
}

const presentCount = computed(() => Object.values(attendance).filter(a => a?.status === 'present').length)
const lateCount = computed(() => Object.values(attendance).filter(a => a?.status === 'late').length)
const absentCount = computed(() => Object.values(attendance).filter(a => a?.status === 'absent').length)
const excusedCount = computed(() => Object.values(attendance).filter(a => a?.status === 'excused').length)

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    weekday: 'long'
  })
}

const saveAttendance = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    groupStudents.value.forEach(student => {
      const record = attendance[student.id]
      dataStore.addAttendanceRecord({
        studentId: student.id,
        date: selectedDate.value,
        subject: selectedSubject.value || 'Umumiy',
        status: record.status,
        note: record.reason,
        lateMinutes: record.status === 'late' ? record.lateMinutes : 0
      })
    })
    toast.success('Muvaffaqiyatli saqlandi!', `${groupStudents.value.length} ta talaba uchun davomat yozildi`)
    showSummary.value = true
  } catch (error) {
    toast.error('Xatolik!', 'Davomatni saqlashda xatolik yuz berdi')
  } finally {
    saving.value = false
  }
}
</script>

