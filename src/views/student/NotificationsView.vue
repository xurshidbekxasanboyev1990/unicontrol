<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Bildirishnomalar</h1>
        <p class="text-slate-500">Xabarlar va e'lonlar</p>
      </div>
      
      <div class="flex items-center gap-3">
        <button
          @click="markAllAsRead"
          class="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-slate-600 hover:bg-slate-50"
        >
          <CheckCheck :size="18" />
          <span>Barchasini o'qilgan deb belgilash</span>
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="flex gap-2 overflow-x-auto pb-2">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-medium transition-all"
        :class="activeTab === tab.id 
          ? 'bg-blue-500 text-white' 
          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
      >
        <component :is="tab.icon" :size="18" />
        {{ tab.name }}
        <span 
          v-if="tab.count > 0"
          class="rounded-full px-2 py-0.5 text-xs"
          :class="activeTab === tab.id ? 'bg-white/20' : 'bg-slate-200'"
        >
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- Notifications List -->
    <div class="space-y-3">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-8">
        <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
        <span class="ml-3 text-slate-600">Yuklanmoqda...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
        <p class="text-red-600">{{ error }}</p>
        <button @click="loadNotifications" class="mt-2 text-red-700 underline">Qayta urinish</button>
      </div>

      <template v-else>
        <TransitionGroup name="list">
          <div
            v-for="notification in filteredNotifications"
            :key="notification.id"
            class="flex gap-4 rounded-2xl border bg-white p-4 shadow-sm transition-all"
            :class="notification.read ? 'border-slate-200' : 'border-blue-200 bg-blue-50/50'"
          >
          <!-- Icon -->
          <div 
            class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl"
            :class="getNotificationIconBg(notification.type)"
          >
            <component 
              :is="getNotificationIcon(notification.type)" 
              :size="24" 
              :class="getNotificationIconColor(notification.type)"
            />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-medium text-slate-800">{{ notification.title }}</h3>
              <span class="flex-shrink-0 text-xs text-slate-400">{{ notification.time }}</span>
            </div>
            <p class="mt-1 text-sm text-slate-600">{{ notification.message }}</p>
            
            <!-- Action Button -->
            <div v-if="notification.action" class="mt-3">
              <button
                @click="handleAction(notification)"
                class="inline-flex items-center gap-1 rounded-lg bg-blue-500 px-3 py-1.5 text-sm text-white hover:bg-blue-600"
              >
                {{ notification.actionText }}
                <ArrowRight :size="14" />
              </button>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col gap-2">
            <button
              v-if="!notification.read"
              @click="markAsRead(notification.id)"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-blue-500"
              title="O'qilgan deb belgilash"
            >
              <Check :size="18" />
            </button>
            <button
              @click="deleteNotification(notification.id)"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
              title="O'chirish"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>
        </TransitionGroup>

        <!-- Empty State -->
        <div 
          v-if="filteredNotifications.length === 0"
          class="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white py-16"
        >
          <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
            <Bell :size="32" class="text-slate-400" />
          </div>
          <h3 class="text-lg font-medium text-slate-800">Xabarlar yo'q</h3>
          <p class="mt-1 text-slate-500">Yangi xabarlar shu yerda ko'rsatiladi</p>
        </div>
      </template>
    </div>

    <!-- Push Notification Settings -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100">
            <BellRing :size="20" class="text-indigo-600" />
          </div>
          <div>
            <h3 class="font-medium text-slate-800">Push bildirishnomalar</h3>
            <p class="text-sm text-slate-500">Yangi xabarlar haqida xabar oling</p>
          </div>
        </div>
        
        <label class="relative inline-flex cursor-pointer items-center">
          <input type="checkbox" v-model="pushEnabled" class="peer sr-only" />
          <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
        </label>
      </div>
      
      <div v-if="pushEnabled" class="mt-4 space-y-3 border-t border-slate-100 pt-4">
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">E'lonlar</span>
          <input type="checkbox" v-model="pushSettings.announcements" class="rounded border-slate-300" />
        </label>
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">Davomat ogohlantirishi</span>
          <input type="checkbox" v-model="pushSettings.attendance" class="rounded border-slate-300" />
        </label>
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">Jadval o'zgarishlari</span>
          <input type="checkbox" v-model="pushSettings.schedule" class="rounded border-slate-300" />
        </label>
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">Kutubxona eslatmalari</span>
          <input type="checkbox" v-model="pushSettings.library" class="rounded border-slate-300" />
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToastStore } from '@/stores/toast'
import api from '../../services/api'
import {
  Bell, BellRing, Check, CheckCheck, Trash2, ArrowRight,
  Megaphone, Calendar, AlertTriangle, BookOpen, Users, Info, Loader2
} from 'lucide-vue-next'

const router = useRouter()
const toast = useToastStore()

// State
const loading = ref(true)
const error = ref(null)
const activeTab = ref('all')
const pushEnabled = ref(true)
const pushSettings = ref({
  announcements: true,
  attendance: true,
  schedule: true,
  library: false
})

// Tabs
const tabs = computed(() => [
  { id: 'all', name: 'Barchasi', icon: Bell, count: unreadCount.value },
  { id: 'announcement', name: 'E\'lonlar', icon: Megaphone, count: getTypeCount('announcement') },
  { id: 'schedule', name: 'Jadval', icon: Calendar, count: getTypeCount('schedule') },
  { id: 'attendance', name: 'Davomat', icon: AlertTriangle, count: getTypeCount('attendance') },
  { id: 'library', name: 'Kutubxona', icon: BookOpen, count: getTypeCount('library') }
])

// Notifications
const notifications = ref([])

// Load notifications from API
const loadNotifications = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.getNotifications({ limit: 50 })
    notifications.value = (response.items || response || []).map(n => ({
      id: n.id,
      type: n.type || 'announcement',
      title: n.title,
      message: n.message || n.content,
      time: formatTime(n.created_at),
      read: n.is_read || n.read || false,
      action: n.action_type,
      actionText: n.action_text || getActionText(n.action_type)
    }))
  } catch (e) {
    console.error('Error loading notifications:', e)
    error.value = 'Bildirishnomalarni yuklashda xatolik'
  } finally {
    loading.value = false
  }
}

// Format time helper
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 60) return `${diffMins} daqiqa oldin`
  if (diffHours < 24) return `${diffHours} soat oldin`
  if (diffDays === 1) return 'Kecha'
  if (diffDays < 7) return `${diffDays} kun oldin`
  return date.toLocaleDateString('uz-UZ')
}

// Get action text
const getActionText = (actionType) => {
  const texts = {
    schedule: 'Jadvalga o\'tish',
    attendance: 'Davomatni ko\'rish',
    library: 'Kutubxonaga o\'tish'
  }
  return texts[actionType] || 'Ko\'rish'
}

// Computed
const filteredNotifications = computed(() => {
  if (activeTab.value === 'all') {
    return notifications.value
  }
  return notifications.value.filter(n => n.type === activeTab.value)
})

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

function getTypeCount(type) {
  return notifications.value.filter(n => n.type === type && !n.read).length
}

// Methods
function getNotificationIcon(type) {
  const icons = {
    announcement: Megaphone,
    schedule: Calendar,
    attendance: AlertTriangle,
    library: BookOpen,
    info: Info
  }
  return icons[type] || Bell
}

function getNotificationIconBg(type) {
  const colors = {
    announcement: 'bg-blue-100',
    schedule: 'bg-purple-100',
    attendance: 'bg-amber-100',
    library: 'bg-emerald-100',
    info: 'bg-slate-100'
  }
  return colors[type] || 'bg-slate-100'
}

function getNotificationIconColor(type) {
  const colors = {
    announcement: 'text-blue-600',
    schedule: 'text-purple-600',
    attendance: 'text-amber-600',
    library: 'text-emerald-600',
    info: 'text-slate-600'
  }
  return colors[type] || 'text-slate-600'
}

async function markAsRead(id) {
  try {
    await api.markNotificationRead(id)
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  } catch (e) {
    console.error('Error marking as read:', e)
    // Still update locally
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }
}

async function markAllAsRead() {
  try {
    await api.markAllNotificationsRead()
    notifications.value.forEach(n => n.read = true)
    toast.success('Barcha xabarlar o\'qilgan deb belgilandi')
  } catch (e) {
    console.error('Error marking all as read:', e)
    // Still update locally
    notifications.value.forEach(n => n.read = true)
    toast.success('Barcha xabarlar o\'qilgan deb belgilandi')
  }
}

async function deleteNotification(id) {
  try {
    await api.deleteNotification(id)
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
      toast.success('Xabar o\'chirildi')
    }
  } catch (e) {
    console.error('Error deleting notification:', e)
    toast.error('O\'chirishda xatolik')
  }
}

function handleAction(notification) {
  markAsRead(notification.id)
  
  const routes = {
    schedule: '/student/schedule',
    attendance: '/student/attendance',
    library: '/student/library'
  }
  
  if (routes[notification.action]) {
    router.push(routes[notification.action])
  }
}

// Initialize
onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
