<template>
  <Teleport to="body">
    <Transition name="search-fade">
      <div v-if="isOpen" class="fixed inset-0 z-[60] flex items-start justify-center pt-[15vh] px-4" @click.self="close">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="close"></div>
        
        <!-- Search Modal -->
        <div class="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden" @click.stop>
          <!-- Search Input -->
          <div class="flex items-center gap-3 px-5 py-4 border-b border-slate-100">
            <Search class="w-5 h-5 text-slate-400 flex-shrink-0" />
            <input
              ref="searchInput"
              v-model="query"
              @input="debouncedSearch"
              @keydown.down.prevent="moveDown"
              @keydown.up.prevent="moveUp"
              @keydown.enter.prevent="selectCurrent"
              @keydown.escape="close"
              type="text"
              :placeholder="t('search.placeholder')"
              class="flex-1 text-base text-slate-800 placeholder-slate-400 outline-none bg-transparent"
              autocomplete="off"
            />
            <kbd class="hidden sm:inline-flex items-center px-2 py-0.5 text-xs text-slate-400 bg-slate-100 rounded font-mono">ESC</kbd>
          </div>

          <!-- Results -->
          <div class="max-h-[50vh] overflow-y-auto" v-if="query.length > 0">
            <!-- Loading -->
            <div v-if="searching" class="flex items-center gap-3 px-5 py-8 justify-center text-slate-400">
              <Loader2 class="w-5 h-5 animate-spin" />
              <span class="text-sm">{{ t('search.searching') }}</span>
            </div>

            <!-- Results List -->
            <div v-else-if="results.length > 0" class="py-2">
              <!-- Group by type -->
              <template v-for="group in groupedResults" :key="group.type">
                <div class="px-5 py-1.5">
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ group.label }}</p>
                </div>
                <div
                  v-for="(item, idx) in group.items"
                  :key="item.id + '-' + item.type"
                  @click="selectItem(item)"
                  @mouseenter="activeIndex = getGlobalIndex(group.type, idx)"
                  class="flex items-center gap-3 px-5 py-3 cursor-pointer transition-colors"
                  :class="activeIndex === getGlobalIndex(group.type, idx) ? 'bg-emerald-50' : 'hover:bg-slate-50'"
                >
                  <!-- Icon -->
                  <div 
                    class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                    :class="getTypeIconBg(item.type)"
                  >
                    <component :is="getTypeIcon(item.type)" class="w-4 h-4" :class="getTypeIconColor(item.type)" />
                  </div>
                  <!-- Info -->
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-slate-800 truncate" v-html="highlight(item.title)"></p>
                    <p v-if="item.subtitle" class="text-xs text-slate-400 truncate" v-html="highlight(item.subtitle)"></p>
                  </div>
                  <!-- Arrow -->
                  <ChevronRight class="w-4 h-4 text-slate-300 flex-shrink-0" />
                </div>
              </template>
            </div>

            <!-- No Results -->
            <div v-else-if="!searching && query.length >= 2" class="px-5 py-12 text-center">
              <SearchX class="w-10 h-10 text-slate-300 mx-auto mb-3" />
              <p class="text-sm text-slate-500">{{ t('search.noResults') }}</p>
              <p class="text-xs text-slate-400 mt-1">{{ t('search.tryAgain') }}</p>
            </div>

            <!-- Type more -->
            <div v-else-if="query.length < 2" class="px-5 py-8 text-center">
              <p class="text-sm text-slate-400">{{ t('search.typeMore') }}</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-5 py-2.5 border-t border-slate-100 flex items-center gap-4 text-[11px] text-slate-400 bg-slate-50/50">
            <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 bg-slate-200 rounded text-[10px] font-mono">↑↓</kbd> {{ t('search.navigate') }}</span>
            <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 bg-slate-200 rounded text-[10px] font-mono">↵</kbd> {{ t('search.select') }}</span>
            <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 bg-slate-200 rounded text-[10px] font-mono">esc</kbd> {{ t('search.close') }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useLanguageStore } from '@/stores/language'
import { useAuthStore } from '@/stores/auth'
import {
    Building2,
    ChevronRight,
    GraduationCap,
    Loader2,
    Search,
    SearchX,
    User
} from 'lucide-vue-next'
import { computed, markRaw, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

const router = useRouter()
const authStore = useAuthStore()
const { t } = useLanguageStore()

const searchInput = ref(null)
const query = ref('')
const results = ref([])
const searching = ref(false)
const activeIndex = ref(0)

let searchTimeout = null

const isOpen = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

watch(isOpen, (val) => {
  if (val) {
    query.value = ''
    results.value = []
    activeIndex.value = 0
    nextTick(() => searchInput.value?.focus())
  }
})

const close = () => {
  isOpen.value = false
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  if (query.value.length < 2) {
    results.value = []
    return
  }
  searching.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const response = await api.globalSearch(query.value)
      results.value = response.results || []
      activeIndex.value = 0
    } catch (e) {
      console.error('Search error:', e)
      results.value = []
    } finally {
      searching.value = false
    }
  }, 300)
}

// Group results by type
const groupedResults = computed(() => {
  const groups = {}
  const typeLabels = {
    student: t('search.students'),
    user: t('search.users'),
    group: t('search.groups')
  }
  const typeOrder = ['student', 'user', 'group']
  
  for (const item of results.value) {
    if (!groups[item.type]) {
      groups[item.type] = {
        type: item.type,
        label: typeLabels[item.type] || item.type,
        items: []
      }
    }
    groups[item.type].items.push(item)
  }
  
  return typeOrder.filter(t => groups[t]).map(t => groups[t])
})

// Get global index for keyboard navigation
const getGlobalIndex = (type, localIdx) => {
  let idx = 0
  for (const group of groupedResults.value) {
    if (group.type === type) return idx + localIdx
    idx += group.items.length
  }
  return idx + localIdx
}

const flatResults = computed(() => {
  const flat = []
  for (const group of groupedResults.value) {
    flat.push(...group.items)
  }
  return flat
})

const moveDown = () => {
  if (activeIndex.value < flatResults.value.length - 1) {
    activeIndex.value++
  }
}

const moveUp = () => {
  if (activeIndex.value > 0) {
    activeIndex.value--
  }
}

const selectCurrent = () => {
  const item = flatResults.value[activeIndex.value]
  if (item) selectItem(item)
}

const selectItem = (item) => {
  close()
  
  // Determine the route based on role and item type
  const role = authStore.user?.role
  const rolePrefix = role === 'superadmin' ? '/super' : role === 'admin' ? '/admin' : role === 'leader' ? '/leader' : '/student'
  
  if (item.type === 'student') {
    router.push(`${rolePrefix}/students`)
  } else if (item.type === 'user') {
    router.push(`${rolePrefix}/users`)
  } else if (item.type === 'group') {
    router.push(`${rolePrefix}/groups`)
  }
}

const highlight = (text) => {
  if (!text || !query.value) return text
  const q = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${q})`, 'gi'), '<mark class="bg-amber-200 text-amber-900 rounded px-0.5">$1</mark>')
}

const getTypeIcon = (type) => {
  const icons = { student: markRaw(GraduationCap), user: markRaw(User), group: markRaw(Building2) }
  return icons[type] || markRaw(Search)
}

const getTypeIconBg = (type) => {
  const colors = { student: 'bg-blue-100', user: 'bg-emerald-100', group: 'bg-violet-100' }
  return colors[type] || 'bg-slate-100'
}

const getTypeIconColor = (type) => {
  const colors = { student: 'text-blue-600', user: 'text-emerald-600', group: 'text-violet-600' }
  return colors[type] || 'text-slate-600'
}
</script>

<style scoped>
.search-fade-enter-active {
  transition: opacity 0.15s ease-out;
}
.search-fade-leave-active {
  transition: opacity 0.1s ease-in;
}
.search-fade-enter-from,
.search-fade-leave-to {
  opacity: 0;
}
</style>
