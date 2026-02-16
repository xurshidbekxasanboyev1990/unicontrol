/// App Constants
/// Ilova bo'ylab ishlatiladigan umumiy konstantalar
library;

class AppConstants {
  AppConstants._();

  // App info
  static const String appName = 'UniControl';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'University Control System';

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // Date formats
  static const String dateFormat = 'dd.MM.yyyy';
  static const String timeFormat = 'HH:mm';
  static const String dateTimeFormat = 'dd.MM.yyyy HH:mm';
  static const String apiDateFormat = 'yyyy-MM-dd';
  static const String apiDateTimeFormat = "yyyy-MM-dd'T'HH:mm:ss";

  // Timeouts
  static const Duration splashDuration = Duration(seconds: 2);
  static const Duration snackBarDuration = Duration(seconds: 3);
  static const Duration animationDuration = Duration(milliseconds: 300);
  static const Duration debounceDelay = Duration(milliseconds: 500);

  // Polling intervals
  static const Duration pollingInterval = Duration(seconds: 60);
  static const Duration notificationPollingInterval = Duration(seconds: 30);

  // Token refresh
  static const Duration tokenRefreshThreshold = Duration(minutes: 3);
  static const Duration inactivityTimeout = Duration(hours: 24);

  // Validation
  static const int minPasswordLength = 6;
  static const int maxPasswordLength = 50;
  static const int maxNameLength = 150;
  static const int maxEmailLength = 255;
  static const int maxPhoneLength = 20;

  // File upload
  static const int maxFileSize = 10 * 1024 * 1024; // 10 MB
  static const List<String> allowedImageExtensions = ['jpg', 'jpeg', 'png', 'gif'];
  static const List<String> allowedDocExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx'];
}

/// User roles
enum UserRole {
  student('student', 'Talaba'),
  leader('leader', 'Guruh sardori'),
  admin('admin', 'Administrator'),
  superadmin('superadmin', 'Super Admin');

  const UserRole(this.value, this.label);
  final String value;
  final String label;

  static UserRole fromString(String value) {
    return UserRole.values.firstWhere(
      (role) => role.value == value,
      orElse: () => UserRole.student,
    );
  }
}

/// Attendance status
enum AttendanceStatus {
  present('present', 'Keldi', '✅'),
  absent('absent', 'Kelmadi', '❌'),
  late('late', 'Kechikdi', '⏰'),
  excused('excused', 'Sababli', '📋');

  const AttendanceStatus(this.value, this.label, this.emoji);
  final String value;
  final String label;
  final String emoji;

  static AttendanceStatus fromString(String value) {
    return AttendanceStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => AttendanceStatus.absent,
    );
  }
}

/// Report status
enum ReportStatus {
  pending('pending', 'Kutilmoqda'),
  approved('approved', 'Tasdiqlangan'),
  rejected('rejected', 'Rad etilgan');

  const ReportStatus(this.value, this.label);
  final String value;
  final String label;

  static ReportStatus fromString(String value) {
    return ReportStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => ReportStatus.pending,
    );
  }
}

/// Notification types
enum NotificationType {
  info('info', 'Ma\'lumot'),
  warning('warning', 'Ogohlantirish'),
  success('success', 'Muvaffaqiyat'),
  error('error', 'Xatolik'),
  attendance('attendance', 'Davomat'),
  schedule('schedule', 'Dars jadvali'),
  report('report', 'Hisobot'),
  system('system', 'Tizim');

  const NotificationType(this.value, this.label);
  final String value;
  final String label;

  static NotificationType fromString(String value) {
    return NotificationType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => NotificationType.info,
    );
  }
}

/// Days of week
enum DayOfWeek {
  monday(1, 'Dushanba', 'Du'),
  tuesday(2, 'Seshanba', 'Se'),
  wednesday(3, 'Chorshanba', 'Ch'),
  thursday(4, 'Payshanba', 'Pa'),
  friday(5, 'Juma', 'Ju'),
  saturday(6, 'Shanba', 'Sh'),
  sunday(7, 'Yakshanba', 'Ya');

  const DayOfWeek(this.value, this.label, this.shortLabel);
  final int value;
  final String label;
  final String shortLabel;

  static DayOfWeek fromInt(int value) {
    return DayOfWeek.values.firstWhere(
      (day) => day.value == value,
      orElse: () => DayOfWeek.monday,
    );
  }
}

