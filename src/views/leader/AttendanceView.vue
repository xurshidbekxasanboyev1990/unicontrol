<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('attendance.takeAttendance') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('attendance.writeForLesson') }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="selectedDate" class="px-4 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all">
          <option v-for="d in recentDates" :key="d" :value="d">
            {{ formatDate(d) }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <Loader2 class="w-10 h-10 text-emerald-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-500">Yuklanmoqda...</p>
      </div>
    </div>

    <template v-else>
      <!-- Today's Lessons from Schedule -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="p-5 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                <BookOpen class="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <h2 class="font-semibold text-slate-800">{{ selectedDayName }} — Darslar</h2>
                <p class="text-sm text-slate-500">{{ todayLessons.length }} ta dars jadvaldagilar</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="todayLessons.length === 0" class="p-8 text-center">
          <Coffee class="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p class="text-slate-500 font-medium">Bu kunda dars yo'q</p>
          <p class="text-sm text-slate-400 mt-1">Jadvalda bu kunga dars qo'yilmagan</p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="lesson in todayLessons"
            :key="lesson.id"
            @click="selectLesson(lesson)"
            :class="[
              'p-4 flex items-center gap-4 cursor-pointer transition-all',
              selectedLesson?.id === lesson.id
                ? 'bg-emerald-50 border-l-4 border-l-emerald-500'
                : 'hover:bg-slate-50 border-l-4 border-l-transparent'
            ]"
          >
            <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="selectedLesson?.id === lesson.id ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600'"
            >
              <span class="text-lg font-bold">{{ lesson.lesson_number }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-slate-800 truncate">{{ lesson.subject }}</p>
              <div class="flex items-center gap-3 mt-1 text-sm text-slate-500">
                <span class="flex items-center gap-1">
                  <Clock class="w-3.5 h-3.5" />
                  {{ lesson.timeDisplay }}
                </span>
                <span v-if="lesson.teacher_name" class="flex items-center gap-1">
                  <User class="w-3.5 h-3.5" />
                  {{ lesson.teacher_name }}
                </span>
                <span v-if="lesson.room" class="flex items-center gap-1">
                  <MapPin class="w-3.5 h-3.5" />
                  {{ lesson.room }}
                </span>
              </div>
            </div>
            <div class="flex-shrink-0">
              <div v-if="lessonAttendanceSaved[lesson.id]" class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-medium">
                <CheckCircle class="w-3.5 h-3.5" />
                Saqlangan
              </div>
              <div v-else-if="selectedLesson?.id === lesson.id" class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-medium">
                <CheckCircle class="w-3.5 h-3.5" />
                Tanlangan
              </div>
              <div v-else class="px-3 py-1.5 bg-slate-100 text-slate-500 rounded-lg text-xs font-medium">
                Tanlang
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No lesson selected warning -->
      <div v-if="!selectedLesson && todayLessons.length > 0" class="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <AlertCircle class="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <h3 class="font-semibold text-amber-900">Darsni tanlang</h3>
            <p class="text-sm text-amber-700">Davomat olish uchun yuqoridagi darslardan birini tanlang</p>
          </div>
        </div>
      </div>

      <!-- Attendance Form (shown when lesson is selected) -->
      <template v-if="selectedLesson">
        <!-- Selected Lesson Info -->
        <div class="rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-50 to-teal-50 p-5">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-emerald-500 rounded-xl flex items-center justify-center text-white flex-shrink-0">
              <span class="text-xl font-bold">{{ selectedLesson.lesson_number }}</span>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-emerald-900">{{ selectedLesson.subject }}</h3>
              <p class="text-sm text-emerald-700 mt-0.5">
                {{ selectedLesson.timeDisplay }}
                <span v-if="selectedLesson.teacher_name"> · {{ selectedLesson.teacher_name }}</span>
                <span v-if="selectedLesson.room"> · {{ selectedLesson.room }}</span>
              </p>
            </div>
            <div v-if="isLessonEnded" class="flex items-center gap-2 text-amber-700 bg-amber-100 px-3 py-1.5 rounded-lg">
              <Lock class="w-4 h-4" />
              <span class="text-xs font-medium">Tugagan</span>
            </div>
          </div>
        </div>

        <!-- Rules Info Banner -->
        <div class="rounded-2xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-5">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
              <AlertCircle class="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 class="font-semibold text-blue-900 mb-1">{{ $t('attendance.rules') }}</h3>
              <ul class="text-sm text-blue-700 space-y-1">
                <li class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
                  {{ $t('attendance.rule1') }}
                </li>
                <li class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
                  {{ $t('attendance.rule2') }}
                </li>
                <li class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 bg-amber-400 rounded-full"></span>
                  {{ $t('attendance.rule3') }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Lesson Ended Warning -->
        <div v-if="isLessonEnded" class="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-5">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
              <Clock class="w-6 h-6 text-amber-600" />
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-amber-900">{{ $t('attendance.lessonEnded') }}</h3>
              <p class="text-sm text-amber-700">{{ $t('attendance.lessonEndedDesc') }}</p>
            </div>
            <div class="flex items-center gap-2 text-amber-700">
              <Lock class="w-5 h-5" />
              <span class="text-sm font-medium">{{ $t('attendance.editRestricted') }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div class="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-3 sm:p-5 border border-emerald-200/50">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xl sm:text-3xl font-bold text-emerald-600">{{ presentCount }}</p>
                <p class="text-xs sm:text-sm text-emerald-700 font-medium">{{ $t('attendance.present') }}</p>
              </div>
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                <CheckCircle class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-2xl p-3 sm:p-5 border border-amber-200/50">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xl sm:text-3xl font-bold text-amber-600">{{ lateCount }}</p>
                <p class="text-xs sm:text-sm text-amber-700 font-medium">{{ $t('attendance.late') }}</p>
              </div>
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
                <Clock class="w-5 h-5 sm:w-6 sm:h-6 text-amber-600" />
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-rose-50 to-rose-100/50 rounded-2xl p-3 sm:p-5 border border-rose-200/50">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xl sm:text-3xl font-bold text-rose-600">{{ absentCount }}</p>
                <p class="text-xs sm:text-sm text-rose-700 font-medium">{{ $t('attendance.absent') }}</p>
              </div>
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-rose-500/20 rounded-xl flex items-center justify-center">
                <XCircle class="w-5 h-5 sm:w-6 sm:h-6 text-rose-600" />
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-3 sm:p-5 border border-blue-200/50">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xl sm:text-3xl font-bold text-blue-600">{{ excusedCount }}</p>
                <p class="text-xs sm:text-sm text-blue-700 font-medium">{{ $t('attendance.excused') }}</p>
              </div>
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                <FileText class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
              </div>
            </div>
          </div>
        </div>

        <!-- Bulk Actions -->
        <div class="bg-white rounded-2xl border border-slate-200 p-4">
          <div class="flex flex-wrap items-center gap-3">
            <span class="text-sm font-medium text-slate-600">{{ $t('attendance.quickActions') }}</span>
            <button
              @click="markAllAs('present')"
              :disabled="isLessonEnded"
              :class="[
                'px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2',
                isLessonEnded ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-emerald-100 hover:bg-emerald-200 text-emerald-700'
              ]"
            >
              <CheckCircle class="w-4 h-4" />
              {{ $t('attendance.markAllPresent') }}
            </button>
            <button
              @click="markAllAs('absent')"
              :disabled="isLessonEnded"
              :class="[
                'px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2',
                isLessonEnded ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-rose-100 hover:bg-rose-200 text-rose-700'
              ]"
            >
              <XCircle class="w-4 h-4" />
              {{ $t('attendance.markAllAbsent') }}
            </button>
            <button @click="resetAll" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-medium transition-colors flex items-center gap-2">
              <RotateCcw class="w-4 h-4" />
              {{ $t('attendance.clearAll') }}
            </button>
          </div>
        </div>

        <!-- Students List -->
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-lg font-semibold text-slate-800">{{ $t('attendance.studentList') }}</h2>
              <p class="text-sm text-slate-500">{{ $t('attendance.totalStudents', { count: groupStudents.length }) }}</p>
            </div>
            <button
              @click="saveAttendance"
              :disabled="saving"
              class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save v-if="!saving" class="w-5 h-5" />
              <Loader2 v-else class="w-5 h-5 animate-spin" />
              <span>{{ saving ? $t('attendance.saving') : (isLessonEnded ? $t('attendance.changeRequest') : $t('common.save')) }}</span>
            </button>
          </div>

          <div class="divide-y divide-slate-100">
            <div
              v-for="(student, index) in groupStudents"
              :key="student.id"
              class="p-4 lg:p-5 hover:bg-slate-50/50 transition-colors"
            >
              <div class="flex flex-col lg:flex-row lg:items-center gap-4">
                <!-- Student Info -->
                <div class="flex items-center gap-4 flex-1">
                  <span class="w-8 h-8 flex items-center justify-center text-sm font-bold text-slate-400 bg-slate-100 rounded-lg">{{ index + 1 }}</span>
                  <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                    <User class="w-5 h-5 text-slate-500" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-semibold text-slate-800">{{ student.name }}</p>
                    <p class="text-sm text-slate-500">{{ student.studentId }}</p>
                  </div>
                </div>

                <!-- Status Buttons -->
                <div class="flex items-center gap-2 flex-wrap">
                  <button
                    @click="handleStatusChange(student.id, 'present')"
                    :class="[
                      'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                      attendance[student.id]?.status === 'present'
                        ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30 scale-105'
                        : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 hover:scale-105'
                    ]"
                  >
                    <CheckCircle class="w-4 h-4" />
                    <span class="hidden sm:inline">{{ $t('attendance.present') }}</span>
                  </button>
                  <button
                    @click="handleStatusChange(student.id, 'absent')"
                    :class="[
                      'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                      attendance[student.id]?.status === 'absent'
                        ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30 scale-105'
                        : 'bg-rose-100 text-rose-700 hover:bg-rose-200 hover:scale-105'
                    ]"
                  >
                    <XCircle class="w-4 h-4" />
                    <span class="hidden sm:inline">{{ $t('attendance.absent') }}</span>
                  </button>
                  <button
                    @click="handleStatusChange(student.id, 'late')"
                    :class="[
                      'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                      attendance[student.id]?.status === 'late'
                        ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/30 scale-105'
                        : 'bg-amber-100 text-amber-700 hover:bg-amber-200 hover:scale-105'
                    ]"
                  >
                    <Clock class="w-4 h-4" />
                    <span class="hidden sm:inline">{{ $t('attendance.late') }}</span>
                  </button>
                  <button
                    @click="handleStatusChange(student.id, 'excused')"
                    :class="[
                      'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                      attendance[student.id]?.status === 'excused'
                        ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30 scale-105'
                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200 hover:scale-105'
                    ]"
                  >
                    <FileText class="w-4 h-4" />
                    <span class="hidden sm:inline">{{ $t('attendance.excused') }}</span>
                  </button>
                </div>
              </div>

              <!-- Absent/Excused reason -->
              <Transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 -translate-y-2"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 -translate-y-2"
              >
                <div v-if="attendance[student.id]?.status === 'absent' || attendance[student.id]?.status === 'excused'" class="mt-4 ml-12 lg:ml-20">
                  <div class="flex items-center gap-3 p-4 bg-rose-50 rounded-xl border border-rose-200">
                    <MessageSquare class="w-5 h-5 text-rose-500 flex-shrink-0" />
                    <div class="flex-1">
                      <label class="block text-sm font-medium text-rose-700 mb-1.5">{{ $t('attendance.reason') }}</label>
                      <input
                        v-model="attendance[student.id].reason"
                        type="text"
                        placeholder="Masalan: Kasallik, oilaviy sabab..."
                        class="w-full px-4 py-2.5 rounded-lg border border-rose-200 bg-white focus:border-rose-400 focus:ring-2 focus:ring-rose-400/20 outline-none text-sm transition-all"
                      />
                    </div>
                  </div>
                </div>
              </Transition>

              <!-- Late reason -->
              <Transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 -translate-y-2"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 -translate-y-2"
              >
                <div v-if="attendance[student.id]?.status === 'late'" class="mt-4 ml-12 lg:ml-20">
                  <div class="flex items-center gap-3 p-4 bg-amber-50 rounded-xl border border-amber-200">
                    <Timer class="w-5 h-5 text-amber-500 flex-shrink-0" />
                    <div class="flex-1 flex flex-col sm:flex-row sm:items-center gap-3">
                      <div class="flex-1">
                        <label class="block text-sm font-medium text-amber-700 mb-1.5">{{ $t('attendance.late') }}?</label>
                        <div class="flex items-center gap-2">
                          <input
                            v-model.number="attendance[student.id].lateMinutes"
                            type="number" min="1" max="90" placeholder="0"
                            class="w-24 px-4 py-2.5 rounded-lg border border-amber-200 bg-white focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm text-center transition-all"
                          />
                          <span class="text-sm text-amber-600 font-medium">daqiqa</span>
                        </div>
                      </div>
                      <div class="flex-1">
                        <label class="block text-sm font-medium text-amber-700 mb-1.5">{{ $t('attendance.reason') }}</label>
                        <input
                          v-model="attendance[student.id].reason"
                          type="text"
                          placeholder="Masalan: Transport muammosi..."
                          class="w-full px-4 py-2.5 rounded-lg border border-amber-200 bg-white focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm transition-all"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- Summary Modal -->
    <Teleport to="body">
      <div v-if="showSummary" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="showSummary = false">
        <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden">
          <div class="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 text-white text-center">
            <div class="w-16 h-16 bg-white/20 rounded-2xl mx-auto flex items-center justify-center mb-4">
              <CheckCircle class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold">Davomat saqlandi!</h3>
            <p class="text-emerald-100 mt-1">{{ selectedLesson?.subject }} — {{ selectedLesson?.timeDisplay }}</p>
          </div>
          <div class="p-6 space-y-4">
            <div class="flex items-center justify-between p-3 bg-emerald-50 rounded-xl">
              <span class="text-emerald-700 font-medium">Kelgan</span>
              <span class="text-2xl font-bold text-emerald-600">{{ presentCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-amber-50 rounded-xl">
              <span class="text-amber-700 font-medium">Kechikkan</span>
              <span class="text-2xl font-bold text-amber-600">{{ lateCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-rose-50 rounded-xl">
              <span class="text-rose-700 font-medium">Kelmagan</span>
              <span class="text-2xl font-bold text-rose-600">{{ absentCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-blue-50 rounded-xl">
              <span class="text-blue-700 font-medium">Sababli</span>
              <span class="text-2xl font-bold text-blue-600">{{ excusedCount }}</span>
            </div>
          </div>
          <div class="px-6 pb-6">
            <button @click="showSummary = false" class="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">Yopish</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Change Reason Modal (for post-lesson edits) -->
    <Teleport to="body">
      <div v-if="showReasonModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="cancelReasonModal">
        <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden">
          <div class="bg-gradient-to-r from-amber-500 to-orange-500 p-6 text-white">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
                <AlertCircle class="w-7 h-7" />
              </div>
              <div>
                <h3 class="text-xl font-bold">O'zgartirish sababi</h3>
                <p class="text-amber-100 text-sm mt-1">Dars tugagan, sabab kiritish talab etiladi</p>
              </div>
            </div>
          </div>
          <div class="p-6">
            <div class="mb-4 p-4 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-3">
                <User class="w-5 h-5 text-slate-500" />
                <span class="font-medium text-slate-800">{{ pendingReasonStudent?.name }}</span>
              </div>
              <div class="mt-2 flex items-center gap-2 text-sm text-slate-600">
                <span>{{ getStatusLabel(pendingReasonData?.oldStatus) }}</span>
                <ArrowRight class="w-4 h-4" />
                <span class="font-medium text-slate-800">{{ getStatusLabel(pendingReasonData?.newStatus) }}</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">O'zgartirish sababi *</label>
              <textarea
                v-model="changeReason"
                rows="3"
                placeholder="Nima uchun davomat o'zgartirilmoqda?"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm transition-all resize-none"
              ></textarea>
            </div>
          </div>
          <div class="px-6 pb-6 flex gap-3">
            <button @click="cancelReasonModal" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">
              Bekor qilish
            </button>
            <button
              @click="confirmChange"
              :disabled="!changeReason.trim()"
              class="flex-1 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Yuborish
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * AttendanceView.vue - Davomat olish sahifasi (Leader)
 * Real API Integration with Schedule-based subjects
 *
 * Flow:
 * 1. Load group info from /dashboard/leader
 * 2. Load students and week schedule in parallel
 * 3. Show today's lessons from real schedule data
 * 4. Leader selects a lesson → attendance form appears
 * 5. Save attendance with subject + lesson_number
 */

import {
  AlertCircle,
  ArrowRight,
  BookOpen,
  CheckCircle,
  Clock,
  Coffee,
  FileText,
  Loader2,
  Lock,
  MapPin,
  MessageSquare,
  RotateCcw,
  Save,
  Timer,
  User,
  XCircle
} from 'lucide-vue-next'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'

const authStore = useAuthStore()
const toast = useToastStore()

// ============ STATE ============
const loading = ref(true)
const saving = ref(false)
const showSummary = ref(false)
const showReasonModal = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedLesson = ref(null)
const changeReason = ref('')
const pendingReasonStudent = ref(null)
const pendingReasonData = ref(null)
const groupStudentsList = ref([])
const weekSchedule = ref({})
const groupId = ref(null)
const lessonAttendanceSaved = reactive({})

const attendance = reactive({})
const originalAttendance = ref({})

// ============ DAY MAPPING ============
const dayMapEngToUz = {
  monday: 'Dushanba', tuesday: 'Seshanba', wednesday: 'Chorshanba',
  thursday: 'Payshanba', friday: 'Juma', saturday: 'Shanba', sunday: 'Yakshanba'
}
const dayMapJsToEng = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

// ============ COMPUTED ============
const groupStudents = computed(() => groupStudentsList.value)

const selectedDayEng = computed(() => {
  const d = new Date(selectedDate.value + 'T12:00:00')
  return dayMapJsToEng[d.getDay()]
})

const selectedDayName = computed(() => dayMapEngToUz[selectedDayEng.value] || selectedDayEng.value)

const todayLessons = computed(() => {
  const dayKey = selectedDayEng.value
  const lessons = weekSchedule.value[dayKey] || []
  return lessons
    .map(s => ({
      ...s,
      timeDisplay: s.time_range
        ? s.time_range.replace(/\s/g, '').replace(/(\d{2}:\d{2}):\d{2}/g, '$1')
        : (s.start_time && s.end_time
          ? `${s.start_time.substring(0, 5)}-${s.end_time.substring(0, 5)}`
          : '')
    }))
    .sort((a, b) => (a.lesson_number || 0) - (b.lesson_number || 0))
})

const isLessonEnded = computed(() => {
  if (!selectedLesson.value) return false
  const today = new Date().toISOString().split('T')[0]
  if (selectedDate.value < today) return true
  if (selectedDate.value === today && selectedLesson.value.end_time) {
    const now = new Date()
    const parts = selectedLesson.value.end_time.split(':').map(Number)
    return now.getHours() > parts[0] || (now.getHours() === parts[0] && now.getMinutes() >= parts[1])
  }
  return false
})

const recentDates = computed(() => {
  const dates = []
  for (let i = 0; i < 14; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(d.toISOString().split('T')[0])
  }
  return dates
})

const presentCount = computed(() => Object.values(attendance).filter(a => a?.status === 'present').length)
const lateCount = computed(() => Object.values(attendance).filter(a => a?.status === 'late').length)
const absentCount = computed(() => Object.values(attendance).filter(a => a?.status === 'absent').length)
const excusedCount = computed(() => Object.values(attendance).filter(a => a?.status === 'excused').length)

// ============ LOAD DATA ============
async function loadGroupData() {
  loading.value = true
  try {
    const dashboardResp = await api.request('/dashboard/leader')
    groupId.value = dashboardResp?.group?.id

    if (!groupId.value) {
      toast.error('Guruh topilmadi')
      loading.value = false
      return
    }

    // Load students + week schedule in parallel
    const [studentsResp, scheduleResp] = await Promise.all([
      api.getStudents({ group_id: groupId.value, page_size: 100 }),
      api.getScheduleByGroup(groupId.value)
    ])

    // Students
    const items = studentsResp.items || studentsResp.data || []
    groupStudentsList.value = items.map(s => ({
      id: s.id,
      name: s.name || s.full_name || 'Ism kiritilmagan',
      studentId: s.student_id || '',
      groupId: s.group_id,
      phone: s.phone
    }))

    // Week schedule (comes as { monday: [...], tuesday: [...], ... })
    if (scheduleResp && typeof scheduleResp === 'object') {
      weekSchedule.value = scheduleResp
    }

    initializeAttendance()
    await loadAttendanceForDate()
  } catch (e) {
    console.error('Load group data error:', e)
    toast.error("Ma'lumotlar yuklanmadi")
  } finally {
    loading.value = false
  }
}

async function loadAttendanceForDate() {
  if (!groupId.value) return

  try {
    const response = await api.getAttendance({
      group_id: groupId.value,
      date_from: selectedDate.value,
      date_to: selectedDate.value
    })

    const records = response.items || response.data || []

    // Mark which lessons already have attendance saved
    const savedLessonNums = new Set()
    records.forEach(r => {
      if (r.lesson_number) savedLessonNums.add(r.lesson_number)
    })
    todayLessons.value.forEach(lesson => {
      lessonAttendanceSaved[lesson.id] = savedLessonNums.has(lesson.lesson_number)
    })

    // If a lesson is selected, populate its attendance data
    if (selectedLesson.value) {
      const lessonRecords = records.filter(r =>
        r.lesson_number === selectedLesson.value.lesson_number
      )

      if (lessonRecords.length > 0) {
        groupStudents.value.forEach(student => {
          const existing = lessonRecords.find(r => r.student_id === student.id)
          if (existing) {
            const data = {
              status: existing.status,
              reason: existing.note || existing.reason || '',
              lateMinutes: existing.late_minutes || 0
            }
            attendance[student.id] = { ...data }
            originalAttendance.value[student.id] = { ...data }
          }
        })
      }
    }
  } catch (e) {
    console.error('Load attendance error:', e)
  }
}

const initializeAttendance = () => {
  groupStudents.value.forEach(student => {
    const data = { status: 'present', reason: '', lateMinutes: 0 }
    attendance[student.id] = { ...data }
    originalAttendance.value[student.id] = { ...data }
  })
}

function selectLesson(lesson) {
  selectedLesson.value = lesson
  initializeAttendance()
  loadAttendanceForDate()
}

watch(selectedDate, async () => {
  selectedLesson.value = null
  Object.keys(lessonAttendanceSaved).forEach(k => delete lessonAttendanceSaved[k])
  initializeAttendance()
  await loadAttendanceForDate()
})

onMounted(() => {
  loadGroupData()
})

// ============ STATUS CHANGE ============
const handleStatusChange = (studentId, newStatus) => {
  if (isLessonEnded.value) {
    const student = groupStudents.value.find(s => s.id === studentId)
    const oldStatus = attendance[studentId]?.status
    if (oldStatus !== newStatus) {
      pendingReasonStudent.value = student
      pendingReasonData.value = { studentId, oldStatus, newStatus }
      changeReason.value = ''
      showReasonModal.value = true
    }
  } else {
    setStatus(studentId, newStatus)
  }
}

const setStatus = (studentId, status) => {
  attendance[studentId] = {
    ...attendance[studentId],
    status,
    reason: status === 'present' ? '' : attendance[studentId]?.reason || '',
    lateMinutes: status === 'late' ? (attendance[studentId]?.lateMinutes || 5) : 0
  }
}

const confirmChange = () => {
  if (!changeReason.value.trim()) {
    toast.error('Sabab kiritilmagan')
    return
  }
  setStatus(pendingReasonData.value.studentId, pendingReasonData.value.newStatus)
  toast.info("So'rov yuborildi")
  showReasonModal.value = false
  changeReason.value = ''
  pendingReasonStudent.value = null
  pendingReasonData.value = null
}

const cancelReasonModal = () => {
  showReasonModal.value = false
  changeReason.value = ''
  pendingReasonStudent.value = null
  pendingReasonData.value = null
}

const markAllAs = (status) => {
  if (isLessonEnded.value) {
    toast.warning("Dars tugagandan keyin ommaviy o'zgartirish mumkin emas")
    return
  }
  groupStudents.value.forEach(student => setStatus(student.id, status))
  toast.info(`Barcha talabalar "${status === 'present' ? 'Keldi' : 'Kelmadi'}" deb belgilandi`)
}

const resetAll = () => {
  initializeAttendance()
  toast.info("Barcha belgilar boshlang'ich holatga qaytarildi")
}

// ============ HELPERS ============
const formatDate = (dateStr) => {
  return new Date(dateStr + 'T12:00:00').toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    weekday: 'long'
  })
}

const getStatusLabel = (status) => {
  const labels = { present: 'Keldi', absent: 'Kelmadi', late: 'Kech qoldi', excused: 'Sababli' }
  return labels[status] || status
}

// ============ SAVE ============
const saveAttendance = async () => {
  if (!selectedLesson.value) {
    toast.warning('Avval darsni tanlang')
    return
  }

  saving.value = true

  try {
    const records = groupStudents.value.map(student => {
      const record = attendance[student.id]
      return {
        student_id: student.id,
        status: record.status,
        note: record.reason || null,
        late_minutes: record.status === 'late' ? record.lateMinutes : 0
      }
    })

    try {
      await api.bulkCreateAttendance({
        date: selectedDate.value,
        subject: selectedLesson.value.subject,
        lesson_number: selectedLesson.value.lesson_number,
        attendances: records
      })
    } catch (e) {
      // Fallback: save one by one
      for (const record of records) {
        await api.createAttendance({
          student_id: record.student_id,
          date: selectedDate.value,
          subject: selectedLesson.value.subject,
          lesson_number: selectedLesson.value.lesson_number,
          status: record.status,
          note: record.note,
          late_minutes: record.late_minutes
        })
      }
    }

    lessonAttendanceSaved[selectedLesson.value.id] = true
    toast.success(`"${selectedLesson.value.subject}" — davomat saqlandi`)
    showSummary.value = true
  } catch (error) {
    console.error('Save attendance error:', error)
    toast.error('Davomatni saqlashda xatolik yuz berdi')
  } finally {
    saving.value = false
  }
}
</script>

