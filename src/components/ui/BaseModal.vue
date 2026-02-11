<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="handleOverlayClick"
      >
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
        
        <!-- Modal Content -->
        <div 
          class="relative w-full rounded-2xl border border-slate-700 bg-slate-800 shadow-xl"
          :class="sizeClasses"
        >
          <!-- Header -->
          <div 
            v-if="title || $slots.header" 
            class="flex items-center justify-between border-b border-slate-700 px-6 py-4"
          >
            <slot name="header">
              <h2 class="text-xl font-bold text-white">{{ title }}</h2>
            </slot>
            <button 
              v-if="closable"
              @click="close"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-700 hover:text-white"
            >
              <X :size="20" />
            </button>
          </div>

          <!-- Body -->
          <div class="p-6" :class="bodyClass">
            <slot></slot>
          </div>

          <!-- Footer -->
          <div 
            v-if="$slots.footer" 
            class="flex items-center justify-end gap-3 border-t border-slate-700 px-6 py-4"
          >
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', 'full'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  },
  bodyClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-[90vw] max-h-[90vh]'
  }
  return sizes[props.size]
})

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function handleOverlayClick() {
  if (props.closeOnOverlay) {
    close()
  }
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

.modal-enter-from > div:last-child,
.modal-leave-to > div:last-child {
  transform: scale(0.95);
}
</style>
