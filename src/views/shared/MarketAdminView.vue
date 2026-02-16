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
        <h1 class="text-xl sm:text-2xl font-bold">{{ $t('market.adminTitle') }}</h1>
        <p class="text-white/80 mt-2">{{ $t('market.adminSubtitle') }}</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('market.totalListings') }}</p>
            <p class="text-xl sm:text-2xl font-bold text-slate-800">{{ stats.total_listings || 0 }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <Package class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('market.pendingApproval') }}</p>
            <p class="text-xl sm:text-2xl font-bold text-amber-600">{{ stats.pending_listings || 0 }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <Clock class="w-5 h-5 sm:w-6 sm:h-6 text-amber-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5 cursor-pointer hover:shadow-md transition-all" @click="activeTab = 'order-payments'">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('market.orderPayments') }}</p>
            <p class="text-xl sm:text-2xl font-bold" :class="stats.pending_payments ? 'text-orange-600' : 'text-slate-400'">{{ stats.pending_payments || 0 }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center" :class="stats.pending_payments ? 'bg-orange-100' : 'bg-slate-100'">
            <CreditCard class="w-5 h-5 sm:w-6 sm:h-6" :class="stats.pending_payments ? 'text-orange-600' : 'text-slate-400'" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('market.activeOrders') }}</p>
            <p class="text-xl sm:text-2xl font-bold text-blue-600">{{ stats.active_orders || 0 }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <ClipboardList class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('market.openDisputes') }}</p>
            <p class="text-xl sm:text-2xl font-bold text-rose-600">{{ stats.open_disputes || 0 }}</p>
          </div>
          <div class="w-10 h-10 sm:w-12 sm:h-12 bg-rose-100 rounded-xl flex items-center justify-center">
            <AlertTriangle class="w-5 h-5 sm:w-6 sm:h-6 text-rose-600" />
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
        <span v-if="tab.badge" class="ml-1 px-2 py-0.5 text-xs font-bold rounded-full" :class="activeTab === tab.value ? 'bg-white/20 text-white' : 'bg-rose-100 text-rose-700'">
          {{ tab.badge }}
        </span>
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

    <!-- Order Payments -->
    <div v-if="activeTab === 'order-payments'" class="space-y-4">
      <!-- Filter -->
      <div class="flex flex-wrap gap-2">
        <button v-for="f in paymentFilters" :key="f.value"
          @click="orderPaymentFilter = f.value"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
            orderPaymentFilter === f.value
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/25'
              : 'bg-white border border-slate-200 text-slate-600 hover:border-emerald-300'
          ]">
          {{ f.label }}
        </button>
      </div>

      <div v-if="orderPaymentsLoading" class="text-center py-12">
        <div class="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      </div>
      <div v-else-if="filteredOrderPayments.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <CreditCard class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noOrderPayments') }}</p>
      </div>

      <div v-else class="space-y-3">
        <div v-for="op in filteredOrderPayments" :key="op.id"
          class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
          <div class="flex flex-col lg:flex-row lg:items-start gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2 flex-wrap">
                <span class="bg-blue-100 text-blue-700 px-2.5 py-0.5 text-xs rounded-full font-medium">
                  {{ $t('market.order') }} #{{ op.id }}
                </span>
                <span :class="op.payment_status === 'pending' ? 'bg-amber-100 text-amber-700' : op.payment_status === 'verified' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
                  class="px-2.5 py-0.5 text-xs rounded-full font-medium">
                  {{ op.payment_status === 'pending' ? $t('market.paymentPending') : op.payment_status === 'verified' ? $t('market.paymentVerified') : $t('market.paymentRejected') }}
                </span>
                <span :class="getStatusBadge(op.status)" class="px-2.5 py-0.5 text-xs rounded-full font-medium">
                  {{ op.status }}
                </span>
              </div>
              <h3 class="font-semibold text-slate-800 text-lg mb-1">{{ op.title }}</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm mt-2">
                <div><span class="text-slate-400">{{ $t('market.buyer') }}:</span> <span class="font-medium text-slate-700">{{ op.buyer_name }}</span></div>
                <div><span class="text-slate-400">{{ $t('market.seller') }}:</span> <span class="font-medium text-slate-700">{{ op.seller_name }}</span></div>
                <div><span class="text-slate-400">{{ $t('market.amount') }}:</span> <span class="font-bold text-emerald-600">{{ formatPrice(op.amount) }}</span></div>
                <div><span class="text-slate-400">{{ $t('market.commission') }}:</span> <span class="font-medium text-slate-600">{{ formatPrice(op.commission_amount) }}</span></div>
                <div><span class="text-slate-400">{{ $t('market.date') }}:</span> <span class="text-slate-600">{{ formatDate(op.created_at) }}</span></div>
                <div v-if="op.payment_receipt_filename"><span class="text-slate-400">{{ $t('market.receiptFile') }}:</span> <span class="text-slate-600">{{ op.payment_receipt_filename }}</span></div>
              </div>
              <p v-if="op.payment_reject_reason" class="mt-2 text-sm text-rose-600 bg-rose-50 rounded-lg px-3 py-2">
                ❌ {{ op.payment_reject_reason }}
              </p>
            </div>
            <div class="flex flex-col gap-2 min-w-[140px]">
              <button @click="viewOrderReceipt(op)"
                class="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:from-blue-600 hover:to-blue-700 shadow-sm transition-all flex items-center justify-center gap-1.5">
                <Eye class="w-4 h-4" /> {{ $t('market.viewReceipt') }}
              </button>
              <button v-if="op.payment_status === 'pending'" @click="verifyOrderPayment(op)"
                class="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-emerald-700 shadow-sm transition-all flex items-center justify-center gap-1.5">
                <CheckCircle class="w-4 h-4" /> {{ $t('market.verifyPayment') }}
              </button>
              <button v-if="op.payment_status === 'pending'" @click="rejectOrderPayment(op)"
                class="w-full border border-rose-200 text-rose-600 px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-rose-50 transition-colors flex items-center justify-center gap-1.5">
                <XCircle class="w-4 h-4" /> {{ $t('market.rejectPayment') }}
              </button>
            </div>
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

    <!-- Receipt Viewer Modal -->
    <div v-if="showReceiptModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showReceiptModal = false">
      <div class="relative bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <button @click="showReceiptModal = false" class="absolute top-4 right-4 p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors z-10"><X class="w-5 h-5" /></button>
        <h2 class="text-xl font-bold text-slate-800 mb-4">{{ $t('market.paymentReceipt') }}</h2>
        <div v-if="receiptPayment" class="mb-4 bg-slate-50 rounded-xl p-4 text-sm space-y-1">
          <p><span class="text-slate-400">{{ $t('market.order') }}:</span> <span class="font-medium">#{{ receiptPayment.id }} — {{ receiptPayment.title }}</span></p>
          <p><span class="text-slate-400">{{ $t('market.buyer') }}:</span> <span class="font-medium">{{ receiptPayment.buyer_name }}</span></p>
          <p><span class="text-slate-400">{{ $t('market.amount') }}:</span> <span class="font-bold text-emerald-600">{{ formatPrice(receiptPayment.amount) }}</span></p>
        </div>
        <div v-if="receiptLoading" class="flex items-center justify-center py-12">
          <div class="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <div v-else-if="receiptUrl">
          <iframe v-if="receiptIsPdf" :src="receiptUrl" class="w-full h-[60vh] rounded-xl border border-slate-200"></iframe>
          <img v-else :src="receiptUrl" class="w-full rounded-xl border border-slate-200 max-h-[60vh] object-contain bg-slate-100" />
        </div>
        <div v-else class="text-center py-8 text-slate-400">{{ $t('market.noReceipt') }}</div>
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
    Eye,
    Package,
    Store,
    X,
    XCircle
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const { t } = useLanguageStore()
const toast = useToastStore()

const activeTab = ref('pending')
const stats = ref({})
const pendingListings = ref([])
const allListings = ref([])
const disputes = ref([])
const payouts = ref([])
const showRejectModal = ref(false)
const rejectingId = ref(null)
const rejectReason = ref('')

// Order Payments
const orderPayments = ref([])
const orderPaymentsLoading = ref(false)
const orderPaymentFilter = ref(null)
const pendingPaymentsCount = computed(() => orderPayments.value.filter(p => p.payment_status === 'pending').length)
const filteredOrderPayments = computed(() => {
  if (!orderPaymentFilter.value) return orderPayments.value
  return orderPayments.value.filter(p => p.payment_status === orderPaymentFilter.value)
})
const paymentFilters = computed(() => [
  { value: null, label: t('common.all') },
  { value: 'pending', label: '⏳ ' + t('market.paymentPending') },
  { value: 'verified', label: '✅ ' + t('market.paymentVerified') },
  { value: 'rejected', label: '❌ ' + t('market.paymentRejected') },
])

// Receipt viewer
const showReceiptModal = ref(false)
const receiptUrl = ref(null)
const receiptIsPdf = ref(false)
const receiptLoading = ref(false)
const receiptPayment = ref(null)

const adminTabs = computed(() => [
  { value: 'pending', label: `📋 ${t('market.pendingApproval')}` },
  { value: 'order-payments', label: `💰 ${t('market.orderPayments')}`, badge: pendingPaymentsCount.value || null },
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

// Order Payments
const loadOrderPayments = async () => {
  orderPaymentsLoading.value = true
  try {
    const res = await api.request('/market/order-payments')
    orderPayments.value = res.items || []
  } catch (e) {
    console.error('Order payments load error:', e)
  } finally {
    orderPaymentsLoading.value = false
  }
}

const viewOrderReceipt = async (payment) => {
  receiptPayment.value = payment
  receiptUrl.value = null
  receiptIsPdf.value = false
  receiptLoading.value = true
  showReceiptModal.value = true
  try {
    const token = localStorage.getItem('access_token') || ''
    const resp = await fetch(`/api/v1/market/orders/${payment.id}/receipt`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!resp.ok) throw new Error('Yuklab bo\'lmadi')
    const contentType = resp.headers.get('content-type') || ''
    receiptIsPdf.value = contentType.includes('pdf')
    const blob = await resp.blob()
    receiptUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    console.error(e)
    toast.error(t('market.receiptLoadError'))
    showReceiptModal.value = false
  } finally {
    receiptLoading.value = false
  }
}

const verifyOrderPayment = async (payment) => {
  if (!confirm(t('market.confirmVerifyPayment'))) return
  try {
    await api.request(`/market/order-payments/${payment.id}?action=verify`, { method: 'PATCH' })
    payment.payment_status = 'verified'
    payment.payment_verified = true
    payment.payment_rejected = false
    toast.success(`${payment.buyer_name} — ${payment.title} to'lovi tasdiqlandi!`)
    loadStats()
  } catch (e) {
    toast.error(e.message || t('common.error'))
  }
}

const rejectOrderPayment = async (payment) => {
  const reason = prompt(t('market.enterRejectReason'))
  if (reason === null) return
  try {
    await api.request(`/market/order-payments/${payment.id}?action=reject&reject_reason=${encodeURIComponent(reason || '')}`, { method: 'PATCH' })
    payment.payment_status = 'rejected'
    payment.payment_rejected = true
    payment.payment_verified = false
    payment.payment_reject_reason = reason
    toast.success(t('market.paymentRejectedSuccess'))
    loadStats()
  } catch (e) {
    toast.error(e.message || t('common.error'))
  }
}

watch(activeTab, (val) => {
  if (val === 'pending') loadPending()
  if (val === 'order-payments') loadOrderPayments()
  if (val === 'listings') loadAllListings()
  if (val === 'disputes') loadDisputes()
  if (val === 'payouts') loadPayouts()
})

onMounted(() => {
  loadStats()
  loadPending()
  loadOrderPayments()
})
</script>
