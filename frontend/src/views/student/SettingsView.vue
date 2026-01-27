<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800">Sozlamalar</h1>
      <p class="text-slate-500">Ilova sozlamalari va shaxsiylashtirish</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-4">
      <!-- Appearance -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100">
            <Palette :size="20" class="text-purple-600" />
          </div>
          <h2 class="font-semibold text-slate-800">Ko'rinish</h2>
        </div>
        
        <div class="space-y-4">
          <!-- Theme -->
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Mavzu</p>
              <p class="text-sm text-slate-500">Ilova ranglar sxemasi</p>
            </div>
            <div class="flex gap-2">
              <button
                v-for="theme in themes"
                :key="theme.id"
                @click="selectedTheme = theme.id"
                class="flex items-center gap-2 rounded-xl px-4 py-2 transition-all"
                :class="selectedTheme === theme.id 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
              >
                <component :is="theme.icon" :size="18" />
                {{ theme.name }}
              </button>
            </div>
          </div>

          <!-- Accent Color -->
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Asosiy rang</p>
              <p class="text-sm text-slate-500">Interfeys aktsent rangi</p>
            </div>
            <div class="flex gap-2">
              <button
                v-for="color in accentColors"
                :key="color.id"
                @click="selectedAccent = color.id"
                class="h-8 w-8 rounded-full transition-all"
                :class="[color.class, selectedAccent === color.id ? 'ring-2 ring-offset-2 ring-slate-400' : '']"
              ></button>
            </div>
          </div>

          <!-- Font Size -->
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Shrift o'lchami</p>
              <p class="text-sm text-slate-500">Matn o'lchami</p>
            </div>
            <select
              v-model="fontSize"
              class="rounded-xl border border-slate-200 px-4 py-2 text-slate-700 focus:border-blue-400 focus:outline-none"
            >
              <option value="small">Kichik</option>
              <option value="medium">O'rtacha</option>
              <option value="large">Katta</option>
            </select>
          </div>
        </div>
      </div>

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
            class="rounded-xl border border-slate-200 px-4 py-2 text-slate-700 focus:border-blue-400 focus:outline-none"
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
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Email bildirishnomalar</p>
              <p class="text-sm text-slate-500">Elektron pochtaga xabar</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.email" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Davomat ogohlantirishi</p>
              <p class="text-sm text-slate-500">Davomat past bo'lganda xabar</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.attendance" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Jadval eslatmasi</p>
              <p class="text-sm text-slate-500">Darsdan oldin eslatma</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="notifications.schedule" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Privacy -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
            <Shield :size="20" class="text-green-600" />
          </div>
          <h2 class="font-semibold text-slate-800">Maxfiylik</h2>
        </div>
        
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Profilni ko'rsatish</p>
              <p class="text-sm text-slate-500">Boshqalar profilingizni ko'rsin</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="privacy.showProfile" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
            </label>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-800">Online holatini ko'rsatish</p>
              <p class="text-sm text-slate-500">Faolligingiz ko'rinsin</p>
            </div>
            <label class="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" v-model="privacy.showOnline" class="peer sr-only" />
              <div class="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-500 peer-checked:after:translate-x-full"></div>
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
          
          <button
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <Smartphone :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Ikki bosqichli tekshiruv</span>
            </div>
            <span class="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-600">O'chirilgan</span>
          </button>
          
          <button
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <History :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Kirish tarixi</span>
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
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <Download :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Ma'lumotlarni yuklab olish</span>
            </div>
            <ChevronRight :size="20" class="text-slate-400" />
          </button>
          
          <button
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
            @click="$router.push('/student/help')"
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <HelpCircle :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Yordam</span>
            </div>
            <ChevronRight :size="20" class="text-slate-400" />
          </button>
          
          <button
            class="flex w-full items-center justify-between rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex items-center gap-3">
              <FileText :size="20" class="text-slate-600" />
              <span class="font-medium text-slate-800">Foydalanish shartlari</span>
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
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Yangi parol</label>
              <input
                type="password"
                v-model="passwordForm.new"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Yangi parolni tasdiqlash</label>
              <input
                type="password"
                v-model="passwordForm.confirm"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
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
              class="flex-1 rounded-xl bg-blue-500 py-3 font-medium text-white hover:bg-blue-600"
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
import { ref } from 'vue'
import { useToastStore } from '@/stores/toast'
import {
  Palette, Globe, Bell, Shield, Lock, Database, Info, HelpCircle,
  Sun, Moon, Monitor, ChevronRight, Key, Smartphone, History,
  Download, Trash2, FileText, X
} from 'lucide-vue-next'

const toast = useToastStore()

// Theme
const selectedTheme = ref('light')
const themes = [
  { id: 'light', name: 'Yorug\'', icon: Sun },
  { id: 'dark', name: 'Qorong\'i', icon: Moon },
  { id: 'system', name: 'Tizim', icon: Monitor }
]

// Accent Colors
const selectedAccent = ref('blue')
const accentColors = [
  { id: 'blue', class: 'bg-blue-500' },
  { id: 'purple', class: 'bg-purple-500' },
  { id: 'green', class: 'bg-green-500' },
  { id: 'amber', class: 'bg-amber-500' },
  { id: 'rose', class: 'bg-rose-500' }
]

// Font Size
const fontSize = ref('medium')

// Language
const language = ref('uz')

// Notifications
const notifications = ref({
  push: true,
  email: false,
  attendance: true,
  schedule: true
})

// Privacy
const privacy = ref({
  showProfile: true,
  showOnline: false
})

// Password
const showChangePassword = ref(false)
const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

function changePassword() {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    toast.error('Parollar mos kelmadi')
    return
  }
  
  if (passwordForm.value.new.length < 6) {
    toast.error('Parol kamida 6 ta belgidan iborat bo\'lishi kerak')
    return
  }
  
  // Here you would send to API
  toast.success('Parol muvaffaqiyatli o\'zgartirildi')
  showChangePassword.value = false
  passwordForm.value = { current: '', new: '', confirm: '' }
}
</script>
