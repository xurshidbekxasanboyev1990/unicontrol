<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Talabalar boshqaruvi</h1>
        <p class="text-sm text-slate-500">{{ filteredStudents.length }} ta talaba</p>
      </div>
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div class="relative">
          <Search class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Qidirish..."
            class="w-full sm:w-64 pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
          />
        </div>
        <select v-model="filterGroup" class="px-4 py-2.5 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none">
          <option value="">Barcha guruhlar</option>
          <option v-for="group in dataStore.groups" :key="group.id" :value="group.name">
            {{ group.name }}
          </option>
        </select>
        <button 
          @click="openModal()"
          class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center justify-center gap-2"
        >
          <UserPlus class="w-5 h-5" />
          <span class="sm:inline hidden">Yangi talaba</span>
          <span class="sm:hidden">Qo'shish</span>
        </button>
      </div>
    </div>

    <!-- Students Table -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50">
              <th class="text-left p-4 font-semibold text-slate-600">Talaba</th>
              <th class="text-left p-4 font-semibold text-slate-600">ID</th>
              <th class="text-left p-4 font-semibold text-slate-600">Guruh</th>
              <th class="text-left p-4 font-semibold text-slate-600">Telefon</th>
              <th class="text-left p-4 font-semibold text-slate-600">Kontrakt</th>
              <th class="text-left p-4 font-semibold text-slate-600">Davomat</th>
              <th class="text-right p-4 font-semibold text-slate-600">Amallar</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="student in filteredStudents" :key="student.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white font-bold">
                    {{ student.name.charAt(0) }}
                  </div>
                  <span class="font-medium text-slate-800">{{ student.name }}</span>
                </div>
              </td>
              <td class="p-4 text-slate-600">{{ student.studentId }}</td>
              <td class="p-4">
                <span class="px-3 py-1 bg-violet-100 text-violet-700 rounded-lg text-sm font-medium">
                  {{ student.group }}
                </span>
              </td>
              <td class="p-4 text-slate-600">{{ student.phone || '—' }}</td>
              <td class="p-4">
                <span 
                  class="px-3 py-1 rounded-lg text-sm font-medium"
                  :class="student.contractPaid ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'"
                >
                  {{ student.contractPaid ? 'To\'langan' : 'To\'lanmagan' }}
                </span>
              </td>
              <td class="p-4">
                <div class="flex items-center gap-2">
                  <div class="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      class="h-full rounded-full"
                      :class="getAttendanceRate(student.id) >= 85 ? 'bg-emerald-500' : getAttendanceRate(student.id) >= 70 ? 'bg-amber-500' : 'bg-rose-500'"
                      :style="{ width: getAttendanceRate(student.id) + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm text-slate-600">{{ getAttendanceRate(student.id) }}%</span>
                </div>
              </td>
              <td class="p-4">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    @click="openModal(student)"
                    class="p-2 text-slate-400 hover:text-violet-500 hover:bg-violet-50 rounded-lg transition-colors"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button 
                    @click="confirmDelete(student)"
                    class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredStudents.length === 0" class="p-12 text-center">
        <UserX class="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p class="text-slate-500">Talaba topilmadi</p>
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
              {{ editingStudent ? 'Talabani tahrirlash' : 'Yangi talaba qo\'shish' }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveStudent" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">F.I.O</label>
              <input 
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="Ism familiya"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Talaba ID</label>
                <input 
                  v-model="form.studentId"
                  type="text"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="S12345"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Guruh</label>
                <select 
                  v-model="form.group"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                >
                  <option value="">Tanlang</option>
                  <option v-for="group in dataStore.groups" :key="group.id" :value="group.name">
                    {{ group.name }}
                  </option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Telefon</label>
              <input 
                v-model="form.phone"
                type="text"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="+998 90 123 45 67"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Manzil</label>
              <input 
                v-model="form.address"
                type="text"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="Shahar, tuman"
              />
            </div>
            <div class="flex items-center gap-3">
              <input 
                v-model="form.contractPaid"
                type="checkbox"
                id="contractPaid"
                class="w-5 h-5 rounded border-slate-300 text-violet-500 focus:ring-violet-500"
              />
              <label for="contractPaid" class="text-sm text-slate-700">Kontrakt to'langan</label>
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
            {{ deletingStudent?.name }} ni o'chirmoqchimisiz? Bu amalni qaytarib bo'lmaydi.
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              @click="deleteStudent"
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
import { ref, computed, reactive } from 'vue'
import { useDataStore } from '../../stores/data'
import {
  Search,
  UserPlus,
  Pencil,
  Trash2,
  UserX,
  X,
  AlertTriangle
} from 'lucide-vue-next'

const dataStore = useDataStore()
const searchQuery = ref('')
const filterGroup = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingStudent = ref(null)
const deletingStudent = ref(null)

const form = reactive({
  name: '',
  studentId: '',
  group: '',
  phone: '',
  address: '',
  contractPaid: false
})

const filteredStudents = computed(() => {
  let result = dataStore.students
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s => 
      s.name.toLowerCase().includes(query) ||
      s.studentId.toLowerCase().includes(query)
    )
  }
  
  if (filterGroup.value) {
    result = result.filter(s => s.group === filterGroup.value)
  }
  
  return result
})

const getAttendanceRate = (studentId) => {
  const records = dataStore.attendanceRecords.filter(r => r.studentId === studentId)
  const total = records.length
  const attended = records.filter(r => r.status === 'present' || r.status === 'late').length
  return total > 0 ? Math.round((attended / total) * 100) : 100
}

const openModal = (student = null) => {
  if (student) {
    editingStudent.value = student
    form.name = student.name
    form.studentId = student.studentId
    form.group = student.group
    form.phone = student.phone || ''
    form.address = student.address || ''
    form.contractPaid = student.contractPaid
  } else {
    editingStudent.value = null
    form.name = ''
    form.studentId = ''
    form.group = ''
    form.phone = ''
    form.address = ''
    form.contractPaid = false
  }
  showModal.value = true
}

const saveStudent = () => {
  if (editingStudent.value) {
    dataStore.updateStudent(editingStudent.value.id, { ...form })
  } else {
    dataStore.addStudent({ ...form })
  }
  showModal.value = false
}

const confirmDelete = (student) => {
  deletingStudent.value = student
  showDeleteConfirm.value = true
}

const deleteStudent = () => {
  if (deletingStudent.value) {
    dataStore.deleteStudent(deletingStudent.value.id)
  }
  showDeleteConfirm.value = false
  deletingStudent.value = null
}
</script>
