<template>
  <div class="rounded-xl border border-slate-700 bg-slate-800/50 backdrop-blur-sm overflow-hidden">
    <!-- Table Header -->
    <div v-if="title || $slots.header" class="flex items-center justify-between border-b border-slate-700 px-4 py-3 md:px-6 md:py-4">
      <slot name="header">
        <h3 class="font-semibold text-white">{{ title }}</h3>
      </slot>
      <slot name="actions"></slot>
    </div>

    <!-- Search and Filters -->
    <div v-if="searchable || $slots.filters" class="flex flex-wrap items-center gap-3 border-b border-slate-700 px-4 py-3">
      <div v-if="searchable" class="relative flex-1 min-w-[200px]">
        <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="searchPlaceholder"
          class="w-full rounded-lg border border-slate-600 bg-slate-700 py-2 pl-10 pr-4 text-sm text-white placeholder-slate-400 focus:border-blue-500 focus:outline-none"
        />
      </div>
      <slot name="filters"></slot>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-slate-800/50">
          <tr>
            <th 
              v-if="selectable" 
              class="w-12 px-4 py-3"
            >
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected"
                @change="toggleSelectAll"
                class="rounded border-slate-600 bg-slate-700 text-blue-500"
              />
            </th>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-4 py-3 text-left text-sm font-medium text-slate-400"
              :class="column.class"
              :style="{ width: column.width }"
            >
              <button
                v-if="column.sortable"
                @click="handleSort(column.key)"
                class="flex items-center gap-1 hover:text-white transition-colors"
              >
                {{ column.label }}
                <component 
                  :is="getSortIcon(column.key)" 
                  :size="14" 
                  :class="sortKey === column.key ? 'text-blue-400' : 'text-slate-600'"
                />
              </button>
              <span v-else>{{ column.label }}</span>
            </th>
            <th v-if="$slots.rowActions" class="w-20 px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-700/50">
          <tr
            v-for="(row, index) in paginatedData"
            :key="row[rowKey] || index"
            class="transition-colors hover:bg-slate-700/30"
            :class="{ 'bg-blue-500/10': isSelected(row) }"
          >
            <td v-if="selectable" class="px-4 py-3">
              <input
                type="checkbox"
                :checked="isSelected(row)"
                @change="toggleSelect(row)"
                class="rounded border-slate-600 bg-slate-700 text-blue-500"
              />
            </td>
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-4 py-3 text-sm text-slate-300"
              :class="column.cellClass"
            >
              <slot :name="'cell-' + column.key" :row="row" :value="getNestedValue(row, column.key)">
                {{ formatValue(row, column) }}
              </slot>
            </td>
            <td v-if="$slots.rowActions" class="px-4 py-3">
              <slot name="rowActions" :row="row" :index="index"></slot>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="paginatedData.length === 0">
            <td :colspan="totalColumns" class="px-4 py-12 text-center">
              <slot name="empty">
                <div class="flex flex-col items-center">
                  <Database :size="48" class="mb-4 text-slate-600" />
                  <p class="text-slate-400">{{ emptyText }}</p>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="paginated && totalPages > 1" class="flex items-center justify-between border-t border-slate-700 px-4 py-3">
      <div class="text-sm text-slate-400">
        {{ paginationInfo }}
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="currentPage = 1"
          :disabled="currentPage === 1"
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-700 disabled:opacity-50"
        >
          <ChevronsLeft :size="18" />
        </button>
        <button
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-700 disabled:opacity-50"
        >
          <ChevronLeft :size="18" />
        </button>
        
        <div class="flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            class="min-w-[32px] rounded-lg px-2 py-1 text-sm transition-colors"
            :class="currentPage === page ? 'bg-blue-500 text-white' : 'text-slate-400 hover:bg-slate-700'"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="currentPage++"
          :disabled="currentPage === totalPages"
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-700 disabled:opacity-50"
        >
          <ChevronRight :size="18" />
        </button>
        <button
          @click="currentPage = totalPages"
          :disabled="currentPage === totalPages"
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-700 disabled:opacity-50"
        >
          <ChevronsRight :size="18" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  Search, Database, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight,
  ArrowUpDown, ArrowUp, ArrowDown
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  columns: {
    type: Array,
    required: true
    // { key: string, label: string, sortable?: boolean, width?: string, class?: string, cellClass?: string, format?: function }
  },
  data: {
    type: Array,
    required: true
  },
  rowKey: {
    type: String,
    default: 'id'
  },
  selectable: {
    type: Boolean,
    default: false
  },
  searchable: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: 'Qidirish...'
  },
  searchKeys: {
    type: Array,
    default: () => []
  },
  paginated: {
    type: Boolean,
    default: false
  },
  perPage: {
    type: Number,
    default: 10
  },
  emptyText: {
    type: String,
    default: 'Ma\'lumot topilmadi'
  }
})

const emit = defineEmits(['select', 'sort'])

// State
const searchQuery = ref('')
const currentPage = ref(1)
const sortKey = ref('')
const sortDirection = ref('asc')
const selectedRows = ref([])

// Computed
const filteredData = computed(() => {
  let result = [...props.data]

  // Search
  if (searchQuery.value && props.searchKeys.length > 0) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(row => {
      return props.searchKeys.some(key => {
        const value = getNestedValue(row, key)
        return String(value).toLowerCase().includes(query)
      })
    })
  }

  // Sort
  if (sortKey.value) {
    result.sort((a, b) => {
      const aVal = getNestedValue(a, sortKey.value)
      const bVal = getNestedValue(b, sortKey.value)
      
      if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
      if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
      return 0
    })
  }

  return result
})

const paginatedData = computed(() => {
  if (!props.paginated) return filteredData.value
  
  const start = (currentPage.value - 1) * props.perPage
  const end = start + props.perPage
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / props.perPage)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 5; i++) pages.push(i)
    } else if (current >= total - 2) {
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      for (let i = current - 2; i <= current + 2; i++) pages.push(i)
    }
  }
  
  return pages
})

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * props.perPage + 1
  const end = Math.min(currentPage.value * props.perPage, filteredData.value.length)
  return `${start}-${end} / ${filteredData.value.length}`
})

const totalColumns = computed(() => {
  let count = props.columns.length
  if (props.selectable) count++
  return count
})

const allSelected = computed(() => {
  return paginatedData.value.length > 0 && 
    paginatedData.value.every(row => selectedRows.value.includes(row[props.rowKey]))
})

const someSelected = computed(() => {
  return selectedRows.value.length > 0 && !allSelected.value
})

// Watch
watch(searchQuery, () => {
  currentPage.value = 1
})

// Methods
function getNestedValue(obj, key) {
  return key.split('.').reduce((o, k) => (o || {})[k], obj)
}

function formatValue(row, column) {
  const value = getNestedValue(row, column.key)
  if (column.format) {
    return column.format(value, row)
  }
  return value
}

function handleSort(key) {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDirection.value = 'asc'
  }
  emit('sort', { key, direction: sortDirection.value })
}

function getSortIcon(key) {
  if (sortKey.value !== key) return ArrowUpDown
  return sortDirection.value === 'asc' ? ArrowUp : ArrowDown
}

function isSelected(row) {
  return selectedRows.value.includes(row[props.rowKey])
}

function toggleSelect(row) {
  const id = row[props.rowKey]
  const index = selectedRows.value.indexOf(id)
  if (index === -1) {
    selectedRows.value.push(id)
  } else {
    selectedRows.value.splice(index, 1)
  }
  emit('select', selectedRows.value)
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedRows.value = []
  } else {
    selectedRows.value = paginatedData.value.map(row => row[props.rowKey])
  }
  emit('select', selectedRows.value)
}
</script>
