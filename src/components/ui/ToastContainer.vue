<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[9999] space-y-3 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'pointer-events-auto flex items-start gap-3 px-4 py-4 rounded-2xl shadow-2xl min-w-[320px] max-w-md backdrop-blur-xl border',
            toast.type === 'success' && 'bg-emerald-500/95 text-white border-emerald-400/30',
            toast.type === 'error' && 'bg-red-500/95 text-white border-red-400/30',
            toast.type === 'warning' && 'bg-amber-500/95 text-white border-amber-400/30',
            toast.type === 'info' && 'bg-blue-500/95 text-white border-blue-400/30'
          ]"
        >
          <div class="flex-shrink-0 w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
            <component :is="getIcon(toast.type)" class="w-5 h-5" />
          </div>
          <div class="flex-1 min-w-0">
            <p v-if="toast.title" class="font-semibold text-sm">{{ toast.title }}</p>
            <p :class="toast.title ? 'text-sm opacity-90 mt-0.5' : 'font-medium'">{{ toast.message }}</p>
          </div>
          <button 
            @click="removeToast(toast.id)" 
            class="flex-shrink-0 p-1.5 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-vue-next'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.toasts)

function getIcon(type) {
  switch (type) {
    case 'success': return CheckCircle
    case 'error': return XCircle
    case 'warning': return AlertTriangle
    default: return Info
  }
}

function removeToast(id) {
  toastStore.removeToast(id)
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}
.toast-move {
  transition: transform 0.3s ease;
}
</style>
