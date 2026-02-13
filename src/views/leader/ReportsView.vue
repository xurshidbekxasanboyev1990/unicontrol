<template>
  <div class="space-y-6">
    <!-- ========================================
         ESLATMA BANNER (Deadline Reminder)
         ======================================== -->
    <div 
      v-if="showDeadlineReminder"
      class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 p-4 shadow-lg"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3 text-white">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-white/20">
            <Bell :size="20" class="animate-bounce" />
          </div>
          <div>
            <p class="font-semibold">{{ $t('reports.deadlineReminder', { days: 3 }) }}</p>
            <p class="text-sm text-white/80">{{ $t('reports.monthlyReminder', { month: currentMonth }) }}</p>
          </div>
        </div>
        <button 
          @click.stop="closeDeadlineReminder"
          type="button"
          class="relative z-10 rounded-lg bg-white/20 p-2 text-white transition-all hover:bg-white/30"
        >
          <X :size="18" />
        </button>
      </div>
      <!-- Decorative circles -->
      <div class="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/10"></div>
      <div class="pointer-events-none absolute -bottom-4 -right-4 h-16 w-16 rounded-full bg-white/10"></div>
    </div>

    <!-- ========================================
         SARLAVHA (Header)
         ======================================== -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">{{ $t('reports.title') }}</h1>
        <p class="text-slate-500">{{ currentGroup?.name }} - {{ $t('reports.groupReports') }}</p>
      </div>
      
      <button
        @click="openCreateModal"
        class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600"
      >
        <Plus :size="20" />
        {{ $t('reports.newReport') }}
      </button>
    </div>

    <!-- ========================================
         FILTER TABS
         ======================================== -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex rounded-xl bg-slate-100 p-1">
        <button
          @click="activeTab = 'my'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'my' 
            ? 'bg-white text-emerald-600 shadow' 
            : 'text-slate-600 hover:text-slate-800'"
        >
          {{ $t('reports.myReports') }}
        </button>
      </div>

      <!-- Month/Year filter -->
      <div class="flex items-center gap-3">
        <select 
          v-model="selectedMonth"
          class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-700 focus:border-emerald-500 focus:outline-none"
        >
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
        
        <select 
          v-model="selectedYear"
          class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-700 focus:border-emerald-500 focus:outline-none"
        >
          <option value="2026">2026</option>
          <option value="2025">2025</option>
        </select>
      </div>
    </div>

    <!-- ========================================
         MENING HISOBOTLARIM (My Reports)
         ======================================== -->
    <div v-if="activeTab === 'my'" class="space-y-4">
      <div 
        v-for="report in myReports" 
        :key="report.id"
        class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-md"
      >
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex gap-4">
            <div 
              class="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl"
              :class="getStatusIconClass(report.status)"
            >
              <FileText :size="24" />
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-slate-800">{{ report.title }}</h3>
              <p class="mt-1 text-sm text-slate-500">{{ report.period }}</p>
              <div class="mt-2 flex flex-wrap items-center gap-2">
                <span 
                  class="rounded-lg px-2.5 py-1 text-xs font-medium"
                  :class="getStatusBadgeClass(report.status)"
                >
                  {{ getStatusText(report.status) }}
                </span>
                <span class="text-xs text-slate-400">
                  {{ $t('reports.created') }}: {{ report.createdAt }}
                </span>
                <!-- File indicators -->
                <span v-if="report.files?.images > 0" class="flex items-center gap-1 text-xs text-blue-500">
                  <ImageIcon :size="12" /> {{ report.files.images }}
                </span>
                <span v-if="report.files?.videos > 0" class="flex items-center gap-1 text-xs text-purple-500">
                  <Video :size="12" /> {{ report.files.videos }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button 
              @click="viewReport(report)"
              class="rounded-lg bg-slate-100 p-2.5 text-slate-600 transition-all hover:bg-slate-200"
              :title="$t('reports.view')"
            >
              <Eye :size="18" />
            </button>
            <button 
              @click="downloadReport(report)"
              class="rounded-lg bg-emerald-100 p-2.5 text-emerald-600 transition-all hover:bg-emerald-200"
              :title="$t('reports.downloadReport')"
            >
              <Download :size="18" />
            </button>
            <button 
              v-if="report.status === 'draft'"
              @click="editReport(report)"
              class="rounded-lg bg-blue-100 p-2.5 text-blue-600 transition-all hover:bg-blue-200"
              :title="$t('reports.editReport')"
            >
              <Pencil :size="18" />
            </button>
            <button 
              v-if="report.status === 'draft' || report.status === 'pending' || report.status === 'failed'"
              @click="deleteReport(report)"
              class="rounded-lg bg-red-100 p-2.5 text-red-600 transition-all hover:bg-red-200"
              :title="$t('reports.deleteReport')"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-xl bg-green-50 p-3 text-center">
            <p class="text-xl font-bold text-green-600">{{ report.stats?.attendance || 0 }}%</p>
            <p class="text-xs text-green-600/70">{{ $t('reports.attendanceStat') }}</p>
          </div>
          <div class="rounded-xl bg-blue-50 p-3 text-center">
            <p class="text-xl font-bold text-blue-600">{{ report.stats?.contract || 0 }}%</p>
            <p class="text-xs text-blue-600/70">{{ $t('reports.contractStat') }}</p>
          </div>
          <div class="rounded-xl bg-purple-50 p-3 text-center">
            <p class="text-xl font-bold text-purple-600">{{ report.stats?.activities || 0 }}</p>
            <p class="text-xs text-purple-600/70">{{ $t('reports.eventsStat') }}</p>
          </div>
          <div class="rounded-xl bg-orange-50 p-3 text-center">
            <p class="text-xl font-bold text-orange-600">{{ report.stats?.meetings || 0 }}</p>
            <p class="text-xs text-orange-600/70">{{ $t('reports.meetingsStat') }}</p>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div 
        v-if="myReports.length === 0"
        class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 py-16"
      >
        <FileText :size="48" class="mb-3 text-slate-300" />
        <p class="text-lg font-medium text-slate-500">{{ $t('reports.noReportsFound') }}</p>
        <p class="text-sm text-slate-400">{{ $t('reports.noReportsDesc') }}</p>
        <button
          @click="openCreateModal"
          class="mt-4 flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white"
        >
          <Plus :size="18" />
          {{ $t('reports.newReport') }}
        </button>
      </div>
    </div>

    <!-- ========================================
         BOSHQA GURUHLAR (Removed - Leaders can only see own reports)
         ======================================== -->

    <!-- ========================================
         HISOBOT YARATISH MODAL
         ======================================== -->
    <div 
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-2 pt-4 sm:p-4 sm:pt-10"
      @click.self="showCreateModal = false"
    >
      <div class="w-full max-w-4xl rounded-2xl bg-white shadow-2xl">
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-slate-200 p-4 sm:p-6">
          <div>
            <h2 class="text-xl font-bold text-slate-800">{{ $t('reports.createReport') }}</h2>
            <p class="text-sm text-slate-500">{{ currentGroup?.name }} - {{ getMonthLabel(newReport.month) }} {{ newReport.year }}</p>
          </div>
          <button 
            @click="showCreateModal = false"
            class="rounded-lg bg-slate-100 p-2 text-slate-500 hover:bg-slate-200"
          >
            <X :size="20" />
          </button>
        </div>

        <!-- Modal Body with Tabs -->
        <div class="max-h-[70vh] overflow-y-auto p-4 sm:p-6">
          <!-- Section Tabs -->
          <div class="mb-4 sm:mb-6 flex flex-wrap gap-1.5 sm:gap-2 border-b border-slate-200 pb-3 sm:pb-4 overflow-x-auto">
            <button
              v-for="section in reportSections"
              :key="section.id"
              @click="activeSection = section.id"
              class="flex items-center gap-1.5 sm:gap-2 rounded-lg px-2.5 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium transition-all whitespace-nowrap"
              :class="activeSection === section.id
                ? 'bg-emerald-500 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            >
              <component :is="section.icon" :size="16" />
              {{ section.label }}
              <span 
                v-if="section.auto"
                class="rounded bg-white/20 px-1.5 py-0.5 text-xs"
              >
                {{ $t('reports.autoTag') }}
              </span>
            </button>
          </div>

          <!-- ============ DAVOMAT SECTION (Auto) ============ -->
          <div v-if="activeSection === 'attendance'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-green-50 p-3 text-green-700">
              <CheckCircle :size="20" />
              <span class="text-sm">{{ $t('reports.autoFilledNote') }}</span>
            </div>

            <!-- Attendance Stats Grid -->
            <div class="grid grid-cols-2 gap-2 sm:gap-4 sm:grid-cols-4">
              <div class="rounded-xl border border-green-200 bg-green-50 p-3 sm:p-4 text-center">
                <p class="text-xl sm:text-3xl font-bold text-green-600">{{ autoData.attendance.rate }}%</p>
                <p class="text-xs sm:text-sm text-green-600/70">{{ $t('reports.overallAttendance') }}</p>
              </div>
              <div class="rounded-xl border border-blue-200 bg-blue-50 p-3 sm:p-4 text-center">
                <p class="text-xl sm:text-3xl font-bold text-blue-600">{{ autoData.attendance.present }}</p>
                <p class="text-xs sm:text-sm text-blue-600/70">{{ $t('reports.attended') }}</p>
              </div>
              <div class="rounded-xl border border-orange-200 bg-orange-50 p-3 sm:p-4 text-center">
                <p class="text-xl sm:text-3xl font-bold text-orange-600">{{ autoData.attendance.late }}</p>
                <p class="text-xs sm:text-sm text-orange-600/70">{{ $t('reports.late') }}</p>
              </div>
              <div class="rounded-xl border border-red-200 bg-red-50 p-3 sm:p-4 text-center">
                <p class="text-xl sm:text-3xl font-bold text-red-600">{{ autoData.attendance.absent }}</p>
                <p class="text-xs sm:text-sm text-red-600/70">{{ $t('reports.absentWithout') }}</p>
              </div>
            </div>

            <!-- Students Attendance Table -->
            <div class="rounded-xl border border-slate-200">
              <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
                <h4 class="font-semibold text-slate-700">{{ $t('reports.studentAttendance') }}</h4>
              </div>
              <div class="divide-y divide-slate-100">
                <div 
                  v-for="student in autoData.studentsAttendance" 
                  :key="student.id"
                  class="px-4 py-3"
                >
                  <div class="flex items-center justify-between gap-2">
                    <span class="text-sm font-medium text-slate-700 truncate min-w-0">{{ student.name }}</span>
                    <span 
                      class="flex-shrink-0 rounded-lg px-2 py-1 text-sm font-medium"
                      :class="student.rate >= 80 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                    >
                      {{ student.rate }}%
                    </span>
                  </div>
                  <div class="mt-1 flex items-center gap-3 text-xs">
                    <span class="text-green-600">✅ {{ student.present }} {{ $t('reports.lessons') }}</span>
                    <span class="text-red-600">❌ {{ student.absent }} {{ $t('reports.absent') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ============ KONTRAKT SECTION (Auto - Real Data) ============ -->
          <div v-if="activeSection === 'contract'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-green-50 p-3 text-green-700">
              <CheckCircle :size="20" />
              <span class="text-sm">{{ $t('reports.autoFilledNote') }} ({{ $t('reports.fromContractDB') }})</span>
            </div>

            <!-- Contract Stats -->
            <div class="grid grid-cols-2 gap-2 sm:gap-3 sm:grid-cols-4">
              <div class="rounded-xl border border-blue-200 bg-blue-50 p-3 sm:p-4 text-center">
                <p class="text-sm sm:text-xl font-bold text-blue-600 truncate">{{ formatMoney(autoData.contract.total) }}</p>
                <p class="text-[10px] sm:text-xs text-blue-600/70">{{ $t('reports.contractAmount') }}</p>
              </div>
              <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 sm:p-4 text-center">
                <p class="text-sm sm:text-xl font-bold text-emerald-600 truncate">{{ formatMoney(autoData.contract.paid) }}</p>
                <p class="text-[10px] sm:text-xs text-emerald-600/70">{{ $t('reports.paid') }}</p>
              </div>
              <div class="rounded-xl border border-red-200 bg-red-50 p-3 sm:p-4 text-center">
                <p class="text-sm sm:text-xl font-bold text-red-600 truncate">{{ formatMoney(contractsData.stats ? Math.abs(Number(contractsData.stats.total_debt || 0)) : 0) }}</p>
                <p class="text-[10px] sm:text-xs text-red-600/70">{{ $t('reports.debt') }}</p>
              </div>
              <div class="rounded-xl border border-purple-200 bg-purple-50 p-3 sm:p-4 text-center">
                <p class="text-sm sm:text-xl font-bold text-purple-600 truncate">{{ formatMoney(contractsData.stats ? Number(contractsData.stats.total_grant_amount || 0) : 0) }}</p>
                <p class="text-[10px] sm:text-xs text-purple-600/70">{{ $t('reports.grant') }}</p>
              </div>
            </div>

            <!-- Summary row -->
            <div class="grid grid-cols-3 gap-2 sm:gap-3">
              <div class="rounded-xl border border-emerald-100 bg-emerald-50 p-2.5 sm:p-3 text-center">
                <p class="text-lg sm:text-2xl font-bold text-emerald-700">{{ contractsData.stats?.fully_paid_count || 0 }}</p>
                <p class="text-[10px] sm:text-xs text-emerald-600">{{ $t('reports.fullyPaid') }}</p>
              </div>
              <div class="rounded-xl border border-red-100 bg-red-50 p-2.5 sm:p-3 text-center">
                <p class="text-lg sm:text-2xl font-bold text-red-700">{{ contractsData.stats?.with_debt_count || 0 }}</p>
                <p class="text-[10px] sm:text-xs text-red-600">{{ $t('reports.debtors') }}</p>
              </div>
              <div class="rounded-xl border border-indigo-100 bg-indigo-50 p-2.5 sm:p-3 text-center">
                <p class="text-lg sm:text-2xl font-bold text-indigo-700">{{ autoData.contract.rate }}%</p>
                <p class="text-[10px] sm:text-xs text-indigo-600">{{ $t('reports.averagePayment') }}</p>
              </div>
            </div>

            <!-- Students Contract Table -->
            <div class="rounded-xl border border-slate-200">
              <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
                <h4 class="font-semibold text-slate-700">{{ $t('reports.studentContractStatus') }}</h4>
              </div>
              <div class="divide-y divide-slate-100">
                <div 
                  v-for="student in autoData.studentsContract" 
                  :key="student.id"
                  class="px-4 py-3"
                >
                  <div class="flex items-center justify-between gap-2 mb-1">
                    <span class="text-sm font-medium text-slate-700 truncate min-w-0">{{ student.name }}</span>
                    <span 
                      class="flex-shrink-0 text-sm font-semibold"
                      :class="student.rate >= 100 ? 'text-emerald-600' : student.rate >= 50 ? 'text-blue-600' : 'text-red-600'"
                    >
                      {{ student.rate }}%
                    </span>
                  </div>
                  <div class="flex items-center gap-2 sm:gap-3">
                    <div class="flex-1 min-w-0">
                      <div class="h-2 overflow-hidden rounded-full bg-slate-200">
                        <div 
                          class="h-full rounded-full transition-all"
                          :class="student.rate >= 100 ? 'bg-emerald-500' : student.rate >= 50 ? 'bg-blue-500' : 'bg-red-500'"
                          :style="{ width: `${Math.min(student.rate, 100)}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div class="mt-1.5 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500">
                    <span>{{ formatMoney(student.paid) }} / {{ formatMoney(student.total) }}</span>
                    <span v-if="student.grant > 0" class="text-purple-500">Grant: {{ formatMoney(student.grant) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ============ GURUH FAOLIYATI SECTION (Manual) ============ -->
          <div v-if="activeSection === 'activities'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-700">
              <Pencil :size="20" />
              <span class="text-sm">{{ $t('reports.groupActivities') }}</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.eventsHeld') }}
              </label>
              <textarea
                v-model="newReport.activities.events"
                rows="4"
                :placeholder="$t('reports.eventsPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.achievements') }}
              </label>
              <textarea
                v-model="newReport.activities.achievements"
                rows="3"
                :placeholder="$t('reports.achievementsPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.additionalNotes') }}
              </label>
              <textarea
                v-model="newReport.activities.notes"
                rows="2"
                :placeholder="$t('reports.additionalNotesPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>
          </div>

          <!-- ============ OTA-ONALAR SECTION (Manual) ============ -->
          <div v-if="activeSection === 'parents'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-700">
              <Pencil :size="20" />
              <span class="text-sm">{{ $t('reports.parentWork') }}</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.meetingsHeld') }}
              </label>
              <textarea
                v-model="newReport.parents.meetings"
                rows="3"
                :placeholder="$t('reports.meetingsPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.individualTalks') }}
              </label>
              <textarea
                v-model="newReport.parents.conversations"
                rows="3"
                :placeholder="$t('reports.individualTalksPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="mb-2 block text-sm font-medium text-slate-700">
                  {{ $t('reports.meetingsCount') }}
                </label>
                <input
                  v-model.number="newReport.parents.meetingsCount"
                  type="number"
                  min="0"
                  class="w-full rounded-xl border border-slate-200 p-3 text-slate-700 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label class="mb-2 block text-sm font-medium text-slate-700">
                  {{ $t('reports.parentAttendees') }}
                </label>
                <input
                  v-model.number="newReport.parents.attendedParents"
                  type="number"
                  min="0"
                  class="w-full rounded-xl border border-slate-200 p-3 text-slate-700 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          <!-- ============ MUAMMOLAR SECTION (Manual) ============ -->
          <div v-if="activeSection === 'problems'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-amber-50 p-3 text-amber-700">
              <AlertCircle :size="20" />
              <span class="text-sm">{{ $t('reports.problemsNote') }}</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.mainProblems') }}
              </label>
              <textarea
                v-model="newReport.problems.main"
                rows="4"
                :placeholder="$t('reports.mainProblemsPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.solutionNeeded') }}
              </label>
              <textarea
                v-model="newReport.problems.needsSolution"
                rows="3"
                :placeholder="$t('reports.solutionNeededPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>
          </div>

          <!-- ============ REJALAR SECTION (Manual) ============ -->
          <div v-if="activeSection === 'plans'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-purple-50 p-3 text-purple-700">
              <Calendar :size="20" />
              <span class="text-sm">{{ $t('reports.nextMonthPlans') }}</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.plannedEvents') }}
              </label>
              <textarea
                v-model="newReport.plans.events"
                rows="3"
                :placeholder="$t('reports.plannedEventsPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                {{ $t('reports.goals') }}
              </label>
              <textarea
                v-model="newReport.plans.goals"
                rows="3"
                :placeholder="$t('reports.goalsPlaceholder')"
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>
          </div>

          <!-- ============ FAYLLAR SECTION ============ -->
          <div v-if="activeSection === 'files'" class="space-y-6">
            <div class="flex items-center gap-2 rounded-xl bg-indigo-50 p-3 text-indigo-700">
              <Upload :size="20" />
              <span class="text-sm">{{ $t('reports.uploadMedia') }}</span>
            </div>

            <!-- Images Upload -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <ImageIcon :size="18" class="text-blue-500" />
                {{ $t('reports.imagesMax') }}
              </label>
              <div class="grid grid-cols-3 gap-2 sm:grid-cols-5 sm:gap-4">
                <!-- Uploaded images preview -->
                <div 
                  v-for="(img, index) in uploadedImages" 
                  :key="index"
                  class="group relative aspect-square overflow-hidden rounded-xl border border-slate-200"
                >
                  <img :src="img.preview" class="h-full w-full object-cover" />
                  <button
                    @click="removeImage(index)"
                    class="absolute right-1 top-1 rounded-full bg-red-500 p-1 text-white opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    <X :size="14" />
                  </button>
                </div>
                <!-- Upload button -->
                <label 
                  v-if="uploadedImages.length < 10"
                  class="flex aspect-square cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 transition-all hover:border-emerald-400 hover:bg-emerald-50"
                >
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    class="hidden"
                    @change="handleImageUpload"
                  />
                  <Plus :size="24" class="text-slate-400" />
                  <span class="mt-1 text-xs text-slate-500">{{ $t('reports.addImage') }}</span>
                </label>
              </div>
            </div>

            <!-- Videos Upload -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <Video :size="18" class="text-purple-500" />
                {{ $t('reports.videosMax') }}
              </label>
              <div class="space-y-3">
                <!-- Uploaded videos -->
                <div 
                  v-for="(video, index) in uploadedVideos" 
                  :key="index"
                  class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3"
                >
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100">
                      <Video :size="20" class="text-purple-600" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-700">{{ video.name }}</p>
                      <p class="text-xs text-slate-500">{{ formatFileSize(video.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click="removeVideo(index)"
                    class="rounded-lg bg-red-100 p-2 text-red-600 hover:bg-red-200"
                  >
                    <X :size="16" />
                  </button>
                </div>

                <!-- Upload button -->
                <label 
                  v-if="uploadedVideos.length < 3"
                  class="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-6 transition-all hover:border-purple-400 hover:bg-purple-50"
                >
                  <input
                    type="file"
                    accept="video/*"
                    class="hidden"
                    @change="handleVideoUpload"
                  />
                  <Upload :size="20" class="text-slate-400" />
                  <span class="text-sm text-slate-500">{{ $t('reports.uploadVideo') }}</span>
                </label>
              </div>
            </div>

            <!-- Documents Upload -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <FileText :size="18" class="text-emerald-500" />
                {{ $t('reports.documentsMax') }}
              </label>
              <div class="space-y-2">
                <!-- Uploaded documents -->
                <div 
                  v-for="(doc, index) in uploadedDocs" 
                  :key="index"
                  class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3"
                >
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                      <FileText :size="20" class="text-emerald-600" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-700">{{ doc.name }}</p>
                      <p class="text-xs text-slate-500">{{ formatFileSize(doc.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click="removeDoc(index)"
                    class="rounded-lg bg-red-100 p-2 text-red-600 hover:bg-red-200"
                  >
                    <X :size="16" />
                  </button>
                </div>

                <!-- Upload button -->
                <label 
                  v-if="uploadedDocs.length < 5"
                  class="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-4 transition-all hover:border-emerald-400 hover:bg-emerald-50"
                >
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    class="hidden"
                    @change="handleDocUpload"
                  />
                  <Upload :size="18" class="text-slate-400" />
                  <span class="text-sm text-slate-500">{{ $t('reports.uploadDocument') }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-t border-slate-200 p-4 sm:p-6">
          <div class="flex items-center gap-4">
            <span class="text-sm text-slate-500">
              <span class="font-medium text-emerald-600">{{ completedSections }}</span> / {{ reportSections.length }} {{ $t('reports.sectionsCompleted') }}
            </span>
          </div>
          <div class="flex gap-3">
            <button
              @click="saveDraft"
              class="rounded-xl border border-slate-200 px-5 py-2.5 font-medium text-slate-600 transition-all hover:bg-slate-100"
            >
              {{ $t('reports.saveDraft') }}
            </button>
            <button
              @click="submitReport"
              class="rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600"
            >
              {{ $t('reports.submitReport') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================
         VIEW REPORT MODAL
         ======================================== -->
    <div 
      v-if="showViewModal && selectedReport"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 pt-10"
      @click.self="showViewModal = false"
    >
      <div class="w-full max-w-3xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 p-6">
          <div>
            <h2 class="text-xl font-bold text-slate-800">{{ selectedReport.title }}</h2>
            <p class="text-sm text-slate-500">{{ selectedReport.period }}</p>
          </div>
          <button 
            @click="showViewModal = false"
            class="rounded-lg bg-slate-100 p-2 text-slate-500 hover:bg-slate-200"
          >
            <X :size="20" />
          </button>
        </div>
        
        <div class="max-h-[70vh] overflow-y-auto p-6">
          <!-- Stats Summary -->
          <div class="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div class="rounded-xl bg-green-50 p-4 text-center">
              <p class="text-2xl font-bold text-green-600">{{ selectedReport.stats?.attendance || 0 }}%</p>
              <p class="text-xs text-green-600/70">{{ $t('reports.attendanceStat') }}</p>
            </div>
            <div class="rounded-xl bg-blue-50 p-4 text-center">
              <p class="text-2xl font-bold text-blue-600">{{ selectedReport.stats?.contract || 0 }}%</p>
              <p class="text-xs text-blue-600/70">{{ $t('reports.contractStat') }}</p>
            </div>
            <div class="rounded-xl bg-purple-50 p-4 text-center">
              <p class="text-2xl font-bold text-purple-600">{{ selectedReport.stats?.activities || 0 }}</p>
              <p class="text-xs text-purple-600/70">{{ $t('reports.eventsStat') }}</p>
            </div>
            <div class="rounded-xl bg-orange-50 p-4 text-center">
              <p class="text-2xl font-bold text-orange-600">{{ selectedReport.stats?.meetings || 0 }}</p>
              <p class="text-xs text-orange-600/70">{{ $t('reports.meetingsStat') }}</p>
            </div>
          </div>

          <!-- Report Content -->
          <div v-if="selectedReport.content" class="space-y-4">
            <div v-if="selectedReport.content.activities" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">{{ $t('reports.groupActivity') }}</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.activities }}</p>
            </div>
            <div v-if="selectedReport.content.parents" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">{{ $t('reports.parentWorkLabel') }}</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.parents }}</p>
            </div>
            <div v-if="selectedReport.content.problems" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">{{ $t('reports.problems') }}</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.problems }}</p>
            </div>
            <div v-if="selectedReport.content.plans" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">{{ $t('reports.nextPlans') }}</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.plans }}</p>
            </div>
          </div>

          <!-- Attached Files -->
          <div v-if="selectedReport.files" class="mt-4 flex flex-wrap gap-2">
            <span v-if="selectedReport.files.images > 0" class="flex items-center gap-1 rounded-lg bg-blue-100 px-3 py-1.5 text-sm text-blue-700">
              <ImageIcon :size="14" /> {{ selectedReport.files.images }} {{ $t('reports.imagesLabel') }}
            </span>
            <span v-if="selectedReport.files.videos > 0" class="flex items-center gap-1 rounded-lg bg-purple-100 px-3 py-1.5 text-sm text-purple-700">
              <Video :size="14" /> {{ selectedReport.files.videos }} {{ $t('reports.videosLabel') }}
            </span>
            <span v-if="selectedReport.files.docs > 0" class="flex items-center gap-1 rounded-lg bg-emerald-100 px-3 py-1.5 text-sm text-emerald-700">
              <FileText :size="14" /> {{ selectedReport.files.docs }} {{ $t('reports.documentsLabel') }}
            </span>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t border-slate-200 p-6">
          <button
            @click="downloadReport(selectedReport)"
            class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white"
          >
            <Download :size="18" />
            {{ $t('reports.downloadPdf') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ReportsView.vue - Guruh sardori hisobotlar sahifasi
 * 
 * Asosiy funksiyalar:
 * 1. Avtomatik ma'lumotlar - Davomat va Kontrakt (tizimdan)
 * 2. Qo'lda kiritish - Faoliyat, Ota-onalar, Muammolar, Rejalar
 * 3. Fayl yuklash - Rasmlar, Videolar, Hujjatlar
 * 4. Eslatma - Muddat yaqinlashganda ogohlantirish
 */

import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import {
    AlertCircle,
    Bell,
    Calendar,
    CheckCircle,
    Download,
    Eye,
    FileText,
    Image as ImageIcon,
    Pencil,
    Plus,
    Trash2,
    Upload,
    Video,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

// ============ STORES ============
const dataStore = useDataStore()
const authStore = useAuthStore()
const toastStore = useToastStore()
const langStore = useLanguageStore()
const { t } = langStore

// ============ STATE ============
const activeTab = ref('my')
const selectedMonth = ref(new Date().getMonth() + 1)
const selectedYear = ref('2026')
const selectedOtherGroup = ref(null)
const showCreateModal = ref(false)
const showViewModal = ref(false)
const selectedReport = ref(null)
const activeSection = ref('attendance')
const showDeadlineReminder = ref(true)
const loading = ref(false)
const saving = ref(false)
const groupInfo = ref(null)
const groupStudentsList = ref([])
const contractsData = ref({ items: [], stats: null })

// File uploads
const uploadedImages = ref([])
const uploadedVideos = ref([])
const uploadedDocs = ref([])

// ============ REPORT FORM ============
const newReport = ref({
  month: new Date().getMonth() + 1,
  year: 2026,
  activities: {
    events: '',
    achievements: '',
    notes: ''
  },
  parents: {
    meetings: '',
    conversations: '',
    meetingsCount: 0,
    attendedParents: 0
  },
  problems: {
    main: '',
    needsSolution: ''
  },
  plans: {
    events: '',
    goals: ''
  }
})

// ============ REPORT SECTIONS CONFIG ============
const reportSections = computed(() => [
  { id: 'attendance', label: t('reports.sectionAttendance'), icon: CheckCircle, auto: true },
  { id: 'contract', label: t('reports.sectionContract'), icon: FileText, auto: true },
  { id: 'activities', label: t('reports.sectionActivities'), icon: Calendar, auto: false },
  { id: 'parents', label: t('reports.sectionParents'), icon: Bell, auto: false },
  { id: 'problems', label: t('reports.sectionProblems'), icon: AlertCircle, auto: false },
  { id: 'plans', label: t('reports.sectionPlans'), icon: Calendar, auto: false },
  { id: 'files', label: t('reports.sectionFiles'), icon: Upload, auto: false }
])

// ============ MONTHS CONFIG ============
const months = computed(() => [
  { value: 1, label: t('reports.january') },
  { value: 2, label: t('reports.february') },
  { value: 3, label: t('reports.march') },
  { value: 4, label: t('reports.april') },
  { value: 5, label: t('reports.may') },
  { value: 6, label: t('reports.june') },
  { value: 7, label: t('reports.july') },
  { value: 8, label: t('reports.august') },
  { value: 9, label: t('reports.september') },
  { value: 10, label: t('reports.october') },
  { value: 11, label: t('reports.november') },
  { value: 12, label: t('reports.december') }
])

// ============ COMPUTED ============

// Joriy oy nomi
const currentMonth = computed(() => {
  return months.value.find(m => m.value === selectedMonth.value)?.label || ''
})

// Joriy guruh - API dan olish
const currentGroup = computed(() => {
  return groupInfo.value
})

// Boshqa guruhlar
const otherGroups = computed(() => {
  if (!groupInfo.value) return []
  return dataStore.groups.filter(g => g.id !== groupInfo.value.id)
})

// Guruh talabalari
const groupStudents = computed(() => {
  return groupStudentsList.value
})

// Avtomatik ma'lumotlar (Davomat va Kontrakt)
const autoData = computed(() => {
  const students = groupStudents.value
  const groupId = currentGroup.value?.id
  
  // Davomat statistikasi
  const attendanceRecords = dataStore.attendanceRecords.filter(r => {
    const student = dataStore.students.find(s => s.id === r.studentId)
    return student?.groupId === groupId
  })
  
  const present = attendanceRecords.filter(r => r.status === 'present').length
  const late = attendanceRecords.filter(r => r.status === 'late').length
  const absent = attendanceRecords.filter(r => r.status === 'absent').length
  const total = attendanceRecords.length
  const attendanceRate = total > 0 ? Math.round((present + late) / total * 100) : 0

  // Talabalar davomati
  const studentsAttendance = students.map(s => {
    const records = dataStore.attendanceRecords.filter(r => r.studentId === s.id)
    const sPresent = records.filter(r => r.status === 'present').length
    const sAbsent = records.filter(r => r.status === 'absent').length
    const sTotal = records.length
    return {
      id: s.id,
      name: s.name,
      present: sPresent,
      absent: sAbsent,
      rate: sTotal > 0 ? Math.round((sPresent / sTotal) * 100) : 0
    }
  })

  // Kontrakt statistikasi - REAL DATA from contracts API
  const cStats = contractsData.value.stats
  const contractTotal = cStats ? Number(cStats.total_contract_amount || 0) : 0
  const contractPaid = cStats ? Number(cStats.total_paid || 0) : 0
  const contractRate = cStats ? Math.round(cStats.payment_percentage || 0) : 0

  // Talabalar kontrakt holati - REAL DATA
  const studentsContract = (contractsData.value.items || []).map(c => {
    const amount = Number(c.contract_amount || 0)
    const paid = Number(c.total_paid || 0)
    const grant = Number(c.grant_amount || 0)
    const debt = Math.abs(Number(c.debt_amount || 0))
    return {
      id: c.student_id,
      name: c.student_name || 'Noma\'lum',
      paid: paid,
      total: amount,
      grant: grant,
      debt: debt,
      rate: amount > 0 ? Math.round((paid / amount) * 100) : 0
    }
  })

  return {
    attendance: {
      rate: attendanceRate,
      present,
      late,
      absent
    },
    studentsAttendance,
    contract: {
      rate: contractRate,
      paid: contractPaid,
      total: contractTotal
    },
    studentsContract
  }
})

// Mening hisobotlarim (from API)
const myReports = ref([])

// Load group info and students from dashboard API
const loadGroupData = async () => {
  try {
    const dashboardResp = await api.request('/dashboard/leader')
    if (dashboardResp?.group) {
      groupInfo.value = dashboardResp.group
    }
    
    // Load students for this group
    if (groupInfo.value?.id) {
      try {
        const studentsResp = await api.request(`/students?group_id=${groupInfo.value.id}&page_size=100`)
        if (studentsResp?.items) {
          groupStudentsList.value = studentsResp.items
        } else if (Array.isArray(studentsResp)) {
          groupStudentsList.value = studentsResp
        }
      } catch (e) {
        console.log('Students API not available')
      }

      // Load real contract data from contracts API
      try {
        const contractsResp = await api.getGroupContracts(groupInfo.value.id, { academic_year: '2025-2026', page_size: 200 })
        if (contractsResp) {
          contractsData.value = {
            items: contractsResp.items || [],
            stats: contractsResp.stats || null,
          }
        }
      } catch (e) {
        console.log('Contracts API not available:', e)
      }
    }
  } catch (e) {
    console.error('Error loading group data:', e)
  }
}

// Load reports from API
const loadReports = async () => {
  loading.value = true
  try {
    if (!groupInfo.value?.id) return
    
    // Try to load from API, but fallback to local storage if not available
    try {
      const response = await api.request('/reports?page_size=50')
      if (response?.items && response.items.length > 0) {
        // Filter reports for current group
        const groupReports = response.items.filter(r => r.group_id === groupInfo.value.id)
        myReports.value = groupReports.map(r => ({
          id: r.id,
          title: r.name || r.title || 'Hisobot',
          period: r.date_from ? `${new Date(r.date_from).toLocaleDateString('uz-UZ')} - ${new Date(r.date_to).toLocaleDateString('uz-UZ')}` : '',
          month: r.date_from ? new Date(r.date_from).getMonth() + 1 : null,
          year: r.date_from ? new Date(r.date_from).getFullYear() : null,
          status: r.status || 'pending',
          createdAt: new Date(r.created_at).toLocaleDateString('uz-UZ'),
          stats: { attendance: 0, contract: 0, activities: 0, meetings: 0 },
          files: { images: 0, videos: 0, docs: 0 },
          content: {}
        }))
      }
    } catch (apiErr) {
      console.log('Reports API not available, using local data')
      // Load from localStorage if available
      const saved = localStorage.getItem(`reports_${groupInfo.value.id}`)
      if (saved) {
        myReports.value = JSON.parse(saved)
      }
    }
  } catch (err) {
    console.error('Error loading reports:', err)
  } finally {
    loading.value = false
  }
}

// Boshqa guruhlar hisobotlari
const otherGroupsReports = ref([])

const loadOtherReports = async () => {
  try {
    if (!groupInfo.value?.id) return
    
    // Try to load from API
    try {
      const response = await api.request('/reports?page_size=50')
      if (response?.items && response.items.length > 0) {
        // Filter reports for other groups
        const otherReports = response.items.filter(r => r.group_id && r.group_id !== groupInfo.value.id)
        otherGroupsReports.value = otherReports.map(r => ({
          id: r.id,
          title: r.name || r.title || 'Hisobot',
          groupName: r.group_name || 'Noma\'lum',
          groupId: r.group_id,
          period: r.date_from ? `${new Date(r.date_from).toLocaleDateString('uz-UZ')}` : ''
        }))
      }
    } catch (apiErr) {
      console.log('Other reports API not available')
      // Keep empty - no local fallback for other groups
    }
  } catch (err) {
    console.error('Error loading other reports:', err)
  }
}

const filteredOtherReports = computed(() => {
  if (selectedOtherGroup.value) {
    return otherGroupsReports.value.filter(r => r.groupId === selectedOtherGroup.value)
  }
  return otherGroupsReports.value
})

// To'ldirilgan bo'limlar soni
const completedSections = computed(() => {
  let count = 2 // Davomat va Kontrakt doimo to'liq
  
  if (newReport.value.activities.events || newReport.value.activities.achievements) count++
  if (newReport.value.parents.meetings || newReport.value.parents.meetingsCount > 0) count++
  if (newReport.value.problems.main) count++
  if (newReport.value.plans.events || newReport.value.plans.goals) count++
  if (uploadedImages.value.length > 0 || uploadedVideos.value.length > 0) count++
  
  return count
})

// ============ METHODS ============

// Oy nomini olish
const getMonthLabel = (month) => {
  return months.value.find(m => m.value === month)?.label || ''
}

// Pul formatini chiqarish
const formatMoney = (amount) => {
  if (amount == null || amount === 0) return '0 so\'m'
  const num = Number(amount)
  if (num === 0) return '0 so\'m'
  const absNum = Math.abs(num)
  const sign = num < 0 ? '-' : ''
  if (absNum >= 1_000_000_000) return sign + (absNum / 1_000_000_000).toFixed(1) + ' mlrd'
  if (absNum >= 1_000_000) return sign + (absNum / 1_000_000).toFixed(1) + ' mln'
  if (absNum >= 1_000) return sign + (absNum / 1_000).toFixed(0) + ' ming'
  return new Intl.NumberFormat('uz-UZ').format(num) + ' so\'m'
}

// Fayl hajmini formatlab chiqarish
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Status icon class
const getStatusIconClass = (status) => {
  const classes = {
    approved: 'bg-green-100 text-green-600',
    pending: 'bg-amber-100 text-amber-600',
    draft: 'bg-slate-100 text-slate-600',
    rejected: 'bg-red-100 text-red-600'
  }
  return classes[status] || classes.draft
}

// Status badge class
const getStatusBadgeClass = (status) => {
  const classes = {
    approved: 'bg-green-100 text-green-700',
    pending: 'bg-amber-100 text-amber-700',
    draft: 'bg-slate-100 text-slate-700',
    rejected: 'bg-red-100 text-red-700'
  }
  return classes[status] || classes.draft
}

// Status text
const getStatusText = (status) => {
  const texts = {
    approved: t('reports.statusApproved'),
    pending: t('reports.statusReviewing'),
    draft: t('reports.statusDraft'),
    rejected: t('reports.statusRejected')
  }
  return texts[status] || t('reports.statusUnknown')
}

// Eslatmani yopish
const closeDeadlineReminder = () => {
  showDeadlineReminder.value = false
}

// ============ FILE HANDLERS ============

// Rasm yuklash
const handleImageUpload = (event) => {
  const files = event.target.files
  const remaining = 10 - uploadedImages.value.length
  
  for (let i = 0; i < Math.min(files.length, remaining); i++) {
    const file = files[i]
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedImages.value.push({
        file,
        name: file.name,
        preview: e.target.result
      })
    }
    reader.readAsDataURL(file)
  }
  event.target.value = ''
}

// Rasm o'chirish
const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

// Video yuklash
const handleVideoUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 50MB limit
  if (file.size > 50 * 1024 * 1024) {
    toastStore.error(t('reports.videoSizeError'))
    return
  }
  
  uploadedVideos.value.push({
    file,
    name: file.name,
    size: file.size
  })
  event.target.value = ''
}

// Video o'chirish
const removeVideo = (index) => {
  uploadedVideos.value.splice(index, 1)
}

// Hujjat yuklash
const handleDocUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  uploadedDocs.value.push({
    file,
    name: file.name,
    size: file.size
  })
  event.target.value = ''
}

// Hujjat o'chirish
const removeDoc = (index) => {
  uploadedDocs.value.splice(index, 1)
}

// ============ REPORT ACTIONS ============

// Modal ochish
const openCreateModal = () => {
  // Reset form
  newReport.value = {
    month: new Date().getMonth() + 1,
    year: 2026,
    activities: { events: '', achievements: '', notes: '' },
    parents: { meetings: '', conversations: '', meetingsCount: 0, attendedParents: 0 },
    problems: { main: '', needsSolution: '' },
    plans: { events: '', goals: '' }
  }
  uploadedImages.value = []
  uploadedVideos.value = []
  uploadedDocs.value = []
  activeSection.value = 'attendance'
  showCreateModal.value = true
}

// Qoralama saqlash
const saveDraft = () => {
  const report = {
    id: Date.now(),
    title: t('reports.monthlyReport', { month: getMonthLabel(newReport.value.month) }),
    period: `${getMonthLabel(newReport.value.month)} ${newReport.value.year}`,
    status: 'draft',
    createdAt: new Date().toLocaleDateString('uz-UZ'),
    stats: {
      attendance: autoData.value.attendance.rate,
      contract: autoData.value.contract.rate,
      activities: newReport.value.activities.events ? 1 : 0,
      meetings: newReport.value.parents.meetingsCount
    },
    files: {
      images: uploadedImages.value.length,
      videos: uploadedVideos.value.length,
      docs: uploadedDocs.value.length
    },
    content: {
      activities: newReport.value.activities.events,
      parents: newReport.value.parents.meetings,
      problems: newReport.value.problems.main,
      plans: newReport.value.plans.events
    }
  }
  
  myReports.value.unshift(report)
  showCreateModal.value = false
  toastStore.success(t('reports.draftSaved'))
}

// Hisobot topshirish
const submitReport = async () => {
  saving.value = true
  try {
    // Create report object for local storage
    const report = {
      id: Date.now(),
      title: t('reports.monthlyReport', { month: getMonthLabel(newReport.value.month) }),
      period: `${getMonthLabel(newReport.value.month)} ${newReport.value.year}`,
      month: newReport.value.month,
      year: newReport.value.year,
      status: 'pending',
      createdAt: new Date().toLocaleDateString('uz-UZ'),
      stats: {
        attendance: autoData.value.attendance.rate,
        contract: autoData.value.contract.rate,
        activities: newReport.value.activities.events ? 1 : 0,
        meetings: newReport.value.parents.meetingsCount
      },
      files: {
        images: uploadedImages.value.length,
        videos: uploadedVideos.value.length,
        docs: uploadedDocs.value.length
      },
      content: {
        activities: newReport.value.activities.events,
        achievements: newReport.value.activities.achievements,
        parents: newReport.value.parents.meetings,
        problems: newReport.value.problems.main,
        plans: newReport.value.plans.events
      }
    }

    // Save to backend
    let savedToBackend = false
    try {
      const startDate = new Date(newReport.value.year, newReport.value.month - 1, 1)
      const endDate = new Date(newReport.value.year, newReport.value.month, 0)
      
      const reportData = {
        name: report.title,
        description: `${groupInfo.value?.name || 'Guruh'} - ${report.title}. Davomat: ${autoData.value.attendance.rate}%, Kontrakt: ${autoData.value.contract.rate}%`,
        report_type: 'attendance',
        format: 'pdf',
        date_from: startDate.toISOString().split('T')[0],
        date_to: endDate.toISOString().split('T')[0],
        group_id: groupInfo.value?.id || null
      }
      
      console.log('Creating report with data:', reportData)
      const response = await api.createReport(reportData)
      console.log('Report created response:', response)
      if (response?.id) {
        report.id = response.id
        report.status = response.status || 'pending'
        savedToBackend = true
      }
    } catch (apiErr) {
      console.error('Report creation API error:', apiErr)
      console.error('Error details:', apiErr?.data, apiErr?.status)
      // Show warning but continue with local save
      toastStore.warning(t('reports.savedLocallyWarning') || 'Serverga saqlanmadi, lokal saqlandi')
    }
    
    // Add to local list
    myReports.value.unshift(report)
    
    // Save to localStorage as backup
    if (groupInfo.value?.id) {
      localStorage.setItem(`reports_${groupInfo.value.id}`, JSON.stringify(myReports.value))
    }
    
    showCreateModal.value = false
    toastStore.success(savedToBackend 
      ? (t('reports.reportSubmitted') || 'Hisobot muvaffaqiyatli topshirildi')
      : (t('reports.reportSavedLocally') || 'Hisobot lokal saqlandi')
    )
  } catch (err) {
    console.error('Error submitting report:', err)
    toastStore.error(t('reports.submitError'))
  } finally {
    saving.value = false
  }
}

// Load data on mount
onMounted(async () => {
  loading.value = true
  try {
    // First load group info from dashboard API
    await loadGroupData()
    
    // Then load other data
    await Promise.all([
      dataStore.fetchGroups(),
      loadReports(),
      loadOtherReports()
    ])
  } catch (e) {
    console.error('Error loading data:', e)
  } finally {
    loading.value = false
  }
})

// Hisobotni ko'rish
const viewReport = (report) => {
  selectedReport.value = report
  showViewModal.value = true
}

// Hisobotni tahrirlash
const editReport = (report) => {
  // Fill form with report data
  newReport.value.month = months.value.find(m => report.period.includes(m.label))?.value || 1
  newReport.value.activities.events = report.content?.activities || ''
  newReport.value.parents.meetings = report.content?.parents || ''
  newReport.value.problems.main = report.content?.problems || ''
  newReport.value.plans.events = report.content?.plans || ''
  
  showCreateModal.value = true
}

// Hisobotni yuklab olish (PDF)
const downloadReport = async (report) => {
  toastStore.info(t('reports.pdfDownloading'))
  
  try {
    // ═══ LOKAL PDF GENERATSIYA ═══
    // Leader hisobotlari kompozit (davomat + kontrakt + faoliyat) bo'lgani uchun
    // har doim lokal PDF generatsiya qilamiz - barcha ma'lumotlar to'liq ko'rinadi
    const group = groupInfo.value || {}
    const stats = report.stats || {}
    const content = report.content || {}
    const data = autoData.value
    
    // Create PDF document
    const doc = new jsPDF('p', 'mm', 'a4')
    const pageWidth = doc.internal.pageSize.getWidth()
    let y = 20
    
    // Title
    doc.setFontSize(20)
    doc.setTextColor(30, 41, 59)
    doc.text(report.title, pageWidth / 2, y, { align: 'center' })
    y += 10
    
    // Subtitle - Group info
    doc.setFontSize(12)
    doc.setTextColor(100, 116, 139)
    doc.text(`Guruh: ${group.name || 'N/A'}`, pageWidth / 2, y, { align: 'center' })
    y += 6
    doc.text(`Davr: ${report.period}`, pageWidth / 2, y, { align: 'center' })
    y += 6
    doc.text(`Sana: ${report.createdAt || new Date().toLocaleDateString('uz-UZ')}`, pageWidth / 2, y, { align: 'center' })
    y += 15
    
    // Line separator
    doc.setDrawColor(16, 185, 129)
    doc.setLineWidth(0.5)
    doc.line(20, y, pageWidth - 20, y)
    y += 15
    
    // Statistics section header
    doc.setFontSize(14)
    doc.setTextColor(30, 41, 59)
    doc.text('Umumiy Ko\'rsatkichlar', 20, y)
    y += 10
    
    // Statistics boxes
    const attRate = stats.attendance || data?.attendance?.rate || 0
    const conRate = stats.contract || data?.contract?.rate || 0
    const statData = [
      { label: 'Davomat', value: `${attRate}%`, color: [34, 197, 94] },
      { label: 'Kontrakt', value: `${conRate}%`, color: [59, 130, 246] },
      { label: 'Tadbirlar', value: `${stats.activities || 0}`, color: [245, 158, 11] },
      { label: 'Yig\'ilishlar', value: `${stats.meetings || 0}`, color: [239, 68, 68] }
    ]
    
    const boxWidth = 40
    const boxHeight = 25
    const startX = (pageWidth - (boxWidth * 4 + 15)) / 2
    
    statData.forEach((stat, i) => {
      const x = startX + i * (boxWidth + 5)
      
      // Box background
      doc.setFillColor(stat.color[0], stat.color[1], stat.color[2])
      doc.roundedRect(x, y, boxWidth, boxHeight, 3, 3, 'F')
      
      // Value
      doc.setFontSize(16)
      doc.setTextColor(255, 255, 255)
      doc.text(stat.value, x + boxWidth / 2, y + 12, { align: 'center' })
      
      // Label
      doc.setFontSize(9)
      doc.text(stat.label, x + boxWidth / 2, y + 20, { align: 'center' })
    })
    y += boxHeight + 15
    
    // ═══ 1. DAVOMAT JADVALI ═══
    if (data?.studentsAttendance?.length > 0) {
      doc.setFontSize(14)
      doc.setTextColor(30, 41, 59)
      doc.text('Talabalar Davomati', 20, y)
      y += 5
      
      const attendanceTableData = data.studentsAttendance.map((s, i) => [
        i + 1,
        s.name,
        s.present,
        s.absent,
        `${s.rate}%`
      ])
      
      autoTable(doc, {
        startY: y,
        head: [['#', 'Talaba', 'Kelgan', 'Kelmagan', 'Foiz']],
        body: attendanceTableData,
        theme: 'striped',
        headStyles: { fillColor: [16, 185, 129], textColor: 255 },
        styles: { fontSize: 10, cellPadding: 3 },
        columnStyles: {
          0: { cellWidth: 10 },
          1: { cellWidth: 70 },
          2: { cellWidth: 25, halign: 'center' },
          3: { cellWidth: 25, halign: 'center' },
          4: { cellWidth: 25, halign: 'center' }
        }
      })
      
      y = doc.lastAutoTable.finalY + 15
    }
    
    // ═══ 2. KONTRAKT JADVALI ═══
    if (data?.studentsContract?.length > 0) {
      // Check if we need a new page
      if (y > 200) {
        doc.addPage()
        y = 20
      }
      
      doc.setFontSize(14)
      doc.setTextColor(30, 41, 59)
      doc.text('Talabalar Kontrakt Holati', 20, y)
      y += 5
      
      // Contract summary row
      const contractSummary = [
        ['Jami kontrakt', formatMoney(data.contract?.total || 0)],
        ['To\'langan', formatMoney(data.contract?.paid || 0)],
        ['To\'lov foizi', `${data.contract?.rate || 0}%`]
      ]
      
      autoTable(doc, {
        startY: y,
        head: [['Ko\'rsatkich', 'Qiymat']],
        body: contractSummary,
        theme: 'striped',
        headStyles: { fillColor: [59, 130, 246], textColor: 255 },
        styles: { fontSize: 10, cellPadding: 3 },
        columnStyles: {
          0: { cellWidth: 80 },
          1: { cellWidth: 75, halign: 'right' }
        }
      })
      
      y = doc.lastAutoTable.finalY + 10
      
      // Students contract table
      const contractTableData = data.studentsContract.map((s, i) => [
        i + 1,
        s.name,
        formatMoney(s.total),
        formatMoney(s.paid),
        formatMoney(s.debt || 0),
        `${s.rate}%`
      ])
      
      autoTable(doc, {
        startY: y,
        head: [['#', 'Talaba', 'Kontrakt', 'To\'langan', 'Qarz', 'Foiz']],
        body: contractTableData,
        theme: 'striped',
        headStyles: { fillColor: [59, 130, 246], textColor: 255 },
        styles: { fontSize: 9, cellPadding: 2.5 },
        columnStyles: {
          0: { cellWidth: 8 },
          1: { cellWidth: 45 },
          2: { cellWidth: 30, halign: 'right' },
          3: { cellWidth: 30, halign: 'right' },
          4: { cellWidth: 25, halign: 'right' },
          5: { cellWidth: 18, halign: 'center' }
        }
      })
      
      y = doc.lastAutoTable.finalY + 15
    }
    
    // Check if we need a new page
    if (y > 250) {
      doc.addPage()
      y = 20
    }
    
    // ═══ 3. MATNLI BO'LIMLAR ═══
    const sections = [
      { title: 'Guruh Faoliyati', text: content.activities },
      { title: 'Yutuqlar', text: content.achievements },
      { title: 'Ota-onalar bilan ishlash', text: content.parents },
      { title: 'Muammolar', text: content.problems },
      { title: 'Rejalar', text: content.plans }
    ]
    
    sections.forEach(section => {
      if (section.text) {
        if (y > 260) {
          doc.addPage()
          y = 20
        }
        
        doc.setFontSize(12)
        doc.setTextColor(30, 41, 59)
        doc.text(section.title, 20, y)
        y += 6
        
        doc.setFontSize(10)
        doc.setTextColor(71, 85, 105)
        const lines = doc.splitTextToSize(section.text, pageWidth - 40)
        doc.text(lines, 20, y)
        y += lines.length * 5 + 10
      }
    })
    
    // Footer
    const pageCount = doc.internal.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFontSize(9)
      doc.setTextColor(148, 163, 184)
      doc.text('UniControl - Talabalar boshqaruv tizimi', pageWidth / 2, 285, { align: 'center' })
      doc.text(`Sahifa ${i} / ${pageCount}`, pageWidth - 20, 285, { align: 'right' })
    }
    
    // Save PDF
    const fileName = `${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(fileName)
    
    toastStore.success(t('reports.pdfDownloaded'))
  } catch (err) {
    console.error('PDF download error:', err)
    toastStore.error(t('reports.pdfError'))
  }
}

// Hisobotni o'chirish
const deleteReport = async (report) => {
  if (!confirm(t('reports.confirmDeleteReport'))) return

  // Faqat draft/pending/failed hisobotlarni o'chirish mumkin
  if (!['draft', 'pending', 'failed'].includes(report.status)) {
    toastStore.error('Faqat kutilayotgan yoki qoralama hisobotlarni o\'chirish mumkin')
    return
  }

  try {
    // Try to delete from backend
    if (typeof report.id === 'number') {
      await api.request(`/reports/${report.id}`, { method: 'DELETE' })
    }
    
    const index = myReports.value.findIndex(r => r.id === report.id)
    if (index !== -1) {
      myReports.value.splice(index, 1)
    }
    
    // Update localStorage
    if (groupInfo.value?.id) {
      localStorage.setItem(`reports_${groupInfo.value.id}`, JSON.stringify(myReports.value))
    }
    
    toastStore.success(t('reports.reportDeleted'))
  } catch (err) {
    console.error('Delete error:', err)
    toastStore.error('Hisobotni o\'chirishda xatolik')
  }
}
</script>
