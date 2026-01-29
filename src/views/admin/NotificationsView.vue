<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800">Bildirishnomalar</h1>
      <p class="text-slate-500">Barcha guruhlarga xabar yuborish</p>
    </div>

    <!-- Compose New -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <PenLine class="w-5 h-5 text-violet-500" />
        Yangi e'lon yozish
      </h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Sarlavha</label>
          <input 
            v-model="newNotification.title"
            type="text"
            placeholder="E'lon sarlavhasi..."
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Xabar matni</label>
          <textarea 
            v-model="newNotification.message"
            rows="4"
            placeholder="E'lon matnini yozing..."
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none resize-none"
          ></textarea>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Guruh</label>
            <select 
              v-model="newNotification.group"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            >
              <option value="">Barcha guruhlar</option>
              <option v-for="group in dataStore.groups" :key="group.id" :value="group.name">
                {{ group.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Turi</label>
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
        <span class="text-sm text-slate-500">{{ dataStore.notifications.length }} ta</span>
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

      <div v-if="dataStore.notifications.length === 0" class="p-12 text-center">
        <BellOff class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Hali e'lon yo'q</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, markRaw } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  PenLine,
  Send,
  Trash2,
  BellOff,
  CheckCircle,
  Info,
  AlertTriangle,
  AlertCircle
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

const newNotification = reactive({
  title: '',
  message: '',
  type: 'info',
  group: ''
})

const notificationTypes = [
  { value: 'info', label: 'Ma\'lumot', icon: markRaw(Info) },
  { value: 'warning', label: 'Ogohlantirish', icon: markRaw(AlertTriangle) },
  { value: 'urgent', label: 'Muhim', icon: markRaw(AlertCircle) }
]

const sortedNotifications = computed(() => {
  return [...dataStore.notifications].sort((a, b) => new Date(b.date) - new Date(a.date))
})

const canSend = computed(() => {
  return newNotification.title.trim() && newNotification.message.trim()
})

const sendNotification = () => {
  if (!canSend.value) return
  
  dataStore.addNotification({
    title: newNotification.title,
    message: newNotification.message,
    type: newNotification.type,
    group: newNotification.group || null,
    date: new Date().toISOString()
  })
  
  newNotification.title = ''
  newNotification.message = ''
  newNotification.type = 'info'
  newNotification.group = ''
  
  toast.success('Muvaffaqiyat', 'E\'lon muvaffaqiyatli yuborildi!')
}

const deleteNotification = (id) => {
  dataStore.deleteNotification(id)
  toast.success('O\'chirildi', 'E\'lon o\'chirildi')
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
    urgent: 'bg-rose-100 text-rose-600'
  }
  return classes[type] || classes.info
}

const getTypeIcon = (type) => {
  const icons = {
    info: markRaw(Info),
    warning: markRaw(AlertTriangle),
    urgent: markRaw(AlertCircle)
  }
  return icons[type] || icons.info
}
</script>
