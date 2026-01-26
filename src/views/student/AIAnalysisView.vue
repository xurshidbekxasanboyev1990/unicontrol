<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">AI Tahlil</h1>
        <p class="text-slate-500">Sun'iy intellekt asosidagi tahlil va tavsiyalar</p>
      </div>
      <button 
        @click="refreshAnalysis"
        :disabled="isAnalyzing"
        class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 px-4 py-2.5 text-white transition-all hover:from-violet-600 hover:to-purple-700 disabled:opacity-50"
      >
        <RefreshCw :size="18" :class="{ 'animate-spin': isAnalyzing }" />
        <span>{{ isAnalyzing ? 'Tahlil qilinmoqda...' : 'Yangilash' }}</span>
      </button>
    </div>

    <!-- AI Summary Card -->
    <div class="rounded-2xl bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600 p-6 text-white shadow-xl">
      <div class="flex items-start gap-4">
        <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/20 backdrop-blur">
          <Sparkles :size="28" />
        </div>
        <div class="flex-1">
          <h2 class="text-xl font-bold">{{ aiSummaryTitle }}</h2>
          <p class="mt-2 text-violet-100 leading-relaxed">{{ aiSummaryText }}</p>
        </div>
      </div>
      
      <div class="mt-6 grid grid-cols-3 gap-4">
        <div class="rounded-xl bg-white/10 p-4 backdrop-blur text-center">
          <p class="text-3xl font-bold">{{ stats.rate }}%</p>
          <p class="text-sm text-violet-200">Davomat</p>
        </div>
        <div class="rounded-xl bg-white/10 p-4 backdrop-blur text-center">
          <p class="text-3xl font-bold">{{ stats.present }}</p>
          <p class="text-sm text-violet-200">Kelgan dars</p>
        </div>
        <div class="rounded-xl bg-white/10 p-4 backdrop-blur text-center">
          <p class="text-3xl font-bold">{{ stats.absent }}</p>
          <p class="text-sm text-violet-200">Qoldirilgan</p>
        </div>
      </div>
    </div>

    <!-- Analysis Sections -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Davomat Tahlili -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
            <TrendingUp :size="24" class="text-emerald-600" />
          </div>
          <div>
            <h3 class="font-semibold text-slate-800">Davomat tahlili</h3>
            <p class="text-sm text-slate-500">So'nggi 30 kun</p>
          </div>
        </div>
        
        <div class="space-y-4">
          <div class="rounded-xl bg-slate-50 p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-600">Umumiy davomat</span>
              <span class="font-semibold text-slate-800">{{ stats.rate }}%</span>
            </div>
            <div class="h-3 overflow-hidden rounded-full bg-slate-200">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :class="getProgressColor(stats.rate)"
                :style="{ width: stats.rate + '%' }"
              ></div>
            </div>
          </div>
          
          <div class="space-y-2">
            <div class="flex items-center justify-between p-3 rounded-lg bg-emerald-50">
              <div class="flex items-center gap-2">
                <CheckCircle :size="18" class="text-emerald-600" />
                <span class="text-emerald-700">Kelgan</span>
              </div>
              <span class="font-semibold text-emerald-700">{{ stats.present }} dars</span>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-amber-50">
              <div class="flex items-center gap-2">
                <Clock :size="18" class="text-amber-600" />
                <span class="text-amber-700">Kechikkan</span>
              </div>
              <span class="font-semibold text-amber-700">{{ stats.late }} dars</span>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-rose-50">
              <div class="flex items-center gap-2">
                <XCircle :size="18" class="text-rose-600" />
                <span class="text-rose-700">Kelmagan</span>
              </div>
              <span class="font-semibold text-rose-700">{{ stats.absent }} dars</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fanlar bo'yicha -->
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
            <BookOpen :size="24" class="text-blue-600" />
          </div>
          <div>
            <h3 class="font-semibold text-slate-800">Fanlar bo'yicha</h3>
            <p class="text-sm text-slate-500">Davomat taqsimoti</p>
          </div>
        </div>
        
        <div class="space-y-3">
          <div 
            v-for="subject in subjectStats" 
            :key="subject.name"
            class="rounded-xl bg-slate-50 p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-slate-700">{{ subject.name }}</span>
              <span class="text-sm font-semibold" :class="getTextColor(subject.rate)">{{ subject.rate }}%</span>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-slate-200">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :class="getProgressColor(subject.rate)"
                :style="{ width: subject.rate + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Tavsiyalar -->
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
          <Lightbulb :size="24" class="text-violet-600" />
        </div>
        <div>
          <h3 class="font-semibold text-slate-800">AI Tavsiyalari</h3>
          <p class="text-sm text-slate-500">Shaxsiy tavsiyalar</p>
        </div>
      </div>
      
      <div class="space-y-3">
        <div 
          v-for="(tip, index) in aiTips" 
          :key="index"
          class="flex items-start gap-3 rounded-xl p-4 transition-all"
          :class="tip.bgClass"
        >
          <component :is="tip.icon" :size="20" :class="tip.iconClass" class="mt-0.5 flex-shrink-0" />
          <div>
            <p class="font-medium" :class="tip.titleClass">{{ tip.title }}</p>
            <p class="mt-1 text-sm" :class="tip.textClass">{{ tip.text }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Haftalik Trend -->
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100">
          <BarChart3 :size="24" class="text-indigo-600" />
        </div>
        <div>
          <h3 class="font-semibold text-slate-800">Haftalik trend</h3>
          <p class="text-sm text-slate-500">So'nggi 4 hafta</p>
        </div>
      </div>
      
      <div class="flex items-end justify-between gap-4 h-40 mt-6">
        <div 
          v-for="week in weeklyData" 
          :key="week.label"
          class="flex-1 flex flex-col items-center gap-2"
        >
          <div class="w-full bg-slate-100 rounded-t-lg relative" style="height: 120px;">
            <div 
              class="absolute bottom-0 left-0 right-0 rounded-t-lg transition-all duration-500"
              :class="getProgressColor(week.rate)"
              :style="{ height: week.rate + '%' }"
            ></div>
          </div>
          <span class="text-xs text-slate-500">{{ week.label }}</span>
          <span class="text-sm font-semibold text-slate-700">{{ week.rate }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * AIAnalysisView.vue - AI Tahlil sahifasi
 * 
 * BU YERDA BALL TIZIMI YO'Q!
 * Faqat:
 * - Davomat tahlili
 * - Faollik tahlili  
 * - AI tavsiyalari
 * - Trend va statistika
 */

import { ref, computed, markRaw } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import {
  Sparkles,
  RefreshCw,
  TrendingUp,
  BookOpen,
  Lightbulb,
  BarChart3,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  Target,
  Calendar
} from 'lucide-vue-next'

const dataStore = useDataStore()
const authStore = useAuthStore()

const isAnalyzing = ref(false)

// Talaba ma'lumotlari
const student = computed(() => {
  return dataStore.students.find(s => s.id === authStore.user?.studentId) || dataStore.students[0]
})

// Davomat yozuvlari
const records = computed(() => {
  return dataStore.attendanceRecords.filter(r => r.studentId === student.value?.id)
})

// Statistika
const stats = computed(() => {
  const total = records.value.length || 1
  const present = records.value.filter(r => r.status === 'present').length
  const late = records.value.filter(r => r.status === 'late').length
  const absent = records.value.filter(r => r.status === 'absent').length
  const rate = Math.round(((present + late) / total) * 100)

  return { total, present, late, absent, rate }
})

// Fanlar bo'yicha statistika
const subjectStats = computed(() => {
  const subjects = [...new Set(records.value.map(r => r.subject))]
  
  return subjects.map(subject => {
    const subjectRecords = records.value.filter(r => r.subject === subject)
    const total = subjectRecords.length || 1
    const attended = subjectRecords.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = Math.round((attended / total) * 100)
    
    return { name: subject, total, attended, rate }
  }).sort((a, b) => b.rate - a.rate)
})

// Haftalik data
const weeklyData = ref([
  { label: '1-hafta', rate: 85 },
  { label: '2-hafta', rate: 90 },
  { label: '3-hafta', rate: 78 },
  { label: '4-hafta', rate: stats.value.rate }
])

// AI xulosa sarlavhasi
const aiSummaryTitle = computed(() => {
  if (stats.value.rate >= 90) return "Ajoyib natija! 🎉"
  if (stats.value.rate >= 75) return "Yaxshi davom etyapsiz! 👍"
  if (stats.value.rate >= 60) return "Yaxshilash imkoniyati bor 📈"
  return "E'tibor qarating! ⚠️"
})

// AI xulosa matni
const aiSummaryText = computed(() => {
  if (stats.value.rate >= 90) {
    return `Tabriklaymiz! Sizning davomatingiz ${stats.value.rate}% ni tashkil etadi. Bu juda yaxshi ko'rsatkich. Shu yo'lda davom eting va darslarga muntazam qatnashishda davom eting.`
  }
  if (stats.value.rate >= 75) {
    return `Sizning davomatingiz ${stats.value.rate}% - yaxshi natija. Ammo ${stats.value.absent} ta dars qoldirgansiz. Agar davomatni 90% dan yuqori ushlab tursangiz, yanada yaxshi bo'ladi.`
  }
  if (stats.value.rate >= 60) {
    return `Davomatingiz ${stats.value.rate}% - o'rtacha daraja. ${stats.value.absent} ta dars qoldirilgan. Darslarni o'tkazib yubormaslikka harakat qiling, bu akademik natijalaringizga ta'sir qilishi mumkin.`
  }
  return `Ogohlantirish! Davomatingiz ${stats.value.rate}% - bu past ko'rsatkich. ${stats.value.absent} ta dars qoldirgansiz. Dekanat bilan bog'lanishingiz va vaziyatni yaxshilashingiz tavsiya etiladi.`
})

// AI tavsiyalar
const aiTips = computed(() => {
  const tips = []
  
  if (stats.value.rate >= 90) {
    tips.push({
      icon: markRaw(Target),
      title: "Maqsadga erishing",
      text: "Siz a'lo ko'rsatkichga erishdingiz. Bu natijani saqlab qoling va boshqalarga namuna bo'ling.",
      bgClass: "bg-emerald-50",
      iconClass: "text-emerald-600",
      titleClass: "text-emerald-800",
      textClass: "text-emerald-600"
    })
  }
  
  if (stats.value.absent > 0) {
    tips.push({
      icon: markRaw(AlertTriangle),
      title: "Qoldirilgan darslar",
      text: `${stats.value.absent} ta dars qoldirgansiz. Imkon qadar darslarga qatnashing.`,
      bgClass: "bg-amber-50",
      iconClass: "text-amber-600",
      titleClass: "text-amber-800",
      textClass: "text-amber-600"
    })
  }
  
  if (stats.value.late > 0) {
    tips.push({
      icon: markRaw(Clock),
      title: "Kechikishlar",
      text: `${stats.value.late} marta kechikgansiz. Vaqtida kelishga harakat qiling.`,
      bgClass: "bg-blue-50",
      iconClass: "text-blue-600",
      titleClass: "text-blue-800",
      textClass: "text-blue-600"
    })
  }
  
  // Eng past fan
  const lowestSubject = subjectStats.value[subjectStats.value.length - 1]
  if (lowestSubject && lowestSubject.rate < 80) {
    tips.push({
      icon: markRaw(BookOpen),
      title: `${lowestSubject.name} faniga e'tibor`,
      text: `Bu fanda davomatingiz ${lowestSubject.rate}%. Darslarni o'tkazib yubormaslikka harakat qiling.`,
      bgClass: "bg-rose-50",
      iconClass: "text-rose-600",
      titleClass: "text-rose-800",
      textClass: "text-rose-600"
    })
  }
  
  tips.push({
    icon: markRaw(Calendar),
    title: "Muntazamlik muhim",
    text: "Har kuni darslarga qatnashish bilim olishning eng yaxshi yo'li. Dars jadvalingizni kuzatib boring.",
    bgClass: "bg-indigo-50",
    iconClass: "text-indigo-600",
    titleClass: "text-indigo-800",
    textClass: "text-indigo-600"
  })
  
  return tips
})

// Rang funksiyalari
function getProgressColor(rate) {
  if (rate >= 85) return 'bg-emerald-500'
  if (rate >= 70) return 'bg-amber-500'
  return 'bg-rose-500'
}

function getTextColor(rate) {
  if (rate >= 85) return 'text-emerald-600'
  if (rate >= 70) return 'text-amber-600'
  return 'text-rose-600'
}

// Yangilash
async function refreshAnalysis() {
  isAnalyzing.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  isAnalyzing.value = false
}
</script>
