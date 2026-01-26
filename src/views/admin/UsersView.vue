<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Foydalanuvchilar boshqaruvi</h1>
        <p class="text-slate-500">Parollarni ko'rish va tiklash</p>
      </div>
    </div>

    <!-- Search Section -->
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
          <Search :size="24" class="text-violet-600" />
        </div>
        <div>
          <h2 class="font-semibold text-slate-800">Foydalanuvchi qidirish</h2>
          <p class="text-sm text-slate-500">Ism yoki familiya bo'yicha qidiring</p>
        </div>
      </div>
      
      <div class="flex gap-3">
        <div class="relative flex-1">
          <Search class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Ism familiya kiriting..."
            class="w-full rounded-xl border border-slate-200 py-3 pl-12 pr-4 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-400/20"
            @input="searchUsers"
          />
        </div>
        <select 
          v-model="filterRole"
          class="rounded-xl border border-slate-200 px-4 py-3 focus:border-violet-400 focus:outline-none"
        >
          <option value="">Barcha rollar</option>
          <option value="student">Talaba</option>
          <option value="leader">Guruh sardori</option>
          <option value="admin">Admin</option>
        </select>
      </div>
    </div>

    <!-- Results -->
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div class="border-b border-slate-100 bg-slate-50 p-4">
        <h3 class="font-semibold text-slate-700">
          Natijalar: {{ filteredUsers.length }} ta foydalanuvchi
        </h3>
      </div>
      
      <div v-if="filteredUsers.length === 0" class="p-12 text-center">
        <UserX :size="48" class="mx-auto mb-4 text-slate-300" />
        <p class="text-slate-500">Foydalanuvchi topilmadi</p>
        <p class="text-sm text-slate-400 mt-1">Boshqa so'z bilan qidirib ko'ring</p>
      </div>
      
      <div v-else class="divide-y divide-slate-100">
        <div 
          v-for="user in filteredUsers" 
          :key="user.id"
          class="p-4 hover:bg-slate-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <!-- Avatar -->
            <div 
              class="flex h-12 w-12 items-center justify-center rounded-xl text-lg font-bold text-white"
              :class="getRoleColor(user.role)"
            >
              {{ user.name.charAt(0) }}
            </div>
            
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <p class="font-semibold text-slate-800">{{ user.name }}</p>
                <span 
                  class="rounded-lg px-2 py-0.5 text-xs font-medium"
                  :class="getRoleBadge(user.role)"
                >
                  {{ getRoleLabel(user.role) }}
                </span>
              </div>
              <div class="mt-1 flex items-center gap-4 text-sm text-slate-500">
                <span v-if="user.studentId">ID: {{ user.studentId }}</span>
                <span v-if="user.group">Guruh: {{ user.group }}</span>
                <span v-if="user.phone">{{ user.phone }}</span>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center gap-2">
              <button 
                @click="viewPassword(user)"
                class="flex items-center gap-2 rounded-xl bg-violet-100 px-4 py-2 text-sm font-medium text-violet-700 transition-all hover:bg-violet-200"
              >
                <Eye :size="16" />
                Parolni ko'rish
              </button>
              <button 
                @click="resetPassword(user)"
                class="flex items-center gap-2 rounded-xl bg-amber-100 px-4 py-2 text-sm font-medium text-amber-700 transition-all hover:bg-amber-200"
              >
                <RefreshCw :size="16" />
                Tiklash
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Password View Modal -->
    <Teleport to="body">
      <div 
        v-if="showPasswordModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showPasswordModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">Foydalanuvchi ma'lumotlari</h2>
            <button @click="showPasswordModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div v-if="selectedUser" class="space-y-4">
            <div class="flex items-center gap-4 rounded-xl bg-slate-50 p-4">
              <div 
                class="flex h-14 w-14 items-center justify-center rounded-xl text-xl font-bold text-white"
                :class="getRoleColor(selectedUser.role)"
              >
                {{ selectedUser.name.charAt(0) }}
              </div>
              <div>
                <p class="font-semibold text-slate-800">{{ selectedUser.name }}</p>
                <p class="text-sm text-slate-500">{{ getRoleLabel(selectedUser.role) }}</p>
              </div>
            </div>
            
            <div class="space-y-3">
              <div class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Login</label>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-slate-800">{{ selectedUser.login || selectedUser.studentId || 'admin' }}</span>
                  <button 
                    @click="copyToClipboard(selectedUser.login || selectedUser.studentId || 'admin')"
                    class="text-slate-400 hover:text-violet-500"
                  >
                    <Copy :size="16" />
                  </button>
                </div>
              </div>
              
              <div class="rounded-xl border border-violet-200 bg-violet-50 p-4">
                <label class="mb-1 block text-xs font-medium text-violet-600">Parol</label>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-lg font-bold text-violet-700">{{ selectedUser.password || '123456' }}</span>
                  <button 
                    @click="copyToClipboard(selectedUser.password || '123456')"
                    class="text-violet-400 hover:text-violet-600"
                  >
                    <Copy :size="16" />
                  </button>
                </div>
              </div>
              
              <div v-if="selectedUser.phone" class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Telefon</label>
                <span class="text-slate-800">{{ selectedUser.phone }}</span>
              </div>
            </div>
            
            <div class="mt-4 rounded-xl bg-amber-50 p-4 text-sm text-amber-700">
              <div class="flex items-start gap-2">
                <AlertTriangle :size="18" class="mt-0.5 flex-shrink-0" />
                <p>Bu ma'lumotlarni faqat foydalanuvchining o'ziga bering. Xavfsizlik uchun parolni o'zgartirish tavsiya etiladi.</p>
              </div>
            </div>
          </div>
          
          <div class="mt-6">
            <button 
              @click="showPasswordModal = false"
              class="w-full rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200"
            >
              Yopish
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Reset Password Modal -->
    <Teleport to="body">
      <div 
        v-if="showResetModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showResetModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">Parolni tiklash</h2>
            <button @click="showResetModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div v-if="selectedUser" class="space-y-4">
            <div class="rounded-xl bg-slate-50 p-4 text-center">
              <p class="text-slate-600">
                <strong>{{ selectedUser.name }}</strong> uchun yangi parol o'rnating
              </p>
            </div>
            
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Yangi parol</label>
              <input 
                v-model="newPassword"
                type="text"
                placeholder="Yangi parol kiriting"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-400/20"
              />
            </div>
            
            <div class="flex gap-3">
              <button 
                @click="generatePassword"
                class="flex-1 rounded-xl border border-slate-200 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Avtomatik yaratish
              </button>
              <button 
                @click="newPassword = '123456'"
                class="flex-1 rounded-xl border border-slate-200 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Standart (123456)
              </button>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button 
              @click="showResetModal = false"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200"
            >
              Bekor qilish
            </button>
            <button 
              @click="confirmReset"
              :disabled="!newPassword"
              class="flex-1 rounded-xl bg-violet-500 py-3 font-medium text-white hover:bg-violet-600 disabled:opacity-50"
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
 * UsersView.vue - Foydalanuvchilar boshqaruvi
 * 
 * Admin imkoniyatlari:
 * - Foydalanuvchi qidirish (ism/familiya)
 * - Parolni ko'rish
 * - Parolni tiklash
 */

import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { useToastStore } from '@/stores/toast'
import {
  Search,
  Eye,
  RefreshCw,
  X,
  Copy,
  AlertTriangle,
  UserX
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

// State
const searchQuery = ref('')
const filterRole = ref('')
const showPasswordModal = ref(false)
const showResetModal = ref(false)
const selectedUser = ref(null)
const newPassword = ref('')

// Barcha foydalanuvchilar (talabalar + adminlar)
const allUsers = computed(() => {
  const users = []
  
  // Talabalar
  dataStore.students.forEach(student => {
    users.push({
      id: student.id,
      name: student.name,
      studentId: student.studentId,
      phone: student.phone,
      group: student.group,
      role: student.role || 'student',
      login: student.studentId,
      password: student.password || '123456'
    })
  })
  
  // Adminlar (mock)
  users.push({
    id: 'admin-1',
    name: 'Admin Adminov',
    role: 'admin',
    login: 'admin',
    password: 'admin123',
    phone: '+998 90 000 00 00'
  })
  
  return users
})

// Filtrlangan foydalanuvchilar
const filteredUsers = computed(() => {
  let result = allUsers.value
  
  // Qidiruv
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(u => 
      u.name.toLowerCase().includes(query) ||
      (u.studentId && u.studentId.toLowerCase().includes(query))
    )
  }
  
  // Rol filtri
  if (filterRole.value) {
    result = result.filter(u => u.role === filterRole.value)
  }
  
  return result
})

// Rol rangi
function getRoleColor(role) {
  const colors = {
    student: 'bg-gradient-to-br from-blue-400 to-blue-600',
    leader: 'bg-gradient-to-br from-emerald-400 to-emerald-600',
    admin: 'bg-gradient-to-br from-violet-400 to-violet-600'
  }
  return colors[role] || colors.student
}

// Rol badge
function getRoleBadge(role) {
  const badges = {
    student: 'bg-blue-100 text-blue-700',
    leader: 'bg-emerald-100 text-emerald-700',
    admin: 'bg-violet-100 text-violet-700'
  }
  return badges[role] || badges.student
}

// Rol nomi
function getRoleLabel(role) {
  const labels = {
    student: 'Talaba',
    leader: 'Guruh sardori',
    admin: 'Admin'
  }
  return labels[role] || 'Foydalanuvchi'
}

// Parolni ko'rish
function viewPassword(user) {
  selectedUser.value = user
  showPasswordModal.value = true
}

// Parolni tiklash
function resetPassword(user) {
  selectedUser.value = user
  newPassword.value = ''
  showResetModal.value = true
}

// Avtomatik parol
function generatePassword() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  let password = ''
  for (let i = 0; i < 8; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  newPassword.value = password
}

// Parolni tasdiqlash
function confirmReset() {
  if (!newPassword.value) return
  
  // Frontend demo - real backendda API chaqiriladi
  toast.success('Parol yangilandi', `${selectedUser.value.name} uchun yangi parol: ${newPassword.value}`)
  showResetModal.value = false
}

// Clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
  toast.info('Nusxalandi', 'Ma\'lumot clipboard\'ga nusxalandi')
}

// Qidiruv
function searchUsers() {
  // Avtomatik computed orqali ishlaydi
}
</script>
