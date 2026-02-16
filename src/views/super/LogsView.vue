<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading && !logs.length" class="flex items-center justify-center py-12">
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
        <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
          <!-- Search -->
          <div class="relative">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              v-model="searchQuery"
              @input="debouncedSearch"
              type="text"
              :placeholder="$t('common.search') + '...'"
              class="w-48 sm:w-56 pl-9 pr-4 py-2 rounded-xl border border-slate-200 focus:border-amber-500 outline-none text-sm"
            />
          </div>
          <!-- Type filter -->
          <select v-model="filterType" @change="resetAndLoad" class="px-3 sm:px-4 py-2 rounded-xl border border-slate-200 focus:border-amber-500 outline-none text-sm">
            <option value="">{{ $t('logs.allTypes') }}</option>
            <option value="auth">{{ $t('logs.auth') }}</option>
            <option value="crud">{{ $t('logs.crud') }}</option>
            <option value="system">{{ $t('logs.system') }}</option>
            <option value="error">{{ $t('logs.errors') }}</option>
          </select>
          <!-- Actions -->
          <button 
            @click="refreshLogs"
            class="p-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            :title="$t('common.refresh')"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
          </button>
          <button 
            @click="confirmClearLogs"
            class="p-2 text-rose-500 hover:bg-rose-50 rounded-xl transition-colors"
            :title="$t('logs.clearAll')"
          >
            <Trash2 class="w-4 h-4" />
          </button>
          <button 
            @click="exportLogs"
            class="px-4 py-2 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2"
          >
            <Download class="w-4 h-4" />
            <span class="hidden sm:inline">{{ $t('logs.export') }}</span>
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <div class="bg-white rounded-2xl border border-slate-200 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
              <ScrollText class="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-slate-800">{{ stats.total }}</p>
              <p class="text-xs text-slate-500">{{ $t('logs.totalLogs') }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-4 cursor-pointer hover:border-emerald-300 transition-colors" @click="filterType = 'auth'; resetAndLoad()">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
              <LogIn class="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-emerald-600">{{ stats.auth_count }}</p>
              <p class="text-xs text-slate-500">{{ $t('logs.loginLogout') }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-4 cursor-pointer hover:border-violet-300 transition-colors" @click="filterType = 'crud'; resetAndLoad()">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-violet-100 rounded-xl flex items-center justify-center">
              <FileEdit class="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-violet-600">{{ stats.crud_count }}</p>
              <p class="text-xs text-slate-500">{{ $t('logs.crudActions') }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-4 cursor-pointer hover:border-rose-300 transition-colors" @click="filterType = 'error'; resetAndLoad()">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-rose-100 rounded-xl flex items-center justify-center">
              <AlertCircle class="w-5 h-5 text-rose-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-rose-600">{{ stats.error_count }}</p>
              <p class="text-xs text-slate-500">{{ $t('logs.errors') }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
              <Calendar class="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-amber-600">{{ stats.today_count }}</p>
              <p class="text-xs text-slate-500">{{ $t('logs.today') }}</p>
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
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('logs.time') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('logs.type') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('common.name') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('logs.action') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('logs.entity') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm">{{ $t('logs.ipAddress') }}</th>
                <th class="text-left p-4 font-semibold text-slate-600 text-sm w-10"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50 transition-colors group">
                <td class="p-4 text-sm text-slate-500 whitespace-nowrap">{{ formatDate(log.created_at) }}</td>
                <td class="p-4">
                  <span 
                    class="px-2 py-1 rounded-lg text-xs font-medium whitespace-nowrap"
                    :class="getActionClass(log.action)"
                  >
                    {{ getActionLabel(log.action) }}
                  </span>
                </td>
                <td class="p-4">
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                      {{ (log.user_name || 'S').charAt(0) }}
                    </div>
                    <span class="text-slate-700 text-sm">{{ log.user_name || 'Tizim' }}</span>
                  </div>
                </td>
                <td class="p-4 text-sm text-slate-700 max-w-[300px]">
                  <p class="truncate" :title="log.description">{{ log.description }}</p>
                </td>
                <td class="p-4 text-sm text-slate-500">
                  <span v-if="log.entity_type" class="px-2 py-0.5 bg-slate-100 rounded text-xs">
                    {{ log.entity_type }}
                    <span v-if="log.entity_id" class="text-slate-400">#{{ log.entity_id }}</span>
                  </span>
                  <span v-else class="text-slate-300">—</span>
                </td>
                <td class="p-4 text-sm text-slate-500 font-mono">{{ log.ip_address || '—' }}</td>
                <td class="p-4">
                  <button 
                    @click="deleteLog(log.id)"
                    class="p-1.5 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <X class="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Loading indicator -->
        <div v-if="loading && logs.length" class="p-4 text-center border-t border-slate-100">
          <Loader2 class="w-5 h-5 animate-spin text-amber-500 mx-auto" />
        </div>

        <div v-if="!loading && logs.length === 0" class="p-12 text-center">
          <ScrollText class="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p class="text-slate-500">{{ $t('logs.logNotFound') }}</p>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 0" class="p-3 sm:p-4 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <p class="text-sm text-slate-500">
            {{ $t('logs.showingOf', { shown: logs.length, total: totalCount }) }}
          </p>
          <div class="flex items-center gap-1 sm:gap-2 flex-wrap">
            <button 
              @click="goToPage(page - 1)" 
              :disabled="page <= 1"
              class="px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft class="w-4 h-4" />
            </button>
            
            <template v-for="p in visiblePages" :key="p">
              <button 
                v-if="p === '...'"
                class="px-3 py-1.5 text-sm text-slate-400" disabled
              >...</button>
              <button 
                v-else
                @click="goToPage(p)"
                class="px-3 py-1.5 rounded-lg text-sm transition-colors"
                :class="p === page ? 'bg-amber-500 text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-50'"
              >
                {{ p }}
              </button>
            </template>
            
            <button 
              @click="goToPage(page + 1)" 
              :disabled="page >= totalPages"
              class="px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Detail Modal -->
      <Teleport to="body">
        <Transition name="fade">
          <div v-if="selectedLog" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="selectedLog = null">
            <div class="bg-white rounded-2xl w-full max-w-lg shadow-xl overflow-hidden">
              <div class="p-6 border-b border-slate-100 flex items-center justify-between">
                <h3 class="font-semibold text-slate-800">{{ $t('logs.logDetail') }}</h3>
                <button @click="selectedLog = null" class="p-1.5 hover:bg-slate-100 rounded-lg">
                  <X class="w-5 h-5 text-slate-400" />
                </button>
              </div>
              <div class="p-6 space-y-3 max-h-[60vh] overflow-y-auto">
                <div><span class="text-sm text-slate-500">{{ $t('logs.action') }}:</span> <span class="font-medium">{{ selectedLog.action }}</span></div>
                <div><span class="text-sm text-slate-500">{{ $t('logs.description') }}:</span> <span>{{ selectedLog.description }}</span></div>
                <div><span class="text-sm text-slate-500">{{ $t('common.name') }}:</span> <span>{{ selectedLog.user_name || 'Tizim' }}</span></div>
                <div><span class="text-sm text-slate-500">{{ $t('logs.time') }}:</span> <span>{{ formatDate(selectedLog.created_at) }}</span></div>
                <div><span class="text-sm text-slate-500">{{ $t('logs.ipAddress') }}:</span> <span class="font-mono">{{ selectedLog.ip_address || '—' }}</span></div>
                <div v-if="selectedLog.entity_type"><span class="text-sm text-slate-500">{{ $t('logs.entity') }}:</span> <span>{{ selectedLog.entity_type }} #{{ selectedLog.entity_id }}</span></div>
                <div v-if="selectedLog.old_data">
                  <span class="text-sm text-slate-500">{{ $t('logs.oldData') }}:</span>
                  <pre class="mt-1 p-3 bg-slate-50 rounded-lg text-xs overflow-x-auto">{{ formatJSON(selectedLog.old_data) }}</pre>
                </div>
                <div v-if="selectedLog.new_data">
                  <span class="text-sm text-slate-500">{{ $t('logs.newData') }}:</span>
                  <pre class="mt-1 p-3 bg-slate-50 rounded-lg text-xs overflow-x-auto">{{ formatJSON(selectedLog.new_data) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Clear Confirm Modal -->
      <Teleport to="body">
        <Transition name="fade">
          <div v-if="showClearConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="showClearConfirm = false">
            <div class="bg-white rounded-2xl w-full max-w-sm shadow-xl p-6">
              <div class="text-center">
                <div class="w-12 h-12 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Trash2 class="w-6 h-6 text-rose-500" />
                </div>
                <h3 class="text-lg font-semibold text-slate-800 mb-2">{{ $t('logs.clearAll') }}</h3>
                <p class="text-sm text-slate-500 mb-6">{{ $t('logs.clearConfirm') }}</p>
                <div class="flex gap-3">
                  <button @click="showClearConfirm = false" class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50">
                    {{ $t('common.cancel') }}
                  </button>
                  <button @click="clearAllLogs" class="flex-1 px-4 py-2.5 bg-rose-500 text-white rounded-xl hover:bg-rose-600">
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </template>
  </div>
</template>

<script setup>
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    AlertCircle,
    Calendar,
    ChevronLeft,
    ChevronRight,
    Download,
    FileEdit,
    Loader2,
    LogIn,
    RefreshCw,
    ScrollText,
    Search,
    Trash2,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const toast = useToastStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const error = ref(null)
const filterType = ref('')
const searchQuery = ref('')
const logs = ref([])
const page = ref(1)
const pageSize = ref(30)
const totalPages = ref(1)
const totalCount = ref(0)
const selectedLog = ref(null)
const showClearConfirm = ref(false)
const stats = ref({
  total: 0,
  auth_count: 0,
  crud_count: 0,
  system_count: 0,
  error_count: 0,
  today_count: 0
})

let searchTimeout = null

// Load stats from API
const loadStats = async () => {
  try {
    const response = await api.getLogStats()
    stats.value = response
  } catch (e) {
    console.error('Error loading log stats:', e)
  }
}

// Load logs from API
const loadLogs = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterType.value) {
      params.action_type = filterType.value
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    
    const response = await api.getLogs(params)
    logs.value = response.items || []
    totalPages.value = response.total_pages || 1
    totalCount.value = response.total || 0
  } catch (e) {
    console.error('Error loading logs:', e)
    error.value = t('logs.loadError')
  } finally {
    loading.value = false
  }
}

const resetAndLoad = () => {
  page.value = 1
  loadLogs()
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    resetAndLoad()
  }, 400)
}

const refreshLogs = () => {
  loadStats()
  loadLogs()
}

// Pagination
const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = page.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const goToPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  loadLogs()
}

// Actions
const deleteLog = async (id) => {
  try {
    await api.deleteLog(id)
    logs.value = logs.value.filter(l => l.id !== id)
    totalCount.value--
    toast.success(t('logs.logDeleted'))
    loadStats()
  } catch (e) {
    console.error('Error deleting log:', e)
    toast.error(t('common.error'))
  }
}

const confirmClearLogs = () => {
  showClearConfirm.value = true
}

const clearAllLogs = async () => {
  showClearConfirm.value = false
  try {
    await api.clearLogs()
    logs.value = []
    totalCount.value = 0
    totalPages.value = 1
    page.value = 1
    toast.success(t('logs.logsCleared'))
    loadStats()
  } catch (e) {
    console.error('Error clearing logs:', e)
    toast.error(t('common.error'))
  }
}

const exportLogs = async () => {
  try {
    toast.info(t('common.loading'))
    // Export as CSV from current logs
    const headers = ['Vaqt', 'Harakat', 'Tavsif', 'Foydalanuvchi', 'IP', 'Ob\'ekt']
    const rows = logs.value.map(l => [
      formatDate(l.created_at),
      l.action,
      l.description,
      l.user_name || 'Tizim',
      l.ip_address || '',
      l.entity_type ? `${l.entity_type}#${l.entity_id || ''}` : ''
    ])
    
    const csvContent = [headers.join(','), ...rows.map(r => r.map(c => `"${(c || '').replace(/"/g, '""')}"`).join(','))].join('\n')
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `logs_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    toast.success(t('logs.exportSuccess'))
  } catch (e) {
    console.error('Error exporting logs:', e)
    toast.error(t('common.error'))
  }
}

// Helpers
const formatDate = (timestamp) => {
  if (!timestamp) return '—'
  return new Date(timestamp).toLocaleString('uz-UZ', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatJSON = (jsonStr) => {
  try {
    return JSON.stringify(JSON.parse(jsonStr), null, 2)
  } catch {
    return jsonStr
  }
}

const getActionClass = (action) => {
  const authActions = ['login', 'logout', 'login_failed', 'password_change', 'password_reset']
  const crudActions = ['create', 'update', 'delete', 'import', 'export']
  const errorActions = ['error']
  
  if (authActions.includes(action)) return 'bg-emerald-100 text-emerald-700'
  if (crudActions.includes(action)) return 'bg-violet-100 text-violet-700'
  if (errorActions.includes(action)) return 'bg-rose-100 text-rose-700'
  if (action === 'login_failed') return 'bg-amber-100 text-amber-700'
  return 'bg-blue-100 text-blue-700'
}

const getActionLabel = (action) => {
  const labels = {
    login: t('logs.actionLogin'),
    logout: t('logs.actionLogout'),
    login_failed: t('logs.actionLoginFailed'),
    password_change: t('logs.actionPasswordChange'),
    password_reset: t('logs.actionPasswordReset'),
    create: t('logs.actionCreate'),
    update: t('logs.actionUpdate'),
    delete: t('logs.actionDelete'),
    import: t('logs.actionImport'),
    export: t('logs.actionExport'),
    sync: t('logs.actionSync'),
    ai_analysis: t('logs.actionAI'),
    report_generate: t('logs.actionReport'),
    user_activate: t('logs.actionActivate'),
    user_deactivate: t('logs.actionDeactivate'),
    role_change: t('logs.actionRoleChange'),
    system: t('logs.system'),
    error: t('logs.actionError'),
  }
  return labels[action] || action
}

// Initialize
onMounted(() => {
  loadStats()
  loadLogs()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
