<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 p-6 text-white">
      <div class="flex items-center gap-3 mb-2">
        <Activity :size="28" />
        <h1 class="text-xl font-bold">{{ t('activity.title') || 'Foydalanuvchilar faoliyati' }}</h1>
      </div>
      <p class="text-amber-100 text-sm">{{ t('activity.description') || "Barcha foydalanuvchilarning har bir qadami kuzatiladi" }}</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm text-center">
        <p class="text-2xl font-bold text-blue-600">{{ stats.total || 0 }}</p>
        <p class="text-xs text-gray-500 mt-1">Jami loglar</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm text-center">
        <p class="text-2xl font-bold text-emerald-600">{{ stats.today_count || 0 }}</p>
        <p class="text-xs text-gray-500 mt-1">Bugungi</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm text-center">
        <p class="text-2xl font-bold text-violet-600">{{ stats.auth_count || 0 }}</p>
        <p class="text-xs text-gray-500 mt-1">Kirish/Chiqish</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm text-center">
        <p class="text-2xl font-bold text-amber-600">{{ activeUsersCount }}</p>
        <p class="text-xs text-gray-500 mt-1">Aktiv foydalanuvchilar</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Search User -->
        <div class="relative flex-1 min-w-[200px]">
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Foydalanuvchi nomi, IP yoki tavsif..."
            class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 outline-none text-sm"
          />
        </div>

        <!-- User Filter -->
        <select v-model="selectedUserId" @change="resetAndLoad" class="px-4 py-2.5 rounded-xl border border-gray-200 focus:border-amber-500 outline-none text-sm min-w-[180px]">
          <option :value="null">Barcha foydalanuvchilar</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }} ({{ roleLabel(u.role) }})</option>
        </select>

        <!-- Action Type Filter -->
        <select v-model="filterAction" @change="resetAndLoad" class="px-4 py-2.5 rounded-xl border border-gray-200 focus:border-amber-500 outline-none text-sm">
          <option value="">Barcha harakatlar</option>
          <option value="auth">Kirish/Chiqish</option>
          <option value="crud">CRUD</option>
          <option value="system">Tizim</option>
          <option value="error">Xatoliklar</option>
        </select>

        <!-- Refresh -->
        <button @click="refreshAll" class="p-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors" title="Yangilash">
          <RefreshCw :size="16" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Selected User Info -->
    <div v-if="selectedUserInfo" class="bg-white rounded-2xl border border-amber-200 p-5 shadow-sm">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-amber-500/20">
          {{ selectedUserInfo.name?.charAt(0) || '?' }}
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-bold text-gray-900">{{ selectedUserInfo.name }}</h3>
          <p class="text-sm text-gray-500">{{ selectedUserInfo.email }} • {{ roleLabel(selectedUserInfo.role) }}</p>
        </div>
        <div class="text-right">
          <p class="text-2xl font-bold text-amber-600">{{ totalLogs }}</p>
          <p class="text-xs text-gray-500">ta harakat</p>
        </div>
      </div>
    </div>

    <!-- Activity Log Table -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50/50">
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Vaqt</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Foydalanuvchi</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Harakat</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Tavsif</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">IP manzil</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Tafsilotlar</th>
            </tr>
          </thead>
          <tbody v-if="logs.length > 0">
            <tr v-for="log in logs" :key="log.id" class="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
              <td class="px-4 py-3">
                <div class="text-xs text-gray-900 font-medium">{{ formatDate(log.created_at) }}</div>
                <div class="text-[10px] text-gray-400">{{ formatTime(log.created_at) }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div :class="['w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold', getUserColor(log.user_name)]">
                    {{ log.user_name?.charAt(0) || '?' }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ log.user_name || 'Tizim' }}</p>
                    <p v-if="log.user_id" class="text-[10px] text-gray-400">ID: {{ log.user_id }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span :class="['inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium', getActionBadge(log.action)]">
                  <component :is="getActionIcon(log.action)" :size="12" />
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <p class="text-sm text-gray-700 max-w-xs truncate">{{ log.description }}</p>
                <p v-if="log.entity_type" class="text-[10px] text-gray-400">{{ log.entity_type }}</p>
              </td>
              <td class="px-4 py-3">
                <span class="text-xs text-gray-500 font-mono">{{ log.ip_address || '-' }}</span>
              </td>
              <td class="px-4 py-3">
                <button @click="showDetail(log)" class="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors">
                  <Eye :size="14" />
                </button>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="6" class="px-4 py-12 text-center">
                <FileText :size="40" class="mx-auto text-gray-200 mb-3" />
                <p class="text-sm text-gray-400">{{ loading ? 'Yuklanmoqda...' : "Ma'lumot topilmadi" }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-gray-100">
        <p class="text-xs text-gray-500">{{ totalLogs }} ta dan {{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, totalLogs) }}</p>
        <div class="flex items-center gap-1">
          <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1" class="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
            <ChevronLeft :size="16" />
          </button>
          <template v-for="p in visiblePages" :key="p">
            <span v-if="p === '...'" class="px-2 text-xs text-gray-400">...</span>
            <button v-else @click="goToPage(p)" :class="['min-w-[32px] h-8 rounded-lg text-xs font-medium transition-colors', p === currentPage ? 'bg-amber-500 text-white' : 'hover:bg-gray-100 text-gray-600']">
              {{ p }}
            </button>
          </template>
          <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages" class="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
            <ChevronRight :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <Transition name="fade">
      <div v-if="detailLog" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="detailLog = null">
        <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto">
          <div class="flex items-center justify-between p-5 border-b border-gray-100">
            <h3 class="text-lg font-bold text-gray-900">Harakat tafsilotlari</h3>
            <button @click="detailLog = null" class="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <X :size="18" />
            </button>
          </div>
          <div class="p-5 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs text-gray-400 mb-1">Foydalanuvchi</p>
                <p class="text-sm font-medium">{{ detailLog.user_name || 'Tizim' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400 mb-1">Vaqt</p>
                <p class="text-sm font-medium">{{ formatDateTime(detailLog.created_at) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400 mb-1">Harakat</p>
                <span :class="['inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium', getActionBadge(detailLog.action)]">
                  {{ getActionLabel(detailLog.action) }}
                </span>
              </div>
              <div>
                <p class="text-xs text-gray-400 mb-1">IP manzil</p>
                <p class="text-sm font-mono">{{ detailLog.ip_address || '-' }}</p>
              </div>
            </div>
            <div>
              <p class="text-xs text-gray-400 mb-1">Tavsif</p>
              <p class="text-sm bg-gray-50 rounded-xl p-3">{{ detailLog.description }}</p>
            </div>
            <div v-if="detailLog.user_agent">
              <p class="text-xs text-gray-400 mb-1">Brauzer</p>
              <p class="text-xs bg-gray-50 rounded-xl p-3 text-gray-600 break-all">{{ detailLog.user_agent }}</p>
            </div>
            <div v-if="detailLog.context">
              <p class="text-xs text-gray-400 mb-1">Kontekst</p>
              <pre class="text-xs bg-gray-900 text-emerald-400 rounded-xl p-3 overflow-x-auto">{{ formatJSON(detailLog.context) }}</pre>
            </div>
            <div v-if="detailLog.entity_type">
              <p class="text-xs text-gray-400 mb-1">Ob'ekt</p>
              <p class="text-sm">{{ detailLog.entity_type }} <span v-if="detailLog.entity_id" class="text-gray-400">#{{ detailLog.entity_id }}</span></p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Loading overlay -->
    <div v-if="loading" class="fixed bottom-6 left-6 z-50 bg-white rounded-xl px-4 py-2 shadow-lg border border-gray-100 flex items-center gap-2">
      <Loader2 :size="14" class="animate-spin text-amber-600" />
      <span class="text-xs text-gray-600">Yuklanmoqda...</span>
    </div>
  </div>
</template>

<script setup>
import {
    Activity,
    ChevronLeft,
    ChevronRight,
    Edit,
    Eye,
    FileText,
    Loader2,
    LogIn,
    LogOut,
    Plus,
    RefreshCw,
    Search,
    Trash2,
    X
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(false)
const logs = ref([])
const users = ref([])
const stats = ref({})
const searchQuery = ref('')
const selectedUserId = ref(null)
const filterAction = ref('')
const currentPage = ref(1)
const pageSize = ref(30)
const totalLogs = ref(0)
const totalPages = ref(1)
const detailLog = ref(null)

let searchTimer = null
const debouncedSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { resetAndLoad() }, 400)
}

const activeUsersCount = computed(() => {
  if (!logs.value.length) return 0
  const uniqueUsers = new Set(logs.value.filter(l => l.user_id).map(l => l.user_id))
  return uniqueUsers.size
})

const selectedUserInfo = computed(() => {
  if (!selectedUserId.value) return null
  return users.value.find(u => u.id === selectedUserId.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      pages.push(i)
    }
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const roleLabel = (role) => {
  const labels = {
    student: 'Talaba',
    leader: 'Sardor',
    teacher: "O'qituvchi",
    admin: 'Admin',
    superadmin: 'Super Admin',
    academic_affairs: 'Akademik ishlar'
  }
  return labels[role] || role
}

const getUserColor = (name) => {
  if (!name) return 'bg-gray-400'
  const colors = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500', 'bg-cyan-500', 'bg-indigo-500', 'bg-pink-500']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const getActionBadge = (action) => {
  const map = {
    login: 'bg-emerald-100 text-emerald-700',
    logout: 'bg-gray-100 text-gray-700',
    login_failed: 'bg-red-100 text-red-700',
    create: 'bg-blue-100 text-blue-700',
    read: 'bg-sky-100 text-sky-700',
    update: 'bg-amber-100 text-amber-700',
    delete: 'bg-red-100 text-red-700',
    import: 'bg-violet-100 text-violet-700',
    export: 'bg-indigo-100 text-indigo-700',
    error: 'bg-rose-100 text-rose-700',
    password_change: 'bg-orange-100 text-orange-700',
    password_reset: 'bg-orange-100 text-orange-700',
  }
  return map[action] || 'bg-gray-100 text-gray-700'
}

const getActionIcon = (action) => {
  const map = {
    login: markRaw(LogIn),
    logout: markRaw(LogOut),
    login_failed: markRaw(X),
    create: markRaw(Plus),
    read: markRaw(Eye),
    update: markRaw(Edit),
    delete: markRaw(Trash2),
  }
  return map[action] || markRaw(Activity)
}

const getActionLabel = (action) => {
  const map = {
    login: 'Kirish',
    logout: 'Chiqish',
    login_failed: 'Muvaffaqiyatsiz',
    create: 'Yaratish',
    read: "Ko'rish",
    update: 'Tahrirlash',
    delete: "O'chirish",
    import: 'Import',
    export: 'Export',
    error: 'Xatolik',
    password_change: 'Parol',
    password_reset: 'Parol tiklash',
    system: 'Tizim',
    sync: 'Sinxronizatsiya',
    ai_analysis: 'AI Tahlil',
  }
  return map[action] || action
}

const formatDate = (dt) => {
  if (!dt) return '-'
  const d = new Date(dt)
  return d.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatTime = (dt) => {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const formatDateTime = (dt) => formatDate(dt) + ' ' + formatTime(dt)

const formatJSON = (str) => {
  try {
    return JSON.stringify(JSON.parse(str), null, 2)
  } catch {
    return str
  }
}

const showDetail = (log) => {
  detailLog.value = log
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadLogs()
}

const resetAndLoad = () => {
  currentPage.value = 1
  loadLogs()
}

const refreshAll = () => {
  loadStats()
  loadLogs()
}

const loadStats = async () => {
  try {
    stats.value = await api.request('/logs/stats')
  } catch (e) {
    console.error('Stats error:', e)
  }
}

const loadUsers = async () => {
  try {
    const res = await api.request('/users?page_size=500')
    users.value = res.items || res || []
  } catch (e) {
    console.error('Users error:', e)
  }
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.set('page', currentPage.value)
    params.set('page_size', pageSize.value)
    if (selectedUserId.value) params.set('user_id', selectedUserId.value)
    if (filterAction.value) params.set('action_type', filterAction.value)
    if (searchQuery.value) params.set('search', searchQuery.value)

    const res = await api.request(`/logs?${params.toString()}`)
    logs.value = res.items || []
    totalLogs.value = res.total || 0
    totalPages.value = res.total_pages || 1
  } catch (e) {
    console.error('Logs error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  loadUsers()
  loadLogs()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
