<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <RefreshCw class="w-12 h-12 text-amber-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-600">{{ $t('dashboard.loadingData') }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6">
      <div class="flex items-center gap-3">
        <AlertCircle class="w-6 h-6 text-rose-500" />
        <div>
          <h3 class="font-semibold text-rose-700">{{ $t('dashboard.errorOccurred') }}</h3>
          <p class="text-rose-600 text-sm mt-1">{{ error }}</p>
        </div>
        <button @click="refresh" class="ml-auto px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600 transition-colors">
          {{ $t('dashboard.retryBtn') }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Welcome Header -->
      <div class="bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 rounded-2xl p-4 sm:p-6 text-white">
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <h1 class="text-xl sm:text-2xl font-bold flex items-center gap-2">
              <Crown class="w-6 h-6 sm:w-7 sm:h-7" />
              {{ $t('dashboard.superAdminPanel') }}
            </h1>
            <p class="text-amber-100 mt-1 text-sm sm:text-base">{{ $t('dashboard.fullMonitoring') }}</p>
          </div>
          <div class="flex items-center gap-3">
            <div class="text-right text-sm">
              <p class="text-amber-100">{{ $t('dashboard.serverStatus') }}</p>
              <p class="font-bold text-lg">
                <span v-if="healthStatus === 'healthy'" class="flex items-center gap-1">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse inline-block"></span>
                  {{ $t('dashboard.working') }}
                </span>
                <span v-else class="flex items-center gap-1">
                  <span class="w-2.5 h-2.5 rounded-full bg-red-400 inline-block"></span>
                  {{ $t('dashboard.problemStatus') }}
                </span>
              </p>
            </div>
            <button @click="refresh" class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center hover:bg-white/30 transition-colors" :title="$t('common.refresh')">
              <RefreshCw class="w-5 h-5" :class="{ 'animate-spin': refreshing }" />
            </button>
          </div>
        </div>
      </div>

      <!-- Main Stats Cards - Row 1 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <!-- Total Users -->
        <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xl sm:text-3xl font-bold text-slate-800">{{ formatNumber(stats.totalUsers) }}</p>
              <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('dashboard.totalUsers') }}</p>
            </div>
            <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <UsersRound class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
            </div>
          </div>
          <div class="mt-2 sm:mt-3 flex items-center gap-1 text-xs">
            <TrendingUp v-if="stats.newUsersWeek > 0" class="w-3.5 h-3.5 text-emerald-500" />
            <span class="text-emerald-600 font-medium">+{{ stats.newUsersWeek }}</span>
            <span class="text-slate-400">{{ $t('dashboard.thisWeekNew') }}</span>
          </div>
        </div>

        <!-- Total Students -->
        <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xl sm:text-3xl font-bold text-violet-600">{{ formatNumber(stats.totalStudents) }}</p>
              <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('dashboard.students') }}</p>
            </div>
            <div class="w-10 h-10 sm:w-12 sm:h-12 bg-violet-100 rounded-xl flex items-center justify-center">
              <GraduationCap class="w-5 h-5 sm:w-6 sm:h-6 text-violet-600" />
            </div>
          </div>
          <div class="mt-2 sm:mt-3 flex items-center gap-1 text-xs">
            <span class="text-slate-500">{{ $t('dashboard.activeLabel') }}:</span>
            <span class="text-violet-600 font-medium">{{ formatNumber(stats.activeStudents) }}</span>
          </div>
        </div>

        <!-- Total Groups -->
        <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5 hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xl sm:text-3xl font-bold text-emerald-600">{{ formatNumber(stats.totalGroups) }}</p>
              <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('dashboard.groups') }}</p>
            </div>
            <div class="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
              <Layers class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
            </div>
          </div>
          <div class="mt-3 flex items-center gap-1 text-xs">
            <span class="text-slate-500">{{ $t('dashboard.activeLabel') }}:</span>
            <span class="text-emerald-600 font-medium">{{ formatNumber(stats.activeGroups) }}</span>
          </div>
        </div>

        <!-- Today Attendance -->
        <div class="bg-white rounded-2xl border border-slate-200 p-3 sm:p-5 hover:shadow-md transition-shadow">hadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xl sm:text-3xl font-bold text-amber-600">{{ todayAttendance.rate }}%</p>
              <p class="text-xs sm:text-sm text-slate-500 mt-1">{{ $t('dashboard.todayAttendance') }}</p>
            </div>
            <div class="w-10 h-10 sm:w-12 sm:h-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <CalendarCheck class="w-5 h-5 sm:w-6 sm:h-6 text-amber-600" />
            </div>
          </div>
          <div class="mt-3 flex items-center gap-1 text-xs">
            <span class="text-slate-500">{{ $t('dashboard.totalLabel') }}:</span>
            <span class="text-amber-600 font-medium">{{ todayAttendance.total }} {{ $t('dashboard.recordsLabel') }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <router-link to="/super/users" class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-blue-200 transition-all group text-center">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
            <Users class="w-6 h-6 text-blue-600" />
          </div>
          <h3 class="font-semibold text-slate-800 text-sm">{{ $t('dashboard.usersAction') }}</h3>
        </router-link>

        <router-link to="/super/admins" class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-amber-200 transition-all group text-center">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
            <ShieldCheck class="w-6 h-6 text-amber-600" />
          </div>
          <h3 class="font-semibold text-slate-800 text-sm">{{ $t('dashboard.adminsAction') }}</h3>
        </router-link>

        <router-link to="/super/settings" class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-violet-200 transition-all group text-center">
          <div class="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
            <Settings class="w-6 h-6 text-violet-600" />
          </div>
          <h3 class="font-semibold text-slate-800 text-sm">{{ $t('dashboard.settingsAction') }}</h3>
        </router-link>

        <router-link to="/super/logs" class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-emerald-200 transition-all group text-center">
          <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
            <ScrollText class="w-6 h-6 text-emerald-600" />
          </div>
          <h3 class="font-semibold text-slate-800 text-sm">{{ $t('dashboard.logsAction') }}</h3>
        </router-link>
      </div>

      <!-- Row: Role Distribution + Today Attendance Detail -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Role Distribution -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <PieChart class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.roleDistribution') }}
          </h2>
          <div class="space-y-3">
            <div v-for="role in roleDistribution" :key="role.key" class="group">
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full" :class="role.dotClass"></div>
                  <span class="text-sm text-slate-700">{{ role.label }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-slate-800">{{ formatNumber(role.count) }}</span>
                  <span class="text-xs text-slate-400">({{ role.percent }}%)</span>
                </div>
              </div>
              <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full transition-all duration-500"
                  :class="role.barClass"
                  :style="{ width: role.percent + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Today Attendance Breakdown -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <CalendarCheck class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.todayAttendanceDetail') }}
          </h2>
          <div v-if="todayAttendance.total > 0" class="space-y-4">
            <!-- Attendance donut-like visual -->
            <div class="flex items-center justify-center gap-4 sm:gap-8 py-4">
              <div class="text-center">
                <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full border-4 border-emerald-500 flex items-center justify-center bg-emerald-50">
                  <span class="text-lg sm:text-xl font-bold text-emerald-600">{{ todayAttendance.present }}</span>
                </div>
                <p class="text-xs text-slate-500 mt-2">{{ $t('dashboard.presentLabel') }}</p>
              </div>
              <div class="text-center">
                <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full border-4 border-rose-500 flex items-center justify-center bg-rose-50">
                  <span class="text-lg sm:text-xl font-bold text-rose-600">{{ todayAttendance.absent }}</span>
                </div>
                <p class="text-xs text-slate-500 mt-2">{{ $t('dashboard.absentLabel') }}</p>
              </div>
              <div class="text-center">
                <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full border-4 border-amber-500 flex items-center justify-center bg-amber-50">
                  <span class="text-lg sm:text-xl font-bold text-amber-600">{{ todayAttendance.late }}</span>
                </div>
                <p class="text-xs text-slate-500 mt-2">{{ $t('dashboard.lateLabel') }}</p>
              </div>
            </div>
            <!-- Rate bar -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-sm text-slate-600">{{ $t('dashboard.overallRate') }}</span>
                <span class="text-sm font-bold" :class="todayAttendance.rate >= 80 ? 'text-emerald-600' : todayAttendance.rate >= 60 ? 'text-amber-600' : 'text-rose-600'">{{ todayAttendance.rate }}%</span>
              </div>
              <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full transition-all duration-500"
                  :class="todayAttendance.rate >= 80 ? 'bg-emerald-500' : todayAttendance.rate >= 60 ? 'bg-amber-500' : 'bg-rose-500'"
                  :style="{ width: todayAttendance.rate + '%' }"
                ></div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-8 text-slate-400">
            <CalendarCheck class="w-12 h-12 mb-3" />
            <p class="text-sm">{{ $t('dashboard.noAttendanceYet') }}</p>
          </div>
        </div>
      </div>

      <!-- Row: Monthly Attendance + Attendance Trend -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Monthly Attendance Stats -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart3 class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.monthlyStats') }}
          </h2>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="bg-emerald-50 rounded-xl p-4 text-center">
              <p class="text-2xl font-bold text-emerald-600">{{ monthAttendance.present }}</p>
              <p class="text-xs text-emerald-700 mt-1">{{ $t('dashboard.monthPresent') }}</p>
            </div>
            <div class="bg-rose-50 rounded-xl p-4 text-center">
              <p class="text-2xl font-bold text-rose-600">{{ monthAttendance.absent }}</p>
              <p class="text-xs text-rose-700 mt-1">{{ $t('dashboard.monthAbsent') }}</p>
            </div>
            <div class="bg-amber-50 rounded-xl p-4 text-center">
              <p class="text-2xl font-bold text-amber-600">{{ monthAttendance.late }}</p>
              <p class="text-xs text-amber-700 mt-1">{{ $t('dashboard.monthLate') }}</p>
            </div>
            <div class="bg-blue-50 rounded-xl p-4 text-center">
              <p class="text-2xl font-bold text-blue-600">{{ monthAttendance.total }}</p>
              <p class="text-xs text-blue-700 mt-1">{{ $t('dashboard.monthTotal') }}</p>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between mb-1.5">
                <span class="text-sm text-slate-600">{{ $t('dashboard.monthlyRate') }}</span>
              <span class="text-sm font-bold" :class="monthAttendance.rate >= 80 ? 'text-emerald-600' : monthAttendance.rate >= 60 ? 'text-amber-600' : 'text-rose-600'">{{ monthAttendance.rate }}%</span>
            </div>
            <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :class="monthAttendance.rate >= 80 ? 'bg-emerald-500' : monthAttendance.rate >= 60 ? 'bg-amber-500' : 'bg-rose-500'"
                :style="{ width: monthAttendance.rate + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Weekly Attendance Trend -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <TrendingUp class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.weeklyTrend') }}
          </h2>
          <div v-if="attendanceTrend.length > 0" class="space-y-2">
            <div v-for="day in attendanceTrend" :key="day.date" class="flex items-center gap-3">
              <span class="text-xs text-slate-500 w-20 shrink-0">{{ formatTrendDate(day.date) }}</span>
              <div class="flex-1 h-6 bg-slate-100 rounded-full overflow-hidden relative flex">
                <div 
                  class="h-full bg-emerald-500 transition-all duration-500" 
                  :style="{ width: (day.total > 0 ? (day.present / day.total * 100) : 0) + '%' }"
                  :title="'Keldi: ' + day.present"
                ></div>
                <div 
                  class="h-full bg-amber-500 transition-all duration-500" 
                  :style="{ width: (day.total > 0 ? (day.late / day.total * 100) : 0) + '%' }"
                  :title="'Kechikdi: ' + day.late"
                ></div>
                <div 
                  class="h-full bg-rose-500 transition-all duration-500" 
                  :style="{ width: (day.total > 0 ? (day.absent / day.total * 100) : 0) + '%' }"
                  :title="'Kelmadi: ' + day.absent"
                ></div>
              </div>
              <span class="text-xs font-bold w-12 text-right" :class="day.rate >= 80 ? 'text-emerald-600' : day.rate >= 60 ? 'text-amber-600' : 'text-rose-600'">{{ day.rate }}%</span>
            </div>
            <!-- Legend -->
            <div class="flex items-center justify-center gap-4 pt-3 border-t border-slate-100 mt-3">
              <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500"></span><span class="text-xs text-slate-500">{{ $t('dashboard.legendPresent') }}</span></div>
              <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-500"></span><span class="text-xs text-slate-500">{{ $t('dashboard.legendLate') }}</span></div>
              <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-rose-500"></span><span class="text-xs text-slate-500">{{ $t('dashboard.legendAbsent') }}</span></div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-8 text-slate-400">
            <TrendingUp class="w-12 h-12 mb-3" />
            <p class="text-sm">{{ $t('dashboard.noWeeklyData') }}</p>
          </div>
        </div>
      </div>

      <!-- Row: Database Stats + Reports + System Health -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Database Stats -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Database class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.databaseStats') }}
          </h2>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-2">
                <UsersRound class="w-4 h-4 text-blue-500" />
                <span class="text-sm text-slate-700">{{ $t('dashboard.dbUsers') }}</span>
              </div>
              <span class="font-semibold text-sm text-slate-800">{{ formatNumber(stats.totalUsers) }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-2">
                <GraduationCap class="w-4 h-4 text-violet-500" />
                <span class="text-sm text-slate-700">{{ $t('dashboard.dbStudents') }}</span>
              </div>
              <span class="font-semibold text-sm text-slate-800">{{ formatNumber(stats.totalStudents) }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-2">
                <Layers class="w-4 h-4 text-emerald-500" />
                <span class="text-sm text-slate-700">{{ $t('dashboard.dbGroups') }}</span>
              </div>
              <span class="font-semibold text-sm text-slate-800">{{ formatNumber(stats.totalGroups) }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-2">
                <ClipboardList class="w-4 h-4 text-amber-500" />
                <span class="text-sm text-slate-700">{{ $t('dashboard.dbAttendance') }}</span>
              </div>
              <span class="font-semibold text-sm text-slate-800">{{ formatNumber(stats.attendanceRecords) }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-2">
                <Bell class="w-4 h-4 text-indigo-500" />
                <span class="text-sm text-slate-700">{{ $t('dashboard.dbNotifications') }}</span>
              </div>
              <span class="font-semibold text-sm text-slate-800">{{ formatNumber(stats.notificationsCount) }}</span>
            </div>
          </div>
        </div>

        <!-- Reports Stats -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <FileBarChart class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.reportsSection') }}
          </h2>
          <div class="text-center py-2 mb-4">
            <p class="text-4xl font-bold text-slate-800">{{ reports.total }}</p>
            <p class="text-sm text-slate-500 mt-1">{{ $t('dashboard.totalReports') }}</p>
          </div>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-amber-50 rounded-xl">
              <div class="flex items-center gap-2">
                <Clock class="w-4 h-4 text-amber-600" />
                <span class="text-sm text-amber-800">{{ $t('dashboard.pendingReports') }}</span>
              </div>
              <span class="font-bold text-amber-600">{{ reports.pending }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-emerald-50 rounded-xl">
              <div class="flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-emerald-600" />
                <span class="text-sm text-emerald-800">{{ $t('dashboard.approvedReports') }}</span>
              </div>
              <span class="font-bold text-emerald-600">{{ reports.approved }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-rose-50 rounded-xl">
              <div class="flex items-center gap-2">
                <XCircle class="w-4 h-4 text-rose-600" />
                <span class="text-sm text-rose-800">{{ $t('dashboard.rejectedReports') }}</span>
              </div>
              <span class="font-bold text-rose-600">{{ reports.rejected }}</span>
            </div>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-100">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">{{ $t('dashboard.approvalRate') }}</span>
              <span class="text-sm font-bold text-emerald-600">{{ reports.approvalRate }}%</span>
            </div>
          </div>
        </div>

        <!-- System Health -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Activity class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.systemStatus') }}
          </h2>
          <div class="space-y-4">
            <!-- API Server -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <Server class="w-4 h-4 text-slate-500" />
                  <span class="text-sm text-slate-600">{{ $t('dashboard.apiServer') }}</span>
                </div>
                <span class="text-xs font-medium flex items-center gap-1" :class="healthStatus === 'healthy' ? 'text-emerald-600' : 'text-rose-600'">
                  <span class="w-2 h-2 rounded-full animate-pulse" :class="healthStatus === 'healthy' ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                  {{ healthStatus === 'healthy' ? $t('dashboard.working') : $t('dashboard.errorStatus') }}
                </span>
              </div>
              <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500" :class="healthStatus === 'healthy' ? 'bg-emerald-500 w-full' : 'bg-rose-500 w-1/4'"></div>
              </div>
            </div>
            <!-- Database -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <Database class="w-4 h-4 text-slate-500" />
                  <span class="text-sm text-slate-600">{{ $t('dashboard.database') }}</span>
                </div>
                <span class="text-xs font-medium flex items-center gap-1" :class="stats.totalUsers > 0 ? 'text-emerald-600' : 'text-rose-600'">
                  <span class="w-2 h-2 rounded-full animate-pulse" :class="stats.totalUsers > 0 ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                  {{ stats.totalUsers > 0 ? $t('dashboard.connected') : $t('dashboard.disconnected') }}
                </span>
              </div>
              <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500" :class="stats.totalUsers > 0 ? 'bg-emerald-500 w-full' : 'bg-rose-500 w-0'"></div>
              </div>
            </div>
            <!-- App info -->
            <div class="pt-3 mt-2 border-t border-slate-100 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-slate-500">{{ $t('dashboard.appLabel') }}</span>
                <span class="text-xs font-medium text-slate-700">{{ healthInfo.app }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-slate-500">{{ $t('dashboard.versionLabel') }}</span>
                <span class="text-xs font-medium text-slate-700">{{ healthInfo.version }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-slate-500">{{ $t('dashboard.environmentLabel') }}</span>
                <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="healthInfo.environment === 'production' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">{{ healthInfo.environment }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Row: Top Groups + Recent Users -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Groups by Students -->
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div class="p-6 border-b border-slate-100">
            <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Award class="w-5 h-5 text-amber-500" />
              {{ $t('dashboard.topGroups') }}
            </h2>
          </div>
          <div v-if="topGroups.length > 0" class="divide-y divide-slate-100">
            <div v-for="(group, index) in topGroups" :key="group.id" class="p-4 flex items-center gap-4">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold" :class="index < 3 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-slate-800 truncate">{{ group.name }}</p>
                <p class="text-xs text-slate-500">{{ group.faculty }} • {{ group.course_year }}-kurs</p>
              </div>
              <div class="flex items-center gap-1 bg-blue-50 px-2.5 py-1 rounded-lg">
                <Users class="w-3.5 h-3.5 text-blue-600" />
                <span class="text-sm font-bold text-blue-600">{{ group.student_count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center text-slate-400">
            <Layers class="w-10 h-10 mx-auto mb-3" />
            <p class="text-sm">{{ $t('dashboard.noGroups') }}</p>
          </div>
        </div>

        <!-- Recent Users -->
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <UserPlus class="w-5 h-5 text-emerald-500" />
              {{ $t('dashboard.newUsers') }}
            </h2>
            <router-link to="/super/users" class="text-xs text-amber-600 hover:text-amber-700 font-medium">
              {{ $t('dashboard.viewAllLink') }}
            </router-link>
          </div>
          <div v-if="recentUsers.length > 0" class="divide-y divide-slate-100">
            <div v-for="user in recentUsers" :key="user.id" class="p-4 flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold" :class="getRoleBgClass(user.role)">
                {{ getInitials(user.name) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-slate-800 truncate">{{ user.name }}</p>
                <p class="text-xs text-slate-500">{{ user.login }}</p>
              </div>
              <div class="flex flex-col items-end gap-1">
                <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="getRoleBadgeClass(user.role)">{{ getRoleLabel(user.role) }}</span>
                <span class="text-xs text-slate-400">{{ formatTime(user.created_at) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center text-slate-400">
            <Users class="w-10 h-10 mx-auto mb-3" />
            <p class="text-sm">{{ $t('dashboard.noUsers') }}</p>
          </div>
        </div>
      </div>

      <!-- Recent Logs -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="p-6 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <ScrollText class="w-5 h-5 text-slate-400" />
            {{ $t('dashboard.recentActivity') }}
          </h2>
          <router-link to="/super/logs" class="text-xs text-amber-600 hover:text-amber-700 font-medium">
            Barchasini ko'rish →
          </router-link>
        </div>
        <div v-if="recentLogs.length === 0" class="p-8 text-center text-slate-400">
          <Clock class="w-10 h-10 mx-auto mb-3" />
          <p class="text-sm">{{ $t('dashboard.noActivity') }}</p>
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="log in recentLogs" :key="log.id" class="p-4 flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="log.bgClass">
              <component :is="log.icon" class="w-5 h-5" :class="log.iconClass" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-slate-800">{{ log.action }}</p>
              <p class="text-sm text-slate-500">{{ log.user }} <span v-if="log.module" class="text-slate-400">• {{ log.module }}</span></p>
            </div>
            <span class="text-xs text-slate-400 whitespace-nowrap">{{ log.time }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
/**
 * Super Admin Dashboard — To'liq real API bilan ishlaydi
 * 
 * API endpoints:
 * - GET /dashboard/superadmin — system_stats, role_distribution, today/month attendance, trend, reports, top_groups, recent_users
 * - GET /health — server status, version, environment
 * - GET /statistics/attendance — attendance breakdown
 * - GET /reports/stats/summary — report statistics
 * - GET /notifications?page_size=1 — notification count
 * - GET /logs?limit=5 — recent activity logs
 */
import {
    Activity,
    AlertCircle,
    Award,
    BarChart3,
    Bell,
    CalendarCheck,
    CheckCircle,
    ClipboardList,
    Clock,
    Crown,
    Database,
    FileBarChart,
    FileEdit,
    GraduationCap,
    Layers,
    LogIn,
    PieChart,
    RefreshCw,
    ScrollText,
    Server,
    Settings,
    ShieldCheck,
    Trash,
    TrendingUp,
    UserPlus,
    Users,
    UsersRound,
    XCircle
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'

// === STATE ===
const loading = ref(true)
const refreshing = ref(false)
const error = ref(null)

// System stats
const stats = reactive({
  totalUsers: 0,
  activeUsers: 0,
  totalStudents: 0,
  activeStudents: 0,
  totalGroups: 0,
  activeGroups: 0,
  admins: 0,
  leaders: 0,
  newUsersWeek: 0,
  attendanceRecords: 0,
  notificationsCount: 0
})

// Today attendance
const todayAttendance = reactive({
  total: 0,
  present: 0,
  absent: 0,
  late: 0,
  rate: 0
})

// Month attendance
const monthAttendance = reactive({
  total: 0,
  present: 0,
  absent: 0,
  late: 0,
  rate: 0
})

// Attendance trend (weekly)
const attendanceTrend = ref([])

// Role distribution (computed from raw data)
const rawRoleDistribution = ref({})

// Reports
const reports = reactive({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0,
  approvalRate: 0
})

// Health
const healthStatus = ref('unknown')
const healthInfo = reactive({
  app: 'UniControl',
  version: '-',
  environment: '-'
})

// Top groups & recent users
const topGroups = ref([])
const recentUsers = ref([])
const recentLogs = ref([])

// === COMPUTED ===
const roleDistribution = computed(() => {
  const raw = rawRoleDistribution.value
  const total = Object.values(raw).reduce((s, v) => s + v, 0) || 1
  
  const roles = [
    { key: 'student', label: 'Talabalar', dotClass: 'bg-blue-500', barClass: 'bg-blue-500' },
    { key: 'leader', label: 'Liderlar', dotClass: 'bg-violet-500', barClass: 'bg-violet-500' },
    { key: 'admin', label: 'Adminlar', dotClass: 'bg-amber-500', barClass: 'bg-amber-500' },
    { key: 'superadmin', label: 'Super Adminlar', dotClass: 'bg-rose-500', barClass: 'bg-rose-500' }
  ]

  return roles.map(r => ({
    ...r,
    count: raw[r.key] || 0,
    percent: Math.round(((raw[r.key] || 0) / total) * 100)
  }))
})

// === LOAD ALL DATA ===
const loadDashboard = async () => {
  loading.value = true
  error.value = null

  try {
    // Call all endpoints in parallel with fault tolerance
    const [dashboardRes, reportsRes, notificationsRes, logsRes] = await Promise.allSettled([
      api.request('/dashboard/superadmin'),
      api.request('/reports/stats/summary'),
      api.request('/notifications?page_size=1'),
      api.getLogs({ limit: 5 })
    ])

    // 1. Dashboard superadmin (main data source) — if this works, system is healthy
    if (dashboardRes.status === 'fulfilled') {
      healthStatus.value = 'healthy'
      healthInfo.app = 'UniControl'
      healthInfo.version = '1.0.0'
      healthInfo.environment = import.meta.env.MODE || 'production'
      const d = dashboardRes.value

      // System stats
      if (d.system_stats) {
        stats.totalUsers = d.system_stats.total_users || 0
        stats.activeUsers = d.system_stats.active_users || 0
        stats.totalStudents = d.system_stats.total_students || d.system_stats.students || 0
        stats.activeStudents = d.system_stats.students || 0
        stats.totalGroups = d.system_stats.total_groups || d.system_stats.groups || 0
        stats.activeGroups = d.system_stats.groups || 0
        stats.admins = d.system_stats.admins || 0
        stats.leaders = d.system_stats.leaders || 0
        stats.newUsersWeek = d.system_stats.new_users_this_week || 0
      }

      // Role distribution
      if (d.role_distribution) {
        rawRoleDistribution.value = d.role_distribution
      }

      // Today attendance
      if (d.today_attendance) {
        todayAttendance.total = d.today_attendance.total || 0
        todayAttendance.present = d.today_attendance.present || 0
        todayAttendance.absent = d.today_attendance.absent || 0
        todayAttendance.late = d.today_attendance.late || 0
        todayAttendance.rate = d.today_attendance.rate || 0
      }

      // Month attendance
      if (d.month_attendance) {
        monthAttendance.total = d.month_attendance.total || 0
        monthAttendance.present = d.month_attendance.present || 0
        monthAttendance.absent = d.month_attendance.absent || 0
        monthAttendance.late = d.month_attendance.late || 0
        monthAttendance.rate = d.month_attendance.rate || 0
      }

      // Attendance trend
      if (d.attendance_trend) {
        attendanceTrend.value = d.attendance_trend
      }

      // Reports from dashboard
      if (d.reports) {
        reports.total = d.reports.total || 0
        reports.pending = d.reports.pending || 0
      }

      // Notifications count
      stats.notificationsCount = d.notifications_count || 0

      // Attendance records from month data
      stats.attendanceRecords = d.month_attendance?.total || 0

      // Top groups
      topGroups.value = d.top_groups || []

      // Recent users
      recentUsers.value = d.recent_users || []
    }

    // 2. Reports stats (more detailed)
    if (reportsRes.status === 'fulfilled') {
      const r = reportsRes.value
      reports.total = r.total || reports.total
      reports.pending = r.by_status?.pending || reports.pending
      reports.approved = r.by_status?.approved || 0
      reports.rejected = r.by_status?.rejected || 0
      reports.approvalRate = r.approval_rate || 0
    }

    // 3. Notifications count (override if available)
    if (notificationsRes.status === 'fulfilled') {
      const n = notificationsRes.value
      if (n.total !== undefined) {
        stats.notificationsCount = n.total
      }
    }

    // 4. Get attendance total records from stats endpoint
    try {
      const attStats = await api.getAttendanceStats()
      if (attStats?.total_records) {
        stats.attendanceRecords = attStats.total_records
      }
    } catch (e) {
      // silently fail
    }

    // 5. Recent logs
    if (logsRes.status === 'fulfilled') {
      const l = logsRes.value
      const items = Array.isArray(l) ? l : (l?.items || [])
      recentLogs.value = items.slice(0, 5).map(log => formatLog(log))
    }

  } catch (err) {
    console.error('Dashboard load error:', err)
    error.value = err.message || 'Ma\'lumotlarni yuklashda xatolik yuz berdi'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

// === HELPERS ===

// Format number with locale
const formatNumber = (num) => {
  return (num || 0).toLocaleString('uz-UZ')
}

// Format trend date (e.g., "2025-01-29" -> "29-yan")
const formatTrendDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const months = ['yan', 'fev', 'mar', 'apr', 'may', 'iyun', 'iyul', 'avg', 'sen', 'okt', 'noy', 'dek']
  return `${d.getDate()}-${months[d.getMonth()]}`
}

// Format log entry
const formatLog = (log) => {
  const iconMap = {
    'login': { icon: LogIn, bg: 'bg-blue-100', text: 'text-blue-600' },
    'logout': { icon: LogIn, bg: 'bg-slate-100', text: 'text-slate-600' },
    'create': { icon: UserPlus, bg: 'bg-emerald-100', text: 'text-emerald-600' },
    'update': { icon: FileEdit, bg: 'bg-amber-100', text: 'text-amber-600' },
    'delete': { icon: Trash, bg: 'bg-rose-100', text: 'text-rose-600' }
  }

  const action = log.action?.toLowerCase() || 'unknown'
  const iconData = iconMap[action] || { icon: Activity, bg: 'bg-slate-100', text: 'text-slate-600' }

  return {
    id: log.id,
    icon: markRaw(iconData.icon),
    bgClass: iconData.bg,
    iconClass: iconData.text,
    action: log.details || log.action || 'Noma\'lum amal',
    user: log.user_name || 'Tizim',
    module: log.module || '',
    time: formatTime(log.timestamp || log.created_at)
  }
}

// Format timestamp to relative time
const formatTime = (timestamp) => {
  if (!timestamp) return 'Hozir'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return 'Hozir'
  if (diff < 3600) return `${Math.floor(diff / 60)} daq oldin`
  if (diff < 86400) return `${Math.floor(diff / 3600)} soat oldin`
  if (diff < 604800) return `${Math.floor(diff / 86400)} kun oldin`
  return date.toLocaleDateString('uz-UZ')
}

// Get user initials
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

// Role styling helpers
const getRoleBgClass = (role) => {
  const map = {
    superadmin: 'bg-rose-100 text-rose-700',
    admin: 'bg-amber-100 text-amber-700',
    leader: 'bg-violet-100 text-violet-700',
    student: 'bg-blue-100 text-blue-700'
  }
  return map[role] || 'bg-slate-100 text-slate-700'
}

const getRoleBadgeClass = (role) => {
  const map = {
    superadmin: 'bg-rose-100 text-rose-700',
    admin: 'bg-amber-100 text-amber-700',
    leader: 'bg-violet-100 text-violet-700',
    student: 'bg-blue-100 text-blue-700'
  }
  return map[role] || 'bg-slate-100 text-slate-700'
}

const getRoleLabel = (role) => {
  const map = {
    superadmin: 'Super Admin',
    admin: 'Admin',
    leader: 'Lider',
    student: 'Talaba'
  }
  return map[role] || role
}

// Refresh
const refresh = async () => {
  refreshing.value = true
  await loadDashboard()
}

// === LIFECYCLE ===
onMounted(() => {
  loadDashboard()
})
</script>
