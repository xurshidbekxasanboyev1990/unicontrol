<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <Brain :size="28" />
            <h1 class="text-xl font-bold">{{ t('academic.aiGenerate') }}</h1>
          </div>
          <p class="text-purple-100 text-sm">{{ t('academic.aiDescription') }}</p>
        </div>
        <!-- Export button -->
        <button
          @click="exportAllSchedules"
          :disabled="exporting"
          class="flex items-center gap-2 rounded-xl bg-white/20 px-5 py-2.5 text-sm font-medium text-white hover:bg-white/30 transition-colors backdrop-blur-sm border border-white/30"
        >
          <Loader2 v-if="exporting" :size="16" class="animate-spin" />
          <Download v-else :size="16" />
          {{ exporting ? 'Yuklanmoqda...' : 'Jadval eksport (Excel)' }}
        </button>
      </div>
    </div>

    <!-- Steps indicator -->
    <div class="flex items-center gap-2 px-2">
      <div v-for="(s, idx) in steps" :key="idx" class="flex items-center gap-2">
        <div :class="[
          'flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all',
          currentStep > idx ? 'bg-green-500 text-white' :
          currentStep === idx ? 'bg-purple-600 text-white ring-4 ring-purple-100' :
          'bg-gray-200 text-gray-500'
        ]">
          <Check v-if="currentStep > idx" :size="14" />
          <span v-else>{{ idx + 1 }}</span>
        </div>
        <span :class="['text-sm font-medium', currentStep >= idx ? 'text-gray-800' : 'text-gray-400']">{{ s }}</span>
        <ChevronRight v-if="idx < steps.length - 1" :size="14" class="text-gray-300 mx-1" />
      </div>
    </div>

    <!-- STEP 1: Guruhlarni tanlash -->
    <div v-if="currentStep === 0" class="space-y-4">
      <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
            <Users :size="20" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">1-qadam: Guruhlarni tanlang</h3>
            <p class="text-sm text-gray-500">AI jadval yaratishi kerak bo'lgan guruhlarni belgilang</p>
          </div>
        </div>

        <!-- Search -->
        <div class="relative mb-4">
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            v-model="groupSearch"
            type="text"
            class="w-full rounded-xl border border-gray-200 pl-10 pr-4 py-2.5 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            placeholder="Guruh qidiring..."
          />
        </div>

        <!-- Faculty filter -->
        <div class="flex flex-wrap gap-2 mb-4">
          <button
            v-for="fac in faculties"
            :key="fac"
            @click="selectedFaculty = selectedFaculty === fac ? '' : fac"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
              selectedFaculty === fac ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ fac }}
          </button>
        </div>

        <!-- Select all / deselect -->
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">{{ selectedGroupIds.length }} ta guruh tanlandi</span>
          <div class="flex gap-2">
            <button @click="selectAllFilteredGroups" class="text-xs text-purple-600 hover:text-purple-700 font-medium">Hammasini tanlash</button>
            <button v-if="selectedGroupIds.length > 0" @click="selectedGroupIds = []" class="text-xs text-red-500 hover:text-red-600 font-medium">Tozalash</button>
          </div>
        </div>

        <!-- Groups grid -->
        <div class="max-h-[320px] overflow-y-auto space-y-1 border rounded-xl p-2">
          <label
            v-for="g in filteredGroups"
            :key="g.id"
            :class="[
              'flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors',
              selectedGroupIds.includes(g.id) ? 'bg-purple-50 border border-purple-200' : 'hover:bg-gray-50'
            ]"
          >
            <input
              type="checkbox"
              :value="g.id"
              v-model="selectedGroupIds"
              class="rounded text-purple-600 focus:ring-purple-500"
            />
            <div class="flex-1 min-w-0">
              <span class="text-sm font-medium text-gray-800">{{ g.name }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ g.faculty }}</span>
            </div>
            <span class="text-xs text-gray-400">{{ g.course_year }}-kurs</span>
            <span class="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full">{{ g.schedule_count }} dars</span>
          </label>
          <div v-if="filteredGroups.length === 0" class="py-6 text-center text-sm text-gray-400">
            Guruh topilmadi
          </div>
        </div>
      </div>

      <button
        @click="currentStep = 1"
        :disabled="selectedGroupIds.length === 0"
        class="w-full rounded-xl bg-purple-600 px-6 py-3 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
      >
        Keyingi qadam
        <ArrowRight :size="16" />
      </button>
    </div>

    <!-- STEP 2: Fanlar va o'qituvchilar -->
    <div v-if="currentStep === 1" class="space-y-4">
      <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
            <BookOpen :size="20" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">2-qadam: Fanlar va soatlarni kiriting</h3>
            <p class="text-sm text-gray-500">Har bir fanning nomi, turi va haftalik soatlarini belgilang</p>
          </div>
        </div>

        <!-- Subject cards -->
        <div class="space-y-3">
          <div
            v-for="(subj, idx) in subjects"
            :key="idx"
            class="rounded-xl border border-gray-200 p-4 hover:border-purple-200 transition-colors"
          >
            <div class="flex items-start gap-3">
              <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-100 text-blue-700 text-xs font-bold mt-0.5">
                {{ idx + 1 }}
              </span>
              <div class="flex-1 space-y-3">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div class="md:col-span-1">
                    <label class="text-xs text-gray-500 mb-1 block">Fan nomi *</label>
                    <input
                      v-model="subjects[idx].name"
                      type="text"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                      placeholder="Masalan: Matematika"
                    />
                  </div>
                  <div>
                    <label class="text-xs text-gray-500 mb-1 block">Dars turi</label>
                    <select v-model="subjects[idx].type" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500">
                      <option value="lecture">📖 Ma'ruza</option>
                      <option value="practice">✏️ Amaliy</option>
                      <option value="lab">🔬 Laboratoriya</option>
                      <option value="seminar">💬 Seminar</option>
                    </select>
                  </div>
                  <div>
                    <label class="text-xs text-gray-500 mb-1 block">Haftalik soat</label>
                    <input
                      v-model.number="subjects[idx].hours"
                      type="number"
                      min="1"
                      max="10"
                      class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-center focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                      placeholder="2"
                    />
                  </div>
                </div>
              </div>
              <button
                @click="subjects.splice(idx, 1)"
                class="text-gray-300 hover:text-red-500 transition-colors mt-5"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </div>
        </div>

        <button
          @click="subjects.push({ name: '', type: 'lecture', hours: 2 })"
          class="mt-3 flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700 font-medium px-3 py-2 rounded-lg hover:bg-purple-50 transition-colors"
        >
          <Plus :size="14" />
          Fan qo'shish
        </button>
      </div>

      <!-- Rooms & constraints -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
          <div class="flex items-center gap-2 mb-3">
            <Building2 :size="16" class="text-gray-500" />
            <h3 class="text-sm font-semibold text-gray-700">Xonalar (ixtiyoriy)</h3>
          </div>
          <textarea
            v-model="roomsText"
            class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm min-h-[100px] focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            placeholder="Har bir qatorda bitta xona&#10;401-xona A bino&#10;302-xona B bino"
          ></textarea>
        </div>

        <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
          <div class="flex items-center gap-2 mb-3">
            <Settings :size="16" class="text-gray-500" />
            <h3 class="text-sm font-semibold text-gray-700">Qo'shimcha shartlar (ixtiyoriy)</h3>
          </div>
          <textarea
            v-model="constraintsText"
            class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm min-h-[100px] focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            placeholder="Masalan:&#10;- Shanba kuni dars bo'lmasin&#10;- Matematika faqat ertalab bo'lsin&#10;- 1 kunda 4 paradan oshmasin"
          ></textarea>
        </div>
      </div>

      <div class="flex gap-3">
        <button
          @click="currentStep = 0"
          class="rounded-xl border border-gray-200 px-6 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 flex items-center gap-2"
        >
          <ArrowLeft :size="16" />
          Orqaga
        </button>
        <button
          @click="currentStep = 2; generateSchedule()"
          :disabled="subjects.filter(s => s.name.trim()).length === 0"
          class="flex-1 rounded-xl bg-purple-600 px-6 py-3 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <Brain :size="16" />
          AI bilan jadval yaratish
          <ArrowRight :size="16" />
        </button>
      </div>
    </div>

    <!-- STEP 3: Natija -->
    <div v-if="currentStep === 2" class="space-y-4">
      <!-- Generating animation -->
      <div v-if="generating" class="rounded-2xl bg-white p-12 shadow-sm border border-gray-100 text-center">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-100 mb-4">
          <Loader2 :size="36" class="animate-spin text-purple-500" />
        </div>
        <h3 class="text-lg font-bold text-gray-800 mb-2">AI jadval yaratmoqda...</h3>
        <p class="text-sm text-gray-500 mb-4">Bu 1-2 daqiqa vaqt olishi mumkin</p>
        <div class="flex justify-center gap-1">
          <span v-for="i in 3" :key="i" class="w-2.5 h-2.5 bg-purple-400 rounded-full animate-bounce" :style="{ animationDelay: `${i * 0.15}s` }"></span>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="generateError" class="rounded-2xl bg-red-50 p-8 border border-red-200 text-center">
        <AlertCircle :size="40" class="mx-auto mb-3 text-red-400" />
        <h3 class="text-base font-bold text-red-700 mb-2">Xatolik yuz berdi</h3>
        <p class="text-sm text-red-600 mb-4">{{ generateError }}</p>
        <div class="flex gap-3 justify-center">
          <button @click="currentStep = 1" class="rounded-xl border border-red-200 px-5 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50">
            <ArrowLeft :size="14" class="inline mr-1" />
            Qayta tahrirlash
          </button>
          <button @click="generateSchedule" class="rounded-xl bg-red-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-red-700">
            Qayta urinish
          </button>
        </div>
      </div>

      <!-- Result -->
      <div v-else-if="result" class="space-y-4">
        <!-- Success header -->
        <div class="rounded-2xl bg-green-50 p-5 border border-green-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-600">
                <Sparkles :size="24" />
              </div>
              <div>
                <h3 class="text-base font-bold text-green-800">Jadval muvaffaqiyatli yaratildi!</h3>
                <p class="text-sm text-green-600">
                  {{ result.schedules?.length || 0 }} ta dars, {{ selectedGroupIds.length }} ta guruh uchun
                </p>
              </div>
            </div>
            <button
              @click="applyResult"
              :disabled="applying"
              class="rounded-xl bg-green-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Loader2 v-if="applying" :size="14" class="animate-spin" />
              <Check v-else :size="14" />
              {{ applying ? 'Qo\'llanmoqda...' : 'Jadvalni bazaga saqlash' }}
            </button>
          </div>
        </div>

        <!-- Preview per group -->
        <div class="rounded-2xl bg-white shadow-sm border border-gray-100 overflow-hidden">
          <!-- Group tabs -->
          <div class="flex border-b overflow-x-auto bg-gray-50">
            <button
              @click="previewTab = 'all'"
              :class="[
                'px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
                previewTab === 'all' ? 'border-purple-600 text-purple-700 bg-white' : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Barchasi ({{ result.schedules?.length || 0 }})
            </button>
            <button
              v-for="gid in selectedGroupIds"
              :key="gid"
              @click="previewTab = gid"
              :class="[
                'px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
                previewTab === gid ? 'border-purple-600 text-purple-700 bg-white' : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              {{ getGroupName(gid) }} ({{ getGroupScheduleCount(gid) }})
            </button>
          </div>

          <!-- Table -->
          <div class="max-h-[450px] overflow-y-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th class="px-3 py-2.5 text-left font-semibold text-gray-600">Kun</th>
                  <th class="px-3 py-2.5 text-center font-semibold text-gray-600">Para</th>
                  <th class="px-3 py-2.5 text-left font-semibold text-gray-600">Fan</th>
                  <th class="px-3 py-2.5 text-left font-semibold text-gray-600">Guruh</th>
                  <th class="px-3 py-2.5 text-left font-semibold text-gray-600">Xona</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(s, i) in previewSchedules"
                  :key="i"
                  class="border-t border-gray-100 hover:bg-purple-50/30 transition-colors"
                >
                  <td class="px-3 py-2.5">
                    <span class="inline-flex items-center gap-1.5">
                      <span :class="['w-2 h-2 rounded-full', getDayColor(s.day_of_week)]"></span>
                      {{ getDayLabel(s.day_of_week) }}
                    </span>
                  </td>
                  <td class="px-3 py-2.5 text-center">
                    <span class="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs font-medium">{{ s.lesson_number }}-para</span>
                  </td>
                  <td class="px-3 py-2.5 font-medium text-gray-800">{{ s.subject }}</td>
                  <td class="px-3 py-2.5 text-gray-600">{{ getGroupName(s.group_id) }}</td>
                  <td class="px-3 py-2.5 text-gray-500">{{ s.room || '—' }}</td>
                </tr>
                <tr v-if="previewSchedules.length === 0">
                  <td colspan="5" class="px-3 py-8 text-center text-gray-400">Jadval ma'lumotlari yo'q</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- AI tavsiyalar -->
        <div v-if="result.recommendations" class="rounded-2xl bg-amber-50 p-5 border border-amber-200">
          <div class="flex items-center gap-2 mb-3">
            <Lightbulb :size="18" class="text-amber-600" />
            <h4 class="text-sm font-bold text-amber-800">AI tavsiялари</h4>
          </div>
          <p class="text-sm text-amber-700 whitespace-pre-wrap leading-relaxed">{{ result.recommendations }}</p>
        </div>

        <!-- Action buttons -->
        <div class="flex gap-3">
          <button
            @click="currentStep = 1"
            class="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 flex items-center gap-2"
          >
            <ArrowLeft :size="14" />
            Qayta tahrirlash
          </button>
          <button
            @click="resetAll"
            class="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 flex items-center gap-2"
          >
            <RotateCcw :size="14" />
            Yangi jadval yaratish
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg flex items-center gap-2', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        <Check v-if="toast.type === 'success'" :size="16" />
        <AlertCircle v-else :size="16" />
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {
    AlertCircle, ArrowLeft, ArrowRight, BookOpen, Brain, Building2, Check, ChevronRight,
    Download, Lightbulb, Loader2, Plus, RotateCcw, Search, Settings, Sparkles, Trash2, Users
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const toast = ref(null)
const generating = ref(false)
const applying = ref(false)
const exporting = ref(false)
const generateError = ref(null)
const result = ref(null)
const currentStep = ref(0)
const previewTab = ref('all')

const steps = ['Guruhlarni tanlash', 'Fanlar va shartlar', 'Natija']

// Groups
const allGroups = ref([])
const selectedGroupIds = ref([])
const groupSearch = ref('')
const selectedFaculty = ref('')

// Subjects
const subjects = ref([
  { name: '', type: 'lecture', hours: 2 },
  { name: '', type: 'practice', hours: 2 },
])
const roomsText = ref('')
const constraintsText = ref('')

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3500)
}

// Computed
const faculties = computed(() => {
  const set = new Set(allGroups.value.map(g => g.faculty).filter(Boolean))
  return [...set].sort()
})

const filteredGroups = computed(() => {
  let list = allGroups.value
  if (selectedFaculty.value) {
    list = list.filter(g => g.faculty === selectedFaculty.value)
  }
  if (groupSearch.value) {
    const q = groupSearch.value.toLowerCase()
    list = list.filter(g => g.name.toLowerCase().includes(q))
  }
  return list
})

const previewSchedules = computed(() => {
  if (!result.value?.schedules) return []
  if (previewTab.value === 'all') return result.value.schedules
  return result.value.schedules.filter(s => s.group_id === previewTab.value)
})

const selectAllFilteredGroups = () => {
  const ids = filteredGroups.value.map(g => g.id)
  const merged = new Set([...selectedGroupIds.value, ...ids])
  selectedGroupIds.value = [...merged]
}

const getGroupName = (groupId) => {
  const g = allGroups.value.find(x => x.id === groupId)
  return g?.name || groupId
}

const getGroupScheduleCount = (groupId) => {
  if (!result.value?.schedules) return 0
  return result.value.schedules.filter(s => s.group_id === groupId).length
}

const dayLabels = {
  monday: 'Dushanba', tuesday: 'Seshanba', wednesday: 'Chorshanba',
  thursday: 'Payshanba', friday: 'Juma', saturday: 'Shanba'
}
const dayColors = {
  monday: 'bg-blue-500', tuesday: 'bg-green-500', wednesday: 'bg-yellow-500',
  thursday: 'bg-orange-500', friday: 'bg-red-500', saturday: 'bg-purple-500'
}

const getDayLabel = (day) => dayLabels[day] || day
const getDayColor = (day) => dayColors[day] || 'bg-gray-400'

// Load groups
const loadGroups = async () => {
  try {
    const res = await api.request('/academic/groups')
    allGroups.value = res.items || []
  } catch (e) {
    console.error(e)
  }
}

// Generate schedule
const generateSchedule = async () => {
  const validSubjects = subjects.value.filter(s => s.name.trim())
  if (selectedGroupIds.value.length === 0 || validSubjects.length === 0) {
    showToast('Guruhlar va fanlarni tanlang', 'error')
    return
  }

  generating.value = true
  generateError.value = null
  result.value = null

  try {
    const rooms = roomsText.value.split('\n').map(s => s.trim()).filter(Boolean)
    const body = {
      group_ids: selectedGroupIds.value,
      subjects: validSubjects.map(s => ({
        name: s.name,
        type: s.type,
        hours_per_week: s.hours
      })),
      rooms,
      constraints: constraintsText.value || '',
      language: 'uz'
    }

    const res = await api.request('/academic/ai/generate', { method: 'POST', body })
    result.value = res
    previewTab.value = 'all'
    showToast('Jadval muvaffaqiyatli yaratildi!')
  } catch (e) {
    generateError.value = e.data?.detail || e.message || 'AI xatolik yuz berdi'
  } finally {
    generating.value = false
  }
}

// Apply result
const applyResult = async () => {
  if (!result.value?.schedules?.length) return
  applying.value = true
  try {
    const res = await api.request('/academic/schedules/bulk', {
      method: 'POST',
      body: { schedules: result.value.schedules }
    })
    showToast(`${res.created || result.value.schedules.length} ta dars bazaga saqlandi!`)
  } catch (e) {
    showToast(e.data?.detail || 'Saqlashda xatolik', 'error')
  } finally {
    applying.value = false
  }
}

// Export all schedules
const exportAllSchedules = async () => {
  exporting.value = true
  try {
    const res = await fetch('/api/v1/academic/schedules/export', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    if (!res.ok) throw new Error('Export xatolik')

    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'dars_jadvali_barcha_guruhlar.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    showToast('Dars jadvali Excel fayli yuklab olindi!')
  } catch (e) {
    showToast('Eksport xatolik: ' + (e.message || 'Noma\'lum xato'), 'error')
  } finally {
    exporting.value = false
  }
}

// Reset
const resetAll = () => {
  currentStep.value = 0
  result.value = null
  generateError.value = null
  selectedGroupIds.value = []
  subjects.value = [
    { name: '', type: 'lecture', hours: 2 },
    { name: '', type: 'practice', hours: 2 },
  ]
  roomsText.value = ''
  constraintsText.value = ''
  previewTab.value = 'all'
}

onMounted(loadGroups)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
