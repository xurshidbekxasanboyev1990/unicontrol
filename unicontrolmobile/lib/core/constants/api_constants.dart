/// API Constants
/// Backend API bilan bog'liq barcha konstantalar
/// Barcha endpointlar faqat /api/mobile orqali ishlaydi
library;

class ApiConstants {
  ApiConstants._();

  // Base URL - Production server (mobile API only)
  static const String baseUrl = 'https://unicontrol.uz/api/mobile';

  // Timeout durations
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // ==========================================
  // AUTH ENDPOINTS (/api/mobile/auth)
  // ==========================================
  static const String login = '/auth/login';
  static const String logout = '/auth/logout';
  static const String refresh = '/auth/refresh';
  static const String registerDevice = '/auth/register-device';
  static const String me = '/auth/me';
  static const String changePassword = '/auth/change-password';

  // ==========================================
  // DASHBOARD ENDPOINTS (/api/mobile/dashboard)
  // ==========================================
  static const String dashboardStats = '/dashboard/stats';

  // ==========================================
  // STUDENT ENDPOINTS (/api/mobile/student)
  // ==========================================
  static const String studentProfile = '/student/profile';
  static const String studentDashboard = '/student/dashboard';
  static const String studentAttendance = '/student/attendance';
  static const String studentScheduleToday = '/student/schedule/today';
  static const String studentScheduleWeek = '/student/schedule/week';
  static const String studentNotifications = '/student/notifications';
  static const String studentNotificationRead = '/student/notifications/{id}/read';

  // ==========================================
  // LEADER ENDPOINTS (/api/mobile/leader)
  // ==========================================
  static const String leaderDashboard = '/leader/dashboard';
  static const String leaderStudents = '/leader/students';
  static const String leaderAttendanceToday = '/leader/attendance/today';
  static const String leaderAttendanceQuick = '/leader/attendance/quick';
  static const String leaderAttendanceBulk = '/leader/attendance/bulk';
  static const String leaderScheduleToday = '/leader/schedule/today';
  static const String leaderStatsWeek = '/leader/stats/week';
  static const String leaderSendNotification = '/leader/send-notification';

  // ==========================================
  // GENERAL ENDPOINTS (/api/mobile/...)
  // ==========================================
  // Schedule
  static const String schedule = '/schedule';
  static const String scheduleToday = '/schedule/today';
  static const String scheduleWeek = '/schedule/week';

  // Attendance
  static const String attendance = '/attendance';
  static const String attendanceBatch = '/attendance/batch';
  static const String attendanceStats = '/attendance/stats';

  // Students
  static const String students = '/students';
  static const String studentById = '/students/{id}';

  // Groups
  static const String groups = '/groups';
  static const String groupById = '/groups/{id}';
  static const String groupStudents = '/groups/{id}/students';

  // Notifications
  static const String notifications = '/notifications';
  static const String notificationUnreadCount = '/notifications/unread-count';
  static const String notificationRead = '/notifications/{id}/read';
  static const String notificationReadAll = '/notifications/read-all';

  // ==========================================
  // CLUBS ENDPOINTS (/api/mobile/clubs)
  // ==========================================
  static const String clubs = '/clubs';
  static const String clubById = '/clubs/{id}';
  static const String clubJoin = '/clubs/{id}/join';
  static const String clubLeave = '/clubs/{id}/leave';

  // ==========================================
  // TOURNAMENTS ENDPOINTS (/api/mobile/tournaments)
  // ==========================================
  static const String tournaments = '/tournaments';
  static const String tournamentById = '/tournaments/{id}';
  static const String tournamentRegister = '/tournaments/{id}/register';
  static const String tournamentUnregister = '/tournaments/{id}/unregister';

  // ==========================================
  // REPORTS ENDPOINTS (/api/mobile/reports)
  // ==========================================
  static const String reports = '/reports';
  static const String reportById = '/reports/{id}';

  // ==========================================
  // PUSH ENDPOINTS (/api/mobile/push)
  // ==========================================
  static const String pushRegister = '/push/register';
  static const String pushSend = '/push/send';

  // System
  static const String health = '/health';
}

/// Storage keys for local storage
class StorageKeys {
  StorageKeys._();

  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String user = 'user_data';
  static const String isLoggedIn = 'is_logged_in';
  static const String language = 'language';
  static const String theme = 'theme';
  static const String deviceToken = 'device_token';
}

