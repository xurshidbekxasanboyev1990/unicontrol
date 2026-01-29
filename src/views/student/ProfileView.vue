<template>
  <div class="space-y-6">
    <!-- Profile Header -->
    <div class="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
      <div class="flex flex-col sm:flex-row items-center gap-6">
        <div class="relative">
          <div class="w-24 h-24 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center text-4xl font-bold">
            {{ student?.name?.charAt(0) || 'U' }}
          </div>
          <button class="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-lg shadow-lg flex items-center justify-center text-emerald-600 hover:bg-emerald-50 transition-colors">
            <Camera class="w-4 h-4" />
          </button>
        </div>
        <div class="text-center sm:text-left">
          <h1 class="text-2xl font-bold">{{ student?.name }}</h1>
          <p class="text-emerald-100 mt-1">{{ student?.studentId }}</p>
          <div class="flex items-center justify-center sm:justify-start gap-2 mt-3">
            <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
              {{ student?.group || 'KI_25-04' }}
            </span>
            <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
              Talaba
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Contract Status -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-slate-800">Kontrakt holati</h2>
        <span 
          class="px-3 py-1 rounded-lg text-sm font-medium"
          :class="contractPercent >= 100 ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
        >
          {{ contractPercent >= 100 ? 'To\'liq to\'langan' : 'Qisman to\'langan' }}
        </span>
      </div>
      
      <div class="grid grid-cols-3 gap-4 mb-4">
        <div class="text-center p-4 bg-slate-50 rounded-xl">
          <p class="text-2xl font-bold text-slate-800">{{ formatMoney(contractAmount) }}</p>
          <p class="text-sm text-slate-500 mt-1">Kontrakt</p>
        </div>
        <div class="text-center p-4 bg-emerald-50 rounded-xl">
          <p class="text-2xl font-bold text-emerald-600">{{ formatMoney(student?.contractPaid || 0) }}</p>
          <p class="text-sm text-slate-500 mt-1">To'langan</p>
        </div>
        <div class="text-center p-4 bg-rose-50 rounded-xl">
          <p class="text-2xl font-bold text-rose-600">{{ formatMoney(debt) }}</p>
          <p class="text-sm text-slate-500 mt-1">Qoldiq</p>
        </div>
      </div>

      <div class="relative">
        <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
            :style="{ width: Math.min(contractPercent, 100) + '%' }"
          ></div>
        </div>
        <div class="flex justify-between mt-2 text-sm">
          <span class="text-slate-500">0%</span>
          <span class="font-semibold text-emerald-600">{{ contractPercent }}%</span>
          <span class="text-slate-500">100%</span>
        </div>
      </div>
    </div>

    <!-- Info Cards -->
    <div class="grid md:grid-cols-2 gap-6">
      <!-- Personal Info (Read-only) -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center gap-2 mb-6">
          <UserCircle class="w-5 h-5 text-emerald-500" />
          <h2 class="text-lg font-semibold text-slate-800">Shaxsiy ma'lumotlar</h2>
          <Lock class="w-4 h-4 text-slate-400 ml-auto" />
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">F.I.O</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.name }}</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Talaba ID</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.studentId }}</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Pasport</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.passport || 'AA 1234567' }}</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">JSHSHIR</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.jshshir || '12345678901234' }}</p>
          </div>
        </div>

        <div class="mt-4 p-3 bg-amber-50 rounded-xl flex items-start gap-2">
          <AlertCircle class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <p class="text-sm text-amber-700">Bu ma'lumotlarni faqat admin o'zgartira oladi</p>
        </div>
      </div>

      <!-- Editable Info -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center gap-2 mb-6">
          <Settings class="w-5 h-5 text-emerald-500" />
          <h2 class="text-lg font-semibold text-slate-800">Tahrirlash mumkin</h2>
        </div>
        
        <form @submit.prevent="saveProfile" class="space-y-4">
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Telefon</label>
            <div class="relative mt-1">
              <Phone class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.phone"
                type="tel"
                class="w-full pl-11 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
                placeholder="+998 90 123 45 67"
              />
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Manzil</label>
            <div class="relative mt-1">
              <MapPin class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.address"
                type="text"
                class="w-full pl-11 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
                placeholder="Toshkent sh., ..."
              />
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Transport</label>
            <div class="relative mt-1">
              <Bus class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.commute"
                type="text"
                class="w-full pl-11 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
                placeholder="Metro, Avtobus, ..."
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="isSaving"
            class="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-2.5 rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Loader2 v-if="isSaving" class="w-5 h-5 animate-spin" />
            <Save v-else class="w-5 h-5" />
            <span>{{ isSaving ? 'Saqlanmoqda...' : 'Saqlash' }}</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Change Password -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <div class="flex items-center gap-2 mb-6">
        <KeyRound class="w-5 h-5 text-emerald-500" />
        <h2 class="text-lg font-semibold text-slate-800">Parolni o'zgartirish</h2>
      </div>

      <form @submit.prevent="changePassword" class="grid md:grid-cols-3 gap-4">
        <div>
          <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Joriy parol</label>
          <div class="relative mt-1">
            <input
              v-model="passwordForm.current"
              :type="showPasswords.current ? 'text' : 'password'"
              class="w-full pl-4 pr-11 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
              placeholder="••••••"
            />
            <button
              type="button"
              @click="showPasswords.current = !showPasswords.current"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <EyeOff v-if="showPasswords.current" class="w-5 h-5" />
              <Eye v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">Yangi parol</label>
          <div class="relative mt-1">
            <input
              v-model="passwordForm.new"
              :type="showPasswords.new ? 'text' : 'password'"
              class="w-full pl-4 pr-11 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
              placeholder="••••••"
            />
            <button
              type="button"
              @click="showPasswords.new = !showPasswords.new"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <EyeOff v-if="showPasswords.new" class="w-5 h-5" />
              <Eye v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">&nbsp;</label>
          <button
            type="submit"
            class="w-full mt-1 bg-slate-800 hover:bg-slate-900 text-white font-semibold py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            <KeyRound class="w-5 h-5" />
            <span>O'zgartirish</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Success Toast -->
    <Transition name="slide">
      <div
        v-if="showToast"
        class="fixed bottom-6 right-6 bg-emerald-500 text-white px-6 py-4 rounded-xl shadow-lg flex items-center gap-3"
      >
        <CheckCircle class="w-5 h-5" />
        <span>{{ toastMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import api from '../../services/api'
import {
  Camera,
  UserCircle,
  Lock,
  Settings,
  Phone,
  MapPin,
  Bus,
  Save,
  Loader2,
  KeyRound,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle
} from 'lucide-vue-next'

const authStore = useAuthStore()
const toast = useToastStore()

// State
const loading = ref(true)
const error = ref(null)
const student = ref(null)
const group = ref(null)

// Load profile data
const loadProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Get current user profile from API
    const response = await api.getMe()
    student.value = response
    
    // Get group info if student has a group
    if (response.group_id) {
      try {
        const groupResponse = await api.getGroup(response.group_id)
        group.value = groupResponse
      } catch (e) {
        console.warn('Could not load group info:', e)
      }
    }
    
    // Initialize form with current data
    if (student.value) {
      form.phone = student.value.phone || ''
      form.address = student.value.address || ''
      form.commute = student.value.commute || ''
    }
  } catch (e) {
    console.error('Error loading profile:', e)
    error.value = 'Profil ma\'lumotlarini yuklashda xatolik'
    
    // Fallback to auth store user data
    if (authStore.user) {
      student.value = {
        id: authStore.user.student_id || authStore.user.id,
        name: authStore.user.name || authStore.user.full_name,
        student_id: authStore.user.email,
        phone: authStore.user.phone || '',
        address: authStore.user.address || '',
        commute: authStore.user.commute || '',
        passport: authStore.user.passport || '-',
        jshshir: authStore.user.jshshir || '-',
        group_id: authStore.user.group_id,
        contract_paid: authStore.user.contract_paid || 0
      }
    }
  } finally {
    loading.value = false
  }
}

// Contract calculations
const contractAmount = computed(() => group.value?.contract_amount || 18411000)
const debt = computed(() => {
  if (!group.value) return 0
  return Math.max(0, contractAmount.value - (student.value?.contract_paid || 0))
})
const contractPercent = computed(() => {
  if (!group.value) return 100
  return Math.round((student.value?.contract_paid || 0) / contractAmount.value * 100)
})

const form = reactive({
  phone: '',
  address: '',
  commute: ''
})

// Watch for student changes
watch(student, (newVal) => {
  if (newVal) {
    form.phone = newVal.phone || ''
    form.address = newVal.address || ''
    form.commute = newVal.commute || ''
  }
}, { immediate: true })

const passwordForm = reactive({
  current: '',
  new: ''
})

const showPasswords = reactive({
  current: false,
  new: false
})

const isSaving = ref(false)
const isChangingPassword = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const formatMoney = (amount) => {
  return new Intl.NumberFormat('uz-UZ').format(amount) + ' so\'m'
}

const saveProfile = async () => {
  if (!student.value?.id) {
    toast.error('Talaba topilmadi')
    return
  }
  
  isSaving.value = true
  
  try {
    await api.updateStudent(student.value.id, {
      phone: form.phone,
      address: form.address,
      commute: form.commute
    })
    
    // Update local state
    student.value = {
      ...student.value,
      phone: form.phone,
      address: form.address,
      commute: form.commute
    }
    
    toast.success('Ma\'lumotlar saqlandi')
    showToastMessage('Ma\'lumotlar saqlandi')
  } catch (e) {
    console.error('Error saving profile:', e)
    toast.error('Saqlashda xatolik yuz berdi')
    showToastMessage('Xatolik yuz berdi')
  } finally {
    isSaving.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.current || !passwordForm.new) {
    toast.error('Parollarni kiriting')
    showToastMessage('Parollarni kiriting')
    return
  }
  
  if (passwordForm.new.length < 6) {
    toast.error('Yangi parol kamida 6 ta belgidan iborat bo\'lishi kerak')
    return
  }
  
  isChangingPassword.value = true
  
  try {
    await api.changePassword(passwordForm.current, passwordForm.new)
    
    passwordForm.current = ''
    passwordForm.new = ''
    
    toast.success('Parol muvaffaqiyatli o\'zgartirildi')
    showToastMessage('Parol o\'zgartirildi')
  } catch (e) {
    console.error('Error changing password:', e)
    const errorMsg = e.response?.data?.detail || 'Parolni o\'zgartirishda xatolik'
    toast.error(errorMsg)
    showToastMessage(errorMsg)
  } finally {
    isChangingPassword.value = false
  }
}

const showToastMessage = (message) => {
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Initialize
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
