<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="relative">
        <div class="w-16 h-16 rounded-full border-4 border-emerald-200 border-t-emerald-500 animate-spin"></div>
        <Brain class="w-7 h-7 text-emerald-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
      </div>
      <p class="mt-4 text-slate-600 font-medium">{{ $t('ai.analyzing') }}</p>
    </div>

    <!-- Paywall / Upgrade Required -->
    <div v-else-if="!hasAIAccess" class="flex items-center justify-center py-12 px-4">
      <div class="max-w-lg w-full bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
        <!-- Top gradient banner -->
        <div class="bg-gradient-to-br from-emerald-500 via-teal-500 to-emerald-600 px-6 py-10 text-center relative">
          <div class="absolute inset-0 opacity-10">
            <div class="absolute top-4 left-8 w-20 h-20 border-2 border-white rounded-full"></div>
            <div class="absolute bottom-6 right-10 w-14 h-14 border-2 border-white rounded-full"></div>
            <div class="absolute top-10 right-20 w-8 h-8 border border-white rounded-full"></div>
          </div>
          <div class="relative z-10">
            <div class="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <Lock class="w-10 h-10 text-white" />
            </div>
            <h2 class="text-2xl font-bold text-white mb-2">{{ $t('ai.noAccess') }}</h2>
            <p class="text-emerald-100 text-sm leading-relaxed">{{ $t('ai.upgradeRequiredDesc') }}</p>
          </div>
        </div>
        <!-- Content -->
        <div class="px-6 py-8 space-y-6">
          <!-- Current plan badge -->
          <div v-if="currentPlan" class="flex items-center justify-center gap-2">
            <span class="text-sm text-slate-500">{{ $t('ai.yourCurrentPlan') }}:</span>
            <span class="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-sm font-semibold uppercase">{{ currentPlan }}</span>
          </div>
          <!-- Required plans -->
          <div class="bg-emerald-50 border border-emerald-100 rounded-2xl p-5">
            <div class="flex items-center gap-2 mb-3">
              <Crown class="w-5 h-5 text-emerald-600" />
              <span class="font-semibold text-slate-700 text-sm">{{ $t('ai.availableInPlans') }}</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span v-for="plan in requiredPlans" :key="plan"
                class="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl text-sm font-bold uppercase shadow-sm">
                {{ plan }}
              </span>
            </div>
          </div>
          <!-- Features list -->
          <div class="space-y-3">
            <p class="text-sm font-medium text-slate-600">{{ $t('ai.whatYouGet') }}:</p>
            <div class="grid gap-2">
              <div class="flex items-center gap-2 text-sm text-slate-600">
                <Brain class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span>{{ $t('ai.featureAnalysis') }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm text-slate-600">
                <Sparkles class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span>{{ $t('ai.featurePrediction') }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm text-slate-600">
                <MessageCircle class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span>{{ $t('ai.featureChat') }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm text-slate-600">
                <Lightbulb class="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span>{{ $t('ai.featureRecommendations') }}</span>
              </div>
            </div>
          </div>
          <!-- CTA button -->
          <button @click="router.push(subscriptionRoute)"
            class="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-bold rounded-2xl transition-all shadow-lg shadow-emerald-200 hover:shadow-emerald-300 text-sm flex items-center justify-center gap-2">
            <Zap class="w-5 h-5" />
            {{ $t('ai.upgradePlan') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
      <AlertTriangle class="w-10 h-10 text-red-400 mx-auto mb-3" />
      <p class="text-red-600 font-medium">{{ error }}</p>
      <button @click="initData" class="mt-4 px-5 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-xl transition-colors text-sm font-medium">
        {{ $t('common.retry') }}
      </button>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('ai.title') }}</h1>
          <p class="text-sm text-slate-500 mt-1">{{ $t('ai.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-2">
          <!-- Health indicator -->
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
               :class="aiHealthy ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">
            <div class="w-2 h-2 rounded-full" :class="aiHealthy ? 'bg-emerald-500' : 'bg-amber-500'"></div>
            {{ aiHealthy ? $t('ai.aiActive') : $t('ai.aiInactive') }}
          </div>
          <button
            @click="refreshAll"
            :disabled="isRefreshing"
            class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-2.5 text-white text-sm font-medium transition-all hover:from-emerald-600 hover:to-teal-700 disabled:opacity-50 shadow-lg shadow-emerald-500/20"
          >
            <RefreshCw :size="16" :class="{ 'animate-spin': isRefreshing }" />
            <span class="hidden sm:inline">{{ $t('common.refresh') }}</span>
          </button>
        </div>
      </div>

      <!-- AI Usage Limit Card -->
      <div v-if="aiUsage" class="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center"
                 :class="aiUsage.is_limit_reached ? 'bg-rose-100' : aiUsage.percentage_used >= 80 ? 'bg-amber-100' : 'bg-emerald-100'">
              <Zap :size="20"
                      :class="aiUsage.is_limit_reached ? 'text-rose-600' : aiUsage.percentage_used >= 80 ? 'text-amber-600' : 'text-emerald-600'" />
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-sm font-semibold text-slate-700">{{ $t('ai.usageLimit') }}</h3>
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                      :class="aiUsage.is_limit_reached ? 'bg-rose-100 text-rose-700' : aiUsage.percentage_used >= 80 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'">
                  {{ aiUsage.is_limit_reached ? $t('ai.limitReached') : Math.round(aiUsage.percentage_used) + '%' }}
                </span>
              </div>
              <p class="text-xs text-slate-500 mt-0.5">
                {{ aiUsage.request_count }} / {{ aiUsage.max_requests || '—' }} {{ $t('ai.requests') }}
              </p>
            </div>
          </div>
          <div class="w-full sm:flex-1 sm:max-w-xs">
            <div class="h-2.5 overflow-hidden rounded-full bg-slate-100">
              <div class="h-full rounded-full transition-all duration-700"
                   :class="aiUsage.is_limit_reached ? 'bg-rose-500' : aiUsage.percentage_used >= 80 ? 'bg-amber-500' : 'bg-emerald-500'"
                   :style="{ width: Math.min(100, aiUsage.percentage_used) + '%' }"></div>
            </div>
            <div class="flex justify-between mt-1">
              <span class="text-xs text-slate-400">0</span>
              <span class="text-xs font-medium" :class="aiUsage.is_limit_reached ? 'text-rose-500' : 'text-slate-500'">
                {{ aiUsage.remaining_requests || 0 }} {{ $t('ai.requestsLeft') }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Limit Reached Banner -->
      <div v-if="aiUsage?.is_limit_reached" class="bg-rose-50 border border-rose-200 rounded-xl sm:rounded-2xl p-3 sm:p-4 flex items-start gap-2.5 sm:gap-3">
        <Zap :size="20" class="text-rose-500 mt-0.5 flex-shrink-0" />
        <div>
          <p class="text-sm font-semibold text-rose-700">{{ $t('ai.limitReachedTitle') }}</p>
          <p class="text-xs text-rose-600 mt-0.5">{{ $t('ai.limitReachedDesc') }}</p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex flex-wrap gap-1 p-1 bg-slate-100 rounded-xl overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-4 py-2 sm:py-2.5 rounded-lg text-xs sm:text-sm font-medium transition-all"
          :class="activeTab === tab.key
            ? 'bg-white text-emerald-700 shadow-sm'
            : 'text-slate-500 hover:text-slate-700 hover:bg-white/50'"
        >
          <component :is="tab.icon" :size="16" />
          <span class="hidden sm:inline">{{ tab.label }}</span>
        </button>
      </div>

      <!-- ====== TAB: OVERVIEW ====== -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Start AI Analysis Button (shown when not yet analyzed) -->
        <div v-if="!aiAnalysisLoaded && !aiAnalysisLoading" class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-8 shadow-sm text-center">
          <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center mx-auto mb-3 sm:mb-4">
            <Brain :size="28" class="text-emerald-600 sm:hidden" />
            <Brain :size="32" class="text-emerald-600 hidden sm:block" />
          </div>
          <h3 class="text-base sm:text-lg font-bold text-slate-800 mb-1.5 sm:mb-2">{{ $t('ai.startAnalysisTitle') }}</h3>
          <p class="text-xs sm:text-sm text-slate-500 mb-1">{{ $t('ai.startAnalysisDesc') }}</p>
          <p class="text-xs text-slate-400 mb-4 sm:mb-5">{{ $t('ai.startAnalysisCost') }}</p>
          <button
            @click="startAIAnalysis"
            :disabled="aiUsage?.is_limit_reached"
            class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-teal-700 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Sparkles :size="18" />
            {{ $t('ai.startAnalysis') }}
          </button>
        </div>

        <!-- AI Analysis Loading -->
        <div v-if="aiAnalysisLoading" class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-12 shadow-sm text-center">
          <div class="relative mx-auto w-16 h-16 mb-4">
            <div class="w-16 h-16 rounded-full border-4 border-emerald-200 border-t-emerald-500 animate-spin"></div>
            <Brain class="w-7 h-7 text-emerald-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
          </div>
          <p class="text-slate-600 font-medium">{{ $t('ai.analyzing') }}</p>
          <p class="text-xs text-slate-400 mt-1">{{ $t('ai.analysisTakesTime') }}</p>
        </div>

        <!-- AI Summary Card (shown after analysis) -->
        <div v-if="aiAnalysisLoaded && !aiAnalysisLoading" class="rounded-2xl bg-gradient-to-br from-emerald-500 via-emerald-600 to-teal-700 p-4 sm:p-6 text-white shadow-xl relative overflow-hidden">
          <div class="absolute -top-10 -right-10 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
          <div class="absolute -bottom-10 -left-10 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
          <div class="relative flex items-start gap-3 sm:gap-4">
            <div class="flex h-11 w-11 sm:h-14 sm:w-14 items-center justify-center rounded-xl sm:rounded-2xl bg-white/20 backdrop-blur flex-shrink-0">
              <Sparkles :size="22" class="sm:hidden" />
              <Sparkles :size="28" class="hidden sm:block" />
            </div>
            <div class="flex-1 min-w-0">
              <h2 class="text-lg sm:text-xl font-bold">{{ summaryTitle }}</h2>
              <p class="mt-1.5 sm:mt-2 text-emerald-100 leading-relaxed text-xs sm:text-sm">{{ summaryText }}</p>
            </div>
          </div>

          <!-- Stats Row -->
          <div class="relative mt-4 sm:mt-6 grid gap-2" :class="isStudentRole ? 'grid-cols-3' : 'grid-cols-2 sm:grid-cols-4'">
            <div v-for="stat in headerStats" :key="stat.label" class="rounded-xl bg-white/10 p-2 sm:p-3 backdrop-blur text-center">
              <p class="text-lg sm:text-2xl font-bold">{{ stat.value }}</p>
              <p class="text-[10px] sm:text-xs text-emerald-200 mt-0.5 leading-tight">{{ stat.label }}</p>
            </div>
          </div>
        </div>

        <!-- Quick Metrics (after analysis) -->
        <div v-if="aiAnalysisLoaded" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="metric in metrics" :key="metric.label"
               class="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-slate-500">{{ metric.label }}</span>
              <div class="w-9 h-9 rounded-lg flex items-center justify-center" :class="metric.iconBg">
                <component :is="metric.icon" :size="18" :class="metric.iconColor" />
              </div>
            </div>
            <p class="text-2xl font-bold text-slate-800">{{ metric.value }}</p>
            <div v-if="metric.trend !== null && metric.trend !== undefined" class="mt-2 flex items-center gap-1">
              <TrendingUp v-if="metric.trend > 0" :size="14" class="text-emerald-500" />
              <TrendingDown v-else-if="metric.trend < 0" :size="14" class="text-rose-500" />
              <Minus v-else :size="14" class="text-slate-400" />
              <span class="text-xs font-medium" :class="metric.trend > 0 ? 'text-emerald-600' : metric.trend < 0 ? 'text-rose-600' : 'text-slate-400'">
                {{ metric.trend > 0 ? '+' : '' }}{{ metric.trend }}%
              </span>
            </div>
          </div>
        </div>

        <!-- AI Insights -->
        <div v-if="aiAnalysisLoaded && insights.length" class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-4">
            <Brain :size="20" class="text-emerald-600" />
            <h3 class="font-semibold text-slate-800">{{ $t('ai.aiInsights') }}</h3>
          </div>
          <div class="space-y-3">
            <div v-for="(insight, i) in insights" :key="i"
                 class="flex items-start gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors">
              <div class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center" :class="getInsightClass(insight.type)">
                <component :is="getInsightIcon(insight.type)" :size="16" />
              </div>
              <div class="min-w-0">
                <p class="text-sm font-medium text-slate-700">{{ insight.title }}</p>
                <p v-if="insight.description" class="text-xs text-slate-500 mt-0.5">{{ insight.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div v-if="aiAnalysisLoaded && recommendations.length" class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-4">
            <Lightbulb :size="20" class="text-amber-500" />
            <h3 class="font-semibold text-slate-800">{{ $t('ai.aiRecommendations') }}</h3>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 sm:gap-3">
            <div v-for="(rec, i) in recommendations" :key="i"
                 class="flex items-start gap-2.5 sm:gap-3 p-3 sm:p-4 bg-amber-50 rounded-xl border border-amber-100">
              <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
                <span class="text-amber-600 text-sm font-bold">{{ i + 1 }}</span>
              </div>
              <div>
                <p class="text-sm font-medium text-slate-700">{{ typeof rec === 'string' ? rec : rec.title }}</p>
                <p v-if="rec.description" class="text-xs text-slate-500 mt-1">{{ rec.description }}</p>
                <span v-if="rec.priority" class="inline-flex items-center mt-1.5 px-2 py-0.5 rounded-full text-xs font-medium"
                      :class="rec.priority === 'high' ? 'bg-rose-100 text-rose-700' : rec.priority === 'medium' ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-600'">
                  {{ rec.priority === 'high' ? $t('ai.highPriority') : rec.priority === 'medium' ? $t('ai.mediumPriority') : $t('ai.lowPriority') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ====== TAB: ATTENDANCE ====== -->
      <div v-if="activeTab === 'attendance'" class="space-y-6">
        <!-- Attendance Overview -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Attendance Stats -->
          <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                <TrendingUp :size="20" class="text-emerald-600" />
              </div>
              <div>
                <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ $t('ai.attendanceAnalysis') }}</h3>
                <p class="text-xs sm:text-sm text-slate-500">{{ $t('ai.last30days') }}</p>
              </div>
            </div>

            <!-- Overall Progress -->
            <div class="rounded-xl bg-slate-50 p-4 mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-slate-600 text-sm">{{ $t('ai.overallAttendance') }}</span>
                <span class="font-semibold text-slate-800">{{ attendanceRate }}%</span>
              </div>
              <div class="h-3 overflow-hidden rounded-full bg-slate-200">
                <div class="h-full rounded-full transition-all duration-700"
                     :class="getProgressColor(attendanceRate)"
                     :style="{ width: attendanceRate + '%' }"></div>
              </div>
            </div>

            <!-- Status Breakdown -->
            <div class="space-y-2">
              <div class="flex items-center justify-between p-3 rounded-lg bg-emerald-50">
                <div class="flex items-center gap-2">
                  <CheckCircle :size="18" class="text-emerald-600" />
                  <span class="text-emerald-700 text-sm">{{ $t('attendance.present') }}</span>
                </div>
                <span class="font-semibold text-emerald-700">{{ attStats.present }} {{ $t('ai.lessons') }}</span>
              </div>
              <div class="flex items-center justify-between p-3 rounded-lg bg-amber-50">
                <div class="flex items-center gap-2">
                  <Clock :size="18" class="text-amber-600" />
                  <span class="text-amber-700 text-sm">{{ $t('attendance.late') }}</span>
                </div>
                <span class="font-semibold text-amber-700">{{ attStats.late }} {{ $t('ai.lessons') }}</span>
              </div>
              <div class="flex items-center justify-between p-3 rounded-lg bg-rose-50">
                <div class="flex items-center gap-2">
                  <XCircle :size="18" class="text-rose-600" />
                  <span class="text-rose-700 text-sm">{{ $t('attendance.absent') }}</span>
                </div>
                <span class="font-semibold text-rose-700">{{ attStats.absent }} {{ $t('ai.lessons') }}</span>
              </div>
              <div class="flex items-center justify-between p-3 rounded-lg bg-blue-50">
                <div class="flex items-center gap-2">
                  <Info :size="18" class="text-blue-600" />
                  <span class="text-blue-700 text-sm">{{ $t('ai.excused') }}</span>
                </div>
                <span class="font-semibold text-blue-700">{{ attStats.excused }} {{ $t('ai.lessons') }}</span>
              </div>
            </div>
          </div>

          <!-- Subject Stats (Student) / Student List (Leader/Admin) -->
          <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                <BookOpen :size="20" class="text-blue-600" />
              </div>
              <div>
                <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ isStudentRole ? $t('ai.bySubjects') : $t('ai.byStudents') }}</h3>
                <p class="text-xs sm:text-sm text-slate-500">{{ $t('ai.attendanceDistribution') }}</p>
              </div>
            </div>

            <div v-if="subjectStats.length" class="space-y-3 max-h-80 overflow-y-auto pr-1">
              <div v-for="item in subjectStats" :key="item.name" class="rounded-xl bg-slate-50 p-3">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="font-medium text-slate-700 text-sm truncate mr-2">{{ item.name }}</span>
                  <span class="text-sm font-semibold flex-shrink-0" :class="getTextColor(item.rate)">{{ item.rate }}%</span>
                </div>
                <div class="h-2 overflow-hidden rounded-full bg-slate-200">
                  <div class="h-full rounded-full transition-all duration-500"
                       :class="getProgressColor(item.rate)"
                       :style="{ width: item.rate + '%' }"></div>
                </div>
              </div>
            </div>
            <div v-else class="py-8 text-center text-slate-400 text-sm">
              {{ $t('ai.noData') }}
            </div>
          </div>
        </div>

        <!-- Weekly Trend -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
              <BarChart3 :size="20" class="text-indigo-600" />
            </div>
            <div>
              <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ $t('ai.weeklyTrend') }}</h3>
              <p class="text-xs sm:text-sm text-slate-500">{{ $t('ai.last4weeks') }}</p>
            </div>
          </div>
          <div class="flex items-end justify-between gap-2 sm:gap-4 h-32 sm:h-40 mt-4 sm:mt-6">
            <div v-for="week in weeklyData" :key="week.label" class="flex-1 flex flex-col items-center gap-2">
              <div class="w-full bg-slate-100 rounded-t-lg relative" style="height: 120px;">
                <div class="absolute bottom-0 left-0 right-0 rounded-t-lg transition-all duration-700"
                     :class="getProgressColor(week.rate)"
                     :style="{ height: (week.rate || 1) + '%' }"></div>
              </div>
              <span class="text-xs text-slate-500">{{ week.label }}</span>
              <span class="text-sm font-semibold text-slate-700">{{ week.rate }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ====== TAB: PREDICTIONS ====== -->
      <div v-if="activeTab === 'predictions'" class="space-y-6">
        <!-- Prediction Loading -->
        <div v-if="predictionLoading" class="bg-white rounded-2xl border border-slate-200 p-12 shadow-sm text-center">
          <Loader2 class="w-8 h-8 animate-spin text-emerald-500 mx-auto mb-3" />
          <p class="text-slate-500">{{ $t('ai.generatingPrediction') }}</p>
        </div>

        <template v-else>
          <!-- Prediction Button -->
          <div v-if="!predictions.length" class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-8 shadow-sm text-center">
            <Activity :size="40" class="text-emerald-300 mx-auto mb-3 sm:mb-4" />
            <h3 class="text-base sm:text-lg font-semibold text-slate-700 mb-2">{{ $t('ai.attendancePrediction') }}</h3>
            <p class="text-xs sm:text-sm text-slate-500 mb-4">{{ $t('ai.predictionDesc') }}</p>
            <button @click="loadPredictions"
                    class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-teal-700 transition-all shadow-lg shadow-emerald-500/20">
              {{ $t('ai.generatePrediction') }}
            </button>
          </div>

          <!-- Predictions List -->
          <div v-else class="space-y-4">
            <!-- Overall Prediction -->
            <div v-if="predictionSummary" class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200 p-4 sm:p-6">
              <div class="flex items-center gap-2 mb-3">
                <Activity :size="20" class="text-blue-600" />
                <h3 class="font-semibold text-slate-800">{{ $t('ai.overallPrediction') }}</h3>
              </div>
              <p class="text-slate-600 text-sm leading-relaxed">{{ predictionSummary }}</p>
              <div v-if="predictionConfidence" class="mt-3 flex flex-wrap items-center gap-2">
                <span class="text-xs text-slate-500">{{ $t('ai.confidence') }}:</span>
                <div class="flex-1 h-2 bg-blue-100 rounded-full max-w-32 sm:max-w-48">
                  <div class="h-full bg-blue-500 rounded-full transition-all" :style="{ width: predictionConfidence + '%' }"></div>
                </div>
                <span class="text-xs font-medium text-blue-600">{{ predictionConfidence }}%</span>
              </div>
            </div>

            <!-- Day-by-day Predictions -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3">
              <div v-for="(pred, i) in predictions" :key="i"
                   class="bg-white rounded-xl border border-slate-200 p-3 sm:p-4 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-1.5 sm:mb-2">
                  <div class="flex items-center gap-1.5 sm:gap-2 min-w-0 flex-1 mr-2">
                    <Calendar :size="14" class="text-blue-500 flex-shrink-0" />
                    <span class="font-medium text-slate-700 text-xs sm:text-sm truncate">{{ pred.day || pred.title }}</span>
                  </div>
                  <span class="text-base sm:text-lg font-bold flex-shrink-0" :class="getTextColor(pred.predicted_rate || pred.value)">
                    {{ pred.predicted_rate || pred.value }}%
                  </span>
                </div>
                <p v-if="pred.reason || pred.description" class="text-xs text-slate-500 line-clamp-2">{{ pred.reason || pred.description }}</p>
              </div>
            </div>

            <!-- Factors -->
            <div v-if="predictionFactors.length" class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
              <div class="flex items-center gap-2 mb-3">
                <Target :size="18" class="text-emerald-600" />
                <h4 class="font-semibold text-slate-800 text-sm">{{ $t('ai.keyFactors') }}</h4>
              </div>
              <div class="space-y-2">
                <div v-for="(factor, i) in predictionFactors" :key="i"
                     class="flex items-center gap-2 text-sm text-slate-600">
                  <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0"></div>
                  {{ factor }}
                </div>
              </div>
            </div>

            <!-- Regenerate -->
            <div class="text-center">
              <button @click="loadPredictions"
                      class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
                {{ $t('ai.regenerate') }}
              </button>
            </div>
          </div>
        </template>
      </div>

      <!-- ====== TAB: CHAT ====== -->
      <div v-if="activeTab === 'chat'" class="space-y-4">
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Sparkles :size="20" class="text-white" />
            </div>
            <div>
              <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ $t('ai.aiAssistant') }}</h3>
              <p class="text-xs sm:text-sm text-slate-500">{{ $t('ai.askQuestion') }}</p>
            </div>
          </div>

          <!-- Chat Messages -->
          <div ref="chatContainer" class="space-y-3 mb-4 max-h-96 overflow-y-auto scroll-smooth" v-if="chatMessages.length">
            <div v-for="(msg, i) in chatMessages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
              <div :class="[
                'inline-block max-w-[92%] sm:max-w-[85%] rounded-2xl px-3 sm:px-4 py-2 sm:py-2.5 text-sm leading-relaxed',
                msg.role === 'user'
                  ? 'bg-emerald-500 text-white rounded-br-md'
                  : 'bg-slate-100 text-slate-700 rounded-bl-md'
              ]">
                <div v-if="msg.role === 'assistant'" class="whitespace-pre-wrap">{{ msg.content }}</div>
                <template v-else>{{ msg.content }}</template>
              </div>
            </div>
            <div v-if="chatLoading" class="text-left">
              <div class="inline-flex items-center gap-2 bg-slate-100 rounded-2xl rounded-bl-md px-4 py-2.5">
                <Loader2 class="w-4 h-4 animate-spin text-emerald-500" />
                <span class="text-xs text-slate-500">{{ $t('ai.thinking') }}</span>
              </div>
            </div>
          </div>

          <!-- Empty Chat -->
          <div v-else class="py-8 text-center">
            <MessageCircle :size="40" class="text-slate-200 mx-auto mb-3" />
            <p class="text-sm text-slate-400">{{ $t('ai.startConversation') }}</p>
            <!-- Initial suggestions -->
            <div class="mt-4 flex flex-wrap justify-center gap-2">
              <button v-for="s in defaultSuggestions" :key="s"
                      @click="chatInput = s; sendChat()"
                      class="text-xs px-3 py-1.5 bg-emerald-50 text-emerald-600 rounded-full hover:bg-emerald-100 transition-colors">
                {{ s }}
              </button>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="flex gap-2">
            <input
              v-model="chatInput"
              @keyup.enter="sendChat"
              :placeholder="$t('ai.chatPlaceholder')"
              class="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-100 transition-colors"
            />
            <button
              @click="sendChat"
              :disabled="!chatInput.trim() || chatLoading"
              class="rounded-xl bg-emerald-500 px-4 py-2.5 text-white hover:bg-emerald-600 disabled:opacity-50 transition-colors flex-shrink-0"
            >
              <Loader2 v-if="chatLoading" :size="18" class="animate-spin" />
              <Send v-else :size="18" />
            </button>
          </div>

          <!-- Suggestions -->
          <div v-if="chatSuggestions.length" class="mt-3 flex flex-wrap gap-2">
            <button v-for="(s, i) in chatSuggestions" :key="i"
                    @click="chatInput = s; sendChat()"
                    class="text-xs px-3 py-1.5 bg-emerald-50 text-emerald-600 rounded-full hover:bg-emerald-100 transition-colors">
              {{ s }}
            </button>
          </div>
        </div>
      </div>

      <!-- ====== TAB: GROUP ANALYSIS (Leader/Admin/Super only) ====== -->
      <div v-if="activeTab === 'group' && !isStudentRole" class="space-y-6">
        <!-- Group Analysis Loading -->
        <div v-if="groupAnalysisLoading" class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-12 shadow-sm text-center">
          <Loader2 class="w-8 h-8 animate-spin text-emerald-500 mx-auto mb-3" />
          <p class="text-slate-500">{{ $t('ai.analyzingGroup') }}</p>
        </div>

        <template v-else-if="groupAnalysis">
          <!-- Group Summary -->
          <div class="bg-gradient-to-r from-teal-50 to-emerald-50 rounded-2xl border border-emerald-200 p-4 sm:p-6">
            <div class="flex items-center gap-2 mb-3">
              <UsersIcon :size="20" class="text-emerald-600" />
              <h3 class="font-semibold text-slate-800">{{ $t('ai.groupSummary') }}</h3>
            </div>
            <p class="text-slate-600 text-sm leading-relaxed">{{ groupAnalysis.summary }}</p>
            <div class="mt-3 sm:mt-4 flex flex-wrap items-center gap-2 sm:gap-4">
              <div class="flex items-center gap-2">
                <span class="text-xs sm:text-sm text-slate-500">{{ $t('ai.avgAttendance') }}:</span>
                <span class="font-bold text-base sm:text-lg" :class="getTextColor(groupAnalysis.average_attendance)">
                  {{ groupAnalysis.average_attendance }}%
                </span>
              </div>
            </div>
          </div>

          <!-- Top Performers & At Risk -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            <!-- Top Performers -->
            <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
              <div class="flex items-center gap-2 mb-4">
                <Award :size="20" class="text-yellow-500" />
                <h3 class="font-semibold text-slate-800">{{ $t('ai.topPerformers') }}</h3>
              </div>
              <div class="space-y-2">
                <div v-for="(s, i) in groupAnalysis.top_performers || []" :key="i"
                     class="flex items-center gap-3 p-3 rounded-lg bg-emerald-50">
                  <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm"
                       :class="i === 0 ? 'bg-yellow-400 text-yellow-900' : i === 1 ? 'bg-slate-300 text-slate-700' : 'bg-orange-300 text-orange-800'">
                    {{ i + 1 }}
                  </div>
                  <span class="flex-1 text-sm font-medium text-slate-700 truncate">{{ s.name }}</span>
                  <span class="text-sm font-bold text-emerald-600">{{ s.rate }}%</span>
                </div>
                <div v-if="!groupAnalysis.top_performers?.length" class="py-4 text-center text-slate-400 text-sm">
                  {{ $t('ai.noData') }}
                </div>
              </div>
            </div>

            <!-- At Risk -->
            <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
              <div class="flex items-center gap-2 mb-4">
                <AlertTriangle :size="20" class="text-rose-500" />
                <h3 class="font-semibold text-slate-800">{{ $t('ai.atRiskStudents') }}</h3>
              </div>
              <div class="space-y-2">
                <div v-for="(s, i) in groupAnalysis.at_risk_students || []" :key="i"
                     class="flex items-center gap-3 p-3 rounded-lg bg-rose-50">
                  <div class="flex-shrink-0 w-8 h-8 rounded-full bg-rose-200 flex items-center justify-center">
                    <span class="text-rose-700 text-xs font-medium">{{ s.name?.charAt(0) }}</span>
                  </div>
                  <span class="flex-1 text-sm font-medium text-slate-700 truncate">{{ s.name }}</span>
                  <span class="text-sm font-bold text-rose-600">{{ s.rate }}%</span>
                </div>
                <div v-if="!groupAnalysis.at_risk_students?.length" class="py-4 text-center text-slate-400 text-sm">
                  {{ $t('ai.noAtRisk') }}
                </div>
              </div>
            </div>
          </div>

          <!-- Group Trends -->
          <div v-if="groupAnalysis.trends?.length" class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
            <div class="flex items-center gap-2 mb-4">
              <TrendingUp :size="20" class="text-indigo-600" />
              <h3 class="font-semibold text-slate-800">{{ $t('ai.trends') }}</h3>
            </div>
            <div class="space-y-2">
              <div v-for="(trend, i) in groupAnalysis.trends" :key="i"
                   class="flex items-center gap-2 text-sm text-slate-600 p-2 rounded-lg hover:bg-slate-50">
                <div class="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0"></div>
                {{ trend }}
              </div>
            </div>
          </div>

          <!-- Group Recommendations -->
          <div v-if="groupAnalysis.recommendations?.length" class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
            <div class="flex items-center gap-2 mb-4">
              <Lightbulb :size="20" class="text-amber-500" />
              <h3 class="font-semibold text-slate-800">{{ $t('ai.groupRecommendations') }}</h3>
            </div>
            <div class="space-y-2">
              <div v-for="(rec, i) in groupAnalysis.recommendations" :key="i"
                   class="flex items-start gap-3 p-3 bg-amber-50 rounded-xl border border-amber-100">
                <div class="flex-shrink-0 w-7 h-7 rounded-lg bg-amber-100 flex items-center justify-center">
                  <span class="text-amber-600 text-xs font-bold">{{ i + 1 }}</span>
                </div>
                <p class="text-sm text-slate-600">{{ typeof rec === 'string' ? rec : rec.title }}</p>
              </div>
            </div>
          </div>

          <!-- Re-analyze button -->
          <div class="text-center">
            <button @click="loadGroupAnalysis"
                    class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
              {{ $t('ai.reanalyze') }}
            </button>
          </div>
        </template>

        <!-- No Group -->
        <div v-else class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-8 shadow-sm text-center">
          <UsersIcon :size="40" class="text-slate-200 mx-auto mb-3 sm:mb-4" />
          <h3 class="text-base sm:text-lg font-semibold text-slate-700 mb-2">{{ $t('ai.groupAnalysis') }}</h3>
          <p class="text-xs sm:text-sm text-slate-500 mb-4">{{ $t('ai.groupAnalysisDesc') }}</p>
          <button @click="loadGroupAnalysis"
                  class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl text-sm font-medium hover:from-emerald-600 hover:to-teal-700 transition-all shadow-lg shadow-emerald-500/20">
            {{ $t('ai.startGroupAnalysis') }}
          </button>
        </div>
      </div>

      <!-- ====== TAB: RISK ANALYSIS ====== -->
      <div v-if="activeTab === 'risk'" class="space-y-6">
        <!-- Risk Level Card -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-4 sm:mb-6">
            <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center"
                 :class="riskLevel === 'low' ? 'bg-emerald-100' : riskLevel === 'medium' ? 'bg-amber-100' : 'bg-rose-100'">
              <Target :size="20" :class="riskLevel === 'low' ? 'text-emerald-600' : riskLevel === 'medium' ? 'text-amber-600' : 'text-rose-600'" />
            </div>
            <div>
              <h3 class="text-sm sm:text-base font-semibold text-slate-800">{{ $t('ai.riskLevel') }}</h3>
              <p class="text-xs sm:text-sm text-slate-500">{{ $t('ai.riskAssessment') }}</p>
            </div>
          </div>

          <!-- Risk Badge -->
          <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 mb-6">
            <div class="px-4 sm:px-5 py-2.5 sm:py-3 rounded-2xl font-bold text-base sm:text-lg w-fit"
                 :class="riskLevel === 'low' ? 'bg-emerald-100 text-emerald-700' : riskLevel === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'">
              {{ riskLabel }}
            </div>
            <div v-if="riskPrediction" class="text-xs sm:text-sm text-slate-600">{{ riskPrediction }}</div>
          </div>

          <!-- Risk Factors -->
          <div class="space-y-3">
            <h4 class="text-sm font-semibold text-slate-700">{{ $t('ai.riskFactors') }}</h4>

            <!-- Attendance based risk -->
            <div class="flex items-center gap-3 p-3 rounded-lg" :class="attendanceRate >= 80 ? 'bg-emerald-50' : attendanceRate >= 60 ? 'bg-amber-50' : 'bg-rose-50'">
              <CheckCircle v-if="attendanceRate >= 80" :size="18" class="text-emerald-600" />
              <AlertTriangle v-else :size="18" :class="attendanceRate >= 60 ? 'text-amber-600' : 'text-rose-600'" />
              <span class="text-sm text-slate-600">{{ $t('ai.attendanceRisk') }}: {{ attendanceRate }}%</span>
            </div>

            <!-- AI Strengths -->
            <div v-for="(s, i) in aiStrengths" :key="'s-' + i"
                 class="flex items-start gap-3 p-3 rounded-lg bg-emerald-50">
              <CheckCircle :size="18" class="text-emerald-600 mt-0.5 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-emerald-800">{{ $t('ai.strength') }}</p>
                <p class="text-xs text-emerald-600 mt-0.5">{{ s }}</p>
              </div>
            </div>

            <!-- Areas for improvement -->
            <div v-for="(a, i) in aiAreas" :key="'a-' + i"
                 class="flex items-start gap-3 p-3 rounded-lg bg-amber-50">
              <AlertTriangle :size="18" class="text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-amber-800">{{ $t('ai.needsImprovement') }}</p>
                <p class="text-xs text-amber-600 mt-0.5">{{ a }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Motivation -->
        <div v-if="aiMotivation" class="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-2xl border border-emerald-200 p-4 sm:p-6">
          <div class="flex items-start gap-3">
            <Sparkles :size="20" class="text-emerald-600 mt-0.5 flex-shrink-0" />
            <div>
              <p class="font-semibold text-emerald-800 text-sm">{{ $t('ai.motivation') }}</p>
              <p class="text-sm text-emerald-600 mt-1 leading-relaxed">{{ aiMotivation }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
/**
 * AIAnalysisView.vue — To'liq AI Tahlil sahifasi
 *
 * Barcha panellar uchun: student, leader, admin, super
 * Real OpenAI backend integration
 *
 * Tabs: Overview | Attendance | Predictions | Chat | Group (leader+) | Risk
 */
import { useAuthStore } from '@/stores/auth'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    Activity,
    AlertTriangle,
    Award,
    BarChart3,
    BookOpen,
    Brain,
    Calendar,
    CheckCircle,
    Clock,
    Crown,
    Info,
    Lightbulb,
    Loader2,
    Lock,
    MessageCircle,
    Minus,
    RefreshCw,
    Send,
    Sparkles,
    Target,
    TrendingDown,
    TrendingUp,
    Users as UsersIcon,
    XCircle,
    Zap
} from 'lucide-vue-next'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()
const langStore = useLanguageStore()
const { t } = langStore

// Subscription route based on role
const subscriptionRoute = computed(() => {
  const role = authStore.user?.role
  if (role === 'leader') return '/leader/subscription'
  if (role === 'student') return '/student/subscription'
  return '/leader/subscription'
})

// ---- State ----
const loading = ref(true)
const error = ref(null)
const isRefreshing = ref(false)
const activeTab = ref('overview')
const aiHealthy = ref(false)

// Subscription / Access check
const hasAIAccess = ref(true)
const currentPlan = ref(null)
const requiredPlans = ref([])

// Current user/data
const profile = ref(null)
const records = ref([])
const groupId = ref(null)

// AI Usage/Limit
const aiUsage = ref(null)

// AI Analysis state
const aiSummary = ref('')
const aiStrengths = ref([])
const aiAreas = ref([])
const aiRecommendations = ref([])
const riskLevel = ref('medium')
const riskPrediction = ref(null)
const aiMotivation = ref(null)
const metrics = ref([])
const insights = ref([])
const recommendations = ref([])

// Group analysis
const groupAnalysis = ref(null)
const groupAnalysisLoading = ref(false)

// AI analysis state control
const aiAnalysisLoaded = ref(false)
const aiAnalysisLoading = ref(false)

// Predictions
const predictions = ref([])
const predictionSummary = ref('')
const predictionConfidence = ref(0)
const predictionFactors = ref([])
const predictionLoading = ref(false)

// Chat
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatSuggestions = ref([])
const chatContainer = ref(null)

const defaultSuggestions = computed(() => {
  if (isStudentRole.value) {
    return [
      "Davomatimni qanday yaxshilasam bo'ladi?",
      "Bu hafta qanday darslarim bor?",
      "O'qish bo'yicha maslahat bering",
      "Imtihonga qanday tayyorlanish kerak?"
    ]
  }
  return [
    "Guruh davomati qanday?",
    "Dars jadvali haqida ma'lumot bering",
    "O'qitish sifatini qanday oshirish mumkin?",
    "Eng faol talabalar kimlar?"
  ]
})

// ---- Computed ----
const isStudentRole = computed(() => authStore.isStudent && !authStore.isLeader && !authStore.isAdmin && !authStore.isSuperAdmin)
const isLeaderOrAbove = computed(() => authStore.isLeader || authStore.isAdmin || authStore.isSuperAdmin)

const tabs = computed(() => {
  const base = [
    { key: 'overview', label: t('ai.overview'), icon: Brain },
    { key: 'attendance', label: t('ai.attendance'), icon: BarChart3 },
    { key: 'predictions', label: t('ai.prediction'), icon: Activity },
    { key: 'chat', label: t('ai.aiAssistant'), icon: MessageCircle },
    { key: 'risk', label: t('ai.riskLevel'), icon: Target },
  ]
  if (isLeaderOrAbove.value) {
    base.splice(4, 0, { key: 'group', label: t('ai.groupAnalysis'), icon: UsersIcon })
  }
  return base
})

const attStats = computed(() => {
  const total = records.value.length || 1
  const present = records.value.filter(r => r.status === 'present').length
  const late = records.value.filter(r => r.status === 'late').length
  const absent = records.value.filter(r => r.status === 'absent').length
  const excused = records.value.filter(r => r.status === 'excused').length
  return { total: records.value.length, present, late, absent, excused }
})

const attendanceRate = computed(() => {
  const t = attStats.value.total || 1
  return Math.round(((attStats.value.present + attStats.value.late) / t) * 100)
})

const subjectStats = computed(() => {
  if (isStudentRole.value) {
    const subjects = [...new Set(records.value.map(r => r.subject))]
    return subjects.map(s => {
      const subRecs = records.value.filter(r => r.subject === s)
      const total = subRecs.length || 1
      const attended = subRecs.filter(r => r.status === 'present' || r.status === 'late').length
      return { name: s, rate: Math.round((attended / total) * 100) }
    }).sort((a, b) => b.rate - a.rate)
  }
  // For leader/admin — show students from group analysis
  if (groupAnalysis.value) {
    const all = [
      ...(groupAnalysis.value.top_performers || []),
      ...(groupAnalysis.value.at_risk_students || [])
    ]
    return all.sort((a, b) => b.rate - a.rate)
  }
  return []
})

const weeklyData = computed(() => {
  const now = new Date()
  const weeks = []
  for (let w = 3; w >= 0; w--) {
    const weekStart = new Date(now)
    weekStart.setDate(now.getDate() - (w * 7 + now.getDay()))
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 6)

    const weekRecs = records.value.filter(r => {
      const d = new Date(r.date)
      return d >= weekStart && d <= weekEnd
    })

    const total = weekRecs.length || 1
    const attended = weekRecs.filter(r => r.status === 'present' || r.status === 'late').length
    const rate = Math.round((attended / total) * 100)

    weeks.push({ label: `${4 - w}-${t('ai.week')}`, rate: weekRecs.length ? rate : 0 })
  }
  return weeks
})

const headerStats = computed(() => {
  if (isStudentRole.value) {
    return [
      { label: t('ai.attendance'), value: attendanceRate.value + '%' },
      { label: t('ai.presentLessons'), value: attStats.value.present },
      { label: t('ai.missedLessons'), value: attStats.value.absent }
    ]
  }
  // Leader/Admin/Super
  const stats = [
    { label: t('ai.attendance'), value: attendanceRate.value + '%' },
    { label: t('ai.totalLessons'), value: attStats.value.total },
  ]
  if (groupAnalysis.value) {
    stats.push({ label: t('ai.topPerformers'), value: (groupAnalysis.value.top_performers || []).length })
    stats.push({ label: t('ai.atRiskStudents'), value: (groupAnalysis.value.at_risk_students || []).length })
  } else {
    stats.push({ label: t('ai.presentCount'), value: attStats.value.present })
    stats.push({ label: t('ai.absentCount'), value: attStats.value.absent })
  }
  return stats
})

const summaryTitle = computed(() => {
  const rate = attendanceRate.value
  if (rate >= 90) return t('ai.excellentResult')
  if (rate >= 75) return t('ai.goodProgress')
  if (rate >= 60) return t('ai.roomForImprovement')
  return t('ai.needsAttention')
})

const summaryText = computed(() => {
  if (aiSummary.value) return aiSummary.value
  return t('ai.defaultSummary').replace('{rate}', attendanceRate.value)
})

const riskLabel = computed(() => {
  const map = { low: t('ai.riskLow'), medium: t('ai.riskMedium'), high: t('ai.riskHigh') }
  return map[riskLevel.value] || riskLevel.value
})

// ---- Data loading ----
async function initData() {
  loading.value = true
  error.value = null

  try {
    // Avval obuna/huquqni tekshirish
    try {
      const accessResp = await api.aiCheckAccess()
      hasAIAccess.value = accessResp?.has_access === true
      currentPlan.value = accessResp?.current_plan || null
      requiredPlans.value = accessResp?.required_plans || ['pro', 'unlimited']
    } catch {
      hasAIAccess.value = false
    }

    if (!hasAIAccess.value) {
      loading.value = false
      return
    }

    profile.value = await api.getMe()

    // Load attendance data based on role
    if (isStudentRole.value) {
      const studentDbId = profile.value.student_db_id || profile.value.id
      const attResp = await api.getStudentAttendance(studentDbId)
      records.value = (attResp.items || attResp || []).map(r => ({
        id: r.id,
        studentId: r.student_id,
        subject: r.subject || r.lesson_name || t('common.unknown'),
        status: r.status,
        date: r.date
      }))
    } else if (authStore.isLeader) {
      // Get group from dashboard
      try {
        const dashResp = await api.request('/dashboard/leader')
        groupId.value = dashResp?.group?.id || null
        if (groupId.value) {
          await loadGroupAttendanceRecords()
        }
      } catch (e) {
        console.warn('Leader dashboard error:', e)
      }
    } else {
      // Admin/Super — overall stats
      try {
        const dashResp = await api.request('/statistics/dashboard')
        if (dashResp) {
          // Use dashboard stats for overview
          metrics.value = buildAdminMetrics(dashResp)
        }
      } catch (e) {
        console.warn('Dashboard stats error:', e)
      }
    }

    // Load AI usage/limits (non-blocking)
    loadAIUsage()

    // Check AI health (non-blocking)
    checkAIHealth()

    // Build local insights from attendance data (FREE - no API call)
    buildLocalInsights()

  } catch (e) {
    console.error('Init error:', e)
    error.value = t('ai.loadError')
  } finally {
    loading.value = false
  }
}

async function loadGroupAttendanceRecords() {
  if (!groupId.value) return
  try {
    const today = new Date()
    const monthAgo = new Date(today)
    monthAgo.setDate(monthAgo.getDate() - 30)
    const dateFrom = monthAgo.toISOString().split('T')[0]
    const dateTo = today.toISOString().split('T')[0]

    const summaryResp = await api.request(`/attendance/group/${groupId.value}/summary?date_from=${dateFrom}&date_to=${dateTo}`)
    if (Array.isArray(summaryResp)) {
      // Convert to flat records
      let allRecords = []
      summaryResp.forEach(s => {
        for (let i = 0; i < (s.present || 0); i++) allRecords.push({ status: 'present', date: dateTo, subject: s.student_name || 'N/A' })
        for (let i = 0; i < (s.absent || 0); i++) allRecords.push({ status: 'absent', date: dateTo, subject: s.student_name || 'N/A' })
        for (let i = 0; i < (s.late || 0); i++) allRecords.push({ status: 'late', date: dateTo, subject: s.student_name || 'N/A' })
        for (let i = 0; i < (s.excused || 0); i++) allRecords.push({ status: 'excused', date: dateTo, subject: s.student_name || 'N/A' })
      })
      records.value = allRecords
    }
  } catch (e) {
    console.warn('Group attendance error:', e)
  }
}

function buildAdminMetrics(data) {
  return [
    {
      label: t('ai.totalStudents'),
      value: data.total_students || data.students_count || '—',
      icon: UsersIcon,
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      trend: null
    },
    {
      label: t('ai.totalGroups'),
      value: data.total_groups || data.groups_count || '—',
      icon: BookOpen,
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      trend: null
    },
    {
      label: t('ai.overallAttendance'),
      value: (data.attendance_rate || data.overall_attendance || '—') + '%',
      icon: CheckCircle,
      iconBg: 'bg-teal-100',
      iconColor: 'text-teal-600',
      trend: null
    },
    {
      label: t('ai.activeUsers'),
      value: data.active_users || '—',
      icon: Activity,
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600',
      trend: null
    }
  ]
}

async function loadAIUsage() {
  try {
    aiUsage.value = await api.aiGetUsage()
  } catch (e) {
    console.warn('AI usage load error:', e)
  }
}

async function checkAIHealth() {
  try {
    const resp = await api.aiHealthCheck()
    aiHealthy.value = resp?.status === 'healthy'
  } catch {
    aiHealthy.value = false
  }
}

async function startAIAnalysis() {
  if (aiUsage.value?.is_limit_reached) {
    toast.error(t('ai.limitReachedTitle'))
    return
  }
  aiAnalysisLoading.value = true
  await loadAIAnalysis()
  aiAnalysisLoading.value = false
  aiAnalysisLoaded.value = true
  // Refresh usage after AI calls
  loadAIUsage()
}

async function loadAIAnalysis() {
  try {
    if (isStudentRole.value && profile.value?.id) {
      // Student: analyze student + recommendations
      const studentDbId = profile.value.student_db_id || profile.value.id
      const [analysis, recs] = await Promise.all([
        api.aiAnalyzeStudent({ student_id: studentDbId }).catch(() => null),
        api.aiStudentRecommendations(studentDbId).catch(() => null)
      ])

      if (analysis) {
        aiSummary.value = analysis.summary || ''
        aiStrengths.value = analysis.strengths || []
        aiAreas.value = analysis.areas_for_improvement || []
        riskLevel.value = analysis.risk_level || 'medium'
        riskPrediction.value = analysis.predicted_performance || null

        insights.value = [
          ...(analysis.strengths || []).map(s => ({ type: 'positive', title: s })),
          ...(analysis.areas_for_improvement || []).map(s => ({ type: 'warning', title: s }))
        ]

        recommendations.value = (analysis.recommendations || []).map(r =>
          typeof r === 'string' ? { title: r } : r
        )

        // Build metrics from analysis context_data
        if (analysis.context_data?.attendance) {
          const att = analysis.context_data.attendance
          metrics.value = [
            { label: t('ai.riskLevel'), value: riskLabel.value, icon: Target, iconBg: riskLevel.value === 'low' ? 'bg-emerald-100' : riskLevel.value === 'medium' ? 'bg-amber-100' : 'bg-rose-100', iconColor: riskLevel.value === 'low' ? 'text-emerald-600' : riskLevel.value === 'medium' ? 'text-amber-600' : 'text-rose-600', trend: null },
            { label: t('ai.attendance'), value: att.rate + '%', icon: CheckCircle, iconBg: 'bg-emerald-100', iconColor: 'text-emerald-600', trend: null },
            { label: t('ai.presentLessons'), value: att.present, icon: TrendingUp, iconBg: 'bg-blue-100', iconColor: 'text-blue-600', trend: null },
            { label: t('ai.missedLessons'), value: att.absent, icon: XCircle, iconBg: 'bg-rose-100', iconColor: 'text-rose-600', trend: null }
          ]
        }
      }

      if (recs) {
        aiMotivation.value = recs.motivation || null
        if (!recommendations.value.length && recs.recommendations) {
          recommendations.value = recs.recommendations.map(r =>
            typeof r === 'object' ? r : { title: r }
          )
        }
      }

      if (!analysis && !recs) {
        // AI not available — use local data
        buildLocalInsights()
      }
    } else if (isLeaderOrAbove.value) {
      // Leader/Admin/Super: dashboard insights + group analysis
      const dashInsights = await api.aiDashboardInsights().catch(() => null)

      if (dashInsights) {
        aiSummary.value = dashInsights.summary || ''
        insights.value = (dashInsights.insights || []).map(i => ({
          type: i.type || 'info',
          title: i.title,
          description: i.description
        }))

        if (dashInsights.metrics?.length) {
          metrics.value = dashInsights.metrics.map(m => ({
            label: m.label,
            value: m.value,
            icon: getMetricIconComponent(m.type),
            iconBg: getMetricIconBg(m.type),
            iconColor: getMetricIconColor(m.type),
            trend: m.trend
          }))
        }

        recommendations.value = (dashInsights.recommendations || []).map(r =>
          typeof r === 'string' ? { title: r } : r
        )
      } else {
        buildLocalInsights()
      }
    }
  } catch (e) {
    console.warn('AI analysis error:', e)
    buildLocalInsights()
  }
}

function buildLocalInsights() {
  const rate = attendanceRate.value
  insights.value = []
  if (rate >= 90) {
    insights.value.push({ type: 'positive', title: t('ai.insightExcellent') })
  } else if (rate >= 70) {
    insights.value.push({ type: 'info', title: t('ai.insightGood') })
  } else {
    insights.value.push({ type: 'warning', title: t('ai.insightLow') })
  }
}

// ---- Group Analysis ----
async function loadGroupAnalysis() {
  if (aiUsage.value?.is_limit_reached) {
    toast.error(t('ai.limitReachedTitle'))
    return
  }
  const gId = groupId.value
  if (!gId && !authStore.isAdmin && !authStore.isSuperAdmin) return

  groupAnalysisLoading.value = true
  try {
    // For admin/super, we can try first group or use dashboard
    let targetGroupId = gId
    if (!targetGroupId && (authStore.isAdmin || authStore.isSuperAdmin)) {
      // Try to get first group
      try {
        const groupsResp = await api.request('/groups?page_size=1')
        targetGroupId = groupsResp?.items?.[0]?.id || null
      } catch { /* ignore */ }
    }

    if (!targetGroupId) {
      toast.warning(t('ai.noGroupFound'))
      groupAnalysisLoading.value = false
      return
    }

    groupId.value = targetGroupId
    const resp = await api.aiAnalyzeGroup({ group_id: targetGroupId })
    groupAnalysis.value = resp
    toast.success(t('ai.analysisComplete'))
    loadAIUsage()
  } catch (e) {
    console.error('Group analysis error:', e)
    if (e?.message?.includes('429') || e?.message?.includes('limit')) {
      aiUsage.value = { ...aiUsage.value, is_limit_reached: true }
    }
    toast.error(e?.message || t('ai.analysisError'))
  } finally {
    groupAnalysisLoading.value = false
  }
}

// ---- Predictions ----
async function loadPredictions() {
  if (aiUsage.value?.is_limit_reached) {
    toast.error(t('ai.limitReachedTitle'))
    return
  }
  predictionLoading.value = true
  try {
    const body = { days_ahead: 7 }
    if (isStudentRole.value && profile.value?.id) {
      body.student_id = profile.value.student_db_id || profile.value.id
    } else if (groupId.value) {
      body.group_id = groupId.value
    }

    const resp = await api.aiPredictAttendance(body)
    predictions.value = resp.predictions || []
    predictionSummary.value = resp.overall_prediction || ''
    predictionConfidence.value = resp.confidence || 0
    predictionFactors.value = resp.factors || []
    loadAIUsage()
  } catch (e) {
    console.error('Prediction error:', e)
    if (e?.message?.includes('429') || e?.message?.includes('limit')) {
      aiUsage.value = { ...aiUsage.value, is_limit_reached: true }
    }
    toast.error(e?.message || t('ai.predictionError'))
  } finally {
    predictionLoading.value = false
  }
}

// ---- Chat ----
async function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg || chatLoading.value) return

  if (aiUsage.value?.is_limit_reached) {
    toast.error(t('ai.limitReachedTitle'))
    return
  }

  chatMessages.value.push({ role: 'user', content: msg })
  chatInput.value = ''
  chatLoading.value = true
  chatSuggestions.value = []

  await nextTick()
  scrollChatToBottom()

  try {
    const history = chatMessages.value.slice(-6).map(m => ({ role: m.role, content: m.content }))
    const contextInfo = isStudentRole.value
      ? `${t('ai.student')}: ${profile.value?.name || ''}, ${t('ai.attendance')}: ${attendanceRate.value}%`
      : `${t('ai.role')}: ${authStore.user?.role || ''}, ${t('ai.attendance')}: ${attendanceRate.value}%`

    const result = await api.aiChat({
      message: msg,
      context: contextInfo,
      conversation_history: history.slice(0, -1)
    })

    chatMessages.value.push({ role: 'assistant', content: result.response })
    chatSuggestions.value = result.suggestions || []
    loadAIUsage()
  } catch (e) {
    chatMessages.value.push({ role: 'assistant', content: t('ai.chatError') })
    if (e?.message?.includes('429') || e?.message?.includes('limit')) {
      aiUsage.value = { ...aiUsage.value, is_limit_reached: true }
    }
  } finally {
    chatLoading.value = false
    await nextTick()
    scrollChatToBottom()
  }
}

function scrollChatToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// ---- Refresh ----
async function refreshAll() {
  isRefreshing.value = true
  // Reset AI data
  aiSummary.value = ''
  aiStrengths.value = []
  aiAreas.value = []
  aiRecommendations.value = []
  insights.value = []
  recommendations.value = []
  predictions.value = []
  groupAnalysis.value = null
  aiAnalysisLoaded.value = false
  aiAnalysisLoading.value = false

  await initData()
  await loadAIUsage()
  isRefreshing.value = false
  toast.success(t('ai.refreshed'))
}

// ---- Helpers ----
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

function getInsightClass(type) {
  const map = {
    positive: 'bg-emerald-100 text-emerald-600',
    warning: 'bg-amber-100 text-amber-600',
    negative: 'bg-rose-100 text-rose-600',
    info: 'bg-blue-100 text-blue-600'
  }
  return map[type] || map.info
}

function getInsightIcon(type) {
  const map = {
    positive: CheckCircle,
    warning: AlertTriangle,
    negative: XCircle,
    info: Info
  }
  return map[type] || Info
}

function getMetricIconComponent(type) {
  const map = { attendance: CheckCircle, warning: AlertTriangle, info: Info, performance: Award }
  return map[type] || Info
}

function getMetricIconBg(type) {
  const map = { attendance: 'bg-emerald-100', warning: 'bg-amber-100', info: 'bg-blue-100', performance: 'bg-teal-100' }
  return map[type] || 'bg-blue-100'
}

function getMetricIconColor(type) {
  const map = { attendance: 'text-emerald-600', warning: 'text-amber-600', info: 'text-blue-600', performance: 'text-teal-600' }
  return map[type] || 'text-blue-600'
}

// Watch tab changes for lazy loading
watch(activeTab, (newTab) => {
  if (newTab === 'group' && !groupAnalysis.value && !groupAnalysisLoading.value) {
    loadGroupAnalysis()
  }
})

// Init
onMounted(() => {
  initData()
})
</script>
