<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('groups.title') }}</h1>
        <p class="text-sm text-slate-500">{{ totalItems.toLocaleString() }} {{ $t('groups.title') }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-2 sm:gap-3">
        <!-- Search -->
        <div class="relative flex-1 min-w-[120px] sm:flex-none">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="..."
            class="pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none w-full sm:w-48"
          />
        </div>
        
        <!-- Excel Import -->
        <label class="px-4 py-2.5 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors flex items-center gap-2 cursor-pointer">
          <FileSpreadsheet class="w-5 h-5" />
          Excel
          <input 
            type="file"
            accept=".xlsx,.xls,.csv"
            @change="handleExcelUpload"
            class="hidden"
          />
        </label>
        
        <button 
          @click="refresh"
          class="p-2.5 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
          :class="{ 'animate-spin': loading }"
        >
          <RefreshCw class="w-5 h-5" />
        </button>
        
        <button 
          @click="openModal()"
          class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2"
        >
          <FolderPlus class="w-5 h-5" />
          {{ $t('groups.addGroup') }}
        </button>
      </div>
    </div>

    <!-- Excel Format Info -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
      <div class="flex items-start gap-3">
        <Info class="w-5 h-5 text-blue-500 mt-0.5" />
        <div>
          <p class="text-sm font-medium text-blue-800">{{ $t('groups.excelFormat') }}</p>
          <p class="text-sm text-blue-600 mt-1">
            {{ $t('groups.excelFormatDesc') }}
          </p>
          <button @click="downloadTemplate" class="text-sm text-blue-700 underline mt-2 hover:text-blue-800">
            Namuna faylni yuklab olish
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <RefreshCw class="w-12 h-12 text-violet-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-600">{{ $t('groups.loadingGroups') }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6">
      <div class="flex items-center gap-3">
        <AlertCircle class="w-6 h-6 text-rose-500" />
        <div>
          <h3 class="font-semibold text-rose-700">{{ $t('groups.errorOccurred') }}</h3>
          <p class="text-rose-600 text-sm mt-1">{{ error }}</p>
        </div>
        <button @click="refresh" class="ml-auto px-4 py-2 bg-rose-500 text-white rounded-lg hover:bg-rose-600">
          {{ $t('common.retry') }}
        </button>
      </div>
    </div>

    <!-- Groups Grid -->
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="group in groups" 
          :key="group.id"
          class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
          :class="{ 'opacity-60 border-rose-200': !group.isActive }"
        >
          <!-- Status Badge -->
          <div class="px-6 pt-4 flex items-center justify-between">
            <span 
              class="px-3 py-1 rounded-full text-xs font-semibold"
              :class="group.isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
            >
              {{ group.isActive ? $t('common.active') : $t('common.inactive') }}
            </span>
            <button 
              @click="toggleStatus(group)"
              class="p-2 rounded-lg transition-colors"
              :class="group.isActive ? 'text-emerald-500 hover:bg-emerald-50' : 'text-rose-500 hover:bg-rose-50'"
              :title="group.isActive ? $t('common.deactivate') : $t('common.activate')"
            >
              <Power class="w-4 h-4" />
            </button>
          </div>

          <div class="p-6 pt-3">
            <div class="flex items-start justify-between mb-4">
              <div 
                class="w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold"
                :class="groupColors[group.id % groupColors.length]"
              >
                {{ group.name.slice(-3) }}
              </div>
              <div class="flex items-center gap-1">
                <button 
                  v-if="authStore.isSuperAdmin"
                  @click="openSubscriptionModal(group)"
                  class="p-2 text-slate-400 hover:text-emerald-500 hover:bg-emerald-50 rounded-lg transition-colors"
                  :title="$t('groups.assignSubscription')"
                >
                  <CreditCard class="w-4 h-4" />
                </button>
                <button 
                  @click="openLeaderModal(group)"
                  class="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                  :title="$t('groups.assignLeader')"
                >
                  <Crown class="w-4 h-4" />
                </button>
                <button 
                  @click="openModal(group)"
                  class="p-2 text-slate-400 hover:text-violet-500 hover:bg-violet-50 rounded-lg transition-colors"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <button 
                  @click="confirmDelete(group)"
                  class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>

            <h3 class="text-xl font-bold text-slate-800">{{ group.name }}</h3>
            <p class="text-slate-500 text-sm mt-1">{{ group.year }}-kurs • {{ group.faculty || 'Noma\'lum' }}</p>

            <div class="mt-4 pt-4 border-t border-slate-100 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-slate-500 flex items-center gap-2">
                  <Users class="w-4 h-4" />
                  {{ $t('groups.students') }}
                </span>
                <span class="font-semibold text-slate-700">{{ group.studentCount.toLocaleString() }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-slate-500 flex items-center gap-2">
                  <Crown class="w-4 h-4" />
                  {{ $t('groups.leader') }}
                </span>
                <span 
                  class="font-medium"
                  :class="group.leaderName ? 'text-amber-600' : 'text-slate-400'"
                >
                  {{ group.leaderName || $t('common.notAssigned') }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-slate-500 flex items-center gap-2">
                  <TrendingUp class="w-4 h-4" />
                  {{ $t('attendance.title') }}
                </span>
                <span 
                  class="font-semibold"
                  :class="group.attendanceRate >= 85 ? 'text-emerald-600' : group.attendanceRate >= 70 ? 'text-amber-600' : 'text-rose-600'"
                >
                  {{ group.attendanceRate }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="groups.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
        <Layers class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">{{ $t('groups.noGroupsFound') }}</p>
        <p class="text-sm text-slate-400 mt-2">{{ $t('groups.noGroupsFoundDesc') }}</p>
        <div class="flex items-center justify-center gap-3 mt-4">
          <label class="px-4 py-2 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors cursor-pointer">
            <FileSpreadsheet class="w-4 h-4 inline mr-2" />
            Excel
            <input 
              type="file"
              accept=".xlsx,.xls,.csv"
              @change="handleExcelUpload"
              class="hidden"
            />
          </label>
          <button 
            @click="openModal()"
            class="px-4 py-2 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors"
          >
            {{ $t('groups.addGroup') }}
          </button>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-4">
        <button 
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft class="w-5 h-5" />
        </button>
        
        <template v-for="page in Math.min(5, totalPages)" :key="page">
          <button 
            @click="goToPage(page)"
            class="w-10 h-10 rounded-lg font-medium transition-colors"
            :class="currentPage === page ? 'bg-violet-500 text-white' : 'border border-slate-200 hover:bg-slate-50'"
          >
            {{ page }}
          </button>
        </template>
        
        <span v-if="totalPages > 5" class="text-slate-400">...</span>
        
        <button 
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronRight class="w-5 h-5" />
        </button>
      </div>
    </template>

    <!-- Add/Edit Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800">
              {{ editingGroup ? $t('groups.editGroup') : $t('groups.addGroup') }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveGroup" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('groups.groupName') }} *</label>
              <input 
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="KI_25-04"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('groups.course') }}</label>
                <input 
                  v-model="form.year"
                  type="number"
                  min="1"
                  max="6"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('groups.facultyLabel') }}</label>
                <input 
                  v-model="form.faculty"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="Kompyuter injiniringi"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ $t('groups.contractAmount') }}</label>
              <input 
                v-model.number="form.contract_amount"
                type="number"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="18411000"
              />
            </div>
            <div class="flex gap-3 pt-4">
              <button 
                type="button"
                @click="showModal = false"
                class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button 
                type="submit"
                :disabled="saving"
                class="flex-1 px-4 py-3 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Loader2 v-if="saving" class="w-5 h-5 animate-spin" />
                {{ saving ? $t('settings.saving') : $t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Leader Assignment Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showLeaderModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showLeaderModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-800">{{ $t('groups.assignLeader') }}</h2>
              <p class="text-sm text-slate-500">{{ selectedGroup?.name }} guruhi</p>
            </div>
            <button @click="showLeaderModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div class="p-6">
            <!-- Loading -->
            <div v-if="loadingStudents" class="py-8 text-center">
              <RefreshCw class="w-8 h-8 text-violet-500 animate-spin mx-auto mb-2" />
              <p class="text-slate-500">{{ $t('groups.loadingStudents') }}</p>
            </div>
            
            <template v-else>
              <!-- Current Leader -->
              <div v-if="selectedGroup?.leaderName" class="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center text-white font-bold">
                      <Crown class="w-5 h-5" />
                    </div>
                    <div>
                      <p class="font-medium text-amber-800">{{ $t('groups.currentLeader') }}</p>
                      <p class="text-sm text-amber-600">{{ selectedGroup.leaderName }}</p>
                    </div>
                  </div>
                  <button 
                    @click="removeLeader"
                    class="px-3 py-1.5 bg-rose-100 text-rose-600 rounded-lg text-sm font-medium hover:bg-rose-200 transition-colors"
                  >
                    {{ $t('common.remove') }}
                  </button>
                </div>
              </div>

            <!-- Search -->
            <div class="relative mb-4">
              <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                v-model="leaderSearch"
                type="text"
                :placeholder="$t('common.search') + '...'"
                class="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
              />
            </div>

            <!-- Students List -->
            <div class="max-h-64 overflow-y-auto space-y-2">
              <div 
                v-for="student in filteredGroupStudents" 
                :key="student.id"
                @click="assignLeader(student)"
                class="p-4 border border-slate-200 rounded-xl hover:border-amber-300 hover:bg-amber-50 cursor-pointer transition-all"
                :class="{ 'border-amber-400 bg-amber-50': selectedGroup?.leaderId === student.id }"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white font-bold">
                    {{ (student.name || 'T').charAt(0) }}
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-slate-800">{{ student.name || 'Ism kiritilmagan' }}</p>
                    <p class="text-sm text-slate-500">{{ student.studentId || '—' }}</p>
                  </div>
                  <div v-if="selectedGroup?.leaderId === student.id">
                    <Crown class="w-5 h-5 text-amber-500" />
                  </div>
                </div>
              </div>
              <div v-if="filteredGroupStudents.length === 0" class="text-center py-8 text-slate-500">
                <Users class="w-8 h-8 mx-auto mb-2 text-slate-300" />
                <p>{{ $t('groups.noStudentsFound') }}</p>
              </div>
            </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Delete Confirmation -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showDeleteConfirm = false"
      >
        <div class="relative bg-white rounded-2xl max-w-sm w-full p-6 text-center">
          <button @click="showDeleteConfirm = false" class="absolute top-3 right-3 p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors z-10"><X class="w-5 h-5" /></button>
          <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle class="w-8 h-8 text-rose-500" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 mb-2">{{ $t('groups.confirmDeleteTitle') }}</h3>
          <p class="text-slate-500 mb-6">
            {{ deletingGroup?.name }} guruhini o'chirmoqchimisiz? Guruh ichidagi talabalar ham o'chiriladi.
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              @click="deleteGroup"
              class="flex-1 px-4 py-3 bg-rose-500 text-white rounded-xl font-medium hover:bg-rose-600 transition-colors"
            >
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Excel Import Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showImportModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showImportModal = false"
      >
        <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-800">{{ $t('groups.importResult') }}</h2>
              <p class="text-sm text-slate-500">{{ importData.length }} {{ $t('groups.groupsFound') }}</p>
            </div>
            <button @click="showImportModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div class="p-6 max-h-96 overflow-y-auto">
            <div v-for="(group, idx) in importData" :key="idx" class="mb-4 p-4 border border-slate-200 rounded-xl">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-semibold text-slate-800">{{ group.group }}</h3>
                <span class="px-2 py-1 bg-violet-100 text-violet-700 rounded-lg text-sm">
                  {{ group.students.length }} {{ $t('groups.student') }}
                </span>
              </div>
              <div class="text-sm text-slate-500 space-y-1">
                <p><span class="font-medium">{{ $t('groups.faculty') }}:</span> {{ group.faculty || $t('common.unknown') }}</p>
                <p><span class="font-medium">{{ $t('groups.students') }}:</span></p>
                <ul class="ml-4 list-disc">
                  <li v-for="(s, i) in group.students.slice(0, 3)" :key="i">{{ s.name }} ({{ s.studentId }})</li>
                  <li v-if="group.students.length > 3" class="text-slate-400">{{ $t('groups.andMore', { count: group.students.length - 3 }) }}</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="p-6 border-t border-slate-100 flex gap-3">
            <button 
              @click="showImportModal = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              @click="confirmImport"
              class="flex-1 px-4 py-3 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors"
            >
              {{ $t('common.importAll') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Subscription Assignment Modal (Super Admin) -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showSubscriptionModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showSubscriptionModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-800">{{ $t('groups.giveSubscription') }}</h2>
              <p class="text-sm text-slate-500">{{ subscriptionGroup?.name }} guruhi</p>
            </div>
            <button @click="showSubscriptionModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div class="p-6">
            <!-- Loading -->
            <div v-if="loadingPlans" class="py-8 text-center">
              <RefreshCw class="w-8 h-8 text-violet-500 animate-spin mx-auto mb-2" />
              <p class="text-slate-500">{{ $t('groups.loadingPlans') }}</p>
            </div>

            <template v-else>
              <p class="text-sm text-slate-600 mb-4">
                {{ $t('groups.selectPlanDesc') }}
              </p>

              <!-- Plans List -->
              <div class="space-y-3 max-h-72 overflow-y-auto">
                <div 
                  v-for="plan in subscriptionPlans" 
                  :key="plan.id"
                  @click="selectedPlanId = plan.id"
                  class="p-4 border-2 rounded-xl cursor-pointer transition-all duration-200"
                  :class="selectedPlanId === plan.id 
                    ? 'border-emerald-500 bg-emerald-50 shadow-lg shadow-emerald-100' 
                    : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <div 
                        class="w-10 h-10 rounded-xl flex items-center justify-center"
                        :class="{
                          'bg-blue-100 text-blue-600': plan.plan_type === 'start',
                          'bg-violet-100 text-violet-600': plan.plan_type === 'plus',
                          'bg-amber-100 text-amber-600': plan.plan_type === 'pro',
                          'bg-emerald-100 text-emerald-600': plan.plan_type === 'unlimited'
                        }"
                      >
                        <Zap class="w-5 h-5" />
                      </div>
                      <div>
                        <h4 class="font-semibold text-slate-800">{{ plan.name }}</h4>
                        <p class="text-sm text-slate-500">{{ plan.duration_days || 30 }} kun</p>
                      </div>
                    </div>
                    <div class="text-right">
                      <p class="font-bold text-slate-800">{{ (plan.price || 0).toLocaleString() }} so'm</p>
                      <div v-if="selectedPlanId === plan.id" class="mt-1">
                        <Check class="w-5 h-5 text-emerald-500 ml-auto" />
                      </div>
                    </div>
                  </div>
                  <p v-if="plan.description" class="text-xs text-slate-400 mt-2">{{ plan.description }}</p>
                </div>
              </div>

              <div v-if="subscriptionPlans.length === 0" class="text-center py-8 text-slate-500">
                <CreditCard class="w-8 h-8 mx-auto mb-2 text-slate-300" />
                <p>{{ $t('groups.noPlansFound') }}</p>
              </div>

              <!-- Actions -->
              <div class="flex gap-3 pt-6">
                <button 
                  type="button"
                  @click="showSubscriptionModal = false"
                  class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
                >
                  {{ $t('common.cancel') }}
                </button>
                <button 
                  @click="assignSubscription"
                  :disabled="!selectedPlanId || assigningSubscription"
                  class="flex-1 px-4 py-3 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Loader2 v-if="assigningSubscription" class="w-5 h-5 animate-spin" />
                  {{ assigningSubscription ? $t('common.loading') : $t('groups.giveSubscription') }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
/**
 * Groups Management - Real API Integration
 * Backend /groups endpoint dan ma'lumot oladi
 * CRUD operatsiyalari, sardor tayinlash
 */
import {
    AlertCircle,
    AlertTriangle,
    Check,
    ChevronLeft,
    ChevronRight,
    CreditCard,
    Crown,
    FileSpreadsheet,
    FolderPlus,
    Info,
    Layers,
    Loader2,
    Pencil,
    Power,
    RefreshCw,
    Search,
    Trash2,
    TrendingUp,
    Users,
    X,
    Zap
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import api from '../../services/api'
import { useDataStore } from '../../stores/data'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const dataStore = useDataStore()
const toast = useToastStore()
const langStore = useLanguageStore()
const { t } = langStore

// Auth store for role check
import { useAuthStore } from '../../stores/auth'
const authStore = useAuthStore()

// State
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const groups = ref([])
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const showLeaderModal = ref(false)
const showImportModal = ref(false)
const editingGroup = ref(null)
const deletingGroup = ref(null)
const selectedGroup = ref(null)
const leaderSearch = ref('')
const importData = ref([])
const groupStudents = ref([])
const loadingStudents = ref(false)

// Subscription assignment state
const showSubscriptionModal = ref(false)
const subscriptionGroup = ref(null)
const subscriptionPlans = ref([])
const selectedPlanId = ref(null)
const loadingPlans = ref(false)
const assigningSubscription = ref(false)

// Pagination
const currentPage = ref(1)
const pageSize = ref(24)
const totalItems = ref(0)
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

// Search
const searchQuery = ref('')

const groupColors = [
  'bg-gradient-to-br from-violet-500 to-purple-600',
  'bg-gradient-to-br from-blue-500 to-cyan-600',
  'bg-gradient-to-br from-emerald-500 to-teal-600',
  'bg-gradient-to-br from-orange-500 to-red-600',
  'bg-gradient-to-br from-pink-500 to-rose-600'
]

const form = reactive({
  name: '',
  year: 1,
  faculty: '',
  contract_amount: 18411000
})

// Load groups
async function loadGroups() {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await api.getGroups(params)
    
    // Backend returns { items: [...], total: N, page: N, ... }
    const items = response.items || response.data || response
    if (items && Array.isArray(items)) {
      groups.value = items.map(g => ({
        id: g.id,
        name: g.name,
        year: g.course_year || g.year || 1,
        faculty: g.faculty || '',
        contractAmount: g.contract_amount || 18411000,
        isActive: g.is_active !== false,
        leaderId: g.leader_id,
        leaderName: g.leader_name || g.leader?.full_name || null,
        studentCount: g.students_count || g.student_count || 0,
        attendanceRate: g.attendance_rate || 0
      }))
      totalItems.value = response.total || items.length
    }
    
    // Also update store cache
    dataStore.groups = groups.value
  } catch (e) {
    console.error('Groups load error:', e)
    error.value = e.message || 'Guruhlar yuklanmadi'
  } finally {
    loading.value = false
  }
}

// Get student count (from loaded data)
function getStudentCount(groupName) {
  const group = groups.value.find(g => g.name === groupName)
  return group?.studentCount || 0
}

// Get group attendance
function getGroupAttendance(groupName) {
  const group = groups.value.find(g => g.name === groupName)
  return group?.attendanceRate || 0
}

// Load students for leader selection
async function loadGroupStudents(groupId) {
  loadingStudents.value = true
  try {
    const response = await api.getStudents({ group_id: groupId, page_size: 100 })
    const items = response.items || response.data || []
    groupStudents.value = items.map(s => ({
      id: s.id,
      name: s.name || s.full_name || 'Ism kiritilmagan',
      studentId: s.student_id || s.hemis_id || ''
    }))
  } catch (e) {
    console.error('Load group students error:', e)
    groupStudents.value = []
  } finally {
    loadingStudents.value = false
  }
}

const filteredGroupStudents = computed(() => {
  if (!leaderSearch.value) return groupStudents.value
  const query = leaderSearch.value.toLowerCase()
  return groupStudents.value.filter(s => 
    (s.name || '').toLowerCase().includes(query) ||
    (s.studentId || '').toLowerCase().includes(query)
  )
})

// Modal operations
function openModal(group = null) {
  if (group) {
    editingGroup.value = group
    form.name = group.name
    form.year = group.year
    form.faculty = group.faculty || ''
    form.contract_amount = group.contractAmount || 18411000
  } else {
    editingGroup.value = null
    form.name = ''
    form.year = 1
    form.faculty = ''
    form.contract_amount = 18411000
  }
  showModal.value = true
}

// Save group
async function saveGroup() {
  if (!form.name) {
    toast.error('Guruh nomini kiriting')
    return
  }
  
  saving.value = true
  
  try {
    const groupData = {
      name: form.name,
      year: form.year,
      faculty: form.faculty || null,
      contract_amount: form.contract_amount
    }
    
    if (editingGroup.value) {
      await api.updateGroup(editingGroup.value.id, groupData)
      toast.success(t('common.success'))
    } else {
      await api.createGroup(groupData)
      toast.success(t('common.success'))
    }
    
    showModal.value = false
    await loadGroups()
  } catch (e) {
    console.error('Save group error:', e)
    toast.error(e.message || t('common.error'))
  } finally {
    saving.value = false
  }
}

// Delete group
function confirmDelete(group) {
  deletingGroup.value = group
  showDeleteConfirm.value = true
}

async function deleteGroup() {
  if (!deletingGroup.value) return
  
  try {
    await api.deleteGroup(deletingGroup.value.id)
    toast.success(t('common.success'))
    showDeleteConfirm.value = false
    deletingGroup.value = null
    await loadGroups()
  } catch (e) {
    console.error('Delete group error:', e)
    toast.error(e.message || t('common.error'))
  }
}

// Toggle group status
async function toggleStatus(group) {
  try {
    await api.updateGroup(group.id, { is_active: !group.isActive })
    group.isActive = !group.isActive
    toast.info(t('common.success'))
  } catch (e) {
    console.error('Toggle status error:', e)
    toast.error(t('common.error'))
  }
}

// Leader Management
async function openLeaderModal(group) {
  selectedGroup.value = group
  leaderSearch.value = ''
  showLeaderModal.value = true
  await loadGroupStudents(group.id)
}

async function assignLeader(student) {
  if (!selectedGroup.value) return
  
  try {
    await api.assignGroupLeader(selectedGroup.value.id, student.id)
    selectedGroup.value.leaderId = student.id
    selectedGroup.value.leaderName = student.name
    toast.success(t('common.success'))
    showLeaderModal.value = false
    await loadGroups()
  } catch (e) {
    console.error('Assign leader error:', e)
    toast.error(e.message || t('common.error'))
  }
}

async function removeLeader() {
  if (!selectedGroup.value) return
  
  try {
    await api.removeGroupLeader(selectedGroup.value.id)
    selectedGroup.value.leaderId = null
    selectedGroup.value.leaderName = null
    toast.info(t('common.success'))
    showLeaderModal.value = false
    await loadGroups()
  } catch (e) {
    console.error('Remove leader error:', e)
    toast.error(t('common.error'))
  }
}

// Subscription Management (Super Admin only)
async function openSubscriptionModal(group) {
  subscriptionGroup.value = group
  selectedPlanId.value = null
  showSubscriptionModal.value = true
  loadingPlans.value = true
  
  try {
    const plans = await api.getSubscriptionPlans()
    subscriptionPlans.value = (plans || []).filter(p => p.is_active !== false)
  } catch (e) {
    console.error('Load plans error:', e)
    subscriptionPlans.value = []
    toast.error('Rejalarni yuklashda xatolik')
  } finally {
    loadingPlans.value = false
  }
}

async function assignSubscription() {
  if (!subscriptionGroup.value || !selectedPlanId.value) {
    toast.error(t('groups.selectPlan'))
    return
  }
  
  assigningSubscription.value = true
  
  try {
    const result = await api.adminAssignSubscription(subscriptionGroup.value.id, selectedPlanId.value)
    toast.success(result.message || 'Obuna faollashtirildi')
    showSubscriptionModal.value = false
    subscriptionGroup.value = null
    selectedPlanId.value = null
  } catch (e) {
    console.error('Assign subscription error:', e)
    toast.error(e.message || 'Obuna berishda xatolik')
  } finally {
    assigningSubscription.value = false
  }
}

// Excel Import - use dataStore method
async function handleExcelUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  
  event.target.value = ''
  
  try {
    toast.info('Import boshlanmoqda...')
    const result = await dataStore.importFromExcel(file)
    toast.success(`${result.imported || 0} ta ma'lumot import qilindi`)
    await loadGroups()
  } catch (e) {
    console.error('Import error:', e)
    toast.error(e.message || 'Import xatoligi')
  }
}

function downloadTemplate() {
  const csv = `Guruh,Fakultet,Talaba ID,Ism Familiya,Telefon,Parol
KI_25-04,Kompyuter injiniringi,ST-2024-001,Aliyev Jasur,+998901234567,123456
KI_25-04,Kompyuter injiniringi,ST-2024-002,Karimov Sardor,+998912345678,123456
DI_25-21,Dasturiy injiniring,ST-2024-003,Toshmatov Alisher,+998923456789,123456`
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'guruhlar_namuna.csv'
  link.click()
  
  toast.info('Namuna fayl yuklab olindi')
}

// Pagination
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadGroups()
  }
}

// Search with debounce
let searchTimeout = null
watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadGroups()
  }, 500)
})

// Refresh
async function refresh() {
  dataStore.clearCache()
  await loadGroups()
}

// Initialize
onMounted(() => {
  loadGroups()
})
</script>
