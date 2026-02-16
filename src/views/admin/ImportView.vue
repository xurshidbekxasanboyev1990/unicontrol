<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('importData.title') }}</h1>
        <p class="text-sm text-slate-500 mt-1">Excel fayllardan ma'lumotlarni yuklash</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 p-1 bg-slate-100 rounded-2xl w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all',
          activeTab === tab.key
            ? 'bg-white text-slate-800 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'
        ]"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab: Kontingent -->
    <div v-if="activeTab === 'kontingent'">
      <ExcelImport @completed="handleImportComplete" />

      <!-- Instructions -->
      <div class="mt-6 bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Import qoidalari</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <h3 class="text-sm font-medium text-slate-700">Qo'llab-quvvatlanadigan formatlar:</h3>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-emerald-500" />
                Excel (.xlsx, .xls)
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-emerald-500" />
                CSV (.csv)
              </li>
            </ul>
          </div>

          <div class="space-y-4">
            <h3 class="text-sm font-medium text-slate-700">Majburiy ustunlar:</h3>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-center gap-2">
                <AlertCircle class="w-4 h-4 text-orange-500" />
                F.I.O (To'liq ism)
              </li>
              <li class="flex items-center gap-2">
                <AlertCircle class="w-4 h-4 text-orange-500" />
                Guruh nomi
              </li>
            </ul>
          </div>
        </div>

        <div class="mt-6 p-4 bg-blue-50 rounded-xl">
          <div class="flex items-start gap-3">
            <Info class="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <p class="text-sm font-medium text-blue-800">Namuna fayl</p>
              <p class="text-xs text-blue-600 mt-1">
                Import uchun namuna faylni yuklab olishingiz mumkin. 
                Bu sizga to'g'ri formatda ma'lumot tayyorlashda yordam beradi.
              </p>
              <button class="mt-3 flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors">
                <Download class="w-4 h-4" />
                Namuna faylni yuklash
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Schedule -->
    <div v-if="activeTab === 'schedule'">
      <ScheduleImport />

      <!-- Instructions for schedule -->
      <div class="mt-6 bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Jadval import qoidalari</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <h3 class="text-sm font-medium text-slate-700">Excel format:</h3>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-start gap-2">
                <CheckCircle class="w-4 h-4 text-emerald-500 mt-0.5" />
                <span>Har bir sheet = bitta yo'nalish</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle class="w-4 h-4 text-emerald-500 mt-0.5" />
                <span>2-qator = guruh nomlari (D2, E2, F2...)</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle class="w-4 h-4 text-emerald-500 mt-0.5" />
                <span>A ustun = hafta kuni, B = para №, C = vaqt</span>
              </li>
            </ul>
          </div>

          <div class="space-y-4">
            <h3 class="text-sm font-medium text-slate-700">Cell formati:</h3>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-start gap-2">
                <Info class="w-4 h-4 text-blue-500 mt-0.5" />
                <span>Fan nomi (turi) O'qituvchi Xona</span>
              </li>
              <li class="flex items-start gap-2">
                <Info class="w-4 h-4 text-blue-500 mt-0.5" />
                <span>Masalan: <em class="text-slate-500">Falsafa (ma'ruza) Ustoz 307-xona A bino</em></span>
              </li>
            </ul>
          </div>
        </div>

        <div class="mt-4 p-3 bg-amber-50 rounded-xl flex items-start gap-3">
          <AlertCircle class="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
          <p class="text-xs text-amber-700">
            <strong>Muhim:</strong> Guruh nomlari bazadagi nomlar bilan mos kelishi kerak. 
            Fuzzy matching yoqilgan — kichik farqlar (-, _, bo'sh joy) avtomatik to'g'rilanadi.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ExcelImport from '@/components/excel/ExcelImport.vue'
import ScheduleImport from '@/components/excel/ScheduleImport.vue'
import { useToastStore } from '@/stores/toast'
import { AlertCircle, CalendarDays, CheckCircle, Download, Info, Users } from 'lucide-vue-next'
import { ref } from 'vue'

const toast = useToastStore()
const activeTab = ref('kontingent')

const tabs = [
  { key: 'kontingent', label: 'Kontingent', icon: Users },
  { key: 'schedule', label: 'Dars jadvali', icon: CalendarDays },
]

function handleImportComplete(result) {
  toast.success(`Import muvaffaqiyatli: ${result.groups} guruh, ${result.students} talaba qo'shildi`)
}
</script>
