<template>
  <div class="min-h-[70vh] flex flex-col items-center justify-center px-4 py-12">
    <div class="text-center mb-8">
      <div class="w-20 h-20 bg-amber-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <UtensilsCrossed class="w-10 h-10 text-amber-500" />
      </div>
      <h1 class="text-3xl font-bold text-slate-800 mb-3">Oshxona</h1>
      <div class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-400 to-orange-400 text-white font-semibold rounded-full shadow-lg shadow-amber-500/30 text-lg">
        <Clock class="w-5 h-5 animate-pulse" />
        Tez kunda!
      </div>
    </div>
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 max-w-md w-full text-center">
      <p class="text-slate-500 text-base leading-relaxed">
        Oshxona bo'limi hozirda ishlab chiqilmoqda. Tez orada foydalanish mumkin bo'ladi.
      </p>
    </div>
  </div>
</template>

<script setup>
import { Clock, UtensilsCrossed } from 'lucide-vue-next'
// Tez kunda
</script>
