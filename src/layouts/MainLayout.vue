<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-72 bg-white/80 backdrop-blur-xl border-r border-slate-200/60 transform transition-all duration-300 ease-out lg:translate-x-0 shadow-xl shadow-slate-200/50',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo -->
      <div class="h-20 flex items-center gap-4 px-6 border-b border-slate-100">
        <div class="relative group">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
          <div class="relative w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
            <GraduationCap class="w-6 h-6 text-white" />
          </div>
        </div>
        <div>
          <h1 class="font-bold text-lg text-slate-800 tracking-tight">Uni Control</h1>
          <p class="text-xs text-slate-400 font-medium">{{ getRoleName }}</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="p-4 space-y-2 overflow-y-auto h-[calc(100vh-10rem)] custom-scrollbar">
        <template v-for="section in menuSections" :key="section.title">
          <div v-if="section.items.length > 0" class="mb-6">
            <p class="px-4 mb-3 text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
              {{ section.title }}
            </p>
            <router-link
              v-for="item in section.items"
              :key="item.path"
              :to="item.path"
              :class="[
                'relative flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-200 group overflow-hidden',
                isActive(item.path)
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/25'
                  : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
              ]"
              @click="isSidebarOpen = false"
            >
              <div :class="[
                'absolute inset-0 bg-gradient-to-r from-emerald-600 to-teal-600 opacity-0 transition-opacity duration-200',
                !isActive(item.path) && 'group-hover:opacity-5'
              ]"></div>
              <component 
                :is="item.icon" 
                :class="[
                  'w-5 h-5 transition-transform duration-200 group-hover:scale-110',
                  isActive(item.path) ? 'text-white' : 'text-slate-400 group-hover:text-emerald-500'
                ]"
              />
              <span class="relative z-10">{{ item.label }}</span>
              <span
                v-if="item.badge"
                :class="[
                  'ml-auto px-2.5 py-0.5 text-xs font-bold rounded-full transition-colors',
                  isActive(item.path) 
                    ? 'bg-white/20 text-white' 
                    : 'bg-emerald-100 text-emerald-600'
                ]"
              >
                {{ item.badge }}
              </span>
              <ChevronRight v-if="!item.badge" :class="[
                'w-4 h-4 ml-auto opacity-0 -translate-x-2 transition-all duration-200',
                isActive(item.path) ? 'text-white opacity-100 translate-x-0' : 'group-hover:opacity-50 group-hover:translate-x-0'
              ]" />
            </router-link>
          </div>
        </template>
      </nav>

      <!-- User Card -->
      <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-white via-white to-transparent">
        <div class="bg-slate-50/80 backdrop-blur rounded-2xl p-4 border border-slate-100">
          <div class="flex items-center gap-3">
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-emerald-500/20">
                {{ authStore.user?.name?.charAt(0) || 'U' }}
              </div>
              <span class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-500 border-2 border-white rounded-full"></span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-800 truncate">{{ authStore.user?.name }}</p>
              <p class="text-xs text-slate-400 truncate">{{ authStore.user?.email }}</p>
            </div>
            <button
              @click="handleLogout"
              class="p-2.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-all duration-200 group"
              title="Chiqish"
            >
              <LogOut class="w-5 h-5 group-hover:scale-110 transition-transform" />
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Overlay -->
    <Transition name="fade">
      <div
        v-if="isSidebarOpen"
        class="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
        @click="isSidebarOpen = false"
      ></div>
    </Transition>

    <!-- Main Content -->
    <div class="lg:pl-72 min-h-screen">
      <!-- Header -->
      <header class="sticky top-0 z-30 bg-white/70 backdrop-blur-xl border-b border-slate-200/60 shadow-sm">
        <div class="h-16 px-4 lg:px-8 flex items-center justify-between">
          <!-- Mobile menu button -->
          <button
            @click="isSidebarOpen = true"
            class="lg:hidden p-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            <Menu class="w-6 h-6" />
          </button>

          <!-- Page Title & Breadcrumb -->
          <div class="hidden lg:flex items-center gap-3">
            <div class="flex items-center gap-2 text-sm">
              <span class="text-slate-400">{{ getRoleName }}</span>
              <ChevronRight class="w-4 h-4 text-slate-300" />
              <span class="font-medium text-slate-700">{{ currentPageTitle }}</span>
            </div>
          </div>

          <div class="lg:hidden">
            <h2 class="text-lg font-semibold text-slate-800">{{ currentPageTitle }}</h2>
          </div>

          <!-- Right side -->
          <div class="flex items-center gap-3">
            <!-- Search -->
            <div class="hidden md:flex items-center">
              <div class="relative group">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
                <input
                  type="text"
                  placeholder="Qidirish..."
                  class="w-72 pl-11 pr-4 py-2.5 bg-slate-100/80 border border-transparent rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:bg-white focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all duration-200"
                />
                <kbd class="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-0.5 bg-slate-200/80 text-slate-400 text-xs rounded font-mono">⌘K</kbd>
              </div>
            </div>

            <!-- Notifications -->
            <button class="relative p-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition-all duration-200 group">
              <Bell class="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span class="absolute top-2 right-2 w-2.5 h-2.5 bg-rose-500 rounded-full ring-2 ring-white animate-pulse"></span>
            </button>

            <!-- User dropdown -->
            <div class="relative">
              <button
                @click="isDropdownOpen = !isDropdownOpen"
                class="flex items-center gap-2 p-1.5 hover:bg-slate-100 rounded-xl transition-all duration-200"
              >
                <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-sm font-semibold shadow-md shadow-emerald-500/20">
                  {{ authStore.user?.name?.charAt(0) || 'U' }}
                </div>
                <ChevronDown :class="['w-4 h-4 text-slate-400 transition-transform duration-200', isDropdownOpen && 'rotate-180']" />
              </button>

              <!-- Dropdown menu -->
              <Transition name="dropdown">
                <div
                  v-if="isDropdownOpen"
                  class="absolute right-0 mt-2 w-64 bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200/60 py-2 z-50 overflow-hidden"
                >
                  <div class="px-4 py-4 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-slate-100">
                    <p class="text-sm font-semibold text-slate-800">{{ authStore.user?.name }}</p>
                    <p class="text-xs text-slate-500 mt-0.5">{{ authStore.user?.email }}</p>
                    <span class="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-lg">
                      <Shield class="w-3 h-3" />
                      {{ getRoleName }}
                    </span>
                  </div>
                  <div class="py-2">
                    <router-link
                      :to="getProfilePath"
                      class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                      @click="isDropdownOpen = false"
                    >
                      <UserCircle class="w-4 h-4" />
                      Profil sozlamalari
                    </router-link>
                    <router-link
                      :to="getSettingsPath"
                      class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                      @click="isDropdownOpen = false"
                    >
                      <Settings class="w-4 h-4" />
                      Sozlamalar
                    </router-link>
                    <router-link
                      :to="getHelpPath"
                      class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                      @click="isDropdownOpen = false"
                    >
                      <HelpCircle class="w-4 h-4" />
                      Yordam
                    </router-link>
                  </div>
                  <div class="border-t border-slate-100 pt-2">
                    <button
                      @click="handleLogout"
                      class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-rose-600 hover:bg-rose-50 transition-colors"
                    >
                      <LogOut class="w-4 h-4" />
                      Tizimdan chiqish
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-4 lg:p-8">
        <router-view v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>

      <!-- Footer -->
      <footer class="px-4 lg:px-8 py-6 border-t border-slate-100">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-400">
          <p>© 2026 Uni Control. Barcha huquqlar himoyalangan.</p>
          <div class="flex items-center gap-4">
            <a href="#" class="hover:text-emerald-500 transition-colors">Yordam</a>
            <a href="#" class="hover:text-emerald-500 transition-colors">Maxfiylik</a>
            <a href="#" class="hover:text-emerald-500 transition-colors">Shartlar</a>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  GraduationCap,
  Menu,
  Search,
  Bell,
  ChevronDown,
  ChevronRight,
  LogOut,
  UserCircle,
  Calendar,
  ClipboardCheck,
  LayoutDashboard,
  Users,
  FileText,
  Building2,
  ShieldCheck,
  Send,
  Settings,
  BarChart3,
  Shield,
  HelpCircle,
  FolderOpen,
  BookOpen,
  Brain,
  Home,
  User
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isSidebarOpen = ref(false)
const isDropdownOpen = ref(false)

const getRoleName = computed(() => {
  const roles = {
    student: 'Talaba',
    leader: 'Guruh sardori',
    admin: 'Administrator',
    superadmin: 'Super Admin'
  }
  return roles[authStore.user?.role] || 'Foydalanuvchi'
})

const currentPageTitle = computed(() => {
  const titles = {
    'student-dashboard': 'Boshqaruv paneli',
    'student-schedule': 'Dars jadvali',
    'student-profile': 'Profil',
    'student-attendance': 'Davomat',
    'student-library': 'Kutubxona',
    'student-ai-analysis': 'AI Tahlil',
    'student-notifications': 'Bildirishnomalar',
    'student-settings': 'Sozlamalar',
    'student-help': 'Yordam',
    'leader-dashboard': 'Boshqaruv paneli',
    'leader-attendance': 'Davomat olish',
    'leader-students': 'Talabalar',
    'leader-schedule': 'Dars jadvali',
    'leader-reports': 'Hisobotlar',
    'leader-notifications': 'Bildirishnomalar',
    'leader-analytics': 'Statistika',
    'leader-files': 'Fayllar',
    'leader-profile': 'Profil',
    'leader-settings': 'Sozlamalar',
    'leader-help': 'Yordam',
    'admin-dashboard': 'Boshqaruv paneli',
    'admin-students': 'Talabalar',
    'admin-groups': 'Guruhlar',
    'admin-reports': 'Hisobotlar',
    'admin-notifications': 'Bildirishnomalar',
    'admin-users': 'Foydalanuvchilar',
    'admin-profile': 'Profil',
    'admin-settings': 'Sozlamalar',
    'admin-help': 'Yordam',
    'super-dashboard': 'Super Admin',
    'super-admins': 'Adminlar',
    'super-settings': 'Sozlamalar',
    'super-logs': 'Tizim loglari',
    'super-students': 'Talabalar',
    'super-groups': 'Guruhlar',
    'super-reports': 'Hisobotlar',
    'super-notifications': 'Bildirishnomalar',
    'super-profile': 'Profil',
    'super-help': 'Yordam'
  }
  return titles[route.name] || 'Boshqaruv paneli'
})

const menuSections = computed(() => {
  const sections = []

  if (authStore.isStudent) {
    sections.push({
      title: 'Asosiy',
      items: [
        { path: '/student/dashboard', label: 'Dashboard', icon: markRaw(Home) },
        { path: '/student/schedule', label: 'Dars jadvali', icon: markRaw(Calendar) },
        { path: '/student/attendance', label: 'Davomat', icon: markRaw(ClipboardCheck) }
      ]
    })
    sections.push({
      title: 'Xizmatlar',
      items: [
        { path: '/student/library', label: 'Kutubxona', icon: markRaw(BookOpen) },
        { path: '/student/ai-analysis', label: 'AI Tahlil', icon: markRaw(Brain) },
        { path: '/student/notifications', label: 'Bildirishnomalar', icon: markRaw(Bell), badge: '3' }
      ]
    })
    sections.push({
      title: 'Profil',
      items: [
        { path: '/student/profile', label: 'Mening profilim', icon: markRaw(User) },
        { path: '/student/settings', label: 'Sozlamalar', icon: markRaw(Settings) },
        { path: '/student/help', label: 'Yordam', icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isLeader) {
    sections.push({
      title: 'Boshqaruv',
      items: [
        { path: '/leader/dashboard', label: 'Dashboard', icon: markRaw(LayoutDashboard) },
        { path: '/leader/attendance', label: 'Davomat olish', icon: markRaw(ClipboardCheck) },
        { path: '/leader/students', label: 'Talabalar', icon: markRaw(Users) }
      ]
    })
    sections.push({
      title: 'Guruh',
      items: [
        { path: '/leader/schedule', label: 'Dars jadvali', icon: markRaw(Calendar) },
        { path: '/leader/reports', label: 'Hisobotlar', icon: markRaw(FileText) },
        { path: '/leader/analytics', label: 'Statistika', icon: markRaw(BarChart3) },
        { path: '/leader/files', label: 'Fayllar', icon: markRaw(FolderOpen) },
        { path: '/leader/notifications', label: 'Bildirishnomalar', icon: markRaw(Send) }
      ]
    })
    sections.push({
      title: 'Profil',
      items: [
        { path: '/leader/profile', label: 'Mening profilim', icon: markRaw(User) },
        { path: '/leader/settings', label: 'Sozlamalar', icon: markRaw(Settings) },
        { path: '/leader/help', label: 'Yordam', icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isAdmin) {
    sections.push({
      title: 'Boshqaruv',
      items: [
        { path: '/admin/dashboard', label: 'Dashboard', icon: markRaw(LayoutDashboard) },
        { path: '/admin/students', label: 'Talabalar', icon: markRaw(Users) },
        { path: '/admin/groups', label: 'Guruhlar', icon: markRaw(Building2) },
        { path: '/admin/users', label: 'Foydalanuvchilar', icon: markRaw(Shield) }
      ]
    })
    sections.push({
      title: 'Hisobotlar',
      items: [
        { path: '/admin/reports', label: 'Hisobotlar', icon: markRaw(BarChart3) },
        { path: '/admin/notifications', label: 'Bildirishnomalar', icon: markRaw(Send) }
      ]
    })
    sections.push({
      title: 'Profil',
      items: [
        { path: '/admin/profile', label: 'Mening profilim', icon: markRaw(User) },
        { path: '/admin/settings', label: 'Sozlamalar', icon: markRaw(Settings) },
        { path: '/admin/help', label: 'Yordam', icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isSuperAdmin) {
    sections.push({
      title: 'Super Admin',
      items: [
        { path: '/super/dashboard', label: 'Dashboard', icon: markRaw(LayoutDashboard) },
        { path: '/super/admins', label: 'Adminlar', icon: markRaw(ShieldCheck) },
        { path: '/super/settings', label: 'Sozlamalar', icon: markRaw(Settings) },
        { path: '/super/logs', label: 'Loglar', icon: markRaw(FileText) }
      ]
    })
    sections.push({
      title: 'Tizim boshqaruvi',
      items: [
        { path: '/super/students', label: 'Talabalar', icon: markRaw(Users) },
        { path: '/super/groups', label: 'Guruhlar', icon: markRaw(Building2) },
        { path: '/super/reports', label: 'Hisobotlar', icon: markRaw(BarChart3) },
        { path: '/super/notifications', label: 'Bildirishnomalar', icon: markRaw(Send) }
      ]
    })
    sections.push({
      title: 'Profil',
      items: [
        { path: '/super/profile', label: 'Mening profilim', icon: markRaw(User) },
        { path: '/super/help', label: 'Yordam', icon: markRaw(HelpCircle) }
      ]
    })
  }

  return sections
})

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

// Rol asosida path larni aniqlash
const getProfilePath = computed(() => {
  if (authStore.isLeader) return '/leader/profile'
  if (authStore.isStudent) return '/student/profile'
  if (authStore.isAdmin) return '/admin/profile'
  if (authStore.isSuperAdmin) return '/super/profile'
  return '/student/profile'
})

const getSettingsPath = computed(() => {
  if (authStore.isLeader) return '/leader/settings'
  if (authStore.isStudent) return '/student/settings'
  if (authStore.isAdmin) return '/admin/settings'
  if (authStore.isSuperAdmin) return '/super/settings'
  return '/student/settings'
})

const getHelpPath = computed(() => {
  if (authStore.isLeader) return '/leader/help'
  if (authStore.isStudent) return '/student/help'
  if (authStore.isAdmin) return '/admin/help'
  if (authStore.isSuperAdmin) return '/super/help'
  return '/student/help'
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleClickOutside = (e) => {
  if (isDropdownOpen.value && !e.target.closest('.relative')) {
    isDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.dropdown-enter-active {
  transition: all 0.2s ease-out;
}
.dropdown-leave-active {
  transition: all 0.15s ease-in;
}
.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
}
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

.page-enter-active {
  transition: all 0.3s ease-out;
}
.page-leave-active {
  transition: all 0.2s ease-in;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
