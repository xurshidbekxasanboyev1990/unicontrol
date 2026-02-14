<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 rounded-3xl p-6 md:p-8 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
      <div class="relative">
        <div class="flex items-center gap-3 mb-2">
          <Store class="w-8 h-8" />
          <span class="text-sm font-medium opacity-90">UniMarket Admin</span>
        </div>
        <h1 class="text-2xl md:text-3xl font-bold">{{ $t('market.adminTitle') }}</h1>
        <p class="text-white/80 mt-2">{{ $t('market.adminSubtitle') }}</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('market.totalListings') }}</p>
            <p class="text-2xl font-bold text-slate-800">{{ stats.total_listings || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <Package class="w-6 h-6 text-emerald-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('market.pendingApproval') }}</p>
            <p class="text-2xl font-bold text-amber-600">{{ stats.pending_listings || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <Clock class="w-6 h-6 text-amber-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('market.activeOrders') }}</p>
            <p class="text-2xl font-bold text-blue-600">{{ stats.active_orders || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <ClipboardList class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('market.openDisputes') }}</p>
            <p class="text-2xl font-bold text-rose-600">{{ stats.open_disputes || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <AlertTriangle class="w-6 h-6 text-rose-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex flex-wrap gap-2">
      <button v-for="tab in adminTabs" :key="tab.value"
        @click="activeTab = tab.value"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all',
          activeTab === tab.value
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/25'
            : 'bg-white border border-slate-200 text-slate-600 hover:border-emerald-300'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Pending Listings -->
    <div v-if="activeTab === 'pending'" class="space-y-4">
      <div v-if="pendingListings.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Package class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noPending') }}</p>
      </div>

      <div v-for="listing in pendingListings" :key="listing.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
        <div class="flex flex-col sm:flex-row sm:items-start gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span :class="getCategoryColor(listing.category)" class="px-2.5 py-0.5 text-xs rounded-full font-medium">
                {{ listing.category }}
              </span>
              <span class="text-xs text-slate-400">{{ listing.seller_name }}</span>
            </div>
            <h3 class="font-semibold text-slate-800 text-lg mb-1">{{ listing.title }}</h3>
            <p class="text-sm text-slate-500 mb-2">{{ listing.description }}</p>
            <div class="flex items-center gap-4 text-sm text-slate-500">
              <span class="font-bold text-emerald-600">{{ formatPrice(listing.price) }}</span>
              <span>{{ listing.delivery_days }} {{ $t('market.days') }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="approveListing(listing.id)"
              class="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-emerald-700 shadow-sm transition-all flex items-center gap-1">
              <CheckCircle class="w-4 h-4" /> {{ $t('market.approve') }}
            </button>
            <button @click="rejectingId = listing.id; rejectReason = ''; showRejectModal = true"
              class="bg-gradient-to-r from-rose-500 to-rose-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-rose-600 hover:to-rose-700 shadow-sm transition-all flex items-center gap-1">
              <XCircle class="w-4 h-4" /> {{ $t('market.reject') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- All Listings -->
    <div v-if="activeTab === 'listings'" class="space-y-4">
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden overflow-x-auto">
        <table class="w-full text-sm min-w-[600px]">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="text-left p-4 text-slate-600 font-semibold">{{ $t('market.listingTitle') }}</th>
              <th class="text-left p-4 text-slate-600 font-semibold">{{ $t('market.seller') }}</th>
              <th class="text-left p-4 text-slate-600 font-semibold">{{ $t('market.price') }}</th>
              <th class="text-left p-4 text-slate-600 font-semibold">{{ $t('market.status') }}</th>
              <th class="text-left p-4 text-slate-600 font-semibold">{{ $t('market.orders') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="listing in allListings" :key="listing.id" class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td class="p-4 font-medium text-slate-800">{{ listing.title }}</td>
              <td class="p-4 text-slate-600">{{ listing.seller_name }}</td>
              <td class="p-4 text-emerald-600 font-semibold">{{ formatPrice(listing.price) }}</td>
              <td class="p-4">
                <span :class="getStatusBadge(listing.status)" class="px-2.5 py-0.5 text-xs rounded-full font-medium">{{ listing.status }}</span>
              </td>
              <td class="p-4 text-slate-600">{{ listing.orders_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Disputes -->
    <div v-if="activeTab === 'disputes'" class="space-y-4">
      <div v-if="disputes.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <AlertTriangle class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noDisputes') }}</p>
      </div>

      <div v-for="dispute in disputes" :key="dispute.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
        <div class="flex flex-col sm:flex-row sm:items-start gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="bg-rose-100 text-rose-700 px-2.5 py-0.5 text-xs rounded-full font-medium">Dispute #{{ dispute.id }}</span>
              <span class="text-xs text-slate-400">Order #{{ dispute.order_id }}</span>
            </div>
            <h3 class="font-semibold text-slate-800">{{ dispute.order_title }}</h3>
            <p class="text-sm text-slate-500 mt-1">{{ dispute.reason }}</p>
            <p class="text-xs text-slate-400 mt-2">{{ dispute.buyer_name }} vs {{ dispute.seller_name }}</p>
          </div>
          <div class="flex gap-2">
            <button @click="resolveDispute(dispute.id, 'buyer')"
              class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-blue-600 hover:to-blue-700 shadow-sm transition-all">
              {{ $t('market.favorBuyer') }}
            </button>
            <button @click="resolveDispute(dispute.id, 'seller')"
              class="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-emerald-700 shadow-sm transition-all">
              {{ $t('market.favorSeller') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Payouts -->
    <div v-if="activeTab === 'payouts'" class="space-y-4">
      <div v-if="payouts.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <CreditCard class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noPayouts') }}</p>
      </div>

      <div v-for="payout in payouts" :key="payout.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 flex flex-col sm:flex-row sm:items-center gap-4 hover:shadow-md transition-all">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span :class="payout.status === 'pending' ? 'bg-amber-100 text-amber-700' : payout.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
              class="px-2.5 py-0.5 text-xs rounded-full font-medium">{{ payout.status }}</span>
          </div>
          <p class="font-semibold text-slate-800">{{ payout.user_name }}</p>
          <p class="text-sm text-slate-500">{{ payout.card_number || 'No card' }} · {{ formatDate(payout.created_at) }}</p>
        </div>
        <div class="text-right">
          <p class="text-lg font-bold text-emerald-600">{{ formatPrice(payout.amount) }}</p>
          <div v-if="payout.status !== 'completed' && payout.status !== 'rejected'" class="flex gap-2 mt-2">
            <button v-if="payout.status !== 'completed'" @click="processPayout(payout.id, 'completed')"
              class="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:from-emerald-600 hover:to-emerald-700 shadow-sm transition-all">
              ✅ {{ $t('market.approvePayout') }}
            </button>
            <button v-if="payout.status !== 'rejected'" @click="processPayout(payout.id, 'rejected')"
              class="border border-rose-200 text-rose-600 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-rose-50 transition-colors">
              ❌ {{ $t('market.rejectPayout') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showRejectModal = false">
      <div class="relative bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-slate-800">{{ $t('market.rejectReason') }}</h2>
          <button @click="showRejectModal = false" class="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"><X class="w-5 h-5" /></button>
        </div>
        <textarea v-model="rejectReason" rows="3"
          class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mb-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          :placeholder="$t('market.rejectReasonPlaceholder')"></textarea>
        <div class="flex gap-3">
          <button @click="showRejectModal = false"
            class="flex-1 border border-slate-200 rounded-xl py-2.5 text-slate-600 font-medium hover:bg-slate-50 transition-colors">{{ $t('common.cancel') }}</button>
          <button @click="rejectListing"
            class="flex-1 bg-gradient-to-r from-rose-500 to-rose-600 text-white rounded-xl py-2.5 font-semibold hover:from-rose-600 hover:to-rose-700 shadow-lg shadow-rose-500/25 transition-all">{{ $t('market.reject') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
    AlertTriangle, CheckCircle,
    ClipboardList,
    Clock,
    CreditCard,
    Package,
    Store,
    X,
    XCircle
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const activeTab = ref('pending')
const stats = ref({})
const pendingListings = ref([])
const allListings = ref([])
const disputes = ref([])
const payouts = ref([])
const showRejectModal = ref(false)
const rejectingId = ref(null)
const rejectReason = ref('')

const adminTabs = computed(() => [
  { value: 'pending', label: `📋 ${t('market.pendingApproval')}` },
  { value: 'listings', label: `📦 ${t('market.allListings')}` },
  { value: 'disputes', label: `⚠️ ${t('market.disputes')}` },
  { value: 'payouts', label: `💳 ${t('market.payouts')}` },
])

const formatPrice = (price) => {
  if (!price && price !== 0) return '0 UZS'
  return new Intl.NumberFormat('uz-UZ').format(price) + ' UZS'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const getCategoryColor = (cat) => {
  const colors = {
    programming: 'bg-blue-100 text-blue-700',
    design: 'bg-pink-100 text-pink-700',
    writing: 'bg-emerald-100 text-emerald-700',
    translation: 'bg-violet-100 text-violet-700',
    math: 'bg-amber-100 text-amber-700',
    science: 'bg-teal-100 text-teal-700',
    other: 'bg-slate-100 text-slate-700',
  }
  return colors[cat] || 'bg-slate-100 text-slate-700'
}

const getStatusBadge = (status) => ({
  active: 'bg-emerald-100 text-emerald-700',
  pending: 'bg-amber-100 text-amber-700',
  rejected: 'bg-rose-100 text-rose-700',
  paused: 'bg-slate-100 text-slate-700',
}[status] || 'bg-slate-100 text-slate-700')

const buildQuery = (params) => {
  const cleaned = {}
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') cleaned[k] = v
  }
  if (Object.keys(cleaned).length === 0) return ''
  return '?' + new URLSearchParams(cleaned).toString()
}

const loadStats = async () => {
  try {
    stats.value = await api.request('/market/stats')
  } catch (e) { console.error(e) }
}

const loadPending = async () => {
  try {
    const res = await api.request('/market/listings' + buildQuery({ status: 'pending', page: 1, page_size: 100 }))
    pendingListings.value = res.items || []
  } catch (e) { console.error(e) }
}

const loadAllListings = async () => {
  try {
    const res = await api.request('/market/listings' + buildQuery({ status: '', page: 1, page_size: 100 }))
    allListings.value = res.items || []
  } catch (e) { console.error(e) }
}

const loadDisputes = async () => {
  try {
    const res = await api.request('/market/disputes')
    disputes.value = res.items || res || []
  } catch (e) { console.error(e) }
}

const loadPayouts = async () => {
  try {
    const res = await api.request('/market/payouts')
    payouts.value = res.items || res || []
  } catch (e) { console.error(e) }
}

const approveListing = async (id) => {
  try {
    await api.request(`/market/listings/${id}/moderate`, { method: 'POST', body: { action: 'approve' } })
    loadPending()
    loadStats()
  } catch (e) { alert(e.data?.detail || 'Error') }
}

const rejectListing = async () => {
  try {
    await api.request(`/market/listings/${rejectingId.value}/moderate`, {
      method: 'POST',
      body: { action: 'reject', reason: rejectReason.value }
    })
    showRejectModal.value = false
    loadPending()
    loadStats()
  } catch (e) { alert(e.data?.detail || 'Error') }
}

const resolveDispute = async (id, winner) => {
  if (!confirm(`Resolve in favor of ${winner}?`)) return
  try {
    await api.request(`/market/disputes/${id}/resolve`, {
      method: 'POST',
      body: { resolution: winner, note: `Resolved in favor of ${winner}` }
    })
    loadDisputes()
    loadStats()
  } catch (e) { alert(e.data?.detail || 'Error') }
}

const processPayout = async (id, status) => {
  try {
    const action = status === 'completed' ? 'complete' : 'fail'
    await api.request(`/market/payouts/${id}/process?action=${action}`, { method: 'POST' })
    loadPayouts()
  } catch (e) { alert(e.data?.detail || 'Error') }
}

watch(activeTab, (val) => {
  if (val === 'pending') loadPending()
  if (val === 'listings') loadAllListings()
  if (val === 'disputes') loadDisputes()
  if (val === 'payouts') loadPayouts()
})

onMounted(() => {
  loadStats()
  loadPending()
})
</script>
