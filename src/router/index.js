/**
 * ============================================
 * UNI CONTROL - Vue Router Configuration
 * ============================================
 * 
 * Bu fayl barcha route'lar va navigation guards'ni o'z ichiga oladi.
 * 
 * ROUTE TUZILISHI:
 * ----------------
 * '/'           -> '/login' ga redirect
 * '/login'      -> LoginView (guest only)
 * '/student/*'  -> Talaba sahifalari (role: student)
 * '/leader/*'   -> Sardor sahifalari (role: leader)
 * '/admin/*'    -> Admin sahifalari (role: admin)
 * '/super/*'    -> Super admin sahifalari (role: superadmin)
 * 
 * META MA'LUMOTLARI:
 * ------------------
 * - requiresAuth: true  -> Faqat login qilgan foydalanuvchilar
 * - guest: true         -> Faqat login qilmagan foydalanuvchilar
 * - role: 'student'     -> Faqat shu rol kirishi mumkin
 * 
 * NAVIGATION GUARDS:
 * ------------------
 * router.beforeEach() - har bir sahifaga o'tishdan oldin tekshiradi:
 * 1. Autentifikatsiya (login qilinganmi?)
 * 2. Rol huquqlari (shu sahifaga kirish mumkinmi?)
 * 3. Guest sahifalar (login bo'lsa redirect)
 * 
 * MUHIM: SuperAdmin barcha sahifalarga kira oladi!
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import MainLayout from '../layouts/MainLayout.vue'
import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'

// Student views
import StudentAttendance from '../views/student/AttendanceView.vue'
import StudentCanteen from '../views/student/CanteenView.vue'
import StudentClubs from '../views/student/ClubsView.vue'
import StudentDashboard from '../views/student/DashboardView.vue'
import StudentHelp from '../views/student/HelpView.vue'
import StudentLibrary from '../views/student/LibraryView.vue'
import StudentNotifications from '../views/student/NotificationsView.vue'
import StudentProfile from '../views/student/ProfileView.vue'
import StudentSchedule from '../views/student/ScheduleView.vue'
import StudentSettings from '../views/student/SettingsView.vue'
import StudentTournaments from '../views/student/TournamentsView.vue'

// Leader views
import LeaderAnalytics from '../views/leader/AnalyticsView.vue'
import LeaderAttendance from '../views/leader/AttendanceView.vue'
import LeaderContracts from '../views/leader/ContractsView.vue'
import LeaderDashboard from '../views/leader/DashboardView.vue'
import LeaderFileManager from '../views/leader/FileManagerView.vue'
import LeaderNotifications from '../views/leader/NotificationsView.vue'
import LeaderReports from '../views/leader/ReportsView.vue'
import LeaderSchedule from '../views/leader/ScheduleView.vue'
import LeaderStudents from '../views/leader/StudentsView.vue'
import LeaderSubscription from '../views/leader/SubscriptionView.vue'

// Admin views
import AdminAttendance from '../views/admin/AttendanceView.vue'
import AdminClubs from '../views/admin/ClubsView.vue'
import AdminContracts from '../views/admin/ContractsView.vue'
import AdminDashboard from '../views/admin/DashboardView.vue'
import AdminGroups from '../views/admin/GroupsView.vue'
import AdminImport from '../views/admin/ImportView.vue'
import AdminHolidays from '../views/admin/HolidaysView.vue'
import AdminNotifications from '../views/admin/NotificationsView.vue'
import AdminReports from '../views/admin/ReportsView.vue'
import AdminStudents from '../views/admin/StudentsView.vue'
import AdminSubjects from '../views/admin/SubjectsView.vue'
import AdminTournaments from '../views/admin/TournamentsView.vue'
import AdminUsers from '../views/admin/UsersView.vue'

// Super Admin views
import SuperAdmins from '../views/super/AdminsView.vue'
import SuperContracts from '../views/super/ContractsView.vue'
import SuperDashboard from '../views/super/DashboardView.vue'
import SuperHelpManage from '../views/super/HelpManageView.vue'
import SuperLandingSettings from '../views/super/LandingSettingsView.vue'
import SuperLogs from '../views/super/LogsView.vue'
import SuperReports from '../views/super/ReportsView.vue'
import SuperSettings from '../views/super/SettingsView.vue'
import SuperSubscriptions from '../views/super/SubscriptionsView.vue'
import SuperTelegramBot from '../views/super/TelegramBotView.vue'
import SuperUsers from '../views/super/UsersView.vue'

// Market views
import AIAnalysisView from '../views/shared/AIAnalysisView.vue'
import CreditModuleView from '../views/shared/CreditModuleView.vue'
import MarketAdminView from '../views/shared/MarketAdminView.vue'
import MarketView from '../views/shared/MarketView.vue'
import QuizView from '../views/shared/QuizView.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView,
    meta: { guest: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guest: true }
  },

  // Student routes
  {
    path: '/student',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: '', redirect: '/student/dashboard' },
      { path: 'dashboard', name: 'student-dashboard', component: StudentDashboard },
      { path: 'schedule', name: 'student-schedule', component: StudentSchedule },
      { path: 'attendance', name: 'student-attendance', component: StudentAttendance },
      { path: 'library', name: 'student-library', component: StudentLibrary },
      { path: 'ai-analysis', name: 'student-ai-analysis', component: AIAnalysisView },
      { path: 'notifications', name: 'student-notifications', component: StudentNotifications },
      { path: 'profile', name: 'student-profile', component: StudentProfile },
      { path: 'settings', name: 'student-settings', component: StudentSettings },
      { path: 'help', name: 'student-help', component: StudentHelp },
      { path: 'clubs', name: 'student-clubs', component: StudentClubs },
      { path: 'canteen', name: 'student-canteen', component: StudentCanteen },
      { path: 'tournaments', name: 'student-tournaments', component: StudentTournaments },
      { path: 'subscription', name: 'student-subscription', component: LeaderSubscription },
      { path: 'market', name: 'student-market', component: MarketView },
      { path: 'quizzes', name: 'student-quizzes', component: QuizView },
      { path: 'credit-module', name: 'student-credit-module', component: CreditModuleView }
    ]
  },

  // Leader routes
  {
    path: '/leader',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'leader' },
    children: [
      { path: '', redirect: '/leader/dashboard' },
      { path: 'dashboard', name: 'leader-dashboard', component: LeaderDashboard },
      { path: 'attendance', name: 'leader-attendance', component: LeaderAttendance },
      { path: 'students', name: 'leader-students', component: LeaderStudents },
      { path: 'contracts', name: 'leader-contracts', component: LeaderContracts },
      { path: 'schedule', name: 'leader-schedule', component: LeaderSchedule },
      { path: 'reports', name: 'leader-reports', component: LeaderReports },
      { path: 'notifications', name: 'leader-notifications', component: LeaderNotifications },
      { path: 'analytics', name: 'leader-analytics', component: LeaderAnalytics },
      { path: 'files', name: 'leader-files', component: LeaderFileManager },
      { path: 'subscription', name: 'leader-subscription', component: LeaderSubscription },
      { path: 'profile', name: 'leader-profile', component: StudentProfile },
      { path: 'settings', name: 'leader-settings', component: StudentSettings },
      { path: 'help', name: 'leader-help', component: StudentHelp },
      { path: 'market', name: 'leader-market', component: MarketView },
      { path: 'quizzes', name: 'leader-quizzes', component: QuizView },
      { path: 'ai-analysis', name: 'leader-ai-analysis', component: AIAnalysisView },
      { path: 'credit-module', name: 'leader-credit-module', component: CreditModuleView },
      { path: 'library', name: 'leader-library', component: StudentLibrary },
      { path: 'clubs', name: 'leader-clubs', component: StudentClubs },
      { path: 'canteen', name: 'leader-canteen', component: StudentCanteen },
      { path: 'tournaments', name: 'leader-tournaments', component: StudentTournaments }
    ]
  },

  // Admin routes
  {
    path: '/admin',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: AdminDashboard },
      { path: 'attendance', name: 'admin-attendance', component: AdminAttendance },
      { path: 'students', name: 'admin-students', component: AdminStudents },
      { path: 'groups', name: 'admin-groups', component: AdminGroups },
      { path: 'users', name: 'admin-users', component: AdminUsers },
      { path: 'contracts', name: 'admin-contracts', component: AdminContracts },
      { path: 'reports', name: 'admin-reports', component: AdminReports },
      { path: 'notifications', name: 'admin-notifications', component: AdminNotifications },
      { path: 'clubs', name: 'admin-clubs', component: AdminClubs },
      { path: 'tournaments', name: 'admin-tournaments', component: AdminTournaments },
      { path: 'subjects', name: 'admin-subjects', component: AdminSubjects },
      { path: 'holidays', name: 'admin-holidays', component: AdminHolidays },
      { path: 'import', name: 'admin-import', component: AdminImport },
      { path: 'profile', name: 'admin-profile', component: StudentProfile },
      { path: 'settings', name: 'admin-settings', component: StudentSettings },
      { path: 'help', name: 'admin-help', component: StudentHelp },
      { path: 'ai-analysis', name: 'admin-ai-analysis', component: AIAnalysisView },
      { path: 'credit-module', name: 'admin-credit-module', component: CreditModuleView }
    ]
  },

  // Super Admin routes
  {
    path: '/super',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'superadmin' },
    children: [
      { path: '', redirect: '/super/dashboard' },
      { path: 'dashboard', name: 'super-dashboard', component: SuperDashboard },
      { path: 'attendance', name: 'super-attendance', component: AdminAttendance },
      { path: 'admins', name: 'super-admins', component: SuperAdmins },
      { path: 'settings', name: 'super-settings', component: SuperSettings },
      { path: 'logs', name: 'super-logs', component: SuperLogs },
      { path: 'landing', name: 'super-landing', component: SuperLandingSettings },
      { path: 'students', name: 'super-students', component: AdminStudents },
      { path: 'groups', name: 'super-groups', component: AdminGroups },
      { path: 'reports', name: 'super-reports', component: SuperReports },
      { path: 'notifications', name: 'super-notifications', component: AdminNotifications },
      { path: 'tournaments', name: 'super-tournaments', component: AdminTournaments },
      { path: 'subscriptions', name: 'super-subscriptions', component: SuperSubscriptions },
      { path: 'telegram-bot', name: 'super-telegram-bot', component: SuperTelegramBot },
      { path: 'holidays', name: 'super-holidays', component: AdminHolidays },
      { path: 'users', name: 'super-users', component: SuperUsers },
      { path: 'contracts', name: 'super-contracts', component: SuperContracts },
      { path: 'profile', name: 'super-profile', component: StudentProfile },
      { path: 'help', name: 'super-help', component: StudentHelp },
      { path: 'market', name: 'super-market', component: MarketAdminView },
      { path: 'ai-analysis', name: 'super-ai-analysis', component: AIAnalysisView },
      { path: 'credit-module', name: 'super-credit-module', component: CreditModuleView },
      { path: 'help-manage', name: 'super-help-manage', component: SuperHelpManage },
      { path: 'import', name: 'super-import', component: AdminImport },
      { path: 'subjects', name: 'super-subjects', component: AdminSubjects },
      { path: 'clubs', name: 'super-clubs', component: AdminClubs }
    ]
  },

  // Catch all
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.guest && auth.isAuthenticated) {
    if (auth.isSuperAdmin) return next('/super')
    if (auth.isAdmin) return next('/admin')
    if (auth.isLeader) return next('/leader')
    return next('/student')
  }

  const routeRole = to.matched.find(record => record.meta.role)?.meta.role

  if (routeRole) {
    if (auth.isSuperAdmin) {
      return next()
    }

    switch (routeRole) {
      case 'student':
        if (!auth.isStudent && !auth.isLeader) {
          return next('/admin')
        }
        break
      case 'leader':
        if (!auth.isLeader) {
          return next(auth.isStudent ? '/student' : '/admin')
        }
        break
      case 'admin':
        if (!auth.isAdmin && !auth.isSuperAdmin) {
          return next(auth.isLeader ? '/leader' : '/student')
        }
        break
      case 'superadmin':
        if (!auth.isSuperAdmin) {
          return next(auth.isAdmin ? '/admin' : '/student')
        }
        break
    }
  }

  next()
})

export default router
