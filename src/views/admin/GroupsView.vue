<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Guruhlar boshqaruvi</h1>
        <p class="text-slate-500">{{ dataStore.groups.length }} ta guruh</p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Excel Import -->
        <label class="px-4 py-2.5 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors flex items-center gap-2 cursor-pointer">
          <FileSpreadsheet class="w-5 h-5" />
          Excel yuklash
          <input 
            type="file"
            accept=".xlsx,.xls,.csv"
            @change="handleExcelUpload"
            class="hidden"
          />
        </label>
        <button 
          @click="openModal()"
          class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2"
        >
          <FolderPlus class="w-5 h-5" />
          Yangi guruh
        </button>
      </div>
    </div>

    <!-- Excel Format Info -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
      <div class="flex items-start gap-3">
        <Info class="w-5 h-5 text-blue-500 mt-0.5" />
        <div>
          <p class="text-sm font-medium text-blue-800">Excel fayl formati</p>
          <p class="text-sm text-blue-600 mt-1">
            Excel faylda quyidagi ustunlar bo'lishi kerak: <span class="font-mono">Guruh, Fakultet, Talaba ID, Ism Familiya, Telefon, Parol</span>
          </p>
          <button @click="downloadTemplate" class="text-sm text-blue-700 underline mt-2 hover:text-blue-800">
            Namuna faylni yuklab olish
          </button>
        </div>
      </div>
    </div>

    <!-- Groups Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="group in dataStore.groups" 
        :key="group.id"
        class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
        :class="{ 'opacity-60 border-rose-200': !group.isActive }"
      >
        <!-- Status Badge -->
        <div class="px-6 pt-4 flex items-center justify-between">
          <span 
            class="px-3 py-1 rounded-full text-xs font-semibold"
            :class="group.isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
          >
            {{ group.isActive ? 'Faol' : 'O\'chirilgan' }}
          </span>
          <button 
            @click="toggleStatus(group)"
            class="p-2 rounded-lg transition-colors"
            :class="group.isActive ? 'text-emerald-500 hover:bg-emerald-50' : 'text-rose-500 hover:bg-rose-50'"
            :title="group.isActive ? 'O\'chirish' : 'Yoqish'"
          >
            <Power class="w-4 h-4" />
          </button>
        </div>

        <div class="p-6 pt-3">
          <div class="flex items-start justify-between mb-4">
            <div 
              class="w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold"
              :class="groupColors[group.id % groupColors.length]"
            >
              {{ group.name.slice(-3) }}
            </div>
            <div class="flex items-center gap-1">
              <button 
                @click="openLeaderModal(group)"
                class="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                title="Sardor tayinlash"
              >
                <Crown class="w-4 h-4" />
              </button>
              <button 
                @click="openModal(group)"
                class="p-2 text-slate-400 hover:text-violet-500 hover:bg-violet-50 rounded-lg transition-colors"
              >
                <Pencil class="w-4 h-4" />
              </button>
              <button 
                @click="confirmDelete(group)"
                class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <h3 class="text-xl font-bold text-slate-800">{{ group.name }}</h3>
          <p class="text-slate-500 text-sm mt-1">{{ group.year }}-kurs • {{ group.faculty || 'Noma\'lum' }}</p>

          <div class="mt-4 pt-4 border-t border-slate-100 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500 flex items-center gap-2">
                <Users class="w-4 h-4" />
                Talabalar
              </span>
              <span class="font-semibold text-slate-700">{{ getStudentCount(group.name) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500 flex items-center gap-2">
                <Crown class="w-4 h-4" />
                Sardor
              </span>
              <span 
                class="font-medium"
                :class="group.leaderName ? 'text-amber-600' : 'text-slate-400'"
              >
                {{ group.leaderName || 'Tayinlanmagan' }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500 flex items-center gap-2">
                <TrendingUp class="w-4 h-4" />
                Davomat
              </span>
              <span 
                class="font-semibold"
                :class="getGroupAttendance(group.name) >= 85 ? 'text-emerald-600' : getGroupAttendance(group.name) >= 70 ? 'text-amber-600' : 'text-rose-600'"
              >
                {{ getGroupAttendance(group.name) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="dataStore.groups.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <Layers class="w-12 h-12 text-slate-300 mx-auto mb-4" />
      <p class="text-slate-500">Hali guruh yo'q</p>
      <p class="text-sm text-slate-400 mt-2">Excel fayl yuklash yoki qo'lda qo'shish mumkin</p>
      <div class="flex items-center justify-center gap-3 mt-4">
        <label class="px-4 py-2 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors cursor-pointer">
          <FileSpreadsheet class="w-4 h-4 inline mr-2" />
          Excel yuklash
          <input 
            type="file"
            accept=".xlsx,.xls,.csv"
            @change="handleExcelUpload"
            class="hidden"
          />
        </label>
        <button 
          @click="openModal()"
          class="px-4 py-2 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors"
        >
          Qo'lda qo'shish
        </button>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800">
              {{ editingGroup ? 'Guruhni tahrirlash' : 'Yangi guruh qo\'shish' }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveGroup" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Guruh nomi</label>
              <input 
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="KI_25-04"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Kurs</label>
                <input 
                  v-model="form.year"
                  type="number"
                  min="1"
                  max="6"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Fakultet</label>
                <input 
                  v-model="form.faculty"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="Kompyuter injiniringi"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Kontrakt summasi</label>
              <input 
                v-model.number="form.contractAmount"
                type="number"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="18411000"
              />
            </div>
            <div class="flex gap-3 pt-4">
              <button 
                type="button"
                @click="showModal = false"
                class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
              >
                Bekor qilish
              </button>
              <button 
                type="submit"
                class="flex-1 px-4 py-3 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors"
              >
                Saqlash
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Leader Assignment Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showLeaderModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showLeaderModal = false"
      >
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-800">Sardor tayinlash</h2>
              <p class="text-sm text-slate-500">{{ selectedGroup?.name }} guruhi</p>
            </div>
            <button @click="showLeaderModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div class="p-6">
            <!-- Current Leader -->
            <div v-if="selectedGroup?.leaderName" class="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center text-white font-bold">
                    <Crown class="w-5 h-5" />
                  </div>
                  <div>
                    <p class="font-medium text-amber-800">Hozirgi sardor</p>
                    <p class="text-sm text-amber-600">{{ selectedGroup.leaderName }}</p>
                  </div>
                </div>
                <button 
                  @click="removeLeader"
                  class="px-3 py-1.5 bg-rose-100 text-rose-600 rounded-lg text-sm font-medium hover:bg-rose-200 transition-colors"
                >
                  Olib tashlash
                </button>
              </div>
            </div>

            <!-- Search -->
            <div class="relative mb-4">
              <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                v-model="leaderSearch"
                type="text"
                placeholder="Talaba qidirish..."
                class="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
              />
            </div>

            <!-- Students List -->
            <div class="max-h-64 overflow-y-auto space-y-2">
              <div 
                v-for="student in filteredGroupStudents" 
                :key="student.id"
                @click="assignLeader(student)"
                class="p-4 border border-slate-200 rounded-xl hover:border-amber-300 hover:bg-amber-50 cursor-pointer transition-all"
                :class="{ 'border-amber-400 bg-amber-50': selectedGroup?.leaderId === student.id }"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white font-bold">
                    {{ student.name.charAt(0) }}
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-slate-800">{{ student.name }}</p>
                    <p class="text-sm text-slate-500">{{ student.studentId }}</p>
                  </div>
                  <div v-if="selectedGroup?.leaderId === student.id">
                    <Crown class="w-5 h-5 text-amber-500" />
                  </div>
                </div>
              </div>
              <div v-if="filteredGroupStudents.length === 0" class="text-center py-8 text-slate-500">
                <Users class="w-8 h-8 mx-auto mb-2 text-slate-300" />
                <p>Talaba topilmadi</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Delete Confirmation -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showDeleteConfirm = false"
      >
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 text-center">
          <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle class="w-8 h-8 text-rose-500" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 mb-2">O'chirishni tasdiqlang</h3>
          <p class="text-slate-500 mb-6">
            {{ deletingGroup?.name }} guruhini o'chirmoqchimisiz? Guruh ichidagi talabalar ham o'chiriladi.
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              @click="deleteGroup"
              class="flex-1 px-4 py-3 bg-rose-500 text-white rounded-xl font-medium hover:bg-rose-600 transition-colors"
            >
              O'chirish
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Excel Import Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showImportModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showImportModal = false"
      >
        <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-800">Excel import natijasi</h2>
              <p class="text-sm text-slate-500">{{ importData.length }} ta guruh topildi</p>
            </div>
            <button @click="showImportModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <div class="p-6 max-h-96 overflow-y-auto">
            <div v-for="(group, idx) in importData" :key="idx" class="mb-4 p-4 border border-slate-200 rounded-xl">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-semibold text-slate-800">{{ group.group }}</h3>
                <span class="px-2 py-1 bg-violet-100 text-violet-700 rounded-lg text-sm">
                  {{ group.students.length }} talaba
                </span>
              </div>
              <div class="text-sm text-slate-500 space-y-1">
                <p><span class="font-medium">Fakultet:</span> {{ group.faculty || 'Noma\'lum' }}</p>
                <p><span class="font-medium">Talabalar:</span></p>
                <ul class="ml-4 list-disc">
                  <li v-for="(s, i) in group.students.slice(0, 3)" :key="i">{{ s.name }} ({{ s.studentId }})</li>
                  <li v-if="group.students.length > 3" class="text-slate-400">va yana {{ group.students.length - 3 }} ta...</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="p-6 border-t border-slate-100 flex gap-3">
            <button 
              @click="showImportModal = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              @click="confirmImport"
              class="flex-1 px-4 py-3 bg-emerald-500 text-white rounded-xl font-medium hover:bg-emerald-600 transition-colors"
            >
              Barchasini import qilish
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  FolderPlus,
  FileSpreadsheet,
  Pencil,
  Trash2,
  Users,
  Crown,
  TrendingUp,
  Layers,
  Power,
  X,
  AlertTriangle,
  Info,
  Search
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

const showModal = ref(false)
const showDeleteConfirm = ref(false)
const showLeaderModal = ref(false)
const showImportModal = ref(false)
const editingGroup = ref(null)
const deletingGroup = ref(null)
const selectedGroup = ref(null)
const leaderSearch = ref('')
const importData = ref([])

const groupColors = [
  'bg-gradient-to-br from-violet-500 to-purple-600',
  'bg-gradient-to-br from-blue-500 to-cyan-600',
  'bg-gradient-to-br from-emerald-500 to-teal-600',
  'bg-gradient-to-br from-orange-500 to-red-600',
  'bg-gradient-to-br from-pink-500 to-rose-600'
]

const form = reactive({
  name: '',
  year: 1,
  faculty: '',
  contractAmount: 18411000
})

const getStudentCount = (groupName) => {
  return dataStore.students.filter(s => s.group === groupName).length
}

const getGroupStudents = (groupName) => {
  return dataStore.students.filter(s => s.group === groupName)
}

const filteredGroupStudents = computed(() => {
  if (!selectedGroup.value) return []
  const students = getGroupStudents(selectedGroup.value.name)
  if (!leaderSearch.value) return students
  return students.filter(s => 
    s.name.toLowerCase().includes(leaderSearch.value.toLowerCase()) ||
    s.studentId.toLowerCase().includes(leaderSearch.value.toLowerCase())
  )
})

const getGroupAttendance = (groupName) => {
  const groupStudents = dataStore.students.filter(s => s.group === groupName)
  const studentIds = groupStudents.map(s => s.id)
  const records = dataStore.attendanceRecords.filter(r => studentIds.includes(r.studentId))
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 0
}

const openModal = (group = null) => {
  if (group) {
    editingGroup.value = group
    form.name = group.name
    form.year = group.year
    form.faculty = group.faculty || ''
    form.contractAmount = group.contractAmount || 18411000
  } else {
    editingGroup.value = null
    form.name = ''
    form.year = 1
    form.faculty = ''
    form.contractAmount = 18411000
  }
  showModal.value = true
}

const saveGroup = () => {
  if (editingGroup.value) {
    dataStore.updateGroup(editingGroup.value.id, { ...form })
    toast.success('Guruh yangilandi')
  } else {
    dataStore.addGroup({ ...form, isActive: true })
    toast.success('Yangi guruh qo\'shildi')
  }
  showModal.value = false
}

const confirmDelete = (group) => {
  deletingGroup.value = group
  showDeleteConfirm.value = true
}

const deleteGroup = () => {
  if (deletingGroup.value) {
    // Guruhdagi talabalarni ham o'chirish
    const groupStudents = dataStore.students.filter(s => s.group === deletingGroup.value.name)
    groupStudents.forEach(s => dataStore.deleteStudent(s.id))
    
    dataStore.deleteGroup(deletingGroup.value.id)
    toast.success('Guruh o\'chirildi')
  }
  showDeleteConfirm.value = false
  deletingGroup.value = null
}

const toggleStatus = (group) => {
  dataStore.toggleGroupStatus(group.id)
  toast.info(group.isActive ? 'Guruh o\'chirildi' : 'Guruh yoqildi')
}

// Leader Management
const openLeaderModal = (group) => {
  selectedGroup.value = group
  leaderSearch.value = ''
  showLeaderModal.value = true
}

const assignLeader = (student) => {
  if (selectedGroup.value) {
    dataStore.assignGroupLeader(selectedGroup.value.id, student.id)
    // Update selected group reference
    selectedGroup.value = dataStore.groups.find(g => g.id === selectedGroup.value.id)
    toast.success(`${student.name} sardor qilindi`)
    showLeaderModal.value = false
  }
}

const removeLeader = () => {
  if (selectedGroup.value) {
    dataStore.removeGroupLeader(selectedGroup.value.id)
    selectedGroup.value = dataStore.groups.find(g => g.id === selectedGroup.value.id)
    toast.info('Sardor olib tashlandi')
    showLeaderModal.value = false
  }
}

// Excel Import
const handleExcelUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Reset input
  event.target.value = ''
  
  // Simulated Excel parsing (real implementation would use xlsx library)
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      // For demo purposes, parsing CSV-like format
      const text = e.target.result
      const lines = text.split('\n').filter(l => l.trim())
      
      if (lines.length < 2) {
        toast.error('Fayl bo\'sh yoki noto\'g\'ri format')
        return
      }
      
      // Parse header
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
      const groupIdx = headers.findIndex(h => h.includes('guruh') || h.includes('group'))
      const facultyIdx = headers.findIndex(h => h.includes('fakultet') || h.includes('faculty'))
      const studentIdIdx = headers.findIndex(h => h.includes('talaba id') || h.includes('student id') || h.includes('id'))
      const nameIdx = headers.findIndex(h => h.includes('ism') || h.includes('name') || h.includes('familiya'))
      const phoneIdx = headers.findIndex(h => h.includes('telefon') || h.includes('phone'))
      const passwordIdx = headers.findIndex(h => h.includes('parol') || h.includes('password'))
      
      if (groupIdx === -1 || nameIdx === -1) {
        toast.error('Guruh yoki Ism ustuni topilmadi')
        return
      }
      
      // Parse data rows
      const groupsMap = {}
      
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(',').map(c => c.trim())
        const groupName = cols[groupIdx]
        
        if (!groupName) continue
        
        if (!groupsMap[groupName]) {
          groupsMap[groupName] = {
            group: groupName,
            faculty: facultyIdx !== -1 ? cols[facultyIdx] : '',
            year: 1,
            students: []
          }
        }
        
        groupsMap[groupName].students.push({
          studentId: studentIdIdx !== -1 ? cols[studentIdIdx] : `ST-${Date.now()}-${i}`,
          name: cols[nameIdx],
          phone: phoneIdx !== -1 ? cols[phoneIdx] : '',
          password: passwordIdx !== -1 ? cols[passwordIdx] : '123456'
        })
      }
      
      importData.value = Object.values(groupsMap)
      
      if (importData.value.length > 0) {
        showImportModal.value = true
      } else {
        toast.error('Ma\'lumot topilmadi')
      }
      
    } catch (error) {
      console.error('Parse error:', error)
      toast.error('Faylni o\'qishda xatolik')
    }
  }
  
  reader.readAsText(file)
}

const confirmImport = () => {
  dataStore.importFromExcel(importData.value)
  
  const totalStudents = importData.value.reduce((sum, g) => sum + g.students.length, 0)
  toast.success(`${importData.value.length} ta guruh va ${totalStudents} ta talaba import qilindi`)
  
  showImportModal.value = false
  importData.value = []
}

const downloadTemplate = () => {
  const csv = `Guruh,Fakultet,Talaba ID,Ism Familiya,Telefon,Parol
KI_25-04,Kompyuter injiniringi,ST-2024-001,Aliyev Jasur,+998901234567,123456
KI_25-04,Kompyuter injiniringi,ST-2024-002,Karimov Sardor,+998912345678,123456
DI_25-21,Dasturiy injiniring,ST-2024-003,Toshmatov Alisher,+998923456789,123456`
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'guruhlar_namuna.csv'
  link.click()
  
  toast.info('Namuna fayl yuklab olindi')
}
</script>
