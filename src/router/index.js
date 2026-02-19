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
import StudentClubs from '../views/student/ClubsView.vue'
import StudentDashboard from '../views/student/DashboardView.vue'
import StudentHelp from '../views/student/HelpView.vue'
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

// Teacher views
import TeacherAttendance from '../views/teacher/AttendanceView.vue'
import TeacherDashboard from '../views/teacher/DashboardView.vue'
import TeacherGroups from '../views/teacher/GroupsView.vue'
import TeacherProfile from '../views/teacher/ProfileView.vue'
import TeacherSchedule from '../views/teacher/ScheduleView.vue'
import TeacherStudents from '../views/teacher/StudentsView.vue'
import TeacherWorkload from '../views/teacher/WorkloadView.vue'

// Academic Affairs views
import AcademicAIGenerate from '../views/academic/AIGenerateView.vue'
import AcademicDashboard from '../views/academic/DashboardView.vue'
import AcademicExamSchedule from '../views/academic/ExamScheduleView.vue'
import AcademicGroups from '../views/academic/GroupsView.vue'
import AcademicRooms from '../views/academic/RoomsView.vue'
import AcademicScheduleEditor from '../views/academic/ScheduleEditorView.vue'

// Admin views
import AdminAttendance from '../views/admin/AttendanceView.vue'
import AdminClubs from '../views/admin/ClubsView.vue'
import AdminContracts from '../views/admin/ContractsView.vue'
import AdminDashboard from '../views/admin/DashboardView.vue'
import AdminGroups from '../views/admin/GroupsView.vue'
import AdminHolidays from '../views/admin/HolidaysView.vue'
import AdminNBPermits from '../views/admin/NBPermitsView.vue'
import AdminNotifications from '../views/admin/NotificationsView.vue'
import AdminReports from '../views/admin/ReportsView.vue'
import AdminSchedule from '../views/admin/ScheduleView.vue'
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

// Shared views - import pages
import KontingentImportView from '../views/shared/KontingentImportView.vue'
import RoomImportView from '../views/shared/RoomImportView.vue'
import ScheduleImportView from '../views/shared/ScheduleImportView.vue'
import WorkloadImportView from '../views/shared/WorkloadImportView.vue'

// Super admin - activity
import SuperActivity from '../views/super/ActivityView.vue'

// Registrar Office views
import RegistrarAttendance from '../views/registrar/AttendanceView.vue'
import RegistrarDashboard from '../views/registrar/DashboardView.vue'
import RegistrarNBPermits from '../views/registrar/NBPermitsView.vue'
import RegistrarStudents from '../views/registrar/StudentsView.vue'

// Dean views
import DeanAttendance from '../views/dean/AttendanceView.vue'
import DeanContracts from '../views/dean/ContractsView.vue'
import DeanDashboard from '../views/dean/DashboardView.vue'
import DeanNBPermits from '../views/dean/NBPermitsView.vue'
import DeanSchedule from '../views/dean/ScheduleView.vue'
import DeanStudents from '../views/dean/StudentsView.vue'
import DeanWorkload from '../views/dean/WorkloadView.vue'

// Student NB Permits
import StudentNBPermits from '../views/student/NBPermitsView.vue'

// Leader NB Permits
import LeaderNBPermits from '../views/leader/NBPermitsView.vue'

// Teacher NB Permits
import TeacherNBPermits from '../views/teacher/NBPermitsView.vue'

// Market & Shared views
import AIAnalysisView from '../views/shared/AIAnalysisView.vue'
import SharedCanteenView from '../views/shared/CanteenView.vue'
import CreditModuleView from '../views/shared/CreditModuleView.vue'
import SharedExamSchedule from '../views/shared/ExamScheduleView.vue'
import LibraryComingSoon from '../views/shared/LibraryComingSoon.vue'
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
      { path: 'library', name: 'student-library', component: LibraryComingSoon },
      { path: 'ai-analysis', name: 'student-ai-analysis', component: AIAnalysisView },
      { path: 'notifications', name: 'student-notifications', component: StudentNotifications },
      { path: 'profile', name: 'student-profile', component: StudentProfile },
      { path: 'settings', name: 'student-settings', component: StudentSettings },
      { path: 'help', name: 'student-help', component: StudentHelp },
      { path: 'clubs', name: 'student-clubs', component: StudentClubs },
      { path: 'canteen', name: 'student-canteen', component: SharedCanteenView },
      { path: 'tournaments', name: 'student-tournaments', component: StudentTournaments },
      { path: 'market', name: 'student-market', component: MarketView },
      { path: 'quizzes', name: 'student-quizzes', component: QuizView },
      { path: 'credit-module', name: 'student-credit-module', component: CreditModuleView },
      { path: 'exam-schedule', name: 'student-exam-schedule', component: SharedExamSchedule },
      { path: 'nb-permits', name: 'student-nb-permits', component: StudentNBPermits }
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
      { path: 'profile', name: 'leader-profile', component: StudentProfile },
      { path: 'settings', name: 'leader-settings', component: StudentSettings },
      { path: 'help', name: 'leader-help', component: StudentHelp },
      { path: 'market', name: 'leader-market', component: MarketView },
      { path: 'quizzes', name: 'leader-quizzes', component: QuizView },
      { path: 'ai-analysis', name: 'leader-ai-analysis', component: AIAnalysisView },
      { path: 'credit-module', name: 'leader-credit-module', component: CreditModuleView },
      { path: 'library', name: 'leader-library', component: LibraryComingSoon },
      { path: 'clubs', name: 'leader-clubs', component: StudentClubs },
      { path: 'canteen', name: 'leader-canteen', component: SharedCanteenView },
      { path: 'tournaments', name: 'leader-tournaments', component: StudentTournaments },
      { path: 'subscription', name: 'leader-subscription', component: LeaderSubscription },
      { path: 'exam-schedule', name: 'leader-exam-schedule', component: SharedExamSchedule },
      { path: 'nb-permits', name: 'leader-nb-permits', component: LeaderNBPermits }
    ]
  },

  // Teacher routes
  {
    path: '/teacher',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      { path: '', redirect: '/teacher/dashboard' },
      { path: 'dashboard', name: 'teacher-dashboard', component: TeacherDashboard },
      { path: 'schedule', name: 'teacher-schedule', component: TeacherSchedule },
      { path: 'groups', name: 'teacher-groups', component: TeacherGroups },
      { path: 'groups/:id/students', name: 'teacher-group-students', component: TeacherStudents },
      { path: 'attendance', name: 'teacher-attendance', component: TeacherAttendance },
      { path: 'workload', name: 'teacher-workload', component: TeacherWorkload },
      { path: 'nb-permits', name: 'teacher-nb-permits', component: TeacherNBPermits },
      { path: 'profile', name: 'teacher-profile', component: TeacherProfile },
      { path: 'help', name: 'teacher-help', component: StudentHelp },
      { path: 'notifications', name: 'teacher-notifications', component: StudentNotifications }
    ]
  },

  // Academic Affairs routes
  {
    path: '/academic',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'academic_affairs' },
    children: [
      { path: '', redirect: '/academic/dashboard' },
      { path: 'dashboard', name: 'academic-dashboard', component: AcademicDashboard },
      { path: 'schedule-editor', name: 'academic-schedule-editor', component: AcademicScheduleEditor },
      { path: 'ai-generate', name: 'academic-ai-generate', component: AcademicAIGenerate },
      { path: 'groups', name: 'academic-groups', component: AcademicGroups },
      { path: 'workload', name: 'academic-workload', component: TeacherWorkload },
      { path: 'workload-import', name: 'academic-workload-import', component: WorkloadImportView },
      { path: 'kontingent-import', name: 'academic-kontingent-import', component: KontingentImportView },
      { path: 'schedule-import', name: 'academic-schedule-import', component: ScheduleImportView },
      { path: 'room-import', name: 'academic-room-import', component: RoomImportView },
      { path: 'rooms', name: 'academic-rooms', component: AcademicRooms },
      { path: 'exam-schedule', name: 'academic-exam-schedule', component: AcademicExamSchedule },
      { path: 'profile', name: 'academic-profile', component: StudentProfile },
      { path: 'help', name: 'academic-help', component: StudentHelp },
      { path: 'notifications', name: 'academic-notifications', component: StudentNotifications }
    ]
  },

  // Registrar Office routes
  {
    path: '/registrar',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'registrar_office' },
    children: [
      { path: '', redirect: '/registrar/dashboard' },
      { path: 'dashboard', name: 'registrar-dashboard', component: RegistrarDashboard },
      { path: 'students', name: 'registrar-students', component: RegistrarStudents },
      { path: 'attendance', name: 'registrar-attendance', component: RegistrarAttendance },
      { path: 'nb-permits', name: 'registrar-nb-permits', component: RegistrarNBPermits },
      { path: 'profile', name: 'registrar-profile', component: StudentProfile },
      { path: 'help', name: 'registrar-help', component: StudentHelp },
      { path: 'notifications', name: 'registrar-notifications', component: StudentNotifications }
    ]
  },

  // Dean routes
  {
    path: '/dean',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'dean' },
    children: [
      { path: '', redirect: '/dean/dashboard' },
      { path: 'dashboard', name: 'dean-dashboard', component: DeanDashboard },
      { path: 'students', name: 'dean-students', component: DeanStudents },
      { path: 'attendance', name: 'dean-attendance', component: DeanAttendance },
      { path: 'schedule', name: 'dean-schedule', component: DeanSchedule },
      { path: 'workload', name: 'dean-workload', component: DeanWorkload },
      { path: 'contracts', name: 'dean-contracts', component: DeanContracts },
      { path: 'nb-permits', name: 'dean-nb-permits', component: DeanNBPermits },
      { path: 'profile', name: 'dean-profile', component: StudentProfile },
      { path: 'help', name: 'dean-help', component: StudentHelp },
      { path: 'notifications', name: 'dean-notifications', component: StudentNotifications }
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
      { path: 'canteen', name: 'admin-canteen', component: SharedCanteenView },
      { path: 'tournaments', name: 'admin-tournaments', component: AdminTournaments },
      { path: 'subjects', name: 'admin-subjects', component: AdminSubjects },
      { path: 'holidays', name: 'admin-holidays', component: AdminHolidays },
      { path: 'schedule', name: 'admin-schedule', component: AdminSchedule },
      { path: 'kontingent-import', name: 'admin-kontingent-import', component: KontingentImportView },
      { path: 'schedule-import', name: 'admin-schedule-import', component: ScheduleImportView },
      { path: 'workload-import', name: 'admin-workload-import', component: WorkloadImportView },
      { path: 'room-import', name: 'admin-room-import', component: RoomImportView },
      { path: 'workload', name: 'admin-workload', component: TeacherWorkload },
      { path: 'profile', name: 'admin-profile', component: StudentProfile },
      { path: 'settings', name: 'admin-settings', component: StudentSettings },
      { path: 'help', name: 'admin-help', component: StudentHelp },
      { path: 'ai-analysis', name: 'admin-ai-analysis', component: AIAnalysisView },
      { path: 'credit-module', name: 'admin-credit-module', component: CreditModuleView },
      { path: 'nb-permits', name: 'admin-nb-permits', component: AdminNBPermits }
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
      { path: 'schedule', name: 'super-schedule', component: AdminSchedule },
      { path: 'users', name: 'super-users', component: SuperUsers },
      { path: 'contracts', name: 'super-contracts', component: SuperContracts },
      { path: 'profile', name: 'super-profile', component: StudentProfile },
      { path: 'help', name: 'super-help', component: StudentHelp },
      { path: 'market', name: 'super-market', component: MarketAdminView },
      { path: 'ai-analysis', name: 'super-ai-analysis', component: AIAnalysisView },
      { path: 'credit-module', name: 'super-credit-module', component: CreditModuleView },
      { path: 'help-manage', name: 'super-help-manage', component: SuperHelpManage },
      { path: 'kontingent-import', name: 'super-kontingent-import', component: KontingentImportView },
      { path: 'schedule-import', name: 'super-schedule-import', component: ScheduleImportView },
      { path: 'workload-import', name: 'super-workload-import', component: WorkloadImportView },
      { path: 'room-import', name: 'super-room-import', component: RoomImportView },
      { path: 'subjects', name: 'super-subjects', component: AdminSubjects },
      { path: 'clubs', name: 'super-clubs', component: AdminClubs },
      { path: 'canteen', name: 'super-canteen', component: SharedCanteenView },
      { path: 'workload', name: 'super-workload', component: TeacherWorkload },
      { path: 'activity', name: 'super-activity', component: SuperActivity },
      { path: 'nb-permits', name: 'super-nb-permits', component: AdminNBPermits }
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
    if (auth.isDean) return next('/dean')
    if (auth.isRegistrarOffice) return next('/registrar')
    if (auth.isAcademicAffairs) return next('/academic')
    if (auth.isTeacher) return next('/teacher')
    if (auth.isLeader) return next('/leader')
    return next('/student')
  }

  const routeRole = to.matched.find(record => record.meta.role)?.meta.role

  if (routeRole) {
    if (auth.isSuperAdmin) {
      return next()
    }

    // Foydalanuvchini o'z dashboard'iga yo'naltirish uchun helper
    const getUserHome = () => {
      if (auth.isAdmin) return '/admin'
      if (auth.isDean) return '/dean'
      if (auth.isRegistrarOffice) return '/registrar'
      if (auth.isAcademicAffairs) return '/academic'
      if (auth.isTeacher) return '/teacher'
      if (auth.isLeader) return '/leader'
      return '/student'
    }

    switch (routeRole) {
      case 'student':
        if (!auth.isStudent && !auth.isLeader) {
          return next(getUserHome())
        }
        break
      case 'leader':
        if (!auth.isLeader) {
          return next(getUserHome())
        }
        break
      case 'teacher':
        if (!auth.isTeacher) {
          return next(getUserHome())
        }
        break
      case 'academic_affairs':
        if (!auth.isAcademicAffairs) {
          return next(getUserHome())
        }
        break
      case 'registrar_office':
        if (!auth.isRegistrarOffice) {
          return next(getUserHome())
        }
        break
      case 'dean':
        if (!auth.isDean) {
          return next(getUserHome())
        }
        break
      case 'admin':
        if (!auth.isAdmin && !auth.isSuperAdmin) {
          return next(getUserHome())
        }
        break
      case 'superadmin':
        if (!auth.isSuperAdmin) {
          return next(getUserHome())
        }
        break
    }
  }

  next()
})

export default router
