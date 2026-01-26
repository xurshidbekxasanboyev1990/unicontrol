<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">AI Tahlil</h1>
        <p class="text-slate-500">Shaxsiy o'quv tahlili va tavsiyalar</p>
      </div>
      <div class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 px-4 py-2 text-white">
        <Sparkles :size="18" />
        <span class="text-sm font-medium">AI tomonidan tahlil qilingan</span>
      </div>
    </div>

    <!-- Overall Score Card -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-6 text-white">
      <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-10 -left-10 h-40 w-40 rounded-full bg-white/10"></div>
      
      <div class="relative flex items-center gap-6">
        <div class="flex h-32 w-32 flex-col items-center justify-center rounded-2xl bg-white/20 backdrop-blur">
          <span class="text-5xl font-bold">{{ overallScore }}</span>
          <span class="text-sm text-white/80">100 dan</span>
        </div>
        
        <div class="flex-1">
          <h2 class="text-xl font-semibold">Umumiy ball</h2>
          <p class="mt-1 text-white/80">{{ getScoreDescription(overallScore) }}</p>
          
          <div class="mt-4 flex items-center gap-4">
            <div class="flex items-center gap-2">
              <TrendingUp :size="18" class="text-green-300" />
              <span class="text-sm">+5 o'tgan haftaga nisbatan</span>
            </div>
          </div>
        </div>
        
        <div class="hidden lg:block">
          <Brain :size="80" class="text-white/20" />
        </div>
      </div>
    </div>

    <!-- Analysis Categories -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="category in analysisCategories"
        :key="category.id"
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <div class="mb-4 flex items-center justify-between">
          <div 
            class="flex h-12 w-12 items-center justify-center rounded-xl"
            :class="category.bgColor"
          >
            <component :is="category.icon" :size="24" :class="category.textColor" />
          </div>
          <span 
            class="text-2xl font-bold"
            :class="getScoreColor(category.score)"
          >
            {{ category.score }}%
          </span>
        </div>
        <h3 class="font-medium text-slate-800">{{ category.name }}</h3>
        <p class="mt-1 text-sm text-slate-500">{{ category.description }}</p>
        
        <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
          <div 
            class="h-full rounded-full transition-all"
            :class="getProgressColor(category.score)"
            :style="{ width: category.score + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Detailed Analysis -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Strengths -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
            <ThumbsUp :size="20" class="text-green-600" />
          </div>
          <h2 class="font-semibold text-slate-800">Kuchli tomonlar</h2>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="strength in strengths"
            :key="strength.id"
            class="flex items-start gap-3 rounded-xl bg-green-50 p-3"
          >
            <CheckCircle :size="20" class="mt-0.5 flex-shrink-0 text-green-500" />
            <div>
              <p class="font-medium text-slate-800">{{ strength.title }}</p>
              <p class="text-sm text-slate-600">{{ strength.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Areas to Improve -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center gap-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
            <Target :size="20" class="text-amber-600" />
          </div>
          <h2 class="font-semibold text-slate-800">Yaxshilash kerak</h2>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="area in areasToImprove"
            :key="area.id"
            class="flex items-start gap-3 rounded-xl bg-amber-50 p-3"
          >
            <AlertTriangle :size="20" class="mt-0.5 flex-shrink-0 text-amber-500" />
            <div>
              <p class="font-medium text-slate-800">{{ area.title }}</p>
              <p class="text-sm text-slate-600">{{ area.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Recommendations -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center gap-2">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100">
          <Lightbulb :size="20" class="text-indigo-600" />
        </div>
        <h2 class="font-semibold text-slate-800">AI Tavsiyalari</h2>
      </div>
      
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="rec in recommendations"
          :key="rec.id"
          class="rounded-xl border border-slate-200 p-4 transition-all hover:border-indigo-300 hover:shadow-md"
        >
          <div class="mb-3 flex items-center gap-2">
            <component :is="rec.icon" :size="20" :class="rec.iconColor" />
            <span 
              class="rounded-full px-2 py-0.5 text-xs font-medium"
              :class="rec.priorityClass"
            >
              {{ rec.priority }}
            </span>
          </div>
          <h3 class="font-medium text-slate-800">{{ rec.title }}</h3>
          <p class="mt-1 text-sm text-slate-600">{{ rec.description }}</p>
          
          <button
            v-if="rec.action"
            @click="handleAction(rec.action)"
            class="mt-3 flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700"
          >
            {{ rec.actionText }}
            <ArrowRight :size="14" />
          </button>
        </div>
      </div>
    </div>

    <!-- Weekly Progress Chart -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="font-semibold text-slate-800">Haftalik progress</h2>
        <select class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600">
          <option>Oxirgi 4 hafta</option>
          <option>Oxirgi 3 oy</option>
          <option>Butun semestr</option>
        </select>
      </div>
      
      <div class="flex items-end justify-between gap-2 h-48">
        <div
          v-for="(week, index) in weeklyProgress"
          :key="index"
          class="flex-1 flex flex-col items-center gap-2"
        >
          <div 
            class="w-full rounded-t-lg transition-all"
            :class="getProgressColor(week.score)"
            :style="{ height: week.score + '%' }"
          ></div>
          <span class="text-xs text-slate-500">{{ week.label }}</span>
        </div>
      </div>
    </div>

    <!-- Attendance Analysis -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center gap-2">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
          <Calendar :size="20" class="text-blue-600" />
        </div>
        <h2 class="font-semibold text-slate-800">Davomat tahlili</h2>
      </div>
      
      <div class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-xl bg-green-50 p-4 text-center">
          <p class="text-3xl font-bold text-green-600">{{ attendanceStats.present }}</p>
          <p class="text-sm text-green-600/70">Kelgan kunlar</p>
        </div>
        <div class="rounded-xl bg-amber-50 p-4 text-center">
          <p class="text-3xl font-bold text-amber-600">{{ attendanceStats.late }}</p>
          <p class="text-sm text-amber-600/70">Kechikkan</p>
        </div>
        <div class="rounded-xl bg-red-50 p-4 text-center">
          <p class="text-3xl font-bold text-red-600">{{ attendanceStats.absent }}</p>
          <p class="text-sm text-red-600/70">Kelmagan</p>
        </div>
      </div>
      
      <div class="mt-4 rounded-xl bg-slate-50 p-4">
        <div class="flex items-start gap-3">
          <Info :size="20" class="mt-0.5 flex-shrink-0 text-blue-500" />
          <div>
            <p class="font-medium text-slate-800">AI xulosasi</p>
            <p class="text-sm text-slate-600">
              {{ attendanceAnalysis }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Study Tips -->
    <div class="rounded-2xl border border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50 p-5">
      <div class="flex items-start gap-4">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500 text-white">
          <Sparkles :size="24" />
        </div>
        <div>
          <h2 class="font-semibold text-slate-800">Bugungi maslahat</h2>
          <p class="mt-1 text-slate-600">{{ dailyTip }}</p>
          <button class="mt-3 flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700">
            <RefreshCw :size="14" />
            Yangi maslahat
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import {
  Sparkles, Brain, TrendingUp, ThumbsUp, Target, Lightbulb, ArrowRight,
  CheckCircle, AlertTriangle, Calendar, Info, RefreshCw,
  BookOpen, Clock, Award, Users, Zap, Heart
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const dataStore = useDataStore()

// Overall Score
const overallScore = ref(78)

// Analysis Categories
const analysisCategories = [
  {
    id: 1,
    name: 'Davomat',
    description: 'Darslarga qatnashish darajasi',
    score: 85,
    icon: Calendar,
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-600'
  },
  {
    id: 2,
    name: 'Faollik',
    description: 'Darsda ishtirok etish',
    score: 72,
    icon: Zap,
    bgColor: 'bg-amber-100',
    textColor: 'text-amber-600'
  },
  {
    id: 3,
    name: 'Vaqtga rioya',
    description: 'Darslarga o\'z vaqtida kelish',
    score: 90,
    icon: Clock,
    bgColor: 'bg-green-100',
    textColor: 'text-green-600'
  },
  {
    id: 4,
    name: 'Kutubxona',
    description: 'Kitob o\'qish faolligi',
    score: 65,
    icon: BookOpen,
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-600'
  }
]

// Strengths
const strengths = [
  {
    id: 1,
    title: 'Yuqori davomat',
    description: 'Darslarning 85% ga qatnashgansiz. Bu guruh o\'rtachasidan yuqori.'
  },
  {
    id: 2,
    title: 'Punktuallik',
    description: 'Aksariyat darslarga o\'z vaqtida keldingiz. Ajoyib!'
  },
  {
    id: 3,
    title: 'Barqarorlik',
    description: 'Oxirgi 4 hafta davomida davomatingiz barqaror.'
  }
]

// Areas to Improve
const areasToImprove = [
  {
    id: 1,
    title: 'Kutubxona faolligi',
    description: 'Oyiga kamida 2 ta kitob o\'qish tavsiya etiladi.'
  },
  {
    id: 2,
    title: 'Dushanba darslari',
    description: 'Dushanba kunlari davomatingiz past. Sababi nima?'
  }
]

// Recommendations
const recommendations = [
  {
    id: 1,
    title: 'Darsga tayyorgarlik',
    description: 'Har kuni 30 daqiqa dars materiallarini takrorlang.',
    icon: BookOpen,
    iconColor: 'text-blue-500',
    priority: 'Muhim',
    priorityClass: 'bg-blue-100 text-blue-600',
    action: 'schedule',
    actionText: 'Jadval yaratish'
  },
  {
    id: 2,
    title: 'Kutubxonaga tashrif',
    description: 'Siz uchun "Dasturlash asoslari" kitobi tavsiya etiladi.',
    icon: BookOpen,
    iconColor: 'text-purple-500',
    priority: 'Tavsiya',
    priorityClass: 'bg-purple-100 text-purple-600',
    action: 'library',
    actionText: 'Kutubxonaga o\'tish'
  },
  {
    id: 3,
    title: 'Dam olish',
    description: 'Kunlik 7-8 soat uxlash o\'zlashtirish uchun muhim.',
    icon: Heart,
    iconColor: 'text-rose-500',
    priority: 'Sog\'liq',
    priorityClass: 'bg-rose-100 text-rose-600'
  }
]

// Weekly Progress
const weeklyProgress = [
  { label: '1-hafta', score: 65 },
  { label: '2-hafta', score: 72 },
  { label: '3-hafta', score: 70 },
  { label: '4-hafta', score: 78 }
]

// Attendance Stats
const attendanceStats = {
  present: 42,
  late: 5,
  absent: 3
}

const attendanceAnalysis = computed(() => {
  const rate = (attendanceStats.present / (attendanceStats.present + attendanceStats.late + attendanceStats.absent)) * 100
  if (rate >= 90) return 'Ajoyib davomat! Siz eng faol talabalar qatoridansiz. Shunday davom eting!'
  if (rate >= 75) return 'Yaxshi davomat. Biroz yaxshilash bilan mukammallikka erishish mumkin.'
  if (rate >= 60) return 'O\'rtacha davomat. Darslarni qoldirmaslikka harakat qiling.'
  return 'Past davomat. Bu o\'zlashtirish va bahoga ta\'sir qilishi mumkin.'
})

const dailyTip = ref('Darsdan oldin 10 daqiqa o\'tgan mavzuni takrorlash, yangi materialni 40% yaxshiroq o\'zlashtirishga yordam beradi.')

// Methods
function getScoreDescription(score) {
  if (score >= 90) return 'Mukammal! Siz eng yaxshi talabalar qatoridansiz.'
  if (score >= 75) return 'Yaxshi natija! Biroz yaxshilash bilan mukammallikka erishasiz.'
  if (score >= 60) return 'O\'rtacha holat. Tavsiyalarga amal qilsangiz yaxshilanadi.'
  return 'E\'tibor bering! Natijalarni yaxshilash kerak.'
}

function getScoreColor(score) {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-red-600'
}

function getProgressColor(score) {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-amber-500'
  return 'bg-red-500'
}

function handleAction(action) {
  if (action === 'library') {
    router.push('/student/library')
  } else if (action === 'schedule') {
    router.push('/student/schedule')
  }
}
</script>
