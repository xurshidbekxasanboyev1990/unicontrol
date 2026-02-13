<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 class="w-8 h-8 animate-spin text-amber-600" />
      <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <div class="flex items-center gap-3 text-red-600">
        <AlertCircle class="w-6 h-6" />
        <span>{{ error }}</span>
      </div>
      <button 
        @click="loadLogs" 
        class="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
      >
        {{ $t('common.retry') }}
      </button>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('logs.title') }}</h1>
          <p class="text-sm text-slate-500">{{ $t('logs.allActivities') }}</p>
        </div>
        <div class="flex items-center gap-2 sm:gap-3">
          <select v-model="filterType" @change="loadLogs" class="flex-1 sm:flex-none px-3 sm:px-4 py-2 rounded-xl border border-slate-200 focus:border-amber-500 outline-none text-sm">
            <option value="">{{ $t('logs.allTypes') }}</option>
            <option value="auth">{{ $t('logs.auth') }}</option>
            <option value="crud">{{ $t('logs.crud') }}</option>
            <option value="system">{{ $t('logs.system') }}</option>
            <option value="error">{{ $t('logs.errors') }}</option>
          </select>
          <button 
            @click="exportLogs"
            class="px-4 py-2 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2"
          >
            <Download class="w-4 h-4" />
            {{ $t('logs.export') }}
          </button>
        </div>
      </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <ScrollText class="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ logs.length }}</p>
            <p class="text-xs text-slate-500">{{ $t('logs.totalLogs') }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <LogIn class="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-emerald-600">{{ authLogs }}</p>
            <p class="text-xs text-slate-500">{{ $t('logs.loginLogout') }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-violet-100 rounded-xl flex items-center justify-center">
            <FileEdit class="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-violet-600">{{ crudLogs }}</p>
            <p class="text-xs text-slate-500">{{ $t('logs.crudActions') }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-rose-100 rounded-xl flex items-center justify-center">
            <AlertCircle class="w-5 h-5 text-rose-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-rose-600">{{ errorLogs }}</p>
            <p class="text-xs text-slate-500">{{ $t('logs.errors') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px]">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('logs.time') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('logs.type') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('common.name') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('common.actions') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('logs.ipAddress') }}</th>
              <th class="text-left p-4 font-semibold text-slate-600">{{ $t('logs.status') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="log in filteredLogs" :key="log.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-4 text-sm text-slate-600">{{ formatDate(log.timestamp) }}</td>
              <td class="p-4">
                <span 
                  class="px-2 py-1 rounded-lg text-xs font-medium"
                  :class="getTypeClass(log.type)"
                >
                  {{ getTypeLabel(log.type) }}
                </span>
              </td>
              <td class="p-4">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white text-xs font-bold">
                    {{ log.user.charAt(0) }}
                  </div>
                  <span class="text-slate-700">{{ log.user }}</span>
                </div>
              </td>
              <td class="p-4 text-slate-700">{{ log.action }}</td>
              <td class="p-4 text-sm text-slate-500 font-mono">{{ log.ip }}</td>
              <td class="p-4">
                <span 
                  class="flex items-center gap-1 text-sm"
                  :class="log.status === 'success' ? 'text-emerald-600' : 'text-rose-600'"
                >
                  <component :is="log.status === 'success' ? CheckCircle : XCircle" class="w-4 h-4" />
                  {{ log.status === 'success' ? $t('logs.success') : $t('common.error') }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredLogs.length === 0" class="p-12 text-center">
        <ScrollText class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">{{ $t('logs.logNotFound') }}</p>
      </div>

      <!-- Pagination -->
      <div class="p-3 sm:p-4 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <p class="text-sm text-slate-500">{{ $t('logs.showingOf', { shown: Math.min(20, filteredLogs.length), total: filteredLogs.length }) }}</p>
        <div class="flex items-center gap-1 sm:gap-2 flex-wrap">
          <button class="px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50" disabled>
            <ChevronLeft class="w-4 h-4" />
          </button>
          <button class="px-3 py-1.5 rounded-lg bg-amber-500 text-white text-sm">1</button>
          <button class="px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50">2</button>
          <button class="px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50">3</button>
          <button class="px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    AlertCircle,
    CheckCircle,
    ChevronLeft,
    ChevronRight,
    Download,
    FileEdit,
    Loader2,
    LogIn,
    ScrollText,
    XCircle
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const toast = useToastStore()
const langStore = useLanguageStore()
const { t } = langStore

// State
const loading = ref(true)
const error = ref(null)
const filterType = ref('')
const logs = ref([])
const page = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

// Load logs from API
const loadLogs = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = { page: page.value, limit: 50 }
    if (filterType.value) {
      params.type = filterType.value
    }
    
    const response = await api.getLogs(params)
    logs.value = (response.items || response || []).map(l => ({
      id: l.id,
      timestamp: l.created_at || l.timestamp,
      type: l.level?.toLowerCase() || l.type || 'info',
      user: l.user_name || l.user || 'System',
      action: l.action || l.message || l.details,
      ip: l.ip_address || l.ip || '-',
      status: l.level === 'ERROR' ? 'error' : 'success'
    }))
    
    totalPages.value = response.pages || Math.ceil((response.total || logs.value.length) / 50)
    totalCount.value = response.total || logs.value.length
  } catch (e) {
    console.error('Error loading logs:', e)
    error.value = 'Loglarni yuklashda xatolik'
  } finally {
    loading.value = false
  }
}

const authLogs = computed(() => logs.value.filter(l => l.type === 'auth').length)
const crudLogs = computed(() => logs.value.filter(l => l.type === 'crud').length)
const errorLogs = computed(() => logs.value.filter(l => l.type === 'error' || l.status === 'error').length)

const filteredLogs = computed(() => {
  if (!filterType.value) return logs.value
  return logs.value.filter(l => l.type === filterType.value)
})

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('uz-UZ', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTypeClass = (type) => {
  const classes = {
    auth: 'bg-emerald-100 text-emerald-700',
    crud: 'bg-violet-100 text-violet-700',
    system: 'bg-blue-100 text-blue-700',
    error: 'bg-rose-100 text-rose-700'
  }
  return classes[type] || 'bg-slate-100 text-slate-700'
}

const getTypeLabel = (type) => {
  const labels = {
    auth: 'Kirish',
    crud: 'CRUD',
    system: 'Tizim',
    error: 'Xato'
  }
  return labels[type] || type
}

const exportLogs = async () => {
  try {
    toast.info(t('common.loading'))
    const response = await api.exportToExcel('logs')
    
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'logs.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    toast.success(t('common.success'))
  } catch (e) {
    console.error('Error exporting logs:', e)
    toast.error('Eksport qilishda xatolik')
  }
}

const goToPage = (p) => {
  page.value = p
  loadLogs()
}

// Initialize
onMounted(() => {
  loadLogs()
})
</script>
