<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Guruhlar boshqaruvi</h1>
        <p class="text-slate-500">{{ dataStore.groups.length }} ta guruh</p>
      </div>
      <button 
        @click="openModal()"
        class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2"
      >
        <FolderPlus class="w-5 h-5" />
        Yangi guruh
      </button>
    </div>

    <!-- Groups Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="group in dataStore.groups" 
        :key="group.id"
        class="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div 
            class="w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold"
            :class="groupColors[group.id % groupColors.length]"
          >
            {{ group.name.slice(-3) }}
          </div>
          <div class="flex items-center gap-1">
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
        <p class="text-slate-500 text-sm mt-1">{{ group.year }}-yil • {{ group.faculty || 'Dasturiy injiniring' }}</p>

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
              Boshlig'i
            </span>
            <span class="font-medium text-slate-700">{{ group.leaderName || '—' }}</span>
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

    <!-- Empty State -->
    <div v-if="dataStore.groups.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <Layers class="w-12 h-12 text-slate-300 mx-auto mb-4" />
      <p class="text-slate-500">Hali guruh yo'q</p>
      <button 
        @click="openModal()"
        class="mt-4 px-4 py-2 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors"
      >
        Birinchi guruhni qo'shing
      </button>
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
                placeholder="SE-401"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">O'quv yili</label>
                <input 
                  v-model="form.year"
                  type="number"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="2024"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Fakultet</label>
                <input 
                  v-model="form.faculty"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="Dasturiy injiniring"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Guruh boshlig'i</label>
              <select 
                v-model="form.leaderName"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
              >
                <option value="">Tanlanmagan</option>
                <option v-for="student in getGroupStudents(form.name)" :key="student.id" :value="student.name">
                  {{ student.name }}
                </option>
              </select>
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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useDataStore } from '../../stores/data'
import {
  FolderPlus,
  Pencil,
  Trash2,
  Users,
  Crown,
  TrendingUp,
  Layers,
  X,
  AlertTriangle
} from 'lucide-vue-next'

const dataStore = useDataStore()
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingGroup = ref(null)
const deletingGroup = ref(null)

const groupColors = [
  'bg-gradient-to-br from-violet-500 to-purple-600',
  'bg-gradient-to-br from-blue-500 to-cyan-600',
  'bg-gradient-to-br from-emerald-500 to-teal-600',
  'bg-gradient-to-br from-orange-500 to-red-600',
  'bg-gradient-to-br from-pink-500 to-rose-600'
]

const form = reactive({
  name: '',
  year: new Date().getFullYear(),
  faculty: '',
  leaderName: ''
})

const getStudentCount = (groupName) => {
  return dataStore.students.filter(s => s.group === groupName).length
}

const getGroupStudents = (groupName) => {
  return dataStore.students.filter(s => s.group === groupName)
}

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
    form.leaderName = group.leaderName || ''
  } else {
    editingGroup.value = null
    form.name = ''
    form.year = new Date().getFullYear()
    form.faculty = ''
    form.leaderName = ''
  }
  showModal.value = true
}

const saveGroup = () => {
  if (editingGroup.value) {
    dataStore.updateGroup(editingGroup.value.id, { ...form })
  } else {
    dataStore.addGroup({ ...form })
  }
  showModal.value = false
}

const confirmDelete = (group) => {
  deletingGroup.value = group
  showDeleteConfirm.value = true
}

const deleteGroup = () => {
  if (deletingGroup.value) {
    dataStore.deleteGroup(deletingGroup.value.id)
  }
  showDeleteConfirm.value = false
  deletingGroup.value = null
}
</script>
