<template>
  <div class="space-y-5">
    <!-- Stats -->
    <div v-if="stats" class="grid grid-cols-3 gap-3">
      <div class="rounded-xl bg-violet-50 p-3 text-center">
        <p class="text-lg font-bold text-violet-600">{{ stats.total_entries }}</p>
        <p class="text-[10px] text-gray-500">Jami yozuvlar</p>
      </div>
      <div class="rounded-xl bg-violet-50 p-3 text-center">
        <p class="text-lg font-bold text-violet-600">{{ stats.total_teachers }}</p>
        <p class="text-[10px] text-gray-500">O'qituvchilar</p>
      </div>
      <div class="rounded-xl bg-violet-50 p-3 text-center">
        <p class="text-lg font-bold text-violet-600">{{ stats.total_departments }}</p>
        <p class="text-[10px] text-gray-500">Kafedralar</p>
      </div>
    </div>

    <!-- Dropzone -->
    <div
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="onDrop"
      :class="['border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer', isDragging ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-violet-300 hover:bg-gray-50']"
      @click="$refs.fileInput.click()"
    >
      <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileSelect" />
      <FileSpreadsheet :size="40" :class="['mx-auto mb-3', isDragging ? 'text-violet-500' : 'text-gray-300']" />
      <p v-if="!selectedFile" class="text-sm text-gray-500">Faylni bu yerga tashlang yoki bosib tanlang</p>
      <div v-else class="flex items-center justify-center gap-2">
        <FileSpreadsheet :size="18" class="text-emerald-600" />
        <span class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</span>
        <span class="text-xs text-gray-400">({{ formatSize(selectedFile.size) }})</span>
        <button @click.stop="selectedFile = null" class="text-gray-400 hover:text-red-500"><X :size="14" /></button>
      </div>
    </div>

    <!-- Options -->
    <label class="flex items-center gap-2 text-sm text-gray-600">
      <input type="checkbox" v-model="clearExisting" class="rounded border-gray-300 text-violet-600 focus:ring-violet-500" />
      Eski ma'lumotlarni o'chirish
    </label>

    <!-- Upload Button -->
    <button
      @click="uploadFile"
      :disabled="!selectedFile || uploading"
      :class="['w-full rounded-xl py-3 text-sm font-medium text-white flex items-center justify-center gap-2 transition-all', !selectedFile || uploading ? 'bg-gray-300 cursor-not-allowed' : 'bg-violet-600 hover:bg-violet-700']"
    >
      <Loader2 v-if="uploading" :size="16" class="animate-spin" />
      <Upload v-else :size="16" />
      {{ uploading ? 'Yuklanmoqda...' : 'Yuklash' }}
    </button>

    <!-- Result -->
    <div v-if="result" :class="['rounded-xl p-4 text-sm', result.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200']">
      <div class="flex items-start gap-2">
        <CheckCircle v-if="result.success" :size="18" class="text-emerald-600 mt-0.5 flex-shrink-0" />
        <AlertCircle v-else :size="18" class="text-red-600 mt-0.5 flex-shrink-0" />
        <div>
          <p :class="result.success ? 'text-emerald-700 font-medium' : 'text-red-700 font-medium'">{{ result.message }}</p>
          <div v-if="result.success" class="mt-2 space-y-1 text-xs text-emerald-600">
            <p>📊 {{ result.total_imported }} ta yozuv import qilindi</p>
            <p>👨‍🏫 {{ result.total_teachers }} ta o'qituvchi</p>
            <p>🏫 {{ result.total_departments }} ta kafedra</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Format hints -->
    <div class="bg-violet-50 rounded-xl p-4 space-y-1.5">
      <p class="text-xs font-medium text-violet-700">📋 Excel format talablari:</p>
      <p class="text-[11px] text-violet-600">• Sheet nomi "bandlig" yoki "band" so'zini o'z ichiga olishi kerak</p>
      <p class="text-[11px] text-violet-600">• O'qituvchilar ismlari — 2-6 so'zli, raqamsiz</p>
      <p class="text-[11px] text-violet-600">• Kun nomlari: Dushanba, Seshanba, Chorshanba...</p>
      <p class="text-[11px] text-violet-600">• Para raqamlari: 1-7 (vaqt avtomatik aniqlanadi)</p>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, CheckCircle, FileSpreadsheet, Loader2, Upload, X } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const emit = defineEmits(['completed'])

const isDragging = ref(false)
const selectedFile = ref(null)
const clearExisting = ref(true)
const uploading = ref(false)
const result = ref(null)
const stats = ref(null)

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

const onFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) { selectedFile.value = file; result.value = null }
}

const onDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    selectedFile.value = file; result.value = null
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  uploading.value = true; result.value = null
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('clear_existing', clearExisting.value)
    const res = await api.request('/academic/workload/upload-excel', { method: 'POST', body: formData })
    result.value = res
    if (res.success) { loadStats(); emit('completed') }
  } catch (e) {
    result.value = { success: false, message: e.response?.data?.detail || e.data?.detail || "Yuklashda xatolik" }
  } finally {
    uploading.value = false
  }
}

const loadStats = async () => {
  try { stats.value = await api.request('/academic/workload/stats') } catch {}
}

onMounted(() => { loadStats() })
</script>
