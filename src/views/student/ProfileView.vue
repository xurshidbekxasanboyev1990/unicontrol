<template>
  <div class="space-y-6">
    <!-- Profile Header -->
    <div class="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-4 sm:p-6 text-white">
      <div class="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
        <div class="relative">
          <div class="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center text-3xl sm:text-4xl font-bold">
            {{ student?.name?.charAt(0) || 'U' }}
          </div>
          <button class="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-lg shadow-lg flex items-center justify-center text-emerald-600 hover:bg-emerald-50 transition-colors">
            <Camera class="w-4 h-4" />
          </button>
        </div>
        <div class="text-center sm:text-left">
          <h1 class="text-2xl font-bold">{{ student?.name }}</h1>
          <p class="text-emerald-100 mt-1">{{ student?.student_id || student?.login || '' }}</p>
          <div class="flex items-center justify-center sm:justify-start gap-2 mt-3">
            <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
              {{ student?.group_name || group?.name || 'Guruh' }}
            </span>
            <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-lg text-sm">
              {{ $t('roles.student') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Contract Status -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-slate-800">{{ $t('profile.sectionContract') || 'Kontrakt ma\'lumotlari' }}</h2>
        <span 
          class="px-3 py-1 rounded-lg text-sm font-medium"
          :class="contractPercent >= 100 ? 'bg-emerald-100 text-emerald-700' : contractPercent >= 50 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'"
        >
          {{ contractPercent >= 100 ? $t('profile.fullyPaid') : $t('profile.partiallyPaid') }}
        </span>
      </div>
      
      <!-- Main financial cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div class="text-center p-4 bg-slate-50 rounded-xl">
          <p class="text-xl font-bold text-slate-800">{{ formatContract(contractData?.contract_amount) }}</p>
          <p class="text-xs text-slate-500 mt-1">{{ $t('profile.contractLabel') || 'Kontrakt summasi' }}</p>
        </div>
        <div class="text-center p-4 bg-emerald-50 rounded-xl">
          <p class="text-xl font-bold text-emerald-600">{{ formatContract(contractData?.total_paid) }}</p>
          <p class="text-xs text-slate-500 mt-1">{{ $t('profile.paidAmount') || 'To\'langan' }}</p>
        </div>
        <div class="text-center p-4 bg-rose-50 rounded-xl">
          <p class="text-xl font-bold text-rose-600">{{ formatContract(Math.abs(contractData?.debt_amount || 0)) }}</p>
          <p class="text-xs text-slate-500 mt-1">{{ $t('profile.remainingAmount') || 'Qarz' }}</p>
        </div>
        <div class="text-center p-4 bg-purple-50 rounded-xl">
          <p class="text-xl font-bold text-purple-600">{{ contractData?.grant_amount > 0 ? formatContract(contractData.grant_amount) : '—' }}</p>
          <p class="text-xs text-slate-500 mt-1">Grant</p>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="relative mb-4">
        <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div 
            class="h-full rounded-full transition-all duration-500"
            :class="contractPercent >= 100 ? 'bg-gradient-to-r from-emerald-500 to-teal-500' : contractPercent >= 50 ? 'bg-gradient-to-r from-amber-500 to-orange-500' : 'bg-gradient-to-r from-red-500 to-rose-500'"
            :style="{ width: Math.min(contractPercent, 100) + '%' }"
          ></div>
        </div>
        <div class="flex justify-between mt-2 text-sm">
          <span class="text-slate-500">0%</span>
          <span class="font-semibold" :class="contractPercent >= 100 ? 'text-emerald-600' : contractPercent >= 50 ? 'text-amber-600' : 'text-red-600'">{{ contractPercent }}%</span>
          <span class="text-slate-500">100%</span>
        </div>
      </div>

      <!-- Extra details -->
      <div v-if="contractData" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="p-3 bg-slate-50 rounded-xl">
          <p class="text-xs text-slate-500">{{ $t('profile.course') || 'Kurs' }}</p>
          <p class="text-sm font-medium text-slate-800">{{ contractData.course || '—' }}</p>
        </div>
        <div class="p-3 bg-slate-50 rounded-xl">
          <p class="text-xs text-slate-500">{{ $t('profile.educationForm') || 'Ta\'lim shakli' }}</p>
          <p class="text-sm font-medium text-slate-800">{{ contractData.education_form || '—' }}</p>
        </div>
        <div class="p-3 bg-slate-50 rounded-xl">
          <p class="text-xs text-slate-500">{{ $t('profile.direction') || 'Yo\'nalish' }}</p>
          <p class="text-sm font-medium text-slate-800">{{ contractData.direction || '—' }}</p>
        </div>
        <div class="p-3 bg-slate-50 rounded-xl">
          <p class="text-xs text-slate-500">{{ $t('profile.status') || 'Holat' }}</p>
          <p class="text-sm font-medium" :class="contractData.student_status?.toLowerCase().includes('o\'qimoqda') ? 'text-emerald-700' : 'text-slate-800'">
            {{ contractData.student_status || '—' }}
          </p>
        </div>
      </div>
      
      <div v-if="!contractData && !loading" class="text-center py-4 text-slate-400 text-sm">
        Kontrakt ma'lumotlari hali yuklanmagan
      </div>
    </div>

    <!-- Info Cards -->
    <div class="grid md:grid-cols-2 gap-6">
      <!-- Personal Info (Read-only) -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center gap-2 mb-6">
          <UserCircle class="w-5 h-5 text-emerald-500" />
          <h2 class="text-lg font-semibold text-slate-800">{{ $t('profile.personalInfo') }}</h2>
          <Lock class="w-4 h-4 text-slate-400 ml-auto" />
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('profile.fullName') }}</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.name }}</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('students.studentIdLabel') }}</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.student_id || student?.login || '-' }}</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('profile.passport') }}</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.passport || 'AA 1234567' }}</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('profile.jshshir') }}</label>
            <p class="text-slate-800 font-medium mt-1">{{ student?.jshshir || '12345678901234' }}</p>
          </div>
        </div>

        <div class="mt-4 p-3 bg-amber-50 rounded-xl flex items-start gap-2">
          <AlertCircle class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <p class="text-sm text-amber-700">{{ $t('profile.adminOnlyNote') }}</p>
        </div>
      </div>

      <!-- Editable Info -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center gap-2 mb-6">
          <Settings class="w-5 h-5 text-emerald-500" />
          <h2 class="text-lg font-semibold text-slate-800">{{ $t('profile.editProfile') }}</h2>
        </div>
        
        <form @submit.prevent="saveProfile" class="space-y-4">
          <div>
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('students.phone') }}</label>
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
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('students.address') }}</label>
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
            <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('students.faculty') }}</label>
            <div class="relative mt-1">
              <GraduationCap class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.commute"
                type="text"
                readonly
                class="w-full pl-11 pr-4 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-slate-600 cursor-not-allowed"
                :placeholder="$t('students.faculty')"
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
            <span>{{ isSaving ? $t('profile.saving') : $t('profile.save') }}</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Change Password -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <div class="flex items-center gap-2 mb-6">
        <KeyRound class="w-5 h-5 text-emerald-500" />
        <h2 class="text-lg font-semibold text-slate-800">{{ $t('profile.changePassword') }}</h2>
      </div>

      <form @submit.prevent="changePassword" class="grid md:grid-cols-3 gap-4">
        <div>
          <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('profile.currentPassword') }}</label>
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
          <label class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ $t('profile.newPassword') }}</label>
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
            <span>{{ $t('profile.change') }}</span>
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
import { useLanguageStore } from '@/stores/language'
import {
    AlertCircle,
    Camera,
    CheckCircle,
    Eye,
    EyeOff,
    GraduationCap,
    KeyRound,
    Loader2,
    Lock,
    MapPin,
    Phone,
    Save,
    Settings,
    UserCircle
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'

const authStore = useAuthStore()
const toast = useToastStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const error = ref(null)
const student = ref(null)
const group = ref(null)
const contractData = ref(null)

// Load profile data
const loadProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Get current user profile from API - returns full student data for students
    const response = await api.getMe()
    student.value = {
      ...response,
      name: response.full_name || response.name,
      contractPaid: response.contract_paid || 0
    }
    
    // Initialize form with current data
    form.phone = response.phone || response.student_phone || ''
    form.address = response.address || ''
    form.commute = response.faculty || response.commute || ''
    
    // Load contract data from contracts table
    try {
      const contractResp = await api.getMyContract('2025-2026')
      if (contractResp?.contract) {
        contractData.value = contractResp.contract
      }
    } catch (e) {
      console.log('Contract data not available:', e.message)
    }
    
  } catch (e) {
    console.error('Error loading profile:', e)
    error.value = t('profile.loadError')
    
    // Fallback to auth store user data
    if (authStore.user) {
      student.value = {
        id: authStore.user.studentId || authStore.user.id,
        name: authStore.user.name || authStore.user.full_name,
        student_id: authStore.user.student_id || authStore.user.email,
        phone: authStore.user.phone || '',
        address: authStore.user.address || '',
        commute: authStore.user.commute || '',
        passport: authStore.user.passport || '-',
        jshshir: authStore.user.jshshir || '-',
        group_id: authStore.user.group_id || authStore.user.groupId,
        group_name: authStore.user.group || authStore.user.group_name,
        contract_amount: 0,
        contract_paid: 0
      }
      form.phone = student.value.phone
      form.address = student.value.address
      form.commute = student.value.commute
    }
  } finally {
    loading.value = false
  }
}

// Contract calculations - use contractData from contracts table, fallback to student model
const contractAmount = computed(() => {
  if (contractData.value) return Number(contractData.value.contract_amount) || 0
  return student.value?.contract_amount || 0
})
const debt = computed(() => {
  if (contractData.value) return Math.abs(Number(contractData.value.debt_amount) || 0)
  return Math.max(0, contractAmount.value - (student.value?.contract_paid || 0))
})
const contractPercent = computed(() => {
  if (contractData.value) {
    const pct = contractData.value.payment_percentage
    if (pct != null) return Math.round(pct * 100)
  }
  if (!contractAmount.value || contractAmount.value === 0) return 100
  const paid = contractData.value ? Number(contractData.value.total_paid) : (student.value?.contract_paid || 0)
  return Math.round(paid / contractAmount.value * 100)
})

const formatContract = (amount) => {
  if (amount == null || amount === 0) return '0'
  const num = Number(amount)
  if (num === 0) return '0'
  const absNum = Math.abs(num)
  if (absNum >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + ' mlrd'
  if (absNum >= 1_000_000) return (num / 1_000_000).toFixed(1) + ' mln'
  if (absNum >= 1_000) return Math.round(num / 1_000) + ' ming'
  return num.toLocaleString('uz-UZ')
}

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
    toast.error(t('profile.studentNotFound'))
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
    
    toast.success(t('profile.dataSaved'))
    showToastMessage(t('profile.dataSaved'))
  } catch (e) {
    console.error('Error saving profile:', e)
    toast.error(t('profile.saveError'))
    showToastMessage(t('profile.errorOccurred'))
  } finally {
    isSaving.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.current || !passwordForm.new) {
    toast.error(t('profile.enterPasswords'))
    showToastMessage(t('profile.enterPasswords'))
    return
  }
  
  if (passwordForm.new.length < 6) {
    toast.error(t('profile.passwordMinLength'))
    return
  }
  
  isChangingPassword.value = true
  
  try {
    await api.changePassword(passwordForm.current, passwordForm.new)
    
    passwordForm.current = ''
    passwordForm.new = ''
    
    toast.success(t('profile.passwordChanged'))
    showToastMessage(t('profile.passwordChangeShort'))
  } catch (e) {
    console.error('Error changing password:', e)
    const errorMsg = e.response?.data?.detail || t('profile.passwordChangeError')
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
