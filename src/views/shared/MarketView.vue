<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 rounded-3xl p-6 md:p-8 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 animate-pulse"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
      <div class="absolute top-1/2 right-1/4 w-32 h-32 bg-white/5 rounded-full animate-bounce" style="animation-duration: 3s"></div>
      <div class="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <Store class="w-6 h-6" />
            </div>
            <div>
              <span class="text-sm font-medium text-white/70">UniMarket</span>
              <div class="flex items-center gap-2">
                <span v-if="profile" :class="[
                  'text-xs px-2 py-0.5 rounded-full font-semibold',
                  profile.tariff === 'premium' ? 'bg-amber-400/30 text-amber-100' :
                  profile.tariff === 'student_pro' ? 'bg-emerald-400/30 text-emerald-100' :
                  'bg-white/20 text-white/80'
                ]">
                  {{ getTariffLabel(profile.tariff) }}
                </span>
              </div>
            </div>
          </div>
          <h1 class="text-2xl md:text-3xl font-bold">{{ $t('market.headerTitle') }}</h1>
          <p class="text-white/80 mt-1 max-w-xl text-sm">{{ $t('market.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <div v-if="profile" class="bg-white/15 backdrop-blur rounded-2xl px-5 py-3 text-center">
            <p class="text-xs text-white/60">{{ $t('market.balance') }}</p>
            <p class="text-xl font-bold">{{ formatPrice(profile.balance || 0) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex flex-wrap gap-2">
      <button v-for="tab in mainTabs" :key="tab.value"
        @click="activeTab = tab.value"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all',
          activeTab === tab.value
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/25'
            : 'bg-white border border-slate-200 text-slate-600 hover:border-emerald-300 hover:text-emerald-600'
        ]"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
        <span v-if="tab.badge" class="bg-white/30 text-[10px] px-1.5 py-0.5 rounded-full font-bold">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- 🎯 FREE Tariff Upgrade CTA Banner — eye-catching animated -->
    <div v-if="profile && profile.tariff === 'free' && profile.tariff_source !== 'group_subscription'"
      class="relative bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-2xl p-5 text-white shadow-xl shadow-purple-500/20 overflow-hidden">
      <div class="absolute -top-6 -right-6 w-32 h-32 bg-yellow-400/20 rounded-full blur-2xl animate-pulse"></div>
      <div class="absolute -bottom-4 -left-4 w-24 h-24 bg-pink-400/20 rounded-full blur-xl"></div>
      <div class="absolute top-2 right-4 text-4xl animate-bounce" style="animation-duration: 2s">🚀</div>
      <div class="relative flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center flex-shrink-0">
            <Zap class="w-7 h-7 text-yellow-300" />
          </div>
          <div>
            <h3 class="font-bold text-lg">{{ $t('market.unlockPower') }}</h3>
            <p class="text-sm text-white/80 max-w-md">{{ $t('market.unlockPowerDesc') }}</p>
            <div class="flex items-center gap-3 mt-2 text-xs text-white/60">
              <span class="flex items-center gap-1"><CheckCircle2 class="w-3.5 h-3.5 text-emerald-300" /> {{ $t('market.canPost') }}</span>
              <span class="flex items-center gap-1"><CheckCircle2 class="w-3.5 h-3.5 text-emerald-300" /> {{ $t('market.chatEnabled') }}</span>
              <span class="flex items-center gap-1"><CheckCircle2 class="w-3.5 h-3.5 text-emerald-300" /> {{ $t('market.escrowEnabled') }}</span>
            </div>
          </div>
        </div>
        <button @click="showTariffModal = true"
          class="bg-white text-purple-700 px-6 py-3 rounded-xl font-bold hover:bg-purple-50 transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 flex items-center gap-2 flex-shrink-0">
          <Sparkles class="w-5 h-5" />
          {{ $t('market.upgradeNow') }}
        </button>
      </div>
    </div>

    <!-- 🎓 Group Subscription Banner — elegant -->
    <div v-if="profile && profile.tariff_source === 'group_subscription'"
      class="relative bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 rounded-2xl p-5 text-white shadow-xl shadow-emerald-500/20 overflow-hidden">
      <div class="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
      <div class="absolute bottom-0 left-1/3 w-20 h-20 bg-white/5 rounded-full blur-lg"></div>
      <div class="relative flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center flex-shrink-0 ring-2 ring-white/30">
            <Crown class="w-7 h-7 text-yellow-300" />
          </div>
          <div>
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-bold text-lg">{{ $t('market.groupSubscription') }}</h3>
              <span class="bg-white/20 text-xs px-2 py-0.5 rounded-full font-semibold">✨ {{ $t('market.freeAccess') }}</span>
            </div>
            <p class="text-sm text-white/80">{{ $t('market.groupSubDescription') }}</p>
          </div>
        </div>
        <div class="bg-white/15 backdrop-blur rounded-xl px-4 py-2.5 text-center flex-shrink-0">
          <p class="text-xs text-white/60">{{ $t('market.activePlan') }}</p>
          <p class="font-bold text-lg">Student Pro</p>
          <p class="text-xs text-white/50">{{ profile.group_plan === 'unlimited' ? '∞ Unlimited' : '⭐ Pro' }} {{ $t('market.group') }}</p>
        </div>
      </div>
    </div>

    <!-- Browse Tab -->
    <div v-if="activeTab === 'browse'" class="space-y-4">
      <!-- Search & Filters -->
      <div class="bg-white rounded-2xl border border-slate-200 p-4 flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <Search class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('market.searchPlaceholder')"
            class="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
            @input="debouncedSearch"
          />
        </div>
        <select v-model="selectedCategory" @change="loadListings" class="border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
          <option value="">{{ $t('market.allCategories') }}</option>
          <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
        </select>
      </div>

      <!-- Listings Grid -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
      </div>

      <div v-else-if="listings.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Package class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noListings') }}</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="listing in listings" :key="listing.id"
          @click="openListing(listing)"
          class="bg-white rounded-2xl border border-slate-200 hover:shadow-lg hover:border-emerald-200 transition-all cursor-pointer overflow-hidden group"
        >
          <div class="p-5">
            <div class="flex items-start justify-between mb-3">
              <span class="px-2.5 py-1 text-xs rounded-full font-medium"
                :class="getCategoryColor(listing.category)">
                {{ getCategoryLabel(listing.category) }}
              </span>
              <span class="text-xs text-slate-400">
                <Eye class="w-3 h-3 inline" /> {{ listing.views }}
              </span>
            </div>
            <h3 class="font-semibold text-slate-800 mb-1 line-clamp-2 group-hover:text-emerald-600 transition-colors">{{ listing.title }}</h3>
            <p class="text-sm text-slate-500 line-clamp-2 mb-3">{{ listing.description }}</p>

            <div class="flex items-center gap-2 mb-3">
              <div class="w-7 h-7 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center">
                <User class="w-3.5 h-3.5 text-white" />
              </div>
              <span class="text-sm text-slate-600">{{ listing.seller_name }}</span>
              <div class="flex items-center gap-1 ml-auto">
                <Star class="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                <span class="text-xs text-slate-500 font-medium">{{ (listing.seller_rating || 0).toFixed(1) }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between pt-3 border-t border-slate-100">
              <span class="text-lg font-bold text-emerald-600">
                {{ formatPrice(listing.price) }}
              </span>
              <span class="text-xs text-slate-400">
                <Clock class="w-3 h-3 inline" /> {{ listing.delivery_days }} {{ $t('market.days') }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalListings > pageSize" class="flex justify-center gap-2 pt-4">
        <button @click="currentPage--; loadListings()" :disabled="currentPage <= 1"
          class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm disabled:opacity-50 hover:border-emerald-300 transition-colors">←</button>
        <span class="px-4 py-2 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl">{{ currentPage }} / {{ Math.ceil(totalListings / pageSize) }}</span>
        <button @click="currentPage++; loadListings()" :disabled="currentPage >= Math.ceil(totalListings / pageSize)"
          class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm disabled:opacity-50 hover:border-emerald-300 transition-colors">→</button>
      </div>
    </div>

    <!-- My Listings Tab -->
    <div v-if="activeTab === 'my-listings'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold text-slate-800">{{ $t('market.myListings') }}</h2>
        <button @click="showCreateModal = true"
          class="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2.5 rounded-xl text-sm font-semibold hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2">
          <Plus class="w-4 h-4" /> {{ $t('market.createListing') }}
        </button>
      </div>

      <div v-if="myListings.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Package class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noMyListings') }}</p>
      </div>

      <div v-for="listing in myListings" :key="listing.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 flex flex-col sm:flex-row sm:items-center gap-4 hover:shadow-md transition-all">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span :class="getStatusBadge(listing.status)" class="px-2.5 py-0.5 text-xs rounded-full font-medium">
              {{ getStatusLabel(listing.status) }}
            </span>
            <span class="text-xs text-slate-400">{{ getCategoryLabel(listing.category) }}</span>
          </div>
          <h3 class="font-semibold text-slate-800">{{ listing.title }}</h3>
          <p class="text-sm text-slate-500">{{ formatPrice(listing.price) }} · {{ listing.orders_count }} {{ $t('market.ordersCount') }}</p>
          <p v-if="listing.rejection_reason" class="text-xs text-rose-500 mt-1">❌ {{ listing.rejection_reason }}</p>
        </div>
        <div class="flex gap-2">
          <button @click="editListing(listing)" class="p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-100 hover:border-slate-300 transition-colors">
            <Pencil class="w-4 h-4" />
          </button>
          <button @click="deleteListing(listing)" class="p-2.5 bg-rose-50 border border-rose-200 text-rose-600 rounded-xl hover:bg-rose-100 transition-colors">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- My Orders Tab -->
    <div v-if="activeTab === 'my-orders'" class="space-y-4">
      <div class="flex gap-2 flex-wrap mb-4">
        <button v-for="tab in orderTabs" :key="tab.value"
          @click="orderFilter = tab.value; loadOrders()"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
            orderFilter === tab.value
              ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
              : 'bg-white text-slate-600 border border-slate-200 hover:border-emerald-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="orders.length === 0" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <ClipboardList class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('market.noOrders') }}</p>
      </div>

      <div v-for="order in orders" :key="order.id"
        @click="openOrder(order)"
        class="bg-white rounded-2xl border border-slate-200 p-5 cursor-pointer hover:shadow-lg hover:border-emerald-200 transition-all">
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span :class="getOrderStatusBadge(order.status)" class="px-2.5 py-0.5 text-xs rounded-full font-medium">
                {{ getOrderStatusLabel(order.status) }}
              </span>
              <span class="text-xs text-slate-400">#{{ order.id }}</span>
            </div>
            <h3 class="font-semibold text-slate-800">{{ order.title }}</h3>
            <p class="text-sm text-slate-500">
              {{ order.buyer_id === authStore.user?.id ? $t('market.seller') + ': ' + order.seller_name : $t('market.buyer') + ': ' + order.buyer_name }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-lg font-bold text-emerald-600">{{ formatPrice(order.amount) }}</p>
            <p v-if="order.deadline" class="text-xs text-slate-400">
              <Clock class="w-3 h-3 inline" /> {{ formatDate(order.deadline) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Wallet Tab -->
    <div v-if="activeTab === 'wallet'" class="space-y-5">
      <!-- Wallet Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-5 text-white relative overflow-hidden shadow-lg shadow-emerald-500/20">
          <div class="absolute -top-4 -right-4 w-20 h-20 bg-white/10 rounded-full blur-lg"></div>
          <div class="relative">
            <div class="flex items-center justify-between mb-3">
              <p class="text-sm text-white/70 font-medium">{{ $t('market.balance') }}</p>
              <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                <Wallet class="w-5 h-5" />
              </div>
            </div>
            <p class="text-3xl font-bold">{{ formatPrice(profile?.balance || 0) }}</p>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm text-slate-500 font-medium">{{ $t('market.totalEarned') }}</p>
            <div class="w-10 h-10 bg-teal-100 rounded-xl flex items-center justify-center">
              <TrendingUp class="w-5 h-5 text-teal-600" />
            </div>
          </div>
          <p class="text-2xl font-bold text-teal-600">{{ formatPrice(profile?.total_earned || 0) }}</p>
          <p class="text-xs text-slate-400 mt-1">{{ $t('market.fromSelling') }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm text-slate-500 font-medium">{{ $t('market.totalSpent') }}</p>
            <div class="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center">
              <CreditCard class="w-5 h-5 text-slate-600" />
            </div>
          </div>
          <p class="text-2xl font-bold text-slate-700">{{ formatPrice(profile?.total_spent || 0) }}</p>
          <p class="text-xs text-slate-400 mt-1">{{ $t('market.fromBuying') }}</p>
        </div>
      </div>

      <!-- 🎯 Tariff Card — Premium Design -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <!-- Tariff Header -->
        <div :class="[
          'p-5 relative overflow-hidden',
          profile?.tariff === 'premium' ? 'bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 text-white' :
          profile?.tariff === 'student_pro' ? 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white' :
          'bg-gradient-to-r from-slate-100 to-slate-200 text-slate-800'
        ]">
          <div class="absolute -top-6 -right-6 w-32 h-32 rounded-full opacity-20"
            :class="profile?.tariff === 'free' ? 'bg-slate-300' : 'bg-white'"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-2xl flex items-center justify-center"
                :class="profile?.tariff === 'free' ? 'bg-slate-300/50' : 'bg-white/20 ring-2 ring-white/30'">
                <component :is="profile?.tariff === 'premium' ? Gem : profile?.tariff === 'student_pro' ? Zap : Lock" class="w-7 h-7"
                  :class="profile?.tariff === 'free' ? 'text-slate-500' : 'text-white'" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-bold text-xl">{{ getTariffLabel(profile?.tariff) }}</h3>
                  <span v-if="profile?.tariff_source === 'group_subscription'"
                    class="bg-white/20 text-xs px-2.5 py-0.5 rounded-full font-semibold flex items-center gap-1">
                    <Crown class="w-3 h-3" /> {{ $t('market.fromGroupSub') }}
                  </span>
                </div>
                <p class="text-sm opacity-80">{{ $t('market.currentTariff') }}</p>
              </div>
            </div>
            <button v-if="profile?.tariff !== 'premium' && profile?.tariff_source !== 'group_subscription'"
              @click="showTariffModal = true"
              class="bg-white/90 hover:bg-white text-emerald-700 px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 flex items-center gap-2">
              <Sparkles class="w-4 h-4" />
              {{ $t('market.upgradeNow') }}
            </button>
          </div>
        </div>

        <!-- Tariff Limits Grid -->
        <div class="p-5">
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-3.5 border border-blue-100">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-7 h-7 bg-blue-100 rounded-lg flex items-center justify-center">
                  <ClipboardList class="w-3.5 h-3.5 text-blue-600" />
                </div>
                <p class="text-xs text-blue-600 font-medium">{{ $t('market.maxOrders') }}</p>
              </div>
              <p class="text-2xl font-bold text-blue-700">{{ tariffLimits.max_active_orders || '—' }}</p>
            </div>
            <div class="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-3.5 border border-emerald-100">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-7 h-7 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <Banknote class="w-3.5 h-3.5 text-emerald-600" />
                </div>
                <p class="text-xs text-emerald-600 font-medium">{{ $t('market.maxAmount') }}</p>
              </div>
              <p class="text-lg font-bold text-emerald-700">{{ tariffLimits.max_amount_per_order ? formatCompact(tariffLimits.max_amount_per_order) : '—' }}</p>
            </div>
            <div class="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-3.5 border border-purple-100">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-7 h-7 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Percent class="w-3.5 h-3.5 text-purple-600" />
                </div>
                <p class="text-xs text-purple-600 font-medium">{{ $t('market.commission') }}</p>
              </div>
              <p class="text-2xl font-bold text-purple-700">{{ (tariffLimits.commission_rate * 100) }}%</p>
            </div>
            <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-3.5 border border-amber-100">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-7 h-7 bg-amber-100 rounded-lg flex items-center justify-center">
                  <Timer class="w-3.5 h-3.5 text-amber-600" />
                </div>
                <p class="text-xs text-amber-600 font-medium">{{ $t('market.payoutDelay') }}</p>
              </div>
              <p class="text-2xl font-bold text-amber-700">{{ tariffLimits.payout_delay_hours }}<span class="text-sm font-medium">{{ $t('market.hours') }}</span></p>
            </div>
          </div>

          <!-- Group Subscription Notice -->
          <div v-if="profile?.tariff_source === 'group_subscription'" class="mt-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-4 flex items-start gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
              <Crown class="w-4 h-4 text-emerald-600" />
            </div>
            <div>
              <p class="text-sm font-semibold text-emerald-800">{{ $t('market.groupSubActive') }}</p>
              <p class="text-xs text-emerald-600 mt-1">{{ $t('market.groupSubHint') }}</p>
            </div>
          </div>

          <!-- Free Tariff Upgrade Prompt -->
          <div v-if="profile?.tariff === 'free' && profile?.tariff_source !== 'group_subscription'"
            class="mt-4 bg-gradient-to-r from-violet-50 to-purple-50 border border-violet-200 rounded-xl p-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-violet-400 to-purple-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Rocket class="w-5 h-5 text-white" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-semibold text-violet-800">{{ $t('market.whyUpgrade') }}</p>
                <p class="text-xs text-violet-600 mt-0.5">{{ $t('market.whyUpgradeDesc') }}</p>
              </div>
              <button @click="showTariffModal = true"
                class="bg-gradient-to-r from-violet-500 to-purple-600 text-white px-4 py-2 rounded-xl text-sm font-bold hover:from-violet-600 hover:to-purple-700 transition-all shadow-md flex-shrink-0">
                {{ $t('market.letsGo') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Payout Section -->
      <div v-if="profile?.balance > 0" class="bg-white rounded-2xl border border-slate-200 p-5">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <ArrowDownToLine class="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <h3 class="font-bold text-lg text-slate-800">{{ $t('market.requestPayout') }}</h3>
            <p class="text-xs text-slate-400">{{ $t('market.payoutHint') }}</p>
          </div>
        </div>
        <div class="flex flex-col sm:flex-row gap-3">
          <div class="flex-1 relative">
            <label class="text-xs font-medium text-slate-500 absolute -top-2 left-3 bg-white px-1">{{ $t('market.amount') }}</label>
            <input v-model.number="payoutAmount" type="number" :placeholder="$t('market.amount')"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all" />
          </div>
          <div class="flex-1 relative">
            <label class="text-xs font-medium text-slate-500 absolute -top-2 left-3 bg-white px-1">{{ $t('market.cardNumber') }}</label>
            <input v-model="payoutCard" type="text" :placeholder="$t('market.cardNumber')"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all" />
          </div>
          <button @click="requestPayout"
            class="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-6 py-2.5 rounded-xl font-semibold hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/25 transition-all flex items-center gap-2 flex-shrink-0">
            <ArrowDownToLine class="w-4 h-4" />
            {{ $t('market.withdraw') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Listing Detail Modal -->
    <div v-if="selectedListing" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selectedListing = null">
      <div class="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <span :class="getCategoryColor(selectedListing.category)" class="px-2.5 py-1 text-xs rounded-full font-medium">
                {{ getCategoryLabel(selectedListing.category) }}
              </span>
              <h2 class="text-xl font-bold text-slate-800 mt-2">{{ selectedListing.title }}</h2>
            </div>
            <button @click="selectedListing = null" class="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors">
              <X class="w-5 h-5" />
            </button>
          </div>

          <p class="text-slate-600 mb-4 whitespace-pre-wrap">{{ selectedListing.description }}</p>

          <div class="grid grid-cols-2 gap-3 mb-4 text-sm">
            <div class="flex items-center gap-2 bg-slate-50 rounded-xl p-3">
              <div class="w-8 h-8 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-lg flex items-center justify-center">
                <User class="w-4 h-4 text-white" />
              </div>
              <div>
                <span class="text-slate-800 font-medium">{{ selectedListing.seller_name }}</span>
                <div class="flex items-center gap-1">
                  <Star class="w-3 h-3 text-amber-400 fill-amber-400" />
                  <span class="text-xs text-slate-500">{{ (selectedListing.seller_rating || 0).toFixed(1) }}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2 bg-slate-50 rounded-xl p-3">
              <Clock class="w-4 h-4 text-slate-400" />
              <span class="text-slate-800">{{ selectedListing.delivery_days }} {{ $t('market.days') }}</span>
            </div>
            <div v-if="selectedListing.subject" class="flex items-center gap-2 bg-slate-50 rounded-xl p-3">
              <BookOpen class="w-4 h-4 text-slate-400" />
              <span class="text-slate-800">{{ selectedListing.subject }}</span>
            </div>
            <div class="flex items-center gap-2 bg-slate-50 rounded-xl p-3">
              <RefreshCcw class="w-4 h-4 text-slate-400" />
              <span class="text-slate-800">{{ selectedListing.max_revisions }} {{ $t('market.revisions') }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between pt-4 border-t border-slate-100">
            <span class="text-2xl font-bold text-emerald-600">{{ formatPrice(selectedListing.price) }}</span>
            <button
              v-if="selectedListing.seller_id !== authStore.user?.id"
              @click="showOrderModal = true"
              class="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-6 py-2.5 rounded-xl font-semibold hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/25 transition-all flex items-center gap-2">
              <ShoppingBag class="w-4 h-4" />
              {{ $t('market.placeOrder') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Listing Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showCreateModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="p-6">
          <h2 class="text-xl font-bold text-slate-800 mb-4">{{ editingListing ? $t('market.editListing') : $t('market.createListing') }}</h2>
          <div class="space-y-3">
            <div>
              <label class="text-sm font-medium text-slate-700">{{ $t('market.listingTitle') }}</label>
              <input v-model="listingForm.title" type="text" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
            </div>
            <div>
              <label class="text-sm font-medium text-slate-700">{{ $t('market.description') }}</label>
              <textarea v-model="listingForm.description" rows="4" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-slate-700">{{ $t('market.category') }}</label>
                <select v-model="listingForm.category" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
                  <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
                </select>
              </div>
              <div>
                <label class="text-sm font-medium text-slate-700">{{ $t('market.price') }} (UZS)</label>
                <input v-model.number="listingForm.price" type="number" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-slate-700">{{ $t('market.deliveryDays') }}</label>
                <input v-model.number="listingForm.delivery_days" type="number" min="1" max="30" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
              </div>
              <div>
                <label class="text-sm font-medium text-slate-700">{{ $t('market.maxRevisions') }}</label>
                <input v-model.number="listingForm.max_revisions" type="number" min="0" max="5" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
              </div>
            </div>
            <div>
              <label class="text-sm font-medium text-slate-700">{{ $t('market.subjectOptional') }}</label>
              <input v-model="listingForm.subject" type="text" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
            </div>
          </div>
          <div class="flex gap-3 mt-5">
            <button @click="showCreateModal = false; editingListing = null" class="flex-1 border border-slate-200 rounded-xl py-2.5 font-medium text-slate-600 hover:bg-slate-50 transition-colors">
              {{ $t('common.cancel') }}
            </button>
            <button @click="submitListing" class="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl py-2.5 font-semibold hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/25 transition-all">
              {{ editingListing ? $t('common.save') : $t('market.publish') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Place Order Modal -->
    <div v-if="showOrderModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showOrderModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl">
        <div class="p-6">
          <h2 class="text-xl font-bold text-slate-800 mb-4">{{ $t('market.placeOrder') }}</h2>

          <!-- Step 1: Requirements -->
          <div v-if="orderStep === 1">
            <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 mb-4 text-sm">
              <p class="font-medium text-emerald-700">🛡️ {{ $t('market.garantInfo') }}</p>
            </div>
            <div class="space-y-3">
              <div>
                <label class="text-sm font-medium text-slate-700">{{ $t('market.requirements') }}</label>
                <textarea v-model="orderForm.requirements" rows="3" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  :placeholder="$t('market.requirementsPlaceholder')"></textarea>
              </div>
              <div>
                <label class="text-sm font-medium text-slate-700">{{ $t('market.deadline') }}</label>
                <input v-model.number="orderForm.deadline_days" type="number" min="1" max="30"
                  class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mt-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" :placeholder="$t('market.deadlinePlaceholder')" />
              </div>
            </div>
            <div class="bg-slate-50 rounded-xl p-4 mt-4 text-sm">
              <div class="flex justify-between"><span class="text-slate-500">{{ $t('market.servicePrice') }}</span><span class="font-bold text-slate-800">{{ formatPrice(selectedListing?.price) }}</span></div>
              <div class="flex justify-between text-slate-400"><span>{{ $t('market.escrowHold') }}</span><span>{{ $t('market.garantHoldNote') }}</span></div>
            </div>
            <div class="flex gap-3 mt-5">
              <button @click="showOrderModal = false; orderStep = 1" class="flex-1 border border-slate-200 rounded-xl py-2.5 font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                {{ $t('common.cancel') }}
              </button>
              <button @click="orderStep = 2" class="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl py-2.5 font-semibold hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/25 transition-all">
                {{ $t('market.continue') }} →
              </button>
            </div>
          </div>

          <!-- Step 2: Payment -->
          <div v-if="orderStep === 2">
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
              <p class="font-bold text-blue-800 text-sm mb-2">💳 {{ $t('market.paymentInfo') }}</p>
              <div v-if="tariffPrices" class="space-y-1">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-blue-600">{{ $t('market.cardNumber') }}:</span>
                  <span class="font-mono font-bold text-blue-900 text-lg">{{ tariffPrices.card_number || '—' }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-blue-600">{{ $t('market.cardHolder') }}:</span>
                  <span class="font-semibold text-blue-900">{{ tariffPrices.card_holder || '—' }}</span>
                </div>
              </div>
              <div class="mt-2 pt-2 border-t border-blue-200 flex items-center justify-between">
                <span class="text-sm text-blue-600">{{ $t('market.paymentAmount') }}:</span>
                <span class="font-bold text-lg text-blue-900">{{ formatPrice(selectedListing?.price) }}</span>
              </div>
            </div>

            <div class="mb-4">
              <label class="text-sm font-medium text-slate-700 mb-2 block">📎 {{ $t('market.uploadReceipt') }}</label>
              <div class="border-2 border-dashed rounded-xl p-4 text-center transition-colors"
                :class="orderReceiptFile ? 'border-emerald-400 bg-emerald-50' : 'border-slate-300 hover:border-emerald-400'">
                <input type="file" accept="image/*,.pdf" class="hidden" ref="orderReceiptInput" @change="handleOrderReceipt" />
                <div v-if="!orderReceiptFile" @click="$refs.orderReceiptInput?.click()" class="cursor-pointer">
                  <Upload class="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p class="text-sm text-slate-500">{{ $t('market.selectReceiptImage') }}</p>
                  <p class="text-xs text-slate-400 mt-1">JPG, PNG, PDF (max 10MB)</p>
                </div>
                <div v-else class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <CheckCircle2 class="w-5 h-5 text-emerald-500" />
                    <span class="text-sm font-medium text-emerald-700">{{ orderReceiptFile.name }}</span>
                  </div>
                  <button @click="orderReceiptFile = null" class="text-slate-400 hover:text-red-500">
                    <X class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button @click="orderStep = 1" class="flex-1 border border-slate-200 rounded-xl py-2.5 font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                ← {{ $t('market.back') }}
              </button>
              <button @click="submitOrder" :disabled="!orderReceiptFile || orderSubmitting"
                class="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl py-2.5 font-semibold hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                <Loader2 v-if="orderSubmitting" class="w-4 h-4 animate-spin" />
                <template v-else>💳</template>
                {{ orderSubmitting ? $t('market.sending') : $t('market.payAndOrder') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div v-if="selectedOrder" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selectedOrder = null">
      <div class="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span :class="getOrderStatusBadge(selectedOrder.status)" class="px-2.5 py-0.5 text-xs rounded-full font-medium">
                  {{ getOrderStatusLabel(selectedOrder.status) }}
                </span>
                <span class="text-slate-400 text-sm">#{{ selectedOrder.id }}</span>
              </div>
              <h2 class="text-xl font-bold text-slate-800 mt-2">{{ selectedOrder.title }}</h2>
            </div>
            <button @click="selectedOrder = null" class="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Order Info -->
          <div class="grid grid-cols-2 gap-3 mb-4 text-sm">
            <div class="bg-slate-50 rounded-xl p-3"><span class="text-slate-500">{{ $t('market.buyer') }}:</span> <span class="font-medium text-slate-800">{{ selectedOrder.buyer_name }}</span></div>
            <div class="bg-slate-50 rounded-xl p-3"><span class="text-slate-500">{{ $t('market.seller') }}:</span> <span class="font-medium text-slate-800">{{ selectedOrder.seller_name }}</span></div>
            <div class="bg-slate-50 rounded-xl p-3"><span class="text-slate-500">{{ $t('market.amount') }}:</span> <span class="font-bold text-emerald-600">{{ formatPrice(selectedOrder.amount) }}</span></div>
            <div v-if="selectedOrder.deadline" class="bg-slate-50 rounded-xl p-3"><span class="text-slate-500">{{ $t('market.deadline') }}:</span> <span class="font-medium text-slate-800">{{ formatDate(selectedOrder.deadline) }}</span></div>
          </div>

          <!-- Escrow Info -->
          <div v-if="selectedOrder.escrow" class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 mb-4 text-sm">
            <p class="font-medium text-emerald-700">🛡️ {{ $t('market.escrowStatus') }}: {{ selectedOrder.escrow.status }}</p>
            <p class="text-emerald-600">{{ $t('market.heldAmount') }}: {{ formatPrice(selectedOrder.escrow.amount) }}</p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-wrap gap-2 mb-4">
            <button v-if="selectedOrder.status === 'pending' && selectedOrder.seller_id === authStore.user?.id"
              @click="acceptOrder(selectedOrder.id)" class="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-emerald-700 shadow-sm transition-all">
              ✅ {{ $t('market.acceptOrder') }}
            </button>
            <button v-if="['in_progress', 'revision'].includes(selectedOrder.status) && selectedOrder.seller_id === authStore.user?.id"
              @click="showDeliverModal = true" class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-blue-600 hover:to-blue-700 shadow-sm transition-all">
              📦 {{ $t('market.deliverWork') }}
            </button>
            <button v-if="selectedOrder.status === 'delivered' && selectedOrder.buyer_id === authStore.user?.id"
              @click="showAcceptDeliveryModal = true" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-teal-600 shadow-sm transition-all">
              ✅ {{ $t('market.acceptDelivery') }}
            </button>
            <button v-if="selectedOrder.status === 'delivered' && selectedOrder.buyer_id === authStore.user?.id"
              @click="showRevisionModal = true" class="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-amber-600 hover:to-amber-700 shadow-sm transition-all">
              🔄 {{ $t('market.requestRevision') }}
            </button>
            <button v-if="['in_progress', 'delivered', 'revision'].includes(selectedOrder.status)"
              @click="showDisputeModal = true" class="bg-gradient-to-r from-rose-500 to-rose-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-rose-600 hover:to-rose-700 shadow-sm transition-all">
              ⚠️ {{ $t('market.openDispute') }}
            </button>
            <button v-if="selectedOrder.status === 'pending'"
              @click="cancelOrder(selectedOrder.id)" class="border border-rose-200 text-rose-600 px-4 py-2 rounded-xl text-sm font-medium hover:bg-rose-50 transition-colors">
              {{ $t('common.cancel') }}
            </button>
            <button @click="openChat(selectedOrder.id)"
              class="bg-gradient-to-r from-teal-500 to-cyan-500 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-teal-600 hover:to-cyan-600 shadow-sm transition-all flex items-center gap-1">
              <MessageSquare class="w-4 h-4" /> {{ $t('market.chat') }}
            </button>
          </div>

          <!-- Chat Section -->
          <div v-if="showChat" class="border border-slate-200 rounded-2xl overflow-hidden">
            <div class="bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-3 flex items-center justify-between">
              <span class="font-medium text-sm text-white">💬 {{ $t('market.chat') }}</span>
              <button @click="closeChat" class="text-white/80 hover:text-white"><X class="w-4 h-4" /></button>
            </div>
            <div ref="chatContainer" class="h-64 overflow-y-auto p-3 space-y-2 bg-slate-50">
              <div v-for="msg in chatMessages" :key="msg.id"
                :class="msg.is_system ? 'text-center' : (msg.sender_id === authStore.user?.id ? 'text-right' : 'text-left')">
                <div v-if="msg.is_system" class="text-xs text-slate-400 italic">{{ msg.content }}</div>
                <div v-else class="inline-block max-w-[80%] px-3 py-2 rounded-2xl text-sm"
                  :class="msg.sender_id === authStore.user?.id ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white' : 'bg-white border border-slate-200 text-slate-800'">
                  <p class="text-xs opacity-70 mb-0.5">{{ msg.sender_name }}</p>
                  <p>{{ msg.content }}</p>
                  <p v-if="msg.file_url" class="text-xs underline mt-1">📎 {{ msg.file_name }}</p>
                </div>
              </div>
            </div>
            <div class="border-t border-slate-200 p-2 flex gap-2 bg-white">
              <input v-model="chatInput" @keyup.enter="sendMessage" :placeholder="$t('market.typeMessage')"
                class="flex-1 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
              <button @click="sendMessage" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 rounded-xl text-sm hover:from-emerald-600 hover:to-teal-600 transition-all">
                <Send class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 🎯 Tariff Upgrade Modal — Premium Design -->
    <div v-if="showTariffModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="showTariffModal = false">
      <div class="bg-white rounded-3xl max-w-4xl w-full shadow-2xl overflow-hidden max-h-[95vh] overflow-y-auto">
        <!-- Modal Header -->
        <div class="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 p-6 text-white text-center relative overflow-hidden">
          <div class="absolute -top-10 -left-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
          <div class="absolute -bottom-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
          <div class="relative">
            <div class="flex justify-center mb-3">
              <div class="w-16 h-16 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center ring-2 ring-white/30">
                <Sparkles class="w-8 h-8 text-yellow-300" />
              </div>
            </div>
            <h2 class="text-2xl font-bold">{{ $t('market.chooseTariff') }}</h2>
            <p class="text-sm text-white/70 mt-1 max-w-md mx-auto">{{ $t('market.chooseTariffDesc') }}</p>
          </div>
        </div>

        <!-- Pending payment notice -->
        <div v-if="myTariffPayments.some(p => p.status === 'pending')" class="mx-6 mt-4 bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3">
          <Clock class="w-5 h-5 text-amber-500 flex-shrink-0" />
          <div>
            <p class="font-medium text-amber-700">{{ $t('market.receiptUnderReview') }}</p>
            <p class="text-sm text-amber-600">{{ $t('market.waitForAdminApproval') }}</p>
          </div>
        </div>

        <!-- Step 1: Choose Tariff -->
        <div v-if="!selectedTariff" class="p-6">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">

            <!-- FREE Plan -->
            <div class="relative rounded-2xl border-2 transition-all group"
              :class="profile?.tariff === 'free' ? 'border-slate-300 bg-slate-50' : 'border-slate-200 bg-white hover:border-slate-300'">
              <div class="p-5">
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-10 h-10 bg-slate-200 rounded-xl flex items-center justify-center">
                    <Lock class="w-5 h-5 text-slate-500" />
                  </div>
                  <div>
                    <h3 class="font-bold text-lg text-slate-700">Free</h3>
                    <p class="text-xs text-slate-400">{{ $t('market.starterPlan') }}</p>
                  </div>
                </div>
                <div class="mb-5">
                  <span class="text-3xl font-bold text-slate-800">0</span>
                  <span class="text-sm text-slate-400 ml-1">UZS</span>
                </div>
                <ul class="space-y-2.5 mb-5">
                  <li class="flex items-center gap-2.5 text-sm">
                    <CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    <span class="text-slate-600">{{ $t('market.canBrowse') }}</span>
                  </li>
                  <li class="flex items-center gap-2.5 text-sm">
                    <CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    <span class="text-slate-600">{{ $t('market.canBuyServices') }}</span>
                  </li>
                  <li class="flex items-center gap-2.5 text-sm text-slate-400">
                    <XCircle class="w-4 h-4 flex-shrink-0" />
                    <span>{{ $t('market.cannotPost') }}</span>
                  </li>
                  <li class="flex items-center gap-2.5 text-sm text-slate-400">
                    <XCircle class="w-4 h-4 flex-shrink-0" />
                    <span>{{ $t('market.noChat') }}</span>
                  </li>
                  <li class="flex items-center gap-2.5 text-sm text-slate-400">
                    <XCircle class="w-4 h-4 flex-shrink-0" />
                    <span>{{ $t('market.noEscrow') }}</span>
                  </li>
                </ul>
                <button disabled class="w-full py-2.5 bg-slate-100 rounded-xl text-sm text-slate-400 font-medium cursor-not-allowed">
                  {{ profile?.tariff === 'free' ? $t('market.currentPlan') : '—' }}
                </button>
              </div>
            </div>

            <!-- STUDENT PRO Plan -->
            <div class="relative rounded-2xl border-2 transition-all transform sm:scale-105 sm:-translate-y-2"
              :class="profile?.tariff === 'student_pro' ? 'border-emerald-400 bg-emerald-50/50 shadow-xl shadow-emerald-500/15' : 'border-emerald-500 bg-white shadow-xl shadow-emerald-500/15 hover:shadow-2xl'">
              <div class="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                <span class="bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-xs px-5 py-1.5 rounded-full font-bold shadow-lg shadow-emerald-500/30 flex items-center gap-1">
                  <Star class="w-3 h-3 fill-yellow-300 text-yellow-300" /> {{ $t('market.mostPopular') }}
                </span>
              </div>
              <div class="p-5 pt-6">
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                    <Zap class="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 class="font-bold text-lg text-emerald-700">Student Pro</h3>
                    <p class="text-xs text-emerald-500">{{ $t('market.bestValue') }}</p>
                  </div>
                </div>
                <div class="mb-5">
                  <span class="text-3xl font-bold text-slate-800">29,000</span>
                  <span class="text-sm text-slate-400 ml-1">UZS / {{ $t('market.month') }}</span>
                </div>
                <ul class="space-y-2.5 mb-5">
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-700 font-medium">{{ $t('market.canPost') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-700 font-medium">{{ $t('market.chatEnabled') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-700 font-medium">{{ $t('market.escrowEnabled') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-600">{{ $t('market.proLimit') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-600">10% {{ $t('market.commissionRate') }}</span></li>
                </ul>
                <button @click="selectedTariff = 'student_pro'"
                  :disabled="profile?.tariff === 'student_pro' || myTariffPayments.some(p => p.status === 'pending')"
                  class="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50 disabled:shadow-none hover:from-emerald-600 hover:to-teal-600 hover:shadow-xl active:scale-[0.98]">
                  {{ profile?.tariff === 'student_pro' ? '✅ ' + $t('market.currentPlan') : '⚡ ' + $t('market.getStarted') }}
                </button>
              </div>
            </div>

            <!-- PREMIUM Plan -->
            <div class="relative rounded-2xl border-2 transition-all"
              :class="profile?.tariff === 'premium' ? 'border-amber-400 bg-amber-50/50 shadow-xl' : 'border-amber-200 bg-gradient-to-b from-amber-50/50 to-white hover:border-amber-300 hover:shadow-lg'">
              <div class="p-5">
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg shadow-amber-500/30">
                    <Gem class="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 class="font-bold text-lg text-amber-700">Premium</h3>
                    <p class="text-xs text-amber-500">{{ $t('market.maxPower') }}</p>
                  </div>
                </div>
                <div class="mb-5">
                  <span class="text-3xl font-bold text-slate-800">79,000</span>
                  <span class="text-sm text-slate-400 ml-1">UZS / {{ $t('market.month') }}</span>
                </div>
                <ul class="space-y-2.5 mb-5">
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-700 font-medium">{{ $t('market.allProFeatures') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-600">{{ $t('market.premiumLimit') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-600">7% {{ $t('market.commissionRate') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-600">{{ $t('market.fastPayout') }}</span></li>
                  <li class="flex items-center gap-2.5 text-sm"><CheckCircle2 class="w-4 h-4 text-emerald-500 flex-shrink-0" /><span class="text-slate-600">{{ $t('market.premiumBadge') }}</span></li>
                </ul>
                <button @click="selectedTariff = 'premium'"
                  :disabled="profile?.tariff === 'premium' || myTariffPayments.some(p => p.status === 'pending')"
                  class="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-amber-500/25 transition-all disabled:opacity-50 disabled:shadow-none hover:from-amber-600 hover:to-orange-600 hover:shadow-xl active:scale-[0.98]">
                  {{ profile?.tariff === 'premium' ? '👑 ' + $t('market.currentPlan') : '💎 ' + $t('market.goPremium') }}
                </button>
              </div>
            </div>

          </div>

          <button @click="showTariffModal = false" class="w-full mt-6 text-center text-sm text-slate-400 hover:text-slate-600 transition-colors py-2">
            {{ $t('common.close') }}
          </button>
        </div>

        <!-- Step 2: Payment -->
        <div v-else class="p-6 space-y-5">
          <button @click="selectedTariff = null; tariffReceiptFile = null" class="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 transition-colors">
            ← {{ $t('market.chooseTariff') }}
          </button>

          <div class="text-center">
            <h3 class="text-xl font-bold text-slate-800">
              {{ selectedTariff === 'student_pro' ? 'Student Pro' : 'Premium' }} — {{ $t('market.payment') }}
            </h3>
            <p class="text-slate-500 text-sm mt-1">{{ $t('market.payToCardAndUpload') }}</p>
          </div>

          <!-- Card Info -->
          <div v-if="tariffPrices?.card_number" class="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-5 text-white">
            <p class="text-slate-400 text-xs mb-2">{{ $t('market.cardNumber') }}</p>
            <p class="text-2xl font-mono tracking-wider mb-3">{{ tariffPrices.card_number }}</p>
            <p class="text-slate-400 text-xs">{{ $t('market.cardHolder') }}</p>
            <p class="font-medium">{{ tariffPrices.card_holder }}</p>
            <div class="mt-3 pt-3 border-t border-slate-700 flex justify-between items-center">
              <span class="text-sm text-slate-400">{{ $t('market.paymentAmount') }}</span>
              <span class="text-xl font-bold text-amber-400">
                {{ selectedTariff === 'student_pro' ? '29,000' : '79,000' }} UZS
              </span>
            </div>
          </div>
          <div v-else class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center text-amber-700 text-sm">
            {{ $t('market.noCardInfoYet') }}
          </div>

          <!-- Upload Receipt -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('market.paymentReceipt') }}</label>
            <div class="border-2 border-dashed rounded-xl p-6 text-center transition-colors"
              :class="tariffReceiptFile ? 'border-emerald-300 bg-emerald-50' : 'border-slate-300 hover:border-emerald-400'">
              <input ref="tariffFileInput" type="file" accept="image/*,.pdf" class="hidden" @change="handleTariffReceipt" />
              <div v-if="tariffReceiptFile" class="flex items-center justify-center gap-3">
                <CheckCircle2 class="w-8 h-8 text-emerald-500" />
                <div class="text-left">
                  <p class="font-medium text-emerald-700">{{ tariffReceiptFile.name }}</p>
                  <p class="text-sm text-emerald-500">{{ (tariffReceiptFile.size / 1024).toFixed(1) }} KB</p>
                </div>
                <button @click="tariffReceiptFile = null" class="ml-4 p-2 hover:bg-red-100 rounded-lg transition-colors">
                  <X class="w-5 h-5 text-red-500" />
                </button>
              </div>
              <div v-else @click="$refs.tariffFileInput.click()" class="cursor-pointer">
                <Upload class="w-10 h-10 text-slate-400 mx-auto mb-2" />
                <p class="text-slate-600 font-medium">{{ $t('market.uploadReceiptImage') }}</p>
                <p class="text-slate-400 text-sm mt-1">JPG, PNG {{ $t('market.or') }} PDF (max 10 MB)</p>
              </div>
            </div>
          </div>

          <!-- Submit -->
          <button
            @click="upgradeTariff(selectedTariff)"
            :disabled="!tariffReceiptFile || tariffUpgrading || !tariffPrices?.card_number"
            class="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Loader2 v-if="tariffUpgrading" class="w-5 h-5 animate-spin" />
            <Send v-else class="w-5 h-5" />
            {{ tariffUpgrading ? $t('market.sending') : $t('market.submitReceipt') }}
          </button>

          <!-- Payment History -->
          <div v-if="myTariffPayments.length > 0" class="border-t border-slate-100 pt-4">
            <h4 class="text-sm font-semibold text-slate-700 mb-3">{{ $t('market.paymentHistory') }}</h4>
            <div class="space-y-2">
              <div v-for="p in myTariffPayments" :key="p.id" class="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                <div class="flex items-center gap-3">
                  <div :class="['w-8 h-8 rounded-lg flex items-center justify-center', p.status === 'approved' ? 'bg-emerald-100' : p.status === 'rejected' ? 'bg-rose-100' : 'bg-amber-100']">
                    <CheckCircle2 v-if="p.status === 'approved'" class="w-4 h-4 text-emerald-600" />
                    <XCircle v-else-if="p.status === 'rejected'" class="w-4 h-4 text-rose-600" />
                    <Clock v-else class="w-4 h-4 text-amber-600" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-slate-800">{{ p.tariff === 'student_pro' ? 'Student Pro' : 'Premium' }}</p>
                    <p class="text-xs text-slate-400">{{ formatDate(p.created_at) }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-semibold text-slate-800">{{ Number(p.amount).toLocaleString() }} UZS</p>
                  <p :class="['text-xs font-medium', p.status === 'approved' ? 'text-emerald-600' : p.status === 'rejected' ? 'text-rose-600' : 'text-amber-600']">
                    {{ p.status === 'approved' ? $t('market.approved') : p.status === 'rejected' ? $t('market.rejected') : $t('market.pending') }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Deliver Modal -->
    <div v-if="showDeliverModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showDeliverModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl">
        <h2 class="text-xl font-bold text-slate-800 mb-4">📦 {{ $t('market.deliverWork') }}</h2>
        <textarea v-model="deliverForm.note" rows="3" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mb-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" :placeholder="$t('market.deliveryNote')"></textarea>
        <div class="flex gap-3">
          <button @click="showDeliverModal = false" class="flex-1 border border-slate-200 rounded-xl py-2.5 text-slate-600 font-medium hover:bg-slate-50 transition-colors">{{ $t('common.cancel') }}</button>
          <button @click="deliverOrder" class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl py-2.5 font-semibold hover:from-blue-600 hover:to-blue-700 shadow-lg shadow-blue-500/25 transition-all">{{ $t('market.submit') }}</button>
        </div>
      </div>
    </div>

    <!-- Accept Delivery Modal -->
    <div v-if="showAcceptDeliveryModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showAcceptDeliveryModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl">
        <h2 class="text-xl font-bold text-slate-800 mb-4">✅ {{ $t('market.acceptDelivery') }}</h2>
        <div class="mb-3">
          <label class="text-sm font-medium text-slate-700">{{ $t('market.rating') }}</label>
          <div class="flex gap-1 mt-1">
            <button v-for="i in 5" :key="i" @click="acceptForm.rating = i"
              :class="i <= acceptForm.rating ? 'text-amber-400' : 'text-slate-200'"
              class="text-2xl transition-colors hover:scale-110">★</button>
          </div>
        </div>
        <textarea v-model="acceptForm.review" rows="2" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mb-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" :placeholder="$t('market.reviewPlaceholder')"></textarea>
        <div class="flex gap-3">
          <button @click="showAcceptDeliveryModal = false" class="flex-1 border border-slate-200 rounded-xl py-2.5 text-slate-600 font-medium hover:bg-slate-50 transition-colors">{{ $t('common.cancel') }}</button>
          <button @click="acceptDelivery" class="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl py-2.5 font-semibold hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/25 transition-all">{{ $t('market.confirmAccept') }}</button>
        </div>
      </div>
    </div>

    <!-- Revision Modal -->
    <div v-if="showRevisionModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showRevisionModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl">
        <h2 class="text-xl font-bold text-slate-800 mb-4">🔄 {{ $t('market.requestRevision') }}</h2>
        <textarea v-model="revisionReason" rows="3" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mb-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" :placeholder="$t('market.revisionReason')"></textarea>
        <div class="flex gap-3">
          <button @click="showRevisionModal = false" class="flex-1 border border-slate-200 rounded-xl py-2.5 text-slate-600 font-medium hover:bg-slate-50 transition-colors">{{ $t('common.cancel') }}</button>
          <button @click="requestRevision" class="flex-1 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl py-2.5 font-semibold hover:from-amber-600 hover:to-amber-700 shadow-lg shadow-amber-500/25 transition-all">{{ $t('market.submit') }}</button>
        </div>
      </div>
    </div>

    <!-- Dispute Modal -->
    <div v-if="showDisputeModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showDisputeModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl">
        <h2 class="text-xl font-bold text-slate-800 mb-4">⚠️ {{ $t('market.openDispute') }}</h2>
        <div class="bg-rose-50 border border-rose-100 text-rose-700 text-sm p-4 rounded-xl mb-3">
          {{ $t('market.disputeWarning') }}
        </div>
        <textarea v-model="disputeReason" rows="3" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 mb-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" :placeholder="$t('market.disputeReason')"></textarea>
        <div class="flex gap-3">
          <button @click="showDisputeModal = false" class="flex-1 border border-slate-200 rounded-xl py-2.5 text-slate-600 font-medium hover:bg-slate-50 transition-colors">{{ $t('common.cancel') }}</button>
          <button @click="openDispute" class="flex-1 bg-gradient-to-r from-rose-500 to-rose-600 text-white rounded-xl py-2.5 font-semibold hover:from-rose-600 hover:to-rose-700 shadow-lg shadow-rose-500/25 transition-all">{{ $t('market.submitDispute') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
    ArrowDownToLine,
    Banknote,
    BookOpen,
    CheckCircle2,
    ClipboardList,
    Clock,
    CreditCard,
    Crown,
    Eye,
    Gem,
    Loader2,
    Lock,
    MessageSquare,
    Package,
    Pencil,
    Percent,
    Plus,
    RefreshCcw,
    Rocket,
    Search,
    Send,
    ShoppingBag,
    Sparkles,
    Star,
    Store,
    Timer,
    Trash2,
    TrendingUp,
    Upload,
    User,
    Wallet,
    X,
    XCircle,
    Zap
} from 'lucide-vue-next'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useLanguageStore } from '../../stores/language'

const authStore = useAuthStore()
const { t } = useLanguageStore()

// State
const activeTab = ref('browse')
const loading = ref(false)
const profile = ref(null)
const listings = ref([])
const myListings = ref([])
const orders = ref([])
const totalListings = ref(0)
const currentPage = ref(1)
const pageSize = 20
const searchQuery = ref('')
const selectedCategory = ref('')
const orderFilter = ref('all')
const selectedListing = ref(null)
const selectedOrder = ref(null)
const showCreateModal = ref(false)
const showOrderModal = ref(false)
const showTariffModal = ref(false)
const showDeliverModal = ref(false)
const showAcceptDeliveryModal = ref(false)
const showRevisionModal = ref(false)
const showDisputeModal = ref(false)
const showChat = ref(false)
const chatMessages = ref([])
const chatInput = ref('')
const chatContainer = ref(null)
const editingListing = ref(null)
const payoutAmount = ref(null)
const payoutCard = ref('')
const tariffPrices = ref(null)
const tariffReceiptFile = ref(null)
const tariffUpgrading = ref(false)
const selectedTariff = ref(null)
const myTariffPayments = ref([])
const revisionReason = ref('')
const disputeReason = ref('')
let ws = null
let debounceTimer = null
let chatPollingInterval = null
let wsReconnectTimer = null
let wsPingInterval = null
let wsReconnectAttempts = 0
const chatOrderId = ref(null)

const listingForm = ref({
  title: '', description: '', category: 'programming',
  price: null, delivery_days: 3, max_revisions: 2, subject: ''
})

const orderForm = ref({ requirements: '', deadline_days: null })
const orderStep = ref(1)
const orderReceiptFile = ref(null)
const orderSubmitting = ref(false)
const deliverForm = ref({ note: '' })
const acceptForm = ref({ rating: 5, review: '' })

const categories = computed(() => [
  { value: 'programming', label: t('market.catProgramming') },
  { value: 'design', label: t('market.catDesign') },
  { value: 'writing', label: t('market.catWriting') },
  { value: 'translation', label: t('market.catTranslation') },
  { value: 'math', label: t('market.catMath') },
  { value: 'science', label: t('market.catScience') },
  { value: 'tutoring', label: t('market.catTutoring') },
  { value: 'coursework', label: t('market.catCoursework') },
  { value: 'presentation', label: t('market.catPresentation') },
  { value: 'research', label: t('market.catResearch') },
  { value: 'other', label: t('market.catOther') },
])

const mainTabs = computed(() => [
  { value: 'browse', label: t('market.browse'), icon: ShoppingBag, badge: null },
  { value: 'my-listings', label: t('market.myListings'), icon: Package, badge: myListings.value.length || null },
  { value: 'my-orders', label: t('market.myOrders'), icon: ClipboardList, badge: orders.value.length || null },
  { value: 'wallet', label: t('market.wallet'), icon: Wallet, badge: null },
])

const orderTabs = computed(() => [
  { value: 'all', label: t('market.allOrders') },
  { value: 'buyer', label: t('market.asBuyer') },
  { value: 'seller', label: t('market.asSeller') },
])

const tariffLimits = computed(() => {
  const limits = {
    free: { max_active_orders: 0, max_amount_per_order: 0, commission_rate: 0.15, payout_delay_hours: 72 },
    student_pro: { max_active_orders: 3, max_amount_per_order: 2000000, commission_rate: 0.10, payout_delay_hours: 48 },
    premium: { max_active_orders: 10, max_amount_per_order: 10000000, commission_rate: 0.07, payout_delay_hours: 24 },
  }
  return limits[profile.value?.tariff] || limits.free
})

// Helpers
const formatPrice = (price) => {
  if (!price && price !== 0) return '0 UZS'
  return new Intl.NumberFormat('uz-UZ').format(price) + ' UZS'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatCompact = (num) => {
  if (!num) return '0'
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(0) + 'M'
  if (num >= 1_000) return (num / 1_000).toFixed(0) + 'K'
  return num.toString()
}

const getCategoryLabel = (cat) => {
  const found = categories.value.find(c => c.value === cat)
  return found ? found.label : cat
}

const getCategoryColor = (cat) => {
  const colors = {
    programming: 'bg-blue-100 text-blue-700',
    design: 'bg-pink-100 text-pink-700',
    writing: 'bg-emerald-100 text-emerald-700',
    translation: 'bg-violet-100 text-violet-700',
    math: 'bg-amber-100 text-amber-700',
    science: 'bg-teal-100 text-teal-700',
    tutoring: 'bg-orange-100 text-orange-700',
    coursework: 'bg-indigo-100 text-indigo-700',
    presentation: 'bg-rose-100 text-rose-700',
    research: 'bg-cyan-100 text-cyan-700',
    other: 'bg-slate-100 text-slate-700',
  }
  return colors[cat] || 'bg-slate-100 text-slate-700'
}

const getStatusBadge = (status) => ({
  active: 'bg-emerald-100 text-emerald-700',
  pending: 'bg-amber-100 text-amber-700',
  rejected: 'bg-rose-100 text-rose-700',
  paused: 'bg-slate-100 text-slate-700',
  archived: 'bg-slate-100 text-slate-500',
}[status] || 'bg-slate-100 text-slate-700')

const getStatusLabel = (status) => ({
  active: t('market.statusActive'),
  pending: t('market.statusPending'),
  rejected: t('market.statusRejected'),
  paused: t('market.statusPaused'),
  archived: t('market.statusArchived'),
}[status] || status)

const getOrderStatusBadge = (status) => ({
  pending: 'bg-amber-100 text-amber-700',
  accepted: 'bg-blue-100 text-blue-700',
  paid: 'bg-indigo-100 text-indigo-700',
  in_progress: 'bg-blue-100 text-blue-700',
  delivered: 'bg-violet-100 text-violet-700',
  revision: 'bg-orange-100 text-orange-700',
  completed: 'bg-emerald-100 text-emerald-700',
  disputed: 'bg-rose-100 text-rose-700',
  cancelled: 'bg-slate-100 text-slate-500',
  refunded: 'bg-slate-100 text-slate-500',
}[status] || 'bg-slate-100 text-slate-700')

const getOrderStatusLabel = (status) => ({
  pending: t('market.orderPending'),
  accepted: t('market.orderAccepted'),
  paid: t('market.orderPaid'),
  in_progress: t('market.orderInProgress'),
  delivered: t('market.orderDelivered'),
  revision: t('market.orderRevision'),
  completed: t('market.orderCompleted'),
  disputed: t('market.orderDisputed'),
  cancelled: t('market.orderCancelled'),
  refunded: t('market.orderRefunded'),
}[status] || status)

const getTariffBadge = (tariff) => ({
  free: 'bg-slate-100 text-slate-700',
  student_pro: 'bg-emerald-100 text-emerald-700',
  premium: 'bg-amber-100 text-amber-700',
}[tariff] || 'bg-slate-100 text-slate-700')

const getTariffLabel = (tariff) => ({
  free: 'Free',
  student_pro: 'Student Pro',
  premium: 'Premium',
}[tariff] || 'Free')

// API Calls
const buildQuery = (params) => {
  const cleaned = {}
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') cleaned[k] = v
  }
  if (Object.keys(cleaned).length === 0) return ''
  return '?' + new URLSearchParams(cleaned).toString()
}

const loadProfile = async () => {
  try {
    profile.value = await api.request('/market/profile')
  } catch (e) {
    console.error('Profile load error:', e)
  }
}

const loadListings = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCategory.value) params.category = selectedCategory.value
    const res = await api.request('/market/listings' + buildQuery(params))
    listings.value = res.items || []
    totalListings.value = res.total || 0
  } catch (e) {
    console.error('Listings load error:', e)
  } finally {
    loading.value = false
  }
}

const loadMyListings = async () => {
  try {
    // Load each status separately and merge
    const statuses = ['active', 'pending', 'rejected', 'paused', 'draft']
    const all = []
    for (const st of statuses) {
      try {
        const res = await api.request('/market/listings' + buildQuery({ seller_id: authStore.user?.id, status: st, page: 1, page_size: 50 }))
        if (res.items) all.push(...res.items)
      } catch (e) { /* skip */ }
    }
    myListings.value = all
  } catch (e) {
    console.error('My listings error:', e)
  }
}

const loadOrders = async () => {
  try {
    const params = { role: orderFilter.value, page: 1, page_size: 50 }
    const res = await api.request('/market/orders' + buildQuery(params))
    orders.value = res.items || []
  } catch (e) {
    console.error('Orders error:', e)
  }
}

const openListing = async (listing) => {
  try {
    selectedListing.value = await api.request(`/market/listings/${listing.id}`)
  } catch (e) {
    selectedListing.value = listing
  }
}

const openOrder = async (order) => {
  try {
    selectedOrder.value = await api.request(`/market/orders/${order.id}`)
    showChat.value = false
  } catch (e) {
    selectedOrder.value = order
  }
}

const submitListing = async () => {
  // Validate required fields
  if (!listingForm.value.title || listingForm.value.title.trim().length < 5) {
    alert(t('market.titleMinLength') || 'Sarlavha kamida 5 ta belgidan iborat bo\'lishi kerak')
    return
  }
  if (!listingForm.value.description || listingForm.value.description.trim().length < 20) {
    alert(t('market.descMinLength') || 'Tavsif kamida 20 ta belgidan iborat bo\'lishi kerak')
    return
  }
  if (!listingForm.value.price || listingForm.value.price <= 0) {
    alert(t('market.priceRequired') || 'Narxni kiriting (0 dan katta)')
    return
  }

  // Clean data: remove empty optional fields
  const data = { ...listingForm.value }
  if (!data.subject || data.subject.trim() === '') delete data.subject
  if (!data.direction || data.direction.trim() === '') delete data.direction
  data.title = data.title.trim()
  data.description = data.description.trim()
  data.price = Number(data.price)
  data.delivery_days = Number(data.delivery_days) || 3
  data.max_revisions = Number(data.max_revisions) ?? 2

  try {
    if (editingListing.value) {
      await api.request(`/market/listings/${editingListing.value.id}`, { method: 'PUT', body: data })
    } else {
      await api.request('/market/listings', { method: 'POST', body: data })
    }
    showCreateModal.value = false
    editingListing.value = null
    listingForm.value = { title: '', description: '', category: 'programming', price: null, delivery_days: 3, max_revisions: 2, subject: '' }
    loadMyListings()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const editListing = (listing) => {
  editingListing.value = listing
  listingForm.value = {
    title: listing.title,
    description: listing.description,
    category: listing.category,
    price: listing.price,
    delivery_days: listing.delivery_days,
    max_revisions: listing.max_revisions,
    subject: listing.subject || ''
  }
  showCreateModal.value = true
}

const deleteListing = async (listing) => {
  if (!confirm(t('market.confirmDelete'))) return
  try {
    await api.request(`/market/listings/${listing.id}`, { method: 'DELETE' })
    loadMyListings()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const handleOrderReceipt = (e) => {
  const file = e.target.files[0]
  if (file) {
    if (file.size > 10 * 1024 * 1024) {
      alert('Fayl hajmi 10MB dan oshmasligi kerak')
      return
    }
    orderReceiptFile.value = file
  }
}

const submitOrder = async () => {
  if (!orderReceiptFile.value) {
    alert('To\'lov chekini yuklang')
    return
  }
  orderSubmitting.value = true
  try {
    const formData = new FormData()
    formData.append('listing_id', selectedListing.value.id)
    if (orderForm.value.requirements) formData.append('requirements', orderForm.value.requirements)
    if (orderForm.value.deadline_days) formData.append('deadline_days', orderForm.value.deadline_days)
    formData.append('receipt', orderReceiptFile.value)

    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/v1/market/orders', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })
    const result = await response.json()
    if (!response.ok) throw { data: result }

    showOrderModal.value = false
    selectedListing.value = null
    orderForm.value = { requirements: '', deadline_days: null }
    orderStep.value = 1
    orderReceiptFile.value = null
    loadOrders()
    activeTab.value = 'my-orders'
  } catch (e) {
    alert(e.data?.detail || e.data?.error || t('common.error'))
  } finally {
    orderSubmitting.value = false
  }
}

const acceptOrder = async (orderId) => {
  try {
    await api.request(`/market/orders/${orderId}/accept`, { method: 'POST' })
    await openOrder(selectedOrder.value)
    loadOrders()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const deliverOrder = async () => {
  try {
    await api.request(`/market/orders/${selectedOrder.value.id}/deliver`, {
      method: 'POST',
      body: { delivery_note: deliverForm.value.note }
    })
    showDeliverModal.value = false
    deliverForm.value = { note: '' }
    await openOrder(selectedOrder.value)
    loadOrders()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const acceptDelivery = async () => {
  try {
    await api.request(`/market/orders/${selectedOrder.value.id}/accept-delivery`, {
      method: 'POST',
      body: acceptForm.value
    })
    showAcceptDeliveryModal.value = false
    acceptForm.value = { rating: 5, review: '' }
    await openOrder(selectedOrder.value)
    loadOrders()
    loadProfile()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const requestRevision = async () => {
  try {
    await api.request(`/market/orders/${selectedOrder.value.id}/revision`, {
      method: 'POST',
      body: { reason: revisionReason.value }
    })
    showRevisionModal.value = false
    revisionReason.value = ''
    await openOrder(selectedOrder.value)
    loadOrders()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const cancelOrder = async (orderId) => {
  if (!confirm(t('market.confirmCancel'))) return
  try {
    await api.request(`/market/orders/${orderId}/cancel`, { method: 'POST' })
    await openOrder(selectedOrder.value)
    loadOrders()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const openDispute = async () => {
  try {
    await api.request(`/market/orders/${selectedOrder.value.id}/dispute`, {
      method: 'POST',
      body: { reason: disputeReason.value }
    })
    showDisputeModal.value = false
    disputeReason.value = ''
    await openOrder(selectedOrder.value)
    loadOrders()
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

const upgradeTariff = async (tariff) => {
  if (!tariffReceiptFile.value) {
    alert(t('market.uploadReceipt') || 'To\'lov chekini yuklang')
    return
  }
  tariffUpgrading.value = true
  try {
    const formData = new FormData()
    formData.append('tariff', tariff)
    formData.append('receipt', tariffReceiptFile.value)

    const token = localStorage.getItem('access_token') || ''
    const response = await fetch(`/api/v1/market/profile/upgrade`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data?.detail || t('common.error'))
    }

    showTariffModal.value = false
    tariffReceiptFile.value = null
    selectedTariff.value = null
    alert(data.message || t('market.receiptSentWaitApproval'))
    await loadTariffPayments()
  } catch (e) {
    alert(e.message || t('common.error'))
  } finally {
    tariffUpgrading.value = false
  }
}

const handleTariffReceipt = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    if (file.size > 10 * 1024 * 1024) {
      alert('Fayl 10 MB dan katta bo\'lmasligi kerak')
      return
    }
    tariffReceiptFile.value = file
  }
}

const loadTariffPrices = async () => {
  try {
    tariffPrices.value = await api.request('/market/tariff-prices')
  } catch (e) {
    console.error('Tariff prices load error:', e)
  }
}

const loadTariffPayments = async () => {
  try {
    const resp = await api.request('/market/tariff-payments')
    myTariffPayments.value = resp?.items || []
  } catch (e) {
    console.error('Tariff payments load error:', e)
  }
}

const requestPayout = async () => {
  try {
    await api.request('/market/payouts', {
      method: 'POST',
      body: {
        amount: payoutAmount.value,
        card_number: payoutCard.value || undefined
      }
    })
    payoutAmount.value = null
    payoutCard.value = ''
    await loadProfile()
    alert(t('market.payoutRequested'))
  } catch (e) {
    alert(e.data?.detail || t('common.error'))
  }
}

// Chat
const openChat = async (orderId) => {
  showChat.value = true
  chatOrderId.value = orderId
  try {
    const res = await api.request(`/market/orders/${orderId}/messages`)
    chatMessages.value = res.items || []
    await nextTick()
    scrollChat()
  } catch (e) {
    console.error('Chat load error:', e)
  }
  // Start polling for new messages (primary real-time mechanism)
  startChatPolling(orderId)
  // Also try WebSocket for instant delivery
  connectWS(orderId)
}

const closeChat = () => {
  showChat.value = false
  chatOrderId.value = null
  stopChatPolling()
  disconnectWS()
}

const startChatPolling = (orderId) => {
  stopChatPolling()
  chatPollingInterval = setInterval(async () => {
    if (!showChat.value || !orderId) return
    try {
      const res = await api.request(`/market/orders/${orderId}/messages`)
      const newMessages = res.items || []
      // Merge: add any messages not yet in our list
      let added = false
      for (const msg of newMessages) {
        const exists = chatMessages.value.some(m => 
          m.id === msg.id || 
          (String(m.id).startsWith('temp_') && m.sender_id === msg.sender_id && m.content === msg.content)
        )
        if (!exists) {
          chatMessages.value.push(msg)
          added = true
        } else {
          // Replace temp message with real server message
          const tempIdx = chatMessages.value.findIndex(m => 
            String(m.id).startsWith('temp_') && m.sender_id === msg.sender_id && m.content === msg.content
          )
          if (tempIdx !== -1) {
            chatMessages.value[tempIdx] = msg
          }
        }
      }
      if (added) {
        await nextTick()
        scrollChat()
      }
    } catch (e) {
      console.error('Chat poll error:', e)
    }
  }, 3000) // Poll every 3 seconds
}

const stopChatPolling = () => {
  if (chatPollingInterval) {
    clearInterval(chatPollingInterval)
    chatPollingInterval = null
  }
}

const connectWS = (orderId) => {
  disconnectWS()
  wsReconnectAttempts = 0
  doConnectWS(orderId)
}

const doConnectWS = (orderId) => {
  const token = localStorage.getItem('access_token')
  if (!token || !showChat.value) return
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.hostname
  const port = window.location.port ? `:${window.location.port}` : ''
  
  try {
    ws = new WebSocket(`${protocol}://${host}${port}/api/v1/market/ws/${orderId}?token=${token}`)
  } catch (e) {
    console.error('WS create error:', e)
    return
  }

  ws.onopen = () => {
    console.log('WS connected for order', orderId)
    wsReconnectAttempts = 0
    // Start ping to keep connection alive through nginx
    if (wsPingInterval) clearInterval(wsPingInterval)
    wsPingInterval = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // Ping every 30 seconds
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'new_message') {
        const exists = chatMessages.value.some(m => m.id === data.data.id)
        if (!exists) {
          chatMessages.value.push(data.data)
          nextTick(() => scrollChat())
        }
      } else if (data.type === 'pong') {
        // Keep-alive response, ignore
      }
    } catch (e) {
      console.error('WS message parse error:', e)
    }
  }

  ws.onerror = (e) => {
    console.error('WS error:', e)
  }

  ws.onclose = () => {
    console.log('WS closed')
    ws = null
    // Auto-reconnect if chat is still open
    if (showChat.value && chatOrderId.value) {
      wsReconnectAttempts++
      const delay = Math.min(2000 * wsReconnectAttempts, 15000)
      console.log(`WS reconnecting in ${delay}ms (attempt ${wsReconnectAttempts})`)
      wsReconnectTimer = setTimeout(() => {
        if (showChat.value && chatOrderId.value) {
          doConnectWS(chatOrderId.value)
        }
      }, delay)
    }
  }
}

const disconnectWS = () => {
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer)
    wsReconnectTimer = null
  }
  if (wsPingInterval) {
    clearInterval(wsPingInterval)
    wsPingInterval = null
  }
  if (ws) {
    ws.onclose = null // Prevent reconnect on intentional close
    ws.close()
    ws = null
  }
}

const sendMessage = async () => {
  if (!chatInput.value.trim()) return
  const content = chatInput.value.trim()
  chatInput.value = ''
  const tempId = 'temp_' + Date.now()
  // Add message locally immediately with temp id
  chatMessages.value.push({
    id: tempId,
    order_id: selectedOrder.value?.id,
    sender_id: authStore.user?.id,
    sender_name: authStore.user?.name,
    content: content,
    message_type: 'text',
    is_system: false,
    is_read: false,
    created_at: new Date().toISOString(),
  })
  nextTick(() => scrollChat())
  try {
    const msg = await api.request(`/market/orders/${selectedOrder.value.id}/messages`, {
      method: 'POST',
      body: { content }
    })
    // Replace temp message with real one from server
    const idx = chatMessages.value.findIndex(m => m.id === tempId)
    if (idx !== -1) {
      chatMessages.value[idx] = {
        id: msg.id,
        order_id: msg.order_id,
        sender_id: msg.sender_id || authStore.user?.id,
        sender_name: msg.sender_name || authStore.user?.name,
        content: msg.content || content,
        message_type: msg.message_type || 'text',
        is_system: false,
        is_read: false,
        created_at: msg.created_at || new Date().toISOString(),
      }
    }
  } catch (e) {
    // Remove temp message and restore input on error
    chatMessages.value = chatMessages.value.filter(m => m.id !== tempId)
    chatInput.value = content
    alert(e.data?.detail || t('common.error'))
  }
}

const scrollChat = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const debouncedSearch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadListings()
  }, 400)
}

// Watch tab changes
watch(activeTab, (val) => {
  if (val === 'browse') loadListings()
  if (val === 'my-listings') loadMyListings()
  if (val === 'my-orders') loadOrders()
  if (val === 'wallet') loadProfile()
})

onMounted(() => {
  loadProfile()
  loadListings()
  loadTariffPrices()
  loadTariffPayments()
})

onBeforeUnmount(() => {
  stopChatPolling()
  disconnectWS()
})
</script>
