<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Adminlar boshqaruvi</h1>
        <p class="text-slate-500">{{ admins.length }} ta admin</p>
      </div>
      <button 
        @click="openModal()"
        class="px-4 py-2.5 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2"
      >
        <UserPlus class="w-5 h-5" />
        Yangi admin
      </button>
    </div>

    <!-- Admins Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="admin in admins" 
        :key="admin.id"
        class="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-4">
            <div 
              class="w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold"
              :class="admin.role === 'super' ? 'bg-gradient-to-br from-amber-500 to-orange-600' : 'bg-gradient-to-br from-violet-500 to-purple-600'"
            >
              {{ admin.name.charAt(0) }}
            </div>
            <div>
              <h3 class="font-semibold text-slate-800">{{ admin.name }}</h3>
              <p class="text-sm text-slate-500">{{ admin.email }}</p>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Shield class="w-4 h-4" />
              Rol
            </span>
            <span 
              class="px-2 py-0.5 rounded-lg text-xs font-medium"
              :class="admin.role === 'super' ? 'bg-amber-100 text-amber-700' : 'bg-violet-100 text-violet-700'"
            >
              {{ admin.role === 'super' ? 'Super Admin' : 'Admin' }}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Calendar class="w-4 h-4" />
              Qo'shilgan
            </span>
            <span class="text-slate-700">{{ formatDate(admin.createdAt) }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Activity class="w-4 h-4" />
              Holat
            </span>
            <span 
              class="flex items-center gap-1 font-medium"
              :class="admin.active ? 'text-emerald-600' : 'text-slate-400'"
            >
              <span class="w-2 h-2 rounded-full" :class="admin.active ? 'bg-emerald-500' : 'bg-slate-300'"></span>
              {{ admin.active ? 'Faol' : 'Nofaol' }}
            </span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-100 flex gap-2">
          <button 
            @click="openModal(admin)"
            class="flex-1 px-3 py-2 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
          >
            <Pencil class="w-4 h-4" />
            Tahrirlash
          </button>
          <button 
            v-if="admin.role !== 'super'"
            @click="confirmDelete(admin)"
            class="px-3 py-2 bg-rose-100 text-rose-700 rounded-xl text-sm font-medium hover:bg-rose-200 transition-colors"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800">
              {{ editingAdmin ? 'Adminni tahrirlash' : 'Yangi admin qo\'shish' }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveAdmin" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">F.I.O</label>
              <input 
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                placeholder="Ism familiya"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Email</label>
              <input 
                v-model="form.email"
                type="email"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                placeholder="admin@example.com"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Username</label>
              <input 
                v-model="form.username"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                placeholder="admin_username"
              />
            </div>
            <div v-if="!editingAdmin">
              <label class="block text-sm font-medium text-slate-700 mb-2">Parol</label>
              <input 
                v-model="form.password"
                type="password"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Rol</label>
              <select 
                v-model="form.role"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              >
                <option value="admin">Admin</option>
                <option value="super">Super Admin</option>
              </select>
            </div>
            <div class="flex items-center gap-3">
              <input 
                v-model="form.active"
                type="checkbox"
                id="active"
                class="w-5 h-5 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
              />
              <label for="active" class="text-sm text-slate-700">Faol</label>
            </div>
            <div class="flex gap-3 pt-4">
              <button 
                type="button"
                @click="showModal = false"
                class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
              >
                Bekor qilish
              </button>
              <button 
                type="submit"
                class="flex-1 px-4 py-3 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors"
              >
                Saqlash
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Delete Confirmation -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showDeleteConfirm = false"
      >
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 text-center">
          <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle class="w-8 h-8 text-rose-500" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 mb-2">O'chirishni tasdiqlang</h3>
          <p class="text-slate-500 mb-6">
            {{ deletingAdmin?.name }} adminini o'chirmoqchimisiz?
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              @click="deleteAdmin"
              class="flex-1 px-4 py-3 bg-rose-500 text-white rounded-xl font-medium hover:bg-rose-600 transition-colors"
            >
              O'chirish
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {
  UserPlus,
  Shield,
  Calendar,
  Activity,
  Pencil,
  Trash2,
  X,
  AlertTriangle
} from 'lucide-vue-next'

const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingAdmin = ref(null)
const deletingAdmin = ref(null)

const admins = ref([
  { id: 1, name: 'Super Admin', email: 'super@uni.uz', username: 'super', role: 'super', active: true, createdAt: '2024-01-15' },
  { id: 2, name: 'Admin User', email: 'admin@uni.uz', username: 'admin', role: 'admin', active: true, createdAt: '2024-02-20' },
  { id: 3, name: 'Sardor Aliyev', email: 'sardor@uni.uz', username: 'sardor', role: 'admin', active: true, createdAt: '2024-03-10' }
])

const form = reactive({
  name: '',
  email: '',
  username: '',
  password: '',
  role: 'admin',
  active: true
})

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const openModal = (admin = null) => {
  if (admin) {
    editingAdmin.value = admin
    form.name = admin.name
    form.email = admin.email
    form.username = admin.username
    form.role = admin.role
    form.active = admin.active
    form.password = ''
  } else {
    editingAdmin.value = null
    form.name = ''
    form.email = ''
    form.username = ''
    form.password = ''
    form.role = 'admin'
    form.active = true
  }
  showModal.value = true
}

const saveAdmin = () => {
  if (editingAdmin.value) {
    const index = admins.value.findIndex(a => a.id === editingAdmin.value.id)
    if (index !== -1) {
      admins.value[index] = {
        ...admins.value[index],
        name: form.name,
        email: form.email,
        username: form.username,
        role: form.role,
        active: form.active
      }
    }
  } else {
    admins.value.push({
      id: Date.now(),
      name: form.name,
      email: form.email,
      username: form.username,
      role: form.role,
      active: form.active,
      createdAt: new Date().toISOString()
    })
  }
  showModal.value = false
}

const confirmDelete = (admin) => {
  deletingAdmin.value = admin
  showDeleteConfirm.value = true
}

const deleteAdmin = () => {
  if (deletingAdmin.value) {
    admins.value = admins.value.filter(a => a.id !== deletingAdmin.value.id)
  }
  showDeleteConfirm.value = false
  deletingAdmin.value = null
}
</script>
