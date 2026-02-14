<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl p-6 md:p-8 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 animate-pulse"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
      <div class="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <Sheet class="w-6 h-6" />
            </div>
            <span class="text-sm font-medium text-white/70">{{ $t('sheets.title') }}</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-bold">{{ $t('sheets.title') }}</h1>
          <p class="text-white/80 mt-1 max-w-xl text-sm">{{ $t('sheets.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <div v-if="dbStats" class="bg-white/15 backdrop-blur rounded-2xl px-4 py-2.5 text-center">
            <p class="text-xs text-white/60">{{ $t('sheets.inDatabase') }}</p>
            <p class="text-xl font-bold">{{ dbStats.total_schedules }}</p>
          </div>
          <button @click="loadSummary" :disabled="loading"
            class="bg-white/20 hover:bg-white/30 backdrop-blur px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 text-sm font-medium">
            <RefreshCw class="w-4 h-4" :class="loading ? 'animate-spin' : ''" />
            {{ $t('sheets.refresh') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex flex-wrap gap-2">
      <button v-for="tab in tabs" :key="tab.value"
        @click="activeTab = tab.value"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all',
          activeTab === tab.value
            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25'
            : 'bg-white border border-slate-200 text-slate-600 hover:border-indigo-300 hover:text-indigo-600'
        ]"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ===================== OVERVIEW TAB ===================== -->
    <div v-if="activeTab === 'overview'" class="space-y-5">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
      </div>

      <!-- Summary Cards -->
      <div v-else-if="summary" class="space-y-5">
        <!-- Stats Row -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-5 text-white shadow-lg shadow-indigo-500/20 relative overflow-hidden">
            <div class="absolute -top-4 -right-4 w-20 h-20 bg-white/10 rounded-full blur-lg"></div>
            <div class="relative flex items-center justify-between">
              <div>
                <p class="text-sm text-white/70">{{ $t('sheets.totalSheets') }}</p>
                <p class="text-3xl font-bold mt-1">{{ summary.total_sheets }}</p>
              </div>
              <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <Layers class="w-6 h-6" />
              </div>
            </div>
          </div>
          <div class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-slate-500">{{ $t('sheets.totalGroups') }}</p>
                <p class="text-3xl font-bold text-slate-800 mt-1">{{ summary.total_groups }}</p>
              </div>
              <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                <Users class="w-6 h-6 text-emerald-600" />
              </div>
            </div>
          </div>
          <div class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-slate-500">{{ $t('sheets.totalLessons') }}</p>
                <p class="text-3xl font-bold text-slate-800 mt-1">{{ summary.total_lessons }}</p>
              </div>
              <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                <BookOpen class="w-6 h-6 text-amber-600" />
              </div>
            </div>
          </div>
        </div>

        <!-- Sheets List -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="sheet in summary.sheets" :key="sheet.title"
            @click="selectSheet(sheet)"
            class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg hover:border-indigo-200 transition-all cursor-pointer group"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="w-10 h-10 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/30 group-hover:scale-110 transition-transform">
                <FileSpreadsheet class="w-5 h-5 text-white" />
              </div>
              <div class="flex items-center gap-1.5">
                <span class="bg-emerald-100 text-emerald-700 text-xs px-2 py-0.5 rounded-full font-medium">
                  {{ sheet.groups_count }} {{ $t('sheets.groups') }}
                </span>
              </div>
            </div>
            <h3 class="font-bold text-slate-800 text-sm mb-1 truncate">{{ sheet.title }}</h3>
            <p class="text-xs text-slate-400 mb-3 truncate">{{ sheet.faculty }}</p>
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span class="flex items-center gap-1">
                <BookOpen class="w-3.5 h-3.5" />
                {{ sheet.total_lessons }} {{ $t('sheets.lessons') }}
              </span>
              <span v-if="sheet.error" class="text-red-500 flex items-center gap-1">
                <AlertCircle class="w-3.5 h-3.5" /> {{ $t('sheets.error') }}
              </span>
            </div>

            <!-- Groups mini list -->
            <div v-if="sheet.groups?.length" class="mt-3 pt-3 border-t border-slate-100">
              <div class="flex flex-wrap gap-1">
                <span v-for="(g, i) in sheet.groups.slice(0, 6)" :key="i"
                  class="bg-slate-100 text-slate-600 text-[10px] px-1.5 py-0.5 rounded font-mono">
                  {{ g }}
                </span>
                <span v-if="sheet.groups.length > 6" class="bg-slate-100 text-slate-500 text-[10px] px-1.5 py-0.5 rounded">
                  +{{ sheet.groups.length - 6 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== SHEET DETAIL TAB ===================== -->
    <div v-if="activeTab === 'detail'" class="space-y-5">
      <!-- Sheet Selector -->
      <div class="bg-white rounded-2xl border border-slate-200 p-4 flex flex-col sm:flex-row gap-3 items-center">
        <div class="flex items-center gap-2 text-sm text-slate-500">
          <FileSpreadsheet class="w-4 h-4" />
          {{ $t('sheets.selectSheet') }}:
        </div>
        <select v-model="selectedSheetName" @change="loadSheetDetail"
          class="flex-1 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
          <option value="">-- {{ $t('sheets.chooseSheet') }} --</option>
          <option v-for="s in summary?.sheets || []" :key="s.title" :value="s.title">
            {{ s.title }} ({{ s.groups_count }} {{ $t('sheets.groups') }})
          </option>
        </select>
        <div class="flex gap-2">
          <button @click="viewMode = 'parsed'" :class="['px-3 py-2 rounded-lg text-sm font-medium transition-all',
            viewMode === 'parsed' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500 hover:bg-slate-200']">
            <LayoutList class="w-4 h-4 inline mr-1" /> {{ $t('sheets.parsed') }}
          </button>
          <button @click="viewMode = 'raw'; loadSheetRaw()" :class="['px-3 py-2 rounded-lg text-sm font-medium transition-all',
            viewMode === 'raw' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500 hover:bg-slate-200']">
            <Table2 class="w-4 h-4 inline mr-1" /> {{ $t('sheets.raw') }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="detailLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
      </div>

      <!-- Parsed View -->
      <template v-else-if="sheetDetail && viewMode === 'parsed'">
        <!-- Sheet Info -->
        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div>
              <h3 class="font-bold text-lg text-slate-800">{{ sheetDetail.title }}</h3>
              <p class="text-sm text-slate-400">{{ sheetDetail.groups_count }} {{ $t('sheets.groups') }} · {{ sheetDetail.total_lessons }} {{ $t('sheets.lessons') }}</p>
            </div>
            <button @click="showSyncModal = true; syncSheetName = selectedSheetName"
              class="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-4 py-2.5 rounded-xl text-sm font-semibold shadow-lg shadow-indigo-500/25 hover:shadow-xl transition-all flex items-center justify-center gap-2">
              <Download class="w-4 h-4" />
              {{ $t('sheets.syncToDb') }}
            </button>
          </div>

          <!-- Group filter -->
          <div class="mb-4">
            <select v-model="filterGroup" class="border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500">
              <option value="">{{ $t('sheets.allGroups') }}</option>
              <option v-for="g in sheetDetail.groups" :key="g.name" :value="g.name">{{ g.name }}</option>
            </select>
          </div>

          <!-- Schedule Table per Day -->
          <div v-for="day in weekDays" :key="day.en" class="mb-6">
            <div v-if="getScheduleForDay(day.en).length > 0">
              <h4 class="font-bold text-slate-700 mb-2 flex items-center gap-2">
                <Calendar class="w-4 h-4 text-indigo-500" />
                {{ day.uz }}
                <span class="text-xs text-slate-400 font-normal">({{ day.en }})</span>
              </h4>
              <div class="overflow-x-auto">
                <table class="w-full text-sm border-collapse">
                  <thead>
                    <tr class="bg-slate-50">
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200 w-8">#</th>
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200 w-28">{{ $t('sheets.time') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200">{{ $t('sheets.group') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200">{{ $t('sheets.subject') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200">{{ $t('sheets.type') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200">{{ $t('sheets.teacher') }}</th>
                      <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500 border border-slate-200">{{ $t('sheets.room') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <template v-for="entry in getScheduleForDay(day.en)" :key="`${entry.lesson_number}-${Math.random()}`">
                      <tr v-for="(lesson, groupName) in getFilteredLessons(entry.lessons)" :key="groupName"
                        class="hover:bg-indigo-50/50 transition-colors">
                        <td class="px-3 py-2 border border-slate-200 text-center font-mono text-xs text-slate-500">{{ entry.lesson_number }}</td>
                        <td class="px-3 py-2 border border-slate-200 text-xs font-medium text-slate-600">{{ entry.time }}</td>
                        <td class="px-3 py-2 border border-slate-200">
                          <span class="bg-indigo-100 text-indigo-700 text-[10px] px-1.5 py-0.5 rounded font-mono">{{ groupName }}</span>
                        </td>
                        <td class="px-3 py-2 border border-slate-200 font-medium text-slate-800 max-w-xs truncate">{{ lesson.subject }}</td>
                        <td class="px-3 py-2 border border-slate-200">
                          <span :class="getTypeClass(lesson.type)">{{ getTypeLabel(lesson.type) }}</span>
                        </td>
                        <td class="px-3 py-2 border border-slate-200 text-slate-600">{{ lesson.teacher || '—' }}</td>
                        <td class="px-3 py-2 border border-slate-200 text-xs text-slate-500">
                          {{ [lesson.room, lesson.building].filter(Boolean).join(', ') || '—' }}
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Raw View -->
      <template v-else-if="rawData && viewMode === 'raw'">
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div class="p-4 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h3 class="font-bold text-slate-800">{{ rawData.sheet_name }}</h3>
              <p class="text-xs text-slate-400">{{ rawData.displayed_rows }} / {{ rawData.total_rows }} {{ $t('sheets.rows') }} · {{ rawData.total_cols }} {{ $t('sheets.columns') }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400">{{ $t('sheets.clickToEdit') }}</span>
            </div>
          </div>
          <div class="overflow-x-auto max-h-[70vh]">
            <table class="text-xs border-collapse min-w-full">
              <thead class="sticky top-0 z-10">
                <tr class="bg-slate-100">
                  <th class="px-1.5 py-1.5 border border-slate-300 text-slate-400 font-mono w-8 text-center">#</th>
                  <th v-for="(_, ci) in (rawData.rows[0] || [])" :key="ci"
                    class="px-1.5 py-1.5 border border-slate-300 text-slate-500 font-mono min-w-[120px] text-center">
                    {{ getColLetter(ci) }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, ri) in rawData.rows" :key="ri" class="hover:bg-indigo-50/30">
                  <td class="px-1.5 py-1 border border-slate-200 text-slate-400 font-mono text-center bg-slate-50">{{ ri + 1 }}</td>
                  <td v-for="(cell, ci) in row" :key="ci"
                    @dblclick="startEditCell(ri + 1, ci + 1, cell)"
                    :class="[
                      'px-1.5 py-1 border border-slate-200 cursor-pointer transition-colors',
                      cell ? 'text-slate-800' : 'text-slate-300',
                      editingCell?.row === ri + 1 && editingCell?.col === ci + 1 ? 'bg-yellow-100 ring-2 ring-yellow-400' : 'hover:bg-blue-50',
                      ri === 0 ? 'font-bold bg-indigo-50 text-indigo-800' : '',
                      ri === 1 ? 'font-semibold bg-purple-50 text-purple-800' : ''
                    ]"
                    :title="cell || '(empty)'"
                  >
                    <!-- Edit mode -->
                    <div v-if="editingCell?.row === ri + 1 && editingCell?.col === ci + 1" class="flex items-center gap-1">
                      <input v-model="editingCell.value" @keydown.enter="saveEditCell" @keydown.escape="cancelEditCell"
                        class="w-full border-0 bg-transparent text-xs focus:outline-none" ref="editInput" autofocus />
                      <button @click="saveEditCell" class="text-green-500 hover:text-green-700"><Check class="w-3 h-3" /></button>
                      <button @click="cancelEditCell" class="text-red-500 hover:text-red-700"><X class="w-3 h-3" /></button>
                    </div>
                    <!-- Display mode -->
                    <span v-else class="block max-w-[200px] truncate">{{ cell || '' }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- Empty state -->
      <div v-else-if="!detailLoading && !selectedSheetName" class="text-center py-16">
        <div class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileSpreadsheet class="w-10 h-10 text-slate-300" />
        </div>
        <p class="text-slate-500 font-medium">{{ $t('sheets.selectSheetHint') }}</p>
      </div>
    </div>

    <!-- ===================== SYNC TAB ===================== -->
    <div v-if="activeTab === 'sync'" class="space-y-5">
      <!-- DB Stats -->
      <div v-if="dbStats" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
              <Database class="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <p class="text-sm text-slate-500">{{ $t('sheets.dbSchedules') }}</p>
              <p class="text-2xl font-bold text-slate-800">{{ dbStats.total_schedules }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
              <CheckCircle2 class="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p class="text-sm text-slate-500">{{ $t('sheets.activeSchedules') }}</p>
              <p class="text-2xl font-bold text-slate-800">{{ dbStats.active_schedules }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-5">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
              <Users class="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p class="text-sm text-slate-500">{{ $t('sheets.groupsWithSchedule') }}</p>
              <p class="text-2xl font-bold text-slate-800">{{ dbStats.groups_with_schedule }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Sync Cards per Sheet -->
      <div v-if="summary" class="space-y-4">
        <h3 class="font-bold text-slate-800 text-lg flex items-center gap-2">
          <Download class="w-5 h-5 text-indigo-500" />
          {{ $t('sheets.syncSheets') }}
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="sheet in summary.sheets" :key="sheet.title"
            class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-all">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-xl flex items-center justify-center">
                  <FileSpreadsheet class="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 class="font-bold text-slate-800 text-sm">{{ sheet.title }}</h4>
                  <p class="text-xs text-slate-400">{{ sheet.groups_count }} {{ $t('sheets.groups') }} · {{ sheet.total_lessons }} {{ $t('sheets.lessons') }}</p>
                </div>
              </div>
            </div>

            <!-- Groups list -->
            <div class="flex flex-wrap gap-1 mb-3">
              <span v-for="(g, i) in (sheet.groups || []).slice(0, 8)" :key="i"
                class="bg-slate-100 text-slate-600 text-[10px] px-1.5 py-0.5 rounded font-mono">{{ g }}</span>
              <span v-if="(sheet.groups || []).length > 8" class="text-[10px] text-slate-400">+{{ sheet.groups.length - 8 }}</span>
            </div>

            <div class="flex items-center gap-2">
              <button @click="previewSync(sheet.title)"
                class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-xl text-xs font-medium transition-all flex items-center justify-center gap-1.5">
                <Eye class="w-3.5 h-3.5" /> {{ $t('sheets.preview') }}
              </button>
              <button @click="showSyncModal = true; syncSheetName = sheet.title"
                class="flex-1 bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-3 py-2 rounded-xl text-xs font-semibold shadow-md transition-all flex items-center justify-center gap-1.5 hover:shadow-lg">
                <Download class="w-3.5 h-3.5" /> {{ $t('sheets.sync') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== SYNC MODAL ===================== -->
    <div v-if="showSyncModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="showSyncModal = false">
      <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl overflow-hidden">
        <div class="bg-gradient-to-r from-indigo-500 to-purple-500 p-5 text-white text-center">
          <Download class="w-10 h-10 mx-auto mb-2 opacity-80" />
          <h2 class="text-xl font-bold">{{ $t('sheets.syncToDatabase') }}</h2>
          <p class="text-sm text-white/70 mt-1">{{ syncSheetName }}</p>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">{{ $t('sheets.academicYear') }}</label>
            <input v-model="syncForm.academic_year" type="text" class="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">{{ $t('sheets.semester') }}</label>
            <select v-model.number="syncForm.semester" class="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500">
              <option :value="1">1-{{ $t('sheets.semester') }}</option>
              <option :value="2">2-{{ $t('sheets.semester') }}</option>
            </select>
          </div>
          <div class="flex items-center gap-3">
            <input v-model="syncForm.clear_existing" type="checkbox" id="clearExisting" class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
            <label for="clearExisting" class="text-sm text-slate-600">{{ $t('sheets.clearExisting') }}</label>
          </div>

          <!-- Preview Data -->
          <div v-if="syncPreview" class="bg-slate-50 rounded-xl p-3 space-y-2">
            <p class="text-xs font-medium text-slate-600">{{ $t('sheets.previewResults') }}:</p>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-500">{{ $t('sheets.totalRecords') }}:</span>
              <span class="font-bold text-slate-800">{{ syncPreview.total_records }}</span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-emerald-600">✅ {{ $t('sheets.matchedGroups') }}:</span>
              <span class="font-bold text-emerald-700">{{ syncPreview.matched_groups?.length || 0 }}</span>
            </div>
            <div v-if="syncPreview.unmatched_groups?.length" class="flex items-center justify-between text-xs">
              <span class="text-amber-600">⚠️ {{ $t('sheets.unmatchedGroups') }}:</span>
              <span class="font-bold text-amber-700">{{ syncPreview.unmatched_groups.length }}</span>
            </div>
            <div v-if="syncPreview.unmatched_groups?.length" class="flex flex-wrap gap-1 mt-1">
              <span v-for="g in syncPreview.unmatched_groups" :key="g"
                class="bg-amber-100 text-amber-700 text-[10px] px-1.5 py-0.5 rounded font-mono">{{ g }}</span>
            </div>
          </div>

          <!-- Sync Result -->
          <div v-if="syncResult" :class="[
            'rounded-xl p-3 space-y-1',
            syncResult.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'
          ]">
            <p class="text-sm font-semibold" :class="syncResult.success ? 'text-emerald-700' : 'text-red-700'">
              {{ syncResult.success ? '✅ ' + $t('sheets.syncSuccess') : '❌ ' + $t('sheets.syncFailed') }}
            </p>
            <p v-if="syncResult.synced" class="text-xs text-emerald-600">{{ $t('sheets.synced') }}: {{ syncResult.synced }}</p>
            <p v-if="syncResult.skipped" class="text-xs text-amber-600">{{ $t('sheets.skipped') }}: {{ syncResult.skipped }}</p>
            <!-- Show auto-mapped groups in sync result -->
            <div v-if="syncResult.group_name_map && Object.keys(syncResult.group_name_map).some(k => k !== syncResult.group_name_map[k])" class="mt-2 pt-2 border-t border-emerald-200">
              <p class="text-[10px] text-blue-600 font-medium mb-1">🔄 {{ $t('sheets.autoMapped') }}:</p>
              <div class="flex flex-wrap gap-1">
                <span v-for="(dbName, sheetName) in syncResult.group_name_map" :key="sheetName" v-show="sheetName !== dbName"
                  class="bg-blue-50 text-blue-600 text-[10px] px-1.5 py-0.5 rounded font-mono">
                  {{ sheetName }} → {{ dbName }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button @click="previewSyncInModal" :disabled="syncing"
              class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2">
              <Eye class="w-4 h-4" /> {{ $t('sheets.preview') }}
            </button>
            <button @click="executeSync" :disabled="syncing"
              class="flex-1 bg-gradient-to-r from-indigo-500 to-purple-500 text-white py-2.5 rounded-xl text-sm font-bold shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50">
              <Download v-if="!syncing" class="w-4 h-4" />
              <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              {{ syncing ? $t('sheets.syncing') : $t('sheets.syncNow') }}
            </button>
          </div>
          <button @click="showSyncModal = false; syncResult = null; syncPreview = null"
            class="w-full text-center text-sm text-slate-400 hover:text-slate-600 transition-colors py-1">
            {{ $t('common.close') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===================== PREVIEW MODAL ===================== -->
    <div v-if="showPreviewModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="showPreviewModal = false">
      <div class="bg-white rounded-3xl max-w-3xl w-full shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="p-5 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-white z-10">
          <div>
            <h3 class="font-bold text-lg text-slate-800">{{ $t('sheets.syncPreview') }}</h3>
            <p class="text-sm text-slate-400">{{ previewData?.sheet_name }}</p>
          </div>
          <button @click="showPreviewModal = false" class="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div v-if="previewData" class="p-5 space-y-4">
          <!-- Group Name Mapping Info -->
          <div v-if="previewData.group_name_map && Object.keys(previewData.group_name_map).some(k => k !== previewData.group_name_map[k])" 
            class="bg-blue-50 rounded-xl p-3 border border-blue-200">
            <p class="text-xs font-semibold text-blue-700 mb-2 flex items-center gap-1.5">
              🔄 {{ $t('sheets.autoMapped') }}
            </p>
            <div class="space-y-1">
              <div v-for="(dbName, sheetName) in previewData.group_name_map" :key="sheetName">
                <div v-if="sheetName !== dbName" class="flex items-center gap-2 text-xs">
                  <span class="bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-mono">{{ sheetName }}</span>
                  <span class="text-slate-400">→</span>
                  <span class="bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-mono">{{ dbName }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="bg-emerald-50 rounded-xl p-3 border border-emerald-100">
              <p class="text-xs text-emerald-600 font-medium">{{ $t('sheets.matchedGroups') }}</p>
              <p class="text-2xl font-bold text-emerald-700">{{ previewData.matched_groups?.length || 0 }}</p>
              <div class="flex flex-wrap gap-1 mt-2">
                <span v-for="g in previewData.matched_groups" :key="g.id"
                  class="text-[10px] px-1.5 py-0.5 rounded font-mono" 
                  :class="g.renamed ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'"
                  :title="g.renamed ? `${g.sheet_name} → ${g.db_name}` : g.name">
                  {{ g.renamed ? `${g.sheet_name} → ${g.db_name}` : g.name }}
                </span>
              </div>
            </div>
            <div class="bg-amber-50 rounded-xl p-3 border border-amber-100">
              <p class="text-xs text-amber-600 font-medium">{{ $t('sheets.unmatchedGroups') }}</p>
              <p class="text-2xl font-bold text-amber-700">{{ previewData.unmatched_groups?.length || 0 }}</p>
              <div class="flex flex-wrap gap-1 mt-2">
                <span v-for="g in previewData.unmatched_groups" :key="g"
                  class="bg-amber-100 text-amber-700 text-[10px] px-1.5 py-0.5 rounded font-mono">{{ g }}</span>
              </div>
            </div>
          </div>

          <!-- Records per group -->
          <div>
            <h4 class="font-semibold text-sm text-slate-700 mb-2">{{ $t('sheets.recordsPerGroup') }}</h4>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              <div v-for="(count, gname) in previewData.records_per_group" :key="gname"
                class="bg-slate-50 rounded-lg px-3 py-2 flex items-center justify-between">
                <span class="text-xs font-mono text-slate-600 truncate">{{ gname }}</span>
                <span class="bg-indigo-100 text-indigo-700 text-[10px] px-1.5 py-0.5 rounded-full font-bold ml-2">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== EXCEL IMPORT TAB ===================== -->
    <div v-if="activeTab === 'excel'" class="space-y-5">
      <!-- Excel Import Card -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 space-y-5">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-xl flex items-center justify-center">
            <Upload class="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 class="font-bold text-slate-800">{{ $t('sheets.excelUploadTitle') }}</h3>
            <p class="text-sm text-slate-400">{{ $t('sheets.excelUploadDesc') }}</p>
          </div>
        </div>

        <!-- File Upload -->
        <div class="border-2 border-dashed rounded-2xl p-8 text-center transition-all"
          :class="excelFile ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200 hover:border-indigo-300 bg-slate-50'"
          @dragover.prevent @drop.prevent="handleDrop">
          <input type="file" ref="excelInput" accept=".xlsx,.xls" class="hidden" @change="handleFileSelect" />
          <div v-if="!excelFile" class="space-y-3">
            <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto">
              <Upload class="w-8 h-8 text-slate-400" />
            </div>
            <div>
              <button @click="$refs.excelInput.click()" class="text-indigo-600 font-medium hover:text-indigo-800 transition-colors">
                Fayl tanlash
              </button>
              <span class="text-slate-400 text-sm"> yoki bu yerga tashlang</span>
            </div>
            <p class="text-xs text-slate-400">{{ $t('sheets.onlyXlsx') }}</p>
          </div>
          <div v-else class="flex items-center justify-center gap-3">
            <FileSpreadsheet class="w-8 h-8 text-emerald-500" />
            <div class="text-left">
              <p class="font-medium text-slate-800 text-sm">{{ excelFile.name }}</p>
              <p class="text-xs text-slate-400">{{ (excelFile.size / 1024).toFixed(1) }} KB</p>
            </div>
            <button @click="excelFile = null" class="ml-4 w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-500 hover:bg-red-200 transition-all">
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Settings -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">O'quv yili</label>
            <input v-model="excelForm.academic_year" type="text" class="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">{{ $t('sheets.semester') }}</label>
            <select v-model.number="excelForm.semester" class="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500">
              <option :value="1">1-semestr</option>
              <option :value="2">2-semestr</option>
            </select>
          </div>
          <div class="flex items-end">
            <div class="flex items-center gap-3 pb-2">
              <input v-model="excelForm.clear_existing" type="checkbox" id="excelClearExisting" class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              <label for="excelClearExisting" class="text-sm text-slate-600">{{ $t('sheets.clearExisting') }}</label>
            </div>
          </div>
        </div>

        <!-- Download Template -->
        <div class="flex items-center justify-between bg-slate-50 rounded-xl p-3">
          <div class="flex items-center gap-2 text-sm text-slate-600">
            <Download class="w-4 h-4" />
            <span>{{ $t('sheets.downloadTemplate') }}</span>
          </div>
          <button @click="downloadTemplate" class="text-indigo-600 text-sm font-medium hover:text-indigo-800 transition-colors">
            {{ $t('sheets.downloadTemplate') }}
          </button>
        </div>

        <!-- Import Button -->
        <button @click="importExcelSchedule" :disabled="!excelFile || excelImporting"
          class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white py-3 rounded-xl text-sm font-bold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
          <div v-if="excelImporting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <Upload v-else class="w-4 h-4" />
          {{ excelImporting ? 'Yuklanmoqda...' : 'Jadval yuklash' }}
        </button>

        <!-- Import Result -->
        <div v-if="excelImportResult" class="rounded-xl p-4 space-y-3" :class="excelImportResult.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'">
          <div class="flex items-center gap-2">
            <CheckCircle2 v-if="excelImportResult.success" class="w-5 h-5 text-emerald-500" />
            <AlertCircle v-else class="w-5 h-5 text-red-500" />
            <p class="font-semibold text-sm" :class="excelImportResult.success ? 'text-emerald-700' : 'text-red-700'">
              {{ excelImportResult.message }}
            </p>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="bg-white rounded-lg p-2.5 text-center">
              <p class="text-xs text-slate-500">{{ $t('common.total') }}</p>
              <p class="text-lg font-bold text-slate-800">{{ excelImportResult.total_records || 0 }}</p>
            </div>
            <div class="bg-white rounded-lg p-2.5 text-center">
              <p class="text-xs text-emerald-500">{{ $t('sheets.uploaded') }}</p>
              <p class="text-lg font-bold text-emerald-600">{{ excelImportResult.synced || 0 }}</p>
            </div>
            <div class="bg-white rounded-lg p-2.5 text-center">
              <p class="text-xs text-amber-500">O'tkazildi</p>
              <p class="text-lg font-bold text-amber-600">{{ excelImportResult.skipped || 0 }}</p>
            </div>
            <div class="bg-white rounded-lg p-2.5 text-center">
              <p class="text-xs text-slate-500">{{ $t('common.groups') }}</p>
              <p class="text-lg font-bold text-indigo-600">{{ (excelImportResult.matched_groups || []).length }}</p>
            </div>
          </div>

          <!-- Matched Groups -->
          <div v-if="excelImportResult.matched_groups?.length" class="space-y-1">
            <p class="text-xs font-medium text-emerald-700">✅ Topilgan guruhlar:</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="g in excelImportResult.matched_groups" :key="g" class="bg-emerald-100 text-emerald-700 text-[10px] px-1.5 py-0.5 rounded font-mono">{{ g }}</span>
            </div>
          </div>

          <!-- Unmatched Groups -->
          <div v-if="excelImportResult.unmatched_groups?.length" class="space-y-1">
            <p class="text-xs font-medium text-amber-700">⚠️ Topilmagan guruhlar:</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="g in excelImportResult.unmatched_groups" :key="g" class="bg-amber-100 text-amber-700 text-[10px] px-1.5 py-0.5 rounded font-mono">{{ g }}</span>
            </div>
          </div>

          <!-- Fuzzy Matches -->
          <div v-if="excelImportResult.group_name_map && Object.keys(excelImportResult.group_name_map).some(k => k !== excelImportResult.group_name_map[k])">
            <p class="text-xs font-medium text-blue-700 mb-1">🔄 Avtomatik moslashtirish:</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="(dbName, sheetName) in excelImportResult.group_name_map" :key="sheetName" v-show="sheetName !== dbName"
                class="bg-blue-50 text-blue-600 text-[10px] px-1.5 py-0.5 rounded font-mono">
                {{ sheetName }} → {{ dbName }}
              </span>
            </div>
          </div>

          <!-- Errors -->
          <div v-if="excelImportResult.errors?.length" class="space-y-1">
            <p class="text-xs font-medium text-red-700">❌ Xatoliklar:</p>
            <div class="max-h-32 overflow-y-auto space-y-1">
              <p v-for="(err, i) in excelImportResult.errors.slice(0, 10)" :key="i" class="text-[10px] text-red-600 font-mono bg-red-50 rounded px-2 py-1">{{ err }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Format Info Card -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="font-bold text-slate-800 mb-3 flex items-center gap-2">
          <AlertCircle class="w-5 h-5 text-indigo-500" />
          Excel fayl formati
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-indigo-50 rounded-xl p-4">
            <h4 class="text-sm font-bold text-indigo-800 mb-2">Format 1: Jadval</h4>
            <p class="text-xs text-indigo-600 mb-2">Har bir qator bitta dars:</p>
            <div class="bg-white rounded-lg p-2 text-[10px] font-mono text-slate-600 space-y-0.5">
              <p class="font-bold">Guruh | Kun | Para | Fan | O'qituvchi | Xona | Boshlanish | Tugash</p>
              <p>PI-23-01 | Dushanba | 1 | Matematika | A.Aliyev | 301 | 08:30 | 10:00</p>
            </div>
          </div>
          <div class="bg-purple-50 rounded-xl p-4">
            <h4 class="text-sm font-bold text-purple-800 mb-2">Format 2: Setka</h4>
            <p class="text-xs text-purple-600 mb-2">{{ $t('sheets.groupsColumnDaysRow') }}</p>
            <div class="bg-white rounded-lg p-2 text-[10px] font-mono text-slate-600 space-y-0.5">
              <p class="font-bold">Kun | Para | PI-23-01 | PI-24-01</p>
              <p>Dushanba | 1 | Matematika | Fizika</p>
            </div>
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-3">💡 Guruh nomlari bazadagi nomlar bilan avtomatik moslashtiriladi (masalan: PI_23_01 → PI-23-01)</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import api from '@/services/api'
import {
    AlertCircle,
    BookOpen,
    Calendar,
    Check,
    CheckCircle2,
    Database,
    Download, Eye,
    FileSpreadsheet,
    Layers,
    LayoutList,
    RefreshCw,
    Sheet,
    Table2,
    Upload,
    Users,
    X,
} from 'lucide-vue-next'
import { computed, inject, markRaw, nextTick, onMounted, ref } from 'vue'

const { t } = inject('i18n')

// State
const loading = ref(false)
const detailLoading = ref(false)
const syncing = ref(false)
const activeTab = ref('overview')
const viewMode = ref('parsed')
const summary = ref(null)
const dbStats = ref(null)
const selectedSheetName = ref('')
const sheetDetail = ref(null)
const rawData = ref(null)
const filterGroup = ref('')
const editingCell = ref(null)
const showSyncModal = ref(false)
const showPreviewModal = ref(false)
const syncSheetName = ref('')
const syncPreview = ref(null)
const syncResult = ref(null)
const previewData = ref(null)

const syncForm = ref({
  academic_year: '2025-2026',
  semester: 2,
  clear_existing: true,
})

// Excel import state
const excelFile = ref(null)
const excelInput = ref(null)
const excelImporting = ref(false)
const excelImportResult = ref(null)
const excelForm = ref({
  academic_year: '2025-2026',
  semester: 2,
  clear_existing: true,
})

const tabs = computed(() => [
  { value: 'excel', label: 'Excel import', icon: markRaw(Upload) },
  { value: 'overview', label: t('sheets.overview'), icon: markRaw(Layers) },
  { value: 'detail', label: t('sheets.sheetView'), icon: markRaw(FileSpreadsheet) },
  { value: 'sync', label: t('sheets.syncTab'), icon: markRaw(Download) },
])

const weekDays = [
  { en: 'monday', uz: 'Dushanba' },
  { en: 'tuesday', uz: 'Seshanba' },
  { en: 'wednesday', uz: 'Chorshanba' },
  { en: 'thursday', uz: 'Payshanba' },
  { en: 'friday', uz: 'Juma' },
  { en: 'saturday', uz: 'Shanba' },
]

// Methods
async function loadSummary() {
  loading.value = true
  try {
    const [summaryRes, statsRes] = await Promise.all([
      api.request('/sheets/summary'),
      api.request('/sheets/db-stats'),
    ])
    summary.value = summaryRes
    dbStats.value = statsRes
  } catch (e) {
    console.error('Error loading sheets summary:', e)
  } finally {
    loading.value = false
  }
}

function selectSheet(sheet) {
  selectedSheetName.value = sheet.title
  activeTab.value = 'detail'
  viewMode.value = 'parsed'
  loadSheetDetail()
}

async function loadSheetDetail() {
  if (!selectedSheetName.value) return
  detailLoading.value = true
  try {
    sheetDetail.value = await api.request(`/sheets/sheet/${encodeURIComponent(selectedSheetName.value)}`)
  } catch (e) {
    console.error('Error loading sheet detail:', e)
  } finally {
    detailLoading.value = false
  }
}

async function loadSheetRaw() {
  if (!selectedSheetName.value) return
  detailLoading.value = true
  try {
    rawData.value = await api.request(`/sheets/sheet/${encodeURIComponent(selectedSheetName.value)}/raw?max_rows=100`)
  } catch (e) {
    console.error('Error loading raw data:', e)
  } finally {
    detailLoading.value = false
  }
}

function getScheduleForDay(dayEn) {
  if (!sheetDetail.value?.schedule) return []
  return sheetDetail.value.schedule.filter(s => s.day_en === dayEn)
}

function getFilteredLessons(lessons) {
  if (!lessons) return {}
  if (!filterGroup.value) return lessons
  const filtered = {}
  if (lessons[filterGroup.value]) {
    filtered[filterGroup.value] = lessons[filterGroup.value]
  }
  return filtered
}

function getTypeClass(type) {
  const classes = {
    lecture: 'bg-blue-100 text-blue-700',
    practice: 'bg-emerald-100 text-emerald-700',
    seminar: 'bg-purple-100 text-purple-700',
    lab: 'bg-amber-100 text-amber-700',
  }
  return `text-[10px] px-1.5 py-0.5 rounded font-medium ${classes[type] || 'bg-slate-100 text-slate-600'}`
}

function getTypeLabel(type) {
  const labels = { lecture: "Ma'ruza", practice: 'Amaliy', seminar: 'Seminar', lab: 'Laboratoriya' }
  return labels[type] || type
}

function getColLetter(index) {
  let result = ''
  let i = index
  while (i >= 0) {
    result = String.fromCharCode((i % 26) + 65) + result
    i = Math.floor(i / 26) - 1
  }
  return result
}

function startEditCell(row, col, value) {
  editingCell.value = { row, col, value: value || '', original: value || '' }
  nextTick(() => {
    const inp = document.querySelector('input[autofocus]')
    if (inp) inp.focus()
  })
}

async function saveEditCell() {
  if (!editingCell.value) return
  const { row, col, value, original } = editingCell.value
  if (value === original) {
    editingCell.value = null
    return
  }
  try {
    await api.request(`/sheets/sheet/${encodeURIComponent(selectedSheetName.value)}/cell?row=${row}&col=${col}`, {
      method: 'PUT',
      body: JSON.stringify({ value }),
    })
    // Update local data
    if (rawData.value?.rows) {
      rawData.value.rows[row - 1][col - 1] = value
    }
    editingCell.value = null
  } catch (e) {
    console.error('Error saving cell:', e)
  }
}

function cancelEditCell() {
  editingCell.value = null
}

async function previewSync(sheetName) {
  try {
    previewData.value = await api.request(`/sheets/sync-preview/${encodeURIComponent(sheetName)}`)
    showPreviewModal.value = true
  } catch (e) {
    console.error('Error previewing sync:', e)
  }
}

async function previewSyncInModal() {
  try {
    syncPreview.value = await api.request(`/sheets/sync-preview/${encodeURIComponent(syncSheetName.value)}`)
  } catch (e) {
    console.error('Error previewing sync:', e)
  }
}

async function executeSync() {
  syncing.value = true
  syncResult.value = null
  try {
    syncResult.value = await api.request('/sheets/sync', {
      method: 'POST',
      body: JSON.stringify({
        sheet_name: syncSheetName.value,
        clear_existing: syncForm.value.clear_existing,
        academic_year: syncForm.value.academic_year,
        semester: syncForm.value.semester,
      }),
    })
    // Refresh DB stats
    dbStats.value = await api.request('/sheets/db-stats')
  } catch (e) {
    console.error('Error syncing:', e)
    syncResult.value = { success: false, error: e.message }
  } finally {
    syncing.value = false
  }
}

// ============ Excel Import Methods ============

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) excelFile.value = file
}

function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    excelFile.value = file
  }
}

async function downloadTemplate() {
  try {
    const blob = await api.downloadExcelTemplate('schedules')
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'jadval_shablon.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Error downloading template:', e)
  }
}

async function importExcelSchedule() {
  if (!excelFile.value) return
  excelImporting.value = true
  excelImportResult.value = null
  try {
    excelImportResult.value = await api.importSchedulesFromExcel(
      excelFile.value,
      excelForm.value.academic_year,
      excelForm.value.semester,
      excelForm.value.clear_existing
    )
    // Refresh DB stats
    try {
      dbStats.value = await api.request('/sheets/db-stats')
    } catch (_) {}
  } catch (e) {
    console.error('Error importing Excel schedule:', e)
    excelImportResult.value = { success: false, message: e.message || "Xatolik yuz berdi", errors: [e.message] }
  } finally {
    excelImporting.value = false
  }
}

onMounted(() => {
  activeTab.value = 'excel'
  loadSummary()
})
</script>
