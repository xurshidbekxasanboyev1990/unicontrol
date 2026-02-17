<template>
  <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2"><CalendarDays class="w-5 h-5 text-indigo-500" /> Dars jadvali import</h2>
        <p class="text-sm text-slate-500">Excel fayldan dars jadvalini yuklash (AI yordamida)</p>
      </div>
    </div>

    <!-- File Upload -->
    <div v-if="!result && !isUploading" class="space-y-6">
      <div
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="[
          'border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 cursor-pointer',
          isDragging
            ? 'border-blue-400 bg-blue-50'
            : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
        ]"
        @click="$refs.fileInput.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          class="hidden"
          @change="handleFileSelect"
        />
        <div class="flex flex-col items-center gap-3">
          <div :class="[
            'w-16 h-16 rounded-2xl flex items-center justify-center transition-colors',
            isDragging ? 'bg-blue-100' : 'bg-slate-100'
          ]">
            <CalendarDays :class="['w-8 h-8', isDragging ? 'text-blue-500' : 'text-slate-400']" />
          </div>
          <div>
            <p class="text-base font-medium text-slate-700">
              Jadval Excel faylni tashlang yoki tanlang
            </p>
            <p class="text-xs text-slate-400 mt-1">
              Format: Sheet = yo'nalish, Row 2 = guruh nomlari, ma'lumotlar Row 3+ dan
            </p>
          </div>
        </div>
      </div>

      <!-- Selected file info -->
      <div v-if="selectedFile" class="bg-blue-50 rounded-xl p-4">
        <div class="flex items-center gap-3">
          <FileSpreadsheet class="w-5 h-5 text-blue-600" />
          <div class="flex-1">
            <p class="text-sm font-medium text-blue-800">{{ selectedFile.name }}</p>
            <p class="text-xs text-blue-600">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <button @click="selectedFile = null" class="p-1 text-blue-400 hover:text-blue-600">
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Settings -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">O'quv yili</label>
          <select v-model="academicYear" class="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400">
            <option value="2024-2025">2024-2025</option>
            <option value="2025-2026">2025-2026</option>
            <option value="2026-2027">2026-2027</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1.5">Semestr</label>
          <select v-model.number="semester" class="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400">
            <option :value="1">1-semestr</option>
            <option :value="2">2-semestr</option>
          </select>
        </div>
        <div class="flex items-end">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="useAi" class="w-4 h-4 rounded border-slate-300 text-violet-500 focus:ring-violet-500/20" />
            <span class="text-sm text-slate-600 flex items-center gap-1">
              <BrainCircuit class="w-4 h-4 text-violet-500" />
              AI yordamida moslashtirish
            </span>
          </label>
        </div>
      </div>

      <!-- Upload button -->
      <div class="flex justify-end">
        <button
          :disabled="!selectedFile"
          @click="uploadSchedule"
          :class="[
            'flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all',
            selectedFile
              ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg shadow-blue-500/20'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          ]"
        >
          <Upload class="w-4 h-4" />
          Jadvalni yuklash
        </button>
      </div>
    </div>

    <!-- Uploading -->
    <div v-if="isUploading" class="text-center py-10">
      <div class="w-16 h-16 mx-auto mb-4 relative">
        <div class="w-full h-full rounded-full border-4 border-slate-200 border-t-blue-500 animate-spin"></div>
        <BrainCircuit v-if="useAi" class="w-6 h-6 text-violet-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
      </div>
      <p class="text-lg font-medium text-slate-700">Jadval yuklanmoqda...</p>
      <p class="text-sm text-slate-400 mt-1">
        {{ useAi ? 'AI tahlil qilmoqda: guruhlarni moslashtirish va ma\'lumotlarni tekshirish' : 'Excel faylni tahlil qilish va guruhlarni moslashtirish' }}
      </p>
    </div>

    <!-- Result -->
    <div v-if="result && !isUploading" class="space-y-6">
      <!-- Success header -->
      <div class="text-center py-4">
        <div class="w-16 h-16 mx-auto mb-4 bg-emerald-100 rounded-full flex items-center justify-center">
          <CheckCircle class="w-8 h-8 text-emerald-500" />
        </div>
        <p class="text-lg font-semibold text-slate-800">{{ result.message }}</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div class="text-center p-4 bg-emerald-50 rounded-xl">
          <p class="text-2xl font-bold text-emerald-600">{{ result.synced }}</p>
          <p class="text-xs text-emerald-600">Jami darslar</p>
        </div>
        <div class="text-center p-4 bg-cyan-50 rounded-xl">
          <p class="text-2xl font-bold text-cyan-600">{{ result.updated || 0 }}</p>
          <p class="text-xs text-cyan-600">Yangilangan</p>
        </div>
        <div class="text-center p-4 bg-indigo-50 rounded-xl">
          <p class="text-2xl font-bold text-indigo-600">{{ result.inserted || 0 }}</p>
          <p class="text-xs text-indigo-600">Qo'shilgan</p>
        </div>
        <div class="text-center p-4 bg-blue-50 rounded-xl">
          <p class="text-2xl font-bold text-blue-600">{{ result.matched_groups?.length || 0 }}</p>
          <p class="text-xs text-blue-600">Topilgan guruhlar</p>
        </div>
        <div class="text-center p-4 bg-red-50 rounded-xl">
          <p class="text-2xl font-bold text-red-600">{{ result.unmatched_groups?.length || 0 }}</p>
          <p class="text-xs text-red-600">Topilmagan guruhlar</p>
        </div>
      </div>

      <!-- AI Results Section -->
      <div v-if="result.ai?.enabled" class="bg-gradient-to-r from-violet-50 to-indigo-50 rounded-xl p-5 border border-violet-200/50">
        <h4 class="text-sm font-semibold text-violet-800 mb-3 flex items-center gap-2">
          <BrainCircuit class="w-4 h-4" /> AI Agent natijalari
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
          <div class="bg-white/60 rounded-lg p-3 text-center">
            <p class="text-lg font-bold text-violet-600">{{ result.ai.matched_groups_count || 0 }}</p>
            <p class="text-xs text-violet-500">AI moslashgan guruhlar</p>
          </div>
          <div class="bg-white/60 rounded-lg p-3 text-center">
            <p class="text-lg font-bold text-violet-600">{{ result.ai.parsed_cells_count || 0 }}</p>
            <p class="text-xs text-violet-500">AI tahlil qilgan kataklar</p>
          </div>
          <div class="bg-white/60 rounded-lg p-3 text-center">
            <p class="text-lg font-bold text-violet-600">{{ result.ai.tokens_used || 0 }}</p>
            <p class="text-xs text-violet-500">AI tokenlar sarflandi</p>
          </div>
        </div>

        <!-- AI Matched Groups -->
        <div v-if="result.ai.matched_groups && Object.keys(result.ai.matched_groups).length" class="mb-3">
          <p class="text-xs font-medium text-violet-700 mb-2">AI moslashtirilgan guruhlar:</p>
          <div class="space-y-1">
            <div v-for="(dbName, excelName) in result.ai.matched_groups" :key="excelName"
              class="flex items-center gap-2 text-xs text-violet-700">
              <span class="px-2 py-0.5 bg-white rounded">{{ excelName }}</span>
              <Sparkles class="w-3 h-3 text-violet-400" />
              <ArrowRight class="w-3 h-3" />
              <span class="px-2 py-0.5 bg-white rounded font-medium">{{ dbName }}</span>
            </div>
          </div>
        </div>

        <!-- AI Quality Analysis -->
        <div v-if="result.ai.analysis" class="mt-3">
          <div v-if="result.ai.analysis.quality_score" class="flex items-center gap-2 mb-2">
            <span class="text-xs font-medium text-violet-700">Sifat bahosi:</span>
            <div class="flex items-center gap-1">
              <div class="w-24 h-2 bg-violet-200 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all"
                  :class="result.ai.analysis.quality_score >= 7 ? 'bg-emerald-500' : result.ai.analysis.quality_score >= 4 ? 'bg-amber-500' : 'bg-red-500'"
                  :style="{ width: (result.ai.analysis.quality_score * 10) + '%' }">
                </div>
              </div>
              <span class="text-xs font-bold text-violet-600">{{ result.ai.analysis.quality_score }}/10</span>
            </div>
          </div>

          <p v-if="result.ai.analysis.summary" class="text-xs text-violet-600 mb-2">
            {{ result.ai.analysis.summary }}
          </p>

          <div v-if="result.ai.analysis.suggestions?.length" class="space-y-1">
            <p class="text-xs font-medium text-violet-700">Takliflar:</p>
            <p v-for="(s, i) in result.ai.analysis.suggestions" :key="i" class="text-xs text-violet-600 flex items-start gap-1">
              <Sparkles class="w-3 h-3 mt-0.5 flex-shrink-0" /> {{ s }}
            </p>
          </div>

          <div v-if="result.ai.analysis.anomalies?.length" class="mt-2 space-y-1">
            <p class="text-xs font-medium text-amber-700">Ogohlantirishlar:</p>
            <p v-for="(a, i) in result.ai.analysis.anomalies" :key="i" class="text-xs text-amber-600 flex items-start gap-1">
              <AlertTriangle class="w-3 h-3 mt-0.5 flex-shrink-0" /> {{ a }}
            </p>
          </div>
        </div>
      </div>

      <!-- Matched groups -->
      <div v-if="result.matched_groups?.length" class="bg-emerald-50 rounded-xl p-4">
        <h4 class="text-sm font-medium text-emerald-800 mb-2 flex items-center gap-2">
          <CheckCircle class="w-4 h-4" /> Topilgan guruhlar ({{ result.matched_groups.length }})
        </h4>
        <div class="flex flex-wrap gap-2">
          <span v-for="g in result.matched_groups" :key="g"
            class="px-2 py-1 bg-white text-xs text-emerald-700 rounded-lg">
            {{ g }}
          </span>
        </div>
      </div>

      <!-- Unmatched groups -->
      <div v-if="result.unmatched_groups?.length" class="bg-red-50 rounded-xl p-4">
        <h4 class="text-sm font-medium text-red-800 mb-2 flex items-center gap-2">
          <AlertCircle class="w-4 h-4" /> Topilmagan guruhlar ({{ result.unmatched_groups.length }})
        </h4>
        <p class="text-xs text-red-600 mb-2">Bu guruhlar bazada mavjud emas. Avval guruhlarni yarating.</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="g in result.unmatched_groups" :key="g"
            class="px-2 py-1 bg-white text-xs text-red-700 rounded-lg">
            {{ g }}
          </span>
        </div>
      </div>

      <!-- Group name mapping -->
      <div v-if="result.group_name_map && Object.keys(result.group_name_map).length" class="bg-blue-50 rounded-xl p-4">
        <h4 class="text-sm font-medium text-blue-800 mb-2 flex items-center gap-2">
          <ArrowRight class="w-4 h-4" /> Guruh nomlari moslashtirildi
        </h4>
        <div class="space-y-1">
          <div v-for="(dbName, sheetName) in result.group_name_map" :key="sheetName"
            class="flex items-center gap-2 text-xs text-blue-700">
            <span class="px-2 py-0.5 bg-white rounded">{{ sheetName }}</span>
            <ArrowRight class="w-3 h-3" />
            <span class="px-2 py-0.5 bg-white rounded font-medium">{{ dbName }}</span>
          </div>
        </div>
      </div>

      <!-- Errors -->
      <div v-if="result.errors?.length" class="bg-orange-50 rounded-xl p-4">
        <h4 class="text-sm font-medium text-orange-800 mb-2 flex items-center gap-2">
          <AlertCircle class="w-4 h-4" /> Xatoliklar ({{ result.errors.length }})
        </h4>
        <div class="space-y-1 max-h-40 overflow-y-auto">
          <p v-for="(err, i) in result.errors" :key="i" class="text-xs text-orange-700">
            {{ err }}
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-center gap-4 pt-4 border-t border-slate-100">
        <button @click="resetForm" class="flex items-center gap-2 px-6 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors">
          <RefreshCw class="w-4 h-4" />
          Yana yuklash
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="mt-4 bg-red-50 rounded-xl p-4 flex items-start gap-3">
      <AlertCircle class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
      <div>
        <p class="text-sm font-medium text-red-800">Xatolik yuz berdi</p>
        <p class="text-xs text-red-600 mt-0.5">{{ error }}</p>
      </div>
      <button @click="error = null" class="ml-auto p-1 text-red-400 hover:text-red-600">
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import api from '@/services/api'
import {
  AlertCircle, AlertTriangle, ArrowRight, BrainCircuit,
  CalendarDays,
  CheckCircle,
  FileSpreadsheet,
  RefreshCw, Sparkles,
  Upload, X
} from 'lucide-vue-next'
import { ref } from 'vue'

const isDragging = ref(false)
const selectedFile = ref(null)
const isUploading = ref(false)
const result = ref(null)
const error = ref(null)

const academicYear = ref('2025-2026')
const semester = ref(2)
const useAi = ref(true)

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    error.value = null
    result.value = null
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    selectedFile.value = file
    error.value = null
    result.value = null
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

async function uploadSchedule() {
  if (!selectedFile.value) return

  isUploading.value = true
  error.value = null
  result.value = null

  try {
    const response = await api.importSchedulesFromExcel(
      selectedFile.value,
      academicYear.value,
      semester.value,
      useAi.value
    )
    result.value = response
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Xatolik yuz berdi'
  } finally {
    isUploading.value = false
  }
}

function resetForm() {
  selectedFile.value = null
  result.value = null
  error.value = null
}
</script>
