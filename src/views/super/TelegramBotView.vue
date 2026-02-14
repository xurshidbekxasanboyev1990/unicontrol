<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('telegram.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('telegram.botStatusDesc') }}</p>
      </div>
      <button
        @click="refresh"
        class="p-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
        :class="{ 'animate-spin': loading }"
      >
        <RefreshCw class="w-5 h-5" />
      </button>
    </div>

    <!-- Bot Info Card -->
    <div class="bg-gradient-to-r from-blue-500 to-cyan-600 rounded-2xl p-6 text-white shadow-xl shadow-blue-500/20">
      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div class="flex items-center gap-4 w-full sm:w-auto">
          <div class="w-14 h-14 sm:w-16 sm:h-16 bg-white/20 rounded-2xl flex items-center justify-center shrink-0">
            <Bot class="w-7 h-7 sm:w-8 sm:h-8 text-white" />
          </div>
          <div class="flex-1">
            <h2 class="text-lg sm:text-xl font-bold">@unicontroluzbot</h2>
            <p class="text-blue-100 text-sm mt-1">{{ $t('telegram.botName') }}</p>
            <div class="flex items-center gap-2 mt-2">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                {{ $t('telegram.running') }}
              </span>
            </div>
          </div>
        </div>
        <a 
          href="https://t.me/unicontroluzbot"
          target="_blank"
          class="w-full sm:w-auto text-center px-5 py-2.5 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-colors shrink-0"
        >
          {{ $t('telegram.openBot') }}
        </a>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-violet-100 rounded-xl flex items-center justify-center">
            <MessageSquare class="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('telegram.connectedChats') }}</p>
            <p class="text-xl sm:text-2xl font-bold text-slate-800">{{ registeredChats.length }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <Building2 class="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p class="text-xs sm:text-sm text-slate-500">{{ $t('telegram.subscribedGroups') }}</p>
            <p class="text-xl sm:text-2xl font-bold text-slate-800">{{ activeGroups }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
            <Zap class="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <p class="text-sm text-slate-500">{{ $t('telegram.botTask') }}</p>
            <p class="text-lg font-bold text-slate-800">{{ $t('telegram.attendanceDelivery') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- How it works -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
      <h3 class="text-lg font-semibold text-slate-800 mb-4">{{ $t('telegram.howBotWorks') }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold text-sm flex-shrink-0">1</div>
            <div>
              <p class="font-medium text-slate-800">{{ $t('telegram.addBotToGroup') }}</p>
              <p class="text-sm text-slate-500">{{ $t('telegram.addBotToGroupDesc') }}</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold text-sm flex-shrink-0">2</div>
            <div>
              <p class="font-medium text-slate-800">{{ $t('telegram.linkGroupCode') }}</p>
              <p class="text-sm text-slate-500">{{ $t('telegram.linkGroupCodeDesc') }}</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold text-sm flex-shrink-0">3</div>
            <div>
              <p class="font-medium text-slate-800">{{ $t('telegram.activateSubscription') }}</p>
              <p class="text-sm text-slate-500">{{ $t('telegram.activateSubscriptionDesc') }}</p>
            </div>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center text-emerald-600 font-bold text-sm flex-shrink-0">4</div>
            <div>
              <p class="font-medium text-slate-800">{{ $t('telegram.realTimeAttendance') }}</p>
              <p class="text-sm text-slate-500">{{ $t('telegram.realTimeAttendanceDesc') }}</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center text-emerald-600 font-bold text-sm flex-shrink-0">5</div>
            <div>
              <p class="font-medium text-slate-800">{{ $t('telegram.groupAndPersonal') }}</p>
              <p class="text-sm text-slate-500">{{ $t('telegram.groupAndPersonalDesc') }}</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center text-emerald-600 font-bold text-sm flex-shrink-0">6</div>
            <div>
              <p class="font-medium text-slate-800">{{ $t('telegram.onlyMediator') }}</p>
              <p class="text-sm text-slate-500">{{ $t('telegram.onlyMediatorDesc') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Registered Chats Table -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-6 border-b border-slate-100">
        <h3 class="text-lg font-semibold text-slate-800">{{ $t('telegram.connectedTelegramChats') }}</h3>
        <p class="text-sm text-slate-500 mt-1">{{ $t('telegram.connectedChatsDesc') }}</p>
      </div>

      <div v-if="loading" class="p-8 text-center">
        <RefreshCw class="w-8 h-8 text-violet-500 animate-spin mx-auto mb-2" />
        <p class="text-slate-500">{{ $t('common.loading') }}</p>
      </div>

      <div v-else-if="registeredChats.length === 0" class="p-12 text-center">
        <MessageSquare class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500 font-medium">{{ $t('telegram.noChatConnected') }}</p>
        <p class="text-sm text-slate-400 mt-2">{{ $t('telegram.noChatConnectedDesc') }}</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div 
          v-for="(chat, idx) in registeredChats" 
          :key="idx"
          class="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors"
        >
          <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <MessageSquare class="w-5 h-5 text-blue-600" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-slate-800 truncate">{{ chat.chat_title || $t('telegram.unknownChat') }}</p>
            <p class="text-sm text-slate-500">
              {{ $t('telegram.groupLabel') }}: <span class="font-medium text-violet-600">{{ chat.group_code }}</span> • 
              {{ $t('telegram.typeLabel') }}: {{ chat.chat_type === 'group' || chat.chat_type === 'supergroup' ? $t('telegram.groupType') : $t('telegram.personalType') }}
            </p>
          </div>
          <div class="text-right text-sm text-slate-400">
            <p>Chat ID: {{ chat.chat_id }}</p>
            <p v-if="chat.registered_at">{{ formatDate(chat.registered_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bot commands info -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
      <h3 class="text-lg font-semibold text-slate-800 mb-4">{{ $t('telegram.botCommands') }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <code class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">/start</code>
          <span class="text-sm text-slate-600">{{ $t('telegram.startBot') }}</span>
        </div>
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <code class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">/subscribe KOD</code>
          <span class="text-sm text-slate-600">{{ $t('telegram.subscribeGroup') }}</span>
        </div>
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <code class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">/unsubscribe</code>
          <span class="text-sm text-slate-600">{{ $t('telegram.unsubscribe') }}</span>
        </div>
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <code class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">/attendance</code>
          <span class="text-sm text-slate-600">{{ $t('telegram.viewAttendance') }}</span>
        </div>
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <code class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">/search</code>
          <span class="text-sm text-slate-600">{{ $t('telegram.searchGroup') }}</span>
        </div>
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
          <code class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-mono">/settings</code>
          <span class="text-sm text-slate-600">{{ $t('telegram.messageSettings') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
    Bot,
    Building2,
    MessageSquare,
    RefreshCw,
    Zap
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useToastStore } from '../../stores/toast'

const toast = useToastStore()
const loading = ref(false)
const registeredChats = ref([])

const activeGroups = computed(() => {
  const codes = new Set()
  registeredChats.value.forEach(c => {
    if (c.group_code) codes.add(c.group_code)
  })
  return codes.size
})

async function loadChats() {
  loading.value = true
  try {
    // Fetch registered chats from admin endpoint (no bot token needed)
    const result = await api.request('/telegram/registered-admin')
    const chats = result?.chats || {}
    registeredChats.value = Object.entries(chats).map(([chatId, info]) => ({
      chat_id: chatId,
      ...info
    }))
  } catch (e) {
    console.error('Load chats error:', e)
    registeredChats.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return isoStr
  }
}

async function refresh() {
  await loadChats()
}

onMounted(() => {
  loadChats()
})
</script>
