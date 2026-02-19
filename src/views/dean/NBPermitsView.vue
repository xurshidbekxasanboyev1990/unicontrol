<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">NB Ruxsatnomalar</h1>
        <p class="text-sm text-slate-500">Talabalar NB ruxsatnomalari (faqat ko'rish)</p>
      </div>
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div class="relative">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Talaba qidirish..."
            class="w-full sm:w-64 pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none"
            @input="debouncedSearch"
          />
        </div>
        <select v-model="filterStatus" @change="loadNBPermits" class="px-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none">
          <option value="">Barcha holatlar</option>
          <option value="pending">Kutilmoqda</option>
          <option value="approved">Tasdiqlangan</option>
          <option value="rejected">Rad etilgan</option>
          <option value="completed">Bajarilgan</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-emerald-500 animate-spin" />
    </div>

    <!-- NB Permits List -->
    <div v-else class="space-y-4">
      <div
        v-for="permit in permits"
        :key="permit.id"
        class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="statusBg(permit.status)">
              <FileCheck class="w-6 h-6" :class="statusIcon(permit.status)" />
            </div>
            <div>
              <h3 class="font-semibold text-slate-800">{{ permit.student_name }}</h3>
              <p class="text-sm text-slate-500">{{ permit.group_name }} • {{ permit.subject || 'Fan ko\'rsatilmagan' }}</p>
              <p v-if="permit.reason" class="text-sm text-slate-600 mt-1">{{ permit.reason }}</p>
              <div class="flex flex-wrap items-center gap-2 mt-2">
                <span class="text-xs text-slate-400">
                  {{ permit.created_at ? new Date(permit.created_at).toLocaleDateString('uz-UZ') : '—' }}
                </span>
                <span v-if="permit.teacher_name" class="text-xs text-slate-400">
                  • O'qituvchi: {{ permit.teacher_name }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span
              class="px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap"
              :class="statusBadge(permit.status)"
            >
              {{ statusLabel(permit.status) }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="permits.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
        <FileCheck class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">NB ruxsatnomalar topilmadi</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FileCheck, Loader2, Search } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(false)
const permits = ref([])
const searchQuery = ref('')
const filterStatus = ref('')

const statusBg = (status) => {
  const map = {
    pending: 'bg-amber-100',
    approved: 'bg-emerald-100',
    rejected: 'bg-rose-100',
    completed: 'bg-blue-100'
  }
  return map[status] || 'bg-slate-100'
}

const statusIcon = (status) => {
  const map = {
    pending: 'text-amber-600',
    approved: 'text-emerald-600',
    rejected: 'text-rose-600',
    completed: 'text-blue-600'
  }
  return map[status] || 'text-slate-600'
}

const statusBadge = (status) => {
  const map = {
    pending: 'bg-amber-100 text-amber-700',
    approved: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-rose-100 text-rose-700',
    completed: 'bg-blue-100 text-blue-700'
  }
  return map[status] || 'bg-slate-100 text-slate-700'
}

const statusLabel = (status) => {
  const map = {
    pending: 'Kutilmoqda',
    approved: 'Tasdiqlangan',
    rejected: 'Rad etilgan',
    completed: 'Bajarilgan'
  }
  return map[status] || status
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadNBPermits()
  }, 400)
}

const loadNBPermits = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    const resp = await api.get(`/dean/nb-permits?${params}`)
    permits.value = resp.permits || resp.items || resp || []
  } catch (err) {
    console.error('Dean NB permits error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadNBPermits()
})
</script>
