<template>
  <div class="bg-white/70 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-lg font-semibold text-slate-800">Excel Import</h2>
        <p class="text-sm text-slate-500">Excel yoki CSV fayldan ma'lumot yuklash</p>
      </div>
      <button
        v-if="currentStep > 1 && currentStep < 4"
        @click="currentStep--"
        class="flex items-center gap-2 px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        Orqaga
      </button>
    </div>

    <!-- Steps indicator -->
    <div class="flex items-center gap-2 mb-8">
      <div 
        v-for="step in 4" 
        :key="step"
        class="flex items-center gap-2"
      >
        <div 
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all',
            currentStep >= step 
              ? 'bg-emerald-500 text-white' 
              : 'bg-slate-100 text-slate-400'
          ]"
        >
          <Check v-if="currentStep > step" class="w-4 h-4" />
          <span v-else>{{ step }}</span>
        </div>
        <span :class="[
          'text-sm font-medium',
          currentStep >= step ? 'text-slate-800' : 'text-slate-400'
        ]">
          {{ stepNames[step - 1] }}
        </span>
        <ChevronRight v-if="step < 4" class="w-4 h-4 text-slate-300 mx-2" />
      </div>
    </div>

    <!-- Step 1: File Upload -->
    <div v-if="currentStep === 1" class="space-y-6">
      <div
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="[
          'border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer',
          isDragging 
            ? 'border-emerald-400 bg-emerald-50' 
            : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
        ]"
        @click="$refs.fileInput.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls,.csv"
          class="hidden"
          @change="handleFileSelect"
        />
        <div class="flex flex-col items-center gap-4">
          <div :class="[
            'w-20 h-20 rounded-2xl flex items-center justify-center transition-colors',
            isDragging ? 'bg-emerald-100' : 'bg-slate-100'
          ]">
            <FileSpreadsheet :class="[
              'w-10 h-10 transition-colors',
              isDragging ? 'text-emerald-500' : 'text-slate-400'
            ]" />
          </div>
          <div>
            <p class="text-lg font-medium text-slate-700">
              Excel yoki CSV faylni bu yerga tashlang
            </p>
            <p class="text-sm text-slate-400 mt-1">
              yoki <span class="text-emerald-500 font-medium">faylni tanlash</span> uchun bosing
            </p>
          </div>
          <div class="flex items-center gap-4 text-xs text-slate-400">
            <span class="flex items-center gap-1">
              <FileSpreadsheet class="w-4 h-4" /> .xlsx
            </span>
            <span class="flex items-center gap-1">
              <FileSpreadsheet class="w-4 h-4" /> .xls
            </span>
            <span class="flex items-center gap-1">
              <FileText class="w-4 h-4" /> .csv
            </span>
          </div>
        </div>
      </div>

      <!-- Recent imports -->
      <div v-if="recentImports.length > 0">
        <h3 class="text-sm font-medium text-slate-600 mb-3">Oxirgi importlar</h3>
        <div class="space-y-2">
          <div
            v-for="item in recentImports"
            :key="item.id"
            class="flex items-center justify-between p-3 bg-slate-50 rounded-xl"
          >
            <div class="flex items-center gap-3">
              <FileSpreadsheet class="w-5 h-5 text-emerald-500" />
              <div>
                <p class="text-sm font-medium text-slate-700">{{ item.name }}</p>
                <p class="text-xs text-slate-400">{{ item.rows }} qator • {{ item.date }}</p>
              </div>
            </div>
            <button class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
              <RefreshCw class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Column Mapping -->
    <div v-if="currentStep === 2" class="space-y-6">
      <div class="bg-emerald-50 rounded-xl p-4 flex items-start gap-3">
        <Info class="w-5 h-5 text-emerald-600 mt-0.5" />
        <div>
          <p class="text-sm font-medium text-emerald-800">
            {{ detectedColumns.length }} ta ustun aniqlandi
          </p>
          <p class="text-xs text-emerald-600 mt-0.5">
            Har bir ustunni kerakli maydon bilan bog'lang
          </p>
        </div>
      </div>

      <div class="grid gap-4">
        <div 
          v-for="(col, index) in detectedColumns"
          :key="index"
          class="flex items-center gap-4 p-4 bg-slate-50 rounded-xl"
        >
          <div class="flex-1">
            <p class="text-sm font-medium text-slate-700">{{ col.name }}</p>
            <p class="text-xs text-slate-400">
              Namuna: {{ col.sample }}
            </p>
          </div>
          <ArrowRight class="w-5 h-5 text-slate-300" />
          <select 
            v-model="col.mapping"
            class="w-48 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400"
          >
            <option value="">Tanlang...</option>
            <option v-for="field in availableFields" :key="field.value" :value="field.value">
              {{ field.label }}
            </option>
          </select>
          <div 
            v-if="col.autoDetected"
            class="flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-lg"
          >
            <Sparkles class="w-3 h-3" />
            Avtomatik
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-100">
        <p class="text-sm text-slate-500">
          {{ mappedCount }}/{{ requiredFields.length }} majburiy maydon bog'langan
        </p>
        <button
          :disabled="mappedCount < requiredFields.length"
          @click="currentStep = 3"
          :class="[
            'flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all',
            mappedCount >= requiredFields.length
              ? 'bg-emerald-500 text-white hover:bg-emerald-600'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          ]"
        >
          Davom etish
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Step 3: Group Detection -->
    <div v-if="currentStep === 3" class="space-y-6">
      <div class="bg-blue-50 rounded-xl p-4 flex items-start gap-3">
        <Users class="w-5 h-5 text-blue-600 mt-0.5" />
        <div>
          <p class="text-sm font-medium text-blue-800">
            {{ detectedGroups.length }} ta guruh aniqlandi
          </p>
          <p class="text-xs text-blue-600 mt-0.5">
            Talabalar avtomatik guruhlarga ajratildi
          </p>
        </div>
      </div>

      <div class="grid gap-4">
        <div 
          v-for="group in detectedGroups"
          :key="group.name"
          class="p-4 bg-slate-50 rounded-xl"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                <span class="text-white text-sm font-bold">{{ group.name.slice(0, 2) }}</span>
              </div>
              <div>
                <p class="font-medium text-slate-700">{{ group.name }}</p>
                <p class="text-xs text-slate-400">{{ group.students.length }} ta talaba</p>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input 
                type="checkbox" 
                v-model="group.import"
                class="w-4 h-4 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500/20"
              />
              <span class="text-sm text-slate-600">Import qilish</span>
            </label>
          </div>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="(student, i) in group.students.slice(0, 5)"
              :key="i"
              class="px-2 py-1 bg-white text-xs text-slate-600 rounded-lg"
            >
              {{ student }}
            </span>
            <span 
              v-if="group.students.length > 5"
              class="px-2 py-1 bg-slate-200 text-xs text-slate-500 rounded-lg"
            >
              +{{ group.students.length - 5 }} ta boshqa
            </span>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-100">
        <p class="text-sm text-slate-500">
          {{ selectedGroupsCount }} ta guruh tanlab olindi
        </p>
        <button
          :disabled="selectedGroupsCount === 0"
          @click="startImport"
          :class="[
            'flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all',
            selectedGroupsCount > 0
              ? 'bg-emerald-500 text-white hover:bg-emerald-600'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          ]"
        >
          <Upload class="w-4 h-4" />
          Import qilish
        </button>
      </div>
    </div>

    <!-- Step 4: Import Progress & Result -->
    <div v-if="currentStep === 4" class="space-y-6">
      <!-- Progress -->
      <div v-if="isImporting" class="text-center py-8">
        <div class="w-20 h-20 mx-auto mb-6 relative">
          <svg class="w-full h-full" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#e2e8f0"
              stroke-width="8"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#10b981"
              stroke-width="8"
              stroke-linecap="round"
              :stroke-dasharray="`${importProgress * 2.83} 283`"
              transform="rotate(-90 50 50)"
              class="transition-all duration-300"
            />
          </svg>
          <span class="absolute inset-0 flex items-center justify-center text-2xl font-bold text-emerald-600">
            {{ importProgress }}%
          </span>
        </div>
        <p class="text-lg font-medium text-slate-700">Import qilinmoqda...</p>
        <p class="text-sm text-slate-400 mt-1">{{ importStatus }}</p>
      </div>

      <!-- Success -->
      <div v-else class="text-center py-8">
        <div class="w-20 h-20 mx-auto mb-6 bg-emerald-100 rounded-full flex items-center justify-center">
          <CheckCircle class="w-10 h-10 text-emerald-500" />
        </div>
        <p class="text-xl font-semibold text-slate-800">Import muvaffaqiyatli!</p>
        <p class="text-sm text-slate-500 mt-2">
          {{ importResult.groups }} ta guruh, {{ importResult.students }} ta talaba qo'shildi
        </p>

        <div class="mt-8 p-4 bg-slate-50 rounded-xl text-left">
          <h4 class="text-sm font-medium text-slate-700 mb-3">Import natijalari:</h4>
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center p-3 bg-white rounded-lg">
              <p class="text-2xl font-bold text-emerald-600">{{ importResult.groups }}</p>
              <p class="text-xs text-slate-500">Guruh</p>
            </div>
            <div class="text-center p-3 bg-white rounded-lg">
              <p class="text-2xl font-bold text-blue-600">{{ importResult.students }}</p>
              <p class="text-xs text-slate-500">Talaba</p>
            </div>
            <div class="text-center p-3 bg-white rounded-lg">
              <p class="text-2xl font-bold text-orange-600">{{ importResult.skipped }}</p>
              <p class="text-xs text-slate-500">O'tkazib yuborildi</p>
            </div>
          </div>
        </div>

        <div class="flex justify-center gap-4 mt-8">
          <button
            @click="resetImport"
            class="flex items-center gap-2 px-6 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors"
          >
            <Plus class="w-4 h-4" />
            Yana import qilish
          </button>
          <button
            @click="$emit('completed', importResult)"
            class="flex items-center gap-2 px-6 py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium hover:bg-emerald-600 transition-colors"
          >
            Tayyor
            <ArrowRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  FileSpreadsheet, FileText, ArrowLeft, ArrowRight, Check, ChevronRight,
  Info, Sparkles, Users, Upload, CheckCircle, Plus, RefreshCw
} from 'lucide-vue-next'

const emit = defineEmits(['completed'])

const stepNames = ['Fayl yuklash', 'Ustunlar', 'Guruhlar', 'Natija']
const currentStep = ref(1)
const isDragging = ref(false)
const selectedFile = ref(null)
const isImporting = ref(false)
const importProgress = ref(0)
const importStatus = ref('')

const recentImports = ref([
  { id: 1, name: 'talabalar_2024.xlsx', rows: 245, date: '2 kun oldin' },
  { id: 2, name: 'yangi_qabul.csv', rows: 120, date: '1 hafta oldin' }
])

// Column mapping
const availableFields = [
  { value: 'fullName', label: 'To\'liq ism' },
  { value: 'firstName', label: 'Ism' },
  { value: 'lastName', label: 'Familiya' },
  { value: 'middleName', label: 'Otasining ismi' },
  { value: 'studentId', label: 'Talaba ID' },
  { value: 'group', label: 'Guruh' },
  { value: 'phone', label: 'Telefon' },
  { value: 'email', label: 'Email' },
  { value: 'birthDate', label: 'Tug\'ilgan sana' },
  { value: 'address', label: 'Manzil' },
  { value: 'parentPhone', label: 'Ota-ona telefoni' }
]

const requiredFields = ['fullName', 'group']

const detectedColumns = ref([])
const detectedGroups = ref([])

const mappedCount = computed(() => {
  return requiredFields.filter(field => 
    detectedColumns.value.some(col => col.mapping === field)
  ).length
})

const selectedGroupsCount = computed(() => {
  return detectedGroups.value.filter(g => g.import).length
})

const importResult = ref({
  groups: 0,
  students: 0,
  skipped: 0
})

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv'))) {
    processFile(file)
  }
}

function processFile(file) {
  selectedFile.value = file
  
  // Simulate parsing - in real app would use xlsx library
  // Auto-detect columns based on headers
  detectedColumns.value = [
    { name: 'F.I.O', sample: 'Aliyev Jasur Kamoliddin o\'g\'li', mapping: 'fullName', autoDetected: true },
    { name: 'Guruh', sample: '21-05', mapping: 'group', autoDetected: true },
    { name: 'Telefon raqam', sample: '+998901234567', mapping: 'phone', autoDetected: true },
    { name: 'Email', sample: 'jasur@mail.com', mapping: 'email', autoDetected: true },
    { name: 'Manzil', sample: 'Toshkent sh.', mapping: 'address', autoDetected: false },
    { name: 'Tug\'ilgan sana', sample: '15.03.2003', mapping: 'birthDate', autoDetected: true }
  ]
  
  currentStep.value = 2
}

function goToGroupDetection() {
  // Simulate group detection
  detectedGroups.value = [
    { 
      name: '21-05', 
      import: true, 
      students: ['Aliyev Jasur', 'Karimova Nilufar', 'Toshmatov Bekzod', 'Rahimova Madina', 'Usmonov Sardor', 'Yusupov Anvar', 'Mahmudova Zarina']
    },
    { 
      name: '21-06', 
      import: true, 
      students: ['Nazarov Bobur', 'Ergasheva Shahlo', 'Qodirov Sanjar', 'Tursunova Dilfuza', 'Ismoilov Javohir']
    },
    { 
      name: '21-07', 
      import: true, 
      students: ['Saidov Mirkomil', 'Xolmatova Ozoda', 'Abdullayev Farrux', 'Normurodova Zilola']
    }
  ]
  currentStep.value = 3
}

// Watch for step 2 completion
function startImport() {
  goToGroupDetection()
  
  // After groups are shown, continue if already at step 3
  if (currentStep.value === 3) {
    currentStep.value = 4
    isImporting.value = true
    importProgress.value = 0
    
    // Simulate import progress
    const interval = setInterval(() => {
      importProgress.value += Math.random() * 15
      
      if (importProgress.value < 30) {
        importStatus.value = 'Faylni tahlil qilish...'
      } else if (importProgress.value < 60) {
        importStatus.value = 'Guruhlarni yaratish...'
      } else if (importProgress.value < 90) {
        importStatus.value = 'Talabalarni qo\'shish...'
      } else {
        importStatus.value = 'Yakunlash...'
      }
      
      if (importProgress.value >= 100) {
        clearInterval(interval)
        importProgress.value = 100
        
        setTimeout(() => {
          isImporting.value = false
          const selectedGroups = detectedGroups.value.filter(g => g.import)
          importResult.value = {
            groups: selectedGroups.length,
            students: selectedGroups.reduce((sum, g) => sum + g.students.length, 0),
            skipped: 3
          }
        }, 500)
      }
    }, 300)
  }
}

function resetImport() {
  currentStep.value = 1
  selectedFile.value = null
  detectedColumns.value = []
  detectedGroups.value = []
  importProgress.value = 0
  isImporting.value = false
}
</script>
