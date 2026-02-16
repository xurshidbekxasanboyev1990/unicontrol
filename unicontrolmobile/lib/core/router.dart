/// App Router
/// Go Router konfiguratsiyasi
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/providers/auth_provider.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/splash_screen.dart';
import '../features/dashboard/screens/dashboard_screen.dart';
import '../features/students/screens/students_screen.dart';
import '../features/students/screens/student_detail_screen.dart';
import '../features/attendance/screens/attendance_screen.dart';
import '../features/attendance/screens/mark_attendance_screen.dart';
import '../features/schedule/screens/schedule_screen.dart';
import '../features/groups/screens/groups_screen.dart';
import '../features/notifications/screens/notifications_screen.dart';
import '../features/profile/screens/profile_screen.dart';
import '../features/reports/screens/reports_screen.dart';
import '../features/clubs/screens/clubs_screen.dart';
import '../features/tournaments/screens/tournaments_screen.dart';
import '../features/settings/screens/settings_screen.dart';
import '../widgets/main_shell.dart';

/// Router provider
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/splash',
    debugLogDiagnostics: true,
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isLoading = authState.isLoading;
      final isLoggingIn = state.matchedLocation == '/login';
      final isSplash = state.matchedLocation == '/splash';

      // Loading holatida splash screen
      if (isLoading && !isSplash) {
        return '/splash';
      }

      // Login qilmagan bo'lsa login sahifasiga
      if (!isLoggedIn && !isLoggingIn && !isSplash) {
        return '/login';
      }

      // Login qilgan va login sahifasida bo'lsa dashboard ga
      if (isLoggedIn && isLoggingIn) {
        return '/dashboard';
      }

      return null;
    },
    routes: [
      // Splash screen
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),

      // Login
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),

      // Main shell (bottom navigation)
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          // Dashboard
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),

          // Attendance
          GoRoute(
            path: '/attendance',
            builder: (context, state) => const AttendanceScreen(),
            routes: [
              GoRoute(
                path: 'mark',
                builder: (context, state) {
                  final groupId = state.uri.queryParameters['groupId'];
                  return MarkAttendanceScreen(
                    groupId: groupId != null ? int.parse(groupId) : null,
                  );
                },
              ),
            ],
          ),

          // Schedule
          GoRoute(
            path: '/schedule',
            builder: (context, state) => const ScheduleScreen(),
          ),

          // Profile
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),

      // Students (separate from shell for custom navigation)
      GoRoute(
        path: '/students',
        builder: (context, state) => const StudentsScreen(),
        routes: [
          GoRoute(
            path: ':id',
            builder: (context, state) {
              final id = int.parse(state.pathParameters['id']!);
              return StudentDetailScreen(studentId: id);
            },
          ),
        ],
      ),

      // Groups
      GoRoute(
        path: '/groups',
        builder: (context, state) => const GroupsScreen(),
      ),

      // Notifications
      GoRoute(
        path: '/notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),

      // Reports
      GoRoute(
        path: '/reports',
        builder: (context, state) => const ReportsScreen(),
      ),

      // Clubs
      GoRoute(
        path: '/clubs',
        builder: (context, state) => const ClubsScreen(),
      ),

      // Tournaments
      GoRoute(
        path: '/tournaments',
        builder: (context, state) => const TournamentsScreen(),
      ),

      // Settings
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'Sahifa topilmadi',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              state.error?.message ?? 'Noma\'lum xatolik',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/dashboard'),
              child: const Text('Bosh sahifaga'),
            ),
          ],
        ),
      ),
    ),
  );
});

