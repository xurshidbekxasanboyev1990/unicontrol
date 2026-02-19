<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
            <DoorOpen :size="22" />
          </div>
          {{ t('rooms.title') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">{{ t('rooms.description') }}</p>
      </div>
      <button
        @click="showAddModal = true"
        class="flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-lg hover:bg-indigo-700 transition-all"
      >
        <Plus :size="16" />
        {{ t('rooms.addRoom') }}
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-100 text-indigo-600">
            <DoorOpen :size="18" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_rooms }}</p>
        <p class="text-xs text-gray-500">{{ t('rooms.totalRooms') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-green-100 text-green-600">
            <Users :size="18" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_capacity }}</p>
        <p class="text-xs text-gray-500">{{ t('rooms.totalCapacity') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-100 text-orange-600">
            <Building2 :size="18" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total_buildings }}</p>
        <p class="text-xs text-gray-500">{{ t('rooms.buildings') }}</p>
      </div>
      <div class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-100 text-purple-600">
            <Monitor :size="18" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stats.room_types?.lab || 0 }}</p>
        <p class="text-xs text-gray-500">{{ t('rooms.labRooms') }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="relative flex-1 min-w-[200px] max-w-xs">
        <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('common.search') + '...'"
          class="w-full rounded-xl border border-gray-200 bg-white py-2.5 pl-10 pr-4 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>
      <select v-model="filterBuilding" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm">
        <option value="">{{ t('rooms.allBuildings') }}</option>
        <option v-for="b in buildings" :key="b" :value="b">{{ b }}</option>
      </select>
      <select v-model="filterType" class="rounded-xl border border-gray-200 px-3 py-2.5 text-sm bg-white shadow-sm">
        <option value="">{{ t('rooms.allTypes') }}</option>
        <option value="lecture">{{ t('rooms.typeLecture') }}</option>
        <option value="lab">{{ t('rooms.typeLab') }}</option>
        <option value="computer">{{ t('rooms.typeComputer') }}</option>
        <option value="conference">{{ t('rooms.typeConference') }}</option>
        <option value="gym">{{ t('rooms.typeGym') }}</option>
        <option value="other">{{ t('rooms.typeOther') }}</option>
      </select>
      <button
        @click="viewMode = viewMode === 'grid' ? 'occupancy' : 'grid'"
        :class="[
          'flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all border',
          viewMode === 'occupancy'
            ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
            : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
        ]"
      >
        <BarChart3 :size="16" />
        {{ t('rooms.occupancy') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <Loader2 :size="32" class="animate-spin text-indigo-500" />
    </div>

    <!-- Grid view -->
    <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="room in filteredRooms"
        :key="room.id"
        class="rounded-2xl bg-white p-5 shadow-sm border border-gray-100 hover:border-indigo-200 hover:shadow-md transition-all group"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3">
            <div :class="[
              'flex h-11 w-11 items-center justify-center rounded-xl text-white font-bold text-sm',
              roomTypeColor(room.room_type)
            ]">
              <component :is="roomTypeIcon(room.room_type)" :size="20" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ room.name }}</h3>
              <p v-if="room.building" class="text-xs text-gray-500">{{ room.building }}</p>
            </div>
          </div>
          <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="editRoom(room)" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-indigo-600">
              <Pencil :size="14" />
            </button>
            <button @click="deleteRoom(room)" class="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>

        <div class="flex flex-wrap gap-2 mb-3">
          <span class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">
            {{ roomTypeName(room.room_type) }}
          </span>
          <span class="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs text-blue-600">
            <Users :size="10" class="inline mr-1" />{{ room.capacity }} {{ t('rooms.seats') }}
          </span>
        </div>

        <!-- Equipment -->
        <div class="flex flex-wrap gap-1.5">
          <span v-if="room.has_projector" class="rounded-lg bg-yellow-50 px-2 py-0.5 text-[10px] font-medium text-yellow-700">📽 {{ t('rooms.projector') }}</span>
          <span v-if="room.has_computer" class="rounded-lg bg-blue-50 px-2 py-0.5 text-[10px] font-medium text-blue-700">💻 {{ t('rooms.computer') }}</span>
          <span v-if="room.has_whiteboard" class="rounded-lg bg-green-50 px-2 py-0.5 text-[10px] font-medium text-green-700">📝 {{ t('rooms.whiteboard') }}</span>
          <span v-if="room.has_air_conditioner" class="rounded-lg bg-cyan-50 px-2 py-0.5 text-[10px] font-medium text-cyan-700">❄️ {{ t('rooms.airCon') }}</span>
        </div>
      </div>

      <div v-if="filteredRooms.length === 0" class="col-span-full flex flex-col items-center justify-center py-16 text-gray-400">
        <DoorOpen :size="48" class="mb-3 opacity-50" />
        <p class="text-sm">{{ t('rooms.noRooms') }}</p>
      </div>
    </div>

    <!-- Occupancy view -->
    <div v-else class="space-y-4">
      <div class="rounded-2xl bg-white shadow-sm border border-gray-100 overflow-hidden">
        <div class="border-b border-gray-100 bg-gray-50/50 px-5 py-3">
          <h3 class="text-sm font-semibold text-gray-700">{{ t('rooms.occupancyTitle') }}</h3>
        </div>
        <div class="p-4 space-y-3">
          <div v-for="room in occupancyData" :key="room.id" class="flex items-center gap-4">
            <div class="w-40 truncate text-sm font-medium text-gray-900">{{ room.full_name }}</div>
            <div class="flex-1">
              <div class="h-6 bg-gray-100 rounded-full overflow-hidden">
                <div
                  :class="[
                    'h-full rounded-full transition-all',
                    room.occupancy_rate > 80 ? 'bg-red-500' : room.occupancy_rate > 50 ? 'bg-yellow-500' : 'bg-green-500'
                  ]"
                  :style="{ width: room.occupancy_rate + '%' }"
                ></div>
              </div>
            </div>
            <div class="w-16 text-right text-sm font-medium" :class="[
              room.occupancy_rate > 80 ? 'text-red-600' : room.occupancy_rate > 50 ? 'text-yellow-600' : 'text-green-600'
            ]">
              {{ room.occupancy_rate }}%
            </div>
            <div class="w-20 text-right text-xs text-gray-500">{{ room.busy_slots }} {{ t('rooms.slots') }}</div>
          </div>
          <div v-if="occupancyData.length === 0" class="text-center py-8 text-gray-400 text-sm">
            {{ t('rooms.noOccupancy') }}
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Transition name="fade">
      <div v-if="showAddModal || editingRoom" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="closeModal">
        <div class="w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div class="bg-indigo-600 px-6 py-4">
            <h3 class="text-lg font-semibold text-white">
              {{ editingRoom ? t('rooms.editRoom') : t('rooms.addRoom') }}
            </h3>
          </div>
          <div class="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('rooms.roomName') }} *</label>
                <input v-model="form.name" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" placeholder="401-xona" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('rooms.buildingName') }}</label>
                <input v-model="form.building" type="text" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" placeholder="A bino" />
              </div>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('rooms.floor') }}</label>
                <input v-model.number="form.floor" type="number" min="1" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('rooms.capacity') }} *</label>
                <input v-model.number="form.capacity" type="number" min="1" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('rooms.roomType') }}</label>
                <select v-model="form.room_type" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                  <option value="lecture">{{ t('rooms.typeLecture') }}</option>
                  <option value="lab">{{ t('rooms.typeLab') }}</option>
                  <option value="computer">{{ t('rooms.typeComputer') }}</option>
                  <option value="conference">{{ t('rooms.typeConference') }}</option>
                  <option value="gym">{{ t('rooms.typeGym') }}</option>
                  <option value="other">{{ t('rooms.typeOther') }}</option>
                </select>
              </div>
            </div>
            <div>
              <label class="mb-2 block text-xs font-medium text-gray-600">{{ t('rooms.equipment') }}</label>
              <div class="flex flex-wrap gap-3">
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input v-model="form.has_projector" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  📽 {{ t('rooms.projector') }}
                </label>
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input v-model="form.has_computer" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  💻 {{ t('rooms.computer') }}
                </label>
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input v-model="form.has_whiteboard" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  📝 {{ t('rooms.whiteboard') }}
                </label>
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input v-model="form.has_air_conditioner" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  ❄️ {{ t('rooms.airCon') }}
                </label>
              </div>
            </div>
            <div>
              <label class="mb-1 block text-xs font-medium text-gray-600">{{ t('rooms.descriptionField') }}</label>
              <textarea v-model="form.description" rows="2" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" :placeholder="t('rooms.descriptionPlaceholder')"></textarea>
            </div>
          </div>
          <div class="px-6 py-4 bg-gray-50 flex items-center justify-end gap-3">
            <button @click="closeModal" class="rounded-xl px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors">
              {{ t('common.cancel') }}
            </button>
            <button
              @click="saveRoom"
              :disabled="saving || !form.name"
              class="flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-all"
            >
              <Loader2 v-if="saving" :size="16" class="animate-spin" />
              {{ t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="fade">
      <div v-if="toast" :class="['fixed bottom-6 right-6 z-50 rounded-xl px-5 py-3 text-white shadow-lg text-sm', toast.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { BarChart3, BookOpen, Building2, Cpu, DoorOpen, Dumbbell, Loader2, Monitor, Pencil, Plus, Presentation, Search, Trash2, Users } from 'lucide-vue-next'
import { computed, markRaw, onMounted, ref } from 'vue'
import api from '../../services/api'
import { useLanguageStore } from '../../stores/language'

const { t } = useLanguageStore()

const loading = ref(false)
const saving = ref(false)
const rooms = ref([])
const buildings = ref([])
const stats = ref({ total_rooms: 0, total_capacity: 0, total_buildings: 0, room_types: {} })
const occupancyData = ref([])
const searchQuery = ref('')
const filterBuilding = ref('')
const filterType = ref('')
const viewMode = ref('grid')
const showAddModal = ref(false)
const editingRoom = ref(null)
const toast = ref(null)

const defaultForm = {
  name: '', building: '', floor: null, capacity: 30, room_type: 'lecture',
  has_projector: false, has_computer: false, has_whiteboard: true, has_air_conditioner: false,
  description: '',
}
const form = ref({ ...defaultForm })

const filteredRooms = computed(() => {
  let result = rooms.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(r => r.name.toLowerCase().includes(q) || (r.building || '').toLowerCase().includes(q))
  }
  if (filterBuilding.value) {
    result = result.filter(r => r.building === filterBuilding.value)
  }
  if (filterType.value) {
    result = result.filter(r => r.room_type === filterType.value)
  }
  return result
})

const roomTypeColor = (type) => {
  const colors = {
    lecture: 'bg-blue-500', lab: 'bg-purple-500', computer: 'bg-indigo-500',
    conference: 'bg-amber-500', gym: 'bg-green-500', other: 'bg-gray-500'
  }
  return colors[type] || 'bg-gray-500'
}

const roomTypeIcon = (type) => {
  const icons = {
    lecture: markRaw(BookOpen), lab: markRaw(Monitor), computer: markRaw(Cpu),
    conference: markRaw(Presentation), gym: markRaw(Dumbbell), other: markRaw(DoorOpen)
  }
  return icons[type] || markRaw(DoorOpen)
}

const roomTypeName = (type) => {
  const names = {
    lecture: t('rooms.typeLecture'), lab: t('rooms.typeLab'), computer: t('rooms.typeComputer'),
    conference: t('rooms.typeConference'), gym: t('rooms.typeGym'), other: t('rooms.typeOther')
  }
  return names[type] || type
}

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const loadRooms = async () => {
  loading.value = true
  try {
    const [roomsRes, statsRes] = await Promise.all([
      api.request('/rooms-exams/rooms'),
      api.request('/rooms-exams/rooms/stats/summary'),
    ])
    rooms.value = roomsRes.items || []
    buildings.value = roomsRes.buildings || []
    stats.value = statsRes
  } catch (e) {
    console.error('Load rooms error:', e)
  } finally {
    loading.value = false
  }
}

const loadOccupancy = async () => {
  try {
    const res = await api.request('/rooms-exams/rooms/occupancy')
    occupancyData.value = (res.items || []).sort((a, b) => b.occupancy_rate - a.occupancy_rate)
  } catch (e) {
    console.error('Load occupancy error:', e)
  }
}

const editRoom = (room) => {
  editingRoom.value = room
  form.value = {
    name: room.name, building: room.building || '', floor: room.floor,
    capacity: room.capacity, room_type: room.room_type,
    has_projector: room.has_projector, has_computer: room.has_computer,
    has_whiteboard: room.has_whiteboard, has_air_conditioner: room.has_air_conditioner,
    description: room.description || '',
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingRoom.value = null
  form.value = { ...defaultForm }
}

const saveRoom = async () => {
  if (!form.value.name) return
  saving.value = true
  try {
    if (editingRoom.value) {
      await api.request(`/rooms-exams/rooms/${editingRoom.value.id}`, { method: 'PUT', body: form.value })
      showToast(t('rooms.roomUpdated'))
    } else {
      await api.request('/rooms-exams/rooms', { method: 'POST', body: form.value })
      showToast(t('rooms.roomCreated'))
    }
    closeModal()
    await loadRooms()
  } catch (e) {
    showToast(e.message || 'Xatolik', 'error')
  } finally {
    saving.value = false
  }
}

const deleteRoom = async (room) => {
  if (!confirm(`"${room.name}" ${t('rooms.confirmDelete')}`)) return
  try {
    await api.request(`/rooms-exams/rooms/${room.id}`, { method: 'DELETE' })
    showToast(t('rooms.roomDeleted'))
    await loadRooms()
  } catch (e) {
    showToast(e.message || 'Xatolik', 'error')
  }
}

onMounted(async () => {
  await loadRooms()
  await loadOccupancy()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
