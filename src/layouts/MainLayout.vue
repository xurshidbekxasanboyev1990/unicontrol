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
              :title="t('common.logout')"
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
              <button
                @click="showSearch = true"
                class="relative group flex items-center w-72 pl-11 pr-4 py-2.5 bg-slate-100/80 border border-transparent rounded-xl text-sm text-slate-400 hover:bg-white hover:border-slate-200 transition-all duration-200 text-left"
              >
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                {{ t('common.search') }}...
                <kbd class="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-0.5 bg-slate-200/80 text-slate-400 text-xs rounded font-mono">Ctrl+K</kbd>
              </button>
            </div>

            <!-- Mobile Search Button -->
            <button @click="showSearch = true" class="md:hidden p-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors">
              <Search class="w-5 h-5" />
            </button>

            <!-- Notifications -->
            <button 
              @click="goToNotifications"
              class="relative p-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition-all duration-200 group"
            >
              <Bell class="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span 
                v-if="dataStore.unreadCount > 0"
                class="absolute -top-0.5 -right-0.5 min-w-[20px] h-5 px-1 flex items-center justify-center bg-rose-500 text-white text-[10px] font-bold rounded-full ring-2 ring-white"
              >
                {{ dataStore.unreadCount > 99 ? '99+' : dataStore.unreadCount }}
              </span>
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
                      {{ t('layout.profileSettings') }}
                    </router-link>
                    <router-link
                      :to="getSettingsPath"
                      class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                      @click="isDropdownOpen = false"
                    >
                      <Settings class="w-4 h-4" />
                      {{ t('layout.settings') }}
                    </router-link>
                    <router-link
                      :to="getHelpPath"
                      class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                      @click="isDropdownOpen = false"
                    >
                      <HelpCircle class="w-4 h-4" />
                      {{ t('layout.help') }}
                    </router-link>
                  </div>
                  <div class="border-t border-slate-100 pt-2">
                    <button
                      @click="handleLogout"
                      class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-rose-600 hover:bg-rose-50 transition-colors"
                    >
                      <LogOut class="w-4 h-4" />
                      {{ t('common.logout') }}
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
          <p>{{ t('layout.allRightsReserved') }}</p>
          <div class="flex items-center gap-4">
            <a href="#" class="hover:text-emerald-500 transition-colors">{{ t('layout.help') }}</a>
            <a href="#" class="hover:text-emerald-500 transition-colors">{{ t('layout.privacy') }}</a>
            <a href="#" class="hover:text-emerald-500 transition-colors">{{ t('layout.terms') }}</a>
          </div>
        </div>
      </footer>
    </div>

    <!-- Search Modal -->
    <SearchModal v-model="showSearch" />
  </div>
</template>

<script setup>
import {
  Activity,
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  Brain,
  Building2,
  Calculator,
  Calendar,
  CalendarCheck,
  CalendarClock,
  CalendarDays,
  CalendarOff,
  ChevronDown,
  ChevronRight,
  ClipboardCheck,
  ClipboardList,
  CreditCard,
  DoorOpen,
  FileCheck,
  FileSpreadsheet,
  FileText,
  FileUp,
  FolderOpen,
  GraduationCap,
  HelpCircle,
  Home,
  LayoutDashboard,
  LogOut,
  Menu,
  Palette,
  Search,
  Send,
  Settings,
  Shield,
  ShieldCheck,
  Sparkles,
  Store,
  Table2,
  Trophy,
  User,
  UserCircle,
  Users,
  UtensilsCrossed
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SearchModal from '../components/layout/SearchModal.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useDataStore } from '../stores/data'
import { useLanguageStore } from '../stores/language'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const dataStore = useDataStore()
const lang = useLanguageStore()
const { t } = lang

// Rolga qarab qaysi ma'lumotlarni polling qilish kerakligini aniqlash
// Faqat zarur ma'lumotlarni kuzatamiz — kam so'rov = tez ishlash
const getPollingTypes = () => {
  const role = authStore.user?.role
  // Barcha rollar uchun bildirishnomalar + dashboard stats
  const base = ['notifications', 'stats']
  if (role === 'superadmin' || role === 'admin') {
    // Admin/superadmin uchun faqat guruhlar va stats (boshqalar sahifada yuklanadi)
    return [...base, 'groups']
  } else if (role === 'academic_affairs') {
    return [...base, 'groups']
  } else if (role === 'registrar_office') {
    return [...base, 'groups']
  } else if (role === 'dean') {
    return [...base, 'groups']
  } else if (role === 'leader') {
    return [...base, 'attendance']
  } else if (role === 'teacher') {
    return [...base, 'schedule']
  } else {
    // student
    return [...base, 'schedule']
  }
}

const isSidebarOpen = ref(false)
const isDropdownOpen = ref(false)
const hasAIAccess = ref(false)
const showSearch = ref(false)

const getRoleName = computed(() => {
  const role = authStore.user?.role
  if (role) return t(`roles.${role}`)
  return t('roles.user')
})

const currentPageTitle = computed(() => {
  const titles = {
    'student-dashboard': () => t('layout.controlPanel'),
    'student-schedule': () => t('layout.schedule'),
    'student-profile': () => t('common.profile'),
    'student-attendance': () => t('layout.attendance'),
    'student-library': () => t('layout.library'),
    'student-ai-analysis': () => t('layout.aiAnalysis'),
    'student-notifications': () => t('layout.notifications'),
    'student-settings': () => t('layout.settings'),
    'student-help': () => t('layout.help'),
    'student-clubs': () => t('layout.clubs'),
    'student-canteen': () => t('layout.canteen'),
    'student-tournaments': () => t('layout.tournaments'),
    'student-subscription': () => t('layout.subscription'),
    'student-exam-schedule': () => t('exams.title'),
    'student-nb-permits': () => 'NB Ruxsatnomalarim',
    'leader-dashboard': () => t('layout.controlPanel'),
    'leader-attendance': () => t('layout.takeAttendance'),
    'leader-students': () => t('layout.students'),
    'leader-schedule': () => t('layout.schedule'),
    'leader-reports': () => t('layout.reports'),
    'leader-notifications': () => t('layout.notifications'),
    'leader-analytics': () => t('layout.analytics'),
    'leader-files': () => t('layout.files'),
    'leader-profile': () => t('common.profile'),
    'leader-settings': () => t('layout.settings'),
    'leader-help': () => t('layout.help'),
    'leader-subscription': () => t('layout.subscription'),
    'leader-exam-schedule': () => t('exams.title'),
    'leader-nb-permits': () => 'Guruh NB Ruxsatnomalari',
    'teacher-dashboard': () => t('layout.controlPanel'),
    'teacher-schedule': () => t('layout.schedule'),
    'teacher-groups': () => t('layout.groups'),
    'teacher-group-students': () => t('teacher.groupStudents'),
    'teacher-attendance': () => t('layout.attendance'),
    'teacher-workload': () => t('teacher.workload'),
    'teacher-profile': () => t('common.profile'),
    'teacher-help': () => t('layout.help'),
    'teacher-notifications': () => t('layout.notifications'),
    'admin-dashboard': () => t('layout.controlPanel'),
    'admin-attendance': () => t('layout.attendance') || 'Davomat boshqaruvi',
    'admin-students': () => t('layout.students'),
    'admin-groups': () => t('layout.groups'),
    'admin-reports': () => t('layout.reports'),
    'admin-notifications': () => t('layout.notifications'),
    'admin-users': () => t('layout.users'),
    'admin-clubs': () => t('layout.clubs'),
    'admin-tournaments': () => t('layout.tournaments'),
    'admin-profile': () => t('common.profile'),
    'admin-settings': () => t('layout.settings'),
    'admin-help': () => t('layout.help'),
    'admin-subjects': () => t('layout.subjects'),
    'super-dashboard': () => t('layout.superAdmin'),
    'super-attendance': () => t('layout.attendance') || 'Davomat boshqaruvi',
    'super-admins': () => t('layout.admins'),
    'super-settings': () => t('layout.settings'),
    'super-logs': () => t('logs.title'),
    'super-landing': () => t('layout.mainPage'),
    'super-students': () => t('layout.students'),
    'super-groups': () => t('layout.groups'),
    'super-reports': () => t('layout.reports'),
    'super-notifications': () => t('layout.notifications'),
    'super-profile': () => t('common.profile'),
    'super-help': () => t('layout.help'),
    'super-subscriptions': () => t('layout.subscriptions'),
    'super-telegram-bot': () => t('layout.telegramBot'),
    'super-contracts': () => t('layout.contracts'),
    'admin-contracts': () => t('layout.contracts'),
    'leader-contracts': () => t('layout.contracts'),
    'student-quizzes': () => t('layout.quizzes'),
    'leader-quizzes': () => t('layout.quizzes'),
    'student-subscription': () => t('layout.subscription'),
    'leader-subscription': () => t('layout.subscription'),
    'student-credit-module': () => t('layout.creditModule'),
    'leader-credit-module': () => t('layout.creditModule'),
    'admin-credit-module': () => t('layout.creditModule'),
    'super-credit-module': () => t('layout.creditModule'),
    'leader-ai-analysis': () => t('layout.aiAnalysis'),
    'teacher-ai-analysis': () => t('layout.aiAnalysis'),
    'dean-ai-analysis': () => t('layout.aiAnalysis'),
    'leader-library': () => t('layout.library'),
    'leader-clubs': () => t('layout.clubs'),
    'leader-canteen': () => t('layout.canteen'),
    'leader-tournaments': () => t('layout.tournaments'),
    'admin-ai-analysis': () => t('layout.aiAnalysis'),
    'super-ai-analysis': () => t('layout.aiAnalysis'),
    'admin-holidays': () => t('layout.holidays'),
    'super-holidays': () => t('layout.holidays'),
    'admin-import': () => t('importData.title') || 'Import',
    'super-import': () => t('importData.title') || 'Import',
    'super-workload': () => t('teacher.workload'),
    'super-workload-import': () => t('workloadImport.title') || "O'qituvchi bandligi import",
    'super-activity': () => t('activity.title') || 'Faoliyatlar',
    'super-nb-permits': () => 'NB Ruxsatnomalar',
    'admin-schedule': () => t('layout.schedule'),
    'admin-nb-permits': () => 'NB Ruxsatnomalar',
    'super-schedule': () => t('layout.schedule'),
    'academic-dashboard': () => t('layout.controlPanel'),
    'academic-schedule-editor': () => t('academic.scheduleEditor'),
    'academic-ai-generate': () => t('academic.aiGenerate'),
    'academic-groups': () => t('academic.manageGroups'),
    'academic-workload': () => t('teacher.workload'),
    'academic-workload-import': () => t('workloadImport.title') || "O'qituvchi bandligi import",
    'academic-data-manager': () => "Ma'lumotlar boshqaruvi",
    'academic-rooms': () => t('rooms.title'),
    'academic-exam-schedule': () => t('exams.title'),
    'academic-profile': () => t('common.profile'),
    'academic-help': () => t('layout.help'),
    'academic-notifications': () => t('layout.notifications'),
    'registrar-dashboard': () => 'Registrator ofisi',
    'registrar-students': () => t('layout.students'),
    'registrar-attendance': () => t('layout.attendance'),
    'registrar-nb-permits': () => 'NB Ruxsatnomalar',
    'registrar-profile': () => t('common.profile'),
    'registrar-help': () => t('layout.help'),
    'registrar-notifications': () => t('layout.notifications'),
    'teacher-nb-permits': () => 'NB Ruxsatnomalar',
    'dean-dashboard': () => 'Dekanat paneli',
    'dean-students': () => 'Talabalar kontingenti',
    'dean-attendance': () => t('layout.attendance'),
    'dean-schedule': () => t('layout.schedule'),
    'dean-workload': () => t('teacher.workload'),
    'dean-contracts': () => t('layout.contracts'),
    'dean-nb-permits': () => 'NB Ruxsatnomalar',
    'dean-profile': () => t('common.profile'),
    'dean-help': () => t('layout.help'),
    'dean-notifications': () => t('layout.notifications'),
  }
  const fn = titles[route.name]
  return fn ? fn() : t('layout.controlPanel')
})

const menuSections = computed(() => {
  const sections = []

  if (authStore.isStudent) {
    sections.push({
      title: t('layout.main'),
      items: [
        { path: '/student/dashboard', label: t('layout.dashboard'), icon: markRaw(Home) },
        { path: '/student/schedule', label: t('layout.schedule'), icon: markRaw(Calendar) },
        { path: '/student/attendance', label: t('layout.attendance'), icon: markRaw(ClipboardCheck) }
      ]
    })
    sections.push({
      title: t('layout.services'),
      items: [
        { path: '/student/library', label: t('layout.library'), icon: markRaw(BookOpen) },
        ...(hasAIAccess.value ? [{ path: '/student/ai-analysis', label: t('layout.aiAnalysis'), icon: markRaw(Brain) }] : []),
        { path: '/student/clubs', label: t('layout.clubs'), icon: markRaw(Palette) },
        { path: '/student/tournaments', label: t('layout.tournaments'), icon: markRaw(Trophy) },
        { path: '/student/canteen', label: t('layout.canteen'), icon: markRaw(UtensilsCrossed) },
        { path: '/student/market', label: t('layout.market'), icon: markRaw(Store) },
        { path: '/student/quizzes', label: t('layout.quizzes'), icon: markRaw(ClipboardList) },
        { path: '/student/credit-module', label: t('layout.creditModule'), icon: markRaw(Calculator) },
        { path: '/student/exam-schedule', label: t('exams.title'), icon: markRaw(CalendarCheck) },
        { path: '/student/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) },
        { path: '/student/notifications', label: t('layout.notifications'), icon: markRaw(Bell), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/student/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/student/settings', label: t('layout.settings'), icon: markRaw(Settings) },
        { path: '/student/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isLeader) {
    sections.push({
      title: t('layout.management'),
      items: [
        { path: '/leader/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/leader/attendance', label: t('layout.takeAttendance'), icon: markRaw(ClipboardCheck) },
        { path: '/leader/students', label: t('layout.students'), icon: markRaw(Users) },
        { path: '/leader/contracts', label: t('layout.contracts'), icon: markRaw(FileSpreadsheet) }
      ]
    })
    sections.push({
      title: t('layout.group'),
      items: [
        { path: '/leader/schedule', label: t('layout.schedule'), icon: markRaw(Calendar) },
        { path: '/leader/reports', label: t('layout.reports'), icon: markRaw(FileText) },
        { path: '/leader/analytics', label: t('layout.analytics'), icon: markRaw(BarChart3) },
        ...(hasAIAccess.value ? [{ path: '/leader/ai-analysis', label: t('layout.aiAnalysis'), icon: markRaw(Brain) }] : []),
        { path: '/leader/library', label: t('layout.library'), icon: markRaw(BookOpen) },
        { path: '/leader/clubs', label: t('layout.clubs'), icon: markRaw(Palette) },
        { path: '/leader/tournaments', label: t('layout.tournaments'), icon: markRaw(Trophy) },
        { path: '/leader/canteen', label: t('layout.canteen'), icon: markRaw(UtensilsCrossed) },
        { path: '/leader/exam-schedule', label: t('exams.title'), icon: markRaw(CalendarCheck) },
        { path: '/leader/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) },
        { path: '/leader/files', label: t('layout.files'), icon: markRaw(FolderOpen) },
        { path: '/leader/market', label: t('layout.market'), icon: markRaw(Store) },
        { path: '/leader/quizzes', label: t('layout.quizzes'), icon: markRaw(ClipboardList) },
        { path: '/leader/credit-module', label: t('layout.creditModule'), icon: markRaw(Calculator) },
        { path: '/leader/notifications', label: t('layout.notifications'), icon: markRaw(Send), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/leader/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/leader/settings', label: t('layout.settings'), icon: markRaw(Settings) },
        { path: '/leader/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isTeacher) {
    sections.push({
      title: t('teacher.teaching'),
      items: [
        { path: '/teacher/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/teacher/schedule', label: t('layout.schedule'), icon: markRaw(Calendar) },
        { path: '/teacher/groups', label: t('layout.groups'), icon: markRaw(Building2) },
        { path: '/teacher/attendance', label: t('layout.attendance'), icon: markRaw(ClipboardCheck) },
        { path: '/teacher/workload', label: t('teacher.workload'), icon: markRaw(CalendarClock) },
        { path: '/teacher/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) },
        ...(hasAIAccess.value ? [{ path: '/teacher/ai-analysis', label: t('layout.aiAnalysis'), icon: markRaw(Brain) }] : []),
        { path: '/teacher/notifications', label: t('layout.notifications'), icon: markRaw(Bell), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/teacher/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/teacher/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isAcademicAffairs) {
    sections.push({
      title: t('academic.title'),
      items: [
        { path: '/academic/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/academic/schedule-editor', label: t('academic.scheduleEditor'), icon: markRaw(Table2) },
        { path: '/academic/ai-generate', label: t('academic.aiGenerate'), icon: markRaw(Sparkles) },
        { path: '/academic/groups', label: t('academic.manageGroups'), icon: markRaw(Building2) },
        { path: '/academic/workload', label: t('teacher.workload'), icon: markRaw(CalendarClock) },
        { path: '/academic/kontingent-import', label: 'Kontingent import', icon: markRaw(Users) },
        { path: '/academic/schedule-import', label: 'Jadval import', icon: markRaw(CalendarDays) },
        { path: '/academic/workload-import', label: "Bandlik import", icon: markRaw(FileUp) },
        { path: '/academic/room-import', label: 'Xona bandlik import', icon: markRaw(DoorOpen) },
        { path: '/academic/rooms', label: t('rooms.title'), icon: markRaw(DoorOpen) },
        { path: '/academic/exam-schedule', label: t('exams.title'), icon: markRaw(CalendarCheck) },
        { path: '/academic/notifications', label: t('layout.notifications'), icon: markRaw(Bell), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/academic/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/academic/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isRegistrarOffice) {
    sections.push({
      title: 'Registrator ofisi',
      items: [
        { path: '/registrar/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/registrar/students', label: t('layout.students'), icon: markRaw(Users) },
        { path: '/registrar/attendance', label: t('layout.attendance'), icon: markRaw(ClipboardCheck) },
        { path: '/registrar/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) },
        { path: '/registrar/notifications', label: t('layout.notifications'), icon: markRaw(Bell), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/registrar/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/registrar/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isDean) {
    sections.push({
      title: 'Dekanat',
      items: [
        { path: '/dean/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/dean/students', label: 'Talabalar kontingenti', icon: markRaw(Users) },
        { path: '/dean/attendance', label: t('layout.attendance'), icon: markRaw(ClipboardCheck) },
        { path: '/dean/schedule', label: t('layout.schedule'), icon: markRaw(Calendar) },
        { path: '/dean/workload', label: t('teacher.workload'), icon: markRaw(CalendarClock) },
        { path: '/dean/contracts', label: t('layout.contracts'), icon: markRaw(FileSpreadsheet) },
        { path: '/dean/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) },
        ...(hasAIAccess.value ? [{ path: '/dean/ai-analysis', label: t('layout.aiAnalysis'), icon: markRaw(Brain) }] : []),
        { path: '/dean/notifications', label: t('layout.notifications'), icon: markRaw(Bell), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/dean/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/dean/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isAdmin) {
    sections.push({
      title: t('layout.management'),
      items: [
        { path: '/admin/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/admin/attendance', label: t('layout.attendance') || 'Davomat', icon: markRaw(ClipboardCheck) },
        { path: '/admin/students', label: t('layout.students'), icon: markRaw(Users) },
        { path: '/admin/groups', label: t('layout.groups'), icon: markRaw(Building2) },
        { path: '/admin/users', label: t('layout.users'), icon: markRaw(Shield) },
        { path: '/admin/clubs', label: t('layout.clubs'), icon: markRaw(Palette) },
        { path: '/admin/tournaments', label: t('layout.tournaments'), icon: markRaw(Trophy) },
        { path: '/admin/subjects', label: t('layout.subjects'), icon: markRaw(BookOpen) },
        { path: '/admin/holidays', label: t('layout.holidays'), icon: markRaw(CalendarOff) },
        { path: '/admin/schedule', label: t('layout.schedule'), icon: markRaw(Calendar) },
        { path: '/admin/contracts', label: t('layout.contracts'), icon: markRaw(FileSpreadsheet) },
        { path: '/admin/kontingent-import', label: 'Kontingent import', icon: markRaw(Users) },
        { path: '/admin/schedule-import', label: 'Jadval import', icon: markRaw(CalendarDays) },
        { path: '/admin/workload-import', label: "Bandlik import", icon: markRaw(FileUp) },
        { path: '/admin/room-import', label: 'Xona bandlik import', icon: markRaw(DoorOpen) },
        { path: '/admin/workload', label: t('teacher.workload'), icon: markRaw(CalendarClock) },
        { path: '/admin/ai-analysis', label: t('layout.aiAnalysis'), icon: markRaw(Brain) },
        { path: '/admin/credit-module', label: t('layout.creditModule'), icon: markRaw(Calculator) },
        { path: '/admin/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) }
      ]
    })
    sections.push({
      title: t('layout.reports'),
      items: [
        { path: '/admin/reports', label: t('layout.reports'), icon: markRaw(BarChart3) },
        { path: '/admin/notifications', label: t('layout.notifications'), icon: markRaw(Send), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/admin/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/admin/settings', label: t('layout.settings'), icon: markRaw(Settings) },
        { path: '/admin/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
      ]
    })
  }

  if (authStore.isSuperAdmin) {
    sections.push({
      title: t('layout.superAdmin'),
      items: [
        { path: '/super/dashboard', label: t('layout.dashboard'), icon: markRaw(LayoutDashboard) },
        { path: '/super/attendance', label: t('layout.attendance') || 'Davomat', icon: markRaw(ClipboardCheck) },
        { path: '/super/admins', label: t('layout.admins'), icon: markRaw(ShieldCheck) },
        { path: '/super/users', label: t('layout.users') || 'Foydalanuvchilar', icon: markRaw(Users) },
        { path: '/super/landing', label: t('layout.mainPage'), icon: markRaw(Home) },
        { path: '/super/settings', label: t('layout.settings'), icon: markRaw(Settings) },
        { path: '/super/logs', label: t('layout.logs'), icon: markRaw(FileText) },
        { path: '/super/activity', label: t('activity.title') || 'Faoliyatlar', icon: markRaw(Activity) }
      ]
    })
    sections.push({
      title: t('layout.systemManagement'),
      items: [
        { path: '/super/students', label: t('layout.students'), icon: markRaw(Users) },
        { path: '/super/groups', label: t('layout.groups'), icon: markRaw(Building2) },
        { path: '/super/contracts', label: t('layout.contracts'), icon: markRaw(FileSpreadsheet) },
        { path: '/super/subjects', label: t('layout.subjects'), icon: markRaw(BookOpen) },
        { path: '/super/holidays', label: t('layout.holidays'), icon: markRaw(CalendarOff) },
        { path: '/super/schedule', label: t('layout.schedule'), icon: markRaw(Calendar) },
        { path: '/super/workload', label: t('teacher.workload'), icon: markRaw(CalendarClock) },
        { path: '/super/rooms', label: t('rooms.title'), icon: markRaw(DoorOpen) },
        { path: '/super/nb-permits', label: 'NB Ruxsatnomalar', icon: markRaw(FileCheck) }
      ]
    })
    sections.push({
      title: t('academic.title'),
      items: [
        { path: '/super/schedule-editor', label: t('academic.scheduleEditor'), icon: markRaw(Table2) },
        { path: '/super/ai-generate', label: t('academic.aiGenerate'), icon: markRaw(Sparkles) },
        { path: '/super/exam-schedule', label: t('exams.title'), icon: markRaw(CalendarCheck) },
        { path: '/super/kontingent-import', label: 'Kontingent import', icon: markRaw(Users) },
        { path: '/super/schedule-import', label: 'Jadval import', icon: markRaw(CalendarDays) },
        { path: '/super/workload-import', label: "Bandlik import", icon: markRaw(FileUp) },
        { path: '/super/room-import', label: 'Xona bandlik import', icon: markRaw(DoorOpen) }
      ]
    })
    sections.push({
      title: t('layout.services'),
      items: [
        { path: '/super/clubs', label: t('layout.clubs'), icon: markRaw(Palette) },
        { path: '/super/tournaments', label: t('layout.tournaments'), icon: markRaw(Trophy) },
        { path: '/super/canteen', label: t('layout.canteen'), icon: markRaw(UtensilsCrossed) },
        { path: '/super/market', label: t('layout.market'), icon: markRaw(Store) },
        { path: '/super/library', label: t('layout.library'), icon: markRaw(BookOpen) },
        { path: '/super/quizzes', label: t('layout.quizzes'), icon: markRaw(ClipboardList) },
        { path: '/super/credit-module', label: t('layout.creditModule'), icon: markRaw(Calculator) },
        { path: '/super/ai-analysis', label: t('layout.aiAnalysis'), icon: markRaw(Brain) }
      ]
    })
    sections.push({
      title: t('layout.reports') + ' & ' + t('layout.analytics'),
      items: [
        { path: '/super/reports', label: t('layout.reports'), icon: markRaw(BarChart3) },
        { path: '/super/analytics', label: t('layout.analytics'), icon: markRaw(BarChart3) },
        { path: '/super/files', label: t('layout.files'), icon: markRaw(FolderOpen) },
        { path: '/super/notifications', label: t('layout.notifications'), icon: markRaw(Send), badge: dataStore.unreadCount > 0 ? String(dataStore.unreadCount) : null },
        { path: '/super/subscriptions', label: t('layout.subscriptions'), icon: markRaw(CreditCard) },
        { path: '/super/telegram-bot', label: t('layout.telegramBot'), icon: markRaw(Bot) }
      ]
    })
    sections.push({
      title: t('common.profile'),
      items: [
        { path: '/super/profile', label: t('layout.myProfile'), icon: markRaw(User) },
        { path: '/super/help', label: t('layout.help'), icon: markRaw(HelpCircle) }
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
  if (authStore.isDean) return '/dean/profile'
  if (authStore.isRegistrarOffice) return '/registrar/profile'
  if (authStore.isAcademicAffairs) return '/academic/profile'
  if (authStore.isTeacher) return '/teacher/profile'
  if (authStore.isLeader) return '/leader/profile'
  if (authStore.isStudent) return '/student/profile'
  if (authStore.isAdmin) return '/admin/profile'
  if (authStore.isSuperAdmin) return '/super/profile'
  return '/student/profile'
})

const getSettingsPath = computed(() => {
  if (authStore.isDean) return '/dean/profile'
  if (authStore.isRegistrarOffice) return '/registrar/profile'
  if (authStore.isAcademicAffairs) return '/academic/profile'
  if (authStore.isTeacher) return '/teacher/profile'
  if (authStore.isLeader) return '/leader/settings'
  if (authStore.isStudent) return '/student/settings'
  if (authStore.isAdmin) return '/admin/settings'
  if (authStore.isSuperAdmin) return '/super/settings'
  return '/student/settings'
})

const getHelpPath = computed(() => {
  if (authStore.isDean) return '/dean/help'
  if (authStore.isRegistrarOffice) return '/registrar/help'
  if (authStore.isAcademicAffairs) return '/academic/help'
  if (authStore.isTeacher) return '/teacher/help'
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

const goToNotifications = () => {
  if (authStore.isStudent) router.push('/student/notifications')
  else if (authStore.isDean) router.push('/dean/notifications')
  else if (authStore.isRegistrarOffice) router.push('/registrar/notifications')
  else if (authStore.isAcademicAffairs) router.push('/academic/notifications')
  else if (authStore.isTeacher) router.push('/teacher/notifications')
  else if (authStore.isLeader) router.push('/leader/notifications')
  else if (authStore.isAdmin) router.push('/admin/notifications')
  else if (authStore.isSuperAdmin) router.push('/super/notifications')
}

const handleClickOutside = (e) => {
  if (isDropdownOpen.value && !e.target.closest('.relative')) {
    isDropdownOpen.value = false
  }
}

const handleKeyboard = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    showSearch.value = !showSearch.value
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeyboard)
  // Real-time polling ishga tushirish
  dataStore.startPolling(getPollingTypes())
  // AI huquqini tekshirish (sidebar menu uchun)
  try {
    const accessResp = await api.aiCheckAccess()
    hasAIAccess.value = accessResp?.has_access === true
  } catch { hasAIAccess.value = false }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeyboard)
  // Polling to'xtatish
  dataStore.stopPolling()
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
