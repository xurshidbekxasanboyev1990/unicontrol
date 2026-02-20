<template>
  <div class="space-y-4">
    <!-- Toolbar: Faculty → Direction → Group cascading filter -->
    <div class="rounded-2xl bg-white p-4 shadow-sm border border-gray-100 space-y-3">
      <!-- Top row: Faculty tabs + actions -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <label class="text-sm font-medium text-gray-600 whitespace-nowrap">{{ t('academic.faculty') }}:</label>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="fac in facultiesTree"
              :key="fac.name"
              @click="selectFaculty(fac.name)"
              :class="[
                'rounded-lg px-3 py-1.5 text-sm font-medium transition-all border',
                selectedFaculty === fac.name
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                  : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
              ]"
            >
              {{ fac.name }}
              <span class="ml-1 text-xs opacity-70">({{ fac.groups_count }})</span>
            </button>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button @click="loadSchedule" :disabled="selectedGroupIds.length === 0" class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50">
            <RefreshCw :size="14" />
            {{ t('academic.load') }}
          </button>
          <button @click="showAddModal = true" class="rounded-xl bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 transition-colors flex items-center gap-2">
            <Plus :size="14" />
            {{ t('academic.addLesson') }}
          </button>
          <button @click="$router.push('/academic/ai-generate')" class="rounded-xl bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 transition-colors flex items-center gap-2">
            <Brain :size="14" />
            AI
          </button>
        </div>
      </div>

      <!-- Direction → Group filter (shows when faculty selected) -->
      <div v-if="selectedFaculty && currentFacultyData" class="border-t border-gray-100 pt-3">
        <div class="flex flex-wrap items-start gap-4">
          <!-- Direction selector -->
          <div class="min-w-[200px]">
            <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.direction') }}:</label>
            <div class="space-y-1 max-h-[160px] overflow-y-auto pr-1">
              <label
                v-for="dir in currentFacultyData.directions"
                :key="dir.name"
                class="flex items-center gap-2 rounded-lg px-2 py-1.5 cursor-pointer transition-colors text-sm"
                :class="selectedDirections.includes(dir.name) ? 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200' : 'hover:bg-gray-50 text-gray-700'"
              >
                <input
                  type="checkbox"
                  :value="dir.name"
                  v-model="selectedDirections"
                  class="rounded text-emerald-600 focus:ring-emerald-500 h-3.5 w-3.5"
                />
                <span class="truncate flex-1">{{ dir.name }}</span>
                <span class="text-xs text-gray-400 flex-shrink-0">{{ dir.groups_count }}</span>
              </label>
            </div>
            <button 
              v-if="currentFacultyData.directions.length > 1"
              @click="toggleAllDirections" 
              class="mt-1.5 text-xs text-emerald-600 hover:text-emerald-700 font-medium"
            >
              {{ allDirectionsSelected ? t('academic.deselectAll') : t('academic.selectAll') }}
            </button>
          </div>

          <!-- Group selector (shows groups from selected directions) -->
          <div class="flex-1 min-w-[300px]">
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs font-medium text-gray-500">{{ t('academic.groups') }}:</label>
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-400">
                  {{ selectedGroupIds.length }} / {{ filteredGroups.length }} {{ t('academic.selected') }}
                </span>
                <button 
                  v-if="filteredGroups.length > 0"
                  @click="toggleAllGroups" 
                  class="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
                >
                  {{ allGroupsSelected ? t('academic.deselectAll') : t('academic.selectAll') }}
                </button>
              </div>
            </div>
            <div class="flex flex-wrap gap-1.5 max-h-[160px] overflow-y-auto p-1">
              <label
                v-for="g in filteredGroups"
                :key="g.id"
                class="flex items-center gap-1.5 rounded-lg border px-2 py-1 cursor-pointer transition-all text-xs"
                :class="selectedGroupIds.includes(g.id) 
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-800 shadow-sm' 
                  : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'"
              >
                <input
                  type="checkbox"
                  :value="g.id"
                  v-model="selectedGroupIds"
                  class="rounded text-emerald-600 focus:ring-emerald-500 h-3 w-3"
                />
                <span class="font-medium">{{ g.name }}</span>
                <span class="text-gray-400">({{ g.students_count }})</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="28" class="animate-spin text-blue-500" />
    </div>

    <!-- Google Sheets-like grid -->
    <div v-else-if="groups.length > 0" class="rounded-2xl bg-white shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full border-collapse min-w-[800px]">
          <!-- Header: day/para | Group1 | Group2 | ... -->
          <thead>
            <tr class="bg-green-600 text-white">
              <th class="border border-green-700 px-2 py-2 text-xs font-bold text-center w-[50px]"></th>
              <th class="border border-green-700 px-2 py-2 text-xs font-bold text-center w-[60px]">{{ t('academic.para') }}</th>
              <th class="border border-green-700 px-2 py-2 text-xs font-bold text-center w-[90px]">{{ t('academic.time') }}</th>
              <th 
                v-for="g in groups" 
                :key="g.id"
                class="border border-green-700 px-2 py-2 text-xs font-bold text-center min-w-[160px]"
              >
                {{ g.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="day in weekDays" :key="day.value">
              <!-- Day rows with paras -->
              <tr v-for="(para, pIdx) in paras" :key="`${day.value}_${para.number}`">
                <!-- Day name cell (merged) -->
                <td 
                  v-if="pIdx === 0"
                  :rowspan="paras.length"
                  class="border border-gray-300 px-1 py-1 text-center font-bold text-sm writing-vertical"
                  :style="{ backgroundColor: day.color }"
                >
                  <div class="transform -rotate-0 whitespace-nowrap font-bold text-sm">
                    {{ day.label }}
                  </div>
                </td>
                <!-- Para number -->
                <td class="border border-gray-300 px-2 py-1 text-center text-sm font-bold bg-gray-50">
                  {{ para.number }}
                </td>
                <!-- Time -->
                <td class="border border-gray-300 px-1 py-1 text-center text-xs bg-gray-50 whitespace-nowrap">
                  {{ para.time }}
                </td>
                <!-- Cells for each group -->
                <td
                  v-for="g in groups"
                  :key="`${day.value}_${para.number}_${g.id}`"
                  class="border border-gray-300 px-1 py-1 text-center cursor-pointer hover:bg-blue-50 transition-colors relative group/cell"
                  :style="getCellStyle(day.value, para.number, g.id)"
                  @click="onCellClick(day.value, para.number, g.id)"
                  @dblclick="onCellDblClick(day.value, para.number, g.id)"
                >
                  <div v-if="getCell(day.value, para.number, g.id)" class="min-h-[50px] flex flex-col items-center justify-center gap-0.5 px-1">
                    <span class="text-xs font-semibold leading-tight text-center">
                      {{ getCell(day.value, para.number, g.id).subject }}
                    </span>
                    <span class="text-[10px] text-gray-600 leading-tight">
                      ({{ getScheduleTypeLabel(getCell(day.value, para.number, g.id).schedule_type) }})
                      {{ getCell(day.value, para.number, g.id).teacher_name || '' }}
                    </span>
                    <span class="text-[10px] text-gray-500 leading-tight">
                      {{ getCell(day.value, para.number, g.id).room || '' }}
                      {{ getCell(day.value, para.number, g.id).building ? getCell(day.value, para.number, g.id).building : '' }}
                    </span>
                    <!-- Delete button on hover -->
                    <button
                      @click.stop="deleteSchedule(getCell(day.value, para.number, g.id).id)"
                      class="absolute top-0.5 right-0.5 hidden group-hover/cell:flex h-5 w-5 items-center justify-center rounded bg-red-500 text-white hover:bg-red-600"
                    >
                      <X :size="10" />
                    </button>
                  </div>
                  <div v-else class="min-h-[50px] flex items-center justify-center">
                    <Plus :size="14" class="text-gray-300 opacity-0 group-hover/cell:opacity-100 transition-opacity" />
                  </div>
                </td>
              </tr>
              <!-- Spacer between days -->
              <tr v-if="day.value !== 'saturday'" class="h-1 bg-gray-200">
                <td :colspan="3 + groups.length"></td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- No groups selected -->
    <div v-else class="flex flex-col items-center justify-center py-16 text-gray-400">
      <Table2 :size="48" class="mb-3 opacity-50" />
      <p class="text-sm">{{ t('academic.selectGroupsToView') }}</p>
    </div>

    <!-- Add/Edit Modal -->
    <Transition name="fade">
      <div v-if="showAddModal || showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="closeModal">
        <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            {{ showEditModal ? t('academic.editLesson') : t('academic.addLesson') }}
          </h3>
          
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.group') }}</label>
                <select v-model="form.group_id" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm">
                  <option v-for="g in allGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.dayOfWeek') }}</label>
                <select v-model="form.day_of_week" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm">
                  <option v-for="d in weekDays" :key="d.value" :value="d.value">{{ d.label }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.subject') }}</label>
              <input v-model="form.subject" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm" :placeholder="t('academic.subjectPlaceholder')" />
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.type') }}</label>
                <select v-model="form.schedule_type" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm">
                  <option value="lecture">{{ t('academic.lecture') }}</option>
                  <option value="practice">{{ t('academic.practice') }}</option>
                  <option value="lab">{{ t('academic.lab') }}</option>
                  <option value="seminar">{{ t('academic.seminar') }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.para') }}</label>
                <select v-model="form.lesson_number" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm">
                  <option v-for="p in paras" :key="p.number" :value="p.number">{{ p.number }}-para ({{ p.time }})</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.color') }}</label>
                <input v-model="form.color" type="color" class="w-full h-[38px] rounded-xl border border-gray-200 px-1 py-1" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.teacher') }}</label>
                <div v-if="!manualTeacherInput" class="space-y-1">
                  <select 
                    v-model="form.teacher_id" 
                    @change="onTeacherSelect"
                    class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm"
                  >
                    <option :value="null">{{ t('academic.selectTeacher') }}</option>
                    <option v-for="teacher in teachersList" :key="teacher.id" :value="teacher.id">
                      {{ teacher.name }}
                    </option>
                  </select>
                  <button type="button" @click="manualTeacherInput = true" class="text-xs text-blue-500 hover:text-blue-700">
                    {{ t('academic.enterManually') }}
                  </button>
                </div>
                <div v-else class="space-y-1">
                  <input v-model="form.teacher_name" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm" :placeholder="t('academic.teacherPlaceholder')" />
                  <button type="button" @click="manualTeacherInput = false; form.teacher_name = ''" class="text-xs text-blue-500 hover:text-blue-700">
                    {{ t('academic.selectFromList') }}
                  </button>
                </div>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.room') }}</label>
                <input v-model="form.room" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm" placeholder="402-xona A bino" />
              </div>
            </div>

            <div>
              <label class="text-xs font-medium text-gray-500 mb-1 block">{{ t('academic.building') }}</label>
              <input v-model="form.building" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm" placeholder="A bino" />
            </div>

            <!-- Multi-group linking (for lecture and seminar) -->
            <div v-if="(form.schedule_type === 'lecture' || form.schedule_type === 'seminar') && !editingId" class="rounded-xl border-2 border-dashed border-orange-300 bg-orange-50 p-3">
              <div class="flex items-center gap-2 mb-2">
                <input type="checkbox" v-model="linkToMultipleGroups" id="linkGroupsCheck" class="rounded text-orange-500 focus:ring-orange-500" />
                <label for="linkGroupsCheck" class="text-sm font-medium text-orange-700 cursor-pointer">
                  {{ t('academic.linkToOtherGroups') }}
                </label>
              </div>
              <p class="text-xs text-orange-600 mb-2">{{ t('academic.linkGroupsHint') }}</p>
              
              <div v-if="linkToMultipleGroups" class="space-y-1.5 max-h-[180px] overflow-y-auto">
                <label 
                  v-for="g in otherGroupsForLink" 
                  :key="g.id" 
                  class="flex items-center gap-2 p-2 rounded-lg hover:bg-orange-100 cursor-pointer transition-colors"
                  :class="linkedGroupIds.includes(g.id) ? 'bg-orange-100 ring-1 ring-orange-300' : ''"
                >
                  <input 
                    type="checkbox" 
                    :value="g.id" 
                    v-model="linkedGroupIds" 
                    :disabled="!linkedGroupIds.includes(g.id) && linkedGroupIds.length >= 4"
                    class="rounded text-orange-500 focus:ring-orange-500"
                  />
                  <span class="text-sm font-medium text-gray-700">{{ g.name }}</span>
                  <span v-if="g.faculty" class="text-xs text-gray-400 ml-auto">{{ g.faculty }}</span>
                </label>
                <p v-if="linkedGroupIds.length >= 4" class="text-xs text-orange-500 font-medium pt-1">{{ t('academic.maxGroupsReached') }}</p>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-5">
            <button @click="closeModal" class="rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-200">
              {{ t('common.cancel') }}
            </button>
            <button 
              @click="saveSchedule" 
              :disabled="saving"
              class="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Loader2 v-if="saving" :size="14" class="animate-spin" />
              <span v-if="linkToMultipleGroups && linkedGroupIds.length > 0">
                {{ t('academic.saveToGroups', { count: linkedGroupIds.length + 1 }) }}
              </span>
              <span v-else>{{ t('common.save') }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { Brain, Loader2, Plus, RefreshCw, Table2, X } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const route = useRoute()

const { t } = useLanguageStore()

const loading = ref(false)
const saving = ref(false)
const toast = ref(null)

const allGroups = ref([])
const groups = ref([])
const selectedGroupIds = ref([])
const scheduleGrid = ref({})
const scheduleItems = ref([])

// Hierarchical filter state
const facultiesTree = ref([])
const selectedFaculty = ref(null)
const selectedDirections = ref([])

const showAddModal = ref(false)
const showEditModal = ref(false)
const editingId = ref(null)

// Lecture multi-group linking
const linkToMultipleGroups = ref(false)
const linkedGroupIds = ref([])

// Teachers list from API
const teachersList = ref([])
const manualTeacherInput = ref(false)

// Other groups (excluding current form.group_id) for linking
const otherGroupsForLink = computed(() => {
  return allGroups.value.filter(g => g.id !== form.group_id)
})

// ===== Hierarchical filter computed =====
const currentFacultyData = computed(() => {
  if (!selectedFaculty.value) return null
  return facultiesTree.value.find(f => f.name === selectedFaculty.value) || null
})

const allDirectionsSelected = computed(() => {
  if (!currentFacultyData.value) return false
  return currentFacultyData.value.directions.every(d => selectedDirections.value.includes(d.name))
})

const filteredGroups = computed(() => {
  if (!currentFacultyData.value || selectedDirections.value.length === 0) return []
  const groups = []
  for (const dir of currentFacultyData.value.directions) {
    if (selectedDirections.value.includes(dir.name)) {
      groups.push(...dir.groups)
    }
  }
  return groups.sort((a, b) => a.name.localeCompare(b.name))
})

const allGroupsSelected = computed(() => {
  if (filteredGroups.value.length === 0) return false
  return filteredGroups.value.every(g => selectedGroupIds.value.includes(g.id))
})

function selectFaculty(facultyName) {
  if (selectedFaculty.value === facultyName) return
  selectedFaculty.value = facultyName
  selectedDirections.value = []
  selectedGroupIds.value = []
  // Auto-select all directions
  if (currentFacultyData.value) {
    selectedDirections.value = currentFacultyData.value.directions.map(d => d.name)
  }
}

function toggleAllDirections() {
  if (!currentFacultyData.value) return
  if (allDirectionsSelected.value) {
    selectedDirections.value = []
    selectedGroupIds.value = []
  } else {
    selectedDirections.value = currentFacultyData.value.directions.map(d => d.name)
  }
}

function toggleAllGroups() {
  if (allGroupsSelected.value) {
    // Deselect all filtered groups
    const filteredIds = new Set(filteredGroups.value.map(g => g.id))
    selectedGroupIds.value = selectedGroupIds.value.filter(id => !filteredIds.has(id))
  } else {
    // Select all filtered groups
    const existing = new Set(selectedGroupIds.value)
    for (const g of filteredGroups.value) {
      existing.add(g.id)
    }
    selectedGroupIds.value = [...existing]
  }
}

const form = reactive({
  group_id: null,
  subject: '',
  subject_code: '',
  schedule_type: 'lecture',
  day_of_week: 'monday',
  lesson_number: 1,
  start_time: '08:30',
  end_time: '09:50',
  room: '',
  building: '',
  teacher_name: '',
  teacher_id: null,
  color: '#E3F2FD',
})

const weekDays = [
  { value: 'monday', label: 'Dushanba', color: '#E3F2FD' },
  { value: 'tuesday', label: 'Seshanba', color: '#FFF3E0' },
  { value: 'wednesday', label: 'Chorshanba', color: '#E8F5E9' },
  { value: 'thursday', label: 'Payshanba', color: '#FCE4EC' },
  { value: 'friday', label: 'Juma', color: '#F3E5F5' },
  { value: 'saturday', label: 'Shanba', color: '#E0F7FA' },
]

const paras = [
  { number: 1, time: '08:30-09:50', start: '08:30', end: '09:50' },
  { number: 2, time: '10:00-11:20', start: '10:00', end: '11:20' },
  { number: 3, time: '12:00-13:20', start: '12:00', end: '13:20' },
  { number: 4, time: '13:30-14:50', start: '13:30', end: '14:50' },
  { number: 5, time: '15:00-16:20', start: '15:00', end: '16:20' },
]

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const onTeacherSelect = () => {
  const teacher = teachersList.value.find(t => t.id === form.teacher_id)
  if (teacher) {
    form.teacher_name = teacher.name
  }
}

const loadTeachers = async () => {
  try {
    const res = await api.request('/academic/teachers')
    teachersList.value = res.items || []
  } catch (e) {
    console.error('Failed to load teachers:', e)
  }
}

const getCell = (day, lessonNumber, groupId) => {
  const key = `${day}_${lessonNumber}_${groupId}`
  return scheduleGrid.value[key] || null
}

const getCellStyle = (day, lessonNumber, groupId) => {
  const cell = getCell(day, lessonNumber, groupId)
  if (cell && cell.color) {
    return { backgroundColor: cell.color }
  }
  return {}
}

const getScheduleTypeLabel = (type) => {
  const map = {
    lecture: "ma'ruza",
    practice: 'amaliy',
    lab: 'lab',
    seminar: 'seminar',
  }
  return map[type] || type
}

const onCellClick = (day, lessonNumber, groupId) => {
  const cell = getCell(day, lessonNumber, groupId)
  if (cell) {
    // Edit
    editingId.value = cell.id
    Object.assign(form, {
      group_id: cell.group_id,
      subject: cell.subject,
      subject_code: cell.subject_code || '',
      schedule_type: cell.schedule_type || 'lecture',
      day_of_week: cell.day_of_week,
      lesson_number: cell.lesson_number,
      start_time: cell.start_time || '08:30',
      end_time: cell.end_time || '09:50',
      room: cell.room || '',
      building: cell.building || '',
      teacher_name: cell.teacher_name || '',
      teacher_id: cell.teacher_id,
      color: cell.color || '#E3F2FD',
    })
    // If teacher_id exists and is in our list, use select mode; otherwise manual
    if (cell.teacher_id && teachersList.value.some(t => t.id === cell.teacher_id)) {
      manualTeacherInput.value = false
    } else if (cell.teacher_name) {
      manualTeacherInput.value = true
    } else {
      manualTeacherInput.value = false
    }
    showEditModal.value = true
  }
}

const onCellDblClick = (day, lessonNumber, groupId) => {
  const cell = getCell(day, lessonNumber, groupId)
  if (!cell) {
    // Add new
    const para = paras.find(p => p.number === lessonNumber)
    Object.assign(form, {
      group_id: groupId,
      subject: '',
      subject_code: '',
      schedule_type: 'lecture',
      day_of_week: day,
      lesson_number: lessonNumber,
      start_time: para?.start || '08:30',
      end_time: para?.end || '09:50',
      room: '',
      building: '',
      teacher_name: '',
      teacher_id: null,
      color: '#E3F2FD',
    })
    editingId.value = null
    showAddModal.value = true
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingId.value = null
  linkToMultipleGroups.value = false
  linkedGroupIds.value = []
  manualTeacherInput.value = false
}

const loadGroups = async () => {
  try {
    const res = await api.request('/academic/groups')
    allGroups.value = res.items || []
  } catch (e) {
    console.error(e)
  }
}

const loadFacultiesTree = async () => {
  try {
    const res = await api.request('/academic/faculties-tree')
    facultiesTree.value = res.faculties || []
  } catch (e) {
    console.error('Failed to load faculties tree:', e)
  }
}

const loadSchedule = async () => {
  if (selectedGroupIds.value.length === 0) return
  loading.value = true
  try {
    const ids = selectedGroupIds.value.join(',')
    const res = await api.request(`/academic/schedules/multi-group?group_ids=${ids}`)
    groups.value = res.groups || []
    scheduleGrid.value = res.grid || {}
    scheduleItems.value = res.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const saveSchedule = async () => {
  if (!form.subject || !form.group_id) {
    showToast(t('academic.fillRequired'), 'error')
    return
  }
  saving.value = true
  try {
    const para = paras.find(p => p.number === form.lesson_number)
    const body = {
      ...form,
      start_time: para?.start || form.start_time,
      end_time: para?.end || form.end_time,
    }
    
    if (editingId.value) {
      // Edit existing
      await api.request(`/academic/schedules/${editingId.value}`, { method: 'PUT', body })
      showToast(t('academic.scheduleUpdated'))
    } else if (linkToMultipleGroups.value && linkedGroupIds.value.length > 0 && (form.schedule_type === 'lecture' || form.schedule_type === 'seminar')) {
      // Lecture multi-group: save to current group + all linked groups
      const allGroupIds = [form.group_id, ...linkedGroupIds.value]
      const multiBody = {
        group_ids: allGroupIds,
        subject: body.subject,
        subject_code: body.subject_code,
        schedule_type: body.schedule_type,
        day_of_week: body.day_of_week,
        start_time: body.start_time,
        end_time: body.end_time,
        lesson_number: body.lesson_number,
        room: body.room,
        building: body.building,
        teacher_name: body.teacher_name,
        teacher_id: body.teacher_id,
        color: body.color,
      }
      const res = await api.request('/academic/schedules/lecture-multi', { method: 'POST', body: multiBody })
      showToast(res.message || t('academic.lectureLinkedSuccess', { count: allGroupIds.length }))
    } else {
      // Normal single create
      await api.request('/academic/schedules', { method: 'POST', body })
      showToast(t('academic.scheduleCreated'))
    }
    closeModal()
    await loadSchedule()
  } catch (e) {
    showToast(e.data?.detail || t('common.error'), 'error')
  } finally {
    saving.value = false
  }
}

const deleteSchedule = async (id) => {
  if (!confirm(t('academic.confirmDelete'))) return
  try {
    await api.request(`/academic/schedules/${id}`, { method: 'DELETE' })
    showToast(t('academic.scheduleDeleted'))
    await loadSchedule()
  } catch (e) {
    showToast(e.data?.detail || t('common.error'), 'error')
  }
}

onMounted(async () => {
  await Promise.all([loadGroups(), loadFacultiesTree(), loadTeachers()])
  
  // If ?group= query param exists, select that group
  const queryGroup = route.query.group
  if (queryGroup) {
    const gId = Number(queryGroup)
    if (gId) {
      selectedGroupIds.value = [gId]
      // Try to find and select the faculty/direction for this group
      for (const fac of facultiesTree.value) {
        for (const dir of fac.directions) {
          if (dir.groups.some(g => g.id === gId)) {
            selectedFaculty.value = fac.name
            selectedDirections.value = [dir.name]
            break
          }
        }
        if (selectedFaculty.value) break
      }
    }
  } else if (facultiesTree.value.length > 0) {
    // Auto-select first faculty and all its directions
    selectFaculty(facultiesTree.value[0].name)
    // Auto-select first 6 groups
    if (filteredGroups.value.length > 0) {
      selectedGroupIds.value = filteredGroups.value.slice(0, 6).map(g => g.id)
    }
  }
  
  if (selectedGroupIds.value.length > 0) {
    await loadSchedule()
  }
})
</script>

<style scoped>
.writing-vertical {
  writing-mode: vertical-lr;
  text-orientation: mixed;
  min-width: 30px;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
