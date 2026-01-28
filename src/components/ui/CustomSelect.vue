<template>
  <div class="custom-select-wrapper" ref="selectRef">
    <!-- Selected value button -->
    <button
      type="button"
      @click="toggleDropdown"
      :class="[
        'select-trigger',
        isOpen && 'select-trigger-open',
        size === 'sm' && 'select-trigger-sm'
      ]"
    >
      <span class="select-value">
        <component 
          v-if="selectedOption?.icon" 
          :is="selectedOption.icon" 
          class="select-icon-component"
        />
        <span>{{ selectedOption?.label || placeholder }}</span>
      </span>
      <svg 
        :class="['select-chevron', isOpen && 'select-chevron-open']" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        stroke-width="2.5"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown -->
    <Transition name="dropdown">
      <div v-if="isOpen" class="select-dropdown">
        <div
          v-for="option in options"
          :key="option.value"
          @click="selectOption(option)"
          :class="[
            'select-option',
            modelValue === option.value && 'select-option-selected'
          ]"
        >
          <component 
            v-if="option.icon" 
            :is="option.icon" 
            class="select-option-icon"
          />
          <span class="select-option-label">{{ option.label }}</span>
          <svg 
            v-if="modelValue === option.value" 
            class="select-option-check" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="3"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null
  },
  options: {
    type: Array,
    required: true
    // [{ value: 'val', label: 'Label', icon: ComponentIcon }]
  },
  placeholder: {
    type: String,
    default: 'Tanlang...'
  },
  size: {
    type: String,
    default: 'md' // 'sm' | 'md'
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const selectRef = ref(null)

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectOption = (option) => {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

// Click outside to close
const handleClickOutside = (event) => {
  if (selectRef.value && !selectRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-select-wrapper {
  @apply relative;
}

.select-trigger {
  @apply w-full flex items-center justify-between gap-2
         px-4 py-3 
         bg-white border-2 border-slate-200 rounded-xl
         text-left text-slate-700 font-medium
         transition-all duration-200 ease-out
         hover:border-emerald-400 hover:shadow-lg hover:shadow-emerald-500/10;
}

.select-trigger:focus {
  @apply outline-none border-emerald-500 ring-4 ring-emerald-500/10;
}

.select-trigger-open {
  @apply border-emerald-500 ring-4 ring-emerald-500/10 shadow-lg shadow-emerald-500/10;
}

.select-trigger-sm {
  @apply px-3 py-2 text-sm rounded-lg;
}

.select-value {
  @apply flex items-center gap-2 truncate;
}

.select-icon-component {
  @apply w-5 h-5 text-emerald-500;
}

.select-trigger-sm .select-icon-component {
  @apply w-4 h-4;
}

.select-chevron {
  @apply w-5 h-5 text-slate-400 transition-transform duration-200 shrink-0;
}

.select-chevron-open {
  @apply rotate-180 text-emerald-500;
}

/* Dropdown */
.select-dropdown {
  @apply absolute z-50 top-full left-0 right-0 mt-2
         bg-white border-2 border-slate-100 rounded-xl
         shadow-2xl shadow-slate-200/50
         overflow-hidden
         max-h-64 overflow-y-auto;
}

.select-option {
  @apply flex items-center gap-3 px-4 py-3
         cursor-pointer transition-all duration-150
         hover:bg-emerald-50;
}

.select-option-selected {
  @apply bg-emerald-50 text-emerald-700;
}

.select-option-icon {
  @apply w-5 h-5 text-slate-400;
}

.select-option-selected .select-option-icon {
  @apply text-emerald-500;
}

.select-option:hover .select-option-icon {
  @apply text-emerald-500;
}

.select-option-label {
  @apply flex-1 font-medium;
}

.select-option-check {
  @apply w-5 h-5 text-emerald-500 shrink-0;
}

/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  @apply transition-all duration-200 ease-out;
}

.dropdown-enter-from,
.dropdown-leave-to {
  @apply opacity-0 -translate-y-2;
}

/* Scrollbar styling */
.select-dropdown::-webkit-scrollbar {
  @apply w-2;
}

.select-dropdown::-webkit-scrollbar-track {
  @apply bg-slate-50 rounded-full;
}

.select-dropdown::-webkit-scrollbar-thumb {
  @apply bg-slate-300 rounded-full hover:bg-slate-400;
}
</style>
