<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('notifications.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('notifications.title') }}</p>
      </div>
      
      <div class="flex items-center gap-3">
        <button
          @click="markAllAsRead"
          class="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-slate-600 hover:bg-slate-50"
        >
          <CheckCheck :size="18" />
          <span>{{ $t('notifications.markAllRead') }}</span>
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
        <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
        <p class="text-red-600">{{ error }}</p>
        <button @click="loadNotifications" class="mt-2 text-red-700 underline">{{ $t('common.retry') }}</button>
      </div>

      <template v-else>
        <TransitionGroup name="list">
          <div
            v-for="notification in filteredNotifications"
            :key="notification.id"
            class="rounded-2xl border bg-white shadow-sm transition-all overflow-hidden"
            :class="notification.isRead ? 'border-slate-200' : 'border-blue-200 bg-blue-50/50'"
          >
          <!-- Clickable Header -->
          <div
            @click="toggleExpand(notification)"
            class="flex gap-4 p-4 cursor-pointer hover:bg-slate-50/50 transition-colors"
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

            <!-- Title Row -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <h3 class="font-medium text-slate-800">{{ notification.title }}</h3>
                <span class="flex-shrink-0 text-xs text-slate-400">{{ notification.time || formatTime(notification.createdAt) }}</span>
              </div>
              <p class="mt-1 text-sm text-slate-500 line-clamp-1" v-if="expandedId !== notification.id">{{ notification.message }}</p>
            </div>

            <!-- Expand Arrow -->
            <div class="flex items-center flex-shrink-0">
              <ChevronDown
                :size="18"
                class="text-slate-400 transition-transform duration-200"
                :class="{ 'rotate-180': expandedId === notification.id }"
              />
            </div>
          </div>

          <!-- Expandable Content -->
          <Transition name="expand">
            <div v-if="expandedId === notification.id" class="px-4 pb-4 border-t border-slate-100">
              <div class="pt-3 pl-16">
                <p class="text-sm text-slate-600 whitespace-pre-line">{{ notification.message }}</p>
                
                <!-- Action Button -->
                <div v-if="notification.actionUrl" class="mt-3">
                  <button
                    @click.stop="handleAction(notification)"
                    class="inline-flex items-center gap-1 rounded-lg bg-blue-500 px-3 py-1.5 text-sm text-white hover:bg-blue-600"
                  >
                    {{ notification.actionText || $t('common.view') }}
                    <ArrowRight :size="14" />
                  </button>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2 mt-3">
                  <button
                    v-if="!notification.isRead"
                    @click.stop="markAsRead(notification.id)"
                    class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors"
                  >
                    <Check :size="14" />
                    {{ $t('notifications.markAsRead') }}
                  </button>
                  <button
                    @click.stop="deleteNotification(notification.id)"
                    class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 transition-colors"
                  >
                    <Trash2 :size="14" />
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </div>
            </div>
          </Transition>
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
          <h3 class="text-lg font-medium text-slate-800">{{ $t('notifications.noNotifications') }}</h3>
          <p class="mt-1 text-slate-500">{{ $t('common.noData') }}</p>
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
            <h3 class="font-medium text-slate-800">{{ $t('settings.pushNotifications') }}</h3>
            <p class="text-sm text-slate-500">{{ $t('settings.pushDesc') }}</p>
          </div>
        </div>
        
        <label class="relative inline-flex cursor-pointer items-center">
          <input type="checkbox" v-model="pushEnabled" class="peer sr-only" />
          <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
        </label>
      </div>
      
      <div v-if="pushEnabled" class="mt-4 space-y-3 border-t border-slate-100 pt-4">
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">{{ $t('notifications.announcements') }}</span>
          <input type="checkbox" v-model="pushSettings.announcements" class="rounded border-slate-300" />
        </label>
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">{{ $t('notifications.attendanceWarning') }}</span>
          <input type="checkbox" v-model="pushSettings.attendance" class="rounded border-slate-300" />
        </label>
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">{{ $t('notifications.scheduleChanges') }}</span>
          <input type="checkbox" v-model="pushSettings.schedule" class="rounded border-slate-300" />
        </label>
        <label class="flex items-center justify-between">
          <span class="text-sm text-slate-600">{{ $t('notifications.libraryReminders') }}</span>
          <input type="checkbox" v-model="pushSettings.library" class="rounded border-slate-300" />
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDataStore } from '@/stores/data'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    AlertTriangle,
    ArrowRight,
    Bell, BellRing,
    BookOpen,
    Calendar,
    Check, CheckCheck,
    ChevronDown,
    Info, Loader2,
    Megaphone,
    Trash2
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()
const toast = useToastStore()
const dataStore = useDataStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const error = ref(null)
const activeTab = ref('all')
const expandedId = ref(null)
const pushEnabled = ref(true)
const pushSettings = ref({
  announcements: true,
  attendance: true,
  schedule: true,
  library: false
})

// Tabs
const tabs = computed(() => [
  { id: 'all', name: t('common.all'), icon: Bell, count: unreadCount.value },
  { id: 'announcement', name: t('notifications.announcements'), icon: Megaphone, count: getTypeCount('announcement') },
  { id: 'schedule', name: t('notifications.scheduleChanges'), icon: Calendar, count: getTypeCount('schedule') },
  { id: 'attendance', name: t('notifications.attendanceWarning'), icon: AlertTriangle, count: getTypeCount('attendance') },
  { id: 'info', name: t('notifications.info'), icon: Info, count: getTypeCount('info') }
])

// Use store notifications
const notifications = computed(() => dataStore.notifications)

// Load notifications from API
const loadNotifications = async () => {
  loading.value = true
  error.value = null
  
  try {
    await dataStore.fetchNotifications({ page_size: 100 })
  } catch (e) {
    console.error('Error loading notifications:', e)
    error.value = t('notifications.loadError')
  } finally {
    loading.value = false
  }
}

// Computed
const filteredNotifications = computed(() => {
  if (activeTab.value === 'all') {
    return notifications.value
  }
  return notifications.value.filter(n => n.type === activeTab.value)
})

const unreadCount = computed(() => {
  return dataStore.unreadCount
})

function getTypeCount(type) {
  return notifications.value.filter(n => n.type === type && !n.isRead && !n.read).length
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
  
  if (diffMins < 60) return t('notifications.minutesAgo', { min: diffMins })
  if (diffHours < 24) return t('notifications.hoursAgo', { hours: diffHours })
  if (diffDays === 1) return t('notifications.daysAgo', { days: 1 })
  if (diffDays < 7) return t('notifications.daysAgo', { days: diffDays })
  return date.toLocaleDateString('uz-UZ')
}

// Toggle expand
function toggleExpand(notification) {
  if (expandedId.value === notification.id) {
    expandedId.value = null
  } else {
    expandedId.value = notification.id
    if (!notification.isRead && !notification.read) {
      markAsRead(notification.id)
    }
  }
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
    await dataStore.markNotificationRead(id)
  } catch (e) {
    console.error('Error marking as read:', e)
  }
}

async function markAllAsRead() {
  try {
    await dataStore.markAllNotificationsRead()
    toast.success(t('notifications.allMarkedRead'))
  } catch (e) {
    console.error('Error marking all as read:', e)
    toast.success(t('notifications.allMarkedRead'))
  }
}

async function deleteNotification(id) {
  try {
    await api.deleteNotification(id)
    // Refresh from store
    await dataStore.fetchNotifications({ page_size: 100 })
    toast.success(t('notifications.messageDeleted'))
  } catch (e) {
    console.error('Error deleting notification:', e)
    toast.error(t('notifications.deleteError'))
  }
}

function handleAction(notification) {
  markAsRead(notification.id)
  
  if (notification.actionUrl) {
    router.push(notification.actionUrl)
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
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  max-height: 500px;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
