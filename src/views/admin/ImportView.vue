<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Ma'lumotlar Import</h1>
        <p class="text-slate-500 mt-1">Excel yoki CSV fayllardan ma'lumotlarni yuklash</p>
      </div>
    </div>

    <!-- Import Component -->
    <ExcelImport @completed="handleImportComplete" />

    <!-- Instructions -->
    <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
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
</template>

<script setup>
import { CheckCircle, AlertCircle, Info, Download } from 'lucide-vue-next'
import ExcelImport from '@/components/excel/ExcelImport.vue'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

function handleImportComplete(result) {
  toast.success(`Import muvaffaqiyatli: ${result.groups} guruh, ${result.students} talaba qo'shildi`)
}
</script>
