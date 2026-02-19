<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-600 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <Users :size="28" />
        <h1 class="text-xl font-bold">{{ t('importData.contingent') || 'Kontingent import' }}</h1>
      </div>
      <p class="text-blue-100 text-sm">Talabalar va guruhlarni Excel yoki CSV fayldan yuklash</p>
    </div>

    <!-- Excel Import Component -->
    <ExcelImport @completed="handleImportComplete" />

    <!-- Instructions -->
    <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
      <h2 class="text-lg font-semibold text-slate-800 mb-4">{{ t('importData.importRules') || 'Import qoidalari' }}</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <h3 class="text-sm font-medium text-slate-700">{{ t('importData.supportedFormats') || "Qo'llab-quvvatlanadigan formatlar" }}</h3>
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
          <h3 class="text-sm font-medium text-slate-700">{{ t('importData.requiredColumns') || "Kerakli ustunlar" }}</h3>
          <ul class="space-y-2 text-sm text-slate-600">
            <li class="flex items-center gap-2">
              <AlertCircle class="w-4 h-4 text-orange-500" />
              {{ t('importData.fullName') || "To'liq ism" }}
            </li>
            <li class="flex items-center gap-2">
              <AlertCircle class="w-4 h-4 text-orange-500" />
              {{ t('importData.groupName') || 'Guruh nomi' }}
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-6 p-4 bg-blue-50 rounded-xl">
        <div class="flex items-start gap-3">
          <Info class="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p class="text-sm font-medium text-blue-800">{{ t('importData.sampleFile') || 'Namuna fayl' }}</p>
            <p class="text-xs text-blue-600 mt-1">
              {{ t('importData.sampleFileDesc') || "Namuna faylni yuklab oling va unga mos fayl tayyorlang" }}
            </p>
            <button class="mt-3 flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors">
              <Download class="w-4 h-4" />
              {{ t('importData.downloadSample') || 'Namunani yuklab olish' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ExcelImport from '@/components/excel/ExcelImport.vue'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import { AlertCircle, CheckCircle, Download, Info, Users } from 'lucide-vue-next'

const toast = useToastStore()
const { t } = useLanguageStore()

function handleImportComplete(result) {
  toast.success(t('importData.importSuccess', { groups: result.groups, students: result.students }) || `Import muvaffaqiyatli: ${result.groups} guruh, ${result.students} talaba`)
}
</script>
