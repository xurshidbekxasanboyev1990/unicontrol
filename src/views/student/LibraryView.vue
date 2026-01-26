<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Kutubxona</h1>
        <p class="text-slate-500">KUAF Mutola - Elektron kutubxona</p>
      </div>
      
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 rounded-xl bg-emerald-100 px-4 py-2 text-emerald-700">
          <Book :size="18" />
          <span class="text-sm font-medium">{{ borrowedCount }} kitob olingan</span>
        </div>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="flex flex-col gap-4 lg:flex-row">
        <div class="relative flex-1">
          <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Kitob nomi, muallif yoki ISBN bo'yicha qidiring..."
            class="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-slate-700 placeholder-slate-400 transition-all focus:border-blue-400 focus:bg-white focus:outline-none"
          />
        </div>
        
        <div class="flex gap-3">
          <select
            v-model="selectedCategory"
            class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700 focus:border-blue-400 focus:outline-none"
          >
            <option value="all">Barcha turkumlar</option>
            <option value="darslik">Darsliklar</option>
            <option value="ilmiy">Ilmiy adabiyotlar</option>
            <option value="badiiy">Badiiy adabiyot</option>
            <option value="texnik">Texnik adabiyot</option>
            <option value="diniy">Diniy adabiyot</option>
          </select>
          
          <select
            v-model="selectedLanguage"
            class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700 focus:border-blue-400 focus:outline-none"
          >
            <option value="all">Barcha tillar</option>
            <option value="uz">O'zbekcha</option>
            <option value="ru">Ruscha</option>
            <option value="en">Inglizcha</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Categories -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="selectedCategory = cat.id"
        class="flex flex-col items-center gap-3 rounded-2xl border-2 p-4 transition-all"
        :class="selectedCategory === cat.id 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-slate-200 bg-white hover:border-blue-300'"
      >
        <div 
          class="flex h-12 w-12 items-center justify-center rounded-xl"
          :class="cat.bgColor"
        >
          <component :is="cat.icon" :size="24" :class="cat.textColor" />
        </div>
        <div class="text-center">
          <p class="text-sm font-medium text-slate-800">{{ cat.name }}</p>
          <p class="text-xs text-slate-500">{{ cat.count }} kitob</p>
        </div>
      </button>
    </div>

    <!-- Featured Books -->
    <div class="rounded-2xl border border-slate-200 bg-gradient-to-r from-blue-500 to-indigo-600 p-6 text-white shadow-sm">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-blue-100">Tavsiya etilgan</p>
          <h2 class="text-xl font-bold">Hafta kitobi</h2>
        </div>
        <Sparkles :size="24" class="text-yellow-300" />
      </div>
      
      <div class="mt-4 flex items-center gap-4">
        <div class="h-32 w-24 overflow-hidden rounded-xl bg-white/20">
          <img 
            src="https://picsum.photos/96/128" 
            alt="Featured book"
            class="h-full w-full object-cover"
          />
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-semibold">Dasturlash asoslari</h3>
          <p class="text-blue-200">Muallif: A. Karimov</p>
          <div class="mt-2 flex items-center gap-2">
            <Star v-for="i in 5" :key="i" :size="16" class="fill-yellow-400 text-yellow-400" />
            <span class="text-sm text-blue-200">(4.8)</span>
          </div>
          <button class="mt-3 rounded-lg bg-white/20 px-4 py-2 text-sm font-medium backdrop-blur transition-all hover:bg-white/30">
            Batafsil ko'rish
          </button>
        </div>
      </div>
    </div>

    <!-- Books Grid -->
    <div>
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-800">
          {{ selectedCategory === 'all' ? 'Barcha kitoblar' : getCategoryName(selectedCategory) }}
        </h2>
        <div class="flex items-center gap-2">
          <button
            @click="viewMode = 'grid'"
            class="rounded-lg p-2 transition-colors"
            :class="viewMode === 'grid' ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-600'"
          >
            <LayoutGrid :size="18" />
          </button>
          <button
            @click="viewMode = 'list'"
            class="rounded-lg p-2 transition-colors"
            :class="viewMode === 'list' ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-600'"
          >
            <List :size="18" />
          </button>
        </div>
      </div>
      
      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        <div
          v-for="book in filteredBooks"
          :key="book.id"
          class="group cursor-pointer overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:shadow-lg"
          @click="openBook(book)"
        >
          <div class="relative aspect-[3/4] overflow-hidden bg-slate-100">
            <img 
              :src="book.cover" 
              :alt="book.title"
              class="h-full w-full object-cover transition-transform group-hover:scale-105"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100"></div>
            <button
              class="absolute bottom-3 left-1/2 -translate-x-1/2 translate-y-4 rounded-lg bg-white px-4 py-2 text-sm font-medium text-slate-800 opacity-0 shadow-lg transition-all group-hover:translate-y-0 group-hover:opacity-100"
            >
              O'qish
            </button>
          </div>
          <div class="p-4">
            <h3 class="line-clamp-2 font-medium text-slate-800">{{ book.title }}</h3>
            <p class="mt-1 text-sm text-slate-500">{{ book.author }}</p>
            <div class="mt-2 flex items-center justify-between">
              <div class="flex items-center gap-1">
                <Star :size="14" class="fill-yellow-400 text-yellow-400" />
                <span class="text-sm text-slate-600">{{ book.rating }}</span>
              </div>
              <span class="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">
                {{ book.pages }} bet
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="space-y-3">
        <div
          v-for="book in filteredBooks"
          :key="book.id"
          class="flex cursor-pointer items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:shadow-md"
          @click="openBook(book)"
        >
          <div class="h-24 w-18 flex-shrink-0 overflow-hidden rounded-xl bg-slate-100">
            <img 
              :src="book.cover" 
              :alt="book.title"
              class="h-full w-full object-cover"
            />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-slate-800">{{ book.title }}</h3>
            <p class="text-sm text-slate-500">{{ book.author }}</p>
            <div class="mt-2 flex items-center gap-4">
              <div class="flex items-center gap-1">
                <Star :size="14" class="fill-yellow-400 text-yellow-400" />
                <span class="text-sm text-slate-600">{{ book.rating }}</span>
              </div>
              <span class="text-sm text-slate-500">{{ book.pages }} bet</span>
              <span class="rounded bg-blue-100 px-2 py-1 text-xs text-blue-600">
                {{ getCategoryName(book.category) }}
              </span>
            </div>
          </div>
          <div class="flex flex-col gap-2">
            <button class="rounded-lg bg-blue-500 px-4 py-2 text-sm text-white hover:bg-blue-600">
              O'qish
            </button>
            <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">
              <Download :size="16" class="inline" /> Yuklab olish
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Book Modal -->
    <Teleport to="body">
      <div
        v-if="selectedBook"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="selectedBook = null"
      >
        <div class="w-full max-w-3xl overflow-hidden rounded-2xl bg-white shadow-2xl">
          <div class="flex">
            <div class="w-1/3 bg-gradient-to-br from-blue-500 to-indigo-600 p-6">
              <div class="aspect-[3/4] overflow-hidden rounded-xl bg-white/20">
                <img 
                  :src="selectedBook.cover" 
                  :alt="selectedBook.title"
                  class="h-full w-full object-cover"
                />
              </div>
            </div>
            <div class="flex-1 p-6">
              <div class="flex items-start justify-between">
                <div>
                  <h2 class="text-xl font-bold text-slate-800">{{ selectedBook.title }}</h2>
                  <p class="text-slate-500">{{ selectedBook.author }}</p>
                </div>
                <button @click="selectedBook = null" class="text-slate-400 hover:text-slate-600">
                  <X :size="24" />
                </button>
              </div>
              
              <div class="mt-4 flex items-center gap-4">
                <div class="flex items-center gap-1">
                  <Star v-for="i in 5" :key="i" :size="18" class="fill-yellow-400 text-yellow-400" />
                  <span class="ml-1 text-slate-600">{{ selectedBook.rating }}</span>
                </div>
                <span class="text-slate-400">|</span>
                <span class="text-slate-600">{{ selectedBook.pages }} bet</span>
                <span class="text-slate-400">|</span>
                <span class="text-slate-600">{{ selectedBook.year }} yil</span>
              </div>
              
              <div class="mt-4">
                <h3 class="font-medium text-slate-800">Tavsif</h3>
                <p class="mt-2 text-sm text-slate-600">{{ selectedBook.description }}</p>
              </div>
              
              <div class="mt-4 flex flex-wrap gap-2">
                <span class="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-600">
                  {{ getCategoryName(selectedBook.category) }}
                </span>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-600">
                  {{ getLanguageName(selectedBook.language) }}
                </span>
              </div>
              
              <div class="mt-6 flex gap-3">
                <button class="flex-1 rounded-xl bg-blue-500 py-3 text-white hover:bg-blue-600">
                  <BookOpen :size="18" class="mr-2 inline" />
                  Onlayn o'qish
                </button>
                <button class="flex-1 rounded-xl border border-slate-200 py-3 text-slate-700 hover:bg-slate-50">
                  <Download :size="18" class="mr-2 inline" />
                  PDF yuklab olish
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- My Books Section -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="font-semibold text-slate-800">Mening kitoblarim</h2>
        <span class="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-600">
          {{ myBooks.length }} ta
        </span>
      </div>
      
      <div v-if="myBooks.length === 0" class="flex flex-col items-center justify-center py-8 text-slate-400">
        <BookOpen :size="48" class="mb-2 opacity-50" />
        <p>Hali kitob olmagansiz</p>
        <p class="text-sm">Kutubxonadan kitob tanlang</p>
      </div>
      
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="book in myBooks"
          :key="book.id"
          class="flex items-center gap-3 rounded-xl bg-slate-50 p-3"
        >
          <div class="h-16 w-12 overflow-hidden rounded-lg bg-slate-200">
            <img :src="book.cover" class="h-full w-full object-cover" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="truncate text-sm font-medium text-slate-800">{{ book.title }}</p>
            <p class="text-xs text-slate-500">{{ book.progress }}% o'qildi</p>
            <div class="mt-1 h-1.5 overflow-hidden rounded-full bg-slate-200">
              <div 
                class="h-full rounded-full bg-blue-500"
                :style="{ width: book.progress + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Book, Search, Sparkles, Star, LayoutGrid, List, Download, X, BookOpen,
  GraduationCap, FileText, BookMarked, Cpu, Heart
} from 'lucide-vue-next'

const route = useRoute()

// State
const searchQuery = ref('')
const selectedCategory = ref(route.query.category || 'all')
const selectedLanguage = ref('all')
const viewMode = ref('grid')
const selectedBook = ref(null)
const borrowedCount = ref(2)

// Categories
const categories = [
  { id: 'all', name: 'Barchasi', count: 5420, icon: Book, bgColor: 'bg-slate-100', textColor: 'text-slate-600' },
  { id: 'darslik', name: 'Darsliklar', count: 1250, icon: GraduationCap, bgColor: 'bg-blue-100', textColor: 'text-blue-600' },
  { id: 'ilmiy', name: 'Ilmiy', count: 890, icon: FileText, bgColor: 'bg-purple-100', textColor: 'text-purple-600' },
  { id: 'badiiy', name: 'Badiiy', count: 2100, icon: BookMarked, bgColor: 'bg-amber-100', textColor: 'text-amber-600' },
  { id: 'texnik', name: 'Texnik', count: 780, icon: Cpu, bgColor: 'bg-emerald-100', textColor: 'text-emerald-600' },
  { id: 'diniy', name: 'Diniy', count: 400, icon: Heart, bgColor: 'bg-rose-100', textColor: 'text-rose-600' }
]

// Mock books data
const books = ref([
  {
    id: 1,
    title: 'Dasturlash asoslari',
    author: 'A. Karimov',
    cover: 'https://picsum.photos/200/300?random=1',
    rating: 4.8,
    pages: 320,
    year: 2023,
    category: 'darslik',
    language: 'uz',
    description: 'Bu kitob dasturlash asoslarini o\'rganmoqchi bo\'lgan talabalar uchun mo\'ljallangan. Kitobda Python dasturlash tili asoslari batafsil tushuntirilgan.'
  },
  {
    id: 2,
    title: 'Matematika - Oliy matematika',
    author: 'M. Rahimov',
    cover: 'https://picsum.photos/200/300?random=2',
    rating: 4.5,
    pages: 450,
    year: 2022,
    category: 'darslik',
    language: 'uz',
    description: 'Oliy matematika kursi bo\'yicha to\'liq qo\'llanma.'
  },
  {
    id: 3,
    title: 'O\'tgan kunlar',
    author: 'Abdulla Qodiriy',
    cover: 'https://picsum.photos/200/300?random=3',
    rating: 5.0,
    pages: 380,
    year: 2020,
    category: 'badiiy',
    language: 'uz',
    description: 'O\'zbek adabiyotining durdonasi, tarixiy roman.'
  },
  {
    id: 4,
    title: 'Artificial Intelligence',
    author: 'Stuart Russell',
    cover: 'https://picsum.photos/200/300?random=4',
    rating: 4.7,
    pages: 520,
    year: 2021,
    category: 'ilmiy',
    language: 'en',
    description: 'A comprehensive guide to artificial intelligence and machine learning.'
  },
  {
    id: 5,
    title: 'Web Development',
    author: 'Jon Duckett',
    cover: 'https://picsum.photos/200/300?random=5',
    rating: 4.6,
    pages: 490,
    year: 2023,
    category: 'texnik',
    language: 'en',
    description: 'Learn HTML, CSS, and JavaScript from scratch.'
  },
  {
    id: 6,
    title: 'Физика',
    author: 'И. Савельев',
    cover: 'https://picsum.photos/200/300?random=6',
    rating: 4.4,
    pages: 560,
    year: 2019,
    category: 'darslik',
    language: 'ru',
    description: 'Общий курс физики для высших учебных заведений.'
  },
  {
    id: 7,
    title: 'Qur\'on tafsiri',
    author: 'Ibn Kasir',
    cover: 'https://picsum.photos/200/300?random=7',
    rating: 4.9,
    pages: 800,
    year: 2018,
    category: 'diniy',
    language: 'uz',
    description: 'Qur\'oni Karimning batafsil tafsiri.'
  },
  {
    id: 8,
    title: 'Kecha va kunduz',
    author: 'Cho\'lpon',
    cover: 'https://picsum.photos/200/300?random=8',
    rating: 4.8,
    pages: 290,
    year: 2021,
    category: 'badiiy',
    language: 'uz',
    description: 'O\'zbek adabiyotining klassik asari.'
  }
])

const myBooks = ref([
  { id: 1, title: 'Dasturlash asoslari', cover: 'https://picsum.photos/200/300?random=1', progress: 65 },
  { id: 3, title: 'O\'tgan kunlar', cover: 'https://picsum.photos/200/300?random=3', progress: 30 }
])

// Computed
const filteredBooks = computed(() => {
  let result = books.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(b => 
      b.title.toLowerCase().includes(query) || 
      b.author.toLowerCase().includes(query)
    )
  }

  if (selectedCategory.value !== 'all') {
    result = result.filter(b => b.category === selectedCategory.value)
  }

  if (selectedLanguage.value !== 'all') {
    result = result.filter(b => b.language === selectedLanguage.value)
  }

  return result
})

// Methods
function getCategoryName(id) {
  const cat = categories.find(c => c.id === id)
  return cat ? cat.name : id
}

function getLanguageName(code) {
  const langs = { uz: 'O\'zbekcha', ru: 'Ruscha', en: 'Inglizcha' }
  return langs[code] || code
}

function openBook(book) {
  selectedBook.value = book
}
</script>
