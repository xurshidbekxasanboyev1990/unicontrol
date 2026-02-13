<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('settings.title') }}</h1>
      <p class="text-sm text-slate-500">{{ $t('settings.appSettings') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-amber-500 animate-spin" />
      <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
      <AlertCircle class="w-12 h-12 text-red-400 mx-auto mb-3" />
      <p class="text-red-600 mb-4">{{ error }}</p>
      <button @click="loadSettings" class="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors flex items-center gap-2 mx-auto">
        <RefreshCw class="w-4 h-4" />
        {{ $t('common.retry') }}
      </button>
    </div>

    <template v-else>

    <!-- Settings Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- General Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Settings class="w-5 h-5 text-slate-400" />
          {{ $t('settings.generalSettings') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.systemName') }}</label>
            <input 
              v-model="settings.systemName"
              type="text"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.universityName') }}</label>
            <input 
              v-model="settings.universityName"
              type="text"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.academicYear') }}</label>
            <select 
              v-model="settings.academicYear"
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
        </div>
      </div>

      <!-- Attendance Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <ClipboardCheck class="w-5 h-5 text-slate-400" />
          {{ $t('settings.attendanceSettings') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.minAttendancePercent') }}</label>
            <input 
              v-model="settings.minAttendance"
              type="number"
              min="0"
              max="100"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.lateThreshold') }}</label>
            <input 
              v-model="settings.lateThreshold"
              type="number"
              min="0"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            />
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.autoWarning') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.autoWarningDesc') }}</p>
            </div>
            <button 
              @click="settings.autoWarning = !settings.autoWarning"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.autoWarning ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.autoWarning ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.weekendAttendance') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.weekendAttendanceDesc') }}</p>
            </div>
            <button 
              @click="settings.weekendAttendance = !settings.weekendAttendance"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.weekendAttendance ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.weekendAttendance ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Bell class="w-5 h-5 text-slate-400" />
          {{ $t('settings.notificationSettings') }}
        </h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.emailNotifications') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.emailNotificationsDesc') }}</p>
            </div>
            <button 
              @click="settings.emailNotifications = !settings.emailNotifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.emailNotifications ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.emailNotifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.smsNotifications') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.smsNotificationsDesc') }}</p>
            </div>
            <button 
              @click="settings.smsNotifications = !settings.smsNotifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.smsNotifications ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.smsNotifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.pushNotifications') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.pushNotificationsDesc') }}</p>
            </div>
            <button 
              @click="settings.pushNotifications = !settings.pushNotifications"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.pushNotifications ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.pushNotifications ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Shield class="w-5 h-5 text-slate-400" />
          {{ $t('settings.securitySettings') }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('settings.sessionTimeout') }}</label>
            <input 
              v-model="settings.sessionTimeout"
              type="number"
              min="5"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
            />
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.twoFactorAuth') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.twoFactorAuthDesc') }}</p>
            </div>
            <button 
              @click="settings.twoFactorAuth = !settings.twoFactorAuth"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.twoFactorAuth ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.twoFactorAuth ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
            <div>
              <p class="font-medium text-slate-700">{{ $t('settings.ipRestriction') }}</p>
              <p class="text-sm text-slate-500">{{ $t('settings.ipRestrictionDesc') }}</p>
            </div>
            <button 
              @click="settings.ipRestriction = !settings.ipRestriction"
              class="w-12 h-6 rounded-full transition-colors"
              :class="settings.ipRestriction ? 'bg-amber-500' : 'bg-slate-300'"
            >
              <div 
                class="w-5 h-5 bg-white rounded-full shadow transition-transform"
                :class="settings.ipRestriction ? 'translate-x-6' : 'translate-x-0.5'"
              ></div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end">
      <button 
        @click="saveSettings"
        :disabled="saving"
        class="px-6 py-3 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Loader2 v-if="saving" class="w-5 h-5 animate-spin" />
        <Save v-else class="w-5 h-5" />
        {{ saving ? $t('settings.saving') : $t('common.save') }}
      </button>
    </div>
    </template>

    <!-- Success Toast -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div 
        v-if="showSuccess"
        class="fixed bottom-6 right-6 bg-emerald-500 text-white px-6 py-4 rounded-2xl shadow-lg flex items-center gap-3"
      >
        <CheckCircle class="w-5 h-5" />
        <span class="font-medium">{{ $t('common.success') }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import api from '@/services/api'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    AlertCircle,
    Bell,
    CheckCircle,
    ClipboardCheck,
    Loader2,
    RefreshCw,
    Save,
    Settings,
    Shield
} from 'lucide-vue-next'
import { onMounted, reactive, ref } from 'vue'

const toast = useToastStore()
const langStore = useLanguageStore()
const { t } = langStore
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const showSuccess = ref(false)

const settings = reactive({
  systemName: 'Uni Control',
  universityName: '',
  academicYear: '2024-2025',
  semester: '1',
  minAttendance: 70,
  lateThreshold: 15,
  autoWarning: true,
  weekendAttendance: false,
  emailNotifications: true,
  smsNotifications: false,
  pushNotifications: true,
  sessionTimeout: 30,
  twoFactorAuth: false,
  ipRestriction: false
})

const loadSettings = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.getSettings()
    if (response) {
      // response.data emas, to'g'ridan-to'g'ri response
      Object.assign(settings, response)
    }
  } catch (err) {
    console.error('Error loading settings:', err)
    error.value = t('common.error')
    // Keep defaults if API fails
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await api.updateSettings({ ...settings })
    showSuccess.value = true
    toast.success(t('common.success'))
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
  } catch (err) {
    console.error('Error saving settings:', err)
    toast.error(t('common.error'))
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>
