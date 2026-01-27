<template>
  <div class="space-y-6">
    <!-- ========================================
         SARLAVHA QISMI (Header)
         ======================================== -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Bildirishnomalar</h1>
        <p class="text-slate-500">Talabalaringizga xabar yuborish</p>
      </div>
      
      <!-- Yangi xabar tugmasi -->
      <button
        @click="showComposeModal = true"
        class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600"
      >
        <Send :size="20" />
        Yangi xabar
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
        Tez yuborish
      </button>
      <button
        @click="activeTab = 'history'"
        class="rounded-lg px-5 py-2.5 text-sm font-medium transition-all"
        :class="activeTab === 'history' 
          ? 'bg-white text-emerald-600 shadow' 
          : 'text-slate-600 hover:text-slate-800'"
      >
        <History :size="16" class="inline mr-2" />
        Yuborilgan xabarlar
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
          Yangi xabar yozish
        </h2>

        <div class="space-y-4">
          <!-- Sarlavha -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Sarlavha</label>
            <input 
              v-model="newMessage.title"
              type="text"
              placeholder="Xabar sarlavhasi..."
              class="w-full rounded-xl border border-slate-200 px-4 py-3 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          <!-- Qabul qiluvchilar -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Kimga yuboriladi?</label>
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
                Barchasi ({{ groupStudents.length }})
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
              {{ selectedRecipients.length }} ta talaba tanlangan
            </p>
          </div>

          <!-- Xabar matni -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Xabar matni</label>
            <textarea 
              v-model="newMessage.text"
              rows="5"
              placeholder="Xabar matnini yozing..."
              class="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
            ></textarea>
            <div class="mt-1 text-right text-xs text-slate-400">
              {{ newMessage.text.length }} / 500 belgi
            </div>
          </div>

          <!-- Xabar turi -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Xabar turi</label>
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <button
                v-for="type in messageTypes"
                :key="type.value"
                @click="newMessage.type = type.value"
                class="flex items-center justify-center gap-2 rounded-xl border p-3 transition-all"
                :class="newMessage.type === type.value 
                  ? `border-${type.color}-500 bg-${type.color}-50 text-${type.color}-600`
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
            Yuborish
          </button>
        </div>
      </div>

      <!-- Tez shablonlar -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-800">
          <Zap :size="20" class="text-yellow-500" />
          Tez shablonlar
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
                :class="`bg-${template.color}-100 text-${template.color}-600`"
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
          <option value="all">Barcha xabarlar</option>
          <option value="info">Ma'lumot</option>
          <option value="warning">Ogohlantirish</option>
          <option value="success">Muvaffaqiyat</option>
          <option value="alert">Muhim</option>
        </select>
        
        <span class="text-sm text-slate-500">
          Jami: {{ filteredHistory.length }} ta xabar
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
                      {{ message.recipientCount }} ta qabul qiluvchi
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
                      {{ message.readCount }}/{{ message.recipientCount }} o'qidi
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
                title="Qayta yuborish"
              >
                <RefreshCw :size="16" />
              </button>
              <button 
                @click="deleteMessage(message)"
                class="rounded-lg bg-red-100 p-2 text-red-600 transition-all hover:bg-red-200"
                title="O'chirish"
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
        <p class="text-lg font-medium text-slate-500">Xabarlar topilmadi</p>
        <p class="text-sm text-slate-400">Hali hech qanday xabar yuborilmagan</p>
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
            <h2 class="text-xl font-bold text-slate-800">Yangi xabar</h2>
            <button 
              @click="showComposeModal = false"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
            >
              <X :size="20" />
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Sarlavha</label>
              <input 
                v-model="modalMessage.title"
                type="text"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-500 focus:outline-none"
                placeholder="Xabar sarlavhasi"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Matn</label>
              <textarea 
                v-model="modalMessage.text"
                rows="4"
                class="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-500 focus:outline-none"
                placeholder="Xabar matni..."
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Qabul qiluvchilar</label>
              <div class="flex flex-wrap gap-2">
                <button
                  @click="modalMessage.toAll = !modalMessage.toAll"
                  class="rounded-xl px-4 py-2 text-sm font-medium transition-all"
                  :class="modalMessage.toAll 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-100 text-slate-600'"
                >
                  Butun guruhga
                </button>
              </div>
            </div>
          </div>

          <div class="mt-6 flex gap-3">
            <button
              @click="showComposeModal = false"
              class="flex-1 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 hover:bg-slate-50"
            >
              Bekor qilish
            </button>
            <button
              @click="sendModalMessage"
              class="flex-1 rounded-xl bg-emerald-500 py-3 font-medium text-white hover:bg-emerald-600"
            >
              Yuborish
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

import { ref, computed, markRaw } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import { useToastStore } from '@/stores/toast'
import {
  Send, PenLine, History, Users, Zap, Clock, CheckCheck,
  RefreshCw, Trash2, X, MessageSquare, Bell, AlertTriangle,
  CheckCircle, Info
} from 'lucide-vue-next'

// ==================== STORES ====================
const authStore = useAuthStore()
const dataStore = useDataStore()
const toast = useToastStore()

// ==================== STATE ====================

// Tab: 'compose' yoki 'history'
const activeTab = ref('compose')

// Filter
const historyFilter = ref('all')

// Modal
const showComposeModal = ref(false)

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
const messageTypes = [
  { value: 'info', label: 'Ma\'lumot', icon: markRaw(Info), color: 'blue' },
  { value: 'warning', label: 'Ogohlantirish', icon: markRaw(AlertTriangle), color: 'yellow' },
  { value: 'success', label: 'Muvaffaqiyat', icon: markRaw(CheckCircle), color: 'green' },
  { value: 'alert', label: 'Muhim', icon: markRaw(Bell), color: 'red' }
]

// Tez shablonlar
const quickTemplates = [
  {
    id: 1,
    title: 'Dars eslatmasi',
    preview: 'Ertaga dars...',
    text: 'Assalomu alaykum! Ertaga soat 8:30 da dars boshlanadi. Iltimos, o\'z vaqtida keling.',
    type: 'info',
    icon: markRaw(Clock),
    color: 'blue'
  },
  {
    id: 2,
    title: 'Davomat ogohlantiirish',
    preview: 'Davomat past...',
    text: 'Hurmatli talaba! Sizning davomatingiz past. Iltimos, e\'tibor bering.',
    type: 'warning',
    icon: markRaw(AlertTriangle),
    color: 'yellow'
  },
  {
    id: 3,
    title: 'Imtihon eslatmasi',
    preview: 'Imtihon sanasi...',
    text: 'Diqqat! Yakuniy imtihon sanasi yaqinlashmoqda. Tayyorgarlik ko\'ring!',
    type: 'alert',
    icon: markRaw(Bell),
    color: 'red'
  },
  {
    id: 4,
    title: 'Tabriknoma',
    preview: 'Tabriklaymiz...',
    text: 'Tabriklaymiz! Siz ajoyib natijaga erishdingiz. Davom eting!',
    type: 'success',
    icon: markRaw(CheckCircle),
    color: 'green'
  }
]

// Yuborilgan xabarlar tarixi (demo)
const messageHistory = ref([
  {
    id: 1,
    title: 'Dars vaqti o\'zgardi',
    text: 'Ertangi matematika darsi 10:00 ga ko\'chirildi.',
    type: 'info',
    sentAt: '26.01.2026, 14:30',
    recipientCount: 5,
    readCount: 4
  },
  {
    id: 2,
    title: 'Davomat to\'g\'risida',
    text: 'Rahimov Bekzod, davomatingiz past. Iltimos, e\'tibor bering.',
    type: 'warning',
    sentAt: '25.01.2026, 09:15',
    recipientCount: 1,
    readCount: 1
  },
  {
    id: 3,
    title: 'Imtihon sanasi',
    text: 'Dasturlash fanidan yakuniy imtihon 15-fevral kuni bo\'lib o\'tadi.',
    type: 'alert',
    sentAt: '24.01.2026, 16:00',
    recipientCount: 5,
    readCount: 5
  },
  {
    id: 4,
    title: 'Tabriklaymiz!',
    text: 'Aliyev Jasur, semestrda eng yaxshi natija ko\'rsatdingiz!',
    type: 'success',
    sentAt: '23.01.2026, 11:20',
    recipientCount: 1,
    readCount: 1
  }
])

// ==================== COMPUTED ====================

// Guruh talabalari
const groupStudents = computed(() => {
  const groupName = authStore.user?.group || authStore.user?.managedGroup
  return dataStore.students.filter(s => s.group === groupName)
})

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
  toast.info('Shablon yuklandi')
}

// Xabar yuborish
function sendMessage() {
  if (!canSend.value) return
  
  const message = {
    id: Date.now(),
    title: newMessage.value.title,
    text: newMessage.value.text,
    type: newMessage.value.type,
    sentAt: new Date().toLocaleString('uz-UZ'),
    recipientCount: selectedRecipients.value.length,
    readCount: 0
  }
  
  messageHistory.value.unshift(message)
  toast.success(`Xabar ${selectedRecipients.value.length} ta talabaga yuborildi!`)
  
  // Formni tozalash
  newMessage.value = { title: '', text: '', type: 'info' }
  selectedRecipients.value = []
}

// Modal orqali yuborish
function sendModalMessage() {
  if (!modalMessage.value.title || !modalMessage.value.text) {
    toast.error('Sarlavha va matnni kiriting')
    return
  }
  
  const message = {
    id: Date.now(),
    title: modalMessage.value.title,
    text: modalMessage.value.text,
    type: 'info',
    sentAt: new Date().toLocaleString('uz-UZ'),
    recipientCount: modalMessage.value.toAll ? groupStudents.value.length : 1,
    readCount: 0
  }
  
  messageHistory.value.unshift(message)
  toast.success('Xabar yuborildi!')
  
  showComposeModal.value = false
  modalMessage.value = { title: '', text: '', toAll: true }
}

// Qayta yuborish
function resendMessage(message) {
  toast.success(`"${message.title}" qayta yuborildi`)
}

// O'chirish
function deleteMessage(message) {
  if (confirm(`"${message.title}" o'chirilsinmi?`)) {
    const index = messageHistory.value.findIndex(m => m.id === message.id)
    if (index !== -1) {
      messageHistory.value.splice(index, 1)
      toast.success('Xabar o\'chirildi')
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
</script>
