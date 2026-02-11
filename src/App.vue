<!--
============================================
UNI CONTROL - Root Component (App.vue)
============================================

Bu Vue ilovasining root (asosiy) komponenti.

TUZILISHI:
----------
1. <router-view> - Barcha sahifalar shu yerda ko'rsatiladi
   - Transition bilan sahifalar o'zgaradi (fade effekt)
   
2. <ToastContainer> - Global toast xabarlar
   - Ekranning yuqori o'ng burchagida
   - toast store orqali boshqariladi

HAYOT SIKLI:
------------
onMounted() da authStore.checkAuth() chaqiriladi.
Bu localStorage'dan foydalanuvchi ma'lumotlarini yuklaydi
(agar oldin login qilgan bo'lsa).

TRANSITION:
-----------
Sahifalar o'rtasida fade animatsiya:
- Eski sahifa: opacity 0, translateY -10px
- Yangi sahifa: opacity 0, translateY +10px dan boshlab
-->

<template>
  <div id="app" class="min-h-screen">
    <!-- 
      Router View: Barcha sahifalar shu yerda renderlanadi
      Transition: Sahifa o'zgarishida fade animatsiya
    -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <!-- 
      Global Toast Notifications
      toast store orqali istalgan joydan chaqirish mumkin:
      toast.success('Saqlandi!')
    -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import ToastContainer from './components/ui/ToastContainer.vue'

const authStore = useAuthStore()

// Ilova yuklanganda localStorage'dan auth holatini tekshirish
onMounted(() => {
  authStore.checkAuth()
})
</script>

<style>
/* Sahifa o'tish animatsiyasi */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
