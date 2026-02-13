<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ t('settings.title') }}</h1>
      <p class="text-sm text-slate-500">{{ t('settings.appSettings') }}</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-4">
      <!-- Language -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
            <Globe :size="20" class="text-blue-600" />
          </div>
          <h2 class="font-semibold text-slate-800">{{ t('settings.language') }}</h2>
        </div>
        
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-slate-800">{{ t('settings.interfaceLanguage') }}</p>
            <p class="text-sm text-slate-500">{{ t('settings.displayLanguage') }}</p>
          </div>
          <select
            v-model="language"
            @change="onLanguageChange"
            class="rounded-xl border border-slate-200 px-4 py-2 text-slate-700 focus:border-emerald-400 focus:outline-none"
          >
            <option value="uz">{{ t('settings.uzbek') }}</option>
            <option value="ru">{{ t('settings.russian') }}</option>
            <option value="en">{{ t('settings.english') }}</option>
          </select>
        </div>
      </div>

      <!-- Notifications -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
            <Bell :size="20" class="text-amber-600" />
          </div>
          <h2 class="font-semibold text-slate-800">{{ t('settings.notifications') }}</h2>
        </div>
        
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">{{ t('settings.pushNotifications') }}</p>
              <p class="text-sm text-slate-500">{{ t('settings.pushDesc') }}</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.push" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">{{ t('settings.emailNotifications') }}</p>
              <p class="text-sm text-slate-500">{{ t('settings.emailDesc') }}</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.email" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">{{ t('settings.attendanceAlert') }}</p>
              <p class="text-sm text-slate-500">{{ t('settings.attendanceAlertDesc') }}</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.attendance" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">{{ t('settings.scheduleReminder') }}</p>
              <p class="text-sm text-slate-500">{{ t('settings.scheduleReminderDesc') }}</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.schedule" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Security -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-100">
            <Lock :size="20" class="text-red-600" />
          </div>
          <h2 class="font-semibold text-slate-800">{{ t('settings.security') }}</h2>
        </div>
        
        <div class="space-y-3">
          <button
            @click="showChangePassword = true"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <Key :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">{{ t('settings.changePassword') }}</span>
            </div>
            <ChevronRight :size="20" class="text-slate-400" />
          </button>
        </div>
      </div>

      <!-- Data -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100">
            <Database :size="20" class="text-indigo-600" />
          </div>
          <h2 class="font-semibold text-slate-800">{{ t('settings.data') }}</h2>
        </div>
        
        <div class="space-y-3">
          <button
            @click="downloadData"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <Download :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">{{ t('settings.downloadData') }}</span>
            </div>
            <ChevronRight :size="20" class="text-slate-400" />
          </button>
          
          <button
            @click="clearCache"
            class="flex w-full items-center justify-between rounded-xl bg-red-50 p-4 transition-all hover:bg-red-100"
          >
            <div class="flex items-center gap-3">
              <Trash2 :size="20" class="text-red-600" />
              <span class="font-medium text-red-600">{{ t('settings.clearCache') }}</span>
            </div>
            <span class="text-sm text-red-500">45 MB</span>
          </button>
        </div>
      </div>

      <!-- About -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100">
            <Info :size="20" class="text-slate-600" />
          </div>
          <h2 class="font-semibold text-slate-800">{{ t('settings.aboutApp') }}</h2>
        </div>
        
        <div class="space-y-3">
          <div class="flex items-center justify-between rounded-xl bg-slate-50 p-4">
            <span class="text-slate-600">{{ t('common.version') }}</span>
            <span class="font-medium text-slate-800">1.0.0</span>
          </div>
          
          <button
            @click="goToHelp"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <HelpCircle :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">{{ t('common.help') }}</span>
            </div>
            <ChevronRight :size="20" class="text-slate-400" />
          </button>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <Teleport to="body">
      <div
        v-if="showChangePassword"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showChangePassword = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">{{ t('settings.changePassword') }}</h2>
            <button @click="showChangePassword = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ t('settings.currentPassword') }}</label>
              <input
                type="password"
                v-model="passwordForm.current"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ t('settings.newPassword') }}</label>
              <input
                type="password"
                v-model="passwordForm.new"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ t('settings.confirmPassword') }}</label>
              <input
                type="password"
                v-model="passwordForm.confirm"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button
              @click="showChangePassword = false"
              :disabled="isChangingPassword"
              class="flex-1 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="changePassword"
              :disabled="isChangingPassword"
              class="flex-1 rounded-xl bg-emerald-500 py-3 font-medium text-white hover:bg-emerald-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Loader2 v-if="isChangingPassword" class="w-5 h-5 animate-spin" />
              <span>{{ isChangingPassword ? t('settings.saving') : t('common.save') }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * SettingsView.vue - Sozlamalar sahifasi
 * 
 * Mavjud bo'limlar:
 * 1. Til - O'zbekcha, Ruscha, Inglizcha
 * 2. Bildirishnomalar - Push, Email, Davomat, Jadval
 * 3. Xavfsizlik - Parol o'zgartirish
 * 4. Ma'lumotlar - Yuklab olish, Kesh tozalash
 * 5. Ilova haqida - Versiya, Yordam
 */

import { useAuthStore } from '@/stores/auth'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    Bell,
    ChevronRight,
    Database,
    Download,
    Globe,
    HelpCircle,
    Info,
    Key,
    Loader2,
    Lock,
    Trash2, X
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()
const toast = useToastStore()
const authStore = useAuthStore()
const langStore = useLanguageStore()
const { t } = langStore

// ============ TIL ============
const language = ref(langStore.locale)

function onLanguageChange() {
  langStore.setLocale(language.value)
  toast.success(t('common.success'))
}

// ============ BILDIRISHNOMALAR ============
const notifications = ref({
  push: true,
  email: false,
  attendance: true,
  schedule: true
})

// ============ PAROL ============
const showChangePassword = ref(false)
const isChangingPassword = ref(false)
const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

async function changePassword() {
  if (!passwordForm.value.current) {
    toast.error(t('settings.enterCurrentPassword'))
    return
  }
  
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    toast.error(t('settings.passwordMismatch'))
    return
  }
  
  if (passwordForm.value.new.length < 6) {
    toast.error(t('settings.passwordMinLength'))
    return
  }
  
  isChangingPassword.value = true
  
  try {
    await api.changePassword(passwordForm.value.current, passwordForm.value.new)
    toast.success(t('settings.passwordChanged'))
    showChangePassword.value = false
    passwordForm.value = { current: '', new: '', confirm: '' }
  } catch (e) {
    console.error('Error changing password:', e)
    const errorMsg = e.response?.data?.detail || t('settings.passwordError')
    toast.error(errorMsg)
  } finally {
    isChangingPassword.value = false
  }
}

// ============ MA'LUMOTLAR ============
async function downloadData() {
  toast.info(t('settings.downloading'))
  
  try {
    const response = await api.exportToExcel('students', { my_data: true })
    
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'my_data.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    toast.success(t('settings.downloadComplete'))
  } catch (e) {
    console.error('Error downloading data:', e)
    toast.info(t('settings.downloadUnavailable'))
  }
}

function clearCache() {
  localStorage.removeItem('unicontrol_cache')
  localStorage.removeItem('unicontrol_data_cache')
  toast.success(t('settings.cacheCleared'))
}

// ============ YORDAM ============
const helpPath = computed(() => {
  if (authStore.isLeader) return '/leader/help'
  if (authStore.isStudent) return '/student/help'
  if (authStore.isAdmin) return '/admin/help'
  if (authStore.isSuperAdmin) return '/super/help'
  return '/student/help'
})

function goToHelp() {
  router.push(helpPath.value)
}
</script>
