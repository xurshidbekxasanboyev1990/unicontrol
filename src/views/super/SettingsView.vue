<template>
  <div class="space-y-6">
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

    <!-- Loading State -->
    <div v-if="isLoading" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-for="i in 6" :key="i" class="bg-white rounded-2xl border border-slate-200 p-6">
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

    <!-- Error State -->
    <div v-else-if="loadError" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
      <AlertCircle class="w-12 h-12 text-red-400 mx-auto mb-3" />
      <p class="text-red-600 mb-4">{{ loadError }}</p>
      <button @click="loadSettings" class="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors flex items-center gap-2 mx-auto">
        <RefreshCw class="w-4 h-4" />
        {{ $t('common.retry') }}
      </button>
    </div>

    <template v-else>

    <!-- Settings Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- 1. Muassasa ma'lumotlari -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Building2 class="w-5 h-5 text-amber-500" />
          {{ $t('settings.institutionInfo') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.institutionName') }}</label>
            <input 
              v-model="settings.institution_name"
              type="text"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              placeholder="UniControl"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.institutionAddress') }}</label>
            <input 
              v-model="settings.institution_address"
              type="text"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              placeholder="Toshkent sh., ..."
            />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.institutionPhone') }}</label>
              <input 
                v-model="settings.institution_phone"
                type="text"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                placeholder="+998 ..."
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.institutionEmail') }}</label>
              <input 
                v-model="settings.institution_email"
                type="email"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                placeholder="info@university.uz"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 2. O'quv yili va semestr -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <GraduationCap class="w-5 h-5 text-amber-500" />
          {{ $t('settings.academicInfo') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.academicYear') }}</label>
            <select 
              v-model="settings.academic_year"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            >
              <option>2024-2025</option>
              <option>2025-2026</option>
              <option>2026-2027</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.semesterLabel') }}</label>
            <select 
              v-model="settings.semester"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            >
              <option value="1">{{ $t('settings.semester1') }}</option>
              <option value="2">{{ $t('settings.semester2') }}</option>
            </select>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.workStart') }}</label>
              <input 
                v-model="settings.working_hours_start"
                type="time"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.workEnd') }}</label>
              <input 
                v-model="settings.working_hours_end"
                type="time"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Davomat sozlamalari -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <ClipboardCheck class="w-5 h-5 text-amber-500" />
          {{ $t('settings.attendanceSettings') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.attendanceThreshold') }}</label>
            <div class="flex items-center gap-3">
              <input 
                v-model.number="settings.attendance_threshold"
                type="range"
                min="50"
                max="100"
                step="5"
                class="flex-1 accent-amber-500"
              />
              <span class="text-lg font-bold text-amber-600 w-14 text-center">{{ settings.attendance_threshold }}%</span>
            </div>
            <p class="text-xs text-slate-500 mt-1">{{ $t('settings.attendanceThresholdDesc') }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.lateThreshold') }}</label>
            <div class="flex items-center gap-3">
              <input 
                v-model.number="settings.late_minutes_threshold"
                type="number"
                min="0"
                max="60"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
              <span class="text-sm text-slate-500 whitespace-nowrap">{{ $t('settings.minutes') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Integratsiyalar -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Plug class="w-5 h-5 text-amber-500" />
          {{ $t('settings.integrations') }}
        </h2>
        <div class="space-y-3">
          <!-- Telegram Bot -->
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <MessageCircle class="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p class="font-medium text-slate-700">Telegram Bot</p>
                <p class="text-xs text-slate-500">{{ $t('settings.telegramBotDesc') }}</p>
              </div>
            </div>
            <button 
              @click="settings.telegram_bot_enabled = !settings.telegram_bot_enabled"
              class="w-12 h-6 rounded-full transition-colors flex-shrink-0"
              :class="settings.telegram_bot_enabled ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.telegram_bot_enabled ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>

          <!-- Email -->
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <Mail class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-slate-700">Email</p>
                <p class="text-xs text-slate-500">{{ $t('settings.emailNotifsDesc') }}</p>
              </div>
            </div>
            <button 
              @click="settings.email_notifications_enabled = !settings.email_notifications_enabled"
              class="w-12 h-6 rounded-full transition-colors flex-shrink-0"
              :class="settings.email_notifications_enabled ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.email_notifications_enabled ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>

          <!-- SMS -->
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <Smartphone class="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <p class="font-medium text-slate-700">SMS</p>
                <p class="text-xs text-slate-500">{{ $t('settings.smsNotifsDesc') }}</p>
              </div>
            </div>
            <button 
              @click="settings.sms_notifications_enabled = !settings.sms_notifications_enabled"
              class="w-12 h-6 rounded-full transition-colors flex-shrink-0"
              :class="settings.sms_notifications_enabled ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.sms_notifications_enabled ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>

          <!-- AI Analysis -->
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                <Brain class="w-4 h-4 text-orange-600" />
              </div>
              <div>
                <p class="font-medium text-slate-700">AI {{ $t('settings.analysis') }}</p>
                <p class="text-xs text-slate-500">{{ $t('settings.aiAnalysisDesc') }}</p>
              </div>
            </div>
            <button 
              @click="settings.ai_analysis_enabled = !settings.ai_analysis_enabled"
              class="w-12 h-6 rounded-full transition-colors flex-shrink-0"
              :class="settings.ai_analysis_enabled ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.ai_analysis_enabled ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- 5. Interfeys sozlamalari -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Monitor class="w-5 h-5 text-amber-500" />
          {{ $t('settings.displaySettings') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.defaultLanguage') }}</label>
            <select 
              v-model="settings.language"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            >
              <option value="uz">O'zbekcha</option>
              <option value="ru">Русский</option>
              <option value="en">English</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.timezone') }}</label>
            <select 
              v-model="settings.timezone"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            >
              <option value="Asia/Tashkent">Asia/Tashkent (UTC+5)</option>
              <option value="Asia/Samarkand">Asia/Samarkand (UTC+5)</option>
              <option value="Europe/Moscow">Europe/Moscow (UTC+3)</option>
              <option value="UTC">UTC</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.theme') }}</label>
            <div class="grid grid-cols-2 gap-3">
              <button 
                @click="settings.theme = 'light'"
                class="p-3 rounded-xl border-2 transition-colors flex items-center gap-2"
                :class="settings.theme === 'light' ? 'border-amber-500 bg-amber-50' : 'border-slate-200 hover:border-slate-300'"
              >
                <Sun class="w-5 h-5 text-amber-500" />
                <span class="text-sm font-medium">{{ $t('settings.lightTheme') }}</span>
              </button>
              <button 
                @click="settings.theme = 'dark'"
                class="p-3 rounded-xl border-2 transition-colors flex items-center gap-2"
                :class="settings.theme === 'dark' ? 'border-amber-500 bg-amber-50' : 'border-slate-200 hover:border-slate-300'"
              >
                <Moon class="w-5 h-5 text-slate-600" />
                <span class="text-sm font-medium">{{ $t('settings.darkTheme') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 6. Tizim ma'lumotlari (faqat ko'rish) -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Info class="w-5 h-5 text-amber-500" />
          {{ $t('settings.systemInfo') }}
        </h2>
        <div class="space-y-3">
          <div class="flex items-center justify-between py-2 border-b border-slate-100">
            <span class="text-sm text-slate-500">{{ $t('settings.version') }}</span>
            <span class="text-sm font-medium text-slate-700">2.0.0</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-slate-100">
            <span class="text-sm text-slate-500">{{ $t('settings.environment') }}</span>
            <span class="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">Production</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-slate-100">
            <span class="text-sm text-slate-500">Backend</span>
            <span class="text-sm font-medium text-slate-700">FastAPI + PostgreSQL</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-slate-100">
            <span class="text-sm text-slate-500">Frontend</span>
            <span class="text-sm font-medium text-slate-700">Vue 3 + Vite</span>
          </div>
          <div class="flex items-center justify-between py-2">
            <span class="text-sm text-slate-500">{{ $t('settings.lastUpdate') }}</span>
            <span class="text-sm font-medium text-slate-700">{{ new Date().toLocaleDateString('uz-UZ') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Bar -->
    <div class="flex items-center justify-between bg-white rounded-2xl border border-slate-200 p-4 sticky bottom-4">
      <div class="text-sm">
        <span v-if="hasChanges" class="text-amber-600 flex items-center gap-1">
          <AlertCircle class="w-4 h-4" />
          {{ $t('settings.unsavedChanges') }}
        </span>
        <span v-else class="text-emerald-600 flex items-center gap-1">
          <CheckCircle2 class="w-4 h-4" />
          {{ $t('settings.allSaved') }}
        </span>
      </div>
      <div class="flex gap-3">
        <button 
          @click="resetSettings"
          :disabled="!hasChanges || isSaving"
          class="px-5 py-2.5 border border-slate-200 text-slate-600 rounded-xl font-medium hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ $t('common.cancel') }}
        </button>
        <button 
          @click="saveSettings"
          :disabled="!hasChanges || isSaving"
          class="px-6 py-2.5 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
 * Super Admin SettingsView.vue
 * ============================
 * Backend API: GET /settings, PUT /settings
 * Barcha maydonlar real backend system_settings.py ga mos
 */

import api from '@/services/api'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
  AlertCircle,
  Brain,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  GraduationCap,
  Info,
  Loader2,
  Mail,
  MessageCircle,
  Monitor,
  Moon,
  Plug,
  RefreshCw,
  Save,
  Smartphone,
  Sun,
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'

const toast = useToastStore()
const { t } = useLanguageStore()

// State
const isLoading = ref(true)
const isRefreshing = ref(false)
const isSaving = ref(false)
const loadError = ref(null)

// Default settings matching backend SettingsResponse exactly
const defaultSettings = {
  institution_name: 'UniControl',
  institution_logo: null,
  institution_address: null,
  institution_phone: null,
  institution_email: null,
  academic_year: '2025-2026',
  semester: '2',
  attendance_threshold: 80,
  late_minutes_threshold: 15,
  working_hours_start: '08:00',
  working_hours_end: '18:00',
  telegram_bot_enabled: true,
  email_notifications_enabled: true,
  sms_notifications_enabled: false,
  ai_analysis_enabled: true,
  language: 'uz',
  timezone: 'Asia/Tashkent',
  theme: 'light',
}

const settings = reactive({ ...defaultSettings })
const originalSettings = ref({ ...defaultSettings })

// O'zgarishlar borligini tekshirish
const hasChanges = computed(() => {
  return JSON.stringify(settings) !== JSON.stringify(originalSettings.value)
})

// Sozlamalarni yuklash
const loadSettings = async () => {
  try {
    loadError.value = null
    isRefreshing.value = true
    
    const response = await api.getSettings()
    
    if (response) {
      Object.keys(defaultSettings).forEach(key => {
        if (response[key] !== undefined && response[key] !== null) {
          settings[key] = response[key]
        }
      })
    }
    
    originalSettings.value = { ...settings }
    
  } catch (err) {
    console.error('Error loading settings:', err)
    loadError.value = t('settings.loadError')
    toast.warning(t('settings.usingDefaults'))
  } finally {
    isLoading.value = false
    isRefreshing.value = false
  }
}

// Sozlamalarni saqlash
const saveSettings = async () => {
  try {
    isSaving.value = true
    
    // Faqat o'zgargan maydonlarni yuborish
    const changedData = {}
    Object.keys(defaultSettings).forEach(key => {
      if (JSON.stringify(settings[key]) !== JSON.stringify(originalSettings.value[key])) {
        changedData[key] = settings[key]
      }
    })
    
    if (Object.keys(changedData).length === 0) {
      toast.info(t('settings.noChanges'))
      return
    }
    
    const response = await api.updateSettings(changedData)
    
    if (response) {
      Object.keys(defaultSettings).forEach(key => {
        if (response[key] !== undefined) {
          settings[key] = response[key]
        }
      })
    }
    
    originalSettings.value = { ...settings }
    toast.success(t('settings.saved'))
    
  } catch (err) {
    console.error('Error saving settings:', err)
    if (err.message?.includes('403')) {
      toast.error(t('settings.noPermission'))
    } else {
      toast.error(t('settings.saveError'))
    }
  } finally {
    isSaving.value = false
  }
}

// O'zgarishlarni bekor qilish
const resetSettings = () => {
  Object.assign(settings, originalSettings.value)
  toast.info(t('settings.changesCancelled'))
}

onMounted(loadSettings)
</script>
