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

    <!-- Error State -->
    <div v-else-if="errorMsg" class="relative py-8 text-center">
      <AlertTriangle class="w-10 h-10 text-amber-500 mx-auto mb-3" />
      <p class="text-slate-600">{{ errorMsg }}</p>
      <button @click="refreshAnalysis" class="mt-3 px-4 py-2 bg-violet-100 text-violet-600 rounded-xl text-sm hover:bg-violet-200 transition-colors">
        Qayta urinish
      </button>
    </div>

    <!-- Analysis Content -->
    <div v-else class="relative space-y-6">
      <!-- Summary Cards (metrics) -->
      <div v-if="metrics.length" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="(metric, index) in metrics"
          :key="index"
          class="bg-white/60 backdrop-blur-sm rounded-2xl p-4 border border-white/80"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-slate-500">{{ metric.label }}</span>
            <component :is="getMetricIcon(metric.type)" :class="['w-5 h-5', getMetricColor(metric.type)]" />
          </div>
          <p class="text-2xl font-bold text-slate-800">{{ metric.value }}</p>
          <div v-if="metric.trend !== undefined" class="mt-2 flex items-center gap-1">
            <TrendingUp v-if="metric.trend > 0" class="w-4 h-4 text-emerald-500" />
            <TrendingDown v-else class="w-4 h-4 text-rose-500" />
            <span :class="['text-sm font-medium', metric.trend > 0 ? 'text-emerald-600' : 'text-rose-600']">
              {{ Math.abs(metric.trend) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- AI Insights -->
      <div v-if="insights.length" class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
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
            <div :class="['flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center', getInsightTypeClass(insight.type)]">
              <component :is="getInsightIcon(insight.type)" class="w-4 h-4" />
            </div>
            <div>
              <p class="text-sm font-medium text-slate-700">{{ insight.title }}</p>
              <p class="text-sm text-slate-500 mt-0.5">{{ insight.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Text -->
      <div v-if="summaryText" class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
        <div class="flex items-center gap-2 mb-3">
          <Sparkles class="w-5 h-5 text-violet-500" />
          <h3 class="font-semibold text-slate-800">Xulosa</h3>
        </div>
        <p class="text-slate-600 leading-relaxed">{{ summaryText }}</p>
      </div>

      <!-- Recommendations -->
      <div v-if="recommendations.length" class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
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
              <p class="text-sm font-medium text-slate-700">{{ rec.title || rec }}</p>
              <p v-if="rec.description" class="text-xs text-slate-500 mt-1">{{ rec.description }}</p>
              <div v-if="rec.priority" class="mt-2">
                <span :class="[
                  'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                  rec.priority === 'high' ? 'bg-rose-100 text-rose-700' :
                  rec.priority === 'medium' ? 'bg-orange-100 text-orange-700' :
                  'bg-slate-100 text-slate-600'
                ]">
                  {{ rec.priority === 'high' ? 'Muhim' : rec.priority === 'medium' ? "O'rta" : 'Past' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Predictions -->
      <div v-if="predictions.length" class="bg-white/60 backdrop-blur-sm rounded-2xl p-5 border border-white/80">
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
                <Calendar class="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p class="text-sm font-medium text-slate-700">{{ pred.day || pred.title }}</p>
                <p class="text-xs text-slate-500">{{ pred.reason || pred.description }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-lg font-bold text-blue-600">{{ pred.predicted_rate || pred.value }}%</p>
              <p v-if="pred.confidence" class="text-xs text-slate-400">{{ pred.confidence }}% ishonch</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
    Activity, AlertTriangle,
    Award,
    Brain,
    Calendar,
    CheckCircle, Info,
    Lightbulb,
    Loader2,
    RefreshCw,
    Sparkles,
    TrendingDown,
    TrendingUp
} from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const props = defineProps({
  title: { type: String, default: 'Umumiy tahlil' },
  type: {
    type: String,
    default: 'student',
    validator: (value) => ['student', 'leader', 'admin'].includes(value)
  },
  studentId: { type: Number, default: null },
  groupId: { type: Number, default: null }
})

const isLoading = ref(true)
const errorMsg = ref(null)
const metrics = ref([])
const insights = ref([])
const recommendations = ref([])
const predictions = ref([])
const summaryText = ref('')

async function loadData() {
  isLoading.value = true
  errorMsg.value = null
  
  try {
    if (props.type === 'student' && props.studentId) {
      await loadStudentData()
    } else if (props.type === 'leader' && props.groupId) {
      await loadLeaderData()
    } else if (props.type === 'admin') {
      await loadAdminData()
    } else {
      // Fallback: dashboard insights
      await loadAdminData()
    }
  } catch (e) {
    console.error('AI Analysis error:', e)
    errorMsg.value = e?.detail || e?.message || 'AI tahlil qilishda xatolik yuz berdi'
  } finally {
    isLoading.value = false
  }
}

async function loadStudentData() {
  // Parallel: analysis + recommendations + prediction
  const [analysis, recs, prediction] = await Promise.all([
    api.aiAnalyzeStudent({ student_id: props.studentId }),
    api.aiStudentRecommendations(props.studentId).catch(() => null),
    api.aiPredictAttendance({ student_id: props.studentId, days_ahead: 7 }).catch(() => null)
  ])
  
  summaryText.value = analysis.summary || ''
  
  // Risk level as metric
  const riskMap = { low: 'Past', medium: "O'rta", high: 'Yuqori' }
  metrics.value = [
    { label: 'Xavf darajasi', value: riskMap[analysis.risk_level] || analysis.risk_level, type: analysis.risk_level === 'low' ? 'attendance' : 'warning' },
  ]
  
  if (analysis.context_data?.attendance) {
    const att = analysis.context_data.attendance
    metrics.value.push(
      { label: 'Davomat', value: att.rate + '%', type: 'attendance', trend: null },
      { label: 'Kelgan / Jami', value: `${att.present}/${att.total}`, type: 'info' }
    )
  }
  
  // Strengths & areas as insights
  insights.value = [
    ...(analysis.strengths || []).map(s => ({ type: 'positive', title: s, description: '' })),
    ...(analysis.areas_for_improvement || []).map(s => ({ type: 'warning', title: s, description: '' }))
  ]
  
  // Recommendations
  if (recs) {
    recommendations.value = (recs.recommendations || []).map(r => typeof r === 'string' ? { title: r } : r)
  } else {
    recommendations.value = (analysis.recommendations || []).map(r => typeof r === 'string' ? { title: r } : r)
  }
  
  // Predictions
  if (prediction && prediction.predictions) {
    predictions.value = prediction.predictions
  }
}

async function loadLeaderData() {
  const [groupAnalysis, prediction] = await Promise.all([
    api.aiAnalyzeGroup({ group_id: props.groupId }),
    api.aiPredictAttendance({ group_id: props.groupId, days_ahead: 7 }).catch(() => null)
  ])
  
  summaryText.value = groupAnalysis.summary || ''
  
  metrics.value = [
    { label: 'O\'rtacha davomat', value: groupAnalysis.average_attendance + '%', type: 'attendance' },
    { label: 'Yaxshi talabalar', value: (groupAnalysis.top_performers || []).length, type: 'info' },
    { label: 'Xavf zonasi', value: (groupAnalysis.at_risk_students || []).length, type: 'warning' }
  ]
  
  insights.value = [
    ...(groupAnalysis.trends || []).map(t => ({ type: 'info', title: t, description: '' })),
    ...(groupAnalysis.top_performers || []).slice(0, 3).map(s => ({ type: 'positive', title: `${s.name}: ${s.rate}%`, description: 'Yaxshi davomat' })),
    ...(groupAnalysis.at_risk_students || []).slice(0, 3).map(s => ({ type: 'negative', title: `${s.name}: ${s.rate}%`, description: 'Past davomat - diqqat talab qiladi' }))
  ]
  
  recommendations.value = (groupAnalysis.recommendations || []).map(r => typeof r === 'string' ? { title: r } : r)
  
  if (prediction && prediction.predictions) {
    predictions.value = prediction.predictions
  }
}

async function loadAdminData() {
  const dashInsights = await api.aiDashboardInsights()
  
  summaryText.value = dashInsights.summary || ''
  
  metrics.value = (dashInsights.metrics || []).map(m => ({
    label: m.label,
    value: m.value,
    type: m.type || 'info',
    trend: m.trend
  }))
  
  insights.value = (dashInsights.insights || []).map(i => ({
    type: i.type || 'info',
    title: i.title,
    description: i.description
  }))
  
  recommendations.value = (dashInsights.recommendations || []).map(r => typeof r === 'string' ? { title: r } : r)
}

function refreshAnalysis() {
  loadData()
}

function getMetricIcon(type) {
  const map = { attendance: CheckCircle, warning: AlertTriangle, info: Info, performance: Award }
  return map[type] || Info
}

function getMetricColor(type) {
  const map = { attendance: 'text-emerald-500', warning: 'text-amber-500', info: 'text-blue-500', performance: 'text-violet-500' }
  return map[type] || 'text-blue-500'
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
  const icons = { positive: CheckCircle, warning: AlertTriangle, negative: AlertTriangle, info: Info }
  return icons[type] || Info
}

onMounted(() => {
  loadData()
})
</script>
