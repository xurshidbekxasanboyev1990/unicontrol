<template>
  <div class="space-y-6">
    <!-- Birthday Cards (bugungi va ertangi tug'ilgan kunlar) -->
    <div 
      v-if="todayBirthdays.length > 0 || tomorrowBirthdays.length > 0"
      class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-6 text-white shadow-lg"
    >
      <div class="absolute -right-6 -top-6 h-32 w-32 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-white/10"></div>
      
      <div class="relative">
        <!-- Bugungi tug'ilgan kunlar -->
        <div v-if="todayBirthdays.length > 0" class="mb-4">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <Cake :size="24" />
            </div>
            <div>
              <h3 class="text-lg font-bold">🎉 {{ $t('dashboard.todayBirthday') }}</h3>
              <p class="text-sm text-white/80">{{ todayDateFormatted }}</p>
            </div>
          </div>
          
          <div class="space-y-3">
            <div 
              v-for="student in todayBirthdays" 
              :key="'today-' + student.id"
              class="flex items-center gap-4 rounded-xl bg-white/15 p-4 backdrop-blur border border-white/20"
            >
              <div class="relative flex h-14 w-14 items-center justify-center rounded-xl bg-white/20 text-2xl font-bold">
                {{ student.name.charAt(0) }}
                <span class="absolute -top-1 -right-1 text-lg">🎂</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-lg truncate">{{ student.name }}</p>
                <p class="text-sm text-white/80">
                  {{ formatBirthDate(student.birth_date) }} • {{ student.age }} {{ $t('dashboard.yearsOld') }}
                </p>
              </div>
              <div class="flex flex-row sm:flex-col gap-2 flex-shrink-0">
                <button 
                  @click="sendCongratulation(student)"
                  :disabled="congratsSending[student.id]"
                  class="flex items-center gap-1.5 rounded-lg bg-white/20 px-2.5 sm:px-3 py-1.5 text-xs font-medium backdrop-blur transition-all hover:bg-white/30 disabled:opacity-50"
                >
                  <Gift :size="14" />
                  <span class="hidden sm:inline">{{ congratsSent[student.id] ? '✓ Yuborildi' : $t('dashboard.congratulate') }}</span>
                  <span class="sm:hidden">{{ congratsSent[student.id] ? '✓' : '🎉' }}</span>
                </button>
                <button 
                  @click="openMessageModal(student)"
                  class="flex items-center gap-1.5 rounded-lg bg-white px-2.5 sm:px-3 py-1.5 text-xs font-medium text-purple-600 transition-all hover:bg-white/90"
                >
                  <Send :size="14" />
                  <span class="hidden sm:inline">{{ $t('dashboard.sendMessage') }}</span>
                  <span class="sm:hidden">✉️</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Ertangi tug'ilgan kunlar -->
        <div v-if="tomorrowBirthdays.length > 0" :class="{ 'mt-6 pt-6 border-t border-white/20': todayBirthdays.length > 0 }">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <Calendar :size="24" />
            </div>
            <div>
              <h3 class="text-lg font-bold">🎂 {{ $t('dashboard.tomorrowBirthday') }}</h3>
              <p class="text-sm text-white/80">{{ tomorrowDateFormatted }}</p>
            </div>
          </div>
          
          <div class="space-y-3">
            <div 
              v-for="student in tomorrowBirthdays" 
              :key="'tmrw-' + student.id"
              class="flex items-center gap-4 rounded-xl bg-white/10 p-4 backdrop-blur"
            >
              <div class="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20 text-2xl font-bold">
                {{ student.name.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-lg truncate">{{ student.name }}</p>
                <p class="text-sm text-white/80">
                  {{ formatBirthDate(student.birth_date) }} • {{ student.age }} {{ $t('dashboard.willTurn') }}
                </p>
              </div>
              <div class="flex flex-col gap-2">
                <button 
                  @click="sendCongratulation(student)"
                  :disabled="congratsSending[student.id]"
                  class="flex items-center gap-1.5 rounded-lg bg-white/20 px-3 py-1.5 text-xs font-medium backdrop-blur transition-all hover:bg-white/30 disabled:opacity-50"
                >
                  <Gift :size="14" />
                  {{ congratsSent[student.id] ? '✓ Yuborildi' : $t('dashboard.congratulate') }}
                </button>
                <button 
                  @click="openMessageModal(student)"
                  class="flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 text-xs font-medium text-purple-600 transition-all hover:bg-white/90"
                >
                  <Send :size="14" />
                  {{ $t('dashboard.sendMessage') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Birthday Message Modal -->
    <Teleport to="body">
      <div 
        v-if="showMessageModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="showMessageModal = false"
      >
        <div class="relative mx-4 w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <button @click="showMessageModal = false" class="absolute top-3 right-3 p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors z-10"><X class="w-5 h-5" /></button>
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100">
              <Gift :size="24" class="text-purple-600" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-slate-800">{{ $t('dashboard.sendBirthdayMessage') }}</h3>
              <p class="text-sm text-slate-500">{{ messageTarget?.name }}</p>
            </div>
          </div>
          
          <textarea
            v-model="customMessage"
            :placeholder="$t('dashboard.birthdayMessagePlaceholder')"
            class="w-full rounded-xl border border-slate-200 p-3 text-sm text-slate-700 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 resize-none"
            rows="4"
          ></textarea>
          
          <div class="mt-4 flex gap-3 justify-end">
            <button 
              @click="showMessageModal = false"
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              @click="sendCustomMessage"
              :disabled="!customMessage.trim() || sendingMessage"
              class="flex items-center gap-2 rounded-xl bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
            >
              <Send :size="16" />
              {{ sendingMessage ? $t('common.sending') : $t('dashboard.sendMessage') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800 md:text-3xl">{{ $t('layout.dashboard') }}</h1>
        <p class="text-slate-500">{{ currentGroup?.name }} <span v-if="currentGroup?.specialty" class="text-emerald-600">({{ currentGroup?.specialty }})</span> - {{ $t('dashboard.todayStatus') }}</p>
      </div>
      
      <div class="flex items-center gap-3">
        <span class="text-sm text-slate-400">
          {{ new Date().toLocaleDateString('uz-UZ', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}
        </span>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-1 gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Davomat foizi -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('dashboard.attendancePercentage') }}</p>
            <p class="mt-1 text-2xl sm:text-3xl font-bold text-slate-800">{{ attendanceRate }}%</p>
            <p class="mt-1 text-xs text-slate-400">{{ $t('dashboard.thisMonth') }}</p>
          </div>
          <div class="rounded-lg bg-green-100 p-2.5">
            <CheckCircle :size="24" class="text-green-600" />
          </div>
        </div>
      </div>

      <!-- Darslar -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('dashboard.lessons') }}</p>
            <p class="mt-1 text-2xl sm:text-3xl font-bold text-slate-800">{{ todayLessons.length }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ $t('dashboard.today') }}</p>
          </div>
          <div class="rounded-lg bg-purple-100 p-2.5">
            <BookOpen :size="24" class="text-purple-600" />
          </div>
        </div>
      </div>

      <!-- Davomat xulosasi (mini) -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('attendance.todayAttendance') }}</p>
            <p class="mt-1 text-2xl sm:text-3xl font-bold text-slate-800">{{ presentToday }}/{{ groupStudents.length }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ $t('attendance.present') }}</p>
          </div>
          <div class="rounded-lg bg-blue-100 p-2.5">
            <Users :size="24" class="text-blue-600" />
          </div>
        </div>
      </div>

      <!-- Tezkor statistika -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ $t('attendance.absent') }}</p>
            <p class="mt-1 text-2xl sm:text-3xl font-bold text-slate-800">{{ absentToday }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ $t('dashboard.today') }}</p>
          </div>
          <div class="rounded-lg bg-red-100 p-2.5">
            <XCircle :size="24" class="text-red-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Bugungi jadval -->
      <div class="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">{{ $t('dashboard.todaySchedule') }}</h3>
          <Calendar :size="18" class="text-slate-400" />
        </div>
        
        <div v-if="todayLessons.length === 0" class="flex flex-col items-center justify-center py-8 text-slate-400">
          <Calendar :size="40" class="mb-2 opacity-50" />
          <p class="text-sm">{{ $t('dashboard.noLessonsToday') }}</p>
        </div>
        
        <div v-else class="space-y-3">
          <div
            v-for="lesson in todayLessons"
            :key="lesson.id"
            class="flex items-center gap-4 rounded-lg bg-slate-50 p-4"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <BookOpen :size="20" class="text-blue-600" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-slate-800">{{ lesson.subject }}</p>
              <p class="text-sm text-slate-500">{{ lesson.time }} • {{ lesson.room }}</p>
            </div>
            <span 
              class="rounded-lg px-3 py-1.5 text-xs font-medium"
              :class="getLessonStatusClass(lesson)"
            >
              {{ getLessonStatus(lesson) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tezkor amallar -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">{{ $t('common.actions') }}</h3>
          <Zap :size="18" class="text-yellow-500" />
        </div>
        
        <div class="grid grid-cols-2 gap-3">
          <button
            @click="navigateTo('/leader/attendance')"
            class="flex flex-col items-center gap-3 rounded-xl bg-blue-50 p-4 text-blue-600 transition-all hover:bg-blue-100"
          >
            <CheckCircle :size="28" />
            <span class="text-sm font-medium">{{ $t('layout.attendance') }}</span>
          </button>
          <button
            @click="navigateTo('/leader/students')"
            class="flex flex-col items-center gap-3 rounded-xl bg-purple-50 p-4 text-purple-600 transition-all hover:bg-purple-100"
          >
            <Users :size="28" />
            <span class="text-sm font-medium">{{ $t('layout.students') }}</span>
          </button>
          <button
            @click="navigateTo('/leader/schedule')"
            class="flex flex-col items-center gap-3 rounded-xl bg-green-50 p-4 text-green-600 transition-all hover:bg-green-100"
          >
            <Calendar :size="28" />
            <span class="text-sm font-medium">{{ $t('layout.schedule') }}</span>
          </button>
          <button
            @click="navigateTo('/leader/analytics')"
            class="flex flex-col items-center gap-3 rounded-xl bg-orange-50 p-4 text-orange-600 transition-all hover:bg-orange-100"
          >
            <TrendingUp :size="28" />
            <span class="text-sm font-medium">{{ $t('layout.analytics') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Davomat xulosasi (to'liq) -->
    <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="font-semibold text-slate-800">{{ $t('attendance.todayAttendance') }}</h3>
        <span class="text-sm text-slate-500">{{ groupStudents.length }} {{ $t('roles.student').toLowerCase() }}</span>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <div class="rounded-xl bg-green-50 p-4 text-center">
          <p class="text-3xl font-bold text-green-600">{{ presentToday }}</p>
          <p class="text-sm text-green-600/70">{{ $t('attendance.present') }}</p>
        </div>
        <div class="rounded-xl bg-red-50 p-4 text-center">
          <p class="text-3xl font-bold text-red-600">{{ absentToday }}</p>
          <p class="text-sm text-red-600/70">{{ $t('attendance.absent') }}</p>
        </div>
        <div class="rounded-xl bg-yellow-50 p-4 text-center">
          <p class="text-3xl font-bold text-yellow-600">{{ lateToday }}</p>
          <p class="text-sm text-yellow-600/70">{{ $t('attendance.late') }}</p>
        </div>
      </div>
      
      <div class="h-3 overflow-hidden rounded-full bg-slate-100">
        <div class="flex h-full">
          <div 
            class="bg-green-500 transition-all" 
            :style="{ width: presentPercent + '%' }"
          ></div>
          <div 
            class="bg-yellow-500 transition-all" 
            :style="{ width: latePercent + '%' }"
          ></div>
          <div 
            class="bg-red-500 transition-all" 
            :style="{ width: absentPercent + '%' }"
          ></div>
        </div>
      </div>
      
      <p class="mt-3 text-center text-sm text-slate-500">
        {{ Math.round((presentToday + lateToday) / (groupStudents.length || 1) * 100) }}% davomat
      </p>
    </div>
  </div>
</template>

<script setup>
/**
 * Leader Dashboard - Real API Integration
 * Guruh sardorining boshqaruv paneli
 */
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import { useLanguageStore } from '@/stores/language'
import {
    BookOpen,
    Cake,
    Calendar,
    CheckCircle,
    Gift, Send,
    TrendingUp,
    Users,
    X,
    XCircle, Zap
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const dataStore = useDataStore()
const authStore = useAuthStore()
const { t } = useLanguageStore()

// State
const loading = ref(true)
const error = ref(null)
const dashboardData = ref(null)
const groupStudentsList = ref([])
const scheduleList = ref([])
const attendanceToday = ref([])

// Birthday state
const birthdayData = ref({ today: [], tomorrow: [], upcoming: [] })
const congratsSending = ref({})
const congratsSent = ref({})
const showMessageModal = ref(false)
const messageTarget = ref(null)
const customMessage = ref('')
const sendingMessage = ref(false)
// Load dashboard data
async function loadDashboard() {
  loading.value = true
  error.value = null
  
  try {
    let groupId = null
    
    // Leader dashboard endpoint - guruh statistikalari
    try {
      const response = await api.request('/dashboard/leader')
      dashboardData.value = response
      
      if (response.group?.id) {
        groupId = response.group.id
      }
    } catch (e) {
      console.warn('Leader dashboard endpoint not available')
    }
    
    // Agar dashboard-dan olmagan bo'lsak
    if (!groupId) {
      groupId = authStore.user?.groupId || authStore.user?.managed_group_id || authStore.user?.group_id
    }
    
    if (groupId) {
      // Guruh talabalarini yuklash
      try {
        const studentsResp = await api.getStudents({ group_id: groupId, page_size: 100 })
        const items = studentsResp.items || studentsResp.data || []
        groupStudentsList.value = items.map(s => ({
          id: s.id,
          name: s.name || s.full_name || 'Ism kiritilmagan',
          studentId: s.student_id || '',
          groupId: s.group_id,
          phone: s.phone,
          birthDate: s.birth_date
        }))
      } catch (e) {
        console.warn('Could not load group students')
      }
      
      // Jadval yuklash
      try {
        const scheduleResp = await api.getScheduleByGroup(groupId)
        // Week schedule returns {monday: [], tuesday: [], ...}
        const dayMapping = {
          'monday': 'Dushanba', 'tuesday': 'Seshanba', 'wednesday': 'Chorshanba',
          'thursday': 'Payshanba', 'friday': 'Juma', 'saturday': 'Shanba', 'sunday': 'Yakshanba'
        }
        const allLessons = []
        for (const [dayKey, lessons] of Object.entries(scheduleResp || {})) {
          if (Array.isArray(lessons)) {
            lessons.forEach(lesson => {
              // Skip cancelled lessons
              if (lesson.is_cancelled) return
              // Build time string: strip spaces and seconds
              let timeStr = lesson.time_range || `${lesson.start_time || ''}-${lesson.end_time || ''}`
              timeStr = timeStr.replace(/\s/g, '').replace(/(\d{2}:\d{2}):\d{2}/g, '$1')
              allLessons.push({
                ...lesson,
                day: dayMapping[dayKey] || dayKey,
                time: timeStr,
                room: lesson.room || lesson.location || '',
                teacher: lesson.teacher_name || ''
              })
            })
          }
        }
        scheduleList.value = allLessons
      } catch (e) {
        console.warn('Could not load schedule')
      }
      
      // Bugungi davomat
      try {
        const today = new Date().toISOString().split('T')[0]
        const attResp = await api.getAttendance({ 
          group_id: groupId, 
          date_from: today,
          date_to: today
        })
        attendanceToday.value = attResp.items || attResp.data || []
      } catch (e) {
        console.warn('Could not load today attendance')
      }
      
      // Tug'ilgan kunlarni yuklash (API orqali)
      try {
        const bdayResp = await api.getUpcomingBirthdays({ group_id: groupId, days: 7 })
        birthdayData.value = {
          today: bdayResp.today || [],
          tomorrow: bdayResp.tomorrow || [],
          upcoming: bdayResp.upcoming || []
        }
      } catch (e) {
        console.warn('Could not load birthdays:', e.message)
      }
    }
  } catch (e) {
    console.error('Dashboard load error:', e)
    error.value = e.message || 'Ma\'lumotlar yuklanmadi'
  } finally {
    loading.value = false
  }
}

// Computed
const currentGroup = computed(() => {
  // dashboardData dan olish
  if (dashboardData.value?.group) {
    return {
      id: dashboardData.value.group.id,
      name: dashboardData.value.group.name,
      specialty: dashboardData.value.group.specialty || dashboardData.value.group.faculty,
      students_count: dashboardData.value.group.students_count
    }
  }
  const groupId = authStore.user?.groupId || authStore.user?.managed_group_id
  const groupName = authStore.user?.group || authStore.user?.managedGroup
  return {
    id: groupId,
    name: groupName || authStore.user?.group_name || 'Noma\'lum guruh',
    specialty: ''
  }
})

const groupStudents = computed(() => groupStudentsList.value)

// Tug'ilgan kunlar (API-dan)
const todayBirthdays = computed(() => birthdayData.value.today)
const tomorrowBirthdays = computed(() => birthdayData.value.tomorrow)

const todayDateFormatted = computed(() => {
  return new Date().toLocaleDateString('uz-UZ', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
})

const tomorrowDateFormatted = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toLocaleDateString('uz-UZ', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
})

function formatBirthDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'long', year: 'numeric' })
  } catch {
    return dateStr
  }
}

// Birthday tabrik yuborish
async function sendCongratulation(student) {
  congratsSending.value[student.id] = true
  try {
    const message = `🎂🎉 Hurmatli ${student.name}!\n\nTug'ilgan kuningiz muborak bo'lsin! Sizga baxt, sog'lik va muvaffaqiyatlar tilaymiz!\n\nHurmat bilan, ${authStore.user?.name || 'Guruh rahbari'}`
    
    await api.createNotification({
      user_id: student.user_id,
      title: "🎂 Tug'ilgan kun tabrigi!",
      message: message,
      type: 'info',
      priority: 'high'
    })
    
    congratsSent.value[student.id] = true
  } catch (e) {
    console.error('Tabrik yuborishda xatolik:', e)
    alert('Tabrik yuborishda xatolik: ' + (e.message || 'Noma\'lum xatolik'))
  } finally {
    congratsSending.value[student.id] = false
  }
}

function openMessageModal(student) {
  messageTarget.value = student
  customMessage.value = `Hurmatli ${student.name}!\n\nTug'ilgan kuningiz muborak! 🎂🎉\n\n`
  showMessageModal.value = true
}

async function sendCustomMessage() {
  if (!customMessage.value.trim() || !messageTarget.value) return
  sendingMessage.value = true
  try {
    await api.createNotification({
      user_id: messageTarget.value.user_id,
      title: "🎂 Tug'ilgan kun xabari",
      message: customMessage.value.trim(),
      type: 'info',
      priority: 'high'
    })
    
    congratsSent.value[messageTarget.value.id] = true
    showMessageModal.value = false
    customMessage.value = ''
    messageTarget.value = null
  } catch (e) {
    console.error('Xabar yuborishda xatolik:', e)
    alert('Xabar yuborishda xatolik: ' + (e.message || 'Noma\'lum xatolik'))
  } finally {
    sendingMessage.value = false
  }
}

const todayLessons = computed(() => {
  const days = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  const today = days[new Date().getDay()]
  return scheduleList.value.filter(s => 
    s.day === today
  )
})

// Attendance stats
const presentToday = computed(() => {
  return attendanceToday.value.filter(a => a.status === 'present' || a.status === 'keldi').length
})

const absentToday = computed(() => {
  return attendanceToday.value.filter(a => a.status === 'absent' || a.status === 'kelmadi').length
})

const lateToday = computed(() => {
  return attendanceToday.value.filter(a => a.status === 'late' || a.status === 'kechikdi').length
})

const attendanceRate = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round(((presentToday.value + lateToday.value) / total) * 100)
})

const presentPercent = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round((presentToday.value / total) * 100)
})

const latePercent = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round((lateToday.value / total) * 100)
})

const absentPercent = computed(() => {
  const total = groupStudents.value.length || 1
  return Math.round((absentToday.value / total) * 100)
})

// Methods
function navigateTo(path) {
  router.push(path)
}

function getTashkentNow() {
  const now = new Date()
  return new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Tashkent' }))
}

function getLessonStatus(lesson) {
  const now = getTashkentNow()
  const timeStr = lesson.time || lesson.start_time || ''
  if (!timeStr.includes('-')) return t('dashboard.lessonPending')
  
  const [startHour, startMin] = timeStr.split('-')[0].split(':').map(Number)
  const [endHour, endMin] = timeStr.split('-')[1].split(':').map(Number)
  
  const startTime = new Date(now)
  startTime.setHours(startHour, startMin, 0, 0)
  
  const endTime = new Date(now)
  endTime.setHours(endHour, endMin, 0, 0)
  
  if (now < startTime) return t('dashboard.lessonPending')
  if (now > endTime) return t('dashboard.lessonFinished')
  return t('dashboard.lessonOngoing')
}

function getLessonStatusClass(lesson) {
  const now = getTashkentNow()
  const timeStr = lesson.time || lesson.start_time || ''
  if (!timeStr.includes('-')) return 'bg-blue-100 text-blue-600'
  
  const [startHour, startMin] = timeStr.split('-')[0].split(':').map(Number)
  const [endHour, endMin] = timeStr.split('-')[1].split(':').map(Number)
  
  const startTime = new Date(now)
  startTime.setHours(startHour, startMin, 0, 0)
  
  const endTime = new Date(now)
  endTime.setHours(endHour, endMin, 0, 0)
  
  if (now > endTime) return 'bg-slate-200 text-slate-500'
  if (now >= startTime) return 'bg-green-100 text-green-600'
  return 'bg-blue-100 text-blue-600'
}

// Refresh
async function refresh() {
  await loadDashboard()
}

// Mount
onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
/* Minimal styles */
</style>
