<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 class="w-8 h-8 animate-spin text-violet-600" />
      <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <div class="flex items-center gap-3 text-red-600">
        <AlertTriangle class="w-6 h-6" />
        <span>{{ error }}</span>
      </div>
      <button 
        @click="loadAnalysisData" 
        class="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
      >
        {{ $t('common.retry') }}
      </button>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('ai.title') }}</h1>
          <p class="text-sm text-slate-500">{{ $t('ai.recommendations') }}</p>
        </div>
        <button 
          @click="refreshAnalysis"
          :disabled="isAnalyzing"
          class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 px-4 py-2.5 text-white transition-all hover:from-violet-600 hover:to-purple-700 disabled:opacity-50"
        >
          <RefreshCw :size="18" :class="{ 'animate-spin': isAnalyzing }" />
          <span>{{ isAnalyzing ? $t('ai.analyzing') : $t('common.refresh') }}</span>
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
      
      <div class="mt-6 grid grid-cols-3 gap-2 sm:gap-4">
        <div class="rounded-xl bg-white/10 p-3 sm:p-4 backdrop-blur text-center">
          <p class="text-xl sm:text-3xl font-bold">{{ stats.rate }}%</p>
          <p class="text-xs sm:text-sm text-violet-200">{{ $t('ai.attendance') }}</p>
        </div>
        <div class="rounded-xl bg-white/10 p-3 sm:p-4 backdrop-blur text-center">
          <p class="text-xl sm:text-3xl font-bold">{{ stats.present }}</p>
          <p class="text-xs sm:text-sm text-violet-200">{{ $t('ai.presentLessons') }}</p>
        </div>
        <div class="rounded-xl bg-white/10 p-3 sm:p-4 backdrop-blur text-center">
          <p class="text-xl sm:text-3xl font-bold">{{ stats.absent }}</p>
          <p class="text-xs sm:text-sm text-violet-200">{{ $t('ai.missedLessons') }}</p>
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
            <h3 class="font-semibold text-slate-800">{{ $t('ai.attendanceAnalysis') }}</h3>
            <p class="text-sm text-slate-500">{{ $t('ai.last30days') }}</p>
          </div>
        </div>
        
        <div class="space-y-4">
          <div class="rounded-xl bg-slate-50 p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-600">{{ $t('ai.overallAttendance') }}</span>
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
                <span class="text-emerald-700">{{ $t('attendance.present') }}</span>
              </div>
              <span class="font-semibold text-emerald-700">{{ stats.present }} {{ $t('ai.lessons') }}</span>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-amber-50">
              <div class="flex items-center gap-2">
                <Clock :size="18" class="text-amber-600" />
                <span class="text-amber-700">{{ $t('attendance.late') }}</span>
              </div>
              <span class="font-semibold text-amber-700">{{ stats.late }} {{ $t('ai.lessons') }}</span>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-rose-50">
              <div class="flex items-center gap-2">
                <XCircle :size="18" class="text-rose-600" />
                <span class="text-rose-700">{{ $t('attendance.absent') }}</span>
              </div>
              <span class="font-semibold text-rose-700">{{ stats.absent }} {{ $t('ai.lessons') }}</span>
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
            <h3 class="font-semibold text-slate-800">{{ $t('ai.bySubjects') }}</h3>
            <p class="text-sm text-slate-500">{{ $t('ai.attendanceDistribution') }}</p>
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

    <!-- AI Tavsiyalar (from real API) -->
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
          <Lightbulb :size="24" class="text-violet-600" />
        </div>
        <div>
          <h3 class="font-semibold text-slate-800">{{ $t('ai.aiRecommendations') }}</h3>
          <p class="text-sm text-slate-500">{{ $t('ai.personalRecommendations') }}</p>
        </div>
      </div>
      
      <!-- AI Loading -->
      <div v-if="aiLoading" class="py-8 text-center">
        <Loader2 class="w-6 h-6 animate-spin text-violet-500 mx-auto mb-2" />
        <p class="text-sm text-slate-500">{{ $t('ai.analyzing') }}...</p>
      </div>

      <!-- AI Error -->
      <div v-else-if="aiError" class="py-4 text-center">
        <AlertTriangle class="w-6 h-6 text-amber-500 mx-auto mb-2" />
        <p class="text-sm text-slate-500">{{ aiError }}</p>
        <button @click="loadAIAnalysis" class="mt-2 text-sm text-violet-600 hover:underline">{{ $t('common.retry') }}</button>
      </div>

      <!-- AI Results -->
      <div v-else class="space-y-3">
        <!-- Strengths -->
        <div 
          v-for="(strength, index) in aiStrengths" 
          :key="'s-' + index"
          class="flex items-start gap-3 rounded-xl p-4 bg-emerald-50"
        >
          <CheckCircle :size="20" class="text-emerald-600 mt-0.5 flex-shrink-0" />
          <div>
            <p class="font-medium text-emerald-800">{{ $t('ai.strength') }}</p>
            <p class="mt-1 text-sm text-emerald-600">{{ strength }}</p>
          </div>
        </div>

        <!-- Areas for improvement -->
        <div 
          v-for="(area, index) in aiAreas" 
          :key="'a-' + index"
          class="flex items-start gap-3 rounded-xl p-4 bg-amber-50"
        >
          <AlertTriangle :size="20" class="text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <p class="font-medium text-amber-800">{{ $t('ai.needsImprovement') }}</p>
            <p class="mt-1 text-sm text-amber-600">{{ area }}</p>
          </div>
        </div>

        <!-- Recommendations -->
        <div 
          v-for="(rec, index) in aiRecommendations" 
          :key="'r-' + index"
          class="flex items-start gap-3 rounded-xl p-4 bg-violet-50"
        >
          <Lightbulb :size="20" class="text-violet-600 mt-0.5 flex-shrink-0" />
          <div>
            <p class="font-medium text-violet-800">{{ $t('ai.recommendation') }} {{ index + 1 }}</p>
            <p class="mt-1 text-sm text-violet-600">{{ rec }}</p>
          </div>
        </div>

        <!-- Risk Level -->
        <div v-if="aiRiskLevel" class="flex items-center gap-3 rounded-xl p-4" :class="riskBgClass">
          <Target :size="20" :class="riskTextClass" class="flex-shrink-0" />
          <div>
            <p class="font-medium" :class="riskTextClass">{{ $t('ai.riskLevel') }}: {{ riskLabel }}</p>
            <p v-if="aiPrediction" class="mt-1 text-sm" :class="riskSubTextClass">{{ aiPrediction }}</p>
          </div>
        </div>

        <!-- Motivation (from recommendations endpoint) -->
        <div v-if="aiMotivation" class="flex items-start gap-3 rounded-xl p-4 bg-indigo-50">
          <Sparkles :size="20" class="text-indigo-600 mt-0.5 flex-shrink-0" />
          <div>
            <p class="font-medium text-indigo-800">{{ $t('ai.motivation') }}</p>
            <p class="mt-1 text-sm text-indigo-600">{{ aiMotivation }}</p>
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
          <h3 class="font-semibold text-slate-800">{{ $t('ai.weeklyTrend') }}</h3>
          <p class="text-sm text-slate-500">{{ $t('ai.last4weeks') }}</p>
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

    <!-- AI Chat -->
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600">
          <Sparkles :size="24" class="text-white" />
        </div>
        <div>
          <h3 class="font-semibold text-slate-800">{{ $t('ai.aiAssistant') }}</h3>
          <p class="text-sm text-slate-500">{{ $t('ai.askQuestion') }}</p>
        </div>
      </div>

      <!-- Chat Messages -->
      <div v-if="chatMessages.length" class="space-y-3 mb-4 max-h-64 overflow-y-auto">
        <div v-for="(msg, i) in chatMessages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
          <div :class="[
            'inline-block max-w-[80%] rounded-2xl px-4 py-2.5 text-sm',
            msg.role === 'user' ? 'bg-violet-500 text-white rounded-br-md' : 'bg-slate-100 text-slate-700 rounded-bl-md'
          ]">
            {{ msg.content }}
          </div>
        </div>
        <div v-if="chatLoading" class="text-left">
          <div class="inline-block bg-slate-100 rounded-2xl rounded-bl-md px-4 py-2.5">
            <Loader2 class="w-4 h-4 animate-spin text-violet-500" />
          </div>
        </div>
      </div>

      <!-- Chat Input -->
      <div class="flex gap-2">
        <input 
          v-model="chatInput"
          @keyup.enter="sendChat"
          placeholder="..."
          class="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-100"
        />
        <button 
          @click="sendChat"
          :disabled="!chatInput.trim() || chatLoading"
          class="rounded-xl bg-violet-500 px-4 py-2.5 text-white hover:bg-violet-600 disabled:opacity-50 transition-colors"
        >
          <RefreshCw v-if="chatLoading" :size="18" class="animate-spin" />
          <span v-else class="text-sm font-medium">{{ $t('ai.send') }}</span>
        </button>
      </div>

      <!-- Suggestions -->
      <div v-if="chatSuggestions.length" class="mt-3 flex flex-wrap gap-2">
        <button 
          v-for="(s, i) in chatSuggestions" :key="i"
          @click="chatInput = s; sendChat()"
          class="text-xs px-3 py-1.5 bg-violet-50 text-violet-600 rounded-full hover:bg-violet-100 transition-colors"
        >
          {{ s }}
        </button>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
/**
 * AIAnalysisView.vue - AI Tahlil sahifasi
 * 
 * Real OpenAI integration:
 * - Davomat tahlili (real data from API)
 * - AI tavsiyalari (from OpenAI)
 * - AI Chat
 * - Trend va statistika
 */

import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import {
    AlertTriangle,
    BarChart3,
    BookOpen,
    CheckCircle,
    Clock,
    Lightbulb,
    Loader2,
    RefreshCw,
    Sparkles,
    Target,
    TrendingUp,
    XCircle
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const authStore = useAuthStore()
const toast = useToastStore()

const loading = ref(true)
const error = ref(null)
const isAnalyzing = ref(false)
const records = ref([])
const student = ref(null)

// AI state
const aiLoading = ref(false)
const aiError = ref(null)
const aiStrengths = ref([])
const aiAreas = ref([])
const aiRecommendations = ref([])
const aiRiskLevel = ref(null)
const aiPrediction = ref(null)
const aiMotivation = ref(null)
const aiSummary = ref('')

// Chat state
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatSuggestions = ref([])

// Load data from API
const loadAnalysisData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const profile = await api.getMe()
    student.value = profile
    
    const attendanceResponse = await api.getStudentAttendance(profile.id)
    records.value = (attendanceResponse.items || attendanceResponse || []).map(r => ({
      id: r.id,
      studentId: r.student_id,
      subject: r.subject || r.lesson_name || "Noma'lum",
      status: r.status,
      date: r.date
    }))
    
    // Load AI analysis in parallel (non-blocking)
    loadAIAnalysis()
  } catch (e) {
    console.error('Error loading analysis data:', e)
    error.value = "Ma'lumotlarni yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

// Load AI analysis from OpenAI
const loadAIAnalysis = async () => {
  if (!student.value?.id) return
  
  aiLoading.value = true
  aiError.value = null
  
  try {
    // Call both endpoints in parallel
    const [analysis, recs] = await Promise.all([
      api.aiAnalyzeStudent({ student_id: student.value.id }).catch(e => {
        console.error('AI analyze error:', e)
        return null
      }),
      api.aiStudentRecommendations(student.value.id).catch(e => {
        console.error('AI recommendations error:', e)
        return null
      })
    ])
    
    if (analysis) {
      aiSummary.value = analysis.summary || ''
      aiStrengths.value = analysis.strengths || []
      aiAreas.value = analysis.areas_for_improvement || []
      aiRecommendations.value = analysis.recommendations || []
      aiRiskLevel.value = analysis.risk_level || null
      aiPrediction.value = analysis.predicted_performance || null
    }
    
    if (recs) {
      aiMotivation.value = recs.motivation || null
      // Merge recommendations if analysis didn't return them
      if (!aiRecommendations.value.length && recs.recommendations) {
        aiRecommendations.value = recs.recommendations.map(r => typeof r === 'object' ? r.title || r.description : r)
      }
    }
    
    if (!analysis && !recs) {
      aiError.value = 'AI tahlil xizmati vaqtincha ishlamayapti'
    }
  } catch (e) {
    console.error('AI analysis error:', e)
    aiError.value = e?.detail || 'AI tahlil qilishda xatolik'
  } finally {
    aiLoading.value = false
  }
}

// AI Chat
const sendChat = async () => {
  const msg = chatInput.value.trim()
  if (!msg || chatLoading.value) return
  
  chatMessages.value.push({ role: 'user', content: msg })
  chatInput.value = ''
  chatLoading.value = true
  chatSuggestions.value = []
  
  try {
    const history = chatMessages.value.slice(-6).map(m => ({ role: m.role, content: m.content }))
    const result = await api.aiChat({
      message: msg,
      context: `Talaba: ${student.value?.name || ''}, Davomat: ${stats.value.rate}%`,
      conversation_history: history.slice(0, -1) // exclude current message
    })
    
    chatMessages.value.push({ role: 'assistant', content: result.response })
    chatSuggestions.value = result.suggestions || []
  } catch (e) {
    chatMessages.value.push({ role: 'assistant', content: 'Xatolik yuz berdi. Qayta urinib ko\'ring.' })
  } finally {
    chatLoading.value = false
  }
}

// Statistika (from real attendance data)
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

// Weekly data computed from real attendance records
const weeklyData = computed(() => {
  const now = new Date()
  const weeks = []
  for (let w = 3; w >= 0; w--) {
    const weekStart = new Date(now)
    weekStart.setDate(now.getDate() - (w * 7 + now.getDay()))
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 6)
    
    const weekRecords = records.value.filter(r => {
      const d = new Date(r.date)
      return d >= weekStart && d <= weekEnd
    })
    
    const total = weekRecords.length || 1
    const attended = weekRecords.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = Math.round((attended / total) * 100)
    
    weeks.push({ label: `${4 - w}-hafta`, rate: weekRecords.length ? rate : 0 })
  }
  return weeks
})

// AI summary title (uses AI data if available, fallback to computed)
const aiSummaryTitle = computed(() => {
  if (aiSummary.value) {
    if (stats.value.rate >= 90) return "Ajoyib natija! 🎉"
    if (stats.value.rate >= 75) return "Yaxshi davom etyapsiz! 👍"
    if (stats.value.rate >= 60) return "Yaxshilash imkoniyati bor 📈"
    return "E'tibor qarating! ⚠️"
  }
  if (stats.value.rate >= 90) return "Ajoyib natija! 🎉"
  if (stats.value.rate >= 75) return "Yaxshi davom etyapsiz! 👍"
  if (stats.value.rate >= 60) return "Yaxshilash imkoniyati bor 📈"
  return "E'tibor qarating! ⚠️"
})

// AI summary text (uses AI data if available)
const aiSummaryText = computed(() => {
  if (aiSummary.value) return aiSummary.value
  // Fallback
  return `Sizning davomatingiz ${stats.value.rate}% ni tashkil etadi. AI tahlil yuklanmoqda...`
})

// Risk level helpers
const riskLabel = computed(() => {
  const map = { low: 'Past ✅', medium: "O'rta ⚠️", high: 'Yuqori 🔴' }
  return map[aiRiskLevel.value] || aiRiskLevel.value
})

const riskBgClass = computed(() => {
  const map = { low: 'bg-emerald-50', medium: 'bg-amber-50', high: 'bg-rose-50' }
  return map[aiRiskLevel.value] || 'bg-slate-50'
})

const riskTextClass = computed(() => {
  const map = { low: 'text-emerald-700', medium: 'text-amber-700', high: 'text-rose-700' }
  return map[aiRiskLevel.value] || 'text-slate-700'
})

const riskSubTextClass = computed(() => {
  const map = { low: 'text-emerald-600', medium: 'text-amber-600', high: 'text-rose-600' }
  return map[aiRiskLevel.value] || 'text-slate-600'
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
  await loadAnalysisData()
  isAnalyzing.value = false
  toast.success('Tahlil yangilandi')
}

// Initialize
onMounted(() => {
  loadAnalysisData()
})
</script>
