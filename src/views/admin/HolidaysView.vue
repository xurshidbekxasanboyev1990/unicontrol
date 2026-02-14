<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('holidays.title') }}</h1>
        <p class="text-sm text-slate-500 mt-1">{{ $t('holidays.subtitle') }}</p>
      </div>
      <button
        @click="openCreateModal"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all text-sm"
      >
        <Plus class="w-4 h-4" />
        {{ $t('holidays.addHoliday') }}
      </button>
    </div>

    <!-- Active holidays banner -->
    <div v-if="currentHoliday" class="bg-gradient-to-r from-amber-500 to-orange-500 rounded-2xl p-4 sm:p-6 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-10 translate-x-10"></div>
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur">
          <PartyPopper class="w-5 h-5" />
        </div>
        <div>
          <h3 class="font-bold text-lg">{{ currentHoliday.title }}</h3>
          <p class="text-white/80 text-sm">{{ $t('holidays.currentlyActive') }}</p>
        </div>
      </div>
      <p v-if="currentHoliday.description" class="text-white/90 text-sm mt-2">{{ currentHoliday.description }}</p>
      <div class="mt-3 flex items-center gap-4 text-sm text-white/80">
        <span class="flex items-center gap-1"><CalendarDays class="w-4 h-4" /> {{ formatDate(currentHoliday.start_date) }} — {{ formatDate(currentHoliday.end_date) }}</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- Holidays List -->
    <div v-else-if="holidays.length > 0" class="space-y-3">
      <div
        v-for="holiday in holidays"
        :key="holiday.id"
        class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5 hover:shadow-md transition-all"
      >
        <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
          <div :class="[
            'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
            getTypeBg(holiday.holiday_type)
          ]">
            <component :is="getTypeIcon(holiday.holiday_type)" :class="['w-6 h-6', getTypeColor(holiday.holiday_type)]" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="font-semibold text-slate-800 text-base">{{ holiday.title }}</h3>
              <span :class="[
                'px-2 py-0.5 text-xs font-medium rounded-full',
                holiday.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'
              ]">
                {{ holiday.is_active ? $t('common.active') : $t('holidays.inactive') }}
              </span>
              <span class="px-2 py-0.5 text-xs font-medium rounded-full bg-slate-100 text-slate-600">
                {{ getTypeLabel(holiday.holiday_type) }}
              </span>
            </div>
            <p v-if="holiday.description" class="text-sm text-slate-500 mt-1 line-clamp-1">{{ holiday.description }}</p>
            <div class="flex items-center gap-3 mt-2 text-sm text-slate-500">
              <span class="flex items-center gap-1">
                <CalendarDays class="w-3.5 h-3.5" />
                {{ formatDate(holiday.start_date) }} — {{ formatDate(holiday.end_date) }}
              </span>
              <span class="text-slate-300">•</span>
              <span>{{ getDayCount(holiday) }} {{ $t('holidays.days') }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="openEditModal(holiday)"
              class="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              :title="$t('common.edit')"
            >
              <Pencil class="w-4 h-4 text-slate-500" />
            </button>
            <button
              @click="confirmDelete(holiday)"
              class="p-2 hover:bg-rose-50 rounded-lg transition-colors"
              :title="$t('common.delete')"
            >
              <Trash2 class="w-4 h-4 text-rose-500" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-16">
      <CalendarX2 class="w-16 h-16 text-slate-300 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-slate-600">{{ $t('holidays.noHolidays') }}</h3>
      <p class="text-sm text-slate-400 mt-1">{{ $t('holidays.noHolidaysDesc') }}</p>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showModal = false">
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="showModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-lg font-bold text-slate-800">
                {{ editingHoliday ? $t('holidays.editHoliday') : $t('holidays.addHoliday') }}
              </h2>
              <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg">
                <X class="w-5 h-5 text-slate-500" />
              </button>
            </div>

            <div class="space-y-4">
              <!-- Title -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('holidays.name') }} *</label>
                <input
                  v-model="form.title"
                  class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
                  :placeholder="$t('holidays.namePlaceholder')"
                />
              </div>

              <!-- Description -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('holidays.description') }}</label>
                <textarea
                  v-model="form.description"
                  rows="3"
                  class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors resize-none"
                  :placeholder="$t('holidays.descriptionPlaceholder')"
                ></textarea>
              </div>

              <!-- Type -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('holidays.type') }}</label>
                <select
                  v-model="form.holiday_type"
                  class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
                >
                  <option value="holiday">{{ $t('holidays.typeHoliday') }}</option>
                  <option value="off_day">{{ $t('holidays.typeOffDay') }}</option>
                  <option value="exam_period">{{ $t('holidays.typeExam') }}</option>
                  <option value="other">{{ $t('holidays.typeOther') }}</option>
                </select>
              </div>

              <!-- Dates -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('holidays.startDate') }} *</label>
                  <input
                    v-model="form.start_date"
                    type="date"
                    class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('holidays.endDate') }} *</label>
                  <input
                    v-model="form.end_date"
                    type="date"
                    class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
                  />
                </div>
              </div>

              <!-- Active toggle (edit mode only) -->
              <div v-if="editingHoliday" class="flex items-center justify-between bg-slate-50 rounded-xl p-3">
                <span class="text-sm font-medium text-slate-700">{{ $t('holidays.isActive') }}</span>
                <button
                  @click="form.is_active = !form.is_active"
                  :class="[
                    'relative w-12 h-6 rounded-full transition-colors',
                    form.is_active ? 'bg-emerald-500' : 'bg-slate-300'
                  ]"
                >
                  <span :class="[
                    'absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                    form.is_active ? 'translate-x-6' : 'translate-x-0.5'
                  ]"></span>
                </button>
              </div>
            </div>

            <div class="flex gap-3 mt-6">
              <button
                @click="showModal = false"
                class="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                @click="saveHoliday"
                :disabled="saving || !form.title || !form.start_date || !form.end_date"
                class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-xl font-semibold hover:bg-emerald-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
                {{ editingHoliday ? $t('common.save') : $t('common.create') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showDeleteModal = false">
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="showDeleteModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
          <button @click="showDeleteModal = false" class="absolute top-3 right-3 p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors z-10"><X class="w-5 h-5" /></button>
          <div class="text-center">
            <div class="w-16 h-16 bg-rose-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Trash2 class="w-8 h-8 text-rose-500" />
            </div>
            <h3 class="text-lg font-bold text-slate-800 mb-2">{{ $t('holidays.deleteConfirm') }}</h3>
            <p class="text-sm text-slate-500">
              "{{ deletingHoliday?.title }}" — {{ formatDate(deletingHoliday?.start_date) }} — {{ formatDate(deletingHoliday?.end_date) }}
            </p>
          </div>
          <div class="flex gap-3 mt-6">
            <button
              @click="showDeleteModal = false"
              class="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              @click="doDelete"
              :disabled="saving"
              class="flex-1 px-4 py-2.5 bg-rose-500 text-white rounded-xl font-semibold hover:bg-rose-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import api from '@/services/api'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    CalendarDays,
    CalendarX2,
    GraduationCap,
    Loader2,
    PartyPopper,
    Pencil,
    Plus,
    Sun,
    Trash2,
    X
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'

const toast = useToastStore()
const { t } = useLanguageStore()

const loading = ref(true)
const saving = ref(false)
const holidays = ref([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingHoliday = ref(null)
const deletingHoliday = ref(null)

const form = ref({
  title: '',
  description: '',
  holiday_type: 'holiday',
  start_date: '',
  end_date: '',
  is_active: true
})

const currentHoliday = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return holidays.value.find(h => h.is_active && h.start_date <= today && h.end_date >= today)
})

const formatDate = (d) => {
  if (!d) return '-'
  return new Date(d + 'T00:00:00').toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

const getDayCount = (h) => {
  if (!h.start_date || !h.end_date) return 0
  const start = new Date(h.start_date)
  const end = new Date(h.end_date)
  return Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1
}

const getTypeBg = (type) => ({
  holiday: 'bg-amber-100',
  off_day: 'bg-blue-100',
  exam_period: 'bg-violet-100',
  other: 'bg-slate-100'
}[type] || 'bg-slate-100')

const getTypeColor = (type) => ({
  holiday: 'text-amber-600',
  off_day: 'text-blue-600',
  exam_period: 'text-violet-600',
  other: 'text-slate-600'
}[type] || 'text-slate-600')

const getTypeIcon = (type) => ({
  holiday: markRaw(PartyPopper),
  off_day: markRaw(Sun),
  exam_period: markRaw(GraduationCap),
  other: markRaw(CalendarDays)
}[type] || markRaw(CalendarDays))

const getTypeLabel = (type) => ({
  holiday: t('holidays.typeHoliday'),
  off_day: t('holidays.typeOffDay'),
  exam_period: t('holidays.typeExam'),
  other: t('holidays.typeOther')
}[type] || type)

const openCreateModal = () => {
  editingHoliday.value = null
  form.value = { title: '', description: '', holiday_type: 'holiday', start_date: '', end_date: '', is_active: true }
  showModal.value = true
}

const openEditModal = (holiday) => {
  editingHoliday.value = holiday
  form.value = {
    title: holiday.title,
    description: holiday.description || '',
    holiday_type: holiday.holiday_type,
    start_date: holiday.start_date,
    end_date: holiday.end_date,
    is_active: holiday.is_active
  }
  showModal.value = true
}

const confirmDelete = (holiday) => {
  deletingHoliday.value = holiday
  showDeleteModal.value = true
}

const loadHolidays = async () => {
  try {
    holidays.value = await api.getHolidays({ active_only: false }) || []
  } catch (e) {
    console.error('Load holidays error:', e)
  } finally {
    loading.value = false
  }
}

const saveHoliday = async () => {
  if (!form.value.title || !form.value.start_date || !form.value.end_date) return
  saving.value = true
  try {
    if (editingHoliday.value) {
      await api.updateHoliday(editingHoliday.value.id, form.value)
      toast.success(t('holidays.updated'))
    } else {
      await api.createHoliday(form.value)
      toast.success(t('holidays.created'))
    }
    showModal.value = false
    await loadHolidays()
  } catch (e) {
    toast.error(e.message || t('holidays.saveError'))
  } finally {
    saving.value = false
  }
}

const doDelete = async () => {
  if (!deletingHoliday.value) return
  saving.value = true
  try {
    await api.deleteHoliday(deletingHoliday.value.id)
    toast.success(t('holidays.deleted'))
    showDeleteModal.value = false
    await loadHolidays()
  } catch (e) {
    toast.error(e.message || t('holidays.deleteError'))
  } finally {
    saving.value = false
  }
}

onMounted(loadHolidays)
</script>
