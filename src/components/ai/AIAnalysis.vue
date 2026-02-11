<template>
  <div class="bg-gradient-to-br from-violet-500/10 via-purple-500/10 to-indigo-500/10 rounded-3xl border border-violet-200/60 p-6 relative overflow-hidden">
    <!-- AI Background decoration -->
    <div class="absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br from-violet-400/20 to-indigo-400/20 rounded-full blur-3xl"></div>
    <div class="absolute -bottom-20 -left-20 w-40 h-40 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"></div>
    
    <!-- Header -->
    <div class="relative flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
          <Sparkles class="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 class="text-lg font-bold text-slate-800">AI Tahlil</h2>
          <p class="text-sm text-slate-500">{{ title }}</p>
        </div>
      </div>
      <button
        @click="refreshAnalysis"
        :disabled="isLoading"
        class="flex items-center gap-2 px-4 py-2 bg-white/80 text-violet-600 rounded-xl text-sm font-medium hover:bg-white transition-colors disabled:opacity-50"
      >
        <RefreshCw :class="['w-4 h-4', isLoading && 'animate-spin']" />
        Yangilash
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="relative py-12 text-center">
      <div class="inline-flex items-center gap-3">
        <Loader2 class="w-6 h-6 text-violet-500 animate-spin" />
        <span class="text-slate-600">AI tahlil qilmoqda...</span>
      </div>
      <div class="mt-4 flex justify-center gap-1">
        <span v-for="i in 3" :key="i" class="w-2 h-2 bg-violet-400 rounded-full animate-bounce" :style="{ animationDelay: `${i * 0.1}s` }"></span>
      </div>
    </div>

    <!-- Analysis Content -->
    <div v-else class="relative space-y-6">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="(metric, index) in metrics"
          :key="index"
          class="bg-white/60 backdrop-blur-sm rounded-2xl p-4 border border-white/80"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-slate-500">{{ metric.label }}</span>
            <component :is="metric.icon" :class="['w-5 h-5', metric.color]" />
          </div>
          <p class="text-2xl font-bold text-slate-800">{{ metric.value }}</p>
          <div class="mt-2 flex items-center gap-1">
            <TrendingUp v-if="metric.trend > 0" class="w-4 h-4 text-emerald-500" />
            <TrendingDown v-else class="w-4 h-4 text-rose-500" />
            <span :class="[
              'text-sm font-medium',
              metric.trend > 0 ? 'text-emerald-600' : 'text-rose-600'
            ]">
              {{ Math.abs(metric.trend) }}%
            </span>
            <span class="text-xs text-slate-400">o'tgan oyga nisbatan</span>
          </div>
        </div>
      </div>

      <!-- AI Insights -->
      <div class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
        <div class="flex items-center gap-2 mb-4">
          <Brain class="w-5 h-5 text-violet-500" />
          <h3 class="font-semibold text-slate-800">AI Xulosalari</h3>
        </div>
        
        <div class="space-y-4">
          <div 
            v-for="(insight, index) in insights"
            :key="index"
            class="flex items-start gap-3 p-3 rounded-xl hover:bg-white/50 transition-colors"
          >
            <div :class="[
              'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center',
              getInsightTypeClass(insight.type)
            ]">
              <component :is="getInsightIcon(insight.type)" class="w-4 h-4" />
            </div>
            <div>
              <p class="text-sm font-medium text-slate-700">{{ insight.title }}</p>
              <p class="text-sm text-slate-500 mt-0.5">{{ insight.description }}</p>
              <button 
                v-if="insight.action"
                class="mt-2 text-xs font-medium text-violet-600 hover:text-violet-700"
              >
                {{ insight.action }} →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
        <div class="flex items-center gap-2 mb-4">
          <Lightbulb class="w-5 h-5 text-amber-500" />
          <h3 class="font-semibold text-slate-800">Tavsiyalar</h3>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="(rec, index) in recommendations"
            :key="index"
            class="flex items-start gap-3 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl border border-amber-100"
          >
            <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
              <span class="text-amber-600 text-sm font-bold">{{ index + 1 }}</span>
            </div>
            <div>
              <p class="text-sm font-medium text-slate-700">{{ rec.title }}</p>
              <p class="text-xs text-slate-500 mt-1">{{ rec.description }}</p>
              <div v-if="rec.priority" class="mt-2">
                <span :class="[
                  'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                  rec.priority === 'high' ? 'bg-rose-100 text-rose-700' :
                  rec.priority === 'medium' ? 'bg-orange-100 text-orange-700' :
                  'bg-slate-100 text-slate-600'
                ]">
                  {{ rec.priority === 'high' ? 'Muhim' : rec.priority === 'medium' ? 'O\'rta' : 'Past' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Predictions (if available) -->
      <div v-if="predictions.length > 0" class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
        <div class="flex items-center gap-2 mb-4">
          <Activity class="w-5 h-5 text-blue-500" />
          <h3 class="font-semibold text-slate-800">Bashoratlar</h3>
        </div>
        
        <div class="space-y-3">
          <div 
            v-for="(pred, index) in predictions"
            :key="index"
            class="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                <component :is="pred.icon" class="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p class="text-sm font-medium text-slate-700">{{ pred.title }}</p>
                <p class="text-xs text-slate-500">{{ pred.description }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-lg font-bold text-blue-600">{{ pred.value }}</p>
              <p class="text-xs text-slate-400">{{ pred.confidence }}% ishonch</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Sparkles, RefreshCw, Loader2, TrendingUp, TrendingDown, Brain, Lightbulb,
  Activity, AlertTriangle, CheckCircle, Info, Clock, Users, BookOpen,
  Target, Award, BarChart3, Calendar
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    default: 'Umumiy tahlil'
  },
  type: {
    type: String,
    default: 'student', // student, leader, admin
    validator: (value) => ['student', 'leader', 'admin'].includes(value)
  }
})

const isLoading = ref(true)
const metrics = ref([])
const insights = ref([])
const recommendations = ref([])
const predictions = ref([])

function loadData() {
  isLoading.value = true
  
  // Simulate API call
  setTimeout(() => {
    if (props.type === 'student') {
      loadStudentData()
    } else if (props.type === 'leader') {
      loadLeaderData()
    } else {
      loadAdminData()
    }
    isLoading.value = false
  }, 1500)
}

function loadStudentData() {
  metrics.value = [
    { label: 'Davomat foizi', value: '87%', icon: CheckCircle, color: 'text-emerald-500', trend: 5 },
    { label: 'O\'rtacha baho', value: '4.2', icon: Award, color: 'text-amber-500', trend: 3 },
    { label: 'Darslar soni', value: '156', icon: BookOpen, color: 'text-blue-500', trend: 0 }
  ]
  
  insights.value = [
    {
      type: 'positive',
      title: 'Davomat yaxshilandi',
      description: 'Oxirgi oyda davomatingiz 5% ga oshdi. Davom eting!',
    },
    {
      type: 'warning',
      title: 'Matematika darslari',
      description: 'Matematika fanidan 3 ta darsni qoldirgansiz. Bu baholashga ta\'sir qilishi mumkin.',
      action: 'Jadvalga qarang'
    },
    {
      type: 'info',
      title: 'Guruh o\'rtachasi bilan taqqoslash',
      description: 'Sizning davomatingiz guruh o\'rtachasidan 12% yuqori.',
    }
  ]
  
  recommendations.value = [
    {
      title: 'Matematika darslariga e\'tibor bering',
      description: 'Qolgan darslarniy qoplash uchun o\'qituvchi bilan gaplashing',
      priority: 'high'
    },
    {
      title: 'Sport to\'garak',
      description: 'Faolligingizni oshirish uchun sport to\'garakka yoziling',
      priority: 'low'
    }
  ]
  
  predictions.value = [
    {
      icon: Target,
      title: 'Semestr oxirigacha davomat',
      description: 'Shu tezlikda davom etsangiz',
      value: '89%',
      confidence: 85
    }
  ]
}

function loadLeaderData() {
  metrics.value = [
    { label: 'Guruh davomati', value: '82%', icon: Users, color: 'text-emerald-500', trend: 2 },
    { label: 'Hisobotlar soni', value: '12', icon: BarChart3, color: 'text-blue-500', trend: 8 },
    { label: 'Faol talabalar', value: '24/28', icon: Activity, color: 'text-violet-500', trend: 4 }
  ]
  
  insights.value = [
    {
      type: 'positive',
      title: 'Guruh faolligi yuqori',
      description: '85% talabalar oxirgi haftada barcha darslarga qatnashdi',
    },
    {
      type: 'warning',
      title: 'Diqqat talab qiluvchi talabalar',
      description: '4 ta talabaning davomati 70% dan past. Ular bilan suhbat o\'tkazing.',
      action: 'Ro\'yxatni ko\'rish'
    },
    {
      type: 'info',
      title: 'Eng faol kun',
      description: 'Dushanba kuni eng yuqori davomat kuzatiladi (94%)',
    },
    {
      type: 'negative',
      title: 'Juma kuni past davomat',
      description: 'Juma kunlari davomat 15% ga tushadi. Sababini aniqlang.',
      action: 'Statistikani ko\'rish'
    }
  ]
  
  recommendations.value = [
    {
      title: 'Past davomatli talabalar bilan suhbat',
      description: 'Aliyev J., Karimova N., va 2 ta boshqa talaba bilan gaplashing',
      priority: 'high'
    },
    {
      title: 'Oylik hisobotni tayyorlang',
      description: 'Fevral oyi hisoboti 3 kun ichida topshirilishi kerak',
      priority: 'medium'
    },
    {
      title: 'Guruh yig\'ilishi',
      description: 'Haftalik guruh yig\'ilishi o\'tkazish tavsiya etiladi',
      priority: 'low'
    }
  ]
  
  predictions.value = [
    {
      icon: Users,
      title: 'Semestr davomati bashorati',
      description: 'Guruh davomati',
      value: '84%',
      confidence: 78
    },
    {
      icon: Award,
      title: 'A\'lochi talabalar soni',
      description: 'Semestr oxirida kutilmoqda',
      value: '8',
      confidence: 72
    }
  ]
}

function loadAdminData() {
  metrics.value = [
    { label: 'Umumiy davomat', value: '79%', icon: Users, color: 'text-emerald-500', trend: -2 },
    { label: 'Faol guruhlar', value: '45/52', icon: Activity, color: 'text-blue-500', trend: 5 },
    { label: 'Hisobotlar', value: '156', icon: BarChart3, color: 'text-violet-500', trend: 12 }
  ]
  
  insights.value = [
    {
      type: 'positive',
      title: 'Eng faol fakultet',
      description: 'Iqtisodiyot fakulteti 91% davomat bilan yetakchilik qilmoqda',
    },
    {
      type: 'negative',
      title: 'Muammoli guruhlar',
      description: '7 ta guruhda davomat 65% dan past. Sardorlar bilan suhbat talab etiladi.',
      action: 'Ro\'yxatni ko\'rish'
    },
    {
      type: 'warning',
      title: 'Hisobotlar kechikmoqda',
      description: '12 ta guruh sardori yanvar oyi hisobotini topshirmagan',
      action: 'Bildirishnoma yuborish'
    },
    {
      type: 'info',
      title: 'O\'sish tendensiyasi',
      description: 'Oxirgi 3 oyda umumiy davomat 8% ga oshdi',
    }
  ]
  
  recommendations.value = [
    {
      title: 'Kechikkan hisobotlar',
      description: '12 ta guruh sardoriga eslatma yuboring',
      priority: 'high'
    },
    {
      title: 'Past davomatli guruhlar',
      description: 'Muammoli guruhlar ro\'yxatini ko\'rib chiqing va chora ko\'ring',
      priority: 'high'
    },
    {
      title: 'Oylik yig\'ilish',
      description: 'Fakultet sardorlari bilan yig\'ilish o\'tkazing',
      priority: 'medium'
    },
    {
      title: 'Mukofotlash tizimi',
      description: 'Eng faol guruhlarni mukofotlash dasturini ko\'rib chiqing',
      priority: 'low'
    }
  ]
  
  predictions.value = [
    {
      icon: Calendar,
      title: 'Keyingi oy bashorati',
      description: 'Kutilayotgan davomat',
      value: '81%',
      confidence: 82
    },
    {
      icon: AlertTriangle,
      title: 'Risk guruhlari',
      description: 'Past davomatga tushishi mumkin',
      value: '4',
      confidence: 68
    }
  ]
}

function refreshAnalysis() {
  loadData()
}

function getInsightTypeClass(type) {
  const classes = {
    positive: 'bg-emerald-100 text-emerald-600',
    warning: 'bg-amber-100 text-amber-600',
    negative: 'bg-rose-100 text-rose-600',
    info: 'bg-blue-100 text-blue-600'
  }
  return classes[type] || classes.info
}

function getInsightIcon(type) {
  const icons = {
    positive: CheckCircle,
    warning: AlertTriangle,
    negative: AlertTriangle,
    info: Info
  }
  return icons[type] || Info
}

onMounted(() => {
  loadData()
})
</script>
