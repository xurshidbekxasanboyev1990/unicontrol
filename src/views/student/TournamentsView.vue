<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 rounded-3xl p-6 md:p-8 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
      <div class="relative">
        <div class="flex items-center gap-3 mb-2">
          <Trophy class="w-8 h-8" />
          <span class="text-sm font-medium opacity-90">{{ $t('tournaments.title') }}</span>
        </div>
        <h1 class="text-2xl md:text-3xl font-bold">{{ $t('tournaments.title') }}</h1>
        <p class="text-white/80 mt-2 max-w-xl">
          {{ $t('tournaments.noTournamentsDesc') }}
        </p>
      </div>
    </div>

    <!-- My Registrations -->
    <div v-if="myRegistrations.length > 0" class="bg-white rounded-2xl border border-slate-200 p-6">
      <h2 class="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
        <ClipboardCheck class="w-5 h-5 text-emerald-500" />
        {{ $t('tournaments.myTournaments') }}
      </h2>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="item in myRegistrations"
          :key="item.registration.id"
          class="p-4 bg-slate-50 rounded-xl border border-slate-100"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <h3 class="font-semibold text-slate-800 text-sm line-clamp-1">{{ item.tournament.title }}</h3>
            <span :class="[
              'px-2 py-0.5 text-xs font-medium rounded-full shrink-0',
              item.registration.status === 'pending' && 'bg-amber-100 text-amber-700',
              item.registration.status === 'approved' && 'bg-emerald-100 text-emerald-700',
              item.registration.status === 'rejected' && 'bg-rose-100 text-rose-700'
            ]">
              {{ getStatusLabel(item.registration.status) }}
            </span>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-500">
            <Calendar class="w-3.5 h-3.5" />
            {{ formatDate(item.tournament.startDate) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="selectedCategory = cat.value"
        :class="[
          'px-4 py-2 rounded-xl text-sm font-medium transition-all',
          selectedCategory === cat.value
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg'
            : 'bg-white border border-slate-200 text-slate-600 hover:border-emerald-300'
        ]"
      >
        <component :is="cat.icon" class="w-4 h-4 inline mr-2" />
        {{ cat.label }}
      </button>
    </div>

    <!-- Tournaments Grid -->
    <div class="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div
        v-for="tournament in filteredTournaments"
        :key="tournament.id"
        class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl hover:border-emerald-200 transition-all group"
      >
        <!-- Header -->
        <div :class="['p-5 text-white relative overflow-hidden', getCategoryGradient(tournament.category)]">
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div class="relative">
            <div class="flex items-center gap-2 mb-2">
              <component :is="getCategoryIcon(tournament.category)" class="w-5 h-5" />
              <span class="text-sm font-medium opacity-90">{{ getCategoryLabel(tournament.category) }}</span>
            </div>
            <h3 class="text-lg font-bold line-clamp-2">{{ tournament.title }}</h3>
          </div>
        </div>

        <!-- Body -->
        <div class="p-5 space-y-4">
          <p class="text-sm text-slate-600 line-clamp-3">{{ tournament.description }}</p>

          <div class="space-y-2.5">
            <div class="flex items-center gap-3 text-sm">
              <div class="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center">
                <Calendar class="w-4 h-4 text-slate-500" />
              </div>
              <div>
                <p class="text-slate-800 font-medium">{{ formatDate(tournament.startDate) }}</p>
                <p v-if="tournament.startDate !== tournament.endDate" class="text-xs text-slate-400">
                  → {{ formatDate(tournament.endDate) }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3 text-sm">
              <div class="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center">
                <MapPin class="w-4 h-4 text-slate-500" />
              </div>
              <p class="text-slate-600">{{ tournament.location }}</p>
            </div>

            <div class="flex items-center gap-3 text-sm">
              <div :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center',
                isDeadlinePassed(tournament.registrationDeadline) ? 'bg-rose-100' : 'bg-emerald-100'
              ]">
                <Clock :class="[
                  'w-4 h-4',
                  isDeadlinePassed(tournament.registrationDeadline) ? 'text-rose-500' : 'text-emerald-500'
                ]" />
              </div>
              <div>
                <p :class="isDeadlinePassed(tournament.registrationDeadline) ? 'text-rose-500' : 'text-emerald-600'" class="font-medium">
                  {{ isDeadlinePassed(tournament.registrationDeadline) ? $t('tournaments.registrationClosed') : $t('tournaments.registrationOpen') }}
                </p>
                <p class="text-xs text-slate-400">{{ formatDate(tournament.registrationDeadline) }}</p>
              </div>
            </div>

            <div v-if="tournament.prize" class="flex items-center gap-3 text-sm">
              <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
                <Gift class="w-4 h-4 text-amber-500" />
              </div>
              <p class="text-slate-600">{{ tournament.prize }}</p>
            </div>

            <!-- Subject-based tournament indicator (YANGI MODEL) -->
            <div v-if="hasParticipationRules(tournament)" class="flex items-center gap-3 text-sm">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <BookOpen class="w-4 h-4 text-blue-500" />
              </div>
              <div>
                <p class="text-blue-600 font-medium">{{ $t('tournaments.subjectCompetition') }}</p>
                <p class="text-xs text-slate-400">
                  {{ getParticipationRuleInfo(tournament) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Participants -->
          <div class="pt-4 border-t border-slate-100">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-slate-500">{{ $t('tournaments.participants') }}</span>
              <span class="text-sm font-semibold text-slate-700">
                {{ tournament.registrationsCount || 0 }} / {{ tournament.maxParticipants }}
              </span>
            </div>
            <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                :class="[
                  'h-full rounded-full transition-all',
                  (tournament.registrationsCount || 0) >= tournament.maxParticipants 
                    ? 'bg-rose-500' 
                    : 'bg-gradient-to-r from-emerald-500 to-teal-500'
                ]"
                :style="{ width: `${Math.min(((tournament.registrationsCount || 0) / tournament.maxParticipants) * 100, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-5 py-4 bg-slate-50 border-t border-slate-100">
          <button
            v-if="isRegistered(tournament.id)"
            disabled
            class="w-full py-3 bg-slate-200 text-slate-500 rounded-xl font-semibold flex items-center justify-center gap-2"
          >
            <CheckCircle class="w-5 h-5" />
            {{ $t('tournaments.registered') }}
          </button>
          <button
            v-else-if="isDeadlinePassed(tournament.registrationDeadline)"
            disabled
            class="w-full py-3 bg-slate-200 text-slate-500 rounded-xl font-semibold"
          >
            {{ $t('tournaments.registrationClosed') }}
          </button>
          <button
            v-else-if="(tournament.registrationsCount || 0) >= tournament.maxParticipants"
            disabled
            class="w-full py-3 bg-slate-200 text-slate-500 rounded-xl font-semibold"
          >
            {{ $t('common.noData') }}
          </button>
          <button
            v-else-if="hasParticipationRules(tournament) && !canParticipateInTournament(tournament)"
            disabled
            class="w-full py-3 bg-amber-100 text-amber-600 rounded-xl font-semibold flex items-center justify-center gap-2"
          >
            <AlertCircle class="w-5 h-5" />
            {{ $t('tournaments.directionCantParticipate') }}
          </button>
          <button
            v-else
            @click="openRegisterModal(tournament)"
            class="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/30 transition-all flex items-center justify-center gap-2"
          >
            <UserPlus class="w-5 h-5" />
            {{ $t('tournaments.register') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="filteredTournaments.length === 0" class="text-center py-16 bg-white rounded-2xl border border-slate-200">
      <Trophy class="w-16 h-16 mx-auto text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-slate-600">{{ $t('tournaments.noTournaments') }}</h3>
      <p class="text-slate-400 mt-1">{{ $t('tournaments.noTournamentsDesc') }}</p>
    </div>

    <!-- Registration Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showRegisterModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showRegisterModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-hidden">
            <!-- Modal header -->
            <div :class="['p-6 text-white relative overflow-hidden', getCategoryGradient(selectedTournament?.category)]">
              <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
              <div class="relative">
                <h3 class="text-xl font-bold">{{ $t('tournaments.registration') }}</h3>
                <p class="text-white/80 mt-1 text-sm">{{ selectedTournament?.title }}</p>
              </div>
            </div>

            <!-- Modal body -->
            <div class="p-6 overflow-y-auto max-h-[calc(90vh-200px)] space-y-4">
              <!-- Auto-filled info -->
              <div class="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                <p class="text-sm text-emerald-700 mb-2 font-medium">{{ $t('tournaments.autoFilled') }}</p>
                <div class="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span class="text-emerald-600">{{ $t('tournaments.yourName') }}:</span>
                    <span class="text-emerald-800 font-medium ml-1">{{ regForm.firstName }}</span>
                  </div>
                  <div>
                    <span class="text-emerald-600">{{ $t('tournaments.yourSurname') }}:</span>
                    <span class="text-emerald-800 font-medium ml-1">{{ regForm.lastName }}</span>
                  </div>
                  <div>
                    <span class="text-emerald-600">{{ $t('tournaments.yourPhone') }}:</span>
                    <span class="text-emerald-800 font-medium ml-1">{{ regForm.phone }}</span>
                  </div>
                  <div>
                    <span class="text-emerald-600">{{ $t('tournaments.yourGroup') }}:</span>
                    <span class="text-emerald-800 font-medium ml-1">{{ regForm.group }}</span>
                  </div>
                </div>
              </div>

              <!-- Subject Selection for Participation Rules Based Tournaments (YANGI MODEL) -->
              <div v-if="hasParticipationRules(selectedTournament)" class="space-y-3">
                <div class="flex items-center gap-2">
                  <BookOpen class="w-5 h-5 text-blue-500" />
                  <label class="text-sm font-semibold text-slate-700">
                    {{ $t('schedule.subjects') }}
                  </label>
                </div>
                
                <!-- Direction info -->
                <div v-if="getStudentDirectionName()" class="p-3 bg-blue-50 rounded-xl border border-blue-100">
                  <p class="text-sm text-blue-700">
                    <span class="font-medium">{{ $t('tournaments.yourDirection') }}:</span> {{ getStudentDirectionName() }}
                  </p>
                </div>

                <!-- Rule not found - Can't participate -->
                <div v-if="!getStudentParticipationRule(selectedTournament)" class="p-4 bg-amber-50 rounded-xl border border-amber-200">
                  <div class="flex items-start gap-3">
                    <AlertCircle class="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                    <div>
                      <p class="text-sm font-medium text-amber-700">{{ $t('tournaments.directionCantParticipate') }}</p>
                      <p class="text-xs text-amber-600 mt-1">
                        {{ $t('tournaments.directionNotOpen') }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- FIXED mode - Auto selected, just show info -->
                <div v-else-if="getStudentParticipationRule(selectedTournament)?.selectionMode === 'fixed'" class="space-y-2">
                  <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                    <p class="text-sm text-emerald-700 font-medium mb-2">
                      {{ $t('tournaments.autoFilled') }}:
                    </p>
                    <div class="flex items-center gap-2 p-2 bg-white rounded-lg border border-emerald-200">
                      <BookOpen class="w-5 h-5 text-emerald-500" />
                      <span class="font-semibold text-emerald-700">{{ getFixedSubject(selectedTournament)?.name }}</span>
                      <CheckCircle class="w-4 h-4 text-emerald-500 ml-auto" />
                    </div>
                  </div>
                </div>

                <!-- SINGLE mode - Choose one from allowed -->
                <div v-else-if="getStudentParticipationRule(selectedTournament)?.selectionMode === 'single'" class="space-y-2">
                  <p class="text-xs text-slate-500">
                    {{ $t('tournaments.selectOneSubject') }}:
                  </p>
                  <div class="grid grid-cols-2 gap-2">
                    <label
                      v-for="subject in getAllowedSubjects(selectedTournament)"
                      :key="subject.id"
                      :class="[
                        'relative flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all',
                        selectedSubjectIds.includes(subject.id)
                          ? 'border-emerald-500 bg-emerald-50'
                          : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
                      ]"
                    >
                      <input
                        type="radio"
                        :value="subject.id"
                        @change="selectSingleSubject(subject.id)"
                        :checked="selectedSubjectIds.includes(subject.id)"
                        class="sr-only"
                      />
                      <BookOpen :class="['w-5 h-5', selectedSubjectIds.includes(subject.id) ? 'text-emerald-500' : 'text-slate-400']" />
                      <span :class="[
                        'text-sm font-medium',
                        selectedSubjectIds.includes(subject.id) ? 'text-emerald-700' : 'text-slate-700'
                      ]">{{ subject.name }}</span>
                      <div v-if="selectedSubjectIds.includes(subject.id)" class="absolute top-1 right-1">
                        <CheckCircle class="w-4 h-4 text-emerald-500" />
                      </div>
                    </label>
                  </div>
                </div>

                <!-- MULTIPLE mode - Choose multiple from allowed -->
                <div v-else-if="getStudentParticipationRule(selectedTournament)?.selectionMode === 'multiple'" class="space-y-2">
                  <div class="flex items-center justify-between">
                    <p class="text-xs text-slate-500">
                      {{ $t('tournaments.selectSubjects') }}
                    </p>
                    <span class="text-xs font-medium text-blue-600">
                      {{ selectedSubjectIds.length }} / {{ getStudentParticipationRule(selectedTournament)?.maxSelect || '?' }} {{ $t('tournaments.selectedCount') }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-400">
                    {{ $t('tournaments.minimum') }} {{ getStudentParticipationRule(selectedTournament)?.minSelect || 1 }} ta, 
                    {{ $t('tournaments.maximum') }} {{ getStudentParticipationRule(selectedTournament)?.maxSelect || '?' }} {{ $t('tournaments.canSelect') }}
                  </p>
                  <div class="grid grid-cols-2 gap-2">
                    <label
                      v-for="subject in getAllowedSubjects(selectedTournament)"
                      :key="subject.id"
                      :class="[
                        'relative flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all',
                        selectedSubjectIds.includes(subject.id)
                          ? 'border-emerald-500 bg-emerald-50'
                          : canSelectMore || selectedSubjectIds.includes(subject.id)
                            ? 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
                            : 'border-slate-100 bg-slate-50 opacity-50 cursor-not-allowed'
                      ]"
                    >
                      <input
                        type="checkbox"
                        :value="subject.id"
                        @change="toggleSubject(subject.id)"
                        :checked="selectedSubjectIds.includes(subject.id)"
                        :disabled="!canSelectMore && !selectedSubjectIds.includes(subject.id)"
                        class="sr-only"
                      />
                      <BookOpen :class="['w-5 h-5', selectedSubjectIds.includes(subject.id) ? 'text-emerald-500' : 'text-slate-400']" />
                      <span :class="[
                        'text-sm font-medium',
                        selectedSubjectIds.includes(subject.id) ? 'text-emerald-700' : 'text-slate-700'
                      ]">{{ subject.name }}</span>
                      <div v-if="selectedSubjectIds.includes(subject.id)" class="absolute top-1 right-1">
                        <CheckCircle class="w-4 h-4 text-emerald-500" />
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Custom fields -->
              <div v-for="field in selectedTournament?.customFields" :key="field.id" class="space-y-1">
                <label class="block text-sm font-medium text-slate-700">
                  {{ field.name }}
                  <span v-if="field.required" class="text-rose-500">*</span>
                </label>
                
                <input
                  v-if="field.type === 'text'"
                  v-model="regForm.customFieldValues[field.name]"
                  type="text"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  :placeholder="$t('tournaments.enterField', { name: field.name })"
                />

                <input
                  v-else-if="field.type === 'number'"
                  v-model.number="regForm.customFieldValues[field.name]"
                  type="number"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  :placeholder="$t('tournaments.enterField', { name: field.name })"
                />

                <select
                  v-else-if="field.type === 'select'"
                  v-model="regForm.customFieldValues[field.name]"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                >
                  <option value="">{{ t('tournaments.selectPlaceholder') }}</option>
                  <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>

                <textarea
                  v-else-if="field.type === 'textarea'"
                  v-model="regForm.customFieldValues[field.name]"
                  rows="3"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  :placeholder="$t('tournaments.enterField', { name: field.name })"
                ></textarea>
              </div>

              <!-- Comment field -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-slate-700">
                  {{ $t('attendance.comment') }}
                </label>
                <textarea
                  v-model="regForm.comment"
                  rows="3"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  :placeholder="$t('tournaments.additionalInfo')"
                ></textarea>
              </div>
            </div>

            <!-- Modal footer -->
            <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-100 bg-slate-50">
              <button
                @click="showRegisterModal = false"
                class="px-5 py-2.5 text-slate-600 hover:bg-slate-200 rounded-xl font-medium transition-colors"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                @click="submitRegistration"
                class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all"
              >
                {{ $t('common.send') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Success Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showSuccessModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 text-center">
            <div class="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-5 animate-bounce-gentle">
              <CheckCircle class="w-10 h-10 text-emerald-500" />
            </div>
            <h3 class="text-2xl font-bold text-slate-800 mb-2">{{ $t('tournaments.success') }}</h3>
            <p class="text-slate-500 mb-6">
              {{ $t('common.success') }}
            </p>
            <button
              @click="showSuccessModal = false"
              class="px-8 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all"
            >
              {{ $t('common.close') }}
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import {
  AlertCircle,
  BookOpen,
  Brain,
  Calendar,
  CheckCircle,
  ClipboardCheck,
  Clock,
  Dumbbell,
  FlaskConical,
  Gift,
  MapPin,
  Palette,
  Trophy,
  UserPlus
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useDataStore } from '../../stores/data'
import { useLanguageStore } from '../../stores/language'
import { useToastStore } from '../../stores/toast'

const dataStore = useDataStore()
const authStore = useAuthStore()
const toast = useToastStore()
const { t } = useLanguageStore()

// Loading states
const loading = ref(false)
const submitting = ref(false)

// Load data on mount
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      dataStore.fetchTournaments(),
      dataStore.fetchDirections(),
      dataStore.fetchSubjects()
    ])
  } catch (err) {
    toast.error(t('common.error'))
    console.error(err)
  } finally {
    loading.value = false
  }
})

const showRegisterModal = ref(false)
const showSuccessModal = ref(false)
const selectedCategory = ref('all')
const selectedTournament = ref(null)
const selectedSubjectIds = ref([]) // YANGI: array ga o'zgartirildi

const categories = computed(() => [
  { value: 'all', label: t('common.all'), icon: Trophy },
  { value: 'intellektual', label: t('ai.analysis'), icon: Brain },
  { value: 'sport', label: t('clubs.sport'), icon: Dumbbell },
  { value: 'ijodiy', label: t('clubs.art'), icon: Palette },
  { value: 'ilmiy', label: t('clubs.science'), icon: FlaskConical }
])

const regForm = ref({
  firstName: '',
  lastName: '',
  phone: '',
  group: '',
  studentId: '',
  customFieldValues: {},
  comment: ''
})

const filteredTournaments = computed(() => {
  const active = dataStore.tournaments.filter(t => t.isActive)
  if (selectedCategory.value === 'all') {
    return active
  }
  return active.filter(t => t.category === selectedCategory.value)
})

const myRegistrations = computed(() => {
  return dataStore.getStudentRegistrations(authStore.user?.studentId || authStore.user?.id)
})

const getCategoryIcon = (category) => {
  const icons = {
    intellektual: Brain,
    sport: Dumbbell,
    ijodiy: Palette,
    ilmiy: FlaskConical
  }
  return icons[category] || Trophy
}

const getCategoryLabel = (category) => {
  const labels = {
    intellektual: t('tournaments.intellectual'),
    sport: t('tournaments.sport'),
    ijodiy: t('tournaments.creative'),
    ilmiy: t('tournaments.scientific')
  }
  return labels[category] || category
}

const getCategoryGradient = (category) => {
  const gradients = {
    intellektual: 'bg-gradient-to-r from-blue-500 to-indigo-500',
    sport: 'bg-gradient-to-r from-emerald-500 to-teal-500',
    ijodiy: 'bg-gradient-to-r from-purple-500 to-pink-500',
    ilmiy: 'bg-gradient-to-r from-amber-500 to-orange-500'
  }
  return gradients[category] || 'bg-gradient-to-r from-slate-500 to-slate-600'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

const isDeadlinePassed = (deadline) => {
  return new Date(deadline) < new Date()
}

const isRegistered = (tournamentId) => {
  return dataStore.isStudentRegistered(tournamentId, authStore.user?.studentId || authStore.user?.id)
}

const getStatusLabel = (status) => {
  const labels = {
    pending: t('common.loading'),
    approved: t('common.active'),
    rejected: t('common.inactive')
  }
  return labels[status] || status
}

const openRegisterModal = (tournament) => {
  selectedTournament.value = tournament
  selectedSubjectIds.value = [] // YANGI: array reset
  
  // Fixed rejimda avtomatik fan belgilash
  const rule = getStudentParticipationRule(tournament)
  if (rule?.selectionMode === 'fixed' && rule.allowedSubjectIds?.length > 0) {
    selectedSubjectIds.value = [...rule.allowedSubjectIds]
  }
  
  // Parse user name
  const nameParts = (authStore.user?.name || '').split(' ')
  
  regForm.value = {
    firstName: nameParts[0] || '',
    lastName: nameParts.slice(1).join(' ') || '',
    phone: authStore.user?.phone || '',
    group: authStore.user?.group || '',
    studentId: authStore.user?.studentId || authStore.user?.id,
    studentDbId: authStore.user?.studentDbId || authStore.user?.student_db_id || authStore.user?.id,
    customFieldValues: {},
    comment: ''
  }
  
  showRegisterModal.value = true
}

// ==========================================
// YANGI MODEL HELPER FUNKSIYALARI
// ==========================================

// Turnirda qatnashish qoidalari bormi?
const hasParticipationRules = (tournament) => {
  return dataStore.hasParticipationRules(tournament?.id)
}

// Talaba uchun qatnashish qoidasini olish
const getStudentParticipationRule = (tournament) => {
  if (!tournament) return null
  const userGroupId = authStore.user?.groupId
  if (!userGroupId) return null
  return dataStore.getParticipationRuleForStudent(tournament.id, userGroupId)
}

// Turnirga qatnasha oladimi?
const canParticipateInTournament = (tournament) => {
  if (!hasParticipationRules(tournament)) return true
  return !!getStudentParticipationRule(tournament)
}

// Ruxsat etilgan fanlarni olish
const getAllowedSubjects = (tournament) => {
  const rule = getStudentParticipationRule(tournament)
  if (!rule?.allowedSubjectIds) return []
  return rule.allowedSubjectIds.map(id => dataStore.getSubjectById(id)).filter(Boolean)
}

// Fixed rejimda tanlangan fanni olish
const getFixedSubject = (tournament) => {
  const rule = getStudentParticipationRule(tournament)
  if (!rule || rule.selectionMode !== 'fixed') return null
  return dataStore.getSubjectById(rule.allowedSubjectIds[0])
}

// Single rejimda bitta tanlash
const selectSingleSubject = (subjectId) => {
  selectedSubjectIds.value = [subjectId]
}

// Multiple rejimda toggle qilish
const toggleSubject = (subjectId) => {
  const index = selectedSubjectIds.value.indexOf(subjectId)
  if (index > -1) {
    selectedSubjectIds.value.splice(index, 1)
  } else {
    const rule = getStudentParticipationRule(selectedTournament.value)
    if (rule && selectedSubjectIds.value.length < rule.maxSelect) {
      selectedSubjectIds.value.push(subjectId)
    }
  }
}

// Multiple rejimda yana tanlash mumkinmi?
const canSelectMore = computed(() => {
  const rule = getStudentParticipationRule(selectedTournament.value)
  if (!rule) return false
  return selectedSubjectIds.value.length < rule.maxSelect
})

// Qatnashish qoidasi haqida ma'lumot
const getParticipationRuleInfo = (tournament) => {
  const rule = getStudentParticipationRule(tournament)
  if (!rule) return t('tournaments.directionNotMatch')
  
  switch (rule.selectionMode) {
    case 'fixed':
      const fixedSubject = dataStore.getSubjectById(rule.allowedSubjectIds[0])
      return t('tournaments.subjectLabel', { name: fixedSubject?.name || t('tournaments.unknownSubject') })
    case 'single':
      return t('tournaments.selectOneFrom', { count: rule.allowedSubjectIds.length })
    case 'multiple':
      return t('tournaments.selectRange', { min: rule.minSelect, max: rule.maxSelect })
    default:
      return ''
  }
}

// Talaba yo'nalishi nomi
const getStudentDirectionName = () => {
  const userGroupId = authStore.user?.groupId
  if (!userGroupId) return ''
  const direction = dataStore.getDirectionByGroupId(userGroupId)
  return direction?.name || ''
}

const submitRegistration = async () => {
  // YANGI MODEL: Qatnashish qoidalarini tekshirish
  if (hasParticipationRules(selectedTournament.value)) {
    const rule = getStudentParticipationRule(selectedTournament.value)
    
    if (!rule) {
      toast.error(t('tournaments.directionCantParticipateError'))
      return
    }

    // Validatsiya
    if (rule.selectionMode === 'single' && selectedSubjectIds.value.length !== 1) {
      toast.error(t('tournaments.selectOneSubjectError'))
      return
    }
    
    if (rule.selectionMode === 'multiple') {
      if (selectedSubjectIds.value.length < rule.minSelect) {
        toast.error(t('tournaments.minSelectError', { min: rule.minSelect }))
        return
      }
      if (selectedSubjectIds.value.length > rule.maxSelect) {
        toast.error(t('tournaments.maxSelectError', { max: rule.maxSelect }))
        return
      }
    }
  }
  
  // Validate required custom fields
  for (const field of selectedTournament.value.customFields || []) {
    if (field.required && !regForm.value.customFieldValues[field.name]) {
      toast.error(t('tournaments.fillFieldError', { name: field.name }))
      return
    }
  }

  const registrationData = {
    ...regForm.value,
    selectedSubjectIds: selectedSubjectIds.value // YANGI: array
  }

  submitting.value = true
  try {
    const result = await dataStore.registerForTournament(selectedTournament.value.id, registrationData)

    if (result.success) {
      showRegisterModal.value = false
      showSuccessModal.value = true
    } else if (result.alreadyRegistered) {
      showRegisterModal.value = false
      toast.info(result.message || t('tournaments.alreadyRegistered'))
    } else {
      toast.error(result.message || t('tournaments.errorOccurred'))
    }
  } catch (err) {
    const errMsg = err?.message || ''
    if (errMsg.includes('allaqachon') || errMsg.includes('409')) {
      showRegisterModal.value = false
      toast.info(t('tournaments.alreadyRegistered'))
    } else {
      toast.error(errMsg || t('tournaments.registrationError'))
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95) translateY(10px);
}

@keyframes bounce-gentle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.animate-bounce-gentle {
  animation: bounce-gentle 1s ease-in-out infinite;
}
</style>
