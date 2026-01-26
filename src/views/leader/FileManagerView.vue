<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 md:text-3xl">Fayl boshqaruvchisi</h1>
        <p class="text-slate-500">Guruh hujjatlari va fayllarini boshqaring</p>
      </div>
      
      <div class="flex items-center gap-3">
        <button
          @click="viewMode = 'grid'"
          class="rounded-lg p-2 transition-colors"
          :class="viewMode === 'grid' ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
        >
          <Grid :size="20" />
        </button>
        <button
          @click="viewMode = 'list'"
          class="rounded-lg p-2 transition-colors"
          :class="viewMode === 'list' ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
        >
          <List :size="20" />
        </button>
        <button
          @click="showUploadModal = true"
          class="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-white hover:bg-emerald-600"
        >
          <Upload :size="18" />
          <span>Yuklash</span>
        </button>
      </div>
    </div>

    <!-- Breadcrumb -->
    <div class="mb-4 flex items-center gap-2 text-sm">
      <button
        v-for="(crumb, index) in breadcrumbs"
        :key="index"
        @click="navigateToFolder(crumb.path)"
        class="flex items-center gap-1 text-slate-500 hover:text-slate-800 transition-colors"
      >
        <Folder v-if="index > 0" :size="16" />
        <Home v-else :size="16" />
        <span>{{ crumb.name }}</span>
        <ChevronRight v-if="index < breadcrumbs.length - 1" :size="16" class="text-slate-300" />
      </button>
    </div>

    <!-- Search and Filter -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row">
      <div class="relative flex-1">
        <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Fayllarni qidirish..."
          class="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
        />
      </div>
      <select
        v-model="filterType"
        class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none"
      >
        <option value="all">Barchasi</option>
        <option value="document">Hujjatlar</option>
        <option value="image">Rasmlar</option>
        <option value="spreadsheet">Jadvallar</option>
        <option value="archive">Arxivlar</option>
      </select>
      <select
        v-model="sortBy"
        class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 focus:border-emerald-500 focus:outline-none"
      >
        <option value="name">Nom bo'yicha</option>
        <option value="date">Sana bo'yicha</option>
        <option value="size">O'lcham bo'yicha</option>
        <option value="type">Tur bo'yicha</option>
      </select>
    </div>

    <!-- Drag & Drop Zone -->
    <div
      v-if="isDragging"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm"
      @dragover.prevent
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div class="rounded-2xl border-2 border-dashed border-emerald-400 bg-emerald-500/10 p-12 text-center">
        <Upload :size="64" class="mx-auto mb-4 text-emerald-500" />
        <p class="text-xl font-medium text-white">Fayllarni shu yerga tashlang</p>
        <p class="mt-2 text-slate-300">Bir nechta faylni yuklash mumkin</p>
      </div>
    </div>

    <!-- Content -->
    <div
      @dragenter.prevent="isDragging = true"
      class="min-h-[400px]"
    >
      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        <!-- Folders -->
        <div
          v-for="folder in filteredFolders"
          :key="folder.id"
          @click="openFolder(folder)"
          @contextmenu.prevent="showContextMenu($event, folder, 'folder')"
          class="group cursor-pointer rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-emerald-300 hover:bg-slate-50 shadow-sm"
        >
          <div class="mb-3 flex justify-center">
            <Folder :size="48" class="text-yellow-500" />
          </div>
          <p class="truncate text-center text-sm font-medium text-slate-800">{{ folder.name }}</p>
          <p class="mt-1 text-center text-xs text-slate-500">{{ folder.itemCount }} ta element</p>
        </div>

        <!-- Files -->
        <div
          v-for="file in filteredFiles"
          :key="file.id"
          @click="selectFile(file)"
          @dblclick="previewFile(file)"
          @contextmenu.prevent="showContextMenu($event, file, 'file')"
          class="group cursor-pointer rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-emerald-300 hover:bg-slate-50 shadow-sm"
          :class="{ 'ring-2 ring-emerald-500': selectedFiles.includes(file.id) }"
        >
          <div class="mb-3 flex justify-center">
            <component :is="getFileIcon(file.type)" :size="48" :class="getFileIconColor(file.type)" />
          </div>
          <p class="truncate text-center text-sm font-medium text-slate-800" :title="file.name">{{ file.name }}</p>
          <p class="mt-1 text-center text-xs text-slate-500">{{ formatFileSize(file.size) }}</p>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
        <table class="w-full">
          <thead class="border-b border-slate-200 bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left text-sm font-medium text-slate-500">
                <input
                  type="checkbox"
                  @change="toggleSelectAll"
                  :checked="allSelected"
                  class="rounded border-slate-300"
                />
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-slate-500">Nom</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-slate-500">Tur</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-slate-500">O'lcham</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-slate-500">O'zgartirilgan</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-slate-500">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="folder in filteredFolders"
              :key="folder.id"
              @click="openFolder(folder)"
              @contextmenu.prevent="showContextMenu($event, folder, 'folder')"
              class="cursor-pointer border-b border-slate-100 transition-colors hover:bg-slate-50"
            >
              <td class="px-4 py-3">
                <input type="checkbox" @click.stop class="rounded border-slate-300" />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <Folder :size="20" class="text-yellow-500" />
                  <span class="text-slate-800">{{ folder.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-slate-500">Papka</td>
              <td class="px-4 py-3 text-slate-500">{{ folder.itemCount }} element</td>
              <td class="px-4 py-3 text-slate-500">{{ formatDate(folder.modified) }}</td>
              <td class="px-4 py-3">
                <button @click.stop="showContextMenu($event, folder, 'folder')" class="text-slate-400 hover:text-slate-600">
                  <MoreVertical :size="18" />
                </button>
              </td>
            </tr>
            <tr
              v-for="file in filteredFiles"
              :key="file.id"
              @click="selectFile(file)"
              @dblclick="previewFile(file)"
              @contextmenu.prevent="showContextMenu($event, file, 'file')"
              class="cursor-pointer border-b border-slate-100 transition-colors hover:bg-slate-50"
              :class="{ 'bg-emerald-50': selectedFiles.includes(file.id) }"
            >
              <td class="px-4 py-3">
                <input
                  type="checkbox"
                  :checked="selectedFiles.includes(file.id)"
                  @click.stop="toggleFileSelect(file.id)"
                  class="rounded border-slate-300"
                />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <component :is="getFileIcon(file.type)" :size="20" :class="getFileIconColor(file.type)" />
                  <span class="text-white">{{ file.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-slate-400">{{ getFileTypeName(file.type) }}</td>
              <td class="px-4 py-3 text-slate-400">{{ formatFileSize(file.size) }}</td>
              <td class="px-4 py-3 text-slate-400">{{ formatDate(file.modified) }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button @click.stop="downloadFile(file)" class="text-slate-400 hover:text-green-400">
                    <Download :size="18" />
                  </button>
                  <button @click.stop="previewFile(file)" class="text-slate-400 hover:text-blue-400">
                    <Eye :size="18" />
                  </button>
                  <button @click.stop="showContextMenu($event, file, 'file')" class="text-slate-400 hover:text-white">
                    <MoreVertical :size="18" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="filteredFiles.length === 0 && filteredFolders.length === 0" class="flex flex-col items-center justify-center py-20">
        <FolderOpen :size="64" class="mb-4 text-slate-600" />
        <h3 class="text-xl font-medium text-slate-400">Fayl topilmadi</h3>
        <p class="mt-2 text-slate-500">Fayllarni yuklash uchun yuqoridagi tugmani bosing</p>
      </div>
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div
        v-if="contextMenu.show"
        :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
        class="fixed z-50 min-w-[180px] rounded-lg border border-slate-600 bg-slate-800 py-2 shadow-xl"
        @click="contextMenu.show = false"
      >
        <button
          v-if="contextMenu.type === 'file'"
          @click="previewFile(contextMenu.item)"
          class="flex w-full items-center gap-3 px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-700"
        >
          <Eye :size="16" /> Ko'rish
        </button>
        <button
          @click="downloadFile(contextMenu.item)"
          class="flex w-full items-center gap-3 px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-700"
        >
          <Download :size="16" /> Yuklab olish
        </button>
        <button
          @click="renameItem(contextMenu.item)"
          class="flex w-full items-center gap-3 px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-700"
        >
          <Edit :size="16" /> Nomini o'zgartirish
        </button>
        <button
          @click="moveItem(contextMenu.item)"
          class="flex w-full items-center gap-3 px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-700"
        >
          <Move :size="16" /> Ko'chirish
        </button>
        <div class="my-2 border-t border-slate-700"></div>
        <button
          @click="deleteItem(contextMenu.item)"
          class="flex w-full items-center gap-3 px-4 py-2 text-left text-sm text-red-400 hover:bg-slate-700"
        >
          <Trash2 :size="16" /> O'chirish
        </button>
      </div>
    </Teleport>

    <!-- Upload Modal -->
    <Teleport to="body">
      <div
        v-if="showUploadModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="showUploadModal = false"
      >
        <div class="w-full max-w-xl rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-bold text-white">Fayl yuklash</h2>
            <button @click="showUploadModal = false" class="text-slate-400 hover:text-white">
              <X :size="24" />
            </button>
          </div>

          <!-- Drop Zone -->
          <div
            @dragover.prevent="uploadDragover = true"
            @dragleave="uploadDragover = false"
            @drop.prevent="handleUploadDrop"
            @click="$refs.fileInput.click()"
            class="mb-4 cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors"
            :class="uploadDragover ? 'border-blue-400 bg-blue-500/10' : 'border-slate-600 hover:border-slate-500'"
          >
            <Upload :size="48" class="mx-auto mb-4 text-slate-400" />
            <p class="text-lg font-medium text-white">Fayllarni tanlang yoki tashlang</p>
            <p class="mt-2 text-sm text-slate-400">PNG, JPG, PDF, DOC, XLS (max 50MB)</p>
            <input
              ref="fileInput"
              type="file"
              multiple
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

          <!-- Upload Queue -->
          <div v-if="uploadQueue.length > 0" class="max-h-60 space-y-2 overflow-y-auto">
            <div
              v-for="item in uploadQueue"
              :key="item.id"
              class="flex items-center gap-3 rounded-lg bg-slate-700/50 p-3"
            >
              <component :is="getFileIcon(getFileType(item.file.name))" :size="24" class="text-slate-400" />
              <div class="flex-1 min-w-0">
                <p class="truncate text-sm font-medium text-white">{{ item.file.name }}</p>
                <p class="text-xs text-slate-400">{{ formatFileSize(item.file.size) }}</p>
                <div v-if="item.progress > 0 && item.progress < 100" class="mt-1 h-1 rounded-full bg-slate-600">
                  <div
                    class="h-full rounded-full bg-blue-500 transition-all"
                    :style="{ width: item.progress + '%' }"
                  ></div>
                </div>
              </div>
              <span v-if="item.status === 'done'" class="text-green-400">
                <CheckCircle :size="20" />
              </span>
              <span v-else-if="item.status === 'error'" class="text-red-400">
                <XCircle :size="20" />
              </span>
              <button v-else @click="removeFromQueue(item.id)" class="text-slate-400 hover:text-red-400">
                <X :size="20" />
              </button>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-4 flex justify-end gap-3">
            <button
              @click="showUploadModal = false"
              class="rounded-lg border border-slate-600 px-4 py-2 text-slate-300 hover:bg-slate-700"
            >
              Bekor qilish
            </button>
            <button
              @click="startUpload"
              :disabled="uploadQueue.length === 0 || uploading"
              class="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
            >
              <Loader2 v-if="uploading" :size="18" class="animate-spin" />
              <Upload v-else :size="18" />
              {{ uploading ? 'Yuklanmoqda...' : 'Yuklash' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Preview Modal -->
    <Teleport to="body">
      <div
        v-if="previewModal.show"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
        @click.self="previewModal.show = false"
      >
        <div class="w-full max-w-4xl max-h-[90vh] rounded-2xl border border-slate-700 bg-slate-800 overflow-hidden">
          <div class="flex items-center justify-between border-b border-slate-700 p-4">
            <h2 class="text-lg font-bold text-white">{{ previewModal.file?.name }}</h2>
            <div class="flex items-center gap-2">
              <button @click="downloadFile(previewModal.file)" class="rounded-lg p-2 text-slate-400 hover:bg-slate-700 hover:text-white">
                <Download :size="20" />
              </button>
              <button @click="previewModal.show = false" class="rounded-lg p-2 text-slate-400 hover:bg-slate-700 hover:text-white">
                <X :size="20" />
              </button>
            </div>
          </div>
          <div class="flex items-center justify-center p-8 min-h-[400px]">
            <img
              v-if="previewModal.file?.type === 'image'"
              :src="previewModal.file?.url"
              :alt="previewModal.file?.name"
              class="max-w-full max-h-[60vh] rounded-lg"
            />
            <div v-else class="text-center">
              <component :is="getFileIcon(previewModal.file?.type)" :size="96" class="mx-auto mb-4 text-slate-400" />
              <p class="text-lg font-medium text-white">{{ previewModal.file?.name }}</p>
              <p class="mt-2 text-slate-400">{{ formatFileSize(previewModal.file?.size) }}</p>
              <button
                @click="downloadFile(previewModal.file)"
                class="mt-4 rounded-lg bg-blue-500 px-6 py-2 text-white hover:bg-blue-600"
              >
                Yuklab olish
              </button>
            </div>
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
  Grid, List, Upload, Search, Folder, FolderOpen, Home, ChevronRight,
  FileText, Image, File, FileSpreadsheet, FileArchive, Download, Eye,
  MoreVertical, Edit, Move, Trash2, X, CheckCircle, XCircle, Loader2
} from 'lucide-vue-next'

const toast = useToastStore()

// State
const viewMode = ref('grid')
const searchQuery = ref('')
const filterType = ref('all')
const sortBy = ref('name')
const currentPath = ref('/')
const isDragging = ref(false)
const selectedFiles = ref([])
const showUploadModal = ref(false)
const uploadDragover = ref(false)
const uploadQueue = ref([])
const uploading = ref(false)

const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  item: null,
  type: null
})

const previewModal = ref({
  show: false,
  file: null
})

// Demo data
const folders = ref([
  { id: 1, name: 'Hisobotlar', path: '/hisobotlar', itemCount: 12, modified: '2024-01-15' },
  { id: 2, name: 'Talabalar ma\'lumotlari', path: '/talabalar', itemCount: 45, modified: '2024-01-14' },
  { id: 3, name: 'Kontrakt hujjatlari', path: '/kontrakt', itemCount: 23, modified: '2024-01-13' },
  { id: 4, name: 'Jadvallar', path: '/jadvallar', itemCount: 8, modified: '2024-01-12' }
])

const files = ref([
  { id: 1, name: 'Davomat_yanvar_2024.xlsx', type: 'spreadsheet', size: 245760, modified: '2024-01-15', url: '' },
  { id: 2, name: 'Guruh_royxati.pdf', type: 'document', size: 1048576, modified: '2024-01-14', url: '' },
  { id: 3, name: 'Kontrakt_namuna.docx', type: 'document', size: 524288, modified: '2024-01-13', url: '' },
  { id: 4, name: 'Talabalar_foto.jpg', type: 'image', size: 2097152, modified: '2024-01-12', url: 'https://picsum.photos/800/600' },
  { id: 5, name: 'Arxiv_2023.zip', type: 'archive', size: 10485760, modified: '2024-01-11', url: '' },
  { id: 6, name: 'Dars_jadvali.xlsx', type: 'spreadsheet', size: 153600, modified: '2024-01-10', url: '' }
])

// Computed
const breadcrumbs = computed(() => {
  const parts = currentPath.value.split('/').filter(Boolean)
  const crumbs = [{ name: 'Asosiy', path: '/' }]
  let path = ''
  parts.forEach(part => {
    path += '/' + part
    crumbs.push({ name: part, path })
  })
  return crumbs
})

const filteredFolders = computed(() => {
  return folders.value.filter(f => {
    if (searchQuery.value) {
      return f.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    }
    return true
  })
})

const filteredFiles = computed(() => {
  let result = files.value

  if (searchQuery.value) {
    result = result.filter(f => f.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }

  if (filterType.value !== 'all') {
    result = result.filter(f => f.type === filterType.value)
  }

  // Sort
  result = [...result].sort((a, b) => {
    switch (sortBy.value) {
      case 'name': return a.name.localeCompare(b.name)
      case 'date': return new Date(b.modified) - new Date(a.modified)
      case 'size': return b.size - a.size
      case 'type': return a.type.localeCompare(b.type)
      default: return 0
    }
  })

  return result
})

const allSelected = computed(() => {
  return filteredFiles.value.length > 0 && 
    filteredFiles.value.every(f => selectedFiles.value.includes(f.id))
})

// Methods
function openFolder(folder) {
  currentPath.value = folder.path
}

function navigateToFolder(path) {
  currentPath.value = path
}

function selectFile(file) {
  const index = selectedFiles.value.indexOf(file.id)
  if (index === -1) {
    selectedFiles.value.push(file.id)
  } else {
    selectedFiles.value.splice(index, 1)
  }
}

function toggleFileSelect(fileId) {
  const index = selectedFiles.value.indexOf(fileId)
  if (index === -1) {
    selectedFiles.value.push(fileId)
  } else {
    selectedFiles.value.splice(index, 1)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedFiles.value = []
  } else {
    selectedFiles.value = filteredFiles.value.map(f => f.id)
  }
}

function showContextMenu(event, item, type) {
  contextMenu.value = {
    show: true,
    x: Math.min(event.clientX, window.innerWidth - 200),
    y: Math.min(event.clientY, window.innerHeight - 200),
    item,
    type
  }
}

function previewFile(file) {
  previewModal.value = {
    show: true,
    file
  }
}

function downloadFile(file) {
  toast.success(`"${file.name}" yuklab olinmoqda...`)
  // Simulate download
  setTimeout(() => {
    toast.success(`"${file.name}" yuklandi!`)
  }, 1500)
}

function renameItem(item) {
  const newName = prompt('Yangi nomni kiriting:', item.name)
  if (newName && newName !== item.name) {
    item.name = newName
    toast.success('Nom o\'zgartirildi')
  }
}

function moveItem(item) {
  toast.info('Ko\'chirish funksiyasi ishlab chiqilmoqda...')
}

function deleteItem(item) {
  if (confirm(`"${item.name}" ni o'chirmoqchimisiz?`)) {
    if (contextMenu.value.type === 'folder') {
      folders.value = folders.value.filter(f => f.id !== item.id)
    } else {
      files.value = files.value.filter(f => f.id !== item.id)
    }
    toast.success('O\'chirildi')
  }
}

function handleDrop(event) {
  isDragging.value = false
  const droppedFiles = Array.from(event.dataTransfer.files)
  addToUploadQueue(droppedFiles)
  showUploadModal.value = true
}

function handleUploadDrop(event) {
  uploadDragover.value = false
  const droppedFiles = Array.from(event.dataTransfer.files)
  addToUploadQueue(droppedFiles)
}

function handleFileSelect(event) {
  const selectedFiles = Array.from(event.target.files)
  addToUploadQueue(selectedFiles)
}

function addToUploadQueue(newFiles) {
  newFiles.forEach(file => {
    uploadQueue.value.push({
      id: Date.now() + Math.random(),
      file,
      progress: 0,
      status: 'pending'
    })
  })
}

function removeFromQueue(id) {
  uploadQueue.value = uploadQueue.value.filter(item => item.id !== id)
}

function startUpload() {
  uploading.value = true
  
  uploadQueue.value.forEach((item, index) => {
    setTimeout(() => {
      // Simulate upload progress
      let progress = 0
      const interval = setInterval(() => {
        progress += Math.random() * 30
        if (progress >= 100) {
          progress = 100
          clearInterval(interval)
          item.status = 'done'
          item.progress = 100
          
          // Add to files list
          files.value.unshift({
            id: Date.now(),
            name: item.file.name,
            type: getFileType(item.file.name),
            size: item.file.size,
            modified: new Date().toISOString().split('T')[0],
            url: ''
          })
          
          // Check if all done
          if (uploadQueue.value.every(q => q.status === 'done')) {
            uploading.value = false
            toast.success('Barcha fayllar yuklandi!')
            setTimeout(() => {
              showUploadModal.value = false
              uploadQueue.value = []
            }, 1000)
          }
        } else {
          item.progress = progress
        }
      }, 200)
    }, index * 500)
  })
}

function getFileType(filename) {
  const ext = filename.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image'
  if (['doc', 'docx', 'pdf', 'txt'].includes(ext)) return 'document'
  if (['xls', 'xlsx', 'csv'].includes(ext)) return 'spreadsheet'
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return 'archive'
  return 'document'
}

function getFileIcon(type) {
  switch (type) {
    case 'image': return Image
    case 'spreadsheet': return FileSpreadsheet
    case 'archive': return FileArchive
    case 'document': return FileText
    default: return File
  }
}

function getFileIconColor(type) {
  switch (type) {
    case 'image': return 'text-purple-400'
    case 'spreadsheet': return 'text-green-400'
    case 'archive': return 'text-yellow-400'
    case 'document': return 'text-blue-400'
    default: return 'text-slate-400'
  }
}

function getFileTypeName(type) {
  const names = {
    image: 'Rasm',
    spreadsheet: 'Jadval',
    archive: 'Arxiv',
    document: 'Hujjat'
  }
  return names[type] || 'Fayl'
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(date) {
  return new Date(date).toLocaleDateString('uz-UZ', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Close context menu on click outside
document.addEventListener('click', () => {
  contextMenu.value.show = false
})
</script>
