<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-3xl p-6 md:p-8 text-white relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
      <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <GraduationCap class="w-8 h-8" />
            <span class="text-sm font-medium opacity-90">Boshqaruv</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-bold">Yo'nalishlar va Fanlar</h1>
          <p class="text-white/80 mt-2">Yo'nalishlarni boshqarish va ularga fanlarni biriktirish</p>
        </div>
        <button
          @click="openCreateDirectionModal"
          class="flex items-center gap-2 px-5 py-3 bg-white/20 hover:bg-white/30 backdrop-blur rounded-xl font-semibold transition-all hover:scale-105"
        >
          <Plus class="w-5 h-5" />
          Yangi yo'nalish
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <GraduationCap class="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ activeDirections.length }}</p>
            <p class="text-sm text-slate-500">Faol yo'nalishlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <BookOpen class="w-6 h-6 text-emerald-500" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ dataStore.subjects.length }}</p>
            <p class="text-sm text-slate-500">Jami fanlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <Link2 class="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ totalLinks }}</p>
            <p class="text-sm text-slate-500">Bog'lanishlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-lg transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <Trophy class="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ subjectBasedTournaments }}</p>
            <p class="text-sm text-slate-500">Fan turnirlari</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Directions List -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="p-5 border-b border-slate-100">
        <h2 class="font-bold text-lg text-slate-800">Yo'nalishlar ro'yxati</h2>
        <p class="text-sm text-slate-500 mt-1">Yo'nalishni tanlang va unga fanlar belgilang</p>
      </div>

      <div class="divide-y divide-slate-100">
        <div
          v-for="direction in dataStore.directions"
          :key="direction.id"
          class="p-5 hover:bg-slate-50 transition-colors"
        >
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <!-- Direction Info -->
            <div class="flex items-center gap-4 flex-1">
              <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg shrink-0">
                {{ direction.code }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <h3 class="font-bold text-slate-800 text-lg">{{ direction.name }}</h3>
                  <span :class="[
                    'px-2 py-0.5 text-xs font-medium rounded-full',
                    direction.isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'
                  ]">
                    {{ direction.isActive ? 'Faol' : 'Nofaol' }}
                  </span>
                </div>
                <p class="text-sm text-slate-500">{{ direction.faculty }}</p>
                
                <!-- Assigned Subjects Preview -->
                <div class="flex flex-wrap items-center gap-2 mt-2">
                  <template v-if="getDirectionSubjects(direction.id).length > 0">
                    <div
                      v-for="subject in getDirectionSubjects(direction.id).slice(0, 4)"
                      :key="subject.id"
                      class="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-lg text-xs font-medium text-slate-600"
                    >
                      <component :is="getSubjectIcon(subject.icon)" class="w-3.5 h-3.5" />
                      {{ subject.name }}
                    </div>
                    <span v-if="getDirectionSubjects(direction.id).length > 4" class="text-xs text-slate-400">
                      +{{ getDirectionSubjects(direction.id).length - 4 }} ta
                    </span>
                  </template>
                  <span v-else class="text-xs text-slate-400 italic">Fanlar belgilanmagan</span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 shrink-0">
              <button
                @click="openDirectionSubjectsModal(direction)"
                class="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all flex items-center gap-2"
              >
                <BookOpen class="w-4 h-4" />
                Fanlar ({{ getDirectionSubjects(direction.id).length }})
              </button>
              <button
                @click="editDirection(direction)"
                class="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl transition-colors"
                title="Tahrirlash"
              >
                <Pencil class="w-4 h-4" />
              </button>
              <button
                @click="toggleDirectionStatus(direction)"
                :class="[
                  'p-2.5 rounded-xl transition-colors',
                  direction.isActive ? 'bg-amber-100 text-amber-600 hover:bg-amber-200' : 'bg-emerald-100 text-emerald-600 hover:bg-emerald-200'
                ]"
                :title="direction.isActive ? 'O\'chirish' : 'Yoqish'"
              >
                <Power class="w-4 h-4" />
              </button>
              <button
                @click="confirmDeleteDirection(direction)"
                class="p-2.5 bg-rose-100 text-rose-600 hover:bg-rose-200 rounded-xl transition-colors"
                title="O'chirish"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="dataStore.directions.length === 0" class="p-16 text-center">
        <GraduationCap class="w-16 h-16 mx-auto text-slate-300 mb-4" />
        <h3 class="text-lg font-semibold text-slate-600">Yo'nalishlar yo'q</h3>
        <p class="text-slate-400 mt-1">Yangi yo'nalish qo'shish uchun yuqoridagi tugmani bosing</p>
      </div>
    </div>

    <!-- Create/Edit Direction Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDirectionModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showDirectionModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden">
            <div class="bg-gradient-to-r from-blue-500 to-indigo-500 p-6 text-white">
              <h3 class="text-xl font-bold">{{ isEditingDirection ? 'Yo\'nalishni tahrirlash' : 'Yangi yo\'nalish' }}</h3>
              <p class="text-white/80 text-sm mt-1">Yo'nalish ma'lumotlarini kiriting</p>
            </div>

            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Yo'nalish nomi *</label>
                <input
                  v-model="directionForm.name"
                  type="text"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  placeholder="Masalan: Kompyuter injiniringi"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Qisqa kod *</label>
                <input
                  v-model="directionForm.code"
                  type="text"
                  maxlength="4"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 uppercase"
                  placeholder="Masalan: KI"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">Fakultet</label>
                <input
                  v-model="directionForm.faculty"
                  type="text"
                  class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  placeholder="Masalan: Axborot texnologiyalari fakulteti"
                />
              </div>
            </div>

            <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-100 bg-slate-50">
              <button
                @click="showDirectionModal = false"
                class="px-5 py-2.5 text-slate-600 hover:bg-slate-200 rounded-xl font-medium transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="saveDirection"
                class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                {{ isEditingDirection ? 'Saqlash' : 'Qo\'shish' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Direction Subjects Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showSubjectsModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showSubjectsModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <!-- Header -->
            <div class="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 text-white shrink-0">
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center font-bold text-xl">
                  {{ selectedDirection?.code }}
                </div>
                <div>
                  <h3 class="text-xl font-bold">{{ selectedDirection?.name }}</h3>
                  <p class="text-white/80 text-sm mt-1">Fanlarni belgilang va yangi fan qo'shing</p>
                </div>
              </div>
            </div>

            <!-- Body -->
            <div class="p-6 overflow-y-auto flex-1 space-y-6">
              <!-- Info -->
              <div class="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <div class="flex items-start gap-3">
                  <Info class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-sm font-medium text-blue-700">Qanday ishlaydi?</p>
                    <p class="text-xs text-blue-600 mt-1">
                      Bu yo'nalishdagi talabalar faqat belgilangan fanlar bo'yicha bellashuvlarda qatnashishi mumkin.
                      Masalan: 2 ta fan tanlasangiz, talaba ulardan birini tanlashi mumkin.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Add new subject -->
              <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <p class="text-sm font-medium text-slate-700 mb-3 flex items-center gap-2">
                  <Plus class="w-4 h-4" />
                  Yangi fan qo'shish
                </p>
                <div class="flex gap-3">
                  <input
                    v-model="newSubjectName"
                    type="text"
                    class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    placeholder="Fan nomini kiriting..."
                    @keyup.enter="addNewSubject"
                  />
                  <select
                    v-model="newSubjectIcon"
                    class="px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  >
                    <option v-for="icon in availableIcons" :key="icon.value" :value="icon.value">
                      {{ icon.label }}
                    </option>
                  </select>
                  <button
                    @click="addNewSubject"
                    class="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-semibold transition-colors flex items-center gap-2"
                  >
                    <Plus class="w-4 h-4" />
                    Qo'shish
                  </button>
                </div>
              </div>

              <!-- Subjects list -->
              <div>
                <p class="text-sm font-medium text-slate-700 mb-3">
                  Fanlarni tanlang 
                  <span class="text-emerald-600">({{ selectedSubjectIds.length }} ta tanlangan)</span>
                </p>
                
                <div class="grid grid-cols-2 gap-2">
                  <label
                    v-for="subject in dataStore.subjects"
                    :key="subject.id"
                    :class="[
                      'flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all border-2',
                      selectedSubjectIds.includes(subject.id)
                        ? 'bg-emerald-50 border-emerald-300'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    ]"
                  >
                    <input
                      type="checkbox"
                      :value="subject.id"
                      v-model="selectedSubjectIds"
                      class="w-4 h-4 text-emerald-500 rounded focus:ring-emerald-500"
                    />
                    <div :class="[
                      'w-8 h-8 rounded-lg flex items-center justify-center',
                      `bg-${subject.color}-100`
                    ]">
                      <component :is="getSubjectIcon(subject.icon)" :class="`w-4 h-4 text-${subject.color}-500`" />
                    </div>
                    <span class="text-sm font-medium text-slate-700 flex-1">{{ subject.name }}</span>
                    <button
                      @click.prevent="confirmDeleteSubject(subject)"
                      class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                      title="O'chirish"
                    >
                      <X class="w-4 h-4" />
                    </button>
                  </label>
                </div>

                <div v-if="dataStore.subjects.length === 0" class="text-center py-8 text-slate-400">
                  <BookOpen class="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Hali fanlar yo'q. Yuqorida yangi fan qo'shing.</p>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-100 bg-slate-50 shrink-0">
              <button
                @click="showSubjectsModal = false"
                class="px-5 py-2.5 text-slate-600 hover:bg-slate-200 rounded-xl font-medium transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="saveDirectionSubjects"
                class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
              >
                <Check class="w-5 h-5" />
                Saqlash
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Direction Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDeleteDirectionModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showDeleteDirectionModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-sm p-6 text-center">
            <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Trash2 class="w-8 h-8 text-rose-500" />
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-2">Yo'nalishni o'chirish</h3>
            <p class="text-slate-500 mb-6">
              "{{ directionToDelete?.name }}" yo'nalishini o'chirishni xohlaysizmi?
            </p>
            <div class="flex gap-3">
              <button
                @click="showDeleteDirectionModal = false"
                class="flex-1 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="deleteDirection"
                class="flex-1 px-5 py-2.5 bg-rose-500 hover:bg-rose-600 text-white rounded-xl font-semibold transition-colors"
              >
                O'chirish
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Subject Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDeleteSubjectModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showDeleteSubjectModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-sm p-6 text-center">
            <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Trash2 class="w-8 h-8 text-rose-500" />
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-2">Fanni o'chirish</h3>
            <p class="text-slate-500 mb-6">
              "{{ subjectToDelete?.name }}" fanini o'chirishni xohlaysizmi?
            </p>
            <div class="flex gap-3">
              <button
                @click="showDeleteSubjectModal = false"
                class="flex-1 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="deleteSubject"
                class="flex-1 px-5 py-2.5 bg-rose-500 hover:bg-rose-600 text-white rounded-xl font-semibold transition-colors"
              >
                O'chirish
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  GraduationCap, BookOpen, Plus, Pencil, Trash2, Power, Link2, Trophy,
  Check, X, Info, Loader2,
  // Subject icons
  Monitor, Calculator, Atom, FlaskConical, Leaf, Scale, BookText, Globe2,
  Languages, Heart, Banknote, Cpu, Code, Microscope, Palette, Music
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

// Loading
const loading = ref(true)
const saving = ref(false)

// Modals
const showDirectionModal = ref(false)
const showSubjectsModal = ref(false)
const showDeleteDirectionModal = ref(false)
const showDeleteSubjectModal = ref(false)

// State
const isEditingDirection = ref(false)
const selectedDirection = ref(null)
const selectedSubjectIds = ref([])
const directionToDelete = ref(null)
const subjectToDelete = ref(null)
const newSubjectName = ref('')
const newSubjectIcon = ref('BookOpen')

// Forms
const directionForm = ref({
  name: '',
  code: '',
  faculty: ''
})

// Load data on mount
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      dataStore.fetchDirections(),
      dataStore.fetchSubjects(),
      dataStore.fetchTournaments()
    ])
  } catch (err) {
    console.error('Error loading data:', err)
    toast.error('Ma\'lumotlarni yuklashda xatolik')
  } finally {
    loading.value = false
  }
})

// Available icons for subjects
const availableIcons = [
  { value: 'Monitor', label: 'Kompyuter' },
  { value: 'Code', label: 'Dasturlash' },
  { value: 'Calculator', label: 'Matematika' },
  { value: 'Atom', label: 'Fizika' },
  { value: 'FlaskConical', label: 'Kimyo' },
  { value: 'Leaf', label: 'Biologiya' },
  { value: 'Microscope', label: 'Tibbiyot' },
  { value: 'Scale', label: 'Huquq' },
  { value: 'Banknote', label: 'Iqtisod' },
  { value: 'BookText', label: 'Adabiyot' },
  { value: 'Globe2', label: 'Geografiya' },
  { value: 'Languages', label: 'Tillar' },
  { value: 'Heart', label: 'Psixologiya' },
  { value: 'Palette', label: 'San\'at' },
  { value: 'Music', label: 'Musiqa' },
  { value: 'Cpu', label: 'Texnika' },
  { value: 'BookOpen', label: 'Boshqa' }
]

// Icon component mapping
const iconComponents = {
  Monitor, Calculator, Atom, FlaskConical, Leaf, Scale, BookText, Globe2,
  Languages, Heart, Banknote, Cpu, Code, Microscope, Palette, Music, BookOpen
}

const getSubjectIcon = (iconName) => {
  return iconComponents[iconName] || BookOpen
}

// Computed
const activeDirections = computed(() => dataStore.directions.filter(d => d.isActive))

const totalLinks = computed(() => {
  return dataStore.directionSubjects.reduce((sum, ds) => sum + ds.subjectIds.length, 0)
})

const subjectBasedTournaments = computed(() => {
  return dataStore.tournaments.filter(t => t.isSubjectBased).length
})

// Get subjects for a direction
const getDirectionSubjects = (directionId) => {
  const ds = dataStore.directionSubjects.find(ds => ds.directionId === directionId)
  if (!ds) return []
  return dataStore.subjects.filter(s => ds.subjectIds.includes(s.id))
}

// Direction CRUD
const openCreateDirectionModal = () => {
  isEditingDirection.value = false
  directionForm.value = { name: '', code: '', faculty: '' }
  showDirectionModal.value = true
}

const editDirection = (direction) => {
  isEditingDirection.value = true
  directionForm.value = { ...direction }
  showDirectionModal.value = true
}

const saveDirection = async () => {
  if (!directionForm.value.name.trim() || !directionForm.value.code.trim()) {
    toast.error('Nom va kodni kiriting')
    return
  }

  saving.value = true
  try {
    if (isEditingDirection.value) {
      await dataStore.updateDirection(directionForm.value.id, directionForm.value)
      toast.success('Yo\'nalish yangilandi')
    } else {
      await dataStore.addDirection(directionForm.value)
      toast.success('Yangi yo\'nalish qo\'shildi')
    }
    showDirectionModal.value = false
  } catch (err) {
    console.error('Error saving direction:', err)
    toast.error('Yo\'nalishni saqlashda xatolik')
  } finally {
    saving.value = false
  }
}

const toggleDirectionStatus = async (direction) => {
  try {
    await dataStore.toggleDirectionStatus(direction.id)
    toast.success(direction.isActive ? 'Yo\'nalish o\'chirildi' : 'Yo\'nalish yoqildi')
  } catch (err) {
    console.error('Error toggling direction status:', err)
    toast.error('Statusni o\'zgartirishda xatolik')
  }
}

const confirmDeleteDirection = (direction) => {
  directionToDelete.value = direction
  showDeleteDirectionModal.value = true
}

const deleteDirection = async () => {
  try {
    await dataStore.deleteDirection(directionToDelete.value.id)
    toast.success('Yo\'nalish o\'chirildi')
  } catch (err) {
    console.error('Error deleting direction:', err)
    toast.error('Yo\'nalishni o\'chirishda xatolik')
  } finally {
    showDeleteDirectionModal.value = false
    directionToDelete.value = null
  }
}

// Subject management
const openDirectionSubjectsModal = (direction) => {
  selectedDirection.value = direction
  const ds = dataStore.directionSubjects.find(ds => ds.directionId === direction.id)
  selectedSubjectIds.value = ds ? [...ds.subjectIds] : []
  newSubjectName.value = ''
  newSubjectIcon.value = 'BookOpen'
  showSubjectsModal.value = true
}

const addNewSubject = async () => {
  if (!newSubjectName.value.trim()) {
    toast.error('Fan nomini kiriting')
    return
  }

  // Check if subject already exists
  const existing = dataStore.subjects.find(s => s.name.toLowerCase() === newSubjectName.value.trim().toLowerCase())
  if (existing) {
    toast.error('Bu fan allaqachon mavjud')
    return
  }

  // Get color based on icon
  const colorMap = {
    Monitor: 'blue',
    Code: 'indigo',
    Calculator: 'purple',
    Atom: 'cyan',
    FlaskConical: 'emerald',
    Leaf: 'green',
    Microscope: 'rose',
    Scale: 'amber',
    Banknote: 'yellow',
    BookText: 'orange',
    Globe2: 'sky',
    Languages: 'violet',
    Heart: 'pink',
    Palette: 'fuchsia',
    Music: 'teal',
    Cpu: 'slate',
    BookOpen: 'blue'
  }

  saving.value = true
  try {
    const newSubject = await dataStore.addSubject({
      name: newSubjectName.value.trim(),
      icon: newSubjectIcon.value,
      color: colorMap[newSubjectIcon.value] || 'blue'
    })

    // Automatically select the new subject
    if (newSubject?.id) {
      selectedSubjectIds.value.push(newSubject.id)
    }
    
    toast.success('Yangi fan qo\'shildi')
    newSubjectName.value = ''
    newSubjectIcon.value = 'BookOpen'
  } catch (err) {
    toast.error(err.message || 'Xatolik yuz berdi')
  } finally {
    saving.value = false
  }
}

const saveDirectionSubjects = async () => {
  saving.value = true
  try {
    await dataStore.updateDirectionSubjects(selectedDirection.value.id, selectedSubjectIds.value)
    toast.success(`${selectedDirection.value.name} uchun fanlar saqlandi`)
    showSubjectsModal.value = false
  } catch (err) {
    toast.error(err.message || 'Xatolik yuz berdi')
  } finally {
    saving.value = false
  }
}

const confirmDeleteSubject = (subject) => {
  subjectToDelete.value = subject
  showDeleteSubjectModal.value = true
}

const deleteSubject = async () => {
  saving.value = true
  try {
    // Remove from selected
    selectedSubjectIds.value = selectedSubjectIds.value.filter(id => id !== subjectToDelete.value.id)
    
    // Delete subject
    await dataStore.deleteSubject(subjectToDelete.value.id)
    toast.success('Fan o\'chirildi')
    showDeleteSubjectModal.value = false
    subjectToDelete.value = null
  } catch (err) {
    toast.error(err.message || 'O\'chirishda xatolik')
  } finally {
    saving.value = false
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
</style>
