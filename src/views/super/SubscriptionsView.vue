<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">{{ $t('subscription.manageSubscriptions') }}</h1>
        <p class="text-slate-500">Guruh obunalari va to'lovlarni boshqarish</p>
      </div>
      <button
        v-if="!trialActivated"
        @click="activateTrial"
        :disabled="trialLoading"
        class="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-semibold hover:from-amber-600 hover:to-orange-600 shadow-lg shadow-amber-500/25 transition-all disabled:opacity-50"
      >
        <Loader2 v-if="trialLoading" class="w-5 h-5 animate-spin" />
        <Rocket v-else class="w-5 h-5" />
        {{ trialLoading ? $t('common.loading') : 'START' }}
      </button>
      <div v-else class="flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-700 rounded-xl">
        <CheckCircle class="w-5 h-5" />
        <span class="font-medium">Sinov muddati: {{ trialEndDate }} gacha</span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 bg-white rounded-xl p-1.5 border border-slate-200 shadow-sm">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all',
          activeTab === tab.id
            ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
            : 'text-slate-600 hover:bg-slate-100'
        ]"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
        <span v-if="tab.badge" class="ml-1 px-2 py-0.5 text-xs font-bold rounded-full" :class="activeTab === tab.id ? 'bg-white/20 text-white' : 'bg-amber-100 text-amber-700'">
          {{ tab.badge }}
        </span>
      </button>
    </div>

    <!-- Tab: Payments -->
    <div v-if="activeTab === 'payments'" class="space-y-4">
      <!-- Filter -->
      <div class="flex gap-3">
        <button
          v-for="f in paymentFilters"
          :key="f.value"
          @click="paymentStatusFilter = f.value"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
            paymentStatusFilter === f.value
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Payments List -->
      <div v-if="paymentsLoading" class="text-center py-12">
        <Loader2 class="w-8 h-8 text-emerald-500 animate-spin mx-auto" />
      </div>
      <div v-else-if="filteredPayments.length === 0" class="text-center py-12 bg-white rounded-2xl border border-slate-200">
        <CreditCard class="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-500">To'lovlar topilmadi</p>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="payment in filteredPayments"
          :key="payment.id"
          class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div :class="[
                'w-12 h-12 rounded-xl flex items-center justify-center',
                payment.status === 'approved' ? 'bg-emerald-100' :
                payment.status === 'rejected' ? 'bg-rose-100' :
                'bg-amber-100'
              ]">
                <component :is="payment.status === 'approved' ? CheckCircle : payment.status === 'rejected' ? XCircle : Clock" :class="[
                  'w-6 h-6',
                  payment.status === 'approved' ? 'text-emerald-600' :
                  payment.status === 'rejected' ? 'text-rose-600' :
                  'text-amber-600'
                ]" />
              </div>
              <div>
                <h3 class="font-semibold text-slate-800">{{ payment.group_name }}</h3>
                <p class="text-sm text-slate-500">{{ getPlanLabel(payment.plan_type) }} · {{ payment.amount?.toLocaleString() }} so'm</p>
                <p class="text-xs text-slate-400 mt-1">{{ payment.paid_by_name || 'Noma\'lum' }} · {{ formatDateTime(payment.created_at) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="payment.receipt_file"
                @click="viewReceipt(payment)"
                class="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                title="Chekni ko'rish"
              >
                <Eye class="w-5 h-5" />
              </button>
              <template v-if="payment.status === 'pending'">
                <button
                  @click="approvePayment(payment)"
                  class="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors flex items-center gap-1.5 text-sm font-medium"
                >
                  <Check class="w-4 h-4" /> Tasdiqlash
                </button>
                <button
                  @click="openRejectModal(payment)"
                  class="px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors flex items-center gap-1.5 text-sm font-medium"
                >
                  <X class="w-4 h-4" /> Rad etish
                </button>
              </template>
              <span v-else :class="[
                'px-3 py-1 rounded-full text-xs font-bold',
                payment.status === 'approved' ? 'bg-emerald-100 text-emerald-700' :
                'bg-rose-100 text-rose-700'
              ]">
                {{ getStatusLabel(payment.status) }}
              </span>
            </div>
          </div>
          <div v-if="payment.admin_note" class="mt-3 p-3 bg-slate-50 rounded-lg text-sm text-slate-600">
            <span class="font-medium">Izoh:</span> {{ payment.admin_note }}
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Market Payments -->
    <div v-if="activeTab === 'market-payments'" class="space-y-4">
      <!-- Filter -->
      <div class="flex gap-3">
        <button
          v-for="f in paymentFilters"
          :key="'m'+f.value"
          @click="marketPaymentFilter = f.value"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
            marketPaymentFilter === f.value
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Market Payments List -->
      <div v-if="marketPaymentsLoading" class="text-center py-12">
        <Loader2 class="w-8 h-8 text-emerald-500 animate-spin mx-auto" />
      </div>
      <div v-else-if="filteredMarketPayments.length === 0" class="text-center py-12 bg-white rounded-2xl border border-slate-200">
        <CreditCard class="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-500">Market tarif to'lovlari topilmadi</p>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="payment in filteredMarketPayments"
          :key="'mp'+payment.id"
          class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div :class="[
                'w-12 h-12 rounded-xl flex items-center justify-center',
                payment.status === 'approved' ? 'bg-emerald-100' :
                payment.status === 'rejected' ? 'bg-rose-100' :
                'bg-amber-100'
              ]">
                <component :is="payment.status === 'approved' ? CheckCircle : payment.status === 'rejected' ? XCircle : Clock" :class="[
                  'w-6 h-6',
                  payment.status === 'approved' ? 'text-emerald-600' :
                  payment.status === 'rejected' ? 'text-rose-600' :
                  'text-amber-600'
                ]" />
              </div>
              <div>
                <h3 class="font-semibold text-slate-800">{{ payment.user_name }}</h3>
                <p class="text-sm text-slate-500">
                  <span :class="payment.tariff === 'premium' ? 'text-amber-600 font-medium' : 'text-emerald-600 font-medium'">
                    {{ payment.tariff === 'student_pro' ? 'Student Pro' : 'Premium' }}
                  </span>
                  · {{ Number(payment.amount).toLocaleString() }} so'm
                </p>
                <p class="text-xs text-slate-400 mt-1">{{ formatDateTime(payment.created_at) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="payment.receipt_file"
                @click="viewMarketReceipt(payment)"
                class="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                title="Chekni ko'rish"
              >
                <Eye class="w-5 h-5" />
              </button>
              <template v-if="payment.status === 'pending'">
                <button
                  @click="approveMarketPayment(payment)"
                  class="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors flex items-center gap-1.5 text-sm font-medium"
                >
                  <Check class="w-4 h-4" /> Tasdiqlash
                </button>
                <button
                  @click="rejectMarketPayment(payment)"
                  class="px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors flex items-center gap-1.5 text-sm font-medium"
                >
                  <X class="w-4 h-4" /> Rad etish
                </button>
              </template>
              <span v-else :class="[
                'px-3 py-1 rounded-full text-xs font-bold',
                payment.status === 'approved' ? 'bg-emerald-100 text-emerald-700' :
                'bg-rose-100 text-rose-700'
              ]">
                {{ getStatusLabel(payment.status) }}
              </span>
            </div>
          </div>
          <div v-if="payment.admin_note" class="mt-3 p-3 bg-slate-50 rounded-lg text-sm text-slate-600">
            <span class="font-medium">Izoh:</span> {{ payment.admin_note }}
          </div>
        </div>
      </div>
    </div>

    <!-- Market Receipt Preview Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showMarketReceiptModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showMarketReceiptModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div class="flex items-center justify-between p-4 border-b border-slate-200">
              <h3 class="text-lg font-semibold text-slate-800">Market to'lov cheki — {{ marketReceiptPayment?.user_name }}</h3>
              <button @click="showMarketReceiptModal = false" class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
                <X class="w-5 h-5 text-slate-500" />
              </button>
            </div>
            <div class="flex-1 overflow-auto p-4 flex items-center justify-center bg-slate-50 min-h-[300px]">
              <Loader2 v-if="marketReceiptLoading" class="w-8 h-8 text-emerald-500 animate-spin" />
              <img v-else-if="marketReceiptUrl && !marketReceiptIsPdf" :src="marketReceiptUrl" class="max-w-full max-h-[70vh] rounded-lg shadow-lg object-contain" alt="Chek" />
              <iframe v-else-if="marketReceiptUrl && marketReceiptIsPdf" :src="marketReceiptUrl" class="w-full h-[70vh] rounded-lg border-0"></iframe>
              <p v-else class="text-slate-400">Chek yuklanmadi</p>
            </div>
            <div class="p-4 border-t border-slate-200 flex justify-end">
              <button @click="showMarketReceiptModal = false" class="px-5 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium">
                Yopish
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Tab: Settings -->
    <div v-if="activeTab === 'settings'" class="bg-white rounded-2xl border border-slate-200 p-6 space-y-6">
      <h3 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
        <Settings class="w-5 h-5 text-slate-400" />
        Obuna sozlamalari
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Karta raqami</label>
          <input
            v-model="settingsForm.card_number"
            type="text"
            placeholder="8600 0000 0000 0000"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Karta egasi</label>
          <input
            v-model="settingsForm.card_holder"
            type="text"
            placeholder="ISM FAMILIYA"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Sinov muddati tugash sanasi</label>
          <input
            v-model="settingsForm.trial_end_date"
            type="date"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
          />
        </div>
        <div class="flex items-center gap-3 pt-8">
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settingsForm.is_subscription_enabled" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-200 peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
          </label>
          <span class="text-sm font-medium text-slate-700">Obuna tizimini yoqish</span>
        </div>
      </div>

      <button
        @click="saveSettings"
        :disabled="settingsSaving"
        class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold hover:from-emerald-600 hover:to-teal-600 transition-all disabled:opacity-50"
      >
        <Loader2 v-if="settingsSaving" class="w-5 h-5 animate-spin" />
        <Save v-else class="w-5 h-5" />
        {{ settingsSaving ? $t('settings.saving') : $t('common.save') }}
      </button>
    </div>

    <!-- Tab: Subscriptions -->
    <div v-if="activeTab === 'subscriptions'" class="space-y-4">
      <!-- Status Filter -->
      <div class="flex gap-3 flex-wrap">
        <button
          v-for="f in subFilters"
          :key="f.value"
          @click="subStatusFilter = f.value"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
            subStatusFilter === f.value
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <div v-if="subsLoading" class="text-center py-12">
        <Loader2 class="w-8 h-8 text-emerald-500 animate-spin mx-auto" />
      </div>
      <div v-else-if="filteredSubscriptions.length === 0" class="text-center py-12 bg-white rounded-2xl border border-slate-200">
        <Crown class="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-500">Hozircha obunalar yo'q</p>
      </div>
      <div v-else class="overflow-x-auto bg-white rounded-2xl border border-slate-200">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50">
              <th class="text-left p-4 text-sm font-medium text-slate-600">Guruh</th>
              <th class="text-left p-4 text-sm font-medium text-slate-600">Reja</th>
              <th class="text-left p-4 text-sm font-medium text-slate-600">Status</th>
              <th class="text-left p-4 text-sm font-medium text-slate-600">Muddat</th>
              <th class="text-left p-4 text-sm font-medium text-slate-600">Qolgan kun</th>
              <th class="text-left p-4 text-sm font-medium text-slate-600">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in filteredSubscriptions" :key="sub.id" class="border-b border-slate-100 hover:bg-slate-50">
              <td class="p-4 font-medium text-slate-800">{{ sub.group_name }}</td>
              <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-bold" :class="getPlanBadgeClass(sub.plan_type)">
                  {{ getPlanLabel(sub.plan_type) }}
                </span>
              </td>
              <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-bold" :class="getStatusBadgeClass(sub.status)">
                  {{ getSubStatusLabel(sub.status) }}
                </span>
              </td>
              <td class="p-4 text-sm text-slate-600">{{ formatDate(sub.start_date) }} - {{ formatDate(sub.end_date) }}</td>
              <td class="p-4">
                <span :class="['font-semibold', sub.days_left <= 3 ? 'text-rose-600' : sub.days_left <= 7 ? 'text-amber-600' : 'text-emerald-600']">
                  {{ sub.days_left }} kun
                </span>
              </td>
              <td class="p-4">
                <div class="flex items-center gap-2 flex-wrap">
                  <!-- Faollashtirish (Activate) — for paused, cancelled, blocked, expired -->
                  <button
                    v-if="['paused', 'cancelled', 'blocked', 'expired'].includes(sub.status)"
                    @click="openStatusModal(sub, 'active')"
                    class="px-3 py-1.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors flex items-center gap-1.5 text-xs font-medium"
                  >
                    <Play class="w-3.5 h-3.5" /> {{ $t('common.active') }}
                  </button>
                  <!-- To'xtatish (Pause) — for active, trial -->
                  <button
                    v-if="['active', 'trial'].includes(sub.status)"
                    @click="openStatusModal(sub, 'paused')"
                    class="px-3 py-1.5 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors flex items-center gap-1.5 text-xs font-medium"
                  >
                    <Pause class="w-3.5 h-3.5" /> {{ $t('subscription.paused') }}
                  </button>
                  <!-- Bekor qilish (Cancel) — for active, trial, paused -->
                  <button
                    v-if="['active', 'trial', 'paused'].includes(sub.status)"
                    @click="openStatusModal(sub, 'cancelled')"
                    class="px-3 py-1.5 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors flex items-center gap-1.5 text-xs font-medium"
                  >
                    <Ban class="w-3.5 h-3.5" /> {{ $t('common.cancel') }}
                  </button>
                  <!-- Bloklash — for active, trial, paused -->
                  <button
                    v-if="['active', 'trial', 'paused'].includes(sub.status)"
                    @click="openStatusModal(sub, 'blocked')"
                    class="px-3 py-1.5 bg-red-700 text-white rounded-lg hover:bg-red-800 transition-colors flex items-center gap-1.5 text-xs font-medium"
                  >
                    <ShieldOff class="w-3.5 h-3.5" /> Bloklash
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab: Plans -->
    <div v-if="activeTab === 'plans'" class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <Package class="w-5 h-5 text-slate-400" />
          {{ $t('subscription.plans') }}
        </h3>
        <button
          @click="openCreatePlanModal"
          class="flex items-center gap-2 px-4 py-2.5 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors shadow-lg shadow-emerald-500/25"
        >
          <Plus class="w-4 h-4" />
          {{ $t('common.create') }}
        </button>
      </div>

      <div v-if="plansLoading" class="text-center py-12">
        <Loader2 class="w-8 h-8 text-emerald-500 animate-spin mx-auto" />
      </div>
      <div v-else-if="plans.length === 0" class="text-center py-12 bg-white rounded-2xl border border-slate-200">
        <DollarSign class="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-500">{{ $t('common.noData') }}</p>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="plan in plans"
          :key="plan.id"
          class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
        >
          <div :class="[
            'px-5 py-4 border-b',
            plan.plan_type === 'start' ? 'bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200' :
            plan.plan_type === 'plus' ? 'bg-gradient-to-r from-violet-50 to-violet-100 border-violet-200' :
            plan.plan_type === 'pro' ? 'bg-gradient-to-r from-amber-50 to-amber-100 border-amber-200' :
            'bg-gradient-to-r from-emerald-50 to-emerald-100 border-emerald-200'
          ]">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-bold text-lg text-slate-800">{{ plan.name }}</h4>
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="getPlanBadgeClass(plan.plan_type)">
                  {{ plan.plan_type }}
                </span>
              </div>
              <div class="flex gap-1.5">
                <button
                  @click="openEditPlanModal(plan)"
                  class="p-2 bg-white/80 hover:bg-white rounded-lg transition-colors shadow-sm"
                  title="Tahrirlash"
                >
                  <Pencil class="w-4 h-4 text-blue-600" />
                </button>
                <button
                  @click="openDeletePlan(plan)"
                  class="p-2 bg-white/80 hover:bg-white rounded-lg transition-colors shadow-sm"
                  title="O'chirish"
                >
                  <Trash2 class="w-4 h-4 text-rose-600" />
                </button>
              </div>
            </div>
          </div>
          <div class="p-5 space-y-4">
            <div class="text-center">
              <span class="text-3xl font-bold text-slate-800">{{ Number(plan.price).toLocaleString() }}</span>
              <span class="text-slate-500 text-sm ml-1">so'm / {{ plan.duration_days }} kun</span>
            </div>
            <p v-if="plan.description" class="text-sm text-slate-500 text-center">{{ plan.description }}</p>
            <div v-if="plan.features && plan.features.length > 0" class="space-y-2">
              <div
                v-for="(feature, idx) in plan.features"
                :key="idx"
                class="flex items-center gap-2 text-sm"
                :class="feature === 'Telegram Bot' ? 'text-blue-600 font-medium' : 'text-slate-600'"
              >
                <Bot v-if="feature === 'Telegram Bot'" class="w-4 h-4 text-blue-500 flex-shrink-0" />
                <CheckCircle v-else class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span>{{ feature }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Plan Create/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showPlanModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showPlanModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div class="sticky top-0 bg-white p-5 border-b border-slate-200 rounded-t-2xl z-10">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-slate-800">
                  {{ planModalMode === 'create' ? $t('common.create') : $t('common.edit') }}
                </h3>
                <button @click="showPlanModal = false" class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
                  <X class="w-5 h-5 text-slate-500" />
                </button>
              </div>
            </div>
            <div class="p-5 space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-slate-700 mb-1.5">Reja nomi</label>
                  <input
                    v-model="planForm.name"
                    type="text"
                    placeholder="Masalan: Pro"
                    class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
                  />
                </div>
                <div v-if="planModalMode === 'create'">
                  <label class="block text-sm font-medium text-slate-700 mb-1.5">Reja turi</label>
                  <select
                    v-model="planForm.plan_type"
                    class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
                  >
                    <option value="start">Start</option>
                    <option value="plus">Plus</option>
                    <option value="pro">Pro</option>
                    <option value="unlimited">Unlimited</option>
                  </select>
                </div>
                <div v-else>
                  <label class="block text-sm font-medium text-slate-700 mb-1.5">Reja turi</label>
                  <div class="px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-600">
                    {{ getPlanLabel(planForm.plan_type) }}
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1.5">Narxi (so'm)</label>
                  <input
                    v-model.number="planForm.price"
                    type="number"
                    min="0"
                    step="1000"
                    placeholder="50000"
                    class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1.5">Muddat (kun)</label>
                  <input
                    v-model.number="planForm.duration_days"
                    type="number"
                    min="1"
                    placeholder="30"
                    class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
                  />
                </div>
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-slate-700 mb-1.5">Tavsif</label>
                  <textarea
                    v-model="planForm.description"
                    rows="2"
                    placeholder="Qisqacha tavsif..."
                    class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none resize-none"
                  ></textarea>
                </div>
              </div>

              <!-- Features -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Imkoniyatlar</label>
                <div class="flex gap-2 mb-3">
                  <input
                    v-model="newFeature"
                    type="text"
                    placeholder="Masalan: Davomat"
                    @keydown.enter.prevent="addFeature"
                    class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
                  />
                  <button
                    @click="addFeature"
                    class="px-4 py-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors"
                  >
                    <Plus class="w-4 h-4" />
                  </button>
                </div>
                <div v-if="planForm.features.length > 0" class="flex flex-wrap gap-2">
                  <span
                    v-for="(feature, idx) in planForm.features"
                    :key="idx"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-sm"
                  >
                    <CheckCircle class="w-3.5 h-3.5" />
                    {{ feature }}
                    <button @click="removeFeature(idx)" class="ml-1 hover:text-rose-500 transition-colors">
                      <X class="w-3.5 h-3.5" />
                    </button>
                  </span>
                </div>
                <p v-else class="text-sm text-slate-400">Hali imkoniyat qo'shilmagan</p>
              </div>

              <!-- Price preview -->
              <div class="bg-slate-50 rounded-xl p-4 text-center">
                <span class="text-sm text-slate-500">Narx:</span>
                <span class="text-2xl font-bold text-slate-800 ml-2">{{ Number(planForm.price || 0).toLocaleString() }}</span>
                <span class="text-slate-500 ml-1">so'm / {{ planForm.duration_days || 30 }} kun</span>
              </div>
            </div>

            <div class="sticky bottom-0 bg-white p-5 border-t border-slate-200 rounded-b-2xl flex gap-3">
              <button
                @click="showPlanModal = false"
                class="flex-1 py-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                @click="savePlan"
                :disabled="planSaving"
                class="flex-1 py-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <Loader2 v-if="planSaving" class="w-4 h-4 animate-spin" />
                <Save v-else class="w-4 h-4" />
                {{ planSaving ? $t('settings.saving') : (planModalMode === 'create' ? $t('common.create') : $t('common.save')) }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Plan Confirm Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showDeleteConfirm = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <div class="text-center mb-4">
              <div class="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                <Trash2 class="w-6 h-6 text-rose-600" />
              </div>
              <h3 class="text-lg font-semibold text-slate-800">{{ $t('common.delete') }}</h3>
              <p class="text-sm text-slate-500 mt-1">
                "{{ deletingPlan?.name }}" - {{ $t('common.confirm') }}?
              </p>
            </div>
            <div class="flex gap-3">
              <button
                @click="showDeleteConfirm = false"
                class="flex-1 py-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                @click="confirmDeletePlan"
                class="flex-1 py-2.5 bg-rose-500 text-white rounded-xl hover:bg-rose-600 transition-colors font-medium"
              >
                {{ $t('common.delete') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Subscription Status Change Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showStatusModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showStatusModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div class="flex items-center gap-3 mb-4">
              <div :class="[
                'w-10 h-10 rounded-xl flex items-center justify-center',
                statusModalTarget === 'active' ? 'bg-emerald-100' :
                statusModalTarget === 'paused' ? 'bg-amber-100' :
                statusModalTarget === 'cancelled' ? 'bg-rose-100' :
                'bg-red-100'
              ]">
                <component :is="statusModalTarget === 'active' ? Play : statusModalTarget === 'paused' ? Pause : statusModalTarget === 'cancelled' ? Ban : ShieldOff" :class="[
                  'w-5 h-5',
                  statusModalTarget === 'active' ? 'text-emerald-600' :
                  statusModalTarget === 'paused' ? 'text-amber-600' :
                  statusModalTarget === 'cancelled' ? 'text-rose-600' :
                  'text-red-700'
                ]" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-slate-800">{{ getStatusActionTitle(statusModalTarget) }}</h3>
                <p class="text-sm text-slate-500">{{ statusModalSub?.group_name }}</p>
              </div>
            </div>
            <p class="text-sm text-slate-600 mb-4">
              "{{ statusModalSub?.group_name }}" guruhining obunasini
              <strong>{{ getSubStatusLabel(statusModalTarget) }}</strong> holatiga o'zgartirmoqchimisiz?
            </p>
            <textarea
              v-model="statusModalReason"
              rows="2"
              placeholder="Sabab (ixtiyoriy)..."
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none resize-none mb-4"
            ></textarea>
            <div class="flex gap-3">
              <button
                @click="showStatusModal = false"
                class="flex-1 py-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                @click="confirmStatusChange"
                :disabled="statusChanging"
                :class="[
                  'flex-1 py-2.5 text-white rounded-xl transition-colors font-medium flex items-center justify-center gap-2',
                  statusModalTarget === 'active' ? 'bg-emerald-500 hover:bg-emerald-600' :
                  statusModalTarget === 'paused' ? 'bg-amber-500 hover:bg-amber-600' :
                  statusModalTarget === 'cancelled' ? 'bg-rose-500 hover:bg-rose-600' :
                  'bg-red-700 hover:bg-red-800'
                ]"
              >
                <Loader2 v-if="statusChanging" class="w-4 h-4 animate-spin" />
                {{ statusChanging ? $t('common.loading') : $t('common.confirm') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Receipt Preview Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showReceiptModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showReceiptModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div class="flex items-center justify-between p-4 border-b border-slate-200">
              <h3 class="text-lg font-semibold text-slate-800">To'lov cheki — {{ receiptPayment?.group_name }}</h3>
              <button @click="showReceiptModal = false" class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
                <X class="w-5 h-5 text-slate-500" />
              </button>
            </div>
            <div class="flex-1 overflow-auto p-4 flex items-center justify-center bg-slate-50 min-h-[300px]">
              <Loader2 v-if="receiptLoading" class="w-8 h-8 text-emerald-500 animate-spin" />
              <img v-else-if="receiptUrl && !receiptIsPdf" :src="receiptUrl" class="max-w-full max-h-[70vh] rounded-lg shadow-lg object-contain" alt="Chek" />
              <iframe v-else-if="receiptUrl && receiptIsPdf" :src="receiptUrl" class="w-full h-[70vh] rounded-lg border-0"></iframe>
              <p v-else class="text-slate-400">Chek yuklanmadi</p>
            </div>
            <div class="p-4 border-t border-slate-200 flex justify-end">
              <button @click="showReceiptModal = false" class="px-5 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium">
                Yopish
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Reject Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showRejectModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h3 class="text-lg font-semibold text-slate-800 mb-4">To'lovni rad etish</h3>
            <textarea
              v-model="rejectNote"
              rows="3"
              placeholder="Rad etish sababini yozing..."
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 outline-none resize-none"
            ></textarea>
            <div class="flex gap-3 mt-4">
              <button
                @click="showRejectModal = false"
                class="flex-1 py-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                @click="rejectPayment"
                class="flex-1 py-2.5 bg-rose-500 text-white rounded-xl hover:bg-rose-600 transition-colors font-medium"
              >
                {{ $t('subscription.rejected') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import api from '@/services/api'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    Ban,
    Bot,
    Check,
    CheckCircle,
    Clock, CreditCard,
    Crown,
    DollarSign,
    Eye,
    Loader2,
    Package,
    Pause,
    Pencil,
    Play,
    Plus,
    Rocket,
    Save,
    Settings,
    ShieldOff,
    Trash2,
    X,
    XCircle
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'

const toast = useToastStore()
const langStore = useLanguageStore()
const { t } = langStore

const activeTab = ref('payments')
const tabs = computed(() => [
  { id: 'payments', label: 'To\'lovlar', icon: markRaw(CreditCard), badge: pendingCount.value || null },
  { id: 'market-payments', label: 'Market to\'lovlari', icon: markRaw(DollarSign), badge: marketPendingCount.value || null },
  { id: 'subscriptions', label: 'Obunalar', icon: markRaw(Crown), badge: null },
  { id: 'plans', label: 'Rejalar', icon: markRaw(DollarSign), badge: null },
  { id: 'settings', label: 'Sozlamalar', icon: markRaw(Settings), badge: null },
])

// Payments
const payments = ref([])
const paymentsLoading = ref(true)
const paymentStatusFilter = ref(null)
const paymentFilters = [
  { value: null, label: 'Barchasi' },
  { value: 'pending', label: 'Kutilmoqda' },
  { value: 'approved', label: 'Tasdiqlangan' },
  { value: 'rejected', label: 'Rad etilgan' },
]

const pendingCount = computed(() => payments.value.filter(p => p.status === 'pending').length)
const filteredPayments = computed(() => {
  if (!paymentStatusFilter.value) return payments.value
  return payments.value.filter(p => p.status === paymentStatusFilter.value)
})

// Market Tariff Payments
const marketPayments = ref([])
const marketPaymentsLoading = ref(true)
const marketPaymentFilter = ref(null)
const marketPendingCount = computed(() => marketPayments.value.filter(p => p.status === 'pending').length)
const filteredMarketPayments = computed(() => {
  if (!marketPaymentFilter.value) return marketPayments.value
  return marketPayments.value.filter(p => p.status === marketPaymentFilter.value)
})
const showMarketReceiptModal = ref(false)
const marketReceiptUrl = ref(null)
const marketReceiptIsPdf = ref(false)
const marketReceiptLoading = ref(false)
const marketReceiptPayment = ref(null)

// Subscriptions
const allSubscriptions = ref([])
const subsLoading = ref(true)
const subStatusFilter = ref(null)
const subFilters = [
  { value: null, label: 'Barchasi' },
  { value: 'active', label: 'Faol' },
  { value: 'trial', label: 'Sinov' },
  { value: 'paused', label: 'To\'xtatilgan' },
  { value: 'expired', label: 'Tugagan' },
  { value: 'cancelled', label: 'Bekor qilingan' },
  { value: 'blocked', label: 'Bloklangan' },
]
const filteredSubscriptions = computed(() => {
  if (!subStatusFilter.value) return allSubscriptions.value
  return allSubscriptions.value.filter(s => s.status === subStatusFilter.value)
})

// Status change modal
const showStatusModal = ref(false)
const statusModalSub = ref(null)
const statusModalTarget = ref('')
const statusModalReason = ref('')
const statusChanging = ref(false)

// Plans
const plans = ref([])
const plansLoading = ref(true)
const showPlanModal = ref(false)
const planModalMode = ref('create') // 'create' or 'edit'
const planSaving = ref(false)
const editingPlan = ref(null)
const planForm = ref({
  name: '',
  plan_type: 'start',
  price: 0,
  duration_days: 30,
  description: '',
  features: [],
})
const newFeature = ref('')
const showDeleteConfirm = ref(false)
const deletingPlan = ref(null)

// Settings
const settingsForm = ref({
  card_number: '',
  card_holder: '',
  trial_end_date: '',
  is_subscription_enabled: true,
})
const settingsSaving = ref(false)

// Trial
const trialActivated = ref(false)
const trialEndDate = ref('')
const trialLoading = ref(false)

// Receipt preview modal
const showReceiptModal = ref(false)
const receiptUrl = ref(null)
const receiptIsPdf = ref(false)
const receiptLoading = ref(false)
const receiptPayment = ref(null)

// Reject modal
const showRejectModal = ref(false)
const rejectNote = ref('')
const rejectingPayment = ref(null)

// Helpers
const getPlanLabel = (type) => {
  const labels = { start: 'Start', plus: 'Plus', pro: 'Pro', unlimited: 'Unlimited', trial: 'Sinov' }
  return labels[type] || type
}
const getStatusLabel = (status) => {
  const labels = { pending: 'Kutilmoqda', approved: 'Tasdiqlangan', rejected: 'Rad etilgan' }
  return labels[status] || status
}
const getSubStatusLabel = (status) => {
  const labels = { trial: 'Sinov', active: 'Faol', expired: 'Tugagan', blocked: 'Bloklangan', cancelled: 'Bekor qilingan', paused: 'To\'xtatilgan' }
  return labels[status] || status
}
const getPlanBadgeClass = (type) => {
  const cls = { start: 'bg-blue-100 text-blue-700', plus: 'bg-violet-100 text-violet-700', pro: 'bg-amber-100 text-amber-700', unlimited: 'bg-emerald-100 text-emerald-700' }
  return cls[type] || 'bg-slate-100 text-slate-700'
}
const getStatusBadgeClass = (status) => {
  const cls = { trial: 'bg-amber-100 text-amber-700', active: 'bg-emerald-100 text-emerald-700', expired: 'bg-rose-100 text-rose-700', blocked: 'bg-red-100 text-red-700', cancelled: 'bg-slate-100 text-slate-700', paused: 'bg-orange-100 text-orange-700' }
  return cls[status] || 'bg-slate-100 text-slate-700'
}
const formatDate = (d) => d ? new Date(d).toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short' }) : '-'
const formatDateTime = (d) => d ? new Date(d).toLocaleString('uz-UZ', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '-'

const viewReceipt = async (payment) => {
  receiptPayment.value = payment
  receiptUrl.value = null
  receiptIsPdf.value = false
  receiptLoading.value = true
  showReceiptModal.value = true
  try {
    const token = localStorage.getItem('access_token') || ''
    const resp = await fetch(`/api/v1/subscriptions/receipt/${payment.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!resp.ok) throw new Error('Yuklab bo\'lmadi')
    const contentType = resp.headers.get('content-type') || ''
    receiptIsPdf.value = contentType.includes('pdf')
    const blob = await resp.blob()
    receiptUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    console.error(e)
    toast.error('Chekni yuklashda xatolik')
    showReceiptModal.value = false
  } finally {
    receiptLoading.value = false
  }
}

// Actions
const approvePayment = async (payment) => {
  try {
    await api.actionPayment(payment.id, { status: 'approved' })
    payment.status = 'approved'
    toast.success(`"${payment.group_name}" guruhi obunasi tasdiqlandi!`)
    await loadSubscriptions()
  } catch (e) {
    toast.error(e.message || 'Xatolik')
  }
}

const openRejectModal = (payment) => {
  rejectingPayment.value = payment
  rejectNote.value = ''
  showRejectModal.value = true
}

const rejectPayment = async () => {
  if (!rejectingPayment.value) return
  try {
    await api.actionPayment(rejectingPayment.value.id, { status: 'rejected', admin_note: rejectNote.value })
    rejectingPayment.value.status = 'rejected'
    rejectingPayment.value.admin_note = rejectNote.value
    showRejectModal.value = false
    toast.success('To\'lov rad etildi')
  } catch (e) {
    toast.error(e.message || 'Xatolik')
  }
}

const saveSettings = async () => {
  settingsSaving.value = true
  try {
    await api.updateSubscriptionSettings(settingsForm.value)
    toast.success('Sozlamalar saqlandi')
  } catch (e) {
    toast.error(e.message || 'Xatolik')
  } finally {
    settingsSaving.value = false
  }
}

const activateTrial = async () => {
  trialLoading.value = true
  try {
    const result = await api.activateTrial()
    toast.success(result.message || 'Sinov muddati faollashtirildi!')
    trialActivated.value = true
    trialEndDate.value = result.trial_end_date
    settingsForm.value.trial_end_date = result.trial_end_date
  } catch (e) {
    toast.error(e.message || 'Xatolik')
  } finally {
    trialLoading.value = false
  }
}

const loadPayments = async () => {
  paymentsLoading.value = true
  try {
    const resp = await api.getSubscriptionPayments()
    payments.value = resp?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    paymentsLoading.value = false
  }
}

// Status change actions
const getStatusActionTitle = (status) => {
  const titles = {
    active: 'Obunani faollashtirish',
    paused: 'Obunani to\'xtatish',
    cancelled: 'Obunani bekor qilish',
    blocked: 'Obunani bloklash'
  }
  return titles[status] || 'Holatni o\'zgartirish'
}

const openStatusModal = (sub, targetStatus) => {
  statusModalSub.value = sub
  statusModalTarget.value = targetStatus
  statusModalReason.value = ''
  showStatusModal.value = true
}

const confirmStatusChange = async () => {
  if (!statusModalSub.value) return
  statusChanging.value = true
  try {
    const result = await api.updateSubscriptionStatus(statusModalSub.value.id, {
      status: statusModalTarget.value,
      reason: statusModalReason.value || null
    })
    // Update local state
    const sub = allSubscriptions.value.find(s => s.id === statusModalSub.value.id)
    if (sub) sub.status = statusModalTarget.value
    showStatusModal.value = false
    toast.success(result.message || t('common.success'))
  } catch (e) {
    toast.error(e.message || t('common.error'))
  } finally {
    statusChanging.value = false
  }
}

// Plans management
const loadPlans = async () => {
  plansLoading.value = true
  try {
    const resp = await api.getSubscriptionPlans()
    plans.value = Array.isArray(resp) ? resp : []
  } catch (e) {
    console.error(e)
  } finally {
    plansLoading.value = false
  }
}

const openCreatePlanModal = () => {
  planModalMode.value = 'create'
  editingPlan.value = null
  planForm.value = {
    name: '',
    plan_type: 'start',
    price: 0,
    duration_days: 30,
    description: '',
    features: [],
  }
  newFeature.value = ''
  showPlanModal.value = true
}

const openEditPlanModal = (plan) => {
  planModalMode.value = 'edit'
  editingPlan.value = plan
  planForm.value = {
    name: plan.name,
    plan_type: plan.plan_type,
    price: plan.price,
    duration_days: plan.duration_days,
    description: plan.description || '',
    features: [...(plan.features || [])],
  }
  newFeature.value = ''
  showPlanModal.value = true
}

const addFeature = () => {
  const f = newFeature.value.trim()
  if (f && !planForm.value.features.includes(f)) {
    planForm.value.features.push(f)
    newFeature.value = ''
  }
}

const removeFeature = (index) => {
  planForm.value.features.splice(index, 1)
}

const savePlan = async () => {
  if (!planForm.value.name || !planForm.value.price) {
    toast.error(t('common.error'))
    return
  }
  planSaving.value = true
  try {
    if (planModalMode.value === 'create') {
      await api.createSubscriptionPlan(planForm.value)
      toast.success(t('common.success'))
    } else {
      await api.updateSubscriptionPlan(editingPlan.value.id, planForm.value)
      toast.success(t('common.success'))
    }
    showPlanModal.value = false
    await loadPlans()
  } catch (e) {
    toast.error(e.message || t('common.error'))
  } finally {
    planSaving.value = false
  }
}

const openDeletePlan = (plan) => {
  deletingPlan.value = plan
  showDeleteConfirm.value = true
}

const confirmDeletePlan = async () => {
  if (!deletingPlan.value) return
  try {
    await api.deleteSubscriptionPlan(deletingPlan.value.id)
    toast.success(t('common.success'))
    showDeleteConfirm.value = false
    await loadPlans()
  } catch (e) {
    toast.error(e.message || t('common.error'))
  }
}

const formatPrice = (price) => {
  return Number(price).toLocaleString('uz-UZ') + ' so\'m'
}

const loadSubscriptions = async () => {
  subsLoading.value = true
  try {
    const resp = await api.getAllSubscriptions()
    allSubscriptions.value = resp?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    subsLoading.value = false
  }
}

// Market tariff payments
const loadMarketPayments = async () => {
  marketPaymentsLoading.value = true
  try {
    const resp = await api.request('/market/tariff-payments')
    marketPayments.value = resp?.items || []
  } catch (e) {
    console.error('Market payments load error:', e)
  } finally {
    marketPaymentsLoading.value = false
  }
}

const viewMarketReceipt = async (payment) => {
  marketReceiptPayment.value = payment
  marketReceiptUrl.value = null
  marketReceiptIsPdf.value = false
  marketReceiptLoading.value = true
  showMarketReceiptModal.value = true
  try {
    const token = localStorage.getItem('access_token') || ''
    const resp = await fetch(`/api/v1/market/tariff-receipt/${payment.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!resp.ok) throw new Error('Yuklab bo\'lmadi')
    const contentType = resp.headers.get('content-type') || ''
    marketReceiptIsPdf.value = contentType.includes('pdf')
    const blob = await resp.blob()
    marketReceiptUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    console.error(e)
    toast.error('Chekni yuklashda xatolik')
    showMarketReceiptModal.value = false
  } finally {
    marketReceiptLoading.value = false
  }
}

const approveMarketPayment = async (payment) => {
  try {
    await api.request(`/market/tariff-payments/${payment.id}?action=approved`, { method: 'PATCH' })
    payment.status = 'approved'
    toast.success(`${payment.user_name} — ${payment.tariff === 'student_pro' ? 'Student Pro' : 'Premium'} tarifi tasdiqlandi!`)
  } catch (e) {
    toast.error(e.message || 'Xatolik')
  }
}

const rejectMarketPayment = async (payment) => {
  const note = prompt('Rad etish sababini yozing:')
  if (note === null) return
  try {
    await api.request(`/market/tariff-payments/${payment.id}?action=rejected&admin_note=${encodeURIComponent(note || '')}`, { method: 'PATCH' })
    payment.status = 'rejected'
    payment.admin_note = note
    toast.success('Market to\'lov rad etildi')
  } catch (e) {
    toast.error(e.message || 'Xatolik')
  }
}

const loadSettings = async () => {
  try {
    const resp = await api.getSubscriptionSettings()
    settingsForm.value = {
      card_number: resp.card_number || '',
      card_holder: resp.card_holder || '',
      trial_end_date: resp.trial_end_date || '',
      is_subscription_enabled: resp.is_subscription_enabled ?? true,
    }
    if (resp.trial_end_date) {
      trialActivated.value = true
      trialEndDate.value = resp.trial_end_date
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await Promise.all([loadPayments(), loadSubscriptions(), loadSettings(), loadPlans(), loadMarketPayments()])
})
</script>
