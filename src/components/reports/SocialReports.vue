<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div class="bg-white/70 backdrop-blur-sm rounded-2xl border border-slate-200/60 p-1.5 inline-flex">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-6 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
          activeTab === tab.id
            ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30'
            : 'text-slate-600 hover:bg-slate-100'
        ]"
      >
        <component :is="tab.icon" class="w-4 h-4 inline-block mr-2" />
        {{ tab.label }}
      </button>
    </div>

    <!-- My Reports Tab -->
    <div v-if="activeTab === 'my'">
      <!-- Month Selector -->
      <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-slate-800">Mening hisobotlarim</h2>
          <div class="flex items-center gap-2">
            <button
              @click="prevMonth"
              class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              <ChevronLeft class="w-5 h-5" />
            </button>
            <span class="px-4 py-2 bg-slate-50 rounded-xl font-medium text-slate-700">
              {{ currentMonthName }} {{ currentYear }}
            </span>
            <button
              @click="nextMonth"
              :disabled="isCurrentMonth"
              :class="[
                'p-2 rounded-xl transition-colors',
                isCurrentMonth 
                  ? 'text-slate-300 cursor-not-allowed' 
                  : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
              ]"
            >
              <ChevronRight class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Current Month Report -->
        <div v-if="isCurrentMonth" class="mb-6">
          <div v-if="!hasCurrentMonthReport" class="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-2xl p-6 border border-emerald-200/50">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                <FilePlus class="w-6 h-6 text-emerald-600" />
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-emerald-800">Joriy oy hisoboti</h3>
                <p class="text-sm text-emerald-600 mt-1">
                  {{ currentMonthName }} oyi uchun hisobot hali yozilmagan
                </p>
                <button
                  @click="showReportModal = true"
                  class="mt-4 flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium hover:bg-emerald-600 transition-colors"
                >
                  <Plus class="w-4 h-4" />
                  Hisobot yozish
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Reports List -->
        <div class="space-y-4">
          <div 
            v-for="report in filteredReports"
            :key="report.id"
            class="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-lg transition-all duration-300"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                  <FileText class="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 class="font-medium text-slate-800">{{ report.title }}</h3>
                  <p class="text-xs text-slate-400">{{ formatDate(report.createdAt) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="[
                  'px-2.5 py-1 rounded-lg text-xs font-medium',
                  report.status === 'approved' ? 'bg-emerald-100 text-emerald-700' :
                  report.status === 'pending' ? 'bg-amber-100 text-amber-700' :
                  'bg-slate-100 text-slate-600'
                ]">
                  {{ getStatusLabel(report.status) }}
                </span>
              </div>
            </div>

            <p class="text-sm text-slate-600 line-clamp-2 mb-4">{{ report.content }}</p>

            <!-- Stats -->
            <div class="flex items-center justify-between pt-4 border-t border-slate-100">
              <div class="flex items-center gap-4">
                <div class="flex items-center gap-1.5 text-slate-400">
                  <Eye class="w-4 h-4" />
                  <span class="text-sm">{{ report.views }}</span>
                </div>
                <div class="flex items-center gap-1.5 text-slate-400">
                  <Heart :class="['w-4 h-4', report.isLiked && 'fill-rose-500 text-rose-500']" />
                  <span class="text-sm">{{ report.likes }}</span>
                </div>
                <div class="flex items-center gap-1.5 text-slate-400">
                  <MessageCircle class="w-4 h-4" />
                  <span class="text-sm">{{ report.comments }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="editReport(report)"
                  class="p-2 text-slate-400 hover:text-emerald-500 hover:bg-emerald-50 rounded-lg transition-colors"
                >
                  <Edit2 class="w-4 h-4" />
                </button>
                <button
                  @click="viewReport(report)"
                  class="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <ExternalLink class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredReports.length === 0" class="text-center py-12">
            <FileX class="w-16 h-16 mx-auto text-slate-300 mb-4" />
            <p class="text-slate-500">Bu oy uchun hisobotlar topilmadi</p>
          </div>
        </div>
      </div>
    </div>

    <!-- All Reports Tab -->
    <div v-if="activeTab === 'all'">
      <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-slate-800">Barcha hisobotlar</h2>
          <div class="flex items-center gap-3">
            <!-- Filter -->
            <select
              v-model="filter"
              class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
            >
              <option value="all">Barcha fakultetlar</option>
              <option value="iqtisodiyot">Iqtisodiyot</option>
              <option value="informatika">Informatika</option>
              <option value="huquq">Huquqshunoslik</option>
            </select>
            <!-- Sort -->
            <select
              v-model="sortBy"
              class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
            >
              <option value="recent">Eng yangi</option>
              <option value="popular">Eng ko'p ko'rilgan</option>
              <option value="liked">Eng ko'p layk</option>
            </select>
          </div>
        </div>

        <!-- Reports Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="report in allReports"
            :key="report.id"
            class="bg-white rounded-2xl border border-slate-200/60 overflow-hidden hover:shadow-lg transition-all duration-300"
          >
            <!-- Header with author -->
            <div class="p-4 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-semibold text-sm">
                  {{ report.author.name.charAt(0) }}
                </div>
                <div>
                  <p class="font-medium text-slate-800">{{ report.author.name }}</p>
                  <p class="text-xs text-slate-400">{{ report.author.group }} • {{ formatDate(report.createdAt) }}</p>
                </div>
              </div>
            </div>

            <!-- Content -->
            <div class="p-4">
              <h3 class="font-medium text-slate-800 mb-2">{{ report.title }}</h3>
              <p class="text-sm text-slate-500 line-clamp-3">{{ report.content }}</p>
            </div>

            <!-- Footer -->
            <div class="px-4 py-3 bg-slate-50 border-t border-slate-100">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="flex items-center gap-1.5 text-slate-400">
                    <Eye class="w-4 h-4" />
                    <span class="text-sm">{{ report.views }}</span>
                  </div>
                  <button
                    @click="toggleLike(report)"
                    :class="[
                      'flex items-center gap-1.5 transition-colors',
                      report.isLiked ? 'text-rose-500' : 'text-slate-400 hover:text-rose-500'
                    ]"
                  >
                    <Heart :class="['w-4 h-4', report.isLiked && 'fill-rose-500']" />
                    <span class="text-sm">{{ report.likes }}</span>
                  </button>
                </div>
                <button
                  @click="viewReport(report)"
                  class="flex items-center gap-1.5 text-sm text-emerald-600 hover:text-emerald-700 font-medium"
                >
                  Ko'rish
                  <ArrowRight class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div class="mt-6 text-center">
          <button
            class="px-6 py-2.5 bg-slate-100 text-slate-600 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors"
          >
            Ko'proq yuklash
          </button>
        </div>
      </div>
    </div>

    <!-- Report Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showReportModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
        >
          <div class="w-full max-w-2xl bg-white rounded-3xl shadow-xl overflow-hidden">
            <!-- Modal Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h3 class="text-lg font-semibold text-slate-800">
                {{ editingReport ? 'Hisobotni tahrirlash' : 'Yangi hisobot' }}
              </h3>
              <button
                @click="closeModal"
                class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Modal Body -->
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Sarlavha</label>
                <input
                  v-model="reportForm.title"
                  type="text"
                  placeholder="Hisobot sarlavhasi"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Matn</label>
                <textarea
                  v-model="reportForm.content"
                  rows="8"
                  placeholder="Hisobot matnini kiriting..."
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 resize-none"
                ></textarea>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Fayl biriktirish</label>
                <div class="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center hover:border-emerald-300 transition-colors cursor-pointer">
                  <Upload class="w-8 h-8 mx-auto text-slate-400 mb-2" />
                  <p class="text-sm text-slate-500">Fayl yuklash uchun bosing</p>
                </div>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="flex items-center justify-end gap-3 px-6 py-4 bg-slate-50 border-t border-slate-100">
              <button
                @click="closeModal"
                class="px-6 py-2.5 text-slate-600 hover:bg-slate-100 rounded-xl text-sm font-medium transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="saveReport"
                class="px-6 py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium hover:bg-emerald-600 transition-colors"
              >
                Saqlash
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  FileText, FilePlus, Plus, ChevronLeft, ChevronRight, Eye, Heart, MessageCircle,
  Edit2, ExternalLink, FileX, ArrowRight, X, Upload
} from 'lucide-vue-next'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const tabs = [
  { id: 'my', label: 'Hisobotlarim', icon: FileText },
  { id: 'all', label: 'Barcha hisobotlar', icon: Eye }
]

const activeTab = ref('my')
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const filter = ref('all')
const sortBy = ref('recent')
const showReportModal = ref(false)
const editingReport = ref(null)

const reportForm = ref({
  title: '',
  content: ''
})

const months = [
  'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
  'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'
]

const currentMonthName = computed(() => months[currentMonth.value])

const isCurrentMonth = computed(() => {
  const now = new Date()
  return currentMonth.value === now.getMonth() && currentYear.value === now.getFullYear()
})

// Demo data - my reports
const myReports = ref([
  {
    id: 1,
    title: 'Yanvar oyi faoliyati haqida hisobot',
    content: 'Yanvar oyida guruhimiz faoliyati yuqori darajada bo\'ldi. Davomat 85% ni tashkil etdi. 3 ta tadbirda ishtirok etdik...',
    month: 0,
    year: 2024,
    status: 'approved',
    views: 45,
    likes: 12,
    comments: 3,
    isLiked: false,
    createdAt: new Date(2024, 0, 28)
  },
  {
    id: 2,
    title: 'Dekabr oyi yakuni',
    content: 'Dekabr oyida guruhimiz 4 ta imtihondan muvaffaqiyatli o\'tdi. O\'rtacha baho 4.2 ni tashkil etdi...',
    month: 11,
    year: 2023,
    status: 'approved',
    views: 67,
    likes: 18,
    comments: 5,
    isLiked: true,
    createdAt: new Date(2023, 11, 25)
  }
])

// Demo data - all reports from other leaders
const allReports = ref([
  {
    id: 101,
    title: 'Qishki sessiya natijalari',
    content: 'Bizning guruhimiz qishki sessiyani muvaffaqiyatli yakunladi. 95% talabalar barcha fanlardan o\'tdi...',
    author: { name: 'Karimova Nodira', group: '21-06' },
    views: 234,
    likes: 45,
    isLiked: true,
    createdAt: new Date(2024, 0, 20)
  },
  {
    id: 102,
    title: 'Sport musobaqalari g\'oliblari',
    content: 'Universitet sport musobaqalarida bizning guruh futbol bo\'yicha 1-o\'rinni egalladi...',
    author: { name: 'Rahimov Jasur', group: '22-03' },
    views: 189,
    likes: 67,
    isLiked: false,
    createdAt: new Date(2024, 0, 18)
  },
  {
    id: 103,
    title: 'Xayriya aksiyasi',
    content: 'Guruhimiz tashabbusi bilan xayriya aksiyasi o\'tkazildi. 50 ta oilaga yordam ko\'rsatildi...',
    author: { name: 'Tursunova Malika', group: '20-12' },
    views: 312,
    likes: 89,
    isLiked: false,
    createdAt: new Date(2024, 0, 15)
  },
  {
    id: 104,
    title: 'Ilmiy konferensiya',
    content: 'Talabalarimiz respublika ilmiy konferensiyasida 3 ta maqola bilan ishtirok etishdi...',
    author: { name: 'Ergashev Bobur', group: '21-08' },
    views: 156,
    likes: 34,
    isLiked: true,
    createdAt: new Date(2024, 0, 10)
  }
])

const hasCurrentMonthReport = computed(() => {
  const now = new Date()
  return myReports.value.some(r => r.month === now.getMonth() && r.year === now.getFullYear())
})

const filteredReports = computed(() => {
  return myReports.value.filter(r => r.month === currentMonth.value && r.year === currentYear.value)
})

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (isCurrentMonth.value) return
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

function formatDate(date) {
  return new Date(date).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function getStatusLabel(status) {
  const labels = {
    approved: 'Tasdiqlangan',
    pending: 'Kutilmoqda',
    draft: 'Qoralama'
  }
  return labels[status] || status
}

function toggleLike(report) {
  report.isLiked = !report.isLiked
  report.likes += report.isLiked ? 1 : -1
}

function viewReport(report) {
  // Navigate to report detail or show modal
  console.log('View report', report.id)
}

function editReport(report) {
  editingReport.value = report
  reportForm.value = {
    title: report.title,
    content: report.content
  }
  showReportModal.value = true
}

function closeModal() {
  showReportModal.value = false
  editingReport.value = null
  reportForm.value = { title: '', content: '' }
}

function saveReport() {
  if (!reportForm.value.title || !reportForm.value.content) {
    toast.warning('Iltimos, barcha maydonlarni to\'ldiring')
    return
  }

  if (editingReport.value) {
    // Update existing report
    const index = myReports.value.findIndex(r => r.id === editingReport.value.id)
    if (index !== -1) {
      myReports.value[index].title = reportForm.value.title
      myReports.value[index].content = reportForm.value.content
    }
    toast.success('Hisobot yangilandi')
  } else {
    // Create new report
    const now = new Date()
    myReports.value.unshift({
      id: Date.now(),
      title: reportForm.value.title,
      content: reportForm.value.content,
      month: now.getMonth(),
      year: now.getFullYear(),
      status: 'pending',
      views: 0,
      likes: 0,
      comments: 0,
      isLiked: false,
      createdAt: now
    })
    toast.success('Hisobot qo\'shildi')
  }

  closeModal()
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

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95);
}
</style>
