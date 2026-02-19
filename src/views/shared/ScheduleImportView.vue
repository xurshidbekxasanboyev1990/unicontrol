<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-orange-600 to-amber-600 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <CalendarDays :size="28" />
        <h1 class="text-xl font-bold">{{ t('importData.scheduleImport') || 'Jadval import' }}</h1>
      </div>
      <p class="text-orange-100 text-sm">Dars jadvalini Excel fayldan yuklash (AI yordamida)</p>
    </div>

    <!-- Schedule Import Component -->
    <ScheduleImport />

    <!-- Instructions for schedule -->
    <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
      <h2 class="text-lg font-semibold text-slate-800 mb-4">{{ t('importData.scheduleRules') || 'Jadval import qoidalari' }}</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <h3 class="text-sm font-medium text-slate-700">{{ t('importData.excelFormat') || 'Excel format' }}</h3>
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
          <h3 class="text-sm font-medium text-slate-700">{{ t('importData.cellFormat') || 'Hujayra formati' }}</h3>
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
</template>

<script setup>
import ScheduleImport from '@/components/excel/ScheduleImport.vue';
import { useLanguageStore } from '@/stores/language';
import { AlertCircle, CalendarDays, CheckCircle, Info } from 'lucide-vue-next';

const { t } = useLanguageStore()
</script>
