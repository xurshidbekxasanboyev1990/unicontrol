<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800">Yordam</h1>
      <p class="text-slate-500">Ko'p so'raladigan savollar va qo'llab-quvvatlash</p>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search :size="20" class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Savollarni qidiring..."
        class="w-full rounded-2xl border border-slate-200 bg-white py-4 pl-12 pr-4 text-slate-700 placeholder-slate-400 shadow-sm focus:border-blue-400 focus:outline-none"
      />
    </div>

    <!-- Quick Actions -->
    <div class="grid gap-4 sm:grid-cols-3">
      <button
        @click="showContactForm = true"
        class="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-blue-300 hover:shadow-md"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
          <MessageCircle :size="24" class="text-blue-600" />
        </div>
        <div class="text-left">
          <h3 class="font-medium text-slate-800">Xabar yuborish</h3>
          <p class="text-sm text-slate-500">Qo'llab-quvvatlashga murojaat</p>
        </div>
      </button>

      <a
        href="tel:+998712345678"
        class="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-green-300 hover:shadow-md"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100">
          <Phone :size="24" class="text-green-600" />
        </div>
        <div class="text-left">
          <h3 class="font-medium text-slate-800">Qo'ng'iroq qilish</h3>
          <p class="text-sm text-slate-500">+998 71 234 56 78</p>
        </div>
      </a>

      <a
        href="https://t.me/kuaf_support"
        target="_blank"
        class="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-indigo-300 hover:shadow-md"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100">
          <Send :size="24" class="text-indigo-600" />
        </div>
        <div class="text-left">
          <h3 class="font-medium text-slate-800">Telegram</h3>
          <p class="text-sm text-slate-500">@kuaf_support</p>
        </div>
      </a>
    </div>

    <!-- FAQ Categories -->
    <div class="flex gap-2 overflow-x-auto pb-2">
      <button
        v-for="category in categories"
        :key="category.id"
        @click="activeCategory = category.id"
        class="flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-medium transition-all"
        :class="activeCategory === category.id 
          ? 'bg-blue-500 text-white' 
          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
      >
        <component :is="category.icon" :size="18" />
        {{ category.name }}
      </button>
    </div>

    <!-- FAQ List -->
    <div class="space-y-3">
      <div
        v-for="faq in filteredFaqs"
        :key="faq.id"
        class="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm"
      >
        <button
          @click="toggleFaq(faq.id)"
          class="flex w-full items-center justify-between p-5 text-left"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100">
              <HelpCircle :size="16" class="text-blue-600" />
            </div>
            <span class="font-medium text-slate-800">{{ faq.question }}</span>
          </div>
          <ChevronDown 
            :size="20" 
            class="text-slate-400 transition-transform"
            :class="{ 'rotate-180': openFaqs.includes(faq.id) }"
          />
        </button>
        
        <div
          v-if="openFaqs.includes(faq.id)"
          class="border-t border-slate-100 bg-slate-50 p-5"
        >
          <p class="text-slate-600">{{ faq.answer }}</p>
          
          <div class="mt-4 flex items-center gap-4">
            <span class="text-sm text-slate-500">Bu javob foydali bo'ldimi?</span>
            <div class="flex gap-2">
              <button 
                @click="rateFaq(faq.id, true)"
                class="flex items-center gap-1 rounded-lg bg-green-100 px-3 py-1 text-sm text-green-600 hover:bg-green-200"
              >
                <ThumbsUp :size="14" /> Ha
              </button>
              <button 
                @click="rateFaq(faq.id, false)"
                class="flex items-center gap-1 rounded-lg bg-red-100 px-3 py-1 text-sm text-red-600 hover:bg-red-200"
              >
                <ThumbsDown :size="14" /> Yo'q
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Video Tutorials -->
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center gap-2">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-100">
          <Play :size="20" class="text-red-600" />
        </div>
        <h2 class="font-semibold text-slate-800">Video qo'llanmalar</h2>
      </div>
      
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="video in videos"
          :key="video.id"
          class="group cursor-pointer overflow-hidden rounded-xl border border-slate-200"
        >
          <div class="relative aspect-video bg-slate-200">
            <img :src="video.thumbnail" class="h-full w-full object-cover" />
            <div class="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100">
              <div class="flex h-12 w-12 items-center justify-center rounded-full bg-white/90">
                <Play :size="20" class="text-slate-800" />
              </div>
            </div>
          </div>
          <div class="p-3">
            <h3 class="text-sm font-medium text-slate-800">{{ video.title }}</h3>
            <p class="text-xs text-slate-500">{{ video.duration }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- User Guide -->
    <div class="rounded-2xl border border-slate-200 bg-gradient-to-r from-blue-500 to-indigo-600 p-6 text-white shadow-sm">
      <div class="flex items-center gap-4">
        <div class="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20">
          <BookOpen :size="28" />
        </div>
        <div>
          <h2 class="text-xl font-semibold">Foydalanuvchi qo'llanmasi</h2>
          <p class="text-blue-100">Tizimdan foydalanish bo'yicha to'liq qo'llanma</p>
        </div>
      </div>
      
      <div class="mt-4 flex gap-3">
        <button class="flex items-center gap-2 rounded-xl bg-white/20 px-4 py-2 backdrop-blur transition-all hover:bg-white/30">
          <Download :size="18" />
          PDF yuklab olish
        </button>
        <button class="flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-blue-600 transition-all hover:bg-blue-50">
          <ExternalLink :size="18" />
          Onlayn o'qish
        </button>
      </div>
    </div>

    <!-- Contact Form Modal -->
    <Teleport to="body">
      <div
        v-if="showContactForm"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showContactForm = false"
      >
        <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">Xabar yuborish</h2>
            <button @click="showContactForm = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Mavzu</label>
              <select
                v-model="contactForm.subject"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
              >
                <option value="">Tanlang...</option>
                <option value="technical">Texnik muammo</option>
                <option value="attendance">Davomat haqida</option>
                <option value="schedule">Jadval haqida</option>
                <option value="library">Kutubxona haqida</option>
                <option value="other">Boshqa</option>
              </select>
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Xabar</label>
              <textarea
                v-model="contactForm.message"
                rows="5"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
                placeholder="Muammoingizni batafsil yozing..."
              ></textarea>
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">Fayl biriktirish (ixtiyoriy)</label>
              <div class="flex items-center gap-3">
                <input type="file" class="hidden" ref="fileInput" @change="handleFileSelect" />
                <button
                  @click="$refs.fileInput.click()"
                  class="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-slate-600 hover:bg-slate-50"
                >
                  <Paperclip :size="18" />
                  Fayl tanlash
                </button>
                <span v-if="contactForm.file" class="text-sm text-slate-600">
                  {{ contactForm.file.name }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button
              @click="showContactForm = false"
              class="flex-1 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 hover:bg-slate-50"
            >
              Bekor qilish
            </button>
            <button
              @click="submitContact"
              class="flex-1 rounded-xl bg-blue-500 py-3 font-medium text-white hover:bg-blue-600"
            >
              Yuborish
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import {
  Search, MessageCircle, Phone, Send, HelpCircle, ChevronDown,
  ThumbsUp, ThumbsDown, Play, BookOpen, Download, ExternalLink,
  X, Paperclip, Calendar, Book, Settings, User
} from 'lucide-vue-next'

const toast = useToastStore()

// State
const searchQuery = ref('')
const activeCategory = ref('all')
const openFaqs = ref([])
const showContactForm = ref(false)
const contactForm = ref({
  subject: '',
  message: '',
  file: null
})

// Categories
const categories = [
  { id: 'all', name: 'Barchasi', icon: HelpCircle },
  { id: 'attendance', name: 'Davomat', icon: Calendar },
  { id: 'library', name: 'Kutubxona', icon: Book },
  { id: 'settings', name: 'Sozlamalar', icon: Settings },
  { id: 'profile', name: 'Profil', icon: User }
]

// FAQs
const faqs = ref([
  {
    id: 1,
    category: 'attendance',
    question: 'Davomatim noto\'g\'ri ko\'rsatilmoqda. Nima qilishim kerak?',
    answer: 'Agar davomatingiz noto\'g\'ri ko\'rsatilayotgan bo\'lsa, guruh sardoringizga murojaat qiling. Sardor davomatni tuzatish huquqiga ega. Agar muammo hal bo\'lmasa, admin bilan bog\'laning.'
  },
  {
    id: 2,
    category: 'attendance',
    question: 'Davomat qachon belgilanadi?',
    answer: 'Davomat har bir dars boshlanishida guruh sardori tomonidan belgilanadi. Dars tugaganidan keyin davomat o\'zgartirilishi mumkin, lekin buning uchun asosli sabab talab etiladi.'
  },
  {
    id: 3,
    category: 'library',
    question: 'Kitobni qanday qilib yuklab olish mumkin?',
    answer: 'Kutubxona bo\'limiga o\'ting, kerakli kitobni toping va "Yuklab olish" tugmasini bosing. Kitob PDF formatida qurilmangizga yuklanadi. Ba\'zi kitoblar faqat onlayn o\'qish uchun mavjud.'
  },
  {
    id: 4,
    category: 'library',
    question: 'Nechta kitob olish mumkin?',
    answer: 'Bir vaqtning o\'zida 5 tagacha kitob olish mumkin. Kitobni qaytarganingizdan keyin yangi kitob olishingiz mumkin.'
  },
  {
    id: 5,
    category: 'settings',
    question: 'Parolni qanday o\'zgartirish mumkin?',
    answer: 'Sozlamalar > Xavfsizlik > Parolni o\'zgartirish bo\'limiga o\'ting. Joriy parolni kiriting, keyin yangi parolni ikki marta kiriting va "Saqlash" tugmasini bosing.'
  },
  {
    id: 6,
    category: 'settings',
    question: 'Bildirishnomalarni qanday o\'chirish mumkin?',
    answer: 'Sozlamalar > Bildirishnomalar bo\'limiga o\'ting. U yerda har xil turdagi bildirishnomalarni alohida-alohida yoqish yoki o\'chirish mumkin.'
  },
  {
    id: 7,
    category: 'profile',
    question: 'Profil rasmini qanday o\'zgartirish mumkin?',
    answer: 'Profil sahifasiga o\'ting, profil rasmi ustiga bosing va "Rasm yuklash" tugmasini tanlang. Rasm JPG yoki PNG formatida, 5MB dan kichik bo\'lishi kerak.'
  },
  {
    id: 8,
    category: 'profile',
    question: 'Telefon raqamni qanday o\'zgartirish mumkin?',
    answer: 'Profil > Tahrirlash bo\'limida telefon raqamni o\'zgartirishingiz mumkin. Yangi raqamga tasdiqlash kodi yuboriladi.'
  }
])

// Videos
const videos = [
  { id: 1, title: 'Tizimga kirish va profil', thumbnail: 'https://picsum.photos/320/180?random=1', duration: '3:45' },
  { id: 2, title: 'Davomat ko\'rish', thumbnail: 'https://picsum.photos/320/180?random=2', duration: '2:30' },
  { id: 3, title: 'Kutubxonadan foydalanish', thumbnail: 'https://picsum.photos/320/180?random=3', duration: '5:15' }
]

// Computed
const filteredFaqs = computed(() => {
  let result = faqs.value

  if (activeCategory.value !== 'all') {
    result = result.filter(f => f.category === activeCategory.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(f => 
      f.question.toLowerCase().includes(query) || 
      f.answer.toLowerCase().includes(query)
    )
  }

  return result
})

// Methods
function toggleFaq(id) {
  const index = openFaqs.value.indexOf(id)
  if (index === -1) {
    openFaqs.value.push(id)
  } else {
    openFaqs.value.splice(index, 1)
  }
}

function rateFaq(id, helpful) {
  toast.success(helpful ? 'Rahmat! Fikringiz uchun!' : 'Tushundik. Yaxshilashga harakat qilamiz.')
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    contactForm.value.file = file
  }
}

function submitContact() {
  if (!contactForm.value.subject || !contactForm.value.message) {
    toast.error('Mavzu va xabarni to\'ldiring')
    return
  }
  
  // Here you would send to API
  toast.success('Xabaringiz yuborildi. Tez orada javob beramiz.')
  showContactForm.value = false
  contactForm.value = { subject: '', message: '', file: null }
}
</script>
