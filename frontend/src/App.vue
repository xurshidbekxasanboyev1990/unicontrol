<template>
  <div id="app" class="min-h-screen">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <!-- Global Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useDataStore } from './stores/data'
import ToastContainer from './components/ui/ToastContainer.vue'

const authStore = useAuthStore()
const dataStore = useDataStore()

onMounted(async () => {
  // Auth tekshirish
  const isAuth = await authStore.checkAuth()
  
  // Agar foydalanuvchi kirgan bo'lsa, ma'lumotlarni yuklash
  if (isAuth) {
    await dataStore.initializeData()
  }
})
</script>

<style>
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
