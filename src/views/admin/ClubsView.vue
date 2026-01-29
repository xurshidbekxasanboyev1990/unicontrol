<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">To'garaklar boshqaruvi</h1>
        <p class="text-slate-500">{{ dataStore.clubs.length }} ta to'garak</p>
      </div>
      <button 
        @click="openModal()"
        class="px-4 py-2.5 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors flex items-center gap-2"
      >
        <Plus class="w-5 h-5" />
        Yangi to'garak
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
      <span class="ml-3 text-slate-600">To'garaklar yuklanmoqda...</span>
    </div>

    <template v-else>
    <!-- Categories Filter -->
    <div class="flex items-center gap-2 flex-wrap">
      <button 
        v-for="cat in categories" 
        :key="cat.value"
        @click="filterCategory = cat.value"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-all"
        :class="filterCategory === cat.value ? 'bg-violet-500 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:border-violet-300'"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- Clubs Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="club in filteredClubs" 
        :key="club.id"
        class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-all"
        :class="{ 'opacity-60 border-rose-200': !club.isActive }"
      >
        <!-- Header with gradient -->
        <div class="h-24 relative" :class="getCategoryGradient(club.category)">
          <div class="absolute top-3 left-3">
            <span 
              class="px-3 py-1 rounded-full text-xs font-semibold bg-white/20 backdrop-blur text-white"
            >
              {{ getCategoryLabel(club.category) }}
            </span>
          </div>
          <div class="absolute top-3 right-3 flex items-center gap-1">
            <button 
              @click="toggleStatus(club)"
              class="p-1.5 rounded-lg bg-white/20 backdrop-blur hover:bg-white/30 transition-colors"
              :title="club.isActive ? 'O\'chirish' : 'Yoqish'"
            >
              <Power class="w-4 h-4 text-white" />
            </button>
          </div>
          <div class="absolute -bottom-6 left-4">
            <div class="w-14 h-14 rounded-xl bg-white shadow-lg flex items-center justify-center">
              <component :is="getCategoryIcon(club.category)" class="w-7 h-7" :class="getCategoryIconColor(club.category)" />
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="p-4 pt-10">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="font-bold text-slate-800">{{ club.name }}</h3>
              <p class="text-sm text-slate-500 mt-1">{{ club.teacher }}</p>
            </div>
            <div class="flex items-center gap-1">
              <button 
                @click="openModal(club)"
                class="p-2 text-slate-400 hover:text-violet-500 hover:bg-violet-50 rounded-lg transition-colors"
              >
                <Pencil class="w-4 h-4" />
              </button>
              <button 
                @click="confirmDelete(club)"
                class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <p class="text-sm text-slate-600 mt-3 line-clamp-2">{{ club.description }}</p>

          <div class="mt-4 pt-4 border-t border-slate-100 space-y-2">
            <div class="flex items-center gap-2 text-sm">
              <Clock class="w-4 h-4 text-slate-400" />
              <span class="text-slate-600">{{ club.schedule }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <MapPin class="w-4 h-4 text-slate-400" />
              <span class="text-slate-600">{{ club.room }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <Phone class="w-4 h-4 text-slate-400" />
              <span class="text-slate-600">{{ club.phone }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <Banknote class="w-4 h-4 text-emerald-500" />
              <span class="font-semibold text-emerald-600">{{ formatPrice(club.price) }} so'm/oy</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredClubs.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <BookOpen class="w-12 h-12 text-slate-300 mx-auto mb-4" />
      <p class="text-slate-500">To'garak topilmadi</p>
      <button 
        @click="openModal()"
        class="mt-4 px-4 py-2 bg-violet-500 text-white rounded-xl font-medium hover:bg-violet-600 transition-colors"
      >
        Yangi to'garak qo'shish
      </button>
    </div>
    </template>

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
        <div class="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white">
            <h2 class="text-lg font-semibold text-slate-800">
              {{ editingClub ? 'To\'garakni tahrirlash' : 'Yangi to\'garak qo\'shish' }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveClub" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">To'garak nomi</label>
              <input 
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="Matematika to'garagi"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">O'qituvchi</label>
              <input 
                v-model="form.teacher"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="Karimov Aziz Shavkatovich"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Telefon</label>
                <input 
                  v-model="form.phone"
                  type="tel"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="+998 90 111 22 33"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Xona</label>
                <input 
                  v-model="form.room"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="A-301"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Kategoriya</label>
                <select 
                  v-model="form.category"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                >
                  <option value="fan">Fan</option>
                  <option value="til">Til</option>
                  <option value="texnik">Texnik</option>
                  <option value="sport">Sport</option>
                  <option value="san'at">San'at</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Narxi (oylik)</label>
                <input 
                  v-model.number="form.price"
                  type="number"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                  placeholder="200000"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Dars jadvali</label>
              <input 
                v-model="form.schedule"
                type="text"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
                placeholder="Dushanba, Chorshanba - 16:00"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Tavsif</label>
              <textarea 
                v-model="form.description"
                rows="3"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none resize-none"
                placeholder="To'garak haqida qisqacha ma'lumot..."
              ></textarea>
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
            "{{ deletingClub?.name }}" to'garagini o'chirmoqchimisiz?
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              @click="deleteClub"
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
import { ref, reactive, computed, markRaw, onMounted } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  Plus,
  Pencil,
  Trash2,
  X,
  Power,
  Clock,
  MapPin,
  Phone,
  Banknote,
  BookOpen,
  AlertTriangle,
  Calculator,
  Globe,
  Code,
  Dumbbell,
  Palette,
  Loader2
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingClub = ref(null)
const deletingClub = ref(null)
const filterCategory = ref('all')
const loading = ref(true)
const saving = ref(false)

// Load clubs on mount
onMounted(async () => {
  loading.value = true
  try {
    await dataStore.fetchClubs()
  } catch (err) {
    console.error('Error loading clubs:', err)
    toast.error('To\'garaklarni yuklashda xatolik')
  } finally {
    loading.value = false
  }
})

const categories = [
  { value: 'all', label: 'Barchasi' },
  { value: 'fan', label: 'Fan' },
  { value: 'til', label: 'Til' },
  { value: 'texnik', label: 'Texnik' },
  { value: 'sport', label: 'Sport' },
  { value: "san'at", label: "San'at" }
]

const form = reactive({
  name: '',
  teacher: '',
  phone: '',
  description: '',
  schedule: '',
  price: 200000,
  room: '',
  category: 'fan'
})

const filteredClubs = computed(() => {
  if (filterCategory.value === 'all') return dataStore.clubs
  return dataStore.clubs.filter(c => c.category === filterCategory.value)
})

const getCategoryGradient = (category) => {
  const gradients = {
    'fan': 'bg-gradient-to-br from-blue-500 to-indigo-600',
    'til': 'bg-gradient-to-br from-emerald-500 to-teal-600',
    'texnik': 'bg-gradient-to-br from-violet-500 to-purple-600',
    'sport': 'bg-gradient-to-br from-orange-500 to-red-600',
    "san'at": 'bg-gradient-to-br from-pink-500 to-rose-600'
  }
  return gradients[category] || gradients['fan']
}

const getCategoryLabel = (category) => {
  const labels = {
    'fan': 'Fan',
    'til': 'Til kursi',
    'texnik': 'Texnik',
    'sport': 'Sport',
    "san'at": "San'at"
  }
  return labels[category] || 'Boshqa'
}

const getCategoryIcon = (category) => {
  const icons = {
    'fan': markRaw(Calculator),
    'til': markRaw(Globe),
    'texnik': markRaw(Code),
    'sport': markRaw(Dumbbell),
    "san'at": markRaw(Palette)
  }
  return icons[category] || icons['fan']
}

const getCategoryIconColor = (category) => {
  const colors = {
    'fan': 'text-blue-500',
    'til': 'text-emerald-500',
    'texnik': 'text-violet-500',
    'sport': 'text-orange-500',
    "san'at": 'text-pink-500'
  }
  return colors[category] || colors['fan']
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('uz-UZ').format(price)
}

const openModal = (club = null) => {
  if (club) {
    editingClub.value = club
    form.name = club.name
    form.teacher = club.teacher
    form.phone = club.phone
    form.description = club.description
    form.schedule = club.schedule
    form.price = club.price
    form.room = club.room
    form.category = club.category
  } else {
    editingClub.value = null
    form.name = ''
    form.teacher = ''
    form.phone = ''
    form.description = ''
    form.schedule = ''
    form.price = 200000
    form.room = ''
    form.category = 'fan'
  }
  showModal.value = true
}

const saveClub = async () => {
  saving.value = true
  try {
    if (editingClub.value) {
      await dataStore.updateClub(editingClub.value.id, { ...form })
      toast.success('To\'garak yangilandi')
    } else {
      await dataStore.addClub({ ...form })
      toast.success('Yangi to\'garak qo\'shildi')
    }
    showModal.value = false
  } catch (err) {
    console.error('Error saving club:', err)
    toast.error('To\'garakni saqlashda xatolik')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (club) => {
  deletingClub.value = club
  showDeleteConfirm.value = true
}

const deleteClub = async () => {
  if (deletingClub.value) {
    try {
      await dataStore.deleteClub(deletingClub.value.id)
      toast.success('To\'garak o\'chirildi')
    } catch (err) {
      console.error('Error deleting club:', err)
      toast.error('To\'garakni o\'chirishda xatolik')
    }
  }
  showDeleteConfirm.value = false
  deletingClub.value = null
}

const toggleStatus = async (club) => {
  try {
    await dataStore.toggleClubStatus(club.id)
    toast.info(club.isActive ? 'To\'garak o\'chirildi' : 'To\'garak yoqildi')
  } catch (err) {
    console.error('Error toggling club status:', err)
    toast.error('Statusni o\'zgartirishda xatolik')
  }
}
</script>
