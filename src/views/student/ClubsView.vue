<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-600 rounded-2xl p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold">To'garaklar</h1>
          <p class="text-violet-100 mt-1">Qo'shimcha darslar va kurslar</p>
        </div>
        <div class="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
          <BookOpen class="w-7 h-7" />
        </div>
      </div>
    </div>

    <!-- Categories Filter -->
    <div class="flex items-center gap-2 overflow-x-auto pb-2">
      <button 
        v-for="cat in categories" 
        :key="cat.value"
        @click="filterCategory = cat.value"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap flex items-center gap-2"
        :class="filterCategory === cat.value 
          ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/30' 
          : 'bg-white border border-slate-200 text-slate-600 hover:border-violet-300'"
      >
        <component :is="cat.icon" class="w-4 h-4" />
        {{ cat.label }}
      </button>
    </div>

    <!-- Clubs Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div 
        v-for="club in filteredClubs" 
        :key="club.id"
        class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl hover:border-violet-200 transition-all duration-300 group"
      >
        <!-- Header with gradient -->
        <div class="h-28 relative" :class="getCategoryGradient(club.category)">
          <!-- Pattern overlay -->
          <div class="absolute inset-0 opacity-10">
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,white_1px,transparent_1px)] bg-[length:20px_20px]"></div>
          </div>
          
          <div class="absolute top-3 left-3">
            <span class="px-3 py-1 rounded-full text-xs font-semibold bg-white/20 backdrop-blur text-white">
              {{ getCategoryLabel(club.category) }}
            </span>
          </div>
          
          <div class="absolute -bottom-7 left-4">
            <div class="w-16 h-16 rounded-2xl bg-white shadow-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <component :is="getCategoryIcon(club.category)" class="w-8 h-8" :class="getCategoryIconColor(club.category)" />
            </div>
          </div>

          <!-- Price badge -->
          <div class="absolute top-3 right-3">
            <span class="px-3 py-1.5 rounded-xl text-sm font-bold bg-white text-emerald-600 shadow-lg">
              {{ formatPrice(club.price) }} so'm
            </span>
          </div>
        </div>

        <!-- Content -->
        <div class="p-5 pt-12">
          <h3 class="text-lg font-bold text-slate-800 group-hover:text-violet-600 transition-colors">{{ club.name }}</h3>
          <p class="text-sm text-violet-500 font-medium mt-1">{{ club.teacher }}</p>
          
          <p class="text-sm text-slate-600 mt-3 line-clamp-2">{{ club.description }}</p>

          <div class="mt-4 pt-4 border-t border-slate-100 space-y-2">
            <div class="flex items-center gap-2 text-sm">
              <div class="w-8 h-8 bg-violet-50 rounded-lg flex items-center justify-center">
                <Clock class="w-4 h-4 text-violet-500" />
              </div>
              <span class="text-slate-600">{{ club.schedule }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <MapPin class="w-4 h-4 text-blue-500" />
              </div>
              <span class="text-slate-600">{{ club.room }}</span>
            </div>
          </div>

          <!-- Contact Button -->
          <a 
            :href="'tel:' + club.phone.replace(/\s/g, '')"
            class="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/30 hover:shadow-emerald-500/50"
          >
            <Phone class="w-5 h-5" />
            Bog'lanish
          </a>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredClubs.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
      <div class="w-20 h-20 bg-violet-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <BookOpen class="w-10 h-10 text-violet-400" />
      </div>
      <p class="text-slate-500 text-lg">Bu kategoriyada to'garak yo'q</p>
      <p class="text-slate-400 text-sm mt-2">Boshqa kategoriyani tanlang</p>
    </div>

    <!-- Info Card -->
    <div class="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-5">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <Lightbulb class="w-6 h-6 text-amber-600" />
        </div>
        <div>
          <h3 class="font-semibold text-amber-800">To'garaklarga qanday yozilish mumkin?</h3>
          <p class="text-sm text-amber-700 mt-2">
            O'zingizga yoqqan to'garakni tanlang va "Bog'lanish" tugmasini bosib to'g'ridan-to'g'ri o'qituvchi bilan aloqaga chiqing. 
            O'qituvchi sizga to'garak haqida batafsil ma'lumot beradi va ro'yxatga oladi.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  BookOpen,
  Clock,
  MapPin,
  Phone,
  Lightbulb,
  Calculator,
  Globe,
  Code,
  Dumbbell,
  Palette,
  Layers
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()
const filterCategory = ref('all')
const loading = ref(false)

// Load data on mount
onMounted(async () => {
  loading.value = true
  try {
    await dataStore.fetchClubs()
  } catch (err) {
    toast.error('To\'garaklarni yuklashda xatolik')
    console.error(err)
  } finally {
    loading.value = false
  }
})

const categories = [
  { value: 'all', label: 'Barchasi', icon: markRaw(Layers) },
  { value: 'fan', label: 'Fan', icon: markRaw(Calculator) },
  { value: 'til', label: 'Til', icon: markRaw(Globe) },
  { value: 'texnik', label: 'Texnik', icon: markRaw(Code) },
  { value: 'sport', label: 'Sport', icon: markRaw(Dumbbell) },
  { value: "san'at", label: "San'at", icon: markRaw(Palette) }
]

const filteredClubs = computed(() => {
  const activeClubs = dataStore.clubs.filter(c => c.isActive)
  if (filterCategory.value === 'all') return activeClubs
  return activeClubs.filter(c => c.category === filterCategory.value)
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
</script>
