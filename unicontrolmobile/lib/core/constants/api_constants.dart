/// API Constants
/// Backend API bilan bog'liq barcha konstantalar
library;

class ApiConstants {
  ApiConstants._();

  // Base URL - Production server
  static const String baseUrl = 'https://unicontrol.uz/api/mobile';

  // Timeout durations
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // Auth endpoints (/api/mobile/auth)
  static const String login = '/auth/login';
  static const String logout = '/auth/logout';
  static const String refresh = '/auth/refresh';
  static const String me = '/auth/me';
  static const String registerDevice = '/auth/register-device';

  // Student endpoints (/api/mobile/student)
  static const String studentProfile = '/student/profile';
  static const String studentDashboard = '/student/dashboard';
  static const String studentAttendance = '/student/attendance';
  static const String studentScheduleToday = '/student/schedule/today';
  static const String studentScheduleWeek = '/student/schedule/week';
  static const String studentNotifications = '/student/notifications';
  static const String studentNotificationRead = '/student/notifications/{id}/read';

  // Leader endpoints (/api/mobile/leader)
  static const String leaderDashboard = '/leader/dashboard';
  static const String leaderStudents = '/leader/students';
  static const String leaderAttendanceToday = '/leader/attendance/today';
  static const String leaderAttendanceQuick = '/leader/attendance/quick';
  static const String leaderAttendanceBulk = '/leader/attendance/bulk';
  static const String leaderScheduleToday = '/leader/schedule/today';
  static const String leaderStatsWeek = '/leader/stats/week';
  static const String leaderSendNotification = '/leader/send-notification';

  // Push endpoints (/api/mobile/push)
  static const String pushRegister = '/push/register';
  static const String pushSend = '/push/send';

  // Legacy endpoints (v1 API - for admin features)
  static const String v1BaseUrl = 'https://unicontrol.uz/api/v1';

  // Students endpoints
  static const String students = '/students';
  static const String studentById = '/students/{id}';

  // Groups endpoints
  static const String groups = '/groups';
  static const String groupById = '/groups/{id}';
  static const String groupStudents = '/groups/{id}/students';

  // Attendance endpoints
  static const String attendance = '/attendance';
  static const String attendanceByDate = '/attendance/date/{date}';
  static const String attendanceStats = '/attendance/statistics';

  // Schedule endpoints
  static const String schedule = '/schedule';
  static const String scheduleToday = '/schedule/today';
  static const String scheduleWeek = '/schedule/week';

  // Reports endpoints
  static const String reports = '/reports';
  static const String reportById = '/reports/{id}';

  // Notifications endpoints
  static const String notifications = '/notifications';
  static const String notificationRead = '/notifications/{id}/read';
  static const String notificationReadAll = '/notifications/read-all';
  static const String notificationUnreadCount = '/notifications/unread-count';

  // Dashboard endpoints
  static const String dashboard = '/dashboard';
  static const String dashboardStats = '/dashboard/stats';

  // Clubs endpoints
  static const String clubs = '/clubs';
  static const String clubById = '/clubs/{id}';
  static const String clubJoin = '/clubs/{id}/join';
  static const String clubLeave = '/clubs/{id}/leave';

  // Tournaments endpoints
  static const String tournaments = '/tournaments';
  static const String tournamentById = '/tournaments/{id}';
  static const String tournamentRegister = '/tournaments/{id}/register';

  // Users endpoints (admin)
  static const String users = '/users';
  static const String userById = '/users/{id}';
  static const String changePassword = '/auth/change-password';

  // Reports endpoints
  static const String reports = '/reports';
  static const String reportById = '/reports/{id}';
  static const String reportSubmit = '/reports/submit';

  // System endpoints
  static const String health = '/health';
}

/// Storage keys for local storage
class StorageKeys {
  StorageKeys._();

  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String user = 'user';
  static const String isLoggedIn = 'is_logged_in';
  static const String locale = 'locale';
  static const String themeMode = 'theme_mode';
  static const String onboardingComplete = 'onboarding_complete';
  static const String lastActivity = 'last_activity';
  static const String deviceToken = 'device_token';
}

