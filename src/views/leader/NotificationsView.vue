<template>
  <div class="space-y-6">
    <!-- ========================================
         SARLAVHA QISMI (Header)
         ======================================== -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('notifications.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('notifications.sendNotification') }}</p>
      </div>
      
      <!-- Yangi xabar tugmasi -->
      <button
        @click="showComposeModal = true"
        class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600"
      >
        <Send :size="20" />
        {{ $t('notifications.newMessage') }}
      </button>
    </div>

    <!-- ========================================
         TABS: Yuborish / Tarix
         ======================================== -->
    <div class="flex rounded-xl bg-slate-100 p-1 w-fit">
      <button
        @click="activeTab = 'compose'"
        class="rounded-lg px-5 py-2.5 text-sm font-medium transition-all"
        :class="activeTab === 'compose' 
          ? 'bg-white text-emerald-600 shadow' 
          : 'text-slate-600 hover:text-slate-800'"
      >
        <PenLine :size="16" class="inline mr-2" />
        {{ $t('notifications.send') }}
      </button>
      <button
        @click="activeTab = 'history'"
        class="rounded-lg px-5 py-2.5 text-sm font-medium transition-all"
        :class="activeTab === 'history' 
          ? 'bg-white text-emerald-600 shadow' 
          : 'text-slate-600 hover:text-slate-800'"
      >
        <History :size="16" class="inline mr-2" />
        {{ $t('notifications.allMessages') }}
      </button>
    </div>

    <!-- ========================================
         TEZ YUBORISH QISMI (Compose Tab)
         ======================================== -->
    <div v-if="activeTab === 'compose'" class="grid gap-6 lg:grid-cols-3">
      <!-- Xabar yozish formasi -->
      <div class="lg:col-span-2 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-800">
          <PenLine :size="20" class="text-emerald-500" />
          {{ $t('notifications.newMessage') }}
        </h2>

        <div class="space-y-4">
          <!-- Sarlavha -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">{{ $t('notifications.subjectLabel') }}</label>
            <input 
              v-model="newMessage.title"
              type="text"
              :placeholder="$t('notifications.titlePlaceholder')"
              class="w-full rounded-xl border border-slate-200 px-4 py-3 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          <!-- Qabul qiluvchilar -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">{{ $t('notifications.whoReceives') }}</label>
            <div class="flex flex-wrap gap-2">
              <!-- Barchasi tugmasi -->
              <button
                @click="selectAllStudents"
                class="rounded-xl px-4 py-2 text-sm font-medium transition-all"
                :class="allSelected 
                  ? 'bg-emerald-500 text-white' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
              >
                <Users :size="16" class="inline mr-1" />
                {{ $t('notifications.selectAll') }} ({{ groupStudents.length }})
              </button>
              
              <!-- Har bir talaba -->
              <button
                v-for="student in groupStudents"
                :key="student.id"
                @click="toggleRecipient(student.id)"
                class="rounded-xl px-3 py-2 text-sm font-medium transition-all"
                :class="selectedRecipients.includes(student.id) 
                  ? 'bg-emerald-500 text-white' 
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
              >
                {{ student.name.split(' ')[0] }}
              </button>
            </div>
            <p class="mt-2 text-xs text-slate-400">
              {{ selectedRecipients.length }} {{ $t('notifications.recipients') }}
            </p>
          </div>

          <!-- Xabar matni -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">{{ $t('notifications.messageText') }}</label>
            <textarea 
              v-model="newMessage.text"
              rows="5"
              :placeholder="$t('notifications.textPlaceholder')"
              class="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
            ></textarea>
            <div class="mt-1 text-right text-xs text-slate-400">
              {{ newMessage.text.length }} / 500 {{ $t('notifications.charCount') }}
            </div>
          </div>

          <!-- Xabar turi -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">{{ $t('notifications.messageType') }}</label>
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <button
                v-for="type in messageTypes"
                :key="type.value"
                @click="newMessage.type = type.value"
                class="flex items-center justify-center gap-2 rounded-xl border p-3 transition-all"
                :class="newMessage.type === type.value 
                  ? colorClasses[type.color]?.active || ''
                  : 'border-slate-200 text-slate-600 hover:border-slate-300'"
              >
                <component :is="type.icon" :size="18" />
                <span class="text-sm">{{ type.label }}</span>
              </button>
            </div>
          </div>

          <!-- Yuborish tugmasi -->
          <button
            @click="sendMessage"
            :disabled="!canSend"
            class="w-full rounded-xl bg-emerald-500 py-3.5 font-medium text-white transition-all hover:bg-emerald-600 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            <Send :size="18" class="inline mr-2" />
            {{ $t('notifications.send') }}
          </button>
        </div>
      </div>

      <!-- Tez shablonlar -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-800">
          <Zap :size="20" class="text-yellow-500" />
          {{ $t('common.templates') }}
        </h2>
        
        <div class="space-y-3">
          <button
            v-for="template in quickTemplates"
            :key="template.id"
            @click="useTemplate(template)"
            class="w-full rounded-xl border border-slate-200 p-4 text-left transition-all hover:border-emerald-300 hover:bg-emerald-50"
          >
            <div class="flex items-center gap-3">
              <div 
                class="flex h-10 w-10 items-center justify-center rounded-lg"
                :class="colorClasses[template.color]?.bg || 'bg-blue-100 text-blue-600'"
              >
                <component :is="template.icon" :size="20" />
              </div>
              <div>
                <p class="font-medium text-slate-700">{{ template.title }}</p>
                <p class="text-xs text-slate-400">{{ template.preview }}</p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================
         YUBORILGAN XABARLAR TARIXI (History Tab)
         ======================================== -->
    <div v-if="activeTab === 'history'" class="space-y-4">
      <!-- Filter -->
      <div class="flex items-center gap-3">
        <select 
          v-model="historyFilter"
          class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-700 focus:border-emerald-500 focus:outline-none"
        >
          <option value="all">{{ $t('notifications.allMessages') }}</option>
          <option value="info">{{ $t('notifications.info') }}</option>
          <option value="warning">{{ $t('notifications.warning') }}</option>
          <option value="success">{{ $t('notifications.success') }}</option>
          <option value="alert">{{ $t('notifications.alert') }}</option>
        </select>
        
        <span class="text-sm text-slate-500">
          {{ $t('notifications.totalMessages', { count: filteredHistory.length }) }}
        </span>
      </div>

      <!-- Xabarlar ro'yxati -->
      <div class="space-y-3">
        <div
          v-for="message in filteredHistory"
          :key="message.id"
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Xabar ma'lumotlari -->
            <div class="flex gap-4">
              <!-- Icon -->
              <div 
                class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl"
                :class="getTypeClass(message.type)"
              >
                <component :is="getTypeIcon(message.type)" :size="22" />
              </div>
              
              <!-- Content -->
              <div class="flex-1">
                <h3 class="font-semibold text-slate-800">{{ message.title }}</h3>
                <p class="mt-1 text-sm text-slate-600">{{ message.text }}</p>
                
                <div class="mt-3 flex flex-wrap items-center gap-3">
                  <!-- Qabul qiluvchilar -->
                  <div class="flex items-center gap-1">
                    <Users :size="14" class="text-slate-400" />
                    <span class="text-xs text-slate-500">
                      {{ message.recipientCount }} {{ $t('notifications.recipientCount') }}
                    </span>
                  </div>
                  
                  <!-- Sana -->
                  <div class="flex items-center gap-1">
                    <Clock :size="14" class="text-slate-400" />
                    <span class="text-xs text-slate-500">{{ message.sentAt }}</span>
                  </div>
                  
                  <!-- O'qilgan -->
                  <div class="flex items-center gap-1">
                    <CheckCheck :size="14" class="text-emerald-500" />
                    <span class="text-xs text-emerald-600">
                      {{ $t('notifications.readCount', { read: message.readCount, total: message.recipientCount }) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Amallar -->
            <div class="flex items-center gap-2">
              <button 
                @click="resendMessage(message)"
                class="rounded-lg bg-slate-100 p-2 text-slate-600 transition-all hover:bg-slate-200"
                :title="$t('notifications.resend')"
              >
                <RefreshCw :size="16" />
              </button>
              <button 
                @click="deleteMessage(message)"
                class="rounded-lg bg-red-100 p-2 text-red-600 transition-all hover:bg-red-200"
                :title="$t('common.delete')"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Bo'sh holat -->
      <div 
        v-if="filteredHistory.length === 0"
        class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 py-16"
      >
        <MessageSquare :size="48" class="mb-3 text-slate-300" />
        <p class="text-lg font-medium text-slate-500">{{ $t('notifications.notFound') }}</p>
        <p class="text-sm text-slate-400">{{ $t('notifications.noMessagesSent') }}</p>
      </div>
    </div>

    <!-- ========================================
         XABAR YOZISH MODALI
         ======================================== -->
    <Teleport to="body">
      <div
        v-if="showComposeModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showComposeModal = false"
      >
        <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-bold text-slate-800">{{ $t('notifications.newMessage') }}</h2>
            <button 
              @click="showComposeModal = false"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
            >
              <X :size="20" />
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ $t('notifications.titleLabel') }}</label>
              <input 
                v-model="modalMessage.title"
                type="text"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-500 focus:outline-none"
                :placeholder="$t('notifications.subjectLabel')"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ $t('notifications.text') }}</label>
              <textarea 
                v-model="modalMessage.text"
                rows="4"
                class="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-500 focus:outline-none"
                :placeholder="$t('notifications.textPlaceholder')"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">{{ $t('notifications.recipients') }}</label>
              <div class="flex flex-wrap gap-2">
                <button
                  @click="modalMessage.toAll = !modalMessage.toAll"
                  class="rounded-xl px-4 py-2 text-sm font-medium transition-all"
                  :class="modalMessage.toAll 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-100 text-slate-600'"
                >
                  {{ $t('notifications.wholeGroup') }}
                </button>
              </div>
            </div>
          </div>

          <div class="mt-6 flex gap-3">
            <button
              @click="showComposeModal = false"
              class="flex-1 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 hover:bg-slate-50"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              @click="sendModalMessage"
              class="flex-1 rounded-xl bg-emerald-500 py-3 font-medium text-white hover:bg-emerald-600"
            >
              {{ $t('notifications.send') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * =============================================
 * BILDIRISHNOMALAR SAHIFASI - NotificationsView.vue
 * =============================================
 * 
 * Bu sahifa guruh sardori uchun xabar yuborish:
 * - Bir yoki bir nechta talabaga xabar
 * - Butun guruhga e'lon
 * - Yuborilgan xabarlar tarixi
 * - Tez shablonlar
 */

import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import {
    AlertTriangle,
    Bell,
    CheckCheck,
    CheckCircle,
    Clock,
    History,
    Info,
    MessageSquare,
    PenLine,
    RefreshCw,
    Send,
    Trash2,
    Users,
    X,
    Zap
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'
import api from '../../services/api'

// ==================== STORES ====================
const authStore = useAuthStore()
const toast = useToastStore()

// Language
import { useLanguageStore } from '@/stores/language'
const langStore = useLanguageStore()
const { t } = langStore

// ==================== STATE ====================

// Loading
const loading = ref(true)
const error = ref(null)
const sending = ref(false)

// Tab: 'compose' yoki 'history'
const activeTab = ref('compose')

// Filter
const historyFilter = ref('all')

// Modal
const showComposeModal = ref(false)

// Group students
const groupStudents = ref([])

// Tanlangan talabalar
const selectedRecipients = ref([])

// Yangi xabar
const newMessage = ref({
  title: '',
  text: '',
  type: 'info'
})

// Modal xabar
const modalMessage = ref({
  title: '',
  text: '',
  toAll: true
})

// Xabar turlari
const colorClasses = {
  blue: { active: 'border-blue-500 bg-blue-50 text-blue-600', bg: 'bg-blue-100 text-blue-600' },
  yellow: { active: 'border-yellow-500 bg-yellow-50 text-yellow-600', bg: 'bg-yellow-100 text-yellow-600' },
  green: { active: 'border-green-500 bg-green-50 text-green-600', bg: 'bg-green-100 text-green-600' },
  red: { active: 'border-red-500 bg-red-50 text-red-600', bg: 'bg-red-100 text-red-600' }
}
const messageTypes = computed(() => [
  { value: 'info', label: t('notifications.info'), icon: markRaw(Info), color: 'blue' },
  { value: 'warning', label: t('notifications.warning'), icon: markRaw(AlertTriangle), color: 'yellow' },
  { value: 'success', label: t('notifications.success'), icon: markRaw(CheckCircle), color: 'green' },
  { value: 'alert', label: t('notifications.alert'), icon: markRaw(Bell), color: 'red' }
])

// Tez shablonlar
const quickTemplates = computed(() => [
  {
    id: 1,
    title: t('notifications.lessonReminder'),
    preview: t('notifications.lessonReminderPreview'),
    text: t('notifications.lessonReminderText'),
    type: 'info',
    icon: markRaw(Clock),
    color: 'blue'
  },
  {
    id: 2,
    title: t('notifications.attendanceWarningTitle'),
    preview: t('notifications.attendanceWarningPreview'),
    text: t('notifications.attendanceWarningText'),
    type: 'warning',
    icon: markRaw(AlertTriangle),
    color: 'yellow'
  },
  {
    id: 3,
    title: t('notifications.examReminder'),
    preview: t('notifications.examReminderPreview'),
    text: t('notifications.examReminderText'),
    type: 'alert',
    icon: markRaw(Bell),
    color: 'red'
  },
  {
    id: 4,
    title: t('notifications.congratulation'),
    preview: t('notifications.congratulationPreview'),
    text: t('notifications.congratulationText'),
    type: 'success',
    icon: markRaw(CheckCircle),
    color: 'green'
  }
])

// Yuborilgan xabarlar tarixi (demo)
const messageHistory = ref([
  {
    id: 1,
    title: t('notifications.scheduleHistory'),
    text: t('notifications.scheduleHistoryText'),
    type: 'info',
    sentAt: '26.01.2026, 14:30',
    recipientCount: 5,
    readCount: 4
  },
  {
    id: 2,
    title: t('notifications.attendanceHistory'),
    text: t('notifications.attendanceHistoryText'),
    type: 'warning',
    sentAt: '25.01.2026, 09:15',
    recipientCount: 1,
    readCount: 1
  },
  {
    id: 3,
    title: t('notifications.examHistory'),
    text: t('notifications.examHistoryText'),
    type: 'alert',
    sentAt: '24.01.2026, 16:00',
    recipientCount: 5,
    readCount: 5
  },
  {
    id: 4,
    title: t('notifications.congratsHistory'),
    text: t('notifications.congratsHistoryText'),
    type: 'success',
    sentAt: '23.01.2026, 11:20',
    recipientCount: 1,
    readCount: 1
  }
])

// ==================== COMPUTED ====================

// Barchasi tanlanganmi?
const allSelected = computed(() => {
  return selectedRecipients.value.length === groupStudents.value.length
})

// Yuborish mumkinmi?
const canSend = computed(() => {
  return newMessage.value.title.trim() !== '' && 
         newMessage.value.text.trim() !== '' && 
         selectedRecipients.value.length > 0
})

// Filtrlangan tarix
const filteredHistory = computed(() => {
  if (historyFilter.value === 'all') {
    return messageHistory.value
  }
  return messageHistory.value.filter(m => m.type === historyFilter.value)
})

// ==================== LOAD DATA ====================

const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Get group info from dashboard API
    const dashboardResp = await api.request('/dashboard/leader')
    const groupId = dashboardResp?.group?.id
    
    if (groupId) {
      // Load group students
      try {
        const studentsResponse = await api.request(`/students?group_id=${groupId}&page_size=100`)
        const items = studentsResponse?.items || []
        groupStudents.value = items.map(s => ({
          id: s.id,
          name: s.name || s.full_name,
          user_id: s.user_id
        }))
      } catch (e) {
        console.warn('Could not load students:', e)
        groupStudents.value = []
      }
      
      // Load sent notifications (own notifications for history)
      try {
        const notifResponse = await api.getNotifications({ page_size: 50 })
        const notifItems = notifResponse?.items || []
        // Show any notifications that were sent to the leader (received)
        // For history we use local state as backend doesn't track "sent by me"
      } catch (e) {
        console.warn('Could not load notification history:', e)
      }
    } else {
      error.value = t('notifications.groupInfoNotFound')
    }
  } catch (e) {
    console.error('Error loading data:', e)
    error.value = t('notifications.loadError')
  } finally {
    loading.value = false
  }
}

// ==================== METHODS ====================

// Barcha talabalarni tanlash
function selectAllStudents() {
  if (allSelected.value) {
    selectedRecipients.value = []
  } else {
    selectedRecipients.value = groupStudents.value.map(s => s.id)
  }
}

// Talabani tanlash/bekor qilish
function toggleRecipient(id) {
  const index = selectedRecipients.value.indexOf(id)
  if (index === -1) {
    selectedRecipients.value.push(id)
  } else {
    selectedRecipients.value.splice(index, 1)
  }
}

// Shablondan foydalanish
function useTemplate(template) {
  newMessage.value.title = template.title
  newMessage.value.text = template.text
  newMessage.value.type = template.type
  toast.info(t('notifications.templateLoaded'))
}

// Xabar yuborish
async function sendMessage() {
  if (!canSend.value) return
  
  sending.value = true
  
  try {
    // Map selected student IDs to user_ids for notification
    const userIds = selectedRecipients.value
      .map(studentId => {
        const student = groupStudents.value.find(s => s.id === studentId)
        return student?.user_id
      })
      .filter(id => id != null)
    
    if (userIds.length === 0) {
      toast.error(t('notifications.noUserAccountFound'))
      return
    }
    
    // Send bulk notification via API
    await api.sendBulkNotification({
      user_ids: userIds,
      title: newMessage.value.title,
      message: newMessage.value.text,
      type: newMessage.value.type
    })
    
    // Add to local history
    const message = {
      id: Date.now(),
      title: newMessage.value.title,
      text: newMessage.value.text,
      type: newMessage.value.type,
      sentAt: new Date().toLocaleString('uz-UZ'),
      recipientCount: userIds.length,
      readCount: 0
    }
    
    messageHistory.value.unshift(message)
    toast.success(t('notifications.messageSentToStudents', { count: userIds.length }))
    
    // Formni tozalash
    newMessage.value = { title: '', text: '', type: 'info' }
    selectedRecipients.value = []
  } catch (e) {
    console.error('Error sending message:', e)
    toast.error(t('notifications.messageSendError'))
  } finally {
    sending.value = false
  }
}

// Modal orqali yuborish
async function sendModalMessage() {
  if (!modalMessage.value.title || !modalMessage.value.text) {
    toast.error(t('notifications.fillTitleAndText'))
    return
  }
  
  sending.value = true
  
  try {
    const recipientStudentIds = modalMessage.value.toAll 
      ? groupStudents.value.map(s => s.id) 
      : selectedRecipients.value
    
    // Map to user_ids
    const userIds = recipientStudentIds
      .map(studentId => {
        const student = groupStudents.value.find(s => s.id === studentId)
        return student?.user_id
      })
      .filter(id => id != null)
    
    if (userIds.length === 0) {
      toast.error(t('notifications.userAccountNotFound'))
      return
    }
    
    await api.sendBulkNotification({
      user_ids: userIds,
      title: modalMessage.value.title,
      message: modalMessage.value.text,
      type: 'info'
    })
    
    const message = {
      id: Date.now(),
      title: modalMessage.value.title,
      text: modalMessage.value.text,
      type: 'info',
      sentAt: new Date().toLocaleString('uz-UZ'),
      recipientCount: userIds.length,
      readCount: 0
    }
  
    messageHistory.value.unshift(message)
    toast.success(t('notifications.messageSent'))
    
    showComposeModal.value = false
    modalMessage.value = { title: '', text: '', toAll: true }
  } catch (e) {
    console.error('Error sending modal message:', e)
    toast.error(t('notifications.messageSendError'))
  } finally {
    sending.value = false
  }
}

// Qayta yuborish
function resendMessage(message) {
  toast.success(t('notifications.messageResent', { title: message.title }))
}

// O'chirish
function deleteMessage(message) {
  if (confirm(t('notifications.confirmDeleteMessage', { title: message.title }))) {
    const index = messageHistory.value.findIndex(m => m.id === message.id)
    if (index !== -1) {
      messageHistory.value.splice(index, 1)
      toast.success(t('notifications.messageDeleted'))
    }
  }
}

// Tur bo'yicha class
function getTypeClass(type) {
  const classes = {
    info: 'bg-blue-100 text-blue-600',
    warning: 'bg-yellow-100 text-yellow-600',
    success: 'bg-green-100 text-green-600',
    alert: 'bg-red-100 text-red-600'
  }
  return classes[type] || classes.info
}

// Tur bo'yicha icon
function getTypeIcon(type) {
  const icons = {
    info: Info,
    warning: AlertTriangle,
    success: CheckCircle,
    alert: Bell
  }
  return icons[type] || Info
}

// Initialize
onMounted(() => {
  loadData()
})
</script>
