<template>
  <div class="relative">
    <!-- Trigger Button -->
    <button 
      @click="isOpen = !isOpen"
      class="relative p-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition-all duration-200 group"
    >
      <Bell class="w-5 h-5 group-hover:scale-110 transition-transform" />
      <span 
        v-if="unreadCount > 0"
        class="absolute top-1.5 right-1.5 min-w-[18px] h-[18px] flex items-center justify-center px-1 bg-rose-500 text-white text-xs font-bold rounded-full ring-2 ring-white"
      >
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>

    <!-- Dropdown -->
    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-96 bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200/60 overflow-hidden z-50"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
          <h3 class="font-semibold text-slate-800">Bildirishnomalar</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-400">{{ unreadCount }} ta yangi</span>
            <button 
              v-if="unreadCount > 0"
              @click="markAllAsRead"
              class="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
            >
              Barchasini o'qilgan deb belgilash
            </button>
          </div>
        </div>

        <!-- Notifications List -->
        <div class="max-h-96 overflow-y-auto divide-y divide-slate-100">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            @click="handleNotificationClick(notification)"
            class="flex items-start gap-3 p-4 hover:bg-slate-50 cursor-pointer transition-colors"
            :class="{ 'bg-blue-50/50': !notification.read }"
          >
            <!-- Icon -->
            <div 
              class="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center"
              :class="getTypeClass(notification.type)"
            >
              <component :is="getTypeIcon(notification.type)" class="w-5 h-5" />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <p class="text-sm font-medium text-slate-800 line-clamp-1">
                  {{ notification.title }}
                </p>
                <span class="flex-shrink-0 text-xs text-slate-400">
                  {{ formatTime(notification.createdAt) }}
                </span>
              </div>
              <p class="mt-0.5 text-sm text-slate-500 line-clamp-2">
                {{ notification.message }}
              </p>
              <div v-if="notification.action" class="mt-2">
                <button 
                  class="text-xs font-medium text-emerald-600 hover:text-emerald-700"
                  @click.stop="handleAction(notification)"
                >
                  {{ notification.action.label }} →
                </button>
              </div>
            </div>

            <!-- Unread indicator -->
            <div 
              v-if="!notification.read"
              class="flex-shrink-0 w-2 h-2 mt-2 bg-blue-500 rounded-full"
            ></div>
          </div>

          <!-- Empty State -->
          <div v-if="notifications.length === 0" class="py-12 text-center">
            <BellOff class="w-12 h-12 mx-auto text-slate-300 mb-3" />
            <p class="text-slate-500">Bildirishnomalar yo'q</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-3 border-t border-slate-100 bg-slate-50/50">
          <router-link
            :to="notificationsRoute"
            class="block w-full py-2 text-center text-sm font-medium text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition-colors"
            @click="isOpen = false"
          >
            Barcha bildirishnomalarni ko'rish
          </router-link>
        </div>
      </div>
    </Transition>

    <!-- Click outside to close -->
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-40" 
      @click="isOpen = false"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import {
  Bell, BellOff, Info, AlertTriangle, CheckCircle, AlertOctagon,
  Calendar, FileText, Users, TrendingUp
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const isOpen = ref(false)
const notifications = ref([])
const loading = ref(false)

// Load notifications from API
const loadNotifications = async () => {
  loading.value = true
  try {
    const response = await api.getNotifications({ limit: 10 })
    if (response?.items) {
      notifications.value = response.items.map(n => ({
        id: n.id,
        type: n.type || 'info',
        title: n.title,
        message: n.message,
        createdAt: new Date(n.created_at),
        read: n.read || false
      }))
    } else if (Array.isArray(response)) {
      notifications.value = response.slice(0, 10).map(n => ({
        id: n.id,
        type: n.type || 'info',
        title: n.title,
        message: n.message,
        createdAt: new Date(n.created_at),
        read: n.read || false
      }))
    }
  } catch (err) {
    console.error('Error loading notifications:', err)
    // Keep empty if API fails
  } finally {
    loading.value = false
  }
}

// Load on mount and when dropdown opens
onMounted(loadNotifications)
watch(isOpen, (newVal) => {
  if (newVal) loadNotifications()
})

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const notificationsRoute = computed(() => {
  if (authStore.isStudent) return '/student/notifications'
  if (authStore.isLeader) return '/leader/notifications'
  if (authStore.isAdmin) return '/admin/notifications'
  return '/super/notifications'
})

async function markAllAsRead() {
  try {
    await api.markAllNotificationsRead()
    notifications.value.forEach(n => n.read = true)
  } catch (err) {
    console.error('Error marking all as read:', err)
  }
}

async function handleNotificationClick(notification) {
  try {
    await api.markNotificationRead(notification.id)
    notification.read = true
  } catch (err) {
    console.error('Error marking as read:', err)
  }
  if (notification.action?.route) {
    router.push(notification.action.route)
    isOpen.value = false
  }
}

function handleAction(notification) {
  if (notification.action?.route) {
    router.push(notification.action.route)
    isOpen.value = false
  }
}

function getTypeClass(type) {
  const classes = {
    info: 'bg-blue-100 text-blue-600',
    warning: 'bg-yellow-100 text-yellow-600',
    success: 'bg-green-100 text-green-600',
    urgent: 'bg-red-100 text-red-600'
  }
  return classes[type] || classes.info
}

function getTypeIcon(type) {
  const icons = {
    info: Info,
    warning: AlertTriangle,
    success: CheckCircle,
    urgent: AlertOctagon
  }
  return icons[type] || Info
}

function formatTime(date) {
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  if (diff < 60000) return 'Hozirgina'
  if (diff < 3600000) return Math.floor(diff / 60000) + ' daqiqa oldin'
  if (diff < 86400000) return Math.floor(diff / 3600000) + ' soat oldin'
  if (diff < 604800000) return Math.floor(diff / 86400000) + ' kun oldin'
  return d.toLocaleDateString('uz-UZ')
}
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
</style>
