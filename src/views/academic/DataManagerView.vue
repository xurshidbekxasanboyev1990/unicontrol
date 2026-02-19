<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <Database :size="28" />
        <h1 class="text-2xl font-bold">Ma'lumotlar boshqaruvi</h1>
      </div>
      <p class="text-blue-100 text-sm">Barcha import, eksport va ma'lumotlarni boshqarish — jadval, kontingent, bandlik</p>
      <div class="flex flex-wrap gap-3 mt-4">
        <div class="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-2 text-sm flex items-center gap-2">
          <CalendarDays :size="16" />
          <span>{{ dashboardStats.total_schedules || 0 }} ta jadval</span>
        </div>
        <div class="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-2 text-sm flex items-center gap-2">
          <Users :size="16" />
          <span>{{ dashboardStats.total_students || 0 }} ta talaba</span>
        </div>
        <div class="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-2 text-sm flex items-center gap-2">
          <GraduationCap :size="16" />
          <span>{{ dashboardStats.total_teachers || 0 }} ta o'qituvchi</span>
        </div>
        <div class="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-2 text-sm flex items-center gap-2">
          <Building2 :size="16" />
          <span>{{ dashboardStats.total_groups || 0 }} ta guruh</span>
        </div>
      </div>
    </div>

    <!-- Section Cards -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- 1. Jadval boshqaruvi -->
      <div class="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
        <div class="bg-gradient-to-r from-emerald-500 to-teal-500 p-5 text-white">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <Table2 :size="24" />
            </div>
            <div>
              <h3 class="text-lg font-bold">Jadval boshqaruvi</h3>
              <p class="text-emerald-100 text-xs">Dars jadvallarini qo'shish, tahrirlash, o'chirish</p>
            </div>
          </div>
        </div>
        <div class="p-5 space-y-4">
          <p class="text-sm text-gray-600">Google Sheets uslubidagi jadval redaktori. Guruhlarni tanlang, darslarni qo'shing, tahrirlang yoki o'chiring.</p>
          <div class="grid grid-cols-3 gap-3">
            <div class="text-center p-3 bg-emerald-50 rounded-xl">
              <p class="text-xl font-bold text-emerald-600">{{ dashboardStats.total_schedules || 0 }}</p>
              <p class="text-[10px] text-gray-500">Jadvallar</p>
            </div>
            <div class="text-center p-3 bg-emerald-50 rounded-xl">
              <p class="text-xl font-bold text-emerald-600">{{ dashboardStats.total_subjects || 0 }}</p>
              <p class="text-[10px] text-gray-500">Fanlar</p>
            </div>
            <div class="text-center p-3 bg-emerald-50 rounded-xl">
              <p class="text-xl font-bold text-emerald-600">{{ dashboardStats.groups_without_schedule || 0 }}</p>
              <p class="text-[10px] text-gray-500">Jadvalsiz</p>
            </div>
          </div>
          <div class="flex gap-2">
            <router-link to="/academic/schedule-editor" class="flex-1 flex items-center justify-center gap-2 rounded-xl bg-emerald-600 text-white px-4 py-3 text-sm font-medium hover:bg-emerald-700 transition-colors">
              <Edit :size="16" />
              Jadval redaktori
            </router-link>
            <router-link to="/academic/ai-generate" class="flex items-center justify-center gap-2 rounded-xl bg-purple-600 text-white px-4 py-3 text-sm font-medium hover:bg-purple-700 transition-colors">
              <Sparkles :size="16" />
              AI
            </router-link>
          </div>
        </div>
      </div>

      <!-- 2. Kontingent import -->
      <div class="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
        <div class="bg-gradient-to-r from-blue-500 to-cyan-500 p-5 text-white">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <Users :size="24" />
            </div>
            <div>
              <h3 class="text-lg font-bold">Kontingent import</h3>
              <p class="text-blue-100 text-xs">Talabalar va guruhlarni Excel/CSV dan yuklash</p>
            </div>
          </div>
        </div>
        <div class="p-5 space-y-4">
          <p class="text-sm text-gray-600">Excel yoki CSV fayldan talabalar ro'yxatini yuklang. Guruhlar avtomatik yaratiladi.</p>
          <div class="grid grid-cols-2 gap-3">
            <div class="text-center p-3 bg-blue-50 rounded-xl">
              <p class="text-xl font-bold text-blue-600">{{ dashboardStats.total_students || 0 }}</p>
              <p class="text-[10px] text-gray-500">Talabalar</p>
            </div>
            <div class="text-center p-3 bg-blue-50 rounded-xl">
              <p class="text-xl font-bold text-blue-600">{{ dashboardStats.total_groups || 0 }}</p>
              <p class="text-[10px] text-gray-500">Guruhlar</p>
            </div>
          </div>
          <button @click="activeSection = 'kontingent'" class="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 text-white px-4 py-3 text-sm font-medium hover:bg-blue-700 transition-colors">
            <FileUp :size="16" />
            Kontingent import qilish
          </button>
        </div>
      </div>

      <!-- 3. Jadval import (Excel) -->
      <div class="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
        <div class="bg-gradient-to-r from-orange-500 to-amber-500 p-5 text-white">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <CalendarDays :size="24" />
            </div>
            <div>
              <h3 class="text-lg font-bold">Jadval import (Excel)</h3>
              <p class="text-orange-100 text-xs">Dars jadvalini Excel fayldan yuklash (AI yordamida)</p>
            </div>
          </div>
        </div>
        <div class="p-5 space-y-4">
          <p class="text-sm text-gray-600">Excel fayldan to'liq dars jadvalini avtomatik import qiling. AI yordamida fan nomlari va o'qituvchilar aniqlanadi.</p>
          <div class="bg-orange-50 rounded-xl p-3 space-y-1.5">
            <p class="text-xs font-medium text-orange-700">📋 Excel format:</p>
            <p class="text-[11px] text-orange-600">• Har bir sheet = bitta yo'nalish</p>
            <p class="text-[11px] text-orange-600">• 2-qator = guruh nomlari</p>
            <p class="text-[11px] text-orange-600">• A = kun, B = para, C = vaqt, D+ = guruhlar</p>
          </div>
          <button @click="activeSection = 'schedule'" class="w-full flex items-center justify-center gap-2 rounded-xl bg-orange-600 text-white px-4 py-3 text-sm font-medium hover:bg-orange-700 transition-colors">
            <CalendarDays :size="16" />
            Jadval import qilish
          </button>
        </div>
      </div>

      <!-- 4. Bandlik import -->
      <div class="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
        <div class="bg-gradient-to-r from-violet-500 to-purple-500 p-5 text-white">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <CalendarClock :size="24" />
            </div>
            <div>
              <h3 class="text-lg font-bold">O'qituvchi bandligi import</h3>
              <p class="text-violet-100 text-xs">Bandlik jadvalini Excel fayldan yuklash</p>
            </div>
          </div>
        </div>
        <div class="p-5 space-y-4">
          <p class="text-sm text-gray-600">O'qituvchilar haftalik bandlik jadvalini Excel fayldan import qiling. Kafedralar va dars vaqtlari avtomatik aniqlanadi.</p>
          <div class="grid grid-cols-3 gap-3">
            <div class="text-center p-3 bg-violet-50 rounded-xl">
              <p class="text-xl font-bold text-violet-600">{{ workloadStats.total_entries || 0 }}</p>
              <p class="text-[10px] text-gray-500">Yozuvlar</p>
            </div>
            <div class="text-center p-3 bg-violet-50 rounded-xl">
              <p class="text-xl font-bold text-violet-600">{{ workloadStats.total_teachers || 0 }}</p>
              <p class="text-[10px] text-gray-500">O'qituvchilar</p>
            </div>
            <div class="text-center p-3 bg-violet-50 rounded-xl">
              <p class="text-xl font-bold text-violet-600">{{ workloadStats.total_departments || 0 }}</p>
              <p class="text-[10px] text-gray-500">Kafedralar</p>
            </div>
          </div>
          <button @click="activeSection = 'workload'" class="w-full flex items-center justify-center gap-2 rounded-xl bg-violet-600 text-white px-4 py-3 text-sm font-medium hover:bg-violet-700 transition-colors">
            <CalendarClock :size="16" />
            Bandlik import qilish
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Actions Bar -->
    <div class="rounded-2xl bg-white border border-gray-100 shadow-sm p-5">
      <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Zap :size="16" class="text-amber-500" />
        Tezkor harakatlar
      </h3>
      <div class="flex flex-wrap gap-2">
        <router-link to="/academic/schedule-editor" class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-50 text-emerald-700 text-sm font-medium hover:bg-emerald-100 transition-colors">
          <Edit :size="14" /> Jadval redaktori
        </router-link>
        <router-link to="/academic/groups" class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-50 text-blue-700 text-sm font-medium hover:bg-blue-100 transition-colors">
          <Building2 :size="14" /> Guruhlar
        </router-link>
        <router-link to="/academic/workload" class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-violet-50 text-violet-700 text-sm font-medium hover:bg-violet-100 transition-colors">
          <CalendarClock :size="14" /> Bandlik jadvali
        </router-link>
        <router-link to="/academic/ai-generate" class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-50 text-purple-700 text-sm font-medium hover:bg-purple-100 transition-colors">
          <Sparkles :size="14" /> AI generatsiya
        </router-link>
      </div>
    </div>

    <!-- Active Section Modal/Overlay -->
    <Transition name="slide-up">
      <div v-if="activeSection" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-sm p-0 sm:p-6" @click.self="activeSection = null">
        <div class="bg-white w-full sm:max-w-4xl sm:rounded-2xl rounded-t-2xl shadow-2xl max-h-[90vh] overflow-y-auto">
          <!-- Section header -->
          <div class="sticky top-0 z-10 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
            <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              <component :is="sectionIcon" :size="20" :class="sectionColor" />
              {{ sectionTitle }}
            </h2>
            <button @click="activeSection = null" class="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <X :size="18" />
            </button>
          </div>

          <!-- Section content -->
          <div class="p-6">
            <!-- Kontingent -->
            <div v-if="activeSection === 'kontingent'">
              <ExcelImport @completed="onKontingentComplete" />
            </div>

            <!-- Schedule import -->
            <div v-if="activeSection === 'schedule'">
              <ScheduleImport />
            </div>

            <!-- Workload import -->
            <div v-if="activeSection === 'workload'">
              <WorkloadUploader @completed="onWorkloadComplete" />
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-[60] rounded-xl px-5 py-3 text-white shadow-lg', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import ExcelImport from '@/components/excel/ExcelImport.vue'
import ScheduleImport from '@/components/excel/ScheduleImport.vue'
import {
    Building2,
    CalendarClock,
    CalendarDays,
    Database,
    Edit,
    FileUp,
    GraduationCap,
    Sparkles,
    Table2,
    Users,
    X,
    Zap
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'
import WorkloadUploader from './WorkloadUploader.vue'

const { t } = useLanguageStore()

const activeSection = ref(null)
const toast = ref(null)
const dashboardStats = ref({})
const workloadStats = ref({})

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 4000)
}

const sectionTitle = computed(() => {
  const map = {
    kontingent: 'Kontingent import (talabalar)',
    schedule: 'Jadval import (Excel → Dars jadvali)',
    workload: "O'qituvchi bandligi import",
  }
  return map[activeSection.value] || ''
})

const sectionIcon = computed(() => {
  const map = {
    kontingent: markRaw(Users),
    schedule: markRaw(CalendarDays),
    workload: markRaw(CalendarClock),
  }
  return map[activeSection.value] || markRaw(Database)
})

const sectionColor = computed(() => {
  const map = {
    kontingent: 'text-blue-600',
    schedule: 'text-orange-600',
    workload: 'text-violet-600',
  }
  return map[activeSection.value] || ''
})

const onKontingentComplete = (result) => {
  showToast(`Import muvaffaqiyatli: ${result.groups} guruh, ${result.students} talaba`)
  loadDashboard()
}

const onWorkloadComplete = () => {
  showToast("Bandlik ma'lumotlari muvaffaqiyatli yuklandi!")
  loadWorkloadStats()
}

const loadDashboard = async () => {
  try {
    const res = await api.request('/academic/dashboard')
    dashboardStats.value = res || {}
  } catch (e) {
    console.error('Dashboard error:', e)
  }
}

const loadWorkloadStats = async () => {
  try {
    const res = await api.request('/academic/workload/stats')
    workloadStats.value = res || {}
  } catch (e) {
    console.error('Workload stats error:', e)
  }
}

onMounted(() => {
  loadDashboard()
  loadWorkloadStats()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active { transition: all 0.3s ease-out; }
.slide-up-leave-active { transition: all 0.2s ease-in; }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }
.slide-up-leave-to { opacity: 0; transform: translateY(20px); }
</style>
