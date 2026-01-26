<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Tizim jurnali</h1>
        <p class="text-slate-500">Barcha faoliyatlar tarixi</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="filterType" class="px-4 py-2 rounded-xl border border-slate-200 focus:border-amber-500 outline-none">
          <option value="">Barcha turlar</option>
          <option value="auth">Autentifikatsiya</option>
          <option value="crud">CRUD amallar</option>
          <option value="system">Tizim</option>
          <option value="error">Xatolar</option>
        </select>
        <button 
          @click="exportLogs"
          class="px-4 py-2 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2"
        >
          <Download class="w-4 h-4" />
          Eksport
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <ScrollText class="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ logs.length }}</p>
            <p class="text-xs text-slate-500">Jami loglar</p>
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
            <p class="text-xs text-slate-500">Kirish/Chiqish</p>
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
            <p class="text-xs text-slate-500">CRUD amallar</p>
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
            <p class="text-xs text-slate-500">Xatolar</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-4 font-semibold text-slate-600">Vaqt</th>
              <th class="text-left p-4 font-semibold text-slate-600">Tur</th>
              <th class="text-left p-4 font-semibold text-slate-600">Foydalanuvchi</th>
              <th class="text-left p-4 font-semibold text-slate-600">Amal</th>
              <th class="text-left p-4 font-semibold text-slate-600">IP manzil</th>
              <th class="text-left p-4 font-semibold text-slate-600">Holat</th>
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
                  {{ log.status === 'success' ? 'Muvaffaqiyatli' : 'Xato' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredLogs.length === 0" class="p-12 text-center">
        <ScrollText class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Log topilmadi</p>
      </div>

      <!-- Pagination -->
      <div class="p-4 border-t border-slate-100 flex items-center justify-between">
        <p class="text-sm text-slate-500">{{ filteredLogs.length }} ta yozuvdan {{ Math.min(20, filteredLogs.length) }} tasi ko'rsatilmoqda</p>
        <div class="flex items-center gap-2">
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
  </div>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
import {
  Download,
  ScrollText,
  LogIn,
  FileEdit,
  AlertCircle,
  CheckCircle,
  XCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'

const filterType = ref('')

const logs = ref([
  { id: 1, timestamp: '2026-01-25T10:30:00', type: 'auth', user: 'Super Admin', action: 'Tizimga kirdi', ip: '192.168.1.100', status: 'success' },
  { id: 2, timestamp: '2026-01-25T10:25:00', type: 'crud', user: 'Admin', action: 'Yangi talaba qo\'shdi: Ali Valiyev', ip: '192.168.1.101', status: 'success' },
  { id: 3, timestamp: '2026-01-25T10:20:00', type: 'crud', user: 'Sardor', action: 'Davomat yozuvi qo\'shildi', ip: '192.168.1.102', status: 'success' },
  { id: 4, timestamp: '2026-01-25T10:15:00', type: 'auth', user: 'Student', action: 'Tizimga kirdi', ip: '192.168.1.103', status: 'success' },
  { id: 5, timestamp: '2026-01-25T10:10:00', type: 'error', user: 'Unknown', action: 'Noto\'g\'ri parol kiritildi', ip: '192.168.1.200', status: 'error' },
  { id: 6, timestamp: '2026-01-25T10:05:00', type: 'system', user: 'System', action: 'Avtomatik zaxira nusxa yaratildi', ip: 'localhost', status: 'success' },
  { id: 7, timestamp: '2026-01-25T09:55:00', type: 'crud', user: 'Admin', action: 'Guruh ma\'lumoti yangilandi: SE-401', ip: '192.168.1.101', status: 'success' },
  { id: 8, timestamp: '2026-01-25T09:50:00', type: 'auth', user: 'Admin', action: 'Tizimdan chiqdi', ip: '192.168.1.101', status: 'success' },
  { id: 9, timestamp: '2026-01-25T09:45:00', type: 'crud', user: 'Super Admin', action: 'Bildirishnoma yuborildi', ip: '192.168.1.100', status: 'success' },
  { id: 10, timestamp: '2026-01-25T09:40:00', type: 'error', user: 'System', action: 'Email yuborishda xato', ip: 'localhost', status: 'error' },
  { id: 11, timestamp: '2026-01-25T09:35:00', type: 'crud', user: 'Sardor', action: 'Talaba ma\'lumoti yangilandi', ip: '192.168.1.102', status: 'success' },
  { id: 12, timestamp: '2026-01-25T09:30:00', type: 'auth', user: 'Sardor', action: 'Tizimga kirdi', ip: '192.168.1.102', status: 'success' }
])

const authLogs = computed(() => logs.value.filter(l => l.type === 'auth').length)
const crudLogs = computed(() => logs.value.filter(l => l.type === 'crud').length)
const errorLogs = computed(() => logs.value.filter(l => l.type === 'error' || l.status === 'error').length)

const filteredLogs = computed(() => {
  if (!filterType.value) return logs.value
  return logs.value.filter(l => l.type === filterType.value)
})

const formatDate = (timestamp) => {
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

const exportLogs = () => {
  alert('Loglar yuklanmoqda...')
}
</script>
