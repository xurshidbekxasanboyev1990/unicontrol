<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <FileUp :size="28" />
        <h1 class="text-xl font-bold">{{ t('workloadImport.title') || "O'qituvchi bandligi import" }}</h1>
      </div>
      <p class="text-purple-100 text-sm">{{ t('workloadImport.description') || "Excel fayldan o'qituvchilar bandligini yuklash" }}</p>
    </div>

    <!-- Stats Card -->
    <div v-if="stats" class="grid grid-cols-3 gap-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 text-center">
        <p class="text-2xl font-bold text-indigo-600">{{ stats.total_entries }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ t('workloadImport.totalEntries') || 'Jami yozuvlar' }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 text-center">
        <p class="text-2xl font-bold text-emerald-600">{{ stats.total_teachers }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ t('workloadImport.totalTeachers') || "O'qituvchilar" }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 text-center">
        <p class="text-2xl font-bold text-amber-600">{{ stats.total_departments }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ t('workloadImport.totalDepartments') || 'Kafedralar' }}</p>
      </div>
    </div>

    <!-- Upload Area -->
    <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
      <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
        <Upload :size="16" />
        {{ t('workloadImport.uploadExcel') || 'Excel fayl yuklash' }}
      </h3>

      <!-- Dropzone -->
      <div
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
        :class="['border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer', isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50']"
        @click="$refs.fileInput.click()"
      >
        <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileSelect" />
        <FileSpreadsheet :size="48" :class="['mx-auto mb-3', isDragging ? 'text-indigo-500' : 'text-gray-300']" />
        <p v-if="!selectedFile" class="text-sm text-gray-500">
          {{ t('workloadImport.dropHere') || "Faylni bu yerga tashlang yoki bosib tanlang" }}
        </p>
        <div v-else class="space-y-2">
          <div class="flex items-center justify-center gap-2">
            <FileSpreadsheet :size="18" class="text-emerald-600" />
            <span class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</span>
            <button @click.stop="selectedFile = null" class="text-gray-400 hover:text-red-500">
              <X :size="14" />
            </button>
          </div>
          <p class="text-xs text-gray-400">{{ formatSize(selectedFile.size) }}</p>
        </div>
      </div>

      <!-- Options -->
      <div class="mt-4 flex items-center gap-4">
        <label class="flex items-center gap-2 text-sm text-gray-600">
          <input type="checkbox" v-model="clearExisting" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
          {{ t('workloadImport.clearExisting') || "Eski ma'lumotlarni o'chirish" }}
        </label>
      </div>

      <!-- Upload Button -->
      <button
        @click="uploadFile"
        :disabled="!selectedFile || uploading"
        :class="['mt-4 w-full rounded-xl py-3 text-sm font-medium text-white flex items-center justify-center gap-2 transition-all', !selectedFile || uploading ? 'bg-gray-300 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700']"
      >
        <Loader2 v-if="uploading" :size="16" class="animate-spin" />
        <Upload v-else :size="16" />
        {{ uploading ? (t('common.uploading') || 'Yuklanmoqda...') : (t('workloadImport.upload') || 'Yuklash') }}
      </button>

      <!-- Result -->
      <div v-if="uploadResult" :class="['mt-4 rounded-xl p-4 text-sm', uploadResult.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200']">
        <div class="flex items-start gap-2">
          <CheckCircle v-if="uploadResult.success" :size="18" class="text-emerald-600 mt-0.5 flex-shrink-0" />
          <AlertCircle v-else :size="18" class="text-red-600 mt-0.5 flex-shrink-0" />
          <div>
            <p :class="uploadResult.success ? 'text-emerald-700 font-medium' : 'text-red-700 font-medium'">{{ uploadResult.message }}</p>
            <div v-if="uploadResult.success" class="mt-2 space-y-1 text-xs text-emerald-600">
              <p>📊 {{ uploadResult.total_imported }} ta yozuv import qilindi</p>
              <p>👨‍🏫 {{ uploadResult.total_teachers }} ta o'qituvchi</p>
              <p>🏫 {{ uploadResult.total_departments }} ta kafedra</p>
              <p>📄 {{ uploadResult.source_file }} ({{ uploadResult.sheet_name }})</p>
            </div>
            <div v-if="uploadResult.available_sheets" class="mt-2 text-xs text-red-600">
              <p>Mavjud varaqlar: {{ uploadResult.available_sheets.join(', ') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { AlertCircle, CheckCircle, FileSpreadsheet, FileUp, Loader2, Upload, X } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const isDragging = ref(false)
const selectedFile = ref(null)
const clearExisting = ref(true)
const uploading = ref(false)
const uploadResult = ref(null)
const stats = ref(null)
const toast = ref(null)

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

const onFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    uploadResult.value = null
  }
}

const onDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    selectedFile.value = file
    uploadResult.value = null
  } else {
    showToast('Faqat Excel fayl yuklang', 'error')
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  uploadResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('clear_existing', clearExisting.value)

    const res = await api.request('/academic/workload/upload-excel', { method: 'POST', body: formData })
    uploadResult.value = res
    if (res.success) {
      showToast(res.message)
      loadStats()
    }
  } catch (e) {
    console.error('Upload error:', e)
    uploadResult.value = { success: false, message: e.response?.data?.detail || "Yuklashda xatolik" }
  } finally {
    uploading.value = false
  }
}

const loadStats = async () => {
  try {
    stats.value = await api.request('/academic/workload/stats')
  } catch (e) {
    // silently fail
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
