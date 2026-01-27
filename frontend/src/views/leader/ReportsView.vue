<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 md:text-3xl">Hisobotlar</h1>
        <p class="text-slate-500">{{ currentGroup?.name }} - Guruh statistikasi va tahlillari</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="selectedPeriod" class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none">
          <option value="week">Bu hafta</option>
          <option value="month">Bu oy</option>
          <option value="semester">Semestr</option>
          <option value="year">Yil</option>
        </select>
        <button 
          @click="showExportModal = true"
          class="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-white hover:bg-emerald-600"
        >
          <Download :size="18" />
          Export
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-green-600">{{ overallAttendance }}%</p>
            <p class="mt-1 text-sm text-slate-500">Umumiy davomat</p>
          </div>
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100">
            <TrendingUp :size="24" class="text-green-600" />
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-blue-600">{{ totalLessons }}</p>
            <p class="mt-1 text-sm text-slate-500">Jami darslar</p>
          </div>
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
            <BookOpen :size="24" class="text-blue-600" />
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-purple-600">{{ bestAttendee }}</p>
            <p class="mt-1 text-sm text-slate-500">Eng yaxshi</p>
          </div>
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100">
            <Award :size="24" class="text-purple-600" />
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-red-600">{{ lowAttendanceCount }}</p>
            <p class="mt-1 text-sm text-slate-500">Past davomat</p>
          </div>
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-red-100">
            <AlertTriangle :size="24" class="text-red-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Weekly Chart -->
      <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-6 text-lg font-semibold text-slate-800">Haftalik davomat</h2>
        <div class="flex h-48 items-end gap-4">
          <div 
            v-for="(day, index) in weeklyData" 
            :key="index"
            class="flex flex-1 flex-col items-center gap-2"
          >
            <div class="relative w-full rounded-lg bg-slate-100" style="height: 160px;">
              <div 
                class="absolute bottom-0 w-full rounded-lg bg-gradient-to-t from-emerald-500 to-emerald-400 transition-all duration-500"
                :style="{ height: day.rate + '%' }"
              ></div>
            </div>
            <span class="text-sm font-medium text-slate-700">{{ day.name }}</span>
            <span class="text-xs text-slate-500">{{ day.rate }}%</span>
          </div>
        </div>
      </div>

      <!-- Subject Analysis -->
      <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 text-lg font-semibold text-slate-800">Fanlar bo'yicha tahlil</h2>
        <div class="space-y-4">
          <div v-for="subject in subjectStats" :key="subject.name">
            <div class="mb-2 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div 
                  class="h-3 w-3 rounded-full"
                  :style="{ backgroundColor: subject.color }"
                ></div>
                <span class="font-medium text-slate-700">{{ subject.name }}</span>
              </div>
              <div class="flex items-center gap-4 text-sm">
                <span class="text-green-600">{{ subject.present }} kelgan</span>
                <span class="text-red-600">{{ subject.absent }} kelmagan</span>
                <span 
                  class="font-semibold"
                  :class="subject.rate >= 85 ? 'text-green-600' : subject.rate >= 70 ? 'text-yellow-600' : 'text-red-600'"
                >
                  {{ subject.rate }}%
                </span>
              </div>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-slate-100">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: subject.rate + '%', backgroundColor: subject.color }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Students Ranking -->
    <div class="mt-6 rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div class="border-b border-slate-200 p-6">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-800">Talabalar reytingi</h2>
          <div class="flex items-center gap-2">
            <button 
              @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
              class="rounded-lg bg-slate-100 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-200"
            >
              {{ sortOrder === 'desc' ? '↓ Kamayish' : '↑ Ortish' }}
            </button>
          </div>
        </div>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="(student, index) in rankedStudents" 
          :key="student.id"
          class="flex items-center gap-4 p-4 transition-colors hover:bg-slate-50"
        >
          <div 
            class="flex h-8 w-8 items-center justify-center rounded-lg text-sm font-bold"
            :class="index < 3 ? 'bg-yellow-100 text-yellow-600' : 'bg-slate-100 text-slate-500'"
          >
            {{ index + 1 }}
          </div>

          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 font-bold text-white">
            {{ student.name.charAt(0) }}
          </div>

          <div class="min-w-0 flex-1">
            <p class="font-medium text-slate-800">{{ student.name }}</p>
            <p class="text-sm text-slate-500">{{ student.total }} ta dars</p>
          </div>

          <div class="flex items-center gap-3">
            <div class="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
              <div 
                class="h-full rounded-full transition-all"
                :class="student.rate >= 85 ? 'bg-green-500' : student.rate >= 70 ? 'bg-yellow-500' : 'bg-red-500'"
                :style="{ width: student.rate + '%' }"
              ></div>
            </div>
            <span 
              class="w-12 text-right font-semibold"
              :class="student.rate >= 85 ? 'text-green-600' : student.rate >= 70 ? 'text-yellow-600' : 'text-red-600'"
            >
              {{ student.rate }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Modal -->
    <Teleport to="body">
      <div
        v-if="showExportModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="showExportModal = false"
      >
        <div class="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
          <div class="mb-6 flex items-center justify-between">
            <h2 class="text-xl font-bold text-slate-800">Hisobotni eksport qilish</h2>
            <button @click="showExportModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>

          <!-- Export Format -->
          <div class="mb-6">
            <label class="mb-3 block text-sm font-medium text-slate-700">Format tanlang</label>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <button
                v-for="format in exportFormats"
                :key="format.value"
                @click="selectedFormat = format.value"
                class="flex flex-col items-center gap-2 rounded-xl border p-4 transition-all"
                :class="selectedFormat === format.value 
                  ? 'border-emerald-500 bg-emerald-50' 
                  : 'border-slate-200 hover:border-slate-300'"
              >
                <component :is="format.icon" :size="32" :class="format.color" />
                <span class="text-sm font-medium text-slate-800">{{ format.label }}</span>
                <span class="text-xs text-slate-500">{{ format.ext }}</span>
              </button>
            </div>
          </div>

          <!-- Template Selection -->
          <div class="mb-6">
            <label class="mb-3 block text-sm font-medium text-slate-700">Shablon tanlang</label>
            <div class="space-y-2">
              <div
                v-for="template in templates"
                :key="template.id"
                @click="selectedTemplate = template.id"
                class="flex cursor-pointer items-center gap-4 rounded-xl border p-4 transition-all"
                :class="selectedTemplate === template.id 
                  ? 'border-emerald-500 bg-emerald-50' 
                  : 'border-slate-200 hover:border-slate-300'"
              >
                <div class="flex h-12 w-12 items-center justify-center rounded-xl" :class="template.bgColor">
                  <component :is="template.icon" :size="24" :class="template.iconColor" />
                </div>
                <div class="flex-1">
                  <p class="font-medium text-slate-800">{{ template.name }}</p>
                  <p class="text-sm text-slate-500">{{ template.description }}</p>
                </div>
                <div 
                  class="h-5 w-5 rounded-full border-2 flex items-center justify-center"
                  :class="selectedTemplate === template.id ? 'border-emerald-500 bg-emerald-500' : 'border-slate-300'"
                >
                  <Check v-if="selectedTemplate === template.id" :size="12" class="text-white" />
                </div>
              </div>
            </div>
          </div>

          <!-- Data Selection -->
          <div class="mb-6">
            <label class="mb-3 block text-sm font-medium text-slate-300">Ma'lumotlar</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="data in dataOptions"
                :key="data.id"
                @click="toggleDataOption(data.id)"
                class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-all"
                :class="selectedDataOptions.includes(data.id) 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'"
              >
                <component :is="data.icon" :size="16" />
                {{ data.label }}
              </button>
            </div>
          </div>

          <!-- Date Range -->
          <div class="mb-6">
            <label class="mb-3 block text-sm font-medium text-slate-300">Sana oralig'i</label>
            <div class="flex items-center gap-3">
              <input
                v-model="exportDateRange.start"
                type="date"
                class="flex-1 rounded-lg border border-slate-600 bg-slate-700 px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
              <span class="text-slate-400">—</span>
              <input
                v-model="exportDateRange.end"
                type="date"
                class="flex-1 rounded-lg border border-slate-600 bg-slate-700 px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <!-- Preview -->
          <div class="mb-6 rounded-xl bg-slate-700/50 p-4">
            <div class="mb-2 flex items-center gap-2 text-sm text-slate-400">
              <Eye :size="16" />
              Oldindan ko'rish
            </div>
            <div class="text-sm text-slate-300">
              <p><strong>Format:</strong> {{ getFormatLabel(selectedFormat) }}</p>
              <p><strong>Shablon:</strong> {{ getTemplateLabel(selectedTemplate) }}</p>
              <p><strong>Ma'lumotlar:</strong> {{ selectedDataOptions.length }} ta bo'lim</p>
              <p><strong>Davr:</strong> {{ exportDateRange.start }} — {{ exportDateRange.end }}</p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3">
            <button
              @click="showExportModal = false"
              class="rounded-lg border border-slate-600 px-4 py-2 text-slate-300 hover:bg-slate-700"
            >
              Bekor qilish
            </button>
            <button
              @click="generateExport"
              :disabled="exporting"
              class="flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
            >
              <Loader2 v-if="exporting" :size="18" class="animate-spin" />
              <Download v-else :size="18" />
              {{ exporting ? 'Tayyorlanmoqda...' : 'Yuklab olish' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import {
  Download, TrendingUp, BookOpen, Award, AlertTriangle, X, Check, Eye,
  FileText, FileSpreadsheet, File, Printer, Loader2, Users, Calendar,
  ClipboardCheck, BarChart3, Clock
} from 'lucide-vue-next'

const dataStore = useDataStore()
const authStore = useAuthStore()
const toast = useToastStore()

// State
const selectedPeriod = ref('month')
const sortOrder = ref('desc')
const showExportModal = ref(false)
const selectedFormat = ref('xlsx')
const selectedTemplate = ref('full')
const selectedDataOptions = ref(['attendance', 'students', 'subjects'])
const exporting = ref(false)

const exportDateRange = ref({
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0]
})

// Export formats
const exportFormats = [
  { value: 'xlsx', label: 'Excel', ext: '.xlsx', icon: FileSpreadsheet, color: 'text-green-400' },
  { value: 'pdf', label: 'PDF', ext: '.pdf', icon: FileText, color: 'text-red-400' },
  { value: 'csv', label: 'CSV', ext: '.csv', icon: File, color: 'text-blue-400' },
  { value: 'print', label: 'Chop etish', ext: '', icon: Printer, color: 'text-purple-400' }
]

// Templates
const templates = [
  { 
    id: 'full', 
    name: 'To\'liq hisobot', 
    description: 'Barcha ma\'lumotlar bilan batafsil hisobot',
    icon: ClipboardCheck,
    bgColor: 'bg-blue-500/20',
    iconColor: 'text-blue-400'
  },
  { 
    id: 'summary', 
    name: 'Qisqacha xulosa', 
    description: 'Faqat asosiy ko\'rsatkichlar',
    icon: BarChart3,
    bgColor: 'bg-green-500/20',
    iconColor: 'text-green-400'
  },
  { 
    id: 'students', 
    name: 'Talabalar ro\'yxati', 
    description: 'Har bir talaba uchun alohida statistika',
    icon: Users,
    bgColor: 'bg-purple-500/20',
    iconColor: 'text-purple-400'
  },
  { 
    id: 'attendance', 
    name: 'Davomat jadvali', 
    description: 'Kunlik davomat ma\'lumotlari',
    icon: Calendar,
    bgColor: 'bg-orange-500/20',
    iconColor: 'text-orange-400'
  }
]

// Data options
const dataOptions = [
  { id: 'attendance', label: 'Davomat', icon: ClipboardCheck },
  { id: 'students', label: 'Talabalar', icon: Users },
  { id: 'subjects', label: 'Fanlar', icon: BookOpen },
  { id: 'trends', label: 'Trendlar', icon: TrendingUp },
  { id: 'late', label: 'Kechikishlar', icon: Clock }
]

// Computed
const currentGroup = computed(() => {
  const groupId = authStore.user?.groupId
  return dataStore.groups.find(g => g.id === groupId)
})

const groupStudents = computed(() => {
  const groupId = authStore.user?.groupId
  return dataStore.students.filter(s => s.groupId === groupId)
})

const overallAttendance = computed(() => {
  return 87 // Simulated
})

const totalLessons = computed(() => {
  return 156
})

const bestAttendee = computed(() => {
  const ranked = rankedStudents.value
  return ranked.length > 0 ? ranked[0].name.split(' ')[0] : '—'
})

const lowAttendanceCount = computed(() => {
  return rankedStudents.value.filter(s => s.rate < 70).length
})

const weeklyData = computed(() => {
  const days = ['Du', 'Se', 'Cho', 'Pa', 'Ju', 'Sha', 'Ya']
  return days.map((name) => ({
    name,
    rate: Math.floor(Math.random() * 30) + 70
  }))
})

const rankedStudents = computed(() => {
  const students = groupStudents.value.map(student => {
    const rate = Math.floor(Math.random() * 30) + 70
    return { ...student, rate, total: Math.floor(Math.random() * 20) + 80 }
  })
  
  return sortOrder.value === 'desc' 
    ? students.sort((a, b) => b.rate - a.rate)
    : students.sort((a, b) => a.rate - b.rate)
})

const subjectStats = computed(() => {
  const subjects = ['Matematika', 'Fizika', 'Informatika', 'Ingliz tili', 'Tarix']
  const colors = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EC4899']
  
  return subjects.map((name, index) => ({
    name,
    color: colors[index],
    present: Math.floor(Math.random() * 50) + 100,
    absent: Math.floor(Math.random() * 20) + 5,
    rate: Math.floor(Math.random() * 20) + 75
  }))
})

// Methods
function toggleDataOption(id) {
  const index = selectedDataOptions.value.indexOf(id)
  if (index === -1) {
    selectedDataOptions.value.push(id)
  } else {
    selectedDataOptions.value.splice(index, 1)
  }
}

function getFormatLabel(format) {
  return exportFormats.find(f => f.value === format)?.label || format
}

function getTemplateLabel(template) {
  return templates.find(t => t.id === template)?.name || template
}

function generateExport() {
  exporting.value = true
  
  setTimeout(() => {
    exporting.value = false
    showExportModal.value = false
    
    if (selectedFormat.value === 'print') {
      toast.info('Chop etish oynasi ochilmoqda...')
      window.print()
    } else {
      toast.success(`Hisobot ${getFormatLabel(selectedFormat.value)} formatida tayyor!`)
      
      // Simulate download
      const filename = `hisobot_${currentGroup.value?.name || 'guruh'}_${new Date().toISOString().split('T')[0]}.${selectedFormat.value}`
      toast.info(`"${filename}" yuklab olinmoqda...`)
    }
  }, 2000)
}
</script>
