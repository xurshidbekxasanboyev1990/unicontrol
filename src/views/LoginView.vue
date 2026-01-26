<template>
  <div class="min-h-screen bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
    <!-- Animated Background -->
    <div class="absolute inset-0">
      <!-- Gradient Orbs -->
      <div class="absolute top-0 -left-40 w-96 h-96 bg-emerald-500/20 rounded-full blur-[120px] animate-pulse"></div>
      <div class="absolute bottom-0 -right-40 w-96 h-96 bg-teal-500/20 rounded-full blur-[120px] animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[150px]"></div>
      
      <!-- Grid Pattern -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]"></div>
      
      <!-- Floating Particles -->
      <div class="absolute top-20 left-20 w-2 h-2 bg-emerald-400/40 rounded-full animate-float"></div>
      <div class="absolute top-40 right-32 w-3 h-3 bg-teal-400/30 rounded-full animate-float" style="animation-delay: 0.5s;"></div>
      <div class="absolute bottom-32 left-40 w-2 h-2 bg-cyan-400/40 rounded-full animate-float" style="animation-delay: 1s;"></div>
      <div class="absolute bottom-20 right-20 w-4 h-4 bg-emerald-400/20 rounded-full animate-float" style="animation-delay: 1.5s;"></div>
    </div>

    <!-- Login Card -->
    <div class="relative w-full max-w-md animate-fade-in-up">
      <!-- Logo & Title -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center mb-6 relative">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-3xl blur-xl opacity-50 animate-pulse"></div>
          <div class="relative w-20 h-20 bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-emerald-500/30">
            <GraduationCap class="w-10 h-10 text-white" />
          </div>
        </div>
        <h1 class="text-4xl font-bold text-white mb-3 tracking-tight">Uni Control</h1>
        <p class="text-slate-400 text-lg">Universitet boshqaruv tizimi</p>
      </div>

      <!-- Card -->
      <div class="relative">
        <div class="absolute inset-0 bg-gradient-to-br from-white/10 to-white/5 rounded-3xl blur-xl"></div>
        <div class="relative bg-white/[0.07] backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
          <form @submit.prevent="handleLogin" class="space-y-6">
            <!-- Error Alert -->
            <Transition name="shake">
              <div v-if="error && !isBlocked" class="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400">
                <div class="w-10 h-10 bg-rose-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                  <AlertCircle class="w-5 h-5" />
                </div>
                <span class="text-sm font-medium">{{ error }}</span>
              </div>
            </Transition>

            <!-- Blocked Group Alert -->
            <Transition name="shake">
              <div v-if="isBlocked" class="p-5 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
                <div class="flex items-start gap-3">
                  <div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                    <ShieldAlert class="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <h3 class="font-semibold text-amber-400 mb-1">Ruxsat etilmagan</h3>
                    <p class="text-sm text-amber-300/80">Guruhingiz ruxsatga ega emas. Tizimga kirish uchun adminga murojaat qiling.</p>
                    <button 
                      @click="isBlocked = false; error = ''"
                      class="mt-3 text-sm text-amber-400 hover:text-amber-300 underline"
                    >
                      Qayta urinish
                    </button>
                  </div>
                </div>
              </div>
            </Transition>

            <!-- Username -->
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-300 flex items-center gap-2">
                <User class="w-4 h-4 text-slate-400" />
                Login
              </label>
              <div class="relative group">
                <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl opacity-0 group-focus-within:opacity-100 blur-xl transition-opacity duration-300"></div>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <div class="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center group-focus-within:bg-emerald-500/20 transition-colors">
                      <User class="w-5 h-5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                    </div>
                  </div>
                  <input
                    v-model="username"
                    type="text"
                    class="w-full bg-white/5 border border-white/10 rounded-2xl pl-16 pr-4 py-4 text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 focus:border-emerald-500/50 focus:ring-4 focus:ring-emerald-500/10 transition-all duration-300"
                    placeholder="Loginni kiriting"
                    autocomplete="username"
                  />
                </div>
              </div>
            </div>

            <!-- Password -->
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Lock class="w-4 h-4 text-slate-400" />
                Parol
              </label>
              <div class="relative group">
                <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl opacity-0 group-focus-within:opacity-100 blur-xl transition-opacity duration-300"></div>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <div class="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center group-focus-within:bg-emerald-500/20 transition-colors">
                      <Lock class="w-5 h-5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                    </div>
                  </div>
                  <input
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    class="w-full bg-white/5 border border-white/10 rounded-2xl pl-16 pr-14 py-4 text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 focus:border-emerald-500/50 focus:ring-4 focus:ring-emerald-500/10 transition-all duration-300"
                    placeholder="••••••••"
                    autocomplete="current-password"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-4 flex items-center"
                  >
                    <div class="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition-colors">
                      <EyeOff v-if="showPassword" class="w-5 h-5 text-slate-400" />
                      <Eye v-else class="w-5 h-5 text-slate-400" />
                    </div>
                  </button>
                </div>
              </div>
            </div>

            <!-- Remember & Forgot -->
            <div class="flex items-center justify-between">
              <label class="flex items-center gap-3 cursor-pointer group">
                <div class="relative">
                  <input type="checkbox" v-model="remember" class="sr-only peer" />
                  <div class="w-5 h-5 bg-white/5 border border-white/20 rounded-lg peer-checked:bg-emerald-500 peer-checked:border-emerald-500 transition-all"></div>
                  <Check class="absolute inset-0 w-5 h-5 text-white opacity-0 peer-checked:opacity-100 transition-opacity p-0.5" />
                </div>
                <span class="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">Eslab qolish</span>
              </label>
              <a href="#" class="text-sm text-emerald-400 hover:text-emerald-300 transition-colors font-medium">Parolni unutdingizmi?</a>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="isLoading"
              class="relative w-full group overflow-hidden"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl"></div>
              <div class="absolute inset-0 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <div class="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.1)_50%,transparent_75%)] bg-[length:250%_250%] animate-shimmer"></div>
              </div>
              <div class="relative flex items-center justify-center gap-3 py-4 px-6 font-semibold text-white">
                <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
                <LogIn v-else class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <span>{{ isLoading ? 'Kirish...' : 'Tizimga kirish' }}</span>
                <ArrowRight class="w-5 h-5 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              </div>
            </button>
          </form>

          <!-- Divider -->
          <div class="relative my-8">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-white/10"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="px-4 bg-transparent text-slate-500 text-sm font-medium">Demo hisoblar</span>
            </div>
          </div>

          <!-- Demo Accounts -->
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="demo in demoAccounts"
              :key="demo.username"
              @click="fillDemo(demo)"
              class="group relative overflow-hidden rounded-2xl transition-all duration-300"
            >
              <div class="absolute inset-0 bg-white/5 group-hover:bg-white/10 transition-colors"></div>
              <div :class="['absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity', demo.glowClass]"></div>
              <div class="relative flex items-center gap-3 p-4 border border-white/10 group-hover:border-white/20 rounded-2xl transition-colors">
                <div :class="['w-11 h-11 rounded-xl flex items-center justify-center shadow-lg transition-transform group-hover:scale-110', demo.bgClass]">
                  <component :is="demo.icon" class="w-5 h-5 text-white" />
                </div>
                <div class="text-left">
                  <p class="text-sm font-semibold text-white">{{ demo.label }}</p>
                  <p class="text-xs text-slate-500 group-hover:text-slate-400 transition-colors">{{ demo.username }}</p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-8 text-center">
        <p class="text-slate-500 text-sm">
          © 2026 Uni Control. Barcha huquqlar himoyalangan.
        </p>
        <div class="flex items-center justify-center gap-4 mt-3">
          <a href="#" class="text-sm text-slate-500 hover:text-emerald-400 transition-colors">Yordam</a>
          <span class="text-slate-700">•</span>
          <a href="#" class="text-sm text-slate-500 hover:text-emerald-400 transition-colors">Maxfiylik</a>
          <span class="text-slate-700">•</span>
          <a href="#" class="text-sm text-slate-500 hover:text-emerald-400 transition-colors">Shartlar</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { 
  GraduationCap, 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  LogIn, 
  Loader2, 
  AlertCircle,
  ShieldAlert,
  UserCircle,
  Users,
  Shield,
  Crown,
  Check,
  ArrowRight
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const remember = ref(false)
const isLoading = ref(false)
const error = ref('')
const isBlocked = ref(false)

const demoAccounts = [
  { 
    username: 'ST-2024-001', 
    password: '123456', 
    label: 'Talaba', 
    icon: markRaw(UserCircle), 
    bgClass: 'bg-gradient-to-br from-blue-500 to-blue-600',
    glowClass: 'bg-blue-500/10'
  },
  { 
    username: 'ST-2024-002', 
    password: '123456', 
    label: 'Sardor', 
    icon: markRaw(Users), 
    bgClass: 'bg-gradient-to-br from-amber-500 to-orange-600',
    glowClass: 'bg-amber-500/10'
  },
  { 
    username: 'admin', 
    password: '123', 
    label: 'Admin', 
    icon: markRaw(Shield), 
    bgClass: 'bg-gradient-to-br from-violet-500 to-purple-600',
    glowClass: 'bg-violet-500/10'
  },
  { 
    username: 'super', 
    password: '123', 
    label: 'Super Admin', 
    icon: markRaw(Crown), 
    bgClass: 'bg-gradient-to-br from-rose-500 to-pink-600',
    glowClass: 'bg-rose-500/10'
  }
]

const fillDemo = (demo) => {
  username.value = demo.username
  password.value = demo.password
}

const handleLogin = async () => {
  error.value = ''
  isBlocked.value = false
  
  if (!username.value || !password.value) {
    error.value = 'Login va parolni kiriting'
    return
  }

  isLoading.value = true

  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const result = authStore.login({ login: username.value, password: password.value })
    
    if (result.success) {
      const redirectPath = {
        student: '/student',
        leader: '/leader',
        admin: '/admin',
        superadmin: '/super'
      }[authStore.user.role] || '/student'
      
      router.push(redirectPath)
    } else if (result.blocked) {
      isBlocked.value = true
    } else {
      error.value = result.message || 'Talaba ID yoki parol noto\'g\'ri'
    }
  } catch (err) {
    error.value = 'Xatolik yuz berdi'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-fade-in-up {
  animation: fade-in-up 0.8s ease-out;
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}

.shake-enter-active {
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}
</style>
