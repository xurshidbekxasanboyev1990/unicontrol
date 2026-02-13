<template>
  <div class="space-y-6">
    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="space-y-6">
      <div>
        <div class="h-8 w-48 bg-slate-200 rounded animate-pulse"></div>
        <div class="h-4 w-64 bg-slate-100 rounded mt-2 animate-pulse"></div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-for="i in 4" :key="i" class="bg-white rounded-2xl border border-slate-200 p-6">
          <div class="h-6 w-40 bg-slate-200 rounded mb-4 animate-pulse"></div>
          <div class="space-y-4">
            <div v-for="j in 3" :key="j">
              <div class="h-4 w-24 bg-slate-100 rounded mb-2 animate-pulse"></div>
              <div class="h-12 bg-slate-100 rounded-xl animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template v-else>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('settings.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('settings.appSettings') }}</p>
      </div>
      <button 
        @click="loadSettings"
        :disabled="isRefreshing"
        class="flex items-center gap-2 px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors disabled:opacity-50"
      >
        <RefreshCw :size="18" :class="{ 'animate-spin': isRefreshing }" />
        {{ $t('common.refresh') }}
      </button>
    </div>

    <!-- Settings Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Faculty Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Building class="w-5 h-5 text-slate-400" />
          {{ $t('profile.faculty') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.facultyName') }}</label>
            <input 
              v-model="settings.faculty_name"
              type="text"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.facultyCode') }}</label>
            <input 
              v-model="settings.faculty_code"
              type="text"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.academicYear') }}</label>
            <select 
              v-model="settings.academic_year"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            >
              <option>2024-2025</option>
              <option>2025-2026</option>
              <option>2026-2027</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.semester') }}</label>
            <select 
              v-model="settings.semester"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            >
              <option value="1">1-semestr (Kuz)</option>
              <option value="2">2-semestr (Bahor)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Attendance Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <ClipboardCheck class="w-5 h-5 text-slate-400" />
          Davomat sozlamalari
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Minimal davomat foizi (%)</label>
            <input 
              v-model.number="settings.min_attendance"
              type="number"
              min="0"
              max="100"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Kechikish chegarasi (daqiqa)</label>
            <input 
              v-model.number="settings.late_threshold"
              type="number"
              min="0"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Avtomatik ogohlantirish</p>
              <p class="text-sm text-slate-500">Past davomat bo'lganda xabar yuborish</p>
            </div>
            <button 
              @click="settings.auto_warning = !settings.auto_warning"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.auto_warning ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.auto_warning ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Hafta oxiri davomati</p>
              <p class="text-sm text-slate-500">Shanba kunlarni hisoblash</p>
            </div>
            <button 
              @click="settings.weekend_attendance = !settings.weekend_attendance"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.weekend_attendance ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.weekend_attendance ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Bell class="w-5 h-5 text-slate-400" />
          Bildirishnoma sozlamalari
        </h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Email xabarnomalar</p>
              <p class="text-sm text-slate-500">Muhim yangiliklar emailga yuborilsin</p>
            </div>
            <button 
              @click="settings.email_notifications = !settings.email_notifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.email_notifications ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.email_notifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">SMS xabarnomalar</p>
              <p class="text-sm text-slate-500">Muhim yangiliklar SMS orqali</p>
            </div>
            <button 
              @click="settings.sms_notifications = !settings.sms_notifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.sms_notifications ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.sms_notifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Telegram xabarnomalar</p>
              <p class="text-sm text-slate-500">Telegram bot orqali xabar yuborish</p>
            </div>
            <button 
              @click="settings.telegram_notifications = !settings.telegram_notifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.telegram_notifications ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.telegram_notifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Push xabarnomalar</p>
              <p class="text-sm text-slate-500">Brauzer orqali xabarnomalar</p>
            </div>
            <button 
              @click="settings.push_notifications = !settings.push_notifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.push_notifications ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.push_notifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Contract Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <CreditCard class="w-5 h-5 text-slate-400" />
          Kontrakt sozlamalari
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Kontrakt summasi (so'm)</label>
            <input 
              v-model.number="settings.contract_amount"
              type="number"
              min="0"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
            <p class="text-xs text-slate-500 mt-1">{{ formatMoney(settings.contract_amount) }} so'm</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">To'lov muddati (kun)</label>
            <input 
              v-model.number="settings.payment_deadline"
              type="number"
              min="1"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">To'lov eslatmasi</p>
              <p class="text-sm text-slate-500">Muddat yaqinlashganda xabar yuborish</p>
            </div>
            <button 
              @click="settings.payment_reminder = !settings.payment_reminder"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.payment_reminder ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.payment_reminder ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Qarzdorlarni bloklash</p>
              <p class="text-sm text-slate-500">Qarzdor talabalarni cheklash</p>
            </div>
            <button 
              @click="settings.block_debtors = !settings.block_debtors"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.block_debtors ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.block_debtors ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Reports Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <FileText class="w-5 h-5 text-slate-400" />
          Hisobotlar sozlamalari
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Haftalik hisobot kuni</label>
            <select 
              v-model="settings.weekly_report_day"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            >
              <option value="1">Dushanba</option>
              <option value="2">Seshanba</option>
              <option value="3">Chorshanba</option>
              <option value="4">Payshanba</option>
              <option value="5">Juma</option>
              <option value="6">Shanba</option>
              <option value="0">Yakshanba</option>
            </select>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Avtomatik hisobot</p>
              <p class="text-sm text-slate-500">Haftalik hisobotlarni avtomatik yaratish</p>
            </div>
            <button 
              @click="settings.auto_report = !settings.auto_report"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.auto_report ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.auto_report ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Hisobotni emailga yuborish</p>
              <p class="text-sm text-slate-500">Yaratilgan hisobotni emailga jo'natish</p>
            </div>
            <button 
              @click="settings.email_report = !settings.email_report"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.email_report ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.email_report ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Display Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Monitor class="w-5 h-5 text-slate-400" />
          Ko'rinish sozlamalari
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Sahifadagi elementlar soni</label>
            <select 
              v-model.number="settings.items_per_page"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            >
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Kompakt ko'rinish</p>
              <p class="text-sm text-slate-500">Jadvallarni ixcham ko'rsatish</p>
            </div>
            <button 
              @click="settings.compact_view = !settings.compact_view"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.compact_view ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.compact_view ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">Animatsiyalar</p>
              <p class="text-sm text-slate-500">Interfeys animatsiyalari</p>
            </div>
            <button 
              @click="settings.animations = !settings.animations"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.animations ? 'bg-violet-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.animations ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex items-center justify-between bg-white rounded-2xl border border-slate-200 p-4">
      <div class="text-sm text-slate-500">
        <span v-if="hasChanges" class="text-amber-600 flex items-center gap-1">
          <AlertCircle class="w-4 h-4" />
          O'zgarishlar saqlanmagan
        </span>
        <span v-else>Barcha o'zgarishlar saqlangan</span>
      </div>
      <div class="flex gap-3">
        <button 
          @click="resetSettings"
          :disabled="!hasChanges || isSaving"
          class="px-6 py-3 border border-slate-200 text-slate-600 rounded-xl font-medium hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ $t('common.cancel') }}
        </button>
        <button 
          @click="saveSettings"
          :disabled="!hasChanges || isSaving"
          class="px-6 py-3 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="isSaving" class="w-5 h-5 animate-spin" />
          <Save v-else class="w-5 h-5" />
          {{ isSaving ? $t('settings.saving') : $t('common.save') }}
        </button>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
/**
 * SettingsView.vue - Admin sozlamalari
 * 
 * Admin imkoniyatlari:
 * - Fakultet ma'lumotlari
 * - Davomat sozlamalari
 * - Bildirishnoma sozlamalari
 * - Kontrakt sozlamalari
 * - Hisobotlar sozlamalari
 * - Ko'rinish sozlamalari
 */

import api from '@/services/api'
import { useToastStore } from '@/stores/toast'
import {
    AlertCircle,
    Bell,
    Building,
    ClipboardCheck,
    CreditCard,
    FileText,
    Loader2,
    Monitor,
    RefreshCw,
    Save
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'

const toast = useToastStore()

// State
const isLoading = ref(true)
const isRefreshing = ref(false)
const isSaving = ref(false)

// Default settings
const defaultSettings = {
  // Fakultet
  faculty_name: '',
  faculty_code: '',
  academic_year: '2025-2026',
  semester: '2',
  
  // Davomat
  min_attendance: 70,
  late_threshold: 15,
  auto_warning: true,
  weekend_attendance: false,
  
  // Bildirishnomalar
  email_notifications: true,
  sms_notifications: false,
  telegram_notifications: false,
  push_notifications: true,
  
  // Kontrakt
  contract_amount: 15000000,
  payment_deadline: 30,
  payment_reminder: true,
  block_debtors: false,
  
  // Hisobotlar
  weekly_report_day: '5',
  auto_report: true,
  email_report: false,
  
  // Ko'rinish
  items_per_page: 50,
  compact_view: false,
  animations: true
}

const settings = reactive({ ...defaultSettings })
const originalSettings = ref({ ...defaultSettings })

// O'zgarishlar borligini tekshirish
const hasChanges = computed(() => {
  return JSON.stringify(settings) !== JSON.stringify(originalSettings.value)
})

// Pul formatini chiqarish
const formatMoney = (amount) => {
  return new Intl.NumberFormat('uz-UZ').format(amount || 0)
}

// Sozlamalarni yuklash
const loadSettings = async () => {
  try {
    isRefreshing.value = true
    
    // Admin sozlamalari API dan
    const response = await api.getSettings()
    
    if (response) {
      Object.keys(defaultSettings).forEach(key => {
        if (response[key] !== undefined) {
          settings[key] = response[key]
        }
      })
    }
    
    // Original qiymatlarni saqlash
    originalSettings.value = { ...settings }
    
  } catch (error) {
    console.error('Error loading settings:', error)
    toast.warning('Ogohlantirish', 'Sozlamalar yuklanmadi, standart qiymatlar ishlatilmoqda')
  } finally {
    isLoading.value = false
    isRefreshing.value = false
  }
}

// Sozlamalarni saqlash
const saveSettings = async () => {
  try {
    isSaving.value = true
    
    await api.updateSettings(settings)
    
    // Original qiymatlarni yangilash
    originalSettings.value = { ...settings }
    
    toast.success('Muvaffaqiyat', 'Sozlamalar saqlandi')
  } catch (error) {
    console.error('Error saving settings:', error)
    toast.error('Xatolik', 'Sozlamalarni saqlashda xatolik yuz berdi')
  } finally {
    isSaving.value = false
  }
}

// O'zgarishlarni bekor qilish
const resetSettings = () => {
  Object.assign(settings, originalSettings.value)
  toast.info('Bekor qilindi', 'O\'zgarishlar bekor qilindi')
}

onMounted(() => {
  loadSettings()
})
</script>
