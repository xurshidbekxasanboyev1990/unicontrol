<template>
  <div class="space-y-6">
    <!-- Profile card -->
    <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
      <div class="flex items-center gap-5 mb-6">
        <div class="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-3xl font-bold text-white">
          {{ profile.name?.charAt(0) || '?' }}
        </div>
        <div>
          <h2 class="text-xl font-bold text-gray-900">{{ profile.name }}</h2>
          <p class="text-sm text-gray-500">{{ profile.login }}</p>
          <span class="mt-1 inline-block rounded-full bg-blue-100 px-3 py-0.5 text-xs font-medium text-blue-600">
            {{ t('roles.teacher') }}
          </span>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('common.name') }}</label>
          <input v-model="form.name" type="text" class="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500" />
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('common.email') }}</label>
          <input v-model="form.email" type="email" class="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500" />
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('common.phone') }}</label>
          <input v-model="form.phone" type="tel" class="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500" />
        </div>
      </div>

      <div class="mt-4 flex justify-end">
        <button
          @click="updateProfile"
          :disabled="saving"
          class="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <Loader2 v-if="saving" :size="16" class="animate-spin" />
          {{ t('common.save') }}
        </button>
      </div>
    </div>

    <!-- Change password -->
    <div class="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
      <h3 class="mb-4 text-lg font-semibold text-gray-900">{{ t('teacher.changePassword') }}</h3>
      
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('teacher.currentPassword') }}</label>
          <input v-model="passwords.current" type="password" class="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500" />
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('teacher.newPassword') }}</label>
          <input v-model="passwords.newPass" type="password" class="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500" />
        </div>
      </div>

      <div class="mt-4 flex justify-end">
        <button
          @click="changePassword"
          :disabled="changingPass"
          class="rounded-xl bg-orange-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-orange-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <Loader2 v-if="changingPass" :size="16" class="animate-spin" />
          {{ t('teacher.changePassword') }}
        </button>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { Loader2 } from 'lucide-vue-next'
import { onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(true)
const saving = ref(false)
const changingPass = ref(false)
const toast = ref(null)

const profile = ref({})
const form = reactive({ name: '', email: '', phone: '' })
const passwords = reactive({ current: '', newPass: '' })

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await api.request('/teacher/profile')
    profile.value = res
    form.name = res.name || ''
    form.email = res.email || ''
    form.phone = res.phone || ''
  } catch (err) {
    console.error('Profile error:', err)
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  saving.value = true
  try {
    await api.request('/teacher/profile', {
      method: 'PUT',
      body: { name: form.name, email: form.email, phone: form.phone }
    })
    profile.value.name = form.name
    showToast(t('teacher.profileUpdated'))
  } catch (err) {
    showToast(err.data?.detail || t('common.error'), 'error')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (!passwords.current || !passwords.newPass) {
    showToast(t('teacher.fillAllFields'), 'error')
    return
  }
  changingPass.value = true
  try {
    await api.request('/teacher/change-password', {
      method: 'POST',
      body: { current_password: passwords.current, new_password: passwords.newPass }
    })
    passwords.current = ''
    passwords.newPass = ''
    showToast(t('teacher.passwordChanged'))
  } catch (err) {
    showToast(err.data?.detail || t('common.error'), 'error')
  } finally {
    changingPass.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
