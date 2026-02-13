<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 via-emerald-600 to-teal-700 p-6 text-white">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-white/10"></div>
      <div class="relative">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold flex items-center gap-3">
              <Calculator class="w-8 h-8" />
              {{ $t('credit.title') }}
            </h1>
            <p class="mt-2 text-emerald-200 text-sm sm:text-base">{{ $t('credit.subtitle') }}</p>
          </div>
          <div class="flex items-center gap-3">
            <button
              @click="showInfo = !showInfo"
              class="flex items-center gap-2 px-4 py-2.5 bg-white/20 hover:bg-white/30 rounded-xl text-sm font-medium transition-all backdrop-blur"
            >
              <Info class="w-4 h-4" />
              {{ $t('credit.aboutSystem') }}
            </button>
          </div>
        </div>
        <!-- Quick Stats -->
        <div class="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="bg-white/15 backdrop-blur rounded-xl p-3 text-center">
            <p class="text-2xl font-bold">{{ totalCredits }}</p>
            <p class="text-xs text-emerald-200">{{ $t('credit.totalCredits') }}</p>
          </div>
          <div class="bg-white/15 backdrop-blur rounded-xl p-3 text-center">
            <p class="text-2xl font-bold">{{ gpa.toFixed(2) }}</p>
            <p class="text-xs text-emerald-200">{{ $t('credit.gpa') }}</p>
          </div>
          <div class="bg-white/15 backdrop-blur rounded-xl p-3 text-center">
            <p class="text-2xl font-bold">{{ totalHours }}</p>
            <p class="text-xs text-emerald-200">{{ $t('credit.totalHours') }}</p>
          </div>
          <div class="bg-white/15 backdrop-blur rounded-xl p-3 text-center">
            <p class="text-2xl font-bold" :class="gpaLetterColor">{{ gpaLetter }}</p>
            <p class="text-xs text-emerald-200">{{ $t('credit.gradeLevel') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Panel (collapsible) -->
    <Transition name="slide">
      <div v-if="showInfo" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 sm:p-6">
        <h3 class="text-lg font-bold text-emerald-800 mb-4 flex items-center gap-2">
          <GraduationCap class="w-5 h-5" />
          {{ $t('credit.aboutCreditSystem') }}
        </h3>
        <div class="grid sm:grid-cols-2 gap-6 text-sm text-emerald-700">
          <div class="space-y-3">
            <div class="flex items-start gap-2">
              <div class="mt-1 w-2 h-2 rounded-full bg-emerald-400 shrink-0"></div>
              <p>{{ $t('credit.info1') }}</p>
            </div>
            <div class="flex items-start gap-2">
              <div class="mt-1 w-2 h-2 rounded-full bg-emerald-400 shrink-0"></div>
              <p>{{ $t('credit.info2') }}</p>
            </div>
            <div class="flex items-start gap-2">
              <div class="mt-1 w-2 h-2 rounded-full bg-emerald-400 shrink-0"></div>
              <p>{{ $t('credit.info3') }}</p>
            </div>
            <div class="flex items-start gap-2">
              <div class="mt-1 w-2 h-2 rounded-full bg-emerald-400 shrink-0"></div>
              <p>{{ $t('credit.info4') }}</p>
            </div>
          </div>
          <div>
            <h4 class="font-semibold text-emerald-800 mb-2">{{ $t('credit.gradingScale') }}</h4>
            <div class="rounded-xl overflow-hidden border border-emerald-200">
              <table class="w-full text-sm">
                <thead class="bg-emerald-100">
                  <tr>
                    <th class="px-3 py-2 text-left font-semibold">{{ $t('credit.grade') }}</th>
                    <th class="px-3 py-2 text-left font-semibold">{{ $t('credit.ball') }}</th>
                    <th class="px-3 py-2 text-left font-semibold">{{ $t('credit.percentage') }}</th>
                    <th class="px-3 py-2 text-left font-semibold">{{ $t('credit.letter') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-t border-emerald-100">
                    <td class="px-3 py-2 font-medium text-emerald-700">{{ $t('credit.excellent') }}</td>
                    <td class="px-3 py-2">5.0</td>
                    <td class="px-3 py-2">86-100%</td>
                    <td class="px-3 py-2 font-bold text-emerald-600">A</td>
                  </tr>
                  <tr class="border-t border-emerald-100 bg-emerald-50/50">
                    <td class="px-3 py-2 font-medium text-blue-700">{{ $t('credit.good') }}</td>
                    <td class="px-3 py-2">4.0</td>
                    <td class="px-3 py-2">71-85%</td>
                    <td class="px-3 py-2 font-bold text-blue-600">B</td>
                  </tr>
                  <tr class="border-t border-emerald-100">
                    <td class="px-3 py-2 font-medium text-amber-700">{{ $t('credit.satisfactory') }}</td>
                    <td class="px-3 py-2">3.0</td>
                    <td class="px-3 py-2">56-70%</td>
                    <td class="px-3 py-2 font-bold text-amber-600">C</td>
                  </tr>
                  <tr class="border-t border-emerald-100 bg-emerald-50/50">
                    <td class="px-3 py-2 font-medium text-red-700">{{ $t('credit.unsatisfactory') }}</td>
                    <td class="px-3 py-2">2.0</td>
                    <td class="px-3 py-2">0-55%</td>
                    <td class="px-3 py-2 font-bold text-red-600">F</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Education Level Selector -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="level in educationLevels"
        :key="level.key"
        @click="selectedLevel = level.key"
        :class="[
          'px-4 py-2 rounded-xl text-sm font-medium transition-all',
          selectedLevel === level.key
            ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/25'
            : 'bg-white border border-slate-200 text-slate-600 hover:bg-emerald-50 hover:border-emerald-300'
        ]"
      >
        {{ level.label }}
      </button>
    </div>

    <!-- Semester Tabs -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="border-b border-slate-200 px-4 py-3 flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            v-for="sem in totalSemesters"
            :key="sem"
            @click="activeSemester = sem"
            :class="[
              'px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap',
              activeSemester === sem
                ? 'bg-emerald-100 text-emerald-700 ring-1 ring-emerald-300'
                : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'
            ]"
          >
            {{ sem }}-{{ $t('credit.semester') }}
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">
            {{ $t('credit.semesterCredits') }}: 
            <span class="font-bold text-emerald-600">{{ semesterCredits }} / 30</span>
          </span>
        </div>
      </div>

      <!-- Subject Table -->
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider w-8">#</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider min-w-[200px]">{{ $t('credit.subjectName') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-24">{{ $t('credit.credits') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-24">{{ $t('credit.hours') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-32">{{ $t('credit.gradeInput') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-24">{{ $t('credit.letter') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-24">{{ $t('credit.points') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-16"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(subject, idx) in currentSemesterSubjects"
              :key="subject.id"
              class="border-t border-slate-100 hover:bg-slate-50/50 transition-colors"
            >
              <td class="px-4 py-3 text-sm text-slate-400 font-medium">{{ idx + 1 }}</td>
              <td class="px-4 py-3">
                <input
                  v-model="subject.name"
                  type="text"
                  :placeholder="$t('credit.enterSubjectName')"
                  class="w-full bg-transparent border-0 border-b border-transparent hover:border-slate-300 focus:border-emerald-500 focus:ring-0 text-sm font-medium text-slate-800 placeholder-slate-300 py-1 px-0 transition-colors"
                />
              </td>
              <td class="px-4 py-3 text-center">
                <input
                  v-model.number="subject.credits"
                  type="number"
                  min="1"
                  max="30"
                  class="w-16 text-center bg-emerald-50 border border-emerald-200 rounded-lg text-sm font-bold text-emerald-700 py-1 focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                />
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-sm font-medium text-slate-600">{{ subject.credits * 30 }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <select
                  v-model.number="subject.grade"
                  class="bg-white border border-slate-200 rounded-lg text-sm font-medium py-1.5 px-2 focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 cursor-pointer"
                  :class="getGradeSelectClass(subject.grade)"
                >
                  <option :value="0" disabled>{{ $t('credit.selectGrade') }}</option>
                  <option :value="5">5 - {{ $t('credit.excellent') }} (A)</option>
                  <option :value="4">4 - {{ $t('credit.good') }} (B)</option>
                  <option :value="3">3 - {{ $t('credit.satisfactory') }} (C)</option>
                  <option :value="2">2 - {{ $t('credit.unsatisfactory') }} (F)</option>
                </select>
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  v-if="subject.grade > 0"
                  :class="[
                    'inline-flex items-center justify-center w-8 h-8 rounded-lg text-sm font-bold',
                    getGradeBadgeClass(subject.grade)
                  ]"
                >
                  {{ getLetterGrade(subject.grade) }}
                </span>
                <span v-else class="text-slate-300">—</span>
              </td>
              <td class="px-4 py-3 text-center">
                <span v-if="subject.grade > 0" class="text-sm font-bold" :class="getGradeTextClass(subject.grade)">
                  {{ (subject.grade * subject.credits).toFixed(1) }}
                </span>
                <span v-else class="text-slate-300">—</span>
              </td>
              <td class="px-4 py-3 text-center">
                <button
                  @click="removeSubject(subject.id)"
                  class="p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  :title="$t('common.delete')"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
            <tr v-if="currentSemesterSubjects.length === 0" class="border-t border-slate-100">
              <td colspan="8" class="px-4 py-8 text-center text-slate-400">
                <BookOpen class="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>{{ $t('credit.noSubjects') }}</p>
              </td>
            </tr>
          </tbody>
          <!-- Footer -->
          <tfoot class="bg-slate-50 border-t-2 border-slate-200">
            <tr>
              <td colspan="2" class="px-4 py-3">
                <button
                  @click="addSubject"
                  class="flex items-center gap-2 text-sm font-medium text-emerald-600 hover:text-emerald-800 transition-colors"
                >
                  <Plus class="w-4 h-4" />
                  {{ $t('credit.addSubject') }}
                </button>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-sm font-bold text-emerald-700">{{ semesterCredits }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-sm font-bold text-slate-600">{{ semesterCredits * 30 }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-xs text-slate-400">{{ $t('credit.semesterGPA') }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-sm font-bold" :class="getGradeTextClass(Math.round(semesterGPA))">
                  {{ semesterGPA > 0 ? getLetterGrade(Math.round(semesterGPA)) : '—' }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-sm font-bold text-emerald-700">{{ semesterGPA > 0 ? semesterGPA.toFixed(2) : '—' }}</span>
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Results Summary -->
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- GPA Card -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider">{{ $t('credit.overallGPA') }}</h3>
          <div class="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
            <Award class="w-5 h-5 text-emerald-600" />
          </div>
        </div>
        <div class="flex items-end gap-3">
          <span class="text-4xl font-bold" :class="getGpaColor(gpa)">{{ gpa.toFixed(2) }}</span>
          <span class="text-sm text-slate-400 mb-1">/ 5.00</span>
        </div>
        <!-- GPA Progress Bar -->
        <div class="mt-4 h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700 ease-out"
            :class="getGpaBarColor(gpa)"
            :style="{ width: `${(gpa / 5) * 100}%` }"
          ></div>
        </div>
        <div class="mt-3 flex items-center justify-between text-xs text-slate-400">
          <span>0.00</span>
          <span class="font-semibold" :class="getGpaColor(gpa)">{{ gpaLetter }} — {{ gpaDescription }}</span>
          <span>5.00</span>
        </div>
      </div>

      <!-- Credits Progress -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider">{{ $t('credit.creditsProgress') }}</h3>
          <div class="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center">
            <Target class="w-5 h-5 text-teal-600" />
          </div>
        </div>
        <div class="flex items-end gap-3">
          <span class="text-4xl font-bold text-teal-600">{{ totalCredits }}</span>
          <span class="text-sm text-slate-400 mb-1">/ {{ requiredCredits }}</span>
        </div>
        <div class="mt-4 h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-teal-500 to-teal-600 rounded-full transition-all duration-700 ease-out"
            :style="{ width: `${Math.min((totalCredits / requiredCredits) * 100, 100)}%` }"
          ></div>
        </div>
        <div class="mt-3 flex items-center justify-between text-xs text-slate-400">
          <span>{{ $t('credit.collected') }}: {{ totalCredits }}</span>
          <span>{{ $t('credit.remaining') }}: {{ Math.max(requiredCredits - totalCredits, 0) }}</span>
        </div>
      </div>

      <!-- Semester Summary -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:col-span-2 lg:col-span-1">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider">{{ $t('credit.semesterSummary') }}</h3>
          <div class="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
            <BarChart3 class="w-5 h-5 text-emerald-600" />
          </div>
        </div>
        <div class="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
          <div
            v-for="sem in totalSemesters"
            :key="sem"
            class="flex items-center justify-between py-1.5 px-2 rounded-lg"
            :class="activeSemester === sem ? 'bg-emerald-50' : 'hover:bg-slate-50'"
          >
            <span class="text-sm" :class="activeSemester === sem ? 'font-semibold text-emerald-700' : 'text-slate-600'">
              {{ sem }}-{{ $t('credit.semester') }}
            </span>
            <div class="flex items-center gap-3">
              <span class="text-xs text-slate-400">
                {{ getSemesterCredits(sem) }} {{ $t('credit.cr') }}
              </span>
              <span
                class="text-sm font-bold"
                :class="getGpaColor(getSemesterGPA(sem))"
              >
                {{ getSemesterGPA(sem) > 0 ? getSemesterGPA(sem).toFixed(2) : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap items-center gap-3">
      <button
        @click="resetAll"
        class="flex items-center gap-2 px-4 py-2.5 bg-red-50 text-red-600 hover:bg-red-100 rounded-xl text-sm font-medium transition-colors"
      >
        <RotateCcw class="w-4 h-4" />
        {{ $t('credit.resetAll') }}
      </button>
      <button
        @click="loadSampleData"
        class="flex items-center gap-2 px-4 py-2.5 bg-teal-50 text-teal-600 hover:bg-teal-100 rounded-xl text-sm font-medium transition-colors"
      >
        <Sparkles class="w-4 h-4" />
        {{ $t('credit.loadSample') }}
      </button>
      <button
        @click="saveToLocalStorage"
        class="flex items-center gap-2 px-4 py-2.5 bg-emerald-50 text-emerald-600 hover:bg-emerald-100 rounded-xl text-sm font-medium transition-colors"
      >
        <Save class="w-4 h-4" />
        {{ $t('credit.save') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import {
  Award,
  BarChart3,
  BookOpen,
  Calculator,
  GraduationCap,
  Info,
  Plus,
  RotateCcw,
  Save,
  Sparkles,
  Target,
  Trash2
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useLanguageStore } from '../../stores/language'

const langStore = useLanguageStore()
const { t } = langStore

// ============ STATE ============

const showInfo = ref(false)
const selectedLevel = ref('bachelor')
const activeSemester = ref(1)

// All subjects data: { [semesterNum]: Subject[] }
const subjects = ref({})

// ============ COMPUTED ============

const educationLevels = computed(() => [
  { key: 'bachelor', label: t('credit.bachelor') + ' (4 ' + t('credit.years') + ' / 240 ' + t('credit.cr') + ')' },
  { key: 'master', label: t('credit.master') + ' (2 ' + t('credit.years') + ' / 120 ' + t('credit.cr') + ')' }
])

const totalSemesters = computed(() => {
  return selectedLevel.value === 'bachelor' ? 8 : 4
})

const requiredCredits = computed(() => {
  return selectedLevel.value === 'bachelor' ? 240 : 120
})

const currentSemesterSubjects = computed(() => {
  return subjects.value[activeSemester.value] || []
})

const semesterCredits = computed(() => {
  const subs = subjects.value[activeSemester.value] || []
  return subs.reduce((sum, s) => sum + (s.credits || 0), 0)
})

const semesterGPA = computed(() => {
  return getSemesterGPA(activeSemester.value)
})

const totalCredits = computed(() => {
  let total = 0
  for (const sem in subjects.value) {
    for (const s of subjects.value[sem]) {
      if (s.grade > 0) total += s.credits || 0
    }
  }
  return total
})

const totalHours = computed(() => {
  return totalCredits.value * 30
})

const gpa = computed(() => {
  let totalPoints = 0
  let totalCreds = 0
  for (const sem in subjects.value) {
    for (const s of subjects.value[sem]) {
      if (s.grade > 0 && s.credits > 0) {
        totalPoints += s.grade * s.credits
        totalCreds += s.credits
      }
    }
  }
  return totalCreds > 0 ? totalPoints / totalCreds : 0
})

const gpaLetter = computed(() => {
  if (gpa.value >= 4.5) return 'A'
  if (gpa.value >= 3.5) return 'B'
  if (gpa.value >= 2.5) return 'C'
  if (gpa.value > 0) return 'F'
  return '—'
})

const gpaLetterColor = computed(() => {
  if (gpa.value >= 4.5) return 'text-yellow-300'
  if (gpa.value >= 3.5) return 'text-sky-200'
  if (gpa.value >= 2.5) return 'text-orange-300'
  if (gpa.value > 0) return 'text-red-300'
  return 'text-white/50'
})

const gpaDescription = computed(() => {
  if (gpa.value >= 4.5) return t('credit.excellent')
  if (gpa.value >= 3.5) return t('credit.good')
  if (gpa.value >= 2.5) return t('credit.satisfactory')
  if (gpa.value > 0) return t('credit.unsatisfactory')
  return t('credit.noData')
})

// ============ METHODS ============

function getSemesterCredits(sem) {
  const subs = subjects.value[sem] || []
  return subs.reduce((sum, s) => sum + (s.grade > 0 ? (s.credits || 0) : 0), 0)
}

function getSemesterGPA(sem) {
  const subs = subjects.value[sem] || []
  let totalPoints = 0
  let totalCreds = 0
  for (const s of subs) {
    if (s.grade > 0 && s.credits > 0) {
      totalPoints += s.grade * s.credits
      totalCreds += s.credits
    }
  }
  return totalCreds > 0 ? totalPoints / totalCreds : 0
}

function addSubject() {
  if (!subjects.value[activeSemester.value]) {
    subjects.value[activeSemester.value] = []
  }
  subjects.value[activeSemester.value].push({
    id: Date.now() + Math.random(),
    name: '',
    credits: 3,
    grade: 0
  })
}

function removeSubject(id) {
  const subs = subjects.value[activeSemester.value]
  if (subs) {
    const idx = subs.findIndex(s => s.id === id)
    if (idx !== -1) subs.splice(idx, 1)
  }
}

function getLetterGrade(grade) {
  if (grade >= 5) return 'A'
  if (grade >= 4) return 'B'
  if (grade >= 3) return 'C'
  return 'F'
}

function getGradeSelectClass(grade) {
  if (grade >= 5) return 'text-emerald-700 border-emerald-300 bg-emerald-50'
  if (grade >= 4) return 'text-blue-700 border-blue-300 bg-blue-50'
  if (grade >= 3) return 'text-amber-700 border-amber-300 bg-amber-50'
  if (grade >= 2) return 'text-red-700 border-red-300 bg-red-50'
  return ''
}

function getGradeBadgeClass(grade) {
  if (grade >= 5) return 'bg-emerald-100 text-emerald-700'
  if (grade >= 4) return 'bg-blue-100 text-blue-700'
  if (grade >= 3) return 'bg-amber-100 text-amber-700'
  return 'bg-red-100 text-red-700'
}

function getGradeTextClass(grade) {
  if (grade >= 5) return 'text-emerald-600'
  if (grade >= 4) return 'text-blue-600'
  if (grade >= 3) return 'text-amber-600'
  if (grade >= 2) return 'text-red-600'
  return 'text-slate-400'
}

function getGpaColor(val) {
  if (val >= 4.5) return 'text-emerald-600'
  if (val >= 3.5) return 'text-blue-600'
  if (val >= 2.5) return 'text-amber-600'
  if (val > 0) return 'text-red-600'
  return 'text-slate-400'
}

function getGpaBarColor(val) {
  if (val >= 4.5) return 'bg-gradient-to-r from-emerald-400 to-emerald-600'
  if (val >= 3.5) return 'bg-gradient-to-r from-blue-400 to-blue-600'
  if (val >= 2.5) return 'bg-gradient-to-r from-amber-400 to-amber-600'
  if (val > 0) return 'bg-gradient-to-r from-red-400 to-red-600'
  return 'bg-slate-200'
}

function resetAll() {
  subjects.value = {}
  localStorage.removeItem('credit_module_data')
}

function loadSampleData() {
  const sampleSubjects = {
    1: [
      { id: 1, name: t('credit.sampleMath'), credits: 5, grade: 4 },
      { id: 2, name: t('credit.samplePhysics'), credits: 4, grade: 5 },
      { id: 3, name: t('credit.sampleHistory'), credits: 3, grade: 4 },
      { id: 4, name: t('credit.sampleForeignLang'), credits: 4, grade: 5 },
      { id: 5, name: t('credit.sampleInformatics'), credits: 5, grade: 4 },
      { id: 6, name: t('credit.samplePhysEd'), credits: 2, grade: 5 },
      { id: 7, name: t('credit.samplePhilosophy'), credits: 3, grade: 3 },
      { id: 8, name: t('credit.sampleEcology'), credits: 2, grade: 4 },
      { id: 9, name: t('credit.sampleDrawing'), credits: 2, grade: 5 }
    ],
    2: [
      { id: 10, name: t('credit.sampleMath') + ' II', credits: 5, grade: 5 },
      { id: 11, name: t('credit.samplePhysics') + ' II', credits: 4, grade: 4 },
      { id: 12, name: t('credit.sampleProgramming'), credits: 5, grade: 5 },
      { id: 13, name: t('credit.sampleForeignLang') + ' II', credits: 4, grade: 4 },
      { id: 14, name: t('credit.sampleChemistry'), credits: 3, grade: 3 },
      { id: 15, name: t('credit.samplePhysEd') + ' II', credits: 2, grade: 5 },
      { id: 16, name: t('credit.sampleEconomics'), credits: 3, grade: 4 },
      { id: 17, name: t('credit.sampleLinearAlgebra'), credits: 4, grade: 4 }
    ]
  }
  subjects.value = sampleSubjects
  activeSemester.value = 1
}

function saveToLocalStorage() {
  try {
    const data = {
      selectedLevel: selectedLevel.value,
      subjects: subjects.value
    }
    localStorage.setItem('credit_module_data', JSON.stringify(data))
    alert(t('credit.dataSaved'))
  } catch {
    alert(t('credit.saveError'))
  }
}

function loadFromLocalStorage() {
  try {
    const raw = localStorage.getItem('credit_module_data')
    if (raw) {
      const data = JSON.parse(raw)
      if (data.selectedLevel) selectedLevel.value = data.selectedLevel
      if (data.subjects) subjects.value = data.subjects
    }
  } catch {
    // ignore
  }
}

// ============ WATCHERS ============

watch(selectedLevel, () => {
  if (activeSemester.value > totalSemesters.value) {
    activeSemester.value = 1
  }
})

// ============ LIFECYCLE ============

onMounted(() => {
  loadFromLocalStorage()
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}
</style>
