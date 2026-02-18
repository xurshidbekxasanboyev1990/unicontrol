<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('contracts.title') }}</h1>
        <p class="text-sm text-slate-500">
          {{ $t('contracts.totalContracts') }}: {{ totalContracts }}
          <span v-if="selectedYear"> · {{ selectedYear }} {{ $t('contracts.academicYear') }}</span>
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button 
          @click="showImportModal = true"
          class="px-4 py-2.5 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors flex items-center gap-2"
        >
          <Upload class="w-5 h-5" />
          {{ $t('contracts.excelImport') }}
        </button>
        <button 
          @click="exportToExcel"
          :disabled="exporting"
          class="px-4 py-2.5 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <Download class="w-5 h-5" />
          {{ exporting ? $t('contracts.exporting') : $t('contracts.excelExport') }}
        </button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.totalContracts') }}</p>
        <p class="text-lg font-bold text-slate-800">{{ formatNumber(stats.total_contracts) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.contractAmount') }}</p>
        <p class="text-lg font-bold text-blue-600">{{ formatMoney(stats.total_contract_amount) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.paid') }}</p>
        <p class="text-lg font-bold text-emerald-600">{{ formatMoney(stats.total_paid) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.debt') }}</p>
        <p class="text-lg font-bold text-red-600">{{ formatMoney(Math.abs(stats.total_debt)) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.grantAmount') }}</p>
        <p class="text-lg font-bold text-purple-600">{{ formatMoney(stats.total_grant_amount) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.paymentPercent') }}</p>
        <p class="text-lg font-bold text-amber-600">{{ stats.payment_percentage?.toFixed(1) }}%</p>
      </div>
    </div>

    <!-- Additional stats row -->
    <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="rounded-xl border border-emerald-100 bg-emerald-50 p-3">
        <p class="text-xs text-emerald-600 mb-1">{{ $t('contracts.fullyPaid') }}</p>
        <p class="text-lg font-bold text-emerald-700">{{ stats.fully_paid_count }}</p>
      </div>
      <div class="rounded-xl border border-red-100 bg-red-50 p-3">
        <p class="text-xs text-red-600 mb-1">{{ $t('contracts.debtors') }}</p>
        <p class="text-lg font-bold text-red-700">{{ stats.with_debt_count }}</p>
      </div>
      <div class="rounded-xl border border-blue-100 bg-blue-50 p-3">
        <p class="text-xs text-blue-600 mb-1">{{ $t('contracts.daytime') }}</p>
        <p class="text-lg font-bold text-blue-700">{{ stats.kunduzgi_count }}</p>
      </div>
      <div class="rounded-xl border border-orange-100 bg-orange-50 p-3">
        <p class="text-xs text-orange-600 mb-1">{{ $t('contracts.studying') }}</p>
        <p class="text-lg font-bold text-orange-700">{{ stats.studying_count }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
          <Filter :size="20" class="text-amber-600" />
        </div>
        <h2 class="font-semibold text-slate-800">{{ $t('contracts.filterAndSearch') }}</h2>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <!-- Search -->
        <div class="relative lg:col-span-2">
          <Search class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
          <input 
            v-model="searchQuery"
            type="text"
            :placeholder="$t('contracts.searchPlaceholder')"
            class="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/20"
            @input="onSearchInput"
          />
        </div>
        <!-- Academic Year -->
        <select 
          v-model="selectedYear"
          class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-amber-400 focus:outline-none"
          @change="loadData"
        >
          <option value="">{{ $t('contracts.allYears') }}</option>
          <option v-for="year in filterOptions.academic_years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
        <!-- Education Form -->
        <select 
          v-model="selectedEducationForm"
          class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-amber-400 focus:outline-none"
          @change="loadData"
        >
          <option value="">{{ $t('contracts.allEducationForms') }}</option>
          <option v-for="form in filterOptions.education_forms" :key="form" :value="form">
            {{ form }}
          </option>
        </select>
        <!-- Debt Filter -->
        <select 
          v-model="selectedDebtFilter"
          class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-amber-400 focus:outline-none"
          @change="loadData"
        >
          <option value="">{{ $t('contracts.allItems') }}</option>
          <option value="true">{{ $t('contracts.debtors') }}</option>
          <option value="false">{{ $t('contracts.noDebt') }}</option>
        </select>
      </div>
      
      <!-- Group Filter Row -->
      <div class="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <select 
          v-model="selectedGroup"
          class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-amber-400 focus:outline-none"
          @change="loadData"
        >
          <option value="">{{ $t('contracts.allGroups') }}</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">
            {{ g.name }}
          </option>
        </select>
        <select 
          v-model="selectedStatus"
          class="rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-amber-400 focus:outline-none"
          @change="loadData"
        >
          <option value="">{{ $t('contracts.allStatuses') }}</option>
          <option v-for="s in filterOptions.student_statuses" :key="s" :value="s">
            {{ s }}
          </option>
        </select>
        <div class="flex items-center justify-end gap-2">
          <button 
            @click="resetFilters"
            class="px-3 py-2 text-sm text-slate-600 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
          >
            {{ $t('contracts.clearFilters') }}
          </button>
          <span class="text-sm text-slate-400">
            {{ $t('contracts.resultsCount', { count: totalContracts }) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading && !contracts.length" class="flex items-center justify-center py-16">
      <Loader2 class="w-8 h-8 text-amber-500 animate-spin" />
      <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
    </div>

    <!-- Table -->
    <div v-else class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div class="border-b border-slate-100 bg-slate-50 p-4 flex items-center justify-between">
        <h3 class="font-semibold text-slate-700">
          {{ $t('contracts.contractInfo') }}
        </h3>
        <div v-if="loading" class="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 class="w-4 h-4 animate-spin" />
        </div>
      </div>

      <div v-if="contracts.length === 0 && !loading" class="p-12 text-center">
        <FileSpreadsheet :size="48" class="mx-auto mb-4 text-slate-300" />
        <p class="text-slate-500">{{ $t('contracts.noContractsFound') }}</p>
        <p class="text-sm text-slate-400 mt-1">{{ $t('contracts.importFromExcel') }}</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm min-w-[1000px]">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">#</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.fullName') }}</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.jshshir') }}</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.group') }}</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.course') }}</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.status') }}</th>
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.educationForm') }}</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.contract') }}</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.paid') }}</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.debt') }}</th>
              <th class="text-right px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.grant') }}</th>
              <th class="text-center px-3 py-2.5 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap">{{ $t('contracts.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(contract, idx) in contracts" 
              :key="contract.id" 
              class="border-b border-slate-100 hover:bg-amber-50/30 transition-colors"
            >
              <td class="px-3 py-2.5 text-slate-500">{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
              <td class="px-3 py-2.5 font-medium text-slate-800 whitespace-nowrap">
                {{ contract.student_name || '—' }}
              </td>
              <td class="px-3 py-2.5 text-slate-600 font-mono text-xs">
                {{ contract.student_jshshir || '—' }}
              </td>
              <td class="px-3 py-2.5">
                <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium">
                  {{ contract.group_name || '—' }}
                </span>
              </td>
              <td class="px-3 py-2.5 text-slate-600">{{ contract.course || '—' }}</td>
              <td class="px-3 py-2.5">
                <span 
                  class="px-2 py-0.5 rounded-lg text-xs font-medium"
                  :class="getStatusClass(contract.student_status)"
                >
                  {{ contract.student_status || '—' }}
                </span>
              </td>
              <td class="px-3 py-2.5 text-slate-600">{{ contract.education_form || '—' }}</td>
              <td class="px-3 py-2.5 text-right font-medium text-slate-800 whitespace-nowrap">
                {{ formatMoney(contract.contract_amount) }}
              </td>
              <td class="px-3 py-2.5 text-right font-medium text-emerald-600 whitespace-nowrap">
                {{ formatMoney(contract.total_paid) }}
              </td>
              <td class="px-3 py-2.5 text-right font-medium whitespace-nowrap"
                :class="Number(contract.debt_amount) < 0 ? 'text-red-600' : 'text-slate-500'">
                {{ formatMoney(contract.debt_amount) }}
              </td>
              <td class="px-3 py-2.5 text-right text-purple-600 whitespace-nowrap">
                {{ Number(contract.grant_amount) > 0 ? formatMoney(contract.grant_amount) : '—' }}
              </td>
              <td class="px-3 py-2.5 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button 
                    @click="openEditModal(contract)"
                    class="p-1.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                    :title="$t('contracts.editBtn')"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button 
                    @click="openDetailModal(contract)"
                    class="p-1.5 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                    :title="$t('contracts.detailsBtn')"
                  >
                    <Eye class="w-4 h-4" />
                  </button>
                  <button 
                    @click="confirmDelete(contract)"
                    class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    :title="$t('contracts.deleteBtn')"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="border-t border-slate-100 bg-slate-50 px-3 sm:px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <p class="text-sm text-slate-500">
          {{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, totalContracts) }} / {{ totalContracts }}
        </p>
        <div class="flex items-center gap-1 flex-wrap">
          <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage <= 1"
            class="px-3 py-1.5 text-sm rounded-lg border border-slate-200 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ←
          </button>
          <template v-for="p in visiblePages" :key="p">
            <button 
              v-if="p !== '...'"
              @click="changePage(p)"
              class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
              :class="p === currentPage ? 'bg-amber-500 text-white border-amber-500' : 'border-slate-200 hover:bg-white'"
            >
              {{ p }}
            </button>
            <span v-else class="px-2 text-slate-400">...</span>
          </template>
          <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage >= totalPages"
            class="px-3 py-1.5 text-sm rounded-lg border border-slate-200 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            →
          </button>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <div v-if="showImportModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showImportModal = false">
      <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
        <button @click="showImportModal = false" class="absolute top-4 right-4 p-1 text-emerald-600 hover:text-emerald-800 hover:bg-emerald-100 rounded-lg transition-colors z-10"><X class="w-5 h-5" /></button>
        <div class="bg-emerald-50 px-6 py-4 border-b border-emerald-100">
          <h3 class="text-lg font-bold text-emerald-800 flex items-center gap-2">
            <Upload class="w-5 h-5" />
            {{ $t('contracts.excelImport') }}
          </h3>
          <p class="text-sm text-emerald-600 mt-1">{{ $t('contracts.importDesc') }}</p>
        </div>
        <div class="p-6 space-y-4">
          <!-- Academic Year -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('contracts.academicYear') }}</label>
            <input 
              v-model="importYear" 
              type="text" 
              class="w-full rounded-xl border border-slate-200 px-4 py-2.5 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20"
              placeholder="2025-2026"
            />
          </div>
          <!-- Update Existing -->
          <label class="flex items-center gap-3 cursor-pointer">
            <input v-model="importUpdateExisting" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-emerald-500 focus:ring-emerald-400" />
            <span class="text-sm text-slate-700">{{ $t('contracts.updateExisting') }}</span>
          </label>
          <!-- File -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">{{ $t('contracts.excelFile') }}</label>
            <div 
              class="border-2 border-dashed rounded-xl p-6 text-center transition-colors"
              :class="importFile ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200 hover:border-slate-300'"
              @dragover.prevent
              @drop.prevent="onDrop"
            >
              <input 
                ref="fileInput"
                type="file" 
                accept=".xlsx,.xls" 
                class="hidden"
                @change="onFileSelect"
              />
              <div v-if="importFile" class="flex items-center justify-center gap-3">
                <FileSpreadsheet class="w-8 h-8 text-emerald-500" />
                <div class="text-left">
                  <p class="text-sm font-medium text-slate-800">{{ importFile.name }}</p>
                  <p class="text-xs text-slate-500">{{ (importFile.size / 1024).toFixed(1) }} KB</p>
                </div>
                <button @click="importFile = null" class="p-1 text-slate-400 hover:text-red-500">
                  <X class="w-4 h-4" />
                </button>
              </div>
              <div v-else @click="$refs.fileInput.click()" class="cursor-pointer">
                <Upload class="w-10 h-10 text-slate-300 mx-auto mb-2" />
                <p class="text-sm text-slate-500">{{ $t('contracts.selectOrDropFile') }}</p>
                <p class="text-xs text-slate-400 mt-1">{{ $t('contracts.xlsxFormat') }}</p>
              </div>
            </div>
          </div>

          <!-- Import Result -->
          <div v-if="importResult" class="rounded-xl p-4" :class="importResult.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'">
            <p class="font-medium mb-2" :class="importResult.success ? 'text-emerald-800' : 'text-red-800'">
              {{ importResult.success ? $t('contracts.importSuccess') : $t('contracts.importError') }}
            </p>
            <div class="text-sm space-y-1" :class="importResult.success ? 'text-emerald-700' : 'text-red-700'">
              <p>{{ $t('contracts.totalRows') }}: {{ importResult.total_rows }}</p>
              <p>{{ $t('contracts.newAdded') }}: {{ importResult.imported }}</p>
              <p>{{ $t('contracts.updated') }}: {{ importResult.updated }}</p>
              <p v-if="importResult.skipped > 0">{{ $t('contracts.skipped') }}: {{ importResult.skipped }}</p>
              <p v-if="importResult.failed > 0" class="text-red-600">{{ $t('contracts.errorCount') }}: {{ importResult.failed }}</p>
            </div>
            <div v-if="importResult.errors?.length" class="mt-2">
              <p class="text-xs font-medium text-red-600 mb-1">{{ $t('contracts.errors') }}:</p>
              <ul class="text-xs text-red-600 space-y-0.5 max-h-32 overflow-y-auto">
                <li v-for="(err, i) in importResult.errors.slice(0, 10)" :key="i">• {{ err }}</li>
              </ul>
            </div>
            <div v-if="importResult.warnings?.length" class="mt-2">
              <p class="text-xs font-medium text-amber-600 mb-1">{{ $t('contracts.warnings') }}:</p>
              <ul class="text-xs text-amber-600 space-y-0.5 max-h-32 overflow-y-auto">
                <li v-for="(w, i) in importResult.warnings.slice(0, 10)" :key="i">• {{ w }}</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 bg-slate-50 border-t flex justify-end gap-3">
          <button 
            @click="showImportModal = false; importResult = null"
            class="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 rounded-lg hover:bg-slate-200 transition-colors"
          >
            {{ $t('contracts.close') }}
          </button>
          <button 
            @click="doImport"
            :disabled="!importFile || importing"
            class="px-5 py-2 text-sm font-medium bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            <Loader2 v-if="importing" class="w-4 h-4 animate-spin" />
            {{ importing ? $t('contracts.importing') : $t('contracts.importBtn') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="showDetailModal && selectedContract" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showDetailModal = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 overflow-hidden max-h-[90vh] overflow-y-auto">
        <div class="bg-amber-50 px-6 py-4 border-b border-amber-100 flex justify-between items-center">
          <div>
            <h3 class="text-lg font-bold text-amber-800">{{ $t('contracts.contractDetails') }}</h3>
            <p class="text-sm text-amber-600">{{ selectedContract.student_name }}</p>
          </div>
          <button @click="showDetailModal = false" class="p-1 text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.fullName') }}</p>
              <p class="font-medium text-slate-800">{{ selectedContract.student_name || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.jshshir') }}</p>
              <p class="font-mono text-sm text-slate-800">{{ selectedContract.student_jshshir || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.group') }}</p>
              <p class="font-medium text-slate-800">{{ selectedContract.group_name || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.academicYear') }}</p>
              <p class="font-medium text-slate-800">{{ selectedContract.academic_year }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.course') }}</p>
              <p class="text-slate-800">{{ selectedContract.course || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.status') }}</p>
              <span class="px-2 py-0.5 rounded-lg text-xs font-medium" :class="getStatusClass(selectedContract.student_status)">
                {{ selectedContract.student_status || '—' }}
              </span>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.direction') }}</p>
              <p class="text-slate-800">{{ selectedContract.direction || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.educationForm') }}</p>
              <p class="text-slate-800">{{ selectedContract.education_form || '—' }}</p>
            </div>
          </div>
          
          <hr class="border-slate-100" />
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.contractAmount') }}</p>
              <p class="text-lg font-bold text-slate-800">{{ formatMoney(selectedContract.contract_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.totalPaid') }}</p>
              <p class="text-lg font-bold text-emerald-600">{{ formatMoney(selectedContract.total_paid) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.debt') }}</p>
              <p class="text-lg font-bold" :class="Number(selectedContract.debt_amount) < 0 ? 'text-red-600' : 'text-slate-600'">
                {{ formatMoney(selectedContract.debt_amount) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.paymentPercentage') }}</p>
              <p class="text-lg font-bold text-amber-600">{{ ((selectedContract.payment_percentage || 0) * 100).toFixed(1) }}%</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.grantPercent') }}</p>
              <p class="text-slate-800">{{ selectedContract.grant_percentage ? (selectedContract.grant_percentage * 100).toFixed(1) + '%' : '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.grantSum') }}</p>
              <p class="text-purple-600 font-medium">{{ formatMoney(selectedContract.grant_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.refundAmount') }}</p>
              <p class="text-slate-800">{{ formatMoney(selectedContract.refund_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.remainingAmount') }}</p>
              <p class="text-slate-800">{{ formatMoney(selectedContract.remaining_amount) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.yearStartBalance') }}</p>
              <p class="text-slate-800">{{ formatMoney(selectedContract.year_start_balance) }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">{{ $t('contracts.yearEndBalance') }}</p>
              <p class="font-medium" :class="Number(selectedContract.year_end_balance) < 0 ? 'text-red-600' : 'text-slate-800'">
                {{ formatMoney(selectedContract.year_end_balance) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal && editForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showEditModal = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 overflow-hidden max-h-[90vh] overflow-y-auto">
        <div class="bg-blue-50 px-6 py-4 border-b border-blue-100 flex justify-between items-center">
          <div>
            <h3 class="text-lg font-bold text-blue-800">{{ $t('contracts.editContract') }}</h3>
            <p class="text-sm text-blue-600">{{ editForm._student_name }}</p>
          </div>
          <button @click="showEditModal = false" class="p-1 text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.contractAmount') }}</label>
              <input v-model.number="editForm.contract_amount" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.totalPaid') }}</label>
              <input v-model.number="editForm.total_paid" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.debt') }}</label>
              <input v-model.number="editForm.debt_amount" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.grantAmount') }}</label>
              <input v-model.number="editForm.grant_amount" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.refundAmount') }}</label>
              <input v-model.number="editForm.refund_amount" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.course') }}</label>
              <input v-model="editForm.course" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.studentStatus') }}</label>
              <input v-model="editForm.student_status" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.educationForm') }}</label>
              <input v-model="editForm.education_form" type="text" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.yearStartBalance') }}</label>
              <input v-model.number="editForm.year_start_balance" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.yearEndBalance') }}</label>
              <input v-model.number="editForm.year_end_balance" type="number" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600 mb-1">{{ $t('contracts.note') }}</label>
            <textarea v-model="editForm.note" rows="2" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none resize-none"></textarea>
          </div>
        </div>
        <div class="px-6 py-4 bg-slate-50 border-t flex justify-end gap-3">
          <button 
            @click="showEditModal = false"
            class="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 rounded-lg hover:bg-slate-200 transition-colors"
          >
            {{ $t('contracts.cancel') }}
          </button>
          <button 
            @click="saveEdit"
            :disabled="saving"
            class="px-5 py-2 text-sm font-medium bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 flex items-center gap-2 transition-colors"
          >
            <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
            {{ saving ? $t('contracts.saving') : $t('contracts.save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showDeleteModal = false">
      <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6 text-center">
        <button @click="showDeleteModal = false" class="absolute top-3 right-3 p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors z-10"><X class="w-5 h-5" /></button>
        <div class="w-14 h-14 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
          <Trash2 class="w-7 h-7 text-red-500" />
        </div>
        <h3 class="text-lg font-bold text-slate-800 mb-2">{{ $t('contracts.confirmDelete') }}</h3>
        <p class="text-sm text-slate-500 mb-6">
          {{ $t('contracts.confirmDeleteMsg', { name: deleteTarget?.student_name }) }}
        </p>
        <div class="flex gap-3 justify-center">
          <button 
            @click="showDeleteModal = false"
            class="px-4 py-2 text-sm text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            {{ $t('contracts.cancel') }}
          </button>
          <button 
            @click="doDelete"
            :disabled="deleting"
            class="px-5 py-2 text-sm font-medium bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 flex items-center gap-2 transition-colors"
          >
            <Loader2 v-if="deleting" class="w-4 h-4 animate-spin" />
            {{ $t('contracts.deleteAction') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
    Download,
    Eye,
    FileSpreadsheet,
    Filter, Loader2,
    Pencil,
    Search,
    Trash2,
    Upload,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

// State
const contracts = ref([])
const totalContracts = ref(0)
const totalPages = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const loading = ref(false)
const stats = ref(null)
const groups = ref([])

// Filters
const searchQuery = ref('')
const selectedYear = ref('2025-2026')
const selectedEducationForm = ref('')
const selectedStatus = ref('')
const selectedGroup = ref('')
const selectedDebtFilter = ref('')
const filterOptions = ref({ academic_years: ['2025-2026'], education_forms: [], student_statuses: [] })

// Import
const showImportModal = ref(false)
const importFile = ref(null)
const importYear = ref('2025-2026')
const importUpdateExisting = ref(true)
const importing = ref(false)
const importResult = ref(null)
const fileInput = ref(null)

// Detail
const showDetailModal = ref(false)
const selectedContract = ref(null)

// Edit
const showEditModal = ref(false)
const editForm = ref(null)
const editId = ref(null)
const saving = ref(false)

// Delete
const showDeleteModal = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

// Export
const exporting = ref(false)

// Search debounce
let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadData()
  }, 400)
}

// Pagination
const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      pages.push(i)
    }
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  
  return pages
})

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadData()
}

// Format helpers
const formatNumber = (n) => {
  if (n == null) return '0'
  return Number(n).toLocaleString('uz-UZ')
}

const formatMoney = (amount) => {
  if (amount == null || amount === 0) return '0'
  const num = Number(amount)
  if (num === 0) return '0'
  const absNum = Math.abs(num)
  const sign = num < 0 ? '-' : ''
  if (absNum >= 1_000_000_000) {
    return sign + (absNum / 1_000_000_000).toFixed(1) + ' ' + t('contracts.billion')
  }
  if (absNum >= 1_000_000) {
    return sign + (absNum / 1_000_000).toFixed(1) + ' ' + t('contracts.million')
  }
  if (absNum >= 1_000) {
    return sign + (absNum / 1_000).toFixed(0) + ' ' + t('contracts.thousand')
  }
  return num.toLocaleString('uz-UZ')
}

const getStatusClass = (status) => {
  if (!status) return 'bg-slate-100 text-slate-600'
  const s = status.toLowerCase()
  if (s.includes("o'qimoqda")) return 'bg-emerald-100 text-emerald-700'
  if (s.includes('akademik')) return 'bg-amber-100 text-amber-700'
  if (s.includes('chetlash')) return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-600'
}

// Data loading
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    if (selectedEducationForm.value) params.education_form = selectedEducationForm.value
    if (selectedStatus.value) params.student_status = selectedStatus.value
    if (selectedDebtFilter.value) params.has_debt = selectedDebtFilter.value
    if (searchQuery.value) params.search = searchQuery.value

    const res = await api.getContracts(params)
    contracts.value = res.items || []
    totalContracts.value = res.total || 0
    totalPages.value = res.total_pages || 0
  } catch (e) {
    console.error('Error loading contracts:', e)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const params = {}
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    stats.value = await api.getContractStatistics(params)
  } catch (e) {
    console.error('Error loading stats:', e)
  }
}

const loadFilters = async () => {
  try {
    filterOptions.value = await api.getContractFilters()
  } catch (e) {
    console.error('Error loading filters:', e)
  }
}

const loadGroups = async () => {
  try {
    const res = await api.getGroups({ page_size: 1000 })
    groups.value = (res.items || res || []).sort((a, b) => a.name.localeCompare(b.name))
  } catch (e) {
    console.error('Error loading groups:', e)
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedYear.value = ''
  selectedEducationForm.value = ''
  selectedStatus.value = ''
  selectedGroup.value = ''
  selectedDebtFilter.value = ''
  currentPage.value = 1
  loadData()
  loadStats()
}

// Import
const onFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) importFile.value = file
}

const onDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    importFile.value = file
  }
}

const doImport = async () => {
  if (!importFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const result = await api.importContracts(importFile.value, importYear.value, importUpdateExisting.value)
    importResult.value = result
    if (result.success) {
      loadData()
      loadStats()
      loadFilters()
    }
  } catch (e) {
    importResult.value = { success: false, total_rows: 0, imported: 0, updated: 0, skipped: 0, failed: 0, errors: [e.message] }
  } finally {
    importing.value = false
  }
}

// Export
const exportToExcel = async () => {
  exporting.value = true
  try {
    const params = {}
    if (selectedYear.value) params.academic_year = selectedYear.value
    if (selectedGroup.value) params.group_id = selectedGroup.value
    const blob = await api.exportContracts(params)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `kontrakt_malumotlari${selectedYear.value ? '_' + selectedYear.value : ''}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Export error:', e)
  } finally {
    exporting.value = false
  }
}

// Detail
const openDetailModal = (contract) => {
  selectedContract.value = contract
  showDetailModal.value = true
}

// Edit
const openEditModal = (contract) => {
  editId.value = contract.id
  editForm.value = {
    _student_name: contract.student_name,
    contract_amount: Number(contract.contract_amount),
    total_paid: Number(contract.total_paid),
    debt_amount: Number(contract.debt_amount),
    grant_amount: Number(contract.grant_amount),
    refund_amount: Number(contract.refund_amount),
    course: contract.course,
    student_status: contract.student_status,
    education_form: contract.education_form,
    year_start_balance: Number(contract.year_start_balance),
    year_end_balance: Number(contract.year_end_balance),
    note: contract.note || '',
  }
  showEditModal.value = true
}

const saveEdit = async () => {
  if (!editId.value) return
  saving.value = true
  try {
    const { _student_name, ...data } = editForm.value
    await api.updateContract(editId.value, data)
    showEditModal.value = false
    loadData()
    loadStats()
  } catch (e) {
    console.error('Save error:', e)
  } finally {
    saving.value = false
  }
}

// Delete
const confirmDelete = (contract) => {
  deleteTarget.value = contract
  showDeleteModal.value = true
}

const doDelete = async () => {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.deleteContract(deleteTarget.value.id)
    showDeleteModal.value = false
    loadData()
    loadStats()
  } catch (e) {
    console.error('Delete error:', e)
  } finally {
    deleting.value = false
  }
}

// Init
onMounted(async () => {
  await Promise.all([loadFilters(), loadGroups()])
  await Promise.all([loadData(), loadStats()])
})
</script>
