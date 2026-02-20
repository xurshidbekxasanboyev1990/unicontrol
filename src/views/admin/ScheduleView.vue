<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('schedule.title') }}</h1>
        <p class="text-sm text-slate-500">{{ totalSchedules }} {{ $t('schedule.lessonsCount') }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <button @click="openCreateModal" class="px-4 py-2.5 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors flex items-center gap-2">
          <Plus class="w-5 h-5" />
          <span class="hidden sm:inline">{{ $t('schedule.addLesson') }}</span>
        </button>
        <button @click="loadSchedules" class="p-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors">
          <RefreshCw class="w-5 h-5 text-slate-500" :class="loading && 'animate-spin'" />
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Group filter -->
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">{{ $t('attendance.group') }}</label>
          <select v-model="filterGroupId" @change="loadSchedules" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
            <option :value="null">{{ $t('attendance.allGroups') }}</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <!-- Day filter -->
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">{{ $t('schedule.day') }}</label>
          <select v-model="filterDay" @change="loadSchedules" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
            <option :value="null">{{ $t('schedule.allDays') }}</option>
            <option value="monday">{{ $t('schedule.monday') }}</option>
            <option value="tuesday">{{ $t('schedule.tuesday') }}</option>
            <option value="wednesday">{{ $t('schedule.wednesday') }}</option>
            <option value="thursday">{{ $t('schedule.thursday') }}</option>
            <option value="friday">{{ $t('schedule.friday') }}</option>
            <option value="saturday">{{ $t('schedule.saturday') }}</option>
          </select>
        </div>
        <!-- View mode -->
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">{{ $t('common.view') }}</label>
          <div class="flex gap-1 bg-slate-100 rounded-xl p-1">
            <button @click="viewMode = 'table'" :class="['flex-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors', viewMode === 'table' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500']">
              {{ $t('schedule.tableView') }}
            </button>
            <button @click="viewMode = 'week'" :class="['flex-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors', viewMode === 'week' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500']">
              {{ $t('schedule.weekly') }}
            </button>
          </div>
        </div>
        <!-- Search -->
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">{{ $t('common.search') }}</label>
          <div class="relative">
            <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input v-model="searchQuery" :placeholder="$t('common.search')" class="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <Loader2 class="w-10 h-10 text-emerald-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-500">{{ $t('common.loading') }}</p>
      </div>
    </div>

    <!-- Table View -->
    <template v-else-if="viewMode === 'table'">
      <div v-if="filteredSchedules.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
        <CalendarDays class="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-slate-600">{{ $t('common.noData') }}</h3>
        <p class="text-sm text-slate-400 mt-1">{{ $t('schedule.noLessonsDesc') }}</p>
      </div>

      <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-slate-50 border-b border-slate-200">
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('attendance.group') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('schedule.day') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('schedule.lessonPeriod') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('common.time') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('schedule.subject') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('schedule.teacher') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('schedule.room') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('common.type') }}</th>
                <th class="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">Hafta</th>
                <th class="text-center px-4 py-3 text-xs font-bold text-slate-500 uppercase">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="s in paginatedSchedules" :key="s.id" class="hover:bg-slate-50 transition-colors">
                <td class="px-4 py-3 text-sm font-medium text-slate-800">{{ s.group_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-slate-600">{{ dayLabel(s.day_of_week) }}</td>
                <td class="px-4 py-3 text-sm text-slate-600">{{ s.lesson_number || '-' }}</td>
                <td class="px-4 py-3 text-sm text-slate-600">{{ s.time_range }}</td>
                <td class="px-4 py-3">
                  <p class="text-sm font-medium text-slate-800">{{ s.subject }}</p>
                  <p v-if="s.subject_code" class="text-xs text-slate-400">{{ s.subject_code }}</p>
                </td>
                <td class="px-4 py-3 text-sm text-slate-600">{{ s.teacher_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-slate-600">{{ s.location || s.room || '-' }}</td>
                <td class="px-4 py-3">
                  <span :class="typeClass(s.schedule_type)" class="px-2 py-0.5 rounded-lg text-xs font-medium">
                    {{ typeLabel(s.schedule_type) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span v-if="s.week_type === 'odd'" class="px-2 py-0.5 rounded-lg text-xs font-medium bg-blue-100 text-blue-700">Toq hafta</span>
                  <span v-else-if="s.week_type === 'even'" class="px-2 py-0.5 rounded-lg text-xs font-medium bg-orange-100 text-orange-700">Juft hafta</span>
                  <span v-else class="px-2 py-0.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-500">Har hafta</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <button @click="editSchedule(s)" class="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors" title="Tahrirlash">
                      <Pencil class="w-4 h-4" />
                    </button>
                    <button @click="confirmDelete(s)" class="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="O'chirish">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="flex items-center justify-between px-4 py-3 border-t border-slate-100">
          <p class="text-sm text-slate-500">
            {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredSchedules.length) }} / {{ filteredSchedules.length }}
          </p>
          <div class="flex gap-1">
            <button @click="currentPage--" :disabled="currentPage <= 1" class="px-3 py-1.5 border border-slate-200 rounded-lg text-sm disabled:opacity-40">
              Oldingi
            </button>
            <button @click="currentPage++" :disabled="currentPage >= totalPages" class="px-3 py-1.5 border border-slate-200 rounded-lg text-sm disabled:opacity-40">
              {{ $t('common.next') }}
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Week View (for selected group) -->
    <template v-else-if="viewMode === 'week'">
      <div v-if="!filterGroupId" class="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
        <AlertCircle class="w-8 h-8 text-amber-500 mx-auto mb-2" />
        <p class="font-medium text-amber-800">{{ $t('schedule.selectGroupForWeek') }}</p>
      </div>

      <div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="overflow-x-auto custom-scrollbar">
          <table class="w-full border-collapse" style="min-width: 900px;">
            <thead>
              <tr>
                <th class="sticky left-0 z-10 bg-slate-50 px-4 py-4 text-left text-xs font-bold text-slate-500 uppercase w-[100px] border-b border-slate-200">
                  {{ $t('common.time') }}
                </th>
                <th v-for="day in weekDayKeys" :key="day" class="px-3 py-4 text-center text-xs font-bold uppercase border-b border-l border-slate-200 bg-slate-50 text-slate-500" :class="isTodayDay(day) && 'bg-emerald-50 text-emerald-700'" style="min-width: 140px;">
                  {{ dayLabel(day) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(slot, idx) in weekTimeSlots" :key="slot" :class="idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
                <td class="sticky left-0 z-10 px-4 py-3 border-b border-slate-100 font-semibold" :class="idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'">
                  <div class="text-sm font-bold text-slate-700">{{ slot.split('-')[0] }}</div>
                  <div class="text-[11px] text-slate-400">{{ slot.split('-')[1] }}</div>
                  <div class="mt-1 text-[10px] text-slate-400 font-bold">{{ idx + 1 }}-{{ $t('schedule.lessonPeriod') }}</div>
                </td>
                <td v-for="day in weekDayKeys" :key="day + slot" class="px-2 py-2 border-b border-l border-slate-100 align-top" :class="isTodayDay(day) && 'bg-emerald-50/30'">
                  <div v-if="getWeekLessons(day, slot).length > 0" class="space-y-1">
                    <div v-for="lesson in getWeekLessons(day, slot)" :key="lesson.id" class="rounded-xl p-2.5 text-sm cursor-pointer hover:shadow-md transition-all" :class="getSubjectBg(lesson.subject)" @click="editSchedule(lesson)">
                      <div class="flex items-center gap-1 mb-1">
                        <p class="font-bold text-slate-800 text-[13px] leading-snug truncate flex-1">{{ lesson.subject }}</p>
                        <span v-if="lesson.week_type === 'odd'" class="shrink-0 px-1 py-0.5 rounded text-[9px] font-bold bg-blue-100 text-blue-700">Toq</span>
                        <span v-else-if="lesson.week_type === 'even'" class="shrink-0 px-1 py-0.5 rounded text-[9px] font-bold bg-orange-100 text-orange-700">Juft</span>
                      </div>
                      <p v-if="lesson.teacher_name" class="text-[11px] text-slate-500 flex items-center gap-1">
                        <User class="w-3 h-3" /> {{ lesson.teacher_name }}
                      </p>
                      <p v-if="lesson.room || lesson.location" class="text-[11px] text-slate-500 flex items-center gap-1">
                        <MapPin class="w-3 h-3" /> {{ lesson.location || lesson.room }}
                      </p>
                    </div>
                  </div>
                  <div v-else class="h-full min-h-[60px] flex items-center justify-center">
                    <button @click="quickAdd(day, idx + 1, slot)" class="w-6 h-6 rounded-full border-2 border-dashed border-slate-200 flex items-center justify-center hover:border-emerald-400 hover:text-emerald-500 text-slate-300 transition-colors">
                      <Plus class="w-3 h-3" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showModal = false">
        <div class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-lg font-bold text-slate-800">{{ editingId ? $t('schedule.editLesson') : $t('schedule.addLesson') }}</h3>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg"><X class="w-5 h-5 text-slate-500" /></button>
          </div>
          <div class="p-6 space-y-4">
            <!-- Group -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('attendance.group') }} *</label>
              <select v-model="form.group_id" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" required>
                <option :value="null" disabled>{{ $t('common.select') }}</option>
                <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
            </div>
            <!-- Subject -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.subject') }} *</label>
              <input v-model="form.subject" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" :placeholder="$t('schedule.subject')" required />
            </div>
            <!-- Day + Lesson number -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.day') }} *</label>
                <select v-model="form.day_of_week" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" required>
                  <option :value="null" disabled>{{ $t('common.select') }}</option>
                  <option value="monday">{{ $t('schedule.monday') }}</option>
                  <option value="tuesday">{{ $t('schedule.tuesday') }}</option>
                  <option value="wednesday">{{ $t('schedule.wednesday') }}</option>
                  <option value="thursday">{{ $t('schedule.thursday') }}</option>
                  <option value="friday">{{ $t('schedule.friday') }}</option>
                  <option value="saturday">{{ $t('schedule.saturday') }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.lessonPeriod') }} №</label>
                <select v-model.number="form.lesson_number" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
                  <option :value="null">-</option>
                  <option v-for="n in 7" :key="n" :value="n">{{ n }}-{{ $t('schedule.lessonPeriod') }}</option>
                </select>
              </div>
            </div>
            <!-- Time -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.startTime') }} *</label>
                <input v-model="form.start_time" type="time" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.endTime') }} *</label>
                <input v-model="form.end_time" type="time" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" required />
              </div>
            </div>
            <!-- Auto-fill from lesson number -->
            <div v-if="form.lesson_number && !editingId" class="flex items-center gap-2">
              <button @click="autoFillTime" class="text-xs text-emerald-600 hover:text-emerald-700 underline">{{ $t('schedule.autoFillTime') }}</button>
            </div>
            <!-- Teacher -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.teacher') }}</label>
              <input v-model="form.teacher_name" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" :placeholder="$t('schedule.teacher')" />
            </div>
            <!-- Room + Building -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.room') }}</label>
                <input v-model="form.room" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" :placeholder="$t('schedule.room')" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.building') }}</label>
                <input v-model="form.building" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500" :placeholder="$t('schedule.building')" />
              </div>
            </div>
            <!-- Type -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('schedule.lessonType') }}</label>
              <select v-model="form.schedule_type" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
                <option value="lecture">{{ $t('schedule.lecture') }}</option>
                <option value="practice">{{ $t('schedule.practice') }}</option>
                <option value="lab">{{ $t('schedule.lab') }}</option>
                <option value="seminar">{{ $t('schedule.seminar') }}</option>
              </select>
            </div>
            <!-- Week Type -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Hafta turi</label>
              <select v-model="form.week_type" class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
                <option value="all">Har hafta</option>
                <option value="odd">Toq hafta</option>
                <option value="even">Juft hafta</option>
              </select>
            </div>
          </div>
          <div class="p-6 border-t border-slate-100 flex gap-3">
            <button @click="showModal = false" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200 transition-colors">{{ $t('common.cancel') }}</button>
            <button @click="saveSchedule" :disabled="saving" class="flex-1 py-2.5 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
              <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
              {{ editingId ? $t('common.save') : $t('common.add') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showDeleteModal = false">
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl">
          <div class="text-center">
            <div class="w-14 h-14 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Trash2 class="w-7 h-7 text-red-500" />
            </div>
            <h3 class="text-lg font-bold text-slate-800 mb-2">{{ $t('schedule.deleteLesson') }}</h3>
            <p class="text-sm text-slate-500">
              <strong>{{ deletingSchedule?.subject }}</strong> — {{ $t('common.confirm') }}?
            </p>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="showDeleteModal = false" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-xl font-medium hover:bg-slate-200">{{ $t('common.cancel') }}</button>
            <button @click="deleteSchedule" :disabled="saving" class="flex-1 py-2.5 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 disabled:opacity-50">{{ $t('common.delete') }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import {
    AlertCircle, CalendarDays, Loader2, MapPin, Pencil, Plus,
    RefreshCw, Search, Trash2, User, X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const toast = useToastStore()
const { t } = useLanguageStore()

// State
const loading = ref(false)
const saving = ref(false)
const schedules = ref([])
const groups = ref([])
const totalSchedules = ref(0)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingId = ref(null)
const deletingSchedule = ref(null)
const viewMode = ref('table')
const currentPage = ref(1)
const pageSize = 50
const searchQuery = ref('')
const filterGroupId = ref(null)
const filterDay = ref(null)

// Default time slots
const DEFAULT_TIMES = {
  1: { start: '08:30', end: '09:50' },
  2: { start: '10:00', end: '11:20' },
  3: { start: '12:00', end: '13:20' },
  4: { start: '13:30', end: '14:50' },
  5: { start: '15:00', end: '16:20' },
  6: { start: '16:30', end: '17:50' },
  7: { start: '18:00', end: '19:20' },
}

const weekDayKeys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

const defaultForm = () => ({
  group_id: null,
  subject: '',
  schedule_type: 'lecture',
  day_of_week: null,
  start_time: '08:30',
  end_time: '09:50',
  lesson_number: null,
  room: '',
  building: '',
  teacher_name: '',
  week_type: 'all',
})

const form = ref(defaultForm())

// Computed
const filteredSchedules = computed(() => {
  let list = schedules.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s =>
      (s.subject || '').toLowerCase().includes(q) ||
      (s.teacher_name || '').toLowerCase().includes(q) ||
      (s.group_name || '').toLowerCase().includes(q) ||
      (s.room || '').toLowerCase().includes(q)
    )
  }
  return list
})

const totalPages = computed(() => Math.ceil(filteredSchedules.value.length / pageSize) || 1)

const paginatedSchedules = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredSchedules.value.slice(start, start + pageSize)
})

// Week view: build time slots from actual data for selected group
const weekTimeSlots = computed(() => {
  const slotSet = new Map()
  schedules.value.forEach(s => {
    if (!s.time_range) return
    const clean = s.time_range.replace(/\s/g, '').replace(/(\d{2}:\d{2}):\d{2}/g, '$1')
    const start = clean.split('-')[0]
    if (start && !slotSet.has(start)) {
      slotSet.set(start, clean)
    }
  })
  if (slotSet.size === 0) {
    return Object.values(DEFAULT_TIMES).map(t => `${t.start}-${t.end}`)
  }
  return [...slotSet.entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([, v]) => v)
})

// Color palette for week view
const SUBJECT_COLORS = [
  'bg-emerald-50 border-l-4 border-emerald-500',
  'bg-blue-50 border-l-4 border-blue-500',
  'bg-violet-50 border-l-4 border-violet-500',
  'bg-amber-50 border-l-4 border-amber-500',
  'bg-rose-50 border-l-4 border-rose-500',
  'bg-cyan-50 border-l-4 border-cyan-500',
  'bg-pink-50 border-l-4 border-pink-500',
  'bg-orange-50 border-l-4 border-orange-500',
  'bg-indigo-50 border-l-4 border-indigo-500',
  'bg-teal-50 border-l-4 border-teal-500',
]
const subjectColorIndex = ref({})
const getSubjectBg = (subject) => {
  if (!subject) return SUBJECT_COLORS[0]
  if (subjectColorIndex.value[subject] !== undefined) return SUBJECT_COLORS[subjectColorIndex.value[subject]]
  const idx = Object.keys(subjectColorIndex.value).length % SUBJECT_COLORS.length
  subjectColorIndex.value[subject] = idx
  return SUBJECT_COLORS[idx]
}

// Helpers
const dayLabels = {
  monday: 'Dushanba', tuesday: 'Seshanba', wednesday: 'Chorshanba',
  thursday: 'Payshanba', friday: 'Juma', saturday: 'Shanba', sunday: 'Yakshanba'
}
const dayLabel = (d) => dayLabels[d] || d || '-'

const typeLabels = { lecture: "Ma'ruza", practice: 'Amaliy', lab: 'Lab', seminar: 'Seminar', exam: 'Imtihon', consultation: 'Konsultatsiya' }
const typeLabel = (t) => typeLabels[t] || t || '-'

const typeClass = (t) => ({
  lecture: 'bg-blue-100 text-blue-700',
  practice: 'bg-emerald-100 text-emerald-700',
  lab: 'bg-violet-100 text-violet-700',
  seminar: 'bg-amber-100 text-amber-700',
  exam: 'bg-red-100 text-red-700',
  consultation: 'bg-cyan-100 text-cyan-700',
}[t] || 'bg-slate-100 text-slate-700')

const isTodayDay = (day) => {
  const map = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
  return map[new Date().getDay()] === day
}

const getWeekLessons = (day, slot) => {
  const slotStart = slot.split('-')[0]?.trim()
  return schedules.value.filter(s => {
    if (s.day_of_week !== day) return false
    const tr = (s.time_range || '').replace(/\s/g, '').replace(/(\d{2}:\d{2}):\d{2}/g, '$1')
    const start = tr.split('-')[0]?.trim()
    return start === slotStart
  })
}

// Load data
async function loadGroups() {
  try {
    const resp = await api.request('/groups?page_size=500')
    groups.value = (resp.items || resp.data || resp || []).sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  } catch (e) {
    console.error('Load groups error:', e)
  }
}

async function loadSchedules() {
  loading.value = true
  currentPage.value = 1
  try {
    const params = { page_size: 500, is_active: true }
    if (filterGroupId.value) params.group_id = filterGroupId.value
    if (filterDay.value) params.day_of_week = filterDay.value
    const resp = await api.getSchedules(params)
    const items = resp.items || resp.data || resp || []
    schedules.value = items
    totalSchedules.value = resp.total || items.length

    // Reset subject colors
    subjectColorIndex.value = {}
    const subjects = [...new Set(items.map(s => s.subject).filter(Boolean))].sort()
    subjects.forEach(s => getSubjectBg(s))
  } catch (e) {
    console.error('Load schedules error:', e)
    toast.error(t('schedule.loadError'))
  } finally {
    loading.value = false
  }
}

// CRUD
function openCreateModal() {
  editingId.value = null
  form.value = defaultForm()
  if (filterGroupId.value) form.value.group_id = filterGroupId.value
  showModal.value = true
}

function editSchedule(s) {
  editingId.value = s.id
  form.value = {
    group_id: s.group_id,
    subject: s.subject || '',
    schedule_type: s.schedule_type || 'lecture',
    day_of_week: s.day_of_week || null,
    start_time: s.start_time ? String(s.start_time).substring(0, 5) : '08:30',
    end_time: s.end_time ? String(s.end_time).substring(0, 5) : '09:50',
    lesson_number: s.lesson_number || null,
    room: s.room || '',
    building: s.building || '',
    teacher_name: s.teacher_name || '',
    week_type: s.week_type || 'all',
  }
  showModal.value = true
}

function quickAdd(day, lessonNum, slot) {
  editingId.value = null
  const times = slot.split('-')
  form.value = {
    ...defaultForm(),
    group_id: filterGroupId.value,
    day_of_week: day,
    lesson_number: lessonNum,
    start_time: times[0]?.trim() || '08:30',
    end_time: times[1]?.trim() || '09:50',
  }
  showModal.value = true
}

function autoFillTime() {
  const slot = DEFAULT_TIMES[form.value.lesson_number]
  if (slot) {
    form.value.start_time = slot.start
    form.value.end_time = slot.end
  }
}

async function saveSchedule() {
  if (!form.value.group_id || !form.value.subject || !form.value.day_of_week || !form.value.start_time || !form.value.end_time) {
    toast.error(t('schedule.fillRequired'))
    return
  }
  saving.value = true
  try {
    const data = { ...form.value }
    if (editingId.value) {
      await api.updateSchedule(editingId.value, data)
      toast.success(t('schedule.lessonUpdated'))
    } else {
      await api.createSchedule(data)
      toast.success(t('schedule.lessonAdded'))
    }
    showModal.value = false
    await loadSchedules()
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || 'Xatolik yuz berdi')
  } finally {
    saving.value = false
  }
}

function confirmDelete(s) {
  deletingSchedule.value = s
  showDeleteModal.value = true
}

async function deleteSchedule() {
  if (!deletingSchedule.value) return
  saving.value = true
  try {
    await api.deleteSchedule(deletingSchedule.value.id)
    toast.success(t('schedule.lessonDeleted'))
    showDeleteModal.value = false
    deletingSchedule.value = null
    await loadSchedules()
  } catch (e) {
    toast.error(e.response?.data?.detail || e.message || 'Xatolik')
  } finally {
    saving.value = false
  }
}

// Init
onMounted(async () => {
  await loadGroups()
  await loadSchedules()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 8px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 8px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
