<template>
  <div 
    class="rounded-xl border border-slate-700 bg-slate-800/50 backdrop-blur-sm transition-all"
    :class="[
      hoverable ? 'hover:border-blue-500/50 hover:bg-slate-700/50 cursor-pointer' : '',
      padding ? paddingClasses : ''
    ]"
  >
    <!-- Header -->
    <div 
      v-if="title || $slots.header" 
      class="flex items-center justify-between"
      :class="headerPaddingClasses"
    >
      <slot name="header">
        <div class="flex items-center gap-3">
          <div 
            v-if="icon" 
            class="flex h-10 w-10 items-center justify-center rounded-lg"
            :class="iconBgClass"
          >
            <component :is="icon" :size="20" :class="iconColorClass" />
          </div>
          <div>
            <h3 class="font-semibold text-white">{{ title }}</h3>
            <p v-if="subtitle" class="text-sm text-slate-400">{{ subtitle }}</p>
          </div>
        </div>
      </slot>
      <slot name="actions"></slot>
    </div>

    <!-- Body -->
    <div :class="bodyPaddingClasses">
      <slot></slot>
    </div>

    <!-- Footer -->
    <div 
      v-if="$slots.footer" 
      class="border-t border-slate-700"
      :class="footerPaddingClasses"
    >
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: [Object, Function],
    default: null
  },
  iconColor: {
    type: String,
    default: 'blue'
  },
  hoverable: {
    type: Boolean,
    default: false
  },
  padding: {
    type: Boolean,
    default: true
  }
})

const paddingClasses = computed(() => 'p-4 md:p-6')
const headerPaddingClasses = computed(() => props.padding ? 'mb-4' : 'p-4 md:p-6 border-b border-slate-700')
const bodyPaddingClasses = computed(() => props.padding ? '' : 'p-4 md:p-6')
const footerPaddingClasses = computed(() => 'p-4 md:p-6')

const iconBgClass = computed(() => `bg-${props.iconColor}-500/20`)
const iconColorClass = computed(() => `text-${props.iconColor}-400`)
</script>
