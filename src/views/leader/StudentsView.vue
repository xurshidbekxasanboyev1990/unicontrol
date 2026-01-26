<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Guruh talabalari</h1>
        <p class="text-slate-500">SE-401 guruhi — {{ groupStudents.length }} ta talaba</p>
      </div>
      <div class="relative">
        <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="Qidirish..."
          class="pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none w-64"
        />
      </div>
    </div>

    <!-- Students Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="student in filteredStudents" 
        :key="student.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start gap-4">
          <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xl font-bold">
            {{ student.name.charAt(0) }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-slate-800 truncate">{{ student.name }}</h3>
            <p class="text-sm text-slate-500">ID: {{ student.studentId }}</p>
          </div>
        </div>

        <div class="mt-4 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Phone class="w-4 h-4" />
              Telefon
            </span>
            <span class="text-slate-700">{{ student.phone || '—' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Percent class="w-4 h-4" />
              Davomat
            </span>
            <span 
              class="font-semibold"
              :class="getAttendanceRate(student.id) >= 85 ? 'text-emerald-600' : getAttendanceRate(student.id) >= 70 ? 'text-amber-600' : 'text-rose-600'"
            >
              {{ getAttendanceRate(student.id) }}%
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <FileCheck class="w-4 h-4" />
              Kontrakt
            </span>
            <span 
              class="px-2 py-0.5 rounded-lg text-xs font-medium"
              :class="student.contractPaid ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
            >
              {{ student.contractPaid ? 'To\'langan' : 'To\'lanmagan' }}
            </span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-100 flex gap-2">
          <button 
            @click="viewStudent(student)"
            class="flex-1 px-3 py-2 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
          >
            <Eye class="w-4 h-4" />
            Ko'rish
          </button>
          <button 
            @click="contactStudent(student)"
            class="flex-1 px-3 py-2 bg-emerald-100 text-emerald-700 rounded-xl text-sm font-medium hover:bg-emerald-200 transition-colors flex items-center justify-center gap-2"
          >
            <MessageCircle class="w-4 h-4" />
            Aloqa
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredStudents.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <UserX class="w-12 h-12 text-slate-300 mx-auto mb-4" />
      <p class="text-slate-500">Talaba topilmadi</p>
    </div>

    <!-- Student Detail Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="selectedStudent"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="selectedStudent = null"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-auto">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800">Talaba ma'lumotlari</h2>
            <button @click="selectedStudent = null" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div class="p-6">
            <div class="flex items-center gap-4 mb-6">
              <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-2xl font-bold">
                {{ selectedStudent.name.charAt(0) }}
              </div>
              <div>
                <h3 class="text-xl font-bold text-slate-800">{{ selectedStudent.name }}</h3>
                <p class="text-slate-500">{{ selectedStudent.group }}</p>
              </div>
            </div>

            <div class="space-y-4">
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <CreditCard class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">Talaba ID</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.studentId }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <Phone class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">Telefon</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.phone || 'Kiritilmagan' }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <MapPin class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">Manzil</p>
                  <p class="font-medium text-slate-800">{{ selectedStudent.address || 'Kiritilmagan' }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                <BarChart2 class="w-5 h-5 text-slate-400" />
                <div>
                  <p class="text-xs text-slate-500">Davomat</p>
                  <p class="font-medium text-slate-800">{{ getAttendanceRate(selectedStudent.id) }}%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../../stores/data'
import {
  Search,
  Phone,
  Percent,
  FileCheck,
  Eye,
  MessageCircle,
  UserX,
  X,
  CreditCard,
  MapPin,
  BarChart2
} from 'lucide-vue-next'

const dataStore = useDataStore()
const searchQuery = ref('')
const selectedStudent = ref(null)

const groupStudents = computed(() => {
  return dataStore.students.filter(s => s.group === 'SE-401')
})

const filteredStudents = computed(() => {
  if (!searchQuery.value) return groupStudents.value
  
  const query = searchQuery.value.toLowerCase()
  return groupStudents.value.filter(s => 
    s.name.toLowerCase().includes(query) ||
    s.studentId.toLowerCase().includes(query)
  )
})

const getAttendanceRate = (studentId) => {
  const records = dataStore.attendanceRecords.filter(r => r.studentId === studentId)
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 100
}

const viewStudent = (student) => {
  selectedStudent.value = student
}

const contactStudent = (student) => {
  if (student.phone) {
    window.open(`tel:${student.phone}`)
  }
}
</script>
