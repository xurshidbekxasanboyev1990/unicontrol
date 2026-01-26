<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-700 p-6 text-white">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-white/10"></div>
      
      <div class="relative flex items-center gap-4">
        <div class="relative">
          <div class="h-16 w-16 overflow-hidden rounded-2xl bg-white/20 backdrop-blur">
            <img 
              v-if="user?.avatar" 
              :src="user.avatar" 
              class="h-full w-full object-cover"
            />
            <div v-else class="flex h-full w-full items-center justify-center text-2xl font-bold">
              {{ user?.name?.charAt(0) || 'T' }}
            </div>
          </div>
          <div class="absolute -bottom-1 -right-1 h-5 w-5 rounded-full border-2 border-white bg-green-400"></div>
        </div>
        
        <div class="flex-1">
          <p class="text-blue-100">Xush kelibsiz!</p>
          <h1 class="text-2xl font-bold">{{ user?.name || 'Talaba' }}</h1>
          <p class="mt-1 text-sm text-blue-200">{{ currentGroup?.name }} guruhi</p>
        </div>
        
        <div class="text-right">
          <p class="text-sm text-blue-200">{{ formattedDate }}</p>
          <p class="text-lg font-medium">{{ formattedTime }}</p>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100">
            <TrendingUp :size="24" class="text-green-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ attendanceRate }}%</p>
            <p class="text-xs text-slate-500">Davomat</p>
          </div>
        </div>
      </div>
      
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
            <BookOpen :size="24" class="text-blue-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ todayLessons.length }}</p>
            <p class="text-xs text-slate-500">Bugungi dars</p>
          </div>
        </div>
      </div>
      
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100">
            <Book :size="24" class="text-purple-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ borrowedBooks }}</p>
            <p class="text-xs text-slate-500">Olingan kitob</p>
          </div>
        </div>
      </div>
      
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100">
            <Bell :size="24" class="text-amber-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ unreadNotifications }}</p>
            <p class="text-xs text-slate-500">Yangi xabar</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid gap-6 lg:grid-cols-3">
      <!-- Today's Schedule -->
      <div class="lg:col-span-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">Bugungi darslar</h2>
          <router-link to="/student/schedule" class="text-sm text-blue-500 hover:text-blue-600">
            Barchasi →
          </router-link>
        </div>
        
        <div v-if="todayLessons.length === 0" class="flex flex-col items-center justify-center py-8 text-slate-400">
          <Calendar :size="48" class="mb-2 opacity-50" />
          <p>Bugun darslar yo'q</p>
        </div>
        
        <div v-else class="space-y-3">
          <div
            v-for="lesson in todayLessons.slice(0, 4)"
            :key="lesson.id"
            class="flex items-center gap-4 rounded-xl bg-slate-50 p-4 transition-all hover:bg-slate-100"
          >
            <div class="flex h-12 w-12 flex-col items-center justify-center rounded-xl bg-blue-500 text-white">
              <span class="text-xs">{{ lesson.time.split('-')[0].split(':')[0] }}</span>
              <span class="text-[10px] opacity-75">{{ lesson.time.split('-')[0].split(':')[1] }}</span>
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-800">{{ lesson.subject }}</p>
              <p class="text-sm text-slate-500">{{ lesson.room }} • {{ lesson.teacher }}</p>
            </div>
            <span 
              class="rounded-lg px-3 py-1 text-xs font-medium"
              :class="getLessonStatusClass(lesson)"
            >
              {{ getLessonStatus(lesson) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Section -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Recent Attendance -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">So'nggi davomat</h2>
          <router-link to="/student/attendance" class="text-sm text-blue-500 hover:text-blue-600">
            Barchasi →
          </router-link>
        </div>
        
        <div class="space-y-2">
          <div
            v-for="record in recentAttendance"
            :key="record.date"
            class="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3"
          >
            <div class="flex items-center gap-3">
              <div 
                class="flex h-10 w-10 items-center justify-center rounded-lg"
                :class="getAttendanceColor(record.status)"
              >
                <CheckCircle v-if="record.status === 'present'" :size="20" />
                <XCircle v-else-if="record.status === 'absent'" :size="20" />
                <Clock v-else :size="20" />
              </div>
              <div>
                <p class="text-sm font-medium text-slate-800">{{ formatDateShort(record.date) }}</p>
                <p class="text-xs text-slate-500">{{ record.subject }}</p>
              </div>
            </div>
            <span 
              class="rounded-lg px-3 py-1 text-xs font-medium"
              :class="getAttendanceBadge(record.status)"
            >
              {{ getAttendanceText(record.status) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Library Quick Access -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">Kutubxona</h2>
          <router-link to="/student/library" class="text-sm text-blue-500 hover:text-blue-600">
            Barchasi →
          </router-link>
        </div>
        
        <div class="mb-4 grid grid-cols-3 gap-3">
          <button
            @click="$router.push('/student/library?category=darslik')"
            class="flex flex-col items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-600 transition-all hover:bg-blue-100"
          >
            <GraduationCap :size="24" />
            <span class="text-xs">Darsliklar</span>
          </button>
          <button
            @click="$router.push('/student/library?category=ilmiy')"
            class="flex flex-col items-center gap-2 rounded-xl bg-purple-50 p-3 text-purple-600 transition-all hover:bg-purple-100"
          >
            <FileText :size="24" />
            <span class="text-xs">Ilmiy</span>
          </button>
          <button
            @click="$router.push('/student/library?category=badiiy')"
            class="flex flex-col items-center gap-2 rounded-xl bg-amber-50 p-3 text-amber-600 transition-all hover:bg-amber-100"
          >
            <BookOpen :size="24" />
            <span class="text-xs">Badiiy</span>
          </button>
        </div>
        
        <div class="rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 p-4 text-white">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
              <Book :size="24" />
            </div>
            <div>
              <p class="font-medium">KUAF Mutola</p>
              <p class="text-sm text-emerald-100">{{ totalBooks }}+ elektron kitob</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <router-link 
        to="/student/schedule"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-blue-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
          <Calendar :size="20" class="text-blue-600" />
        </div>
        <span class="font-medium text-slate-700">Jadval</span>
      </router-link>
      
      <router-link 
        to="/student/attendance"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-green-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
          <CheckCircle :size="20" class="text-green-600" />
        </div>
        <span class="font-medium text-slate-700">Davomat</span>
      </router-link>
      
      <router-link 
        to="/student/library"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-purple-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100">
          <Book :size="20" class="text-purple-600" />
        </div>
        <span class="font-medium text-slate-700">Kutubxona</span>
      </router-link>
      
      <router-link 
        to="/student/profile"
        class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-amber-300 hover:shadow-md"
      >
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
          <User :size="20" class="text-amber-600" />
        </div>
        <span class="font-medium text-slate-700">Profil</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import {
  TrendingUp, BookOpen, Book, Bell, Calendar,
  CheckCircle, XCircle, Clock, GraduationCap, FileText, User
} from 'lucide-vue-next'

const authStore = useAuthStore()
const dataStore = useDataStore()

const currentTime = ref(new Date())
let timeInterval = null

onMounted(() => {
  timeInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timeInterval)
})

// Computed
const user = computed(() => authStore.user)

const currentGroup = computed(() => {
  return dataStore.groups.find(g => g.id === user.value?.groupId)
})

const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('uz-UZ', {
    weekday: 'long',
    day: 'numeric',
    month: 'long'
  })
})

const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('uz-UZ', {
    hour: '2-digit',
    minute: '2-digit'
  })
})

const todayLessons = computed(() => {
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
  return dataStore.schedule.filter(s => 
    s.groupId === user.value?.groupId && s.day.toLowerCase() === today
  )
})

const attendanceRate = computed(() => {
  const records = dataStore.attendanceRecords.filter(a => a.studentId === user.value?.id)
  if (records.length === 0) return 100
  const present = records.filter(a => a.status === 'present' || a.status === 'late').length
  return Math.round((present / records.length) * 100)
})

const recentAttendance = computed(() => {
  return dataStore.attendanceRecords
    .filter(a => a.studentId === user.value?.id)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
    .map(a => ({
      ...a,
      subject: 'Matematika' // Mock subject
    }))
})

const borrowedBooks = ref(2)
const unreadNotifications = ref(3)
const totalBooks = ref(5000)

// Methods
function getLessonStatus(lesson) {
  const now = new Date()
  const [startHour, startMin] = lesson.time.split('-')[0].split(':').map(Number)
  const [endHour, endMin] = lesson.time.split('-')[1].split(':').map(Number)
  
  const startTime = new Date()
  startTime.setHours(startHour, startMin, 0)
  
  const endTime = new Date()
  endTime.setHours(endHour, endMin, 0)
  
  if (now < startTime) return 'Kutilmoqda'
  if (now > endTime) return 'Tugadi'
  return 'Hozir'
}

function getLessonStatusClass(lesson) {
  const status = getLessonStatus(lesson)
  if (status === 'Hozir') return 'bg-green-100 text-green-600'
  if (status === 'Tugadi') return 'bg-slate-100 text-slate-500'
  return 'bg-blue-100 text-blue-600'
}

function getAttendanceColor(status) {
  if (status === 'present') return 'bg-green-100 text-green-600'
  if (status === 'absent') return 'bg-red-100 text-red-600'
  return 'bg-yellow-100 text-yellow-600'
}

function getAttendanceBadge(status) {
  if (status === 'present') return 'bg-green-100 text-green-600'
  if (status === 'absent') return 'bg-red-100 text-red-600'
  return 'bg-yellow-100 text-yellow-600'
}

function getAttendanceText(status) {
  if (status === 'present') return 'Keldi'
  if (status === 'absent') return 'Kelmadi'
  return 'Kechikdi'
}

function formatDateShort(date) {
  return new Date(date).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'short'
  })
}
</script>
