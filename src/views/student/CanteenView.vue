<template>
  <div class="min-h-[calc(100vh-200px)] flex items-center justify-center p-4">
    <div class="text-center max-w-lg mx-auto">
      <!-- Animated Food Icon -->
      <div class="relative mb-8">
        <!-- Glow effect -->
        <div class="absolute inset-0 blur-3xl bg-gradient-to-r from-orange-400/30 via-amber-400/30 to-yellow-400/30 rounded-full animate-pulse"></div>
        
        <!-- Main icon container -->
        <div class="relative">
          <!-- Floating food items -->
          <div class="absolute -top-4 -left-4 animate-float-slow">
            <div class="w-12 h-12 bg-gradient-to-br from-red-400 to-red-500 rounded-2xl flex items-center justify-center shadow-lg shadow-red-500/30">
              <Pizza class="w-6 h-6 text-white" />
            </div>
          </div>
          
          <div class="absolute -top-2 -right-6 animate-float-medium">
            <div class="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/30">
              <Coffee class="w-5 h-5 text-white" />
            </div>
          </div>
          
          <div class="absolute -bottom-4 -left-6 animate-float-fast">
            <div class="w-10 h-10 bg-gradient-to-br from-emerald-400 to-green-500 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/30">
              <Salad class="w-5 h-5 text-white" />
            </div>
          </div>
          
          <div class="absolute -bottom-2 -right-4 animate-float-slow" style="animation-delay: 0.5s;">
            <div class="w-11 h-11 bg-gradient-to-br from-purple-400 to-violet-500 rounded-xl flex items-center justify-center shadow-lg shadow-violet-500/30">
              <IceCream class="w-5 h-5 text-white" />
            </div>
          </div>

          <!-- Center icon -->
          <div class="w-28 h-28 bg-gradient-to-br from-orange-500 via-amber-500 to-yellow-500 rounded-3xl flex items-center justify-center mx-auto shadow-2xl shadow-orange-500/40 animate-bounce-gentle">
            <UtensilsCrossed class="w-14 h-14 text-white" />
          </div>
        </div>
      </div>

      <!-- Text content -->
      <div class="space-y-4">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-100 to-amber-100 rounded-full">
          <div class="w-2 h-2 bg-orange-500 rounded-full animate-ping"></div>
          <span class="text-sm font-semibold text-orange-600">Dasturlash jarayonida</span>
        </div>

        <h1 class="text-3xl md:text-4xl font-bold text-slate-800">
          Universitet Oshxonasi
        </h1>
        
        <p class="text-lg text-slate-500 leading-relaxed">
          Tez orada siz bu yerda oshxona menyusini ko'rishingiz, 
          ovqatlar narxini bilishingiz va mavjudligini tekshirishingiz mumkin bo'ladi!
        </p>
      </div>

      <!-- Features preview -->
      <div class="mt-10 grid grid-cols-3 gap-4">
        <div class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-orange-200 transition-all group">
          <div class="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
            <ChefHat class="w-6 h-6 text-orange-500" />
          </div>
          <p class="text-sm font-medium text-slate-700">Kunlik menyu</p>
          <p class="text-xs text-slate-400 mt-1">Har kuni yangilanadi</p>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-emerald-200 transition-all group">
          <div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
            <Banknote class="w-6 h-6 text-emerald-500" />
          </div>
          <p class="text-sm font-medium text-slate-700">Narxlar</p>
          <p class="text-xs text-slate-400 mt-1">Arzon va sifatli</p>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-lg hover:border-blue-200 transition-all group">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
            <Clock class="w-6 h-6 text-blue-500" />
          </div>
          <p class="text-sm font-medium text-slate-700">Mavjudlik</p>
          <p class="text-xs text-slate-400 mt-1">Real vaqtda</p>
        </div>
      </div>

      <!-- Progress indicator -->
      <div class="mt-10 bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-slate-600">Yaratilish jarayoni</span>
          <span class="text-sm font-bold text-orange-500">75%</span>
        </div>
        <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-orange-500 to-amber-500 rounded-full relative animate-progress"
            style="width: 75%"
          >
            <div class="absolute inset-0 bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.4),transparent)] animate-shimmer"></div>
          </div>
        </div>
        <div class="flex items-center justify-center gap-2 mt-4 text-sm text-slate-500">
          <Sparkles class="w-4 h-4 text-amber-500" />
          <span>Tez orada ishga tushadi!</span>
        </div>
      </div>

      <!-- Notification signup -->
      <div class="mt-8 p-6 bg-gradient-to-br from-orange-500 to-amber-500 rounded-2xl text-white">
        <Bell class="w-8 h-8 mx-auto mb-3 animate-ring" />
        <p class="font-semibold">Xabar olishni xohlaysizmi?</p>
        <p class="text-sm text-orange-100 mt-1">
          Oshxona menyusi ishga tushganda sizga xabar beramiz
        </p>
        <button 
          @click="subscribeNotification"
          class="mt-4 px-6 py-2.5 bg-white text-orange-500 rounded-xl font-semibold hover:bg-orange-50 transition-colors"
        >
          Obuna bo'lish
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToastStore } from '../../stores/toast'
import {
  UtensilsCrossed,
  Pizza,
  Coffee,
  Salad,
  IceCream,
  ChefHat,
  Banknote,
  Clock,
  Bell,
  Sparkles
} from 'lucide-vue-next'

const toast = useToastStore()

const subscribeNotification = () => {
  toast.success('Rahmat! Oshxona menyusi tayyor bo\'lganda sizga xabar beramiz.')
}
</script>

<style scoped>
@keyframes float-slow {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-15px) rotate(5deg); }
}

@keyframes float-medium {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-12px) rotate(-5deg); }
}

@keyframes float-fast {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-10px) rotate(3deg); }
}

@keyframes bounce-gentle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}

@keyframes progress {
  0% { width: 0%; }
  100% { width: 75%; }
}

@keyframes ring {
  0%, 100% { transform: rotate(0); }
  10%, 30% { transform: rotate(-10deg); }
  20%, 40% { transform: rotate(10deg); }
  50% { transform: rotate(0); }
}

.animate-float-slow {
  animation: float-slow 4s ease-in-out infinite;
}

.animate-float-medium {
  animation: float-medium 3s ease-in-out infinite;
}

.animate-float-fast {
  animation: float-fast 2.5s ease-in-out infinite;
}

.animate-bounce-gentle {
  animation: bounce-gentle 3s ease-in-out infinite;
}

.animate-shimmer {
  animation: shimmer 2s ease-in-out infinite;
}

.animate-progress {
  animation: progress 2s ease-out;
}

.animate-ring {
  animation: ring 2s ease-in-out infinite;
}
</style>
