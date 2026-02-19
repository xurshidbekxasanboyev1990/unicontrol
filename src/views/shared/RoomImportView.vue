<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-teal-600 to-emerald-600 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <DoorOpen :size="28" />
        <h1 class="text-xl font-bold">Xona bandligi import</h1>
      </div>
      <p class="text-teal-100 text-sm">Xonalar bandlik jadvalini Excel fayldan yuklash</p>
    </div>

    <!-- Stats Card -->
    <div v-if="stats" class="grid grid-cols-3 gap-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 text-center">
        <p class="text-2xl font-bold text-teal-600">{{ stats.total_rooms || 0 }}</p>
        <p class="text-xs text-gray-500 mt-1">Jami xonalar</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 text-center">
        <p class="text-2xl font-bold text-emerald-600">{{ stats.available_rooms || 0 }}</p>
        <p class="text-xs text-gray-500 mt-1">Bo'sh xonalar</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 text-center">
        <p class="text-2xl font-bold text-amber-600">{{ stats.occupied_rooms || 0 }}</p>
        <p class="text-xs text-gray-500 mt-1">Band xonalar</p>
      </div>
    </div>

    <!-- Upload Area -->
    <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
      <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
        <Upload :size="16" />
        Excel fayl yuklash
      </h3>

      <!-- Dropzone -->
      <div
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
        :class="['border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer', isDragging ? 'border-teal-500 bg-teal-50' : 'border-gray-200 hover:border-teal-300 hover:bg-gray-50']"
        @click="$refs.fileInput.click()"
      >
        <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileSelect" />
        <FileSpreadsheet :size="48" :class="['mx-auto mb-3', isDragging ? 'text-teal-500' : 'text-gray-300']" />
        <p v-if="!selectedFile" class="text-sm text-gray-500">
          Faylni bu yerga tashlang yoki bosib tanlang
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
          <input type="checkbox" v-model="clearExisting" class="rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
          Eski xona bandlik ma'lumotlarini o'chirish
        </label>
      </div>

      <!-- Upload Button -->
      <button
        @click="uploadFile"
        :disabled="!selectedFile || uploading"
        :class="['mt-4 w-full rounded-xl py-3 text-sm font-medium text-white flex items-center justify-center gap-2 transition-all', !selectedFile || uploading ? 'bg-gray-300 cursor-not-allowed' : 'bg-teal-600 hover:bg-teal-700']"
      >
        <Loader2 v-if="uploading" :size="16" class="animate-spin" />
        <Upload v-else :size="16" />
        {{ uploading ? 'Yuklanmoqda...' : 'Yuklash' }}
      </button>

      <!-- Result -->
      <div v-if="uploadResult" :class="['mt-4 rounded-xl p-4 text-sm', uploadResult.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200']">
        <div class="flex items-start gap-2">
          <CheckCircle v-if="uploadResult.success" :size="18" class="text-emerald-600 mt-0.5 flex-shrink-0" />
          <AlertCircle v-else :size="18" class="text-red-600 mt-0.5 flex-shrink-0" />
          <div>
            <p :class="uploadResult.success ? 'text-emerald-700 font-medium' : 'text-red-700 font-medium'">{{ uploadResult.message }}</p>
            <div v-if="uploadResult.success" class="mt-2 space-y-1 text-xs text-emerald-600">
              <p>🏫 {{ uploadResult.total_rooms || 0 }} ta xona import qilindi</p>
              <p>📅 {{ uploadResult.total_slots || 0 }} ta vaqt oralig'i</p>
              <p>📄 {{ uploadResult.source_file || selectedFile?.name }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Format Info -->
    <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
      <h2 class="text-lg font-semibold text-slate-800 mb-4">Excel format qoidalari</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <h3 class="text-sm font-medium text-slate-700">Fayl tuzilishi</h3>
          <ul class="space-y-2 text-sm text-slate-600">
            <li class="flex items-start gap-2">
              <CheckCircle class="w-4 h-4 text-emerald-500 mt-0.5" />
              <span>1-qator = ustun nomlari (xona, kun, vaqt, holat)</span>
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle class="w-4 h-4 text-emerald-500 mt-0.5" />
              <span>Har bir qator = bitta xona-vaqt bandligi</span>
            </li>
            <li class="flex items-start gap-2">
              <CheckCircle class="w-4 h-4 text-emerald-500 mt-0.5" />
              <span>Xona nomi, bino va sig'im ma'lumotlari</span>
            </li>
          </ul>
        </div>

        <div class="space-y-4">
          <h3 class="text-sm font-medium text-slate-700">Kerakli ustunlar</h3>
          <ul class="space-y-2 text-sm text-slate-600">
            <li class="flex items-start gap-2">
              <Info class="w-4 h-4 text-blue-500 mt-0.5" />
              <span><strong>Xona nomi</strong> — 301, A-201 va h.k.</span>
            </li>
            <li class="flex items-start gap-2">
              <Info class="w-4 h-4 text-blue-500 mt-0.5" />
              <span><strong>Bino</strong> — A, B, C bino</span>
            </li>
            <li class="flex items-start gap-2">
              <Info class="w-4 h-4 text-blue-500 mt-0.5" />
              <span><strong>Sig'im</strong> — xona sig'imi (raqam)</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-4 p-3 bg-teal-50 rounded-xl flex items-start gap-3">
        <AlertCircle class="w-4 h-4 text-teal-600 mt-0.5 flex-shrink-0" />
        <p class="text-xs text-teal-700">
          <strong>Muhim:</strong> Xona nomlari bazadagi nomlar bilan mos kelishi kerak. 
          Yangi xonalar avtomatik yaratiladi.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, CheckCircle, DoorOpen, FileSpreadsheet, Info, Loader2, Upload, X } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const isDragging = ref(false)
const selectedFile = ref(null)
const clearExisting = ref(false)
const uploading = ref(false)
const uploadResult = ref(null)
const stats = ref(null)

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

    const res = await api.request('/rooms/import-excel', { method: 'POST', body: formData })
    uploadResult.value = { success: true, message: "Xona ma'lumotlari muvaffaqiyatli import qilindi!", ...res }
    loadStats()
  } catch (e) {
    console.error('Upload error:', e)
    uploadResult.value = { success: false, message: e.response?.data?.detail || "Yuklashda xatolik yuz berdi" }
  } finally {
    uploading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await api.request('/rooms/stats')
    stats.value = res || {}
  } catch (e) {
    // silently fail
  }
}

onMounted(() => {
  loadStats()
})
</script>
