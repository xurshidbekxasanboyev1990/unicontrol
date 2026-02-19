<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25">
            <CalendarCheck :size="22" />
          </div>
          {{ t('exams.title') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">{{ t('exams.description') }}</p>
      </div>
      <button
        @click="openAssignModal"
        class="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white shadow-lg hover:bg-emerald-700 transition-all"
      >
        <Plus :size="16" />
        {{ t('exams.addExam') }}
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 mb-2">
          <FileText :size="18" />
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ examStats.total_exams }}</p>
        <p class="text-xs text-gray-500">{{ t('exams.totalExams') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-100 text-blue-600 mb-2">
          <Building2 :size="18" />
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ examStats.total_groups }}</p>
        <p class="text-xs text-gray-500">{{ t('exams.groupsWithExams') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-100 text-purple-600 mb-2">
          <BookOpen :size="18" />
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ examStats.total_subjects }}</p>
        <p class="text-xs text-gray-500">{{ t('exams.subjects') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-100 text-amber-600 mb-2">
          <Clock :size="18" />
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ examStats.upcoming_exams }}</p>
        <p class="text-xs text-gray-500">{{ t('exams.upcoming') }}</p>
      </div>
    </div>

    <!-- View Mode Tabs -->
    <div class="flex gap-2 bg-white rounded-xl p-1 border border-gray-200 w-fit">
      <button
        v-for="tab in viewTabs"
        :key="tab.key"
        @click="viewMode = tab.key"
        :class="['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all', viewMode === tab.key ? 'bg-emerald-600 text-white shadow' : 'text-gray-500 hover:bg-gray-100']"
      >
        <component :is="tab.icon" :size="16" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ============ FACULTY VIEW ============ -->
    <div v-if="viewMode === 'faculty'">
      <div class="flex flex-wrap items-center gap-3 mb-6">
        <select v-model="filterFaculty" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm">
          <option value="">Barcha fakultetlar</option>
          <option v-for="f in faculties" :key="f.name" :value="f.name">{{ f.name }} ({{ f.group_count }})</option>
        </select>
        <select v-model="filterType" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm" @change="loadExams">
          <option value="">{{ t('exams.allTypes') }}</option>
          <option value="exam">{{ t('exams.typeExam') }}</option>
          <option value="midterm">{{ t('exams.typeMidterm') }}</option>
          <option value="retake">{{ t('exams.typeRetake') }}</option>
          <option value="final">{{ t('exams.typeFinal') }}</option>
        </select>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-16">
        <Loader2 :size="32" class="animate-spin text-emerald-500" />
      </div>

      <!-- Faculty → Groups hierarchy -->
      <div v-else-if="facultyGrouped.length > 0" class="space-y-6">
        <div v-for="fac in facultyGrouped" :key="fac.faculty" class="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden">
          <!-- Faculty header -->
          <button
            @click="fac.expanded = !fac.expanded"
            class="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
                <GraduationCap :size="20" />
              </div>
              <div class="text-left">
                <h3 class="font-bold text-gray-900">{{ fac.faculty }}</h3>
                <p class="text-xs text-gray-500">{{ fac.groups.length }} guruh · {{ fac.examCount }} imtihon</p>
              </div>
            </div>
            <ChevronDown :class="['w-5 h-5 text-gray-400 transition-transform', fac.expanded && 'rotate-180']" />
          </button>

          <!-- Groups inside faculty -->
          <div v-if="fac.expanded" class="border-t border-gray-100">
            <div v-for="grp in fac.groups" :key="grp.name" class="border-b border-gray-50 last:border-b-0">
              <!-- Group header -->
              <button
                @click="grp.expanded = !grp.expanded"
                class="w-full flex items-center justify-between px-6 py-3 pl-12 hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center gap-3">
                  <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 text-blue-600 text-xs font-bold">
                    {{ grp.course_year }}K
                  </div>
                  <div class="text-left">
                    <h4 class="font-semibold text-gray-800 text-sm">{{ grp.name }}</h4>
                    <p class="text-[11px] text-gray-400">{{ grp.exams.length }} ta imtihon</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span v-if="grp.exams.length" class="rounded-full bg-emerald-100 text-emerald-700 px-2 py-0.5 text-[10px] font-bold">
                    {{ grp.exams.length }}
                  </span>
                  <ChevronRight :class="['w-4 h-4 text-gray-400 transition-transform', grp.expanded && 'rotate-90']" />
                </div>
              </button>

              <!-- Exams for this group -->
              <div v-if="grp.expanded" class="bg-gray-50/50 px-6 py-3 pl-20 space-y-2">
                <div v-if="grp.exams.length === 0" class="text-sm text-gray-400 py-2">
                  Imtihon belgilanmagan
                </div>
                <div
                  v-for="exam in grp.exams"
                  :key="exam.id"
                  class="flex items-center justify-between rounded-xl bg-white p-3 border border-gray-100 hover:border-emerald-200 hover:shadow-sm transition-all group"
                >
                  <div class="flex items-center gap-3">
                    <div class="flex flex-col items-center rounded-lg bg-emerald-50 px-2 py-1 min-w-[50px]">
                      <span class="text-xs font-bold text-emerald-700">{{ formatShortDate(exam.exam_date) }}</span>
                      <span class="text-[10px] text-emerald-500">{{ exam.start_time }}</span>
                    </div>
                    <div>
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-semibold text-gray-900">{{ exam.subject }}</span>
                        <span :class="['rounded-full px-2 py-0.5 text-[9px] font-bold uppercase', examTypeClass(exam.exam_type)]">
                          {{ examTypeName(exam.exam_type) }}
                        </span>
                      </div>
                      <div class="flex gap-3 text-[11px] text-gray-400 mt-0.5">
                        <span v-if="exam.room" class="flex items-center gap-0.5"><DoorOpen :size="10" /> {{ exam.room }}</span>
                        <span v-if="exam.teacher_name" class="flex items-center gap-0.5"><User :size="10" /> {{ exam.teacher_name }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="editExam(exam)" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-emerald-600">
                      <Pencil :size="13" />
                    </button>
                    <button @click="deleteExam(exam)" class="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600">
                      <Trash2 :size="13" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-16 text-gray-400">
        <CalendarCheck :size="48" class="mb-3 opacity-50" />
        <p class="text-sm">{{ t('exams.noExams') }}</p>
      </div>
    </div>

    <!-- ============ TIMELINE VIEW ============ -->
    <div v-if="viewMode === 'timeline'">
      <div class="flex flex-wrap items-center gap-3 mb-6">
        <select v-model="filterGroup" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm" @change="loadExams">
          <option :value="null">{{ t('exams.allGroups') }}</option>
          <option v-for="g in allGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <select v-model="filterType" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm" @change="loadExams">
          <option value="">{{ t('exams.allTypes') }}</option>
          <option value="exam">{{ t('exams.typeExam') }}</option>
          <option value="midterm">{{ t('exams.typeMidterm') }}</option>
          <option value="retake">{{ t('exams.typeRetake') }}</option>
          <option value="final">{{ t('exams.typeFinal') }}</option>
        </select>
        <input v-model="filterDateFrom" type="date" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm" @change="loadExams" />
        <span class="text-gray-400 text-sm">—</span>
        <input v-model="filterDateTo" type="date" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm" @change="loadExams" />
      </div>

      <div v-if="loading" class="flex items-center justify-center py-16">
        <Loader2 :size="32" class="animate-spin text-emerald-500" />
      </div>

      <div v-else-if="groupedByDate.length > 0" class="space-y-6">
        <div v-for="dateGroup in groupedByDate" :key="dateGroup.date" class="space-y-3">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 font-bold text-sm flex-col leading-none">
              <span class="text-lg">{{ getDayNum(dateGroup.date) }}</span>
              <span class="text-[10px] uppercase">{{ getMonthShort(dateGroup.date) }}</span>
            </div>
            <div>
              <p class="font-semibold text-gray-900">{{ formatDate(dateGroup.date) }}</p>
              <p class="text-xs text-gray-500">{{ getDayName(dateGroup.date) }} · {{ dateGroup.items.length }} {{ t('exams.examsCount') }}</p>
            </div>
          </div>

          <div class="ml-6 border-l-2 border-emerald-200 pl-6 space-y-3">
            <div
              v-for="exam in dateGroup.items"
              :key="exam.id"
              class="rounded-2xl bg-white p-4 shadow-sm border border-gray-100 hover:border-emerald-200 hover:shadow-md transition-all group"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-semibold text-gray-900">{{ exam.subject }}</h4>
                    <span :class="['rounded-full px-2 py-0.5 text-[10px] font-bold uppercase', examTypeClass(exam.exam_type)]">
                      {{ examTypeName(exam.exam_type) }}
                    </span>
                  </div>
                  <div class="flex flex-wrap gap-3 text-xs text-gray-500">
                    <span class="flex items-center gap-1"><Building2 :size="12" /> {{ exam.group_name }}</span>
                    <span class="flex items-center gap-1"><Clock :size="12" /> {{ exam.start_time }} - {{ exam.end_time }}</span>
                    <span v-if="exam.room" class="flex items-center gap-1"><DoorOpen :size="12" /> {{ exam.room }}</span>
                    <span v-if="exam.teacher_name" class="flex items-center gap-1"><User :size="12" /> {{ exam.teacher_name }}</span>
                  </div>
                  <p v-if="exam.notes" class="mt-1.5 text-xs text-gray-400 italic">{{ exam.notes }}</p>
                </div>
                <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="editExam(exam)" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-emerald-600">
                    <Pencil :size="14" />
                  </button>
                  <button @click="deleteExam(exam)" class="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-16 text-gray-400">
        <CalendarCheck :size="48" class="mb-3 opacity-50" />
        <p class="text-sm">{{ t('exams.noExams') }}</p>
      </div>
    </div>

    <!-- ============ ASSIGN MODAL (3-step wizard) ============ -->
    <Transition name="fade">
      <div v-if="showAssignModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="closeModal">
        <div class="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden">
          <!-- Modal header with steps -->
          <div class="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-4">
            <h3 class="text-lg font-semibold text-white">
              {{ editingExam ? t('exams.editExam') : t('exams.addExam') }}
            </h3>
            <div v-if="!editingExam" class="flex items-center gap-2 mt-3">
              <div v-for="s in 3" :key="s" class="flex items-center gap-2">
                <div :class="['flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-all', assignStep >= s ? 'bg-white text-emerald-600' : 'bg-white/20 text-white/60']">
                  {{ s }}
                </div>
                <span :class="['text-xs font-medium hidden sm:inline', assignStep >= s ? 'text-white' : 'text-white/50']">
                  {{ s === 1 ? "Fakultet" : s === 2 ? 'Guruhlar' : 'Imtihon' }}
                </span>
                <div v-if="s < 3" class="w-4 sm:w-6 h-0.5 bg-white/20 mx-0.5"></div>
              </div>
            </div>
          </div>

          <!-- Step 1: Select Faculty / Direction -->
          <div v-if="assignStep === 1 && !editingExam" class="p-6 max-h-[60vh] overflow-y-auto">
            <div class="flex gap-2 mb-5">
              <button
                @click="selectMode = 'faculty'"
                :class="['flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium border-2 transition-all', selectMode === 'faculty' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-gray-200 text-gray-500 hover:border-gray-300']"
              >
                <GraduationCap :size="18" />
                Fakultet bo'yicha
              </button>
              <button
                @click="selectMode = 'direction'"
                :class="['flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium border-2 transition-all', selectMode === 'direction' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-gray-200 text-gray-500 hover:border-gray-300']"
              >
                <Compass :size="18" />
                Yo'nalish bo'yicha
              </button>
            </div>

            <!-- Faculty list -->
            <div v-if="selectMode === 'faculty'" class="space-y-2">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Fakultetni tanlang</p>
              <div
                v-for="f in faculties"
                :key="f.name"
                @click="selectedFaculty = selectedFaculty === f.name ? null : f.name; selectedDirection = null"
                :class="['flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all', selectedFaculty === f.name ? 'border-emerald-500 bg-emerald-50' : 'border-gray-100 hover:border-emerald-200 hover:bg-emerald-50/30']"
              >
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
                    <GraduationCap :size="20" />
                  </div>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">{{ f.name }}</p>
                    <p class="text-xs text-gray-400">{{ f.group_count }} guruh</p>
                  </div>
                </div>
                <div v-if="selectedFaculty === f.name" class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-white">
                  <Check :size="14" />
                </div>
              </div>
              <div v-if="faculties.length === 0" class="text-center py-8 text-gray-400 text-sm">Fakultetlar topilmadi</div>
            </div>

            <!-- Direction list -->
            <div v-if="selectMode === 'direction'" class="space-y-2">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Yo'nalishni tanlang</p>
              <div
                v-for="d in directions"
                :key="d.id"
                @click="selectedDirection = selectedDirection === d.id ? null : d.id; selectedFaculty = null"
                :class="['flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all', selectedDirection === d.id ? 'border-emerald-500 bg-emerald-50' : 'border-gray-100 hover:border-emerald-200 hover:bg-emerald-50/30']"
              >
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100 text-teal-600">
                    <Compass :size="20" />
                  </div>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">{{ d.name }}</p>
                    <p v-if="d.code" class="text-xs text-gray-400">{{ d.code }}</p>
                  </div>
                </div>
                <div v-if="selectedDirection === d.id" class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-white">
                  <Check :size="14" />
                </div>
              </div>
              <div v-if="directions.length === 0" class="text-center py-8 text-gray-400 text-sm">Yo'nalishlar topilmadi</div>
            </div>
          </div>

          <!-- Step 2: Select Groups -->
          <div v-if="assignStep === 2 && !editingExam" class="p-6 max-h-[60vh] overflow-y-auto">
            <div class="flex items-center justify-between mb-4">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Guruhlarni tanlang</p>
              <button @click="toggleAllGroups" class="text-xs font-medium text-emerald-600 hover:text-emerald-700">
                {{ selectedGroupIds.length === step2Groups.length ? 'Bekor qilish' : 'Barchasini tanlash' }}
              </button>
            </div>

            <div v-if="loadingGroups" class="flex items-center justify-center py-12">
              <Loader2 :size="28" class="animate-spin text-emerald-500" />
            </div>

            <div v-else class="space-y-2">
              <div v-for="section in groupsByCourse" :key="section.course">
                <p class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2 mt-3">{{ section.course }}-kurs</p>
                <div class="grid grid-cols-2 gap-2">
                  <div
                    v-for="g in section.groups"
                    :key="g.id"
                    @click="toggleGroup(g.id)"
                    :class="['flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all', selectedGroupIds.includes(g.id) ? 'border-emerald-500 bg-emerald-50' : 'border-gray-100 hover:border-emerald-200']"
                  >
                    <div :class="['flex h-5 w-5 items-center justify-center rounded border-2 transition-all', selectedGroupIds.includes(g.id) ? 'border-emerald-500 bg-emerald-500' : 'border-gray-300']">
                      <Check v-if="selectedGroupIds.includes(g.id)" :size="12" class="text-white" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-semibold text-gray-800 truncate">{{ g.name }}</p>
                      <p class="text-[10px] text-gray-400">{{ g.exam_count }} imtihon</p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="step2Groups.length === 0" class="text-center py-8 text-gray-400 text-sm">Guruhlar topilmadi</div>
            </div>

            <div v-if="selectedGroupIds.length > 0" class="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200">
              <p class="text-sm text-emerald-700 font-medium">✅ {{ selectedGroupIds.length }} ta guruh tanlandi</p>
            </div>
          </div>

          <!-- Step 3: Exam Details (also for edit) -->
          <div v-if="assignStep === 3 || editingExam" class="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
            <!-- Selected groups summary (new) -->
            <div v-if="!editingExam && selectedGroupIds.length > 0" class="p-3 rounded-xl bg-emerald-50 border border-emerald-200 mb-2">
              <p class="text-xs font-medium text-emerald-700 mb-1">Tanlangan guruhlar ({{ selectedGroupIds.length }}):</p>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="gid in selectedGroupIds" :key="gid" class="rounded-full bg-emerald-100 text-emerald-700 px-2.5 py-0.5 text-[11px] font-medium">
                  {{ getGroupName(gid) }}
                </span>
              </div>
            </div>

            <!-- Edit mode -->
            <div v-if="editingExam" class="p-3 rounded-xl bg-gray-50 border border-gray-200 mb-2">
              <p class="text-sm text-gray-600"><span class="font-medium">Guruh:</span> {{ editingExam.group_name }}</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="col-span-2">
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.subject') }} *</label>
                <input v-model="examForm.subject" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" :placeholder="t('exams.subjectPlaceholder')" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.examType') }}</label>
                <select v-model="examForm.exam_type" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500">
                  <option value="exam">{{ t('exams.typeExam') }}</option>
                  <option value="midterm">{{ t('exams.typeMidterm') }}</option>
                  <option value="retake">{{ t('exams.typeRetake') }}</option>
                  <option value="final">{{ t('exams.typeFinal') }}</option>
                </select>
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.date') }} *</label>
                <input v-model="examForm.exam_date" type="date" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.startTime') }} *</label>
                <input v-model="examForm.start_time" type="time" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.endTime') }} *</label>
                <input v-model="examForm.end_time" type="time" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.room') }}</label>
                <input v-model="examForm.room" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" placeholder="401" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.building') }}</label>
                <input v-model="examForm.building" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" placeholder="A bino" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.teacher') }}</label>
                <input v-model="examForm.teacher_name" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" :placeholder="t('exams.teacherPlaceholder')" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.semester') }}</label>
                <select v-model.number="examForm.semester" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500">
                  <option :value="null">—</option>
                  <option :value="1">1-semestr</option>
                  <option :value="2">2-semestr</option>
                </select>
              </div>
            </div>
            <div>
              <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('exams.notes') }}</label>
              <textarea v-model="examForm.notes" rows="2" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500" :placeholder="t('exams.notesPlaceholder')"></textarea>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 bg-gray-50 flex items-center justify-between">
            <button
              v-if="assignStep > 1 && !editingExam"
              @click="assignStep--"
              class="flex items-center gap-1 rounded-xl px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <ChevronLeft :size="16" /> Orqaga
            </button>
            <div v-else></div>

            <div class="flex items-center gap-3">
              <button @click="closeModal" class="rounded-xl px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors">
                {{ t('common.cancel') }}
              </button>

              <button
                v-if="assignStep === 1 && !editingExam"
                @click="goToStep2"
                :disabled="!selectedFaculty && !selectedDirection"
                class="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition-all"
              >
                Keyingi <ChevronRight :size="16" />
              </button>

              <button
                v-if="assignStep === 2 && !editingExam"
                @click="assignStep = 3"
                :disabled="selectedGroupIds.length === 0"
                class="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition-all"
              >
                Keyingi <ChevronRight :size="16" />
              </button>

              <button
                v-if="assignStep === 3 || editingExam"
                @click="saveExam"
                :disabled="saving || !examForm.subject || !examForm.exam_date || !examForm.start_time || !examForm.end_time"
                class="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition-all"
              >
                <Loader2 v-if="saving" :size="16" class="animate-spin" />
                {{ editingExam ? t('common.save') : `Tayinlash (${selectedGroupIds.length} guruh)` }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg text-sm', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {
    BookOpen, Building2, CalendarCheck, Check, ChevronDown, ChevronLeft, ChevronRight,
    Clock, Compass, DoorOpen, FileText, GraduationCap, LayoutList, Loader2,
    Pencil, Plus, Trash2, User
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

// State
const loading = ref(false)
const loadingGroups = ref(false)
const saving = ref(false)
const viewMode = ref('faculty')
const exams = ref([])
const allGroups = ref([])
const faculties = ref([])
const directions = ref([])
const examStats = ref({ total_exams: 0, total_groups: 0, total_subjects: 0, upcoming_exams: 0 })

// Filters
const filterGroup = ref(null)
const filterType = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const filterFaculty = ref('')

// Assign wizard
const showAssignModal = ref(false)
const assignStep = ref(1)
const selectMode = ref('faculty')
const selectedFaculty = ref(null)
const selectedDirection = ref(null)
const selectedGroupIds = ref([])
const step2Groups = ref([])
const editingExam = ref(null)
const toast = ref(null)

const defaultExamForm = {
  subject: '', exam_type: 'exam', exam_date: '', start_time: '09:00', end_time: '11:00',
  room: '', building: '', teacher_name: '', semester: null, notes: '',
}
const examForm = ref({ ...defaultExamForm })

const viewTabs = [
  { key: 'faculty', label: "Fakultet ko'rinish", icon: markRaw(GraduationCap) },
  { key: 'timeline', label: "Sana bo'yicha", icon: markRaw(LayoutList) },
]

// Date helpers
const dayNames = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
const monthNames = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']
const getDayNum = (d) => new Date(d).getDate()
const getMonthShort = (d) => monthNames[new Date(d).getMonth()]
const getDayName = (d) => dayNames[new Date(d).getDay()]
const formatDate = (d) => { const dt = new Date(d); return `${dt.getDate()} ${monthNames[dt.getMonth()]} ${dt.getFullYear()}` }
const formatShortDate = (d) => { const dt = new Date(d); return `${dt.getDate()}/${dt.getMonth() + 1}` }

// Type helpers
const examTypeClass = (type) => ({
  exam: 'bg-emerald-100 text-emerald-700', midterm: 'bg-amber-100 text-amber-700',
  retake: 'bg-orange-100 text-orange-700', final: 'bg-red-100 text-red-700',
}[type] || 'bg-gray-100 text-gray-700')

const examTypeName = (type) => ({
  exam: t('exams.typeExam'), midterm: t('exams.typeMidterm'),
  retake: t('exams.typeRetake'), final: t('exams.typeFinal'),
}[type] || type)

// Faculty → Groups → Exams hierarchy
const facultyGrouped = computed(() => {
  const examsByGroup = {}
  exams.value.forEach(e => {
    if (!examsByGroup[e.group_id]) examsByGroup[e.group_id] = []
    examsByGroup[e.group_id].push(e)
  })

  const facMap = {}
  allGroups.value.forEach(g => {
    const fac = g.faculty || 'Boshqa'
    if (filterFaculty.value && fac !== filterFaculty.value) return
    if (!facMap[fac]) facMap[fac] = { faculty: fac, groups: [], examCount: 0, expanded: true }
    const grpExams = examsByGroup[g.id] || []
    facMap[fac].groups.push({ id: g.id, name: g.name, course_year: g.course_year, exams: grpExams, expanded: false })
    facMap[fac].examCount += grpExams.length
  })

  return Object.values(facMap).sort((a, b) => a.faculty.localeCompare(b.faculty))
})

// Timeline
const groupedByDate = computed(() => {
  const map = {}
  exams.value.forEach(e => {
    if (!map[e.exam_date]) map[e.exam_date] = { date: e.exam_date, items: [] }
    map[e.exam_date].items.push(e)
  })
  return Object.values(map).sort((a, b) => a.date.localeCompare(b.date))
})

// Step 2 groups by course
const groupsByCourse = computed(() => {
  const map = {}
  step2Groups.value.forEach(g => {
    const c = g.course_year || 1
    if (!map[c]) map[c] = { course: c, groups: [] }
    map[c].groups.push(g)
  })
  return Object.values(map).sort((a, b) => a.course - b.course)
})

const getGroupName = (gid) => {
  const g = step2Groups.value.find(gr => gr.id === gid)
  return g ? g.name : `#${gid}`
}

// API
const loadExams = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterGroup.value) params.append('group_id', filterGroup.value)
    if (filterType.value) params.append('exam_type', filterType.value)
    if (filterDateFrom.value) params.append('date_from', filterDateFrom.value)
    if (filterDateTo.value) params.append('date_to', filterDateTo.value)
    const qs = params.toString() ? `?${params.toString()}` : ''
    const res = await api.request(`/rooms-exams/exams${qs}`)
    exams.value = res.items || []
  } catch (e) { console.error('Load exams error:', e) }
  finally { loading.value = false }
}

const loadStats = async () => {
  try { examStats.value = await api.request('/rooms-exams/exams/stats') } catch (e) { console.error(e) }
}

const loadAllGroups = async () => {
  try { const res = await api.request('/rooms-exams/exams/groups'); allGroups.value = res.items || [] } catch (e) { console.error(e) }
}

const loadFaculties = async () => {
  try { const res = await api.request('/rooms-exams/exams/faculties'); faculties.value = res.items || [] } catch (e) { console.error(e) }
}

const loadDirections = async () => {
  try { const res = await api.request('/rooms-exams/exams/directions'); directions.value = res.items || [] } catch (e) { console.error(e) }
}

const loadFacultyGroups = async (faculty) => {
  loadingGroups.value = true
  try { const res = await api.request(`/rooms-exams/exams/faculty-groups?faculty=${encodeURIComponent(faculty)}`); step2Groups.value = res.items || [] }
  catch (e) { console.error(e) }
  finally { loadingGroups.value = false }
}

// Modal
const openAssignModal = () => {
  showAssignModal.value = true
  assignStep.value = 1
  selectMode.value = 'faculty'
  selectedFaculty.value = null
  selectedDirection.value = null
  selectedGroupIds.value = []
  step2Groups.value = []
  examForm.value = { ...defaultExamForm }
  editingExam.value = null
  loadFaculties()
  loadDirections()
}

const closeModal = () => {
  showAssignModal.value = false
  editingExam.value = null
  assignStep.value = 1
  examForm.value = { ...defaultExamForm }
}

const goToStep2 = async () => {
  if (selectMode.value === 'faculty' && selectedFaculty.value) {
    await loadFacultyGroups(selectedFaculty.value)
  } else if (selectMode.value === 'direction' && selectedDirection.value) {
    loadingGroups.value = true
    try { const res = await api.request('/rooms-exams/exams/groups'); step2Groups.value = res.items || [] }
    catch (e) { console.error(e) }
    finally { loadingGroups.value = false }
  }
  selectedGroupIds.value = []
  assignStep.value = 2
}

const toggleGroup = (gid) => {
  const idx = selectedGroupIds.value.indexOf(gid)
  if (idx >= 0) selectedGroupIds.value.splice(idx, 1)
  else selectedGroupIds.value.push(gid)
}

const toggleAllGroups = () => {
  if (selectedGroupIds.value.length === step2Groups.value.length) selectedGroupIds.value = []
  else selectedGroupIds.value = step2Groups.value.map(g => g.id)
}

// CRUD
const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const saveExam = async () => {
  if (!examForm.value.subject || !examForm.value.exam_date) return
  saving.value = true
  try {
    if (editingExam.value) {
      await api.request(`/rooms-exams/exams/${editingExam.value.id}`, { method: 'PUT', body: examForm.value })
      showToast(t('exams.examUpdated'))
    } else {
      await api.request('/rooms-exams/exams/assign-groups', {
        method: 'POST',
        body: { group_ids: selectedGroupIds.value, ...examForm.value }
      })
      showToast(`${selectedGroupIds.value.length} ta guruhga imtihon tayinlandi`)
    }
    closeModal()
    await Promise.all([loadExams(), loadStats(), loadAllGroups()])
  } catch (e) { showToast(e.message || 'Xatolik', 'error') }
  finally { saving.value = false }
}

const editExam = (exam) => {
  editingExam.value = exam
  showAssignModal.value = true
  assignStep.value = 3
  examForm.value = {
    subject: exam.subject, exam_type: exam.exam_type, exam_date: exam.exam_date,
    start_time: exam.start_time, end_time: exam.end_time, room: exam.room || '',
    building: exam.building || '', teacher_name: exam.teacher_name || '',
    semester: exam.semester, notes: exam.notes || '',
  }
}

const deleteExam = async (exam) => {
  if (!confirm(`"${exam.subject}" — ${t('exams.confirmDelete')}`)) return
  try {
    await api.request(`/rooms-exams/exams/${exam.id}`, { method: 'DELETE' })
    showToast(t('exams.examDeleted'))
    await Promise.all([loadExams(), loadStats(), loadAllGroups()])
  } catch (e) { showToast(e.message || 'Xatolik', 'error') }
}

// Init
onMounted(async () => {
  await Promise.all([loadAllGroups(), loadStats(), loadFaculties()])
  await loadExams()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
