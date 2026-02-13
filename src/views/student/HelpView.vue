<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('common.help') }}</h1>
      <p class="text-sm text-slate-500">{{ $t('common.help') }}</p>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search :size="20" class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('help.searchPlaceholder')"
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
          <h3 class="font-medium text-slate-800">{{ $t('help.sendMessage') }}</h3>
          <p class="text-sm text-slate-500">{{ $t('help.supportContact') }}</p>
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
          <h3 class="font-medium text-slate-800">{{ $t('help.callUs') }}</h3>
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
            <span class="text-sm text-slate-500">{{ $t('help.wasHelpful') }}</span>
            <div class="flex gap-2">
              <button 
                @click="rateFaq(faq.id, true)"
                class="flex items-center gap-1 rounded-lg bg-green-100 px-3 py-1 text-sm text-green-600 hover:bg-green-200"
              >
                <ThumbsUp :size="14" /> {{ $t('help.yes') }}
              </button>
              <button 
                @click="rateFaq(faq.id, false)"
                class="flex items-center gap-1 rounded-lg bg-red-100 px-3 py-1 text-sm text-red-600 hover:bg-red-200"
              >
                <ThumbsDown :size="14" /> {{ $t('help.no') }}
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
        <h2 class="font-semibold text-slate-800">{{ $t('help.videoTutorials') }}</h2>
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
          <h2 class="text-xl font-semibold">{{ $t('help.userGuide') }}</h2>
          <p class="text-blue-100">{{ $t('help.userGuideDesc') }}</p>
        </div>
      </div>
      
      <div class="mt-4 flex gap-3">
        <button class="flex items-center gap-2 rounded-xl bg-white/20 px-4 py-2 backdrop-blur transition-all hover:bg-white/30">
          <Download :size="18" />
          {{ $t('help.pdfDownload') }}
        </button>
        <button class="flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-blue-600 transition-all hover:bg-blue-50">
          <ExternalLink :size="18" />
          {{ $t('help.readOnline') }}
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
            <h2 class="text-lg font-bold text-slate-800">{{ $t('help.sendMessage') }}</h2>
            <button @click="showContactForm = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ $t('help.subject') }}</label>
              <select
                v-model="contactForm.subject"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
              >
                <option value="">{{ $t('help.selectPlaceholder') }}</option>
                <option value="technical">{{ $t('help.technicalIssue') }}</option>
                <option value="attendance">{{ $t('help.aboutAttendance') }}</option>
                <option value="schedule">{{ $t('help.aboutSchedule') }}</option>
                <option value="library">{{ $t('help.aboutLibrary') }}</option>
                <option value="other">{{ $t('help.other') }}</option>
              </select>
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ $t('help.message') }}</label>
              <textarea
                v-model="contactForm.message"
                rows="5"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-blue-400 focus:outline-none"
                :placeholder="$t('help.describeProblem')"
              ></textarea>
            </div>
            
            <div>
              <label class="mb-1 block text-sm font-medium text-slate-700">{{ $t('help.attachFile') }}</label>
              <div class="flex items-center gap-3">
                <input type="file" class="hidden" ref="fileInput" @change="handleFileSelect" />
                <button
                  @click="$refs.fileInput.click()"
                  class="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-slate-600 hover:bg-slate-50"
                >
                  <Paperclip :size="18" />
                  {{ $t('help.selectFile') }}
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
              {{ $t('common.cancel') }}
            </button>
            <button
              @click="submitContact"
              class="flex-1 rounded-xl bg-blue-500 py-3 font-medium text-white hover:bg-blue-600"
            >
              {{ $t('common.send') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import api from '@/services/api'
import { useLanguageStore } from '@/stores/language'
import { useToastStore } from '@/stores/toast'
import {
    Book,
    BookOpen,
    Calendar,
    ChevronDown,
    Download, ExternalLink,
    HelpCircle,
    MessageCircle,
    Paperclip,
    Phone,
    Play,
    Search,
    Send,
    Settings,
    ThumbsDown,
    ThumbsUp,
    User,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

const toast = useToastStore()
const { t } = useLanguageStore()

// State
const searchQuery = ref('')
const activeCategory = ref('all')
const openFaqs = ref([])
const showContactForm = ref(false)
const loading = ref(false)
const faqs = ref([])

const contactForm = ref({
  subject: '',
  message: '',
  file: null
})

// Load data on mount
onMounted(async () => {
  await loadFaqs()
})

async function loadFaqs() {
  loading.value = true
  try {
    const response = await api.getFaqs()
    const list = response?.items || response?.data || (Array.isArray(response) ? response : [])
    faqs.value = list.map(f => ({
      id: f.id,
      category: f.category || 'all',
      question: f.question,
      answer: f.answer
    }))
  } catch (err) {
    console.error('Load FAQs error:', err)
    // Keep empty faqs if API fails
  } finally {
    loading.value = false
  }
}

// Categories
const categories = computed(() => [
  { id: 'all', name: t('help.categories.all'), icon: HelpCircle },
  { id: 'attendance', name: t('help.categories.attendance'), icon: Calendar },
  { id: 'library', name: t('help.categories.library'), icon: Book },
  { id: 'settings', name: t('help.categories.settings'), icon: Settings },
  { id: 'profile', name: t('help.categories.profile'), icon: User }
])

// FAQs - Now loaded from API
// Removed hardcoded demo data

// Videos (placeholder - no API for this)
const videos = computed(() => [
  { id: 1, title: t('help.videoTitles.loginProfile'), thumbnail: 'https://picsum.photos/320/180?random=1', duration: '3:45' },
  { id: 2, title: t('help.videoTitles.viewAttendance'), thumbnail: 'https://picsum.photos/320/180?random=2', duration: '2:30' },
  { id: 3, title: t('help.videoTitles.useLibrary'), thumbnail: 'https://picsum.photos/320/180?random=3', duration: '5:15' }
])

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
  toast.success(helpful ? t('help.thanksFeedback') : t('help.willImprove'))
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    contactForm.value.file = file
  }
}

function submitContact() {
  if (!contactForm.value.subject || !contactForm.value.message) {
    toast.error(t('help.fillSubjectAndMessage'))
    return
  }
  
  // Here you would send to API
  toast.success(t('help.messageSent'))
  showContactForm.value = false
  contactForm.value = { subject: '', message: '', file: null }
}
</script>
