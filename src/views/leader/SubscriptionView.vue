<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
      <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('subscription.title') }}</h1>
          <p class="text-sm text-slate-500">{{ $t('subscription.groupSubscription') }}</p>
        </div>
        <div v-if="groupName" class="text-right">
          <p class="text-sm text-slate-500">{{ $t('subscription.group') }}</p>
          <p class="font-semibold text-slate-800">{{ groupName }}</p>
        </div>
      </div>

      <!-- Current Subscription Status -->
      <div :class="[
        'rounded-2xl p-6 text-white shadow-xl',
        isBlocked ? 'bg-gradient-to-br from-rose-500 to-red-600' :
        subscription?.is_trial ? 'bg-gradient-to-br from-amber-500 to-orange-600' :
        'bg-gradient-to-br from-emerald-500 to-teal-600'
      ]">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-3 mb-3">
              <div class="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center">
                <component :is="isBlocked ? Lock : subscription?.is_trial ? Clock : CrownIcon" class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-xl font-bold">
                  {{ isBlocked ? $t('subscription.title') : subscription?.is_trial ? $t('subscription.trial') : getPlanLabel(subscription?.plan_type) }}
                </h2>
                <p class="text-white/80 text-sm">
                  {{ isBlocked ? $t('subscription.expired') :
                     subscription?.is_trial ? $t('subscription.trial') :
                     $t('subscription.active') }}
                </p>
              </div>
            </div>
          </div>
          <div v-if="subscription && !isBlocked" class="text-right">
            <p class="text-3xl font-bold">{{ subscription.days_left }}</p>
            <p class="text-white/80 text-sm">{{ $t('subscription.daysLeft') }}</p>
          </div>
        </div>

        <div v-if="subscription" class="mt-4 grid grid-cols-2 gap-4">
          <div class="rounded-xl bg-white/10 p-3 backdrop-blur text-center">
            <p class="text-sm text-white/70">{{ $t('subscription.startDate') }}</p>
            <p class="font-semibold">{{ formatDate(subscription.start_date) }}</p>
          </div>
          <div class="rounded-xl bg-white/10 p-3 backdrop-blur text-center">
            <p class="text-sm text-white/70">{{ $t('subscription.endDate') }}</p>
            <p class="font-semibold">{{ formatDate(subscription.end_date) }}</p>
          </div>
        </div>

        <div v-if="subscription?.days_left <= 3 && subscription?.days_left > 0" class="mt-4 bg-white/10 rounded-xl p-3 flex items-center gap-2">
          <AlertTriangle class="w-5 h-5" />
          <span class="text-sm">{{ $t('subscription.subscriptionEndsIn', { days: subscription.days_left }) }}</span>
        </div>
      </div>

      <!-- Plans -->
      <div>
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Sparkles class="w-5 h-5 text-amber-500" />
          {{ $t('subscription.plans') }}
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="plan in plans"
            :key="plan.id"
            :class="[
              'relative rounded-2xl border-2 p-5 transition-all cursor-pointer hover:shadow-lg',
              selectedPlan?.id === plan.id
                ? 'border-emerald-500 bg-emerald-50 shadow-lg shadow-emerald-500/10'
                : 'border-slate-200 bg-white hover:border-emerald-300'
            ]"
            @click="selectedPlan = plan"
          >
            <div v-if="plan.plan_type === 'pro'" class="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-bold rounded-full">
              {{ $t('subscription.premium') }}
            </div>
            <div class="text-center mb-4">
              <div :class="[
                'w-14 h-14 mx-auto rounded-2xl flex items-center justify-center mb-3',
                plan.plan_type === 'start' ? 'bg-blue-100' :
                plan.plan_type === 'plus' ? 'bg-violet-100' :
                plan.plan_type === 'pro' ? 'bg-amber-100' :
                'bg-emerald-100'
              ]">
                <component :is="getPlanIcon(plan.plan_type)" :class="[
                  'w-7 h-7',
                  plan.plan_type === 'start' ? 'text-blue-600' :
                  plan.plan_type === 'plus' ? 'text-violet-600' :
                  plan.plan_type === 'pro' ? 'text-amber-600' :
                  'text-emerald-600'
                ]" />
              </div>
              <h3 class="text-lg font-bold text-slate-800">{{ plan.name }}</h3>
              <p class="text-2xl font-bold text-slate-900 mt-1">
                {{ plan.price.toLocaleString() }}
                <span class="text-sm font-normal text-slate-500">{{ $t('subscription.sumPerMonth') }}</span>
              </p>
            </div>
            <ul class="space-y-2">
              <li
                v-for="feature in (plan.features || [])"
                :key="feature"
                class="flex items-center gap-2 text-sm"
                :class="feature === 'Telegram Bot' ? 'text-blue-600 font-medium' : 'text-slate-600'"
              >
                <Bot v-if="feature === 'Telegram Bot'" class="w-4 h-4 text-blue-500 flex-shrink-0" />
                <CheckCircle v-else class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                {{ feature }}
              </li>
            </ul>
            <div v-if="selectedPlan?.id === plan.id" class="mt-4 text-center">
              <span class="inline-flex items-center gap-1 px-3 py-1 bg-emerald-500 text-white text-sm font-medium rounded-full">
                <Check class="w-4 h-4" /> {{ $t('common.active') }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Purchase Section -->
      <div v-if="selectedPlan" class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <CreditCard class="w-5 h-5 text-slate-400" />
          {{ $t('subscription.receipt') }}
        </h3>

        <!-- Card info -->
        <div v-if="cardInfo.card_number" class="mb-6 bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-5 text-white">
          <p class="text-slate-400 text-xs mb-2">{{ $t('subscription.cardNumber') }}</p>
          <p class="text-2xl font-mono tracking-wider mb-3">{{ cardInfo.card_number }}</p>
          <p class="text-slate-400 text-xs">{{ $t('subscription.cardOwner') }}</p>
          <p class="font-medium">{{ cardInfo.card_holder }}</p>
          <div class="mt-3 pt-3 border-t border-slate-700 flex justify-between items-center">
            <span class="text-sm text-slate-400">{{ $t('subscription.paymentAmount') }}</span>
            <span class="text-xl font-bold text-amber-400">{{ selectedPlan.price.toLocaleString() }} {{ $t('canteen.sum') }}</span>
          </div>
        </div>

        <!-- Upload receipt -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">
              {{ $t('subscription.selectReceipt') }}
            </label>
            <div
              class="border-2 border-dashed rounded-xl p-6 text-center transition-colors"
              :class="receiptFile ? 'border-emerald-300 bg-emerald-50' : 'border-slate-300 hover:border-emerald-400'"
            >
              <input
                ref="fileInput"
                type="file"
                accept="image/*,.pdf"
                class="hidden"
                @change="handleFileSelect"
              />
              <div v-if="receiptFile" class="flex items-center justify-center gap-3">
                <FileCheck class="w-8 h-8 text-emerald-500" />
                <div class="text-left">
                  <p class="font-medium text-emerald-700">{{ receiptFile.name }}</p>
                  <p class="text-sm text-emerald-500">{{ (receiptFile.size / 1024).toFixed(1) }} KB</p>
                </div>
                <button @click="receiptFile = null" class="ml-4 p-2 hover:bg-red-100 rounded-lg transition-colors">
                  <X class="w-5 h-5 text-red-500" />
                </button>
              </div>
              <div v-else @click="$refs.fileInput.click()" class="cursor-pointer">
                <Upload class="w-10 h-10 text-slate-400 mx-auto mb-2" />
                <p class="text-slate-600 font-medium">{{ $t('subscription.selectReceipt') }}</p>
                <p class="text-slate-400 text-sm mt-1">{{ $t('subscription.receiptFormats') }}</p>
              </div>
            </div>
          </div>

          <button
            @click="submitPayment"
            :disabled="!receiptFile || submitting"
            class="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Loader2 v-if="submitting" class="w-5 h-5 animate-spin" />
            <Send v-else class="w-5 h-5" />
            {{ submitting ? $t('common.loading') : $t('common.send') }}
          </button>
        </div>
      </div>

      <!-- Payment History -->
      <div v-if="myPayments.length > 0" class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Receipt class="w-5 h-5 text-slate-400" />
          {{ $t('subscription.paymentHistory') }}
        </h3>
        <div class="space-y-3">
          <div
            v-for="payment in myPayments"
            :key="payment.id"
            class="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100"
          >
            <div class="flex items-center gap-3">
              <div :class="[
                'w-10 h-10 rounded-xl flex items-center justify-center',
                payment.status === 'approved' ? 'bg-emerald-100' :
                payment.status === 'rejected' ? 'bg-rose-100' :
                'bg-amber-100'
              ]">
                <component :is="payment.status === 'approved' ? CheckCircle : payment.status === 'rejected' ? XCircle : Clock" :class="[
                  'w-5 h-5',
                  payment.status === 'approved' ? 'text-emerald-600' :
                  payment.status === 'rejected' ? 'text-rose-600' :
                  'text-amber-600'
                ]" />
              </div>
              <div>
                <p class="font-medium text-slate-800">{{ getPlanLabel(payment.plan_type) }}</p>
                <p class="text-sm text-slate-500">{{ formatDateTime(payment.created_at) }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-semibold text-slate-800">{{ payment.amount?.toLocaleString() }} {{ t('canteen.sum') }}</p>
              <p :class="[
                'text-xs font-medium',
                payment.status === 'approved' ? 'text-emerald-600' :
                payment.status === 'rejected' ? 'text-rose-600' :
                'text-amber-600'
              ]">
                {{ getStatusLabel(payment.status) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    AlertTriangle,
    Bot,
    Check,
    CheckCircle,
    Clock,
    CreditCard,
    Crown,
    FileCheck,
    Loader2, Lock,
    Receipt,
    Rocket,
    Send,
    Sparkles,
    Star,
    Upload,
    X,
    XCircle,
    Zap
} from 'lucide-vue-next'
import { markRaw, onMounted, ref } from 'vue'

const CrownIcon = markRaw(Crown)

const authStore = useAuthStore()
const toast = useToastStore()
const { t } = useLanguageStore()

const loading = ref(true)
const submitting = ref(false)
const subscription = ref(null)
const isBlocked = ref(false)
const groupId = ref(null)
const groupName = ref(null)
const plans = ref([])
const selectedPlan = ref(null)
const cardInfo = ref({})
const receiptFile = ref(null)
const myPayments = ref([])

const getPlanLabel = (type) => {
  const labels = { start: 'Start', plus: 'Plus', pro: 'Pro', unlimited: 'Unlimited', trial: 'Sinov' }
  return labels[type] || type
}

const getPlanIcon = (type) => {
  const icons = { start: markRaw(Zap), plus: markRaw(Star), pro: markRaw(Crown), unlimited: markRaw(Rocket) }
  return icons[type] || markRaw(Zap)
}

const getStatusLabel = (status) => {
  const labels = { pending: t('common.pending'), approved: t('common.approved'), rejected: t('common.rejected') }
  return labels[status] || status
}

const formatDate = (d) => {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

const formatDateTime = (d) => {
  if (!d) return '-'
  return new Date(d).toLocaleString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Fayl 10 MB dan katta bo\'lmasligi kerak')
      return
    }
    receiptFile.value = file
  }
}

const submitPayment = async () => {
  if (!selectedPlan.value || !receiptFile.value || !groupId.value) return
  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('group_id', groupId.value)
    formData.append('plan_type', selectedPlan.value.plan_type)
    formData.append('receipt', receiptFile.value)

    const result = await api.purchaseSubscription(formData)
    toast.success(result.message || 'To\'lov cheki yuborildi!')
    receiptFile.value = null
    selectedPlan.value = null
    await loadPayments()
  } catch (e) {
    toast.error(e.message || 'To\'lov yuborishda xatolik')
  } finally {
    submitting.value = false
  }
}

const loadPayments = async () => {
  try {
    if (groupId.value) {
      const resp = await api.getSubscriptionPayments({ group_id: groupId.value })
      myPayments.value = resp?.items || []
    }
  } catch (e) {
    console.error('Load payments error:', e)
  }
}

onMounted(async () => {
  try {
    const [subResp, plansResp, settingsResp] = await Promise.all([
      api.getMyGroupSubscription(),
      api.getSubscriptionPlans(),
      api.getSubscriptionSettings()
    ])

    subscription.value = subResp?.subscription
    isBlocked.value = subResp?.is_blocked || false
    groupId.value = subResp?.group_id
    groupName.value = subResp?.group_name
    plans.value = plansResp || []
    cardInfo.value = settingsResp || {}

    await loadPayments()
  } catch (e) {
    console.error('Subscription load error:', e)
  } finally {
    loading.value = false
  }
})
</script>
