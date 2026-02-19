<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('notifications.title') }}</h1>
      <p class="text-sm text-slate-500">{{ $t('notifications.manageNotifications') }}</p>
    </div>

    <!-- Main Tabs: E'lonlar vs Bildirishnomalar -->
    <div class="flex gap-2 overflow-x-auto pb-2">
      <button
        @click="activeSection = 'announcements'"
        class="flex items-center gap-2 whitespace-nowrap rounded-xl px-5 py-2.5 text-sm font-medium transition-all"
        :class="activeSection === 'announcements'
          ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/25'
          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
      >
        <Megaphone class="w-4 h-4" />
        {{ $t('notifications.announcementsTab') }}
        <span 
          v-if="announcements.length > 0"
          class="rounded-full px-2 py-0.5 text-xs"
          :class="activeSection === 'announcements' ? 'bg-white/20' : 'bg-slate-200'"
        >
          {{ announcements.length }}
        </span>
      </button>
      <button
        @click="activeSection = 'notifications'"
        class="flex items-center gap-2 whitespace-nowrap rounded-xl px-5 py-2.5 text-sm font-medium transition-all"
        :class="activeSection === 'notifications'
          ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25'
          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
      >
        <Bell class="w-4 h-4" />
        {{ $t('notifications.personalTab') }}
        <span 
          v-if="unreadPersonalCount > 0"
          class="rounded-full px-2 py-0.5 text-xs"
          :class="activeSection === 'notifications' ? 'bg-white/20' : 'bg-red-100 text-red-600'"
        >
          {{ unreadPersonalCount }}
        </span>
      </button>
    </div>

    <!-- ===================== ANNOUNCEMENTS SECTION ===================== -->
    <template v-if="activeSection === 'announcements'">
      <!-- Compose New Announcement -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <PenLine class="w-5 h-5 text-violet-500" />
          {{ $t('notifications.newMessage') }}
        </h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('notifications.subjectLabel') }}</label>
            <input 
              v-model="newNotification.title"
              type="text"
              :placeholder="$t('notifications.announcementTitlePlaceholder')"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('notifications.messageText') }}</label>
            <textarea 
              v-model="newNotification.message"
              rows="4"
              :placeholder="$t('notifications.announcementTextPlaceholder')"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none resize-none"
            ></textarea>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('notifications.selectGroup') }}</label>
              <select 
                v-model="newNotification.group"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
              >
                <option value="">{{ $t('notifications.allGroups') }}</option>
                <option v-for="group in dataStore.groups" :key="group.id" :value="group.name">
                  {{ group.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('notifications.type') }}</label>
              <div class="flex gap-2">
                <label 
                  v-for="type in announcementTypes" 
                  :key="type.value"
                  class="flex-1 flex items-center justify-center gap-2 px-3 py-3 rounded-xl border cursor-pointer transition-colors"
                  :class="newNotification.type === type.value 
                    ? 'border-violet-500 bg-violet-50 text-violet-700' 
                    : 'border-slate-200 hover:border-violet-200'"
                >
                  <input 
                    type="radio" 
                    :value="type.value" 
                    v-model="newNotification.type"
                    class="hidden"
                  />
                  <component :is="type.icon" class="w-4 h-4" />
                  <span class="text-sm">{{ type.label }}</span>
                </label>
              </div>
            </div>
          </div>
          <div class="flex justify-end">
            <button 
              @click="sendNotification"
              :disabled="!canSend"
              class="px-6 py-3 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send class="w-4 h-4" />
              {{ $t('notifications.send') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Announcements List -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="p-6 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Megaphone class="w-5 h-5 text-violet-500" />
            {{ $t('notifications.allAnnouncements') }}
          </h2>
          <span class="text-sm text-slate-500">{{ announcements.length }} ta</span>
        </div>

        <div class="divide-y divide-slate-100">
          <div 
            v-for="notification in sortedAnnouncements" 
            :key="notification.id"
            class="overflow-hidden transition-all"
          >
            <!-- Clickable Header -->
            <div
              @click="expandedAnnouncementId = expandedAnnouncementId === notification.id ? null : notification.id"
              class="p-4 flex items-start gap-4 cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                :class="getTypeClass(notification.type)"
              >
                <component :is="getTypeIcon(notification.type)" class="w-5 h-5" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <h3 class="font-semibold text-slate-800">{{ notification.title }}</h3>
                  <span 
                    v-if="notification.group"
                    class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-xs"
                  >
                    {{ notification.group }}
                  </span>
                  <span 
                    v-else
                    class="px-2 py-0.5 bg-violet-100 text-violet-600 rounded text-xs"
                  >
                    {{ $t('notifications.toEveryone') }}
                  </span>
                </div>
                <p v-if="expandedAnnouncementId !== notification.id" class="text-sm text-slate-500 mt-1 line-clamp-1">{{ notification.message }}</p>
                <p class="text-xs text-slate-400 mt-1">{{ formatDate(notification.date) }}</p>
              </div>
              <ChevronDown
                :size="16"
                class="text-slate-400 transition-transform duration-200 flex-shrink-0 mt-2"
                :class="{ 'rotate-180': expandedAnnouncementId === notification.id }"
              />
            </div>
            <!-- Expandable content -->
            <Transition name="expand">
              <div v-if="expandedAnnouncementId === notification.id" class="border-t border-slate-100">
                <div class="px-4 pb-4 pt-3 pl-[72px]">
                  <p class="text-sm text-slate-700 whitespace-pre-line leading-relaxed">{{ notification.message }}</p>
                  <div class="flex items-center gap-2 mt-3">
                    <button 
                      @click.stop="deleteNotification(notification.id, 'announcement')"
                      class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 transition-colors"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                      {{ $t('common.delete') }}
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <div v-if="announcements.length === 0" class="p-12 text-center">
          <Megaphone class="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p class="text-slate-500">{{ $t('notifications.noAnnouncements') }}</p>
        </div>
      </div>
    </template>

    <!-- ===================== PERSONAL NOTIFICATIONS SECTION ===================== -->
    <template v-if="activeSection === 'notifications'">
      <!-- Filter Tabs for notification types -->
      <div class="flex gap-2 overflow-x-auto pb-2">
        <button
          v-for="tab in notifFilterTabs"
          :key="tab.id"
          @click="notifFilter = tab.id"
          class="flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-2 text-sm font-medium transition-all"
          :class="notifFilter === tab.id 
            ? 'bg-blue-500 text-white' 
            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          {{ tab.name }}
          <span 
            v-if="tab.count > 0"
            class="rounded-full px-2 py-0.5 text-xs"
            :class="notifFilter === tab.id ? 'bg-white/20' : 'bg-slate-200'"
          >
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- Notifications List -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="p-6 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Bell class="w-5 h-5 text-blue-500" />
            {{ $t('notifications.personalNotifications') }}
          </h2>
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">{{ filteredPersonalNotifications.length }} ta</span>
            <button 
              v-if="personalNotifications.some(n => !n.isRead)"
              @click="markAllAsRead"
              class="text-sm text-blue-500 hover:text-blue-600 flex items-center gap-1"
            >
              <CheckCheck class="w-4 h-4" />
              {{ $t('notifications.markAllRead') }}
            </button>
          </div>
        </div>

        <div class="divide-y divide-slate-100">
          <div 
            v-for="notification in filteredPersonalNotifications" 
            :key="notification.id"
            class="overflow-hidden transition-all"
            :class="notification.isRead ? '' : 'bg-blue-50/50'"
          >
            <!-- Clickable Header -->
            <div
              @click="togglePersonalNotif(notification)"
              class="p-4 flex items-start gap-4 cursor-pointer hover:bg-slate-50/50 transition-colors"
            >
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                :class="getTypeClass(notification.type)"
              >
                <component :is="getTypeIcon(notification.type)" class="w-5 h-5" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <h3 class="font-semibold text-slate-800">{{ notification.title }}</h3>
                  <span 
                    class="px-2 py-0.5 rounded text-xs"
                    :class="getTypeBadgeClass(notification.type)"
                  >
                    {{ getTypeLabel(notification.type) }}
                  </span>
                  <span v-if="!notification.isRead" class="w-2 h-2 rounded-full bg-blue-500"></span>
                </div>
                <p v-if="expandedPersonalId !== notification.id" class="text-sm text-slate-500 mt-1 line-clamp-1">{{ notification.message }}</p>
                <div class="flex items-center gap-3 mt-1">
                  <p class="text-xs text-slate-400">{{ formatDate(notification.date) }}</p>
                  <span v-if="notification.senderName" class="text-xs text-slate-400">
                    {{ $t('notifications.from') }}: {{ notification.senderName }}
                  </span>
                </div>
              </div>
              <ChevronDown
                :size="16"
                class="text-slate-400 transition-transform duration-200 flex-shrink-0 mt-2"
                :class="{ 'rotate-180': expandedPersonalId === notification.id }"
              />
            </div>
            <!-- Expandable content -->
            <Transition name="expand">
              <div v-if="expandedPersonalId === notification.id" class="border-t border-slate-100">
                <div class="px-4 pb-4 pt-3 pl-[72px]">
                  <p class="text-sm text-slate-700 whitespace-pre-line leading-relaxed">{{ notification.message }}</p>
                  <div class="flex items-center gap-2 mt-3">
                    <button
                      v-if="!notification.isRead"
                      @click.stop="markAsRead(notification.id)"
                      class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors"
                    >
                      <Check class="w-3.5 h-3.5" />
                      {{ $t('notifications.markAsRead') }}
                    </button>
                    <button 
                      @click.stop="deleteNotification(notification.id, 'personal')"
                      class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 transition-colors"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                      {{ $t('common.delete') }}
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <div v-if="filteredPersonalNotifications.length === 0" class="p-12 text-center">
          <BellOff class="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p class="text-slate-500">{{ $t('notifications.noPersonalNotifications') }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
/**
 * Admin Notifications - Separated Announcements & Personal Notifications
 * E'lonlar va bildirishnomalar alohida boshqariladi
 */
import {
    AlertCircle,
    AlertTriangle,
    Bell,
    BellOff,
    Check,
    CheckCheck,
    ChevronDown,
    CreditCard,
    Info,
    Megaphone,
    PenLine,
    Send,
    ShieldCheck,
    Trash2
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const dataStore = useDataStore()
const toast = useToastStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const sending = ref(false)
const activeSection = ref('announcements')
const notifFilter = ref('all')
const announcements = ref([])
const personalNotifications = ref([])
const expandedAnnouncementId = ref(null)
const expandedPersonalId = ref(null)

const newNotification = reactive({
  title: '',
  message: '',
  type: 'info',
  group: ''
})

// Announcement types (for compose form)
const announcementTypes = [
  { value: 'info', label: t('notifications.info'), icon: markRaw(Info) },
  { value: 'warning', label: t('notifications.warning'), icon: markRaw(AlertTriangle) },
  { value: 'announcement', label: t('notifications.announcements'), icon: markRaw(AlertCircle) }
]

// Personal notification type = everything except announcement-like broadcasts
const announcementNotifTypes = ['announcement', 'info', 'warning']
// Personal types: payment, success, error, system, schedule, attendance, etc.

// Notification filter tabs
const notifFilterTabs = computed(() => [
  { id: 'all', name: t('common.all'), icon: markRaw(Bell), count: personalNotifications.value.filter(n => !n.isRead).length },
  { id: 'payment', name: t('notifications.payments'), icon: markRaw(CreditCard), count: personalNotifications.value.filter(n => n.type === 'payment' && !n.isRead).length },
  { id: 'success', name: t('notifications.success'), icon: markRaw(ShieldCheck), count: personalNotifications.value.filter(n => n.type === 'success' && !n.isRead).length },
  { id: 'system', name: t('notifications.systemNotifs'), icon: markRaw(Info), count: personalNotifications.value.filter(n => ['system', 'error'].includes(n.type) && !n.isRead).length }
])

// Load all notifications and separate them
async function loadNotifications() {
  loading.value = true
  try {
    // Load groups if not loaded
    if (!dataStore.groups.length) {
      await dataStore.fetchGroups()
    }
    
    // Load ALL notifications from API
    try {
      const response = await api.getNotifications({ page_size: 200 })
      if (response?.items) {
        const allNotifs = response.items.map(n => ({
          id: n.id,
          title: n.title,
          message: n.message || n.content,
          type: n.type || 'info',
          group: n.group_name || null,
          date: n.created_at,
          senderName: n.sender_name || null,
          isRead: n.is_read || false,
          senderId: n.sender_id || null
        }))
        
        // Separate: announcements are broadcast messages (type = announcement, info, warning) 
        // that have sender_id (meaning admin sent them) or group target
        // Personal notifications are system-generated (payment, success, error, etc.)
        announcements.value = allNotifs.filter(n => {
          // Announcement types that admin broadcasts
          return ['announcement'].includes(n.type) || 
                 // Also include info/warning that were sent by someone (broadcast)
                 (['info', 'warning'].includes(n.type) && n.senderId)
        })
        
        personalNotifications.value = allNotifs.filter(n => {
          // Everything that's NOT an announcement broadcast
          return !(['announcement'].includes(n.type) || 
                   (['info', 'warning'].includes(n.type) && n.senderId))
        })
      }
    } catch (e) {
      console.log('Notifications API error:', e)
      announcements.value = []
      personalNotifications.value = []
    }
  } catch (err) {
    console.error('Load notifications error:', err)
  } finally {
    loading.value = false
  }
}

// Computed
const sortedAnnouncements = computed(() => {
  return [...announcements.value].sort((a, b) => new Date(b.date) - new Date(a.date))
})

const filteredPersonalNotifications = computed(() => {
  let notifs = [...personalNotifications.value]
  if (notifFilter.value !== 'all') {
    if (notifFilter.value === 'system') {
      notifs = notifs.filter(n => ['system', 'error'].includes(n.type))
    } else {
      notifs = notifs.filter(n => n.type === notifFilter.value)
    }
  }
  return notifs.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const unreadPersonalCount = computed(() => {
  return personalNotifications.value.filter(n => !n.isRead).length
})

const canSend = computed(() => {
  return newNotification.title.trim() && newNotification.message.trim()
})

const sendNotification = async () => {
  if (!canSend.value || sending.value) return
  
  sending.value = true
  try {
    if (newNotification.group) {
      const group = dataStore.groups.find(g => g.name === newNotification.group)
      if (group) {
        await api.broadcastNotification({
          title: newNotification.title,
          message: newNotification.message,
          type: newNotification.type,
          target_group_id: group.id
        })
      }
    } else {
      await api.broadcastNotification({
        title: newNotification.title,
        message: newNotification.message,
        type: newNotification.type,
        target_role: 'all'
      })
    }
    
    await loadNotifications()
    
    newNotification.title = ''
    newNotification.message = ''
    newNotification.type = 'info'
    newNotification.group = ''
    
    toast.success(t('notifications.sentSuccess'))
  } catch (err) {
    console.error('Send notification error:', err)
    toast.error(t('notifications.sendError') + ': ' + (err.message || ''))
  } finally {
    sending.value = false
  }
}

const deleteNotification = async (id, source) => {
  try {
    await api.deleteNotification(id)
    if (source === 'announcement') {
      const index = announcements.value.findIndex(n => n.id === id)
      if (index !== -1) announcements.value.splice(index, 1)
    } else {
      const index = personalNotifications.value.findIndex(n => n.id === id)
      if (index !== -1) personalNotifications.value.splice(index, 1)
    }
    toast.success(t('notifications.messageDeleted'))
  } catch (err) {
    console.error('Delete notification error:', err)
    toast.error(t('notifications.deleteError'))
  }
}

const markAsRead = async (id) => {
  try {
    await api.markNotificationRead(id)
    const notif = personalNotifications.value.find(n => n.id === id)
    if (notif) notif.isRead = true
  } catch (err) {
    console.error('Mark as read error:', err)
  }
}

function togglePersonalNotif(notification) {
  if (expandedPersonalId.value === notification.id) {
    expandedPersonalId.value = null
  } else {
    expandedPersonalId.value = notification.id
    if (!notification.isRead) {
      markAsRead(notification.id)
    }
  }
}

const markAllAsRead = async () => {
  try {
    // Mark all personal notifications as read
    const unread = personalNotifications.value.filter(n => !n.isRead)
    for (const n of unread) {
      await api.markNotificationRead(n.id)
      n.isRead = true
    }
    toast.success(t('notifications.allMarkedRead'))
  } catch (err) {
    console.error('Mark all read error:', err)
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTypeClass = (type) => {
  const classes = {
    info: 'bg-blue-100 text-blue-600',
    warning: 'bg-amber-100 text-amber-600',
    announcement: 'bg-violet-100 text-violet-600',
    error: 'bg-rose-100 text-rose-600',
    success: 'bg-emerald-100 text-emerald-600',
    payment: 'bg-green-100 text-green-600',
    system: 'bg-slate-100 text-slate-600',
    schedule: 'bg-purple-100 text-purple-600',
    attendance: 'bg-orange-100 text-orange-600'
  }
  return classes[type] || classes.info
}

const getTypeIcon = (type) => {
  const icons = {
    info: markRaw(Info),
    warning: markRaw(AlertTriangle),
    announcement: markRaw(Megaphone),
    error: markRaw(AlertCircle),
    success: markRaw(ShieldCheck),
    payment: markRaw(CreditCard),
    system: markRaw(Info),
    schedule: markRaw(Bell),
    attendance: markRaw(AlertTriangle)
  }
  return icons[type] || icons.info
}

const getTypeBadgeClass = (type) => {
  const classes = {
    info: 'bg-blue-100 text-blue-600',
    warning: 'bg-amber-100 text-amber-600',
    error: 'bg-rose-100 text-rose-600',
    success: 'bg-emerald-100 text-emerald-600',
    payment: 'bg-green-100 text-green-600',
    system: 'bg-slate-100 text-slate-600',
    schedule: 'bg-purple-100 text-purple-600',
    attendance: 'bg-orange-100 text-orange-600'
  }
  return classes[type] || 'bg-slate-100 text-slate-600'
}

const getTypeLabel = (type) => {
  const labels = {
    info: t('notifications.info'),
    warning: t('notifications.warning'),
    error: t('notifications.alert'),
    success: t('notifications.success'),
    payment: t('notifications.payments'),
    system: t('notifications.systemNotifs'),
    schedule: t('notifications.scheduleChanges'),
    attendance: t('notifications.attendanceWarning')
  }
  return labels[type] || type
}

// Initialize
onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
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
}
</style>
