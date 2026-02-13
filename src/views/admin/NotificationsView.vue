<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('notifications.title') }}</h1>
      <p class="text-sm text-slate-500">{{ $t('notifications.broadcast') }}</p>
    </div>

    <!-- Compose New -->
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
            placeholder="E'lon sarlavhasi..."
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('notifications.messageText') }}</label>
          <textarea 
            v-model="newNotification.message"
            rows="4"
            placeholder="E'lon matnini yozing..."
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
                v-for="type in notificationTypes" 
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
            Yuborish
          </button>
        </div>
      </div>
    </div>

    <!-- All Notifications -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800">Barcha e'lonlar</h2>
        <span class="text-sm text-slate-500">{{ notifications.length }} ta</span>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="notification in sortedNotifications" 
          :key="notification.id"
          class="p-4 flex items-start gap-4"
        >
          <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="getTypeClass(notification.type)"
          >
            <component :is="getTypeIcon(notification.type)" class="w-5 h-5" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
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
                Hammaga
              </span>
            </div>
            <p class="text-sm text-slate-600 mt-1">{{ notification.message }}</p>
            <p class="text-xs text-slate-400 mt-2">{{ formatDate(notification.date) }}</p>
          </div>
          <button 
            @click="deleteNotification(notification.id)"
            class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div v-if="notifications.length === 0" class="p-12 text-center">
        <BellOff class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Hali e'lon yo'q</p>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Admin Notifications - Real API Integration
 * E'lonlar yuborish va boshqarish
 */
import {
    AlertCircle,
    AlertTriangle,
    BellOff,
    Info,
    PenLine,
    Send,
    Trash2
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'

const dataStore = useDataStore()
const toast = useToastStore()

// State
const loading = ref(true)
const sending = ref(false)
const notifications = ref([])

const newNotification = reactive({
  title: '',
  message: '',
  type: 'info',
  group: ''
})

const notificationTypes = [
  { value: 'info', label: 'Ma\'lumot', icon: markRaw(Info) },
  { value: 'warning', label: 'Ogohlantirish', icon: markRaw(AlertTriangle) },
  { value: 'announcement', label: 'E\'lon', icon: markRaw(AlertCircle) }
]

// Load notifications from API
async function loadNotifications() {
  loading.value = true
  try {
    // Load groups if not loaded
    if (!dataStore.groups.length) {
      await dataStore.fetchGroups()
    }
    
    // Load notifications from API
    try {
      const response = await api.getNotifications({ page_size: 100 })
      if (response?.items) {
        notifications.value = response.items.map(n => ({
          id: n.id,
          title: n.title,
          message: n.message || n.content,
          type: n.type || 'info',
          group: n.group_name || null,
          date: n.created_at,
          senderName: n.sender_name || null
        }))
      }
    } catch (e) {
      console.log('Notifications API error:', e)
      notifications.value = []
    }
  } catch (err) {
    console.error('Load notifications error:', err)
  } finally {
    loading.value = false
  }
}

const sortedNotifications = computed(() => {
  return [...notifications.value].sort((a, b) => new Date(b.date) - new Date(a.date))
})

const canSend = computed(() => {
  return newNotification.title.trim() && newNotification.message.trim()
})

const sendNotification = async () => {
  if (!canSend.value || sending.value) return
  
  sending.value = true
  try {
    if (newNotification.group) {
      // Send to specific group - find group and use broadcast
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
      // Broadcast to all users
      await api.broadcastNotification({
        title: newNotification.title,
        message: newNotification.message,
        type: newNotification.type,
        target_role: 'all'
      })
    }
    
    // Refresh notifications list
    await loadNotifications()
    
    // Reset form
    newNotification.title = ''
    newNotification.message = ''
    newNotification.type = 'info'
    newNotification.group = ''
    
    toast.success('E\'lon muvaffaqiyatli yuborildi!')
  } catch (err) {
    console.error('Send notification error:', err)
    toast.error('Yuborishda xatolik: ' + (err.message || 'Noma\'lum xatolik'))
  } finally {
    sending.value = false
  }
}

const deleteNotification = async (id) => {
  try {
    await api.deleteNotification(id)
    // Remove from local list
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
    toast.success('E\'lon o\'chirildi')
  } catch (err) {
    console.error('Delete notification error:', err)
    toast.error('O\'chirishda xatolik')
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
    success: 'bg-emerald-100 text-emerald-600'
  }
  return classes[type] || classes.info
}

const getTypeIcon = (type) => {
  const icons = {
    info: markRaw(Info),
    warning: markRaw(AlertTriangle),
    announcement: markRaw(AlertCircle),
    error: markRaw(AlertCircle),
    success: markRaw(Info)
  }
  return icons[type] || icons.info
}

// Initialize
onMounted(() => {
  loadNotifications()
})
</script>
