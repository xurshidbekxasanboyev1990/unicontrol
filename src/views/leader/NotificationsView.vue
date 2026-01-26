<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 md:text-3xl">Bildirishnomalar</h1>
        <p class="text-slate-500">Talabalar uchun xabar yuborish va faoliyat tarixi</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="activeTab = 'compose'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'compose' ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
        >
          <PenLine :size="16" class="inline mr-1" />
          Xabar yozish
        </button>
        <button
          @click="activeTab = 'history'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'history' ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
        >
          <History :size="16" class="inline mr-1" />
          Tarix
        </button>
        <button
          @click="activeTab = 'activity'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'activity' ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
        >
          <Activity :size="16" class="inline mr-1" />
          Faoliyat
        </button>
      </div>
    </div>

    <!-- Compose Tab -->
    <div v-if="activeTab === 'compose'" class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Compose Form -->
      <div class="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-800">
          <PenLine :size="20" class="text-emerald-500" />
          Yangi xabar yozish
        </h2>

        <div class="space-y-4">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Sarlavha</label>
            <input 
              v-model="newNotification.title"
              type="text"
              placeholder="Xabar sarlavhasi..."
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Qabul qiluvchilar</label>
            <div class="flex flex-wrap gap-2">
              <button
                @click="selectAllStudents"
                class="rounded-lg px-3 py-1.5 text-sm transition-all"
                :class="allStudentsSelected ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
              >
                <Users :size="14" class="inline mr-1" />
                Barchasi
              </button>
              <button
                v-for="student in groupStudents"
                :key="student.id"
                @click="toggleRecipient(student.id)"
                class="rounded-lg px-3 py-1.5 text-sm transition-all"
                :class="selectedRecipients.includes(student.id) 
                  ? 'bg-emerald-500 text-white' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
              >
                {{ student.name.split(' ')[0] }}
              </button>
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Xabar matni</label>
            <textarea 
              v-model="newNotification.message"
              rows="5"
              placeholder="Xabar matnini yozing..."
              class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none resize-none"
            ></textarea>
            <div class="mt-1 text-right text-xs text-slate-500">{{ newNotification.message.length }}/500</div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-300">Xabar turi</label>
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <button
                v-for="type in notificationTypes"
                :key="type.value"
                @click="newNotification.type = type.value"
                class="flex items-center justify-center gap-2 rounded-lg border p-3 transition-all"
                :class="newNotification.type === type.value 
                  ? 'border-blue-500 bg-blue-500/10 ' + type.textColor
                  : 'border-slate-600 text-slate-400 hover:border-slate-500'"
              >
                <component :is="type.icon" :size="18" />
                <span class="text-sm">{{ type.label }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Muhimlik darajasi</label>
            <div class="flex gap-2">
              <button
                v-for="priority in priorities"
                :key="priority.value"
                @click="newNotification.priority = priority.value"
                class="flex-1 rounded-lg border p-2 text-center text-sm transition-all"
                :class="newNotification.priority === priority.value 
                  ? 'border-' + priority.color + '-500 bg-' + priority.color + '-50 text-' + priority.color + '-600'
                  : 'border-slate-200 text-slate-600 hover:border-slate-300'"
              >
                {{ priority.label }}
              </button>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="newNotification.sendEmail"
                class="rounded border-slate-300 bg-white text-emerald-500"
              />
              <span class="text-sm text-slate-700">Email orqali ham yuborish</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="newNotification.scheduled"
                class="rounded border-slate-300 bg-white text-emerald-500"
              />
              <span class="text-sm text-slate-700">Keyinroq yuborish</span>
            </label>
          </div>

          <div v-if="newNotification.scheduled" class="flex gap-3">
            <input
              v-model="newNotification.scheduledDate"
              type="date"
              class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none"
            />
            <input
              v-model="newNotification.scheduledTime"
              type="time"
              class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          <div class="flex justify-end gap-3">
            <button 
              @click="resetForm"
              class="rounded-lg border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
            >
              Tozalash
            </button>
            <button 
              @click="sendNotification"
              :disabled="!canSend || sending"
              class="flex items-center gap-2 rounded-lg bg-emerald-500 px-6 py-2 text-white hover:bg-emerald-600 disabled:opacity-50"
            >
              <Loader2 v-if="sending" :size="18" class="animate-spin" />
              <Send v-else :size="18" />
              {{ sending ? 'Yuborilmoqda...' : newNotification.scheduled ? 'Rejalashtirish' : 'Yuborish' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Quick Templates -->
      <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 class="mb-4 text-lg font-semibold text-slate-800">Tez shablonlar</h3>
        <div class="space-y-2">
          <button
            v-for="template in quickTemplates"
            :key="template.id"
            @click="applyTemplate(template)"
            class="w-full rounded-lg border border-slate-200 p-3 text-left transition-all hover:border-emerald-300 hover:bg-slate-50"
          >
            <div class="flex items-center gap-2">
              <component :is="template.icon" :size="18" :class="template.iconColor" />
              <span class="font-medium text-slate-800">{{ template.title }}</span>
            </div>
            <p class="mt-1 text-xs text-slate-500 line-clamp-2">{{ template.message }}</p>
          </button>
        </div>
      </div>
    </div>

    <!-- History Tab -->
    <div v-if="activeTab === 'history'" class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <!-- Filters -->
      <div class="border-b border-slate-200 p-4">
        <div class="flex flex-wrap items-center gap-3">
          <select
            v-model="historyFilter.type"
            class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700"
          >
            <option value="all">Barcha turlar</option>
            <option value="info">Ma'lumot</option>
            <option value="warning">Ogohlantirish</option>
            <option value="success">Muvaffaqiyat</option>
            <option value="urgent">Shoshilinch</option>
          </select>
          <input
            v-model="historyFilter.search"
            type="text"
            placeholder="Qidirish..."
            class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 placeholder-slate-400"
          />
        </div>
      </div>

      <!-- Notifications List -->
      <div class="divide-y divide-slate-100">
        <div 
          v-for="notification in filteredNotifications" 
          :key="notification.id"
          class="flex items-start gap-4 p-4 transition-colors hover:bg-slate-50"
        >
          <div 
            class="flex h-10 w-10 items-center justify-center rounded-xl"
            :class="getTypeClass(notification.type).bg"
          >
            <component :is="getTypeIcon(notification.type)" :size="20" :class="getTypeClass(notification.type).text" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h4 class="font-medium text-slate-800">{{ notification.title }}</h4>
              <span 
                v-if="notification.priority === 'high'"
                class="rounded bg-red-100 px-2 py-0.5 text-xs text-red-600"
              >
                Muhim
              </span>
            </div>
            <p class="mt-1 text-sm text-slate-500 line-clamp-2">{{ notification.message }}</p>
            <div class="mt-2 flex items-center gap-4 text-xs text-slate-400">
              <span class="flex items-center gap-1">
                <Clock :size="12" />
                {{ formatTime(notification.createdAt) }}
              </span>
              <span class="flex items-center gap-1">
                <Users :size="12" />
                {{ notification.recipientCount }} ta qabul qiluvchi
              </span>
              <span v-if="notification.readCount" class="flex items-center gap-1">
                <Eye :size="12" />
                {{ notification.readCount }} ta o'qilgan
              </span>
            </div>
          </div>
          <button 
            @click="deleteNotification(notification.id)"
            class="text-slate-400 hover:text-red-500"
          >
            <Trash2 :size="18" />
          </button>
        </div>

        <div v-if="filteredNotifications.length === 0" class="py-12 text-center">
          <Bell :size="48" class="mx-auto mb-4 text-slate-300" />
          <p class="text-slate-500">Xabarlar topilmadi</p>
        </div>
      </div>
    </div>

    <!-- Activity Timeline Tab -->
    <div v-if="activeTab === 'activity'" class="rounded-xl border border-slate-200 bg-white shadow-sm">
      <!-- Activity Filters -->
      <div class="border-b border-slate-200 p-4">
        <div class="flex flex-wrap items-center gap-3">
          <select
            v-model="activityFilter.type"
            class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700"
          >
            <option value="all">Barcha faoliyatlar</option>
            <option value="attendance">Davomat</option>
            <option value="notification">Xabarlar</option>
            <option value="student">Talabalar</option>
            <option value="report">Hisobotlar</option>
            <option value="file">Fayllar</option>
          </select>
          <input
            v-model="activityFilter.date"
            type="date"
            class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700"
          />
          <button
            @click="refreshActivity"
            class="flex items-center gap-2 rounded-lg bg-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-600"
          >
            <RefreshCw :size="16" :class="{ 'animate-spin': refreshing }" />
            Yangilash
          </button>
        </div>
      </div>

      <!-- Timeline -->
      <div class="p-6">
        <div class="relative">
          <!-- Timeline Line -->
          <div class="absolute left-5 top-0 bottom-0 w-0.5 bg-slate-700"></div>

          <!-- Timeline Items -->
          <div class="space-y-6">
            <div 
              v-for="(activity, index) in filteredActivities" 
              :key="activity.id"
              class="relative flex gap-4"
            >
              <!-- Timeline Dot -->
              <div 
                class="relative z-10 flex h-10 w-10 items-center justify-center rounded-full border-2"
                :class="getActivityClass(activity.type)"
              >
                <component :is="getActivityIcon(activity.type)" :size="18" />
              </div>

              <!-- Content -->
              <div class="flex-1 rounded-lg border border-slate-700 bg-slate-700/30 p-4">
                <div class="flex items-start justify-between">
                  <div>
                    <h4 class="font-medium text-white">{{ activity.title }}</h4>
                    <p class="mt-1 text-sm text-slate-400">{{ activity.description }}</p>
                  </div>
                  <span class="text-xs text-slate-500">{{ formatActivityTime(activity.timestamp) }}</span>
                </div>
                
                <!-- Extra info -->
                <div v-if="activity.details" class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="(value, key) in activity.details"
                    :key="key"
                    class="rounded bg-slate-600 px-2 py-1 text-xs text-slate-300"
                  >
                    {{ key }}: {{ value }}
                  </span>
                </div>

                <!-- User info -->
                <div class="mt-3 flex items-center gap-2 text-xs text-slate-500">
                  <div class="h-5 w-5 rounded-full bg-slate-600 flex items-center justify-center">
                    <User :size="12" class="text-slate-400" />
                  </div>
                  {{ activity.user }}
                </div>
              </div>
            </div>
          </div>

          <!-- Load More -->
          <div v-if="hasMoreActivities" class="mt-6 text-center">
            <button
              @click="loadMoreActivities"
              class="rounded-lg bg-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-600"
            >
              Ko'proq yuklash
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import {
  PenLine, History, Activity, Send, Users, Bell, Info, AlertTriangle,
  CheckCircle, AlertOctagon, Clock, Eye, Trash2, RefreshCw, User,
  Loader2, Calendar, FileText, ClipboardCheck, Upload, Download
} from 'lucide-vue-next'

const dataStore = useDataStore()
const authStore = useAuthStore()
const toast = useToastStore()

// State
const activeTab = ref('compose')
const sending = ref(false)
const refreshing = ref(false)
const selectedRecipients = ref([])

const newNotification = ref({
  title: '',
  message: '',
  type: 'info',
  priority: 'normal',
  sendEmail: false,
  scheduled: false,
  scheduledDate: '',
  scheduledTime: ''
})

const historyFilter = ref({
  type: 'all',
  search: ''
})

const activityFilter = ref({
  type: 'all',
  date: ''
})

// Options
const notificationTypes = [
  { value: 'info', label: 'Ma\'lumot', icon: Info, textColor: 'text-blue-400' },
  { value: 'warning', label: 'Ogohlantirish', icon: AlertTriangle, textColor: 'text-yellow-400' },
  { value: 'success', label: 'Muvaffaqiyat', icon: CheckCircle, textColor: 'text-green-400' },
  { value: 'urgent', label: 'Shoshilinch', icon: AlertOctagon, textColor: 'text-red-400' }
]

const priorities = [
  { value: 'low', label: 'Past', color: 'slate' },
  { value: 'normal', label: 'O\'rtacha', color: 'blue' },
  { value: 'high', label: 'Yuqori', color: 'red' }
]

const quickTemplates = [
  { 
    id: 1, 
    title: 'Dars boshlanishi', 
    message: 'Hurmatli talabalar, ertaga soat 9:00 da dars boshlanadi. Vaqtida kelishingizni so\'raymiz.',
    type: 'info',
    icon: Calendar,
    iconColor: 'text-blue-400'
  },
  { 
    id: 2, 
    title: 'Imtihon eslatmasi', 
    message: 'Eslatma: Kelasi hafta juma kuni yakuniy imtihon bo\'lib o\'tadi. Tayyorlanishni unutmang!',
    type: 'warning',
    icon: AlertTriangle,
    iconColor: 'text-yellow-400'
  },
  { 
    id: 3, 
    title: 'Dars bekor qilindi', 
    message: 'Bugungi dars texnik sabablarga ko\'ra bekor qilindi. Keyingi dars haqida xabar beramiz.',
    type: 'urgent',
    icon: AlertOctagon,
    iconColor: 'text-red-400'
  },
  { 
    id: 4, 
    title: 'Tabriklaymiz!', 
    message: 'Guruhimiz bu oydagi eng yaxshi davomat ko\'rsatkichiga erishdi. Rahmat!',
    type: 'success',
    icon: CheckCircle,
    iconColor: 'text-green-400'
  }
]

// Demo data
const notifications = ref([
  { id: 1, title: 'Dars jadvali o\'zgardi', message: 'Matematika darsi 10:00 ga ko\'chirildi', type: 'info', priority: 'normal', createdAt: new Date(), recipientCount: 25, readCount: 18 },
  { id: 2, title: 'Imtihon sanasi', message: 'Yakuniy imtihon 15-yanvarga belgilandi', type: 'warning', priority: 'high', createdAt: new Date(Date.now() - 86400000), recipientCount: 25, readCount: 22 },
  { id: 3, title: 'Tabriklaymiz!', message: 'Guruh 95% davomat ko\'rsatdi', type: 'success', priority: 'normal', createdAt: new Date(Date.now() - 172800000), recipientCount: 25, readCount: 25 }
])

const activities = ref([
  { id: 1, type: 'attendance', title: 'Davomat saqlandi', description: 'Bugungi dars uchun 23 ta talaba davomati saqlandi', user: 'Sardor (Siz)', timestamp: new Date(), details: { 'Keldi': 20, 'Kelmadi': 2, 'Kechikdi': 1 } },
  { id: 2, type: 'notification', title: 'Xabar yuborildi', description: 'Dars jadvali o\'zgarishi haqida xabar yuborildi', user: 'Sardor (Siz)', timestamp: new Date(Date.now() - 3600000), details: { 'Qabul qiluvchilar': 25 } },
  { id: 3, type: 'file', title: 'Fayl yuklandi', description: 'Davomat hisoboti yuklandi', user: 'Sardor (Siz)', timestamp: new Date(Date.now() - 7200000), details: { 'Fayl': 'hisobot.pdf' } },
  { id: 4, type: 'student', title: 'Talaba ma\'lumotlari yangilandi', description: 'Aliyev Jasur telefon raqami o\'zgartirildi', user: 'Admin', timestamp: new Date(Date.now() - 86400000) },
  { id: 5, type: 'report', title: 'Hisobot yaratildi', description: 'Haftalik davomat hisoboti eksport qilindi', user: 'Sardor (Siz)', timestamp: new Date(Date.now() - 172800000), details: { 'Format': 'PDF' } },
  { id: 6, type: 'attendance', title: 'Davomat saqlandi', description: 'O\'tgan dars uchun davomat saqlandi', user: 'Sardor (Siz)', timestamp: new Date(Date.now() - 259200000), details: { 'Keldi': 22, 'Kelmadi': 1, 'Kechikdi': 2 } }
])

// Computed
const groupStudents = computed(() => {
  const groupId = authStore.user?.groupId
  return dataStore.students.filter(s => s.groupId === groupId)
})

const allStudentsSelected = computed(() => {
  return groupStudents.value.length > 0 && 
    groupStudents.value.every(s => selectedRecipients.value.includes(s.id))
})

const canSend = computed(() => {
  return newNotification.value.title.trim() && 
    newNotification.value.message.trim() && 
    selectedRecipients.value.length > 0
})

const filteredNotifications = computed(() => {
  return notifications.value.filter(n => {
    if (historyFilter.value.type !== 'all' && n.type !== historyFilter.value.type) return false
    if (historyFilter.value.search && !n.title.toLowerCase().includes(historyFilter.value.search.toLowerCase())) return false
    return true
  })
})

const filteredActivities = computed(() => {
  return activities.value.filter(a => {
    if (activityFilter.value.type !== 'all' && a.type !== activityFilter.value.type) return false
    return true
  })
})

const hasMoreActivities = computed(() => activities.value.length > 5)

// Methods
function selectAllStudents() {
  if (allStudentsSelected.value) {
    selectedRecipients.value = []
  } else {
    selectedRecipients.value = groupStudents.value.map(s => s.id)
  }
}

function toggleRecipient(id) {
  const index = selectedRecipients.value.indexOf(id)
  if (index === -1) {
    selectedRecipients.value.push(id)
  } else {
    selectedRecipients.value.splice(index, 1)
  }
}

function applyTemplate(template) {
  newNotification.value.title = template.title
  newNotification.value.message = template.message
  newNotification.value.type = template.type
  toast.info('Shablon qo\'llanildi')
}

function resetForm() {
  newNotification.value = {
    title: '',
    message: '',
    type: 'info',
    priority: 'normal',
    sendEmail: false,
    scheduled: false,
    scheduledDate: '',
    scheduledTime: ''
  }
  selectedRecipients.value = []
}

function sendNotification() {
  sending.value = true
  
  setTimeout(() => {
    // Add to notifications
    notifications.value.unshift({
      id: Date.now(),
      title: newNotification.value.title,
      message: newNotification.value.message,
      type: newNotification.value.type,
      priority: newNotification.value.priority,
      createdAt: new Date(),
      recipientCount: selectedRecipients.value.length,
      readCount: 0
    })

    // Add activity
    activities.value.unshift({
      id: Date.now(),
      type: 'notification',
      title: 'Xabar yuborildi',
      description: newNotification.value.title,
      user: 'Sardor (Siz)',
      timestamp: new Date(),
      details: { 'Qabul qiluvchilar': selectedRecipients.value.length }
    })

    sending.value = false
    toast.success('Xabar muvaffaqiyatli yuborildi!')
    resetForm()
  }, 1500)
}

function deleteNotification(id) {
  if (confirm('Bu xabarni o\'chirmoqchimisiz?')) {
    notifications.value = notifications.value.filter(n => n.id !== id)
    toast.success('Xabar o\'chirildi')
  }
}

function refreshActivity() {
  refreshing.value = true
  setTimeout(() => {
    refreshing.value = false
    toast.success('Faoliyat yangilandi')
  }, 1000)
}

function loadMoreActivities() {
  // Simulated load more
  toast.info('Ko\'proq yuklash...')
}

function getTypeClass(type) {
  const classes = {
    info: { bg: 'bg-blue-500/20', text: 'text-blue-400' },
    warning: { bg: 'bg-yellow-500/20', text: 'text-yellow-400' },
    success: { bg: 'bg-green-500/20', text: 'text-green-400' },
    urgent: { bg: 'bg-red-500/20', text: 'text-red-400' }
  }
  return classes[type] || classes.info
}

function getTypeIcon(type) {
  const icons = { info: Info, warning: AlertTriangle, success: CheckCircle, urgent: AlertOctagon }
  return icons[type] || Info
}

function getActivityClass(type) {
  const classes = {
    attendance: 'border-green-500 bg-green-500/20 text-green-400',
    notification: 'border-blue-500 bg-blue-500/20 text-blue-400',
    student: 'border-purple-500 bg-purple-500/20 text-purple-400',
    report: 'border-orange-500 bg-orange-500/20 text-orange-400',
    file: 'border-cyan-500 bg-cyan-500/20 text-cyan-400'
  }
  return classes[type] || 'border-slate-500 bg-slate-500/20 text-slate-400'
}

function getActivityIcon(type) {
  const icons = {
    attendance: ClipboardCheck,
    notification: Bell,
    student: Users,
    report: FileText,
    file: Upload
  }
  return icons[type] || Activity
}

function formatTime(date) {
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  if (diff < 60000) return 'Hozirgina'
  if (diff < 3600000) return Math.floor(diff / 60000) + ' daqiqa oldin'
  if (diff < 86400000) return Math.floor(diff / 3600000) + ' soat oldin'
  return d.toLocaleDateString('uz-UZ')
}

function formatActivityTime(date) {
  const d = new Date(date)
  return d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' }) + 
    ' • ' + d.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short' })
}
</script>
