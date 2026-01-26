<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-800 md:text-3xl">Statistika va Tahlil</h1>
      <p class="text-slate-500">{{ currentGroup?.name }} - Davomat va boshqa ko'rsatkichlar</p>
    </div>

    <!-- Date Range Filter -->
    <div class="mb-6 flex flex-wrap items-center gap-4">
      <div class="flex items-center gap-2 rounded-lg bg-slate-100 p-2">
        <button
          v-for="range in dateRanges"
          :key="range.value"
          @click="selectedRange = range.value"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="selectedRange === range.value 
            ? 'bg-emerald-500 text-white' 
            : 'text-slate-600 hover:bg-slate-200'"
        >
          {{ range.label }}
        </button>
      </div>
      
      <div class="flex items-center gap-2">
        <input
          v-model="customStartDate"
          type="date"
          class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none"
        />
        <span class="text-slate-400">—</span>
        <input
          v-model="customEndDate"
          type="date"
          class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none"
        />
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div 
        v-for="card in summaryCards" 
        :key="card.title"
        class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500">{{ card.title }}</p>
            <p class="mt-1 text-2xl font-bold text-slate-800">{{ card.value }}</p>
          </div>
          <div 
            class="rounded-lg p-3"
            :class="'bg-' + card.color + '-100'"
          >
            <component :is="card.icon" :size="24" :class="'text-' + card.color + '-600'" />
          </div>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <component 
            :is="card.trend > 0 ? TrendingUp : card.trend < 0 ? TrendingDown : Minus" 
            :size="16" 
            :class="card.trend > 0 ? 'text-green-600' : card.trend < 0 ? 'text-red-600' : 'text-slate-500'"
          />
          <span 
            class="text-sm"
            :class="card.trend > 0 ? 'text-green-600' : card.trend < 0 ? 'text-red-600' : 'text-slate-500'"
          >
            {{ card.trend > 0 ? '+' : '' }}{{ card.trend }}% o'tgan davriga nisbatan
          </span>
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Attendance Trend Chart -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800">Davomat dinamikasi</h3>
          <div class="flex gap-2">
            <button
              @click="trendChartType = 'line'"
              class="rounded p-1.5 transition-colors"
              :class="trendChartType === 'line' ? 'bg-emerald-500 text-white' : 'text-slate-500 hover:bg-slate-100'"
            >
              <TrendingUp :size="18" />
            </button>
            <button
              @click="trendChartType = 'bar'"
              class="rounded p-1.5 transition-colors"
              :class="trendChartType === 'bar' ? 'bg-emerald-500 text-white' : 'text-slate-500 hover:bg-slate-100'"
            >
              <BarChart3 :size="18" />
            </button>
          </div>
        </div>
        <div class="h-64">
          <Line v-if="trendChartType === 'line'" :data="attendanceTrendData" :options="lineChartOptions" />
          <Bar v-else :data="attendanceTrendData" :options="barChartOptions" />
        </div>
      </div>

      <!-- Status Distribution Chart -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800">Status bo'yicha taqsimot</h3>
          <PieChart :size="18" class="text-slate-400" />
        </div>
        <div class="h-64">
          <Doughnut :data="statusDistributionData" :options="doughnutChartOptions" />
        </div>
        <div class="mt-4 flex flex-wrap justify-center gap-4">
          <div v-for="(label, i) in statusLabels" :key="label" class="flex items-center gap-2">
            <div class="h-3 w-3 rounded-full" :style="{ backgroundColor: statusColors[i] }"></div>
            <span class="text-sm text-slate-500">{{ label }}</span>
          </div>
        </div>
      </div>

      <!-- Weekly Heatmap -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:col-span-2">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800">Haftalik davomat xaritasi</h3>
          <Calendar :size="18" class="text-slate-400" />
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[600px]">
            <thead>
              <tr>
                <th class="p-2 text-left text-sm text-slate-500">Talaba</th>
                <th v-for="day in weekDays" :key="day" class="p-2 text-center text-sm text-slate-500">
                  {{ day }}
                </th>
                <th class="p-2 text-center text-sm text-slate-500">Jami %</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in heatmapData" :key="student.id" class="border-t border-slate-100">
                <td class="p-2 text-sm text-slate-800">{{ student.name }}</td>
                <td v-for="(status, dayIndex) in student.days" :key="dayIndex" class="p-2 text-center">
                  <div 
                    class="mx-auto h-8 w-8 rounded-lg flex items-center justify-center text-xs font-medium"
                    :class="getHeatmapCellClass(status)"
                    :title="getStatusLabel(status)"
                  >
                    {{ getStatusShort(status) }}
                  </div>
                </td>
                <td class="p-2 text-center">
                  <span 
                    class="font-medium"
                    :class="student.rate >= 80 ? 'text-green-600' : student.rate >= 60 ? 'text-yellow-600' : 'text-red-600'"
                  >
                    {{ student.rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Student Comparison Chart -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800">Talabalar solishtirmasi</h3>
          <Users :size="18" class="text-slate-400" />
        </div>
        <div class="h-64">
          <Bar :data="studentComparisonData" :options="horizontalBarOptions" />
        </div>
      </div>

      <!-- Subject Attendance Chart -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800">Fanlar bo'yicha davomat</h3>
          <BookOpen :size="18" class="text-slate-400" />
        </div>
        <div class="h-64">
          <Radar :data="subjectAttendanceData" :options="radarChartOptions" />
        </div>
      </div>
    </div>

    <!-- Top/Bottom Students -->
    <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Top Attendance -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center gap-2">
          <Award class="text-yellow-500" :size="20" />
          <h3 class="text-lg font-semibold text-slate-800">Eng yaxshi davomat</h3>
        </div>
        <div class="space-y-3">
          <div 
            v-for="(student, index) in topStudents" 
            :key="student.id"
            class="flex items-center gap-3 rounded-lg bg-slate-50 p-3"
          >
            <div 
              class="flex h-8 w-8 items-center justify-center rounded-full font-bold"
              :class="index === 0 ? 'bg-yellow-500 text-yellow-900' : index === 1 ? 'bg-slate-300 text-slate-700' : 'bg-orange-400 text-orange-900'"
            >
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-800">{{ student.name }}</p>
              <p class="text-xs text-slate-500">{{ student.present }}/{{ student.total }} dars</p>
            </div>
            <span class="text-lg font-bold text-green-600">{{ student.rate }}%</span>
          </div>
        </div>
      </div>

      <!-- Needs Attention -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center gap-2">
          <AlertTriangle class="text-red-500" :size="20" />
          <h3 class="text-lg font-semibold text-slate-800">E'tibor kerak</h3>
        </div>
        <div class="space-y-3">
          <div 
            v-for="student in needsAttention" 
            :key="student.id"
            class="flex items-center gap-3 rounded-lg bg-red-50 p-3"
          >
            <div class="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
              <span class="text-sm font-medium text-red-600">{{ student.name.charAt(0) }}</span>
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-800">{{ student.name }}</p>
              <p class="text-xs text-red-600">{{ student.absent }} marta kelmagan</p>
            </div>
            <span class="text-lg font-bold text-red-600">{{ student.rate }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar, Doughnut, Radar } from 'vue-chartjs'
import {
  TrendingUp, TrendingDown, Minus, BarChart3, PieChart, Calendar,
  Users, BookOpen, Award, AlertTriangle, CheckCircle, XCircle, Clock
} from 'lucide-vue-next'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
)

const dataStore = useDataStore()
const authStore = useAuthStore()

// State
const selectedRange = ref('month')
const customStartDate = ref('')
const customEndDate = ref('')
const trendChartType = ref('line')

const dateRanges = [
  { label: 'Hafta', value: 'week' },
  { label: 'Oy', value: 'month' },
  { label: 'Semestr', value: 'semester' },
  { label: 'Yil', value: 'year' }
]

const weekDays = ['Du', 'Se', 'Cho', 'Pa', 'Ju', 'Sha', 'Ya']
const statusLabels = ['Keldi', 'Kelmadi', 'Kech qoldi', 'Sababli']
const statusColors = ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6']

// Computed
const currentGroup = computed(() => {
  const groupId = authStore.user?.groupId
  return dataStore.groups.find(g => g.id === groupId)
})

const groupStudents = computed(() => {
  const groupId = authStore.user?.groupId
  return dataStore.students.filter(s => s.groupId === groupId)
})

const summaryCards = computed(() => [
  {
    title: 'Umumiy davomat',
    value: calculateOverallAttendance() + '%',
    icon: CheckCircle,
    color: 'green',
    trend: 5
  },
  {
    title: 'Kelmaganlar soni',
    value: getTotalAbsent(),
    icon: XCircle,
    color: 'red',
    trend: -3
  },
  {
    title: 'Kech qolganlar',
    value: getTotalLate(),
    icon: Clock,
    color: 'yellow',
    trend: 2
  },
  {
    title: 'Darslar soni',
    value: getTotalLessons(),
    icon: BookOpen,
    color: 'blue',
    trend: 0
  }
])

// Chart Data
const attendanceTrendData = computed(() => {
  const labels = getLast7Days()
  const presentData = [85, 90, 88, 92, 87, 91, 89]
  const absentData = [10, 7, 8, 5, 9, 6, 8]
  const lateData = [5, 3, 4, 3, 4, 3, 3]

  return {
    labels,
    datasets: [
      {
        label: 'Keldi',
        data: presentData,
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Kelmadi',
        data: absentData,
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Kech qoldi',
        data: lateData,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const statusDistributionData = computed(() => {
  const present = 75
  const absent = 10
  const late = 8
  const excused = 7

  return {
    labels: statusLabels,
    datasets: [{
      data: [present, absent, late, excused],
      backgroundColor: statusColors,
      borderWidth: 0,
      hoverOffset: 10
    }]
  }
})

const heatmapData = computed(() => {
  return groupStudents.value.slice(0, 10).map(student => {
    const days = weekDays.map(() => {
      const rand = Math.random()
      if (rand > 0.85) return 'absent'
      if (rand > 0.75) return 'late'
      if (rand > 0.7) return 'excused'
      return 'present'
    })
    
    const presentCount = days.filter(d => d === 'present' || d === 'late').length
    const rate = Math.round((presentCount / days.length) * 100)
    
    return {
      id: student.id,
      name: student.name.split(' ').slice(0, 2).join(' '),
      days,
      rate
    }
  })
})

const studentComparisonData = computed(() => {
  const students = groupStudents.value.slice(0, 8)
  const rates = students.map(() => Math.floor(Math.random() * 30) + 70)

  return {
    labels: students.map(s => s.name.split(' ')[0]),
    datasets: [{
      label: 'Davomat %',
      data: rates,
      backgroundColor: rates.map(r => 
        r >= 90 ? '#22c55e' : r >= 75 ? '#f59e0b' : '#ef4444'
      ),
      borderRadius: 6
    }]
  }
})

const subjectAttendanceData = computed(() => {
  return {
    labels: ['Matematika', 'Fizika', 'Informatika', 'Ingliz tili', 'Tarix', 'Kimyo'],
    datasets: [{
      label: 'Davomat %',
      data: [92, 85, 95, 88, 78, 90],
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      borderColor: '#3b82f6',
      borderWidth: 2,
      pointBackgroundColor: '#3b82f6'
    }]
  }
})

const topStudents = computed(() => {
  return groupStudents.value
    .slice(0, 5)
    .map(s => ({
      ...s,
      present: Math.floor(Math.random() * 10) + 85,
      total: 95,
      rate: Math.floor(Math.random() * 10) + 90
    }))
    .sort((a, b) => b.rate - a.rate)
    .slice(0, 3)
})

const needsAttention = computed(() => {
  return groupStudents.value
    .slice(0, 5)
    .map(s => ({
      ...s,
      absent: Math.floor(Math.random() * 10) + 5,
      rate: Math.floor(Math.random() * 20) + 50
    }))
    .sort((a, b) => a.rate - b.rate)
    .slice(0, 3)
})

// Chart Options
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#94a3b8', usePointStyle: true }
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(148, 163, 184, 0.1)' },
      ticks: { color: '#94a3b8' }
    },
    y: {
      grid: { color: 'rgba(148, 163, 184, 0.1)' },
      ticks: { color: '#94a3b8' },
      min: 0,
      max: 100
    }
  }
}

const barChartOptions = {
  ...lineChartOptions,
  plugins: {
    ...lineChartOptions.plugins
  }
}

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '60%',
  plugins: {
    legend: { display: false }
  }
}

const horizontalBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: {
      grid: { color: 'rgba(148, 163, 184, 0.1)' },
      ticks: { color: '#94a3b8' },
      min: 0,
      max: 100
    },
    y: {
      grid: { display: false },
      ticks: { color: '#94a3b8' }
    }
  }
}

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    r: {
      grid: { color: 'rgba(148, 163, 184, 0.2)' },
      angleLines: { color: 'rgba(148, 163, 184, 0.2)' },
      ticks: { 
        color: '#94a3b8',
        backdropColor: 'transparent'
      },
      pointLabels: { color: '#94a3b8' },
      min: 0,
      max: 100
    }
  }
}

// Methods
function calculateOverallAttendance() {
  return 87 // Simulated
}

function getTotalAbsent() {
  return 24
}

function getTotalLate() {
  return 18
}

function getTotalLessons() {
  return 156
}

function getLast7Days() {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(date.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short' }))
  }
  return days
}

function getHeatmapCellClass(status) {
  switch (status) {
    case 'present': return 'bg-green-500/30 text-green-400'
    case 'absent': return 'bg-red-500/30 text-red-400'
    case 'late': return 'bg-yellow-500/30 text-yellow-400'
    case 'excused': return 'bg-blue-500/30 text-blue-400'
    default: return 'bg-slate-700 text-slate-400'
  }
}

function getStatusLabel(status) {
  const labels = {
    present: 'Keldi',
    absent: 'Kelmadi',
    late: 'Kech qoldi',
    excused: 'Sababli'
  }
  return labels[status] || status
}

function getStatusShort(status) {
  const shorts = {
    present: 'K',
    absent: 'X',
    late: 'KQ',
    excused: 'S'
  }
  return shorts[status] || '?'
}
</script>
