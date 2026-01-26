import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import LoginView from '../views/LoginView.vue'
import MainLayout from '../layouts/MainLayout.vue'

// Student views
import StudentDashboard from '../views/student/DashboardView.vue'
import StudentSchedule from '../views/student/ScheduleView.vue'
import StudentProfile from '../views/student/ProfileView.vue'
import StudentAttendance from '../views/student/AttendanceView.vue'
import StudentLibrary from '../views/student/LibraryView.vue'
import StudentAIAnalysis from '../views/student/AIAnalysisView.vue'
import StudentNotifications from '../views/student/NotificationsView.vue'
import StudentSettings from '../views/student/SettingsView.vue'
import StudentHelp from '../views/student/HelpView.vue'

// Leader views
import LeaderDashboard from '../views/leader/DashboardView.vue'
import LeaderAttendance from '../views/leader/AttendanceView.vue'
import LeaderStudents from '../views/leader/StudentsView.vue'
import LeaderSchedule from '../views/leader/ScheduleView.vue'
import LeaderReports from '../views/leader/ReportsView.vue'
import LeaderNotifications from '../views/leader/NotificationsView.vue'
import LeaderAnalytics from '../views/leader/AnalyticsView.vue'
import LeaderFileManager from '../views/leader/FileManagerView.vue'

// Admin views
import AdminDashboard from '../views/admin/DashboardView.vue'
import AdminStudents from '../views/admin/StudentsView.vue'
import AdminGroups from '../views/admin/GroupsView.vue'
import AdminUsers from '../views/admin/UsersView.vue'
import AdminReports from '../views/admin/ReportsView.vue'
import AdminNotifications from '../views/admin/NotificationsView.vue'

// Super Admin views
import SuperDashboard from '../views/super/DashboardView.vue'
import SuperAdmins from '../views/super/AdminsView.vue'
import SuperSettings from '../views/super/SettingsView.vue'
import SuperLogs from '../views/super/LogsView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
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
      { path: 'ai-analysis', name: 'student-ai-analysis', component: StudentAIAnalysis },
      { path: 'notifications', name: 'student-notifications', component: StudentNotifications },
      { path: 'profile', name: 'student-profile', component: StudentProfile },
      { path: 'settings', name: 'student-settings', component: StudentSettings },
      { path: 'help', name: 'student-help', component: StudentHelp }
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
      { path: 'schedule', name: 'leader-schedule', component: LeaderSchedule },
      { path: 'reports', name: 'leader-reports', component: LeaderReports },
      { path: 'notifications', name: 'leader-notifications', component: LeaderNotifications },
      { path: 'analytics', name: 'leader-analytics', component: LeaderAnalytics },
      { path: 'files', name: 'leader-files', component: LeaderFileManager },
      { path: 'profile', name: 'leader-profile', component: StudentProfile },
      { path: 'settings', name: 'leader-settings', component: StudentSettings },
      { path: 'help', name: 'leader-help', component: StudentHelp }
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
      { path: 'students', name: 'admin-students', component: AdminStudents },
      { path: 'groups', name: 'admin-groups', component: AdminGroups },
      { path: 'users', name: 'admin-users', component: AdminUsers },
      { path: 'reports', name: 'admin-reports', component: AdminReports },
      { path: 'notifications', name: 'admin-notifications', component: AdminNotifications },
      { path: 'profile', name: 'admin-profile', component: StudentProfile },
      { path: 'settings', name: 'admin-settings', component: StudentSettings },
      { path: 'help', name: 'admin-help', component: StudentHelp }
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
      { path: 'admins', name: 'super-admins', component: SuperAdmins },
      { path: 'settings', name: 'super-settings', component: SuperSettings },
      { path: 'logs', name: 'super-logs', component: SuperLogs },
      { path: 'students', name: 'super-students', component: AdminStudents },
      { path: 'groups', name: 'super-groups', component: AdminGroups },
      { path: 'reports', name: 'super-reports', component: AdminReports },
      { path: 'notifications', name: 'super-notifications', component: AdminNotifications },
      { path: 'profile', name: 'super-profile', component: StudentProfile },
      { path: 'help', name: 'super-help', component: StudentHelp }
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
