<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800">Sozlamalar</h1>
      <p class="text-slate-500">Ilova sozlamalari</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-4">
      <!-- Language -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
            <Globe :size="20" class="text-blue-600" />
          </div>
          <h2 class="font-semibold text-slate-800">Til</h2>
        </div>
        
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-slate-800">Interfeys tili</p>
            <p class="text-sm text-slate-500">Ilova ko'rsatish tili</p>
          </div>
          <select
            v-model="language"
            class="rounded-xl border border-slate-200 px-4 py-2 text-slate-700 focus:border-emerald-400 focus:outline-none"
          >
            <option value="uz">O'zbekcha</option>
            <option value="ru">Русский</option>
            <option value="en">English</option>
          </select>
        </div>
      </div>

      <!-- Notifications -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
            <Bell :size="20" class="text-amber-600" />
          </div>
          <h2 class="font-semibold text-slate-800">Bildirishnomalar</h2>
        </div>
        
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Push bildirishnomalar</p>
              <p class="text-sm text-slate-500">Telefonga xabar yuborish</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.push" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Email bildirishnomalar</p>
              <p class="text-sm text-slate-500">Elektron pochtaga xabar</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.email" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Davomat ogohlantirishi</p>
              <p class="text-sm text-slate-500">Davomat past bo'lganda xabar</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.attendance" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Jadval eslatmasi</p>
              <p class="text-sm text-slate-500">Darsdan oldin eslatma</p>
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
          <h2 class="font-semibold text-slate-800">Xavfsizlik</h2>
        </div>
        
        <div class="space-y-3">
          <button
            @click="showChangePassword = true"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <Key :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Parolni o'zgartirish</span>
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
          <h2 class="font-semibold text-slate-800">Ma'lumotlar</h2>
        </div>
        
        <div class="space-y-3">
          <button
            @click="downloadData"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <Download :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Ma'lumotlarni yuklab olish</span>
            </div>
            <ChevronRight :size="20" class="text-slate-400" />
          </button>
          
          <button
            @click="clearCache"
            class="flex w-full items-center justify-between rounded-xl bg-red-50 p-4 transition-all hover:bg-red-100"
          >
            <div class="flex items-center gap-3">
              <Trash2 :size="20" class="text-red-600" />
              <span class="font-medium text-red-600">Keshni tozalash</span>
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
          <h2 class="font-semibold text-slate-800">Ilova haqida</h2>
        </div>
        
        <div class="space-y-3">
          <div class="flex items-center justify-between rounded-xl bg-slate-50 p-4">
            <span class="text-slate-600">Versiya</span>
            <span class="font-medium text-slate-800">1.0.0</span>
          </div>
          
          <button
            @click="goToHelp"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <HelpCircle :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Yordam</span>
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
            <h2 class="text-lg font-bold text-slate-800">Parolni o'zgartirish</h2>
            <button @click="showChangePassword = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Joriy parol</label>
              <input
                type="password"
                v-model="passwordForm.current"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Yangi parol</label>
              <input
                type="password"
                v-model="passwordForm.new"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-emerald-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Yangi parolni tasdiqlash</label>
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
              class="flex-1 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 hover:bg-slate-50"
            >
              Bekor qilish
            </button>
            <button
              @click="changePassword"
              class="flex-1 rounded-xl bg-emerald-500 py-3 font-medium text-white hover:bg-emerald-600"
            >
              Saqlash
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

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'
import {
  Globe, Bell, Lock, Database, Info, HelpCircle,
  ChevronRight, Key, Download, Trash2, X
} from 'lucide-vue-next'

const router = useRouter()
const toast = useToastStore()
const authStore = useAuthStore()

// ============ TIL ============
const language = ref('uz')

// ============ BILDIRISHNOMALAR ============
const notifications = ref({
  push: true,
  email: false,
  attendance: true,
  schedule: true
})

// ============ PAROL ============
const showChangePassword = ref(false)
const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

function changePassword() {
  if (!passwordForm.value.current) {
    toast.error('Joriy parolni kiriting')
    return
  }
  
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    toast.error('Yangi parollar mos kelmadi')
    return
  }
  
  if (passwordForm.value.new.length < 6) {
    toast.error('Parol kamida 6 ta belgidan iborat bo\'lishi kerak')
    return
  }
  
  toast.success('Parol muvaffaqiyatli o\'zgartirildi')
  showChangePassword.value = false
  passwordForm.value = { current: '', new: '', confirm: '' }
}

// ============ MA'LUMOTLAR ============
function downloadData() {
  toast.info('Ma\'lumotlar yuklab olinmoqda...')
}

function clearCache() {
  toast.success('Kesh tozalandi')
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
