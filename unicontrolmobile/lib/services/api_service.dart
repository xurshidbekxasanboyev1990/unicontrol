/// API Service
/// Backend API bilan aloqa qilish uchun asosiy servis
library;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';
import '../core/constants/api_constants.dart';
import '../data/models/models.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  final Logger _logger = Logger();

  String? _accessToken;
  String? _refreshToken;
  bool _isRefreshing = false;

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: ApiConstants.connectTimeout,
      receiveTimeout: ApiConstants.receiveTimeout,
      sendTimeout: ApiConstants.sendTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Request interceptor
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Token qo'shish
        if (_accessToken != null) {
          options.headers['Authorization'] = 'Bearer $_accessToken';
        }

        if (kDebugMode) {
          _logger.d('REQUEST: ${options.method} ${options.path}');
        }

        return handler.next(options);
      },
      onResponse: (response, handler) {
        if (kDebugMode) {
          _logger.d('RESPONSE: ${response.statusCode} ${response.requestOptions.path}');
        }
        return handler.next(response);
      },
      onError: (error, handler) async {
        if (kDebugMode) {
          _logger.e('ERROR: ${error.response?.statusCode} ${error.requestOptions.path}');
        }

        // 401 - token muddati tugagan
        if (error.response?.statusCode == 401 && !_isRefreshing) {
          try {
            final refreshed = await refreshTokens();
            if (refreshed) {
              // Qayta so'rov yuborish
              final opts = error.requestOptions;
              opts.headers['Authorization'] = 'Bearer $_accessToken';
              final response = await _dio.fetch(opts);
              return handler.resolve(response);
            }
          } catch (e) {
            _logger.e('Token refresh failed: $e');
          }
        }

        return handler.next(error);
      },
    ));

    // Token larni yuklash
    _loadTokens();
  }

  Future<void> _loadTokens() async {
    _accessToken = await _storage.read(key: StorageKeys.accessToken);
    _refreshToken = await _storage.read(key: StorageKeys.refreshToken);
  }

  Future<void> _saveTokens(String accessToken, String refreshToken) async {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    await _storage.write(key: StorageKeys.accessToken, value: accessToken);
    await _storage.write(key: StorageKeys.refreshToken, value: refreshToken);
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    _refreshToken = null;
    await _storage.delete(key: StorageKeys.accessToken);
    await _storage.delete(key: StorageKeys.refreshToken);
    await _storage.delete(key: StorageKeys.user);
    await _storage.delete(key: StorageKeys.isLoggedIn);
  }

  bool get isLoggedIn => _accessToken != null;

  // ==========================================
  // AUTH ENDPOINTS
  // ==========================================

  /// Login
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      _logger.d('Attempting login: $username to ${ApiConstants.baseUrl}${ApiConstants.login}');

      final response = await _dio.post(
        ApiConstants.login,
        data: {
          'username': username,
          'password': password,
          'device_token': null, // Firebase token - keyinchalik qo'shiladi
          'device_type': 'android',
        },
      );

      final data = response.data;
      _logger.d('Login success: ${data.keys}');

      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String? ?? '';

      await _saveTokens(accessToken, refreshToken);
      await _storage.write(key: StorageKeys.isLoggedIn, value: 'true');

      return data;
    } on DioException catch (e) {
      _logger.e('Login error: ${e.response?.statusCode} - ${e.response?.data}');
      throw _handleError(e);
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      await _dio.post(ApiConstants.logout);
    } catch (e) {
      // Logout xatosi bo'lsa ham tokenlarni tozalash
    }
    await clearTokens();
  }

  /// Refresh tokens
  Future<bool> refreshTokens() async {
    if (_refreshToken == null || _isRefreshing) return false;

    _isRefreshing = true;
    try {
      final response = await _dio.post(
        ApiConstants.refresh,
        data: {'refresh_token': _refreshToken},
      );

      final data = response.data;
      await _saveTokens(
        data['access_token'] as String,
        data['refresh_token'] as String,
      );

      _isRefreshing = false;
      return true;
    } catch (e) {
      _isRefreshing = false;
      await clearTokens();
      return false;
    }
  }

  /// Get current user
  Future<User> getMe() async {
    try {
      final response = await _dio.get(ApiConstants.me);
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Change password
  Future<void> changePassword(String currentPassword, String newPassword) async {
    try {
      await _dio.post(
        ApiConstants.changePassword,
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // STUDENTS ENDPOINTS
  // ==========================================

  /// Get students list
  Future<List<Student>> getStudents({
    int page = 1,
    int pageSize = 20,
    String? search,
    int? groupId,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.students,
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (search != null && search.isNotEmpty) 'search': search,
          if (groupId != null) 'group_id': groupId,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['students'] ?? data;

      if (items is List) {
        return items.map((e) => Student.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get student by ID
  Future<Student> getStudent(int id) async {
    try {
      final response = await _dio.get(
        ApiConstants.studentById.replaceAll('{id}', id.toString()),
      );
      return Student.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create student
  Future<Student> createStudent(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post(ApiConstants.students, data: data);
      return Student.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Update student
  Future<Student> updateStudent(int id, Map<String, dynamic> data) async {
    try {
      final response = await _dio.put(
        ApiConstants.studentById.replaceAll('{id}', id.toString()),
        data: data,
      );
      return Student.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Delete student
  Future<void> deleteStudent(int id) async {
    try {
      await _dio.delete(
        ApiConstants.studentById.replaceAll('{id}', id.toString()),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // GROUPS ENDPOINTS
  // ==========================================

  /// Get groups list
  Future<List<Group>> getGroups({
    int page = 1,
    int pageSize = 100,
    String? search,
    bool? activeOnly,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.groups,
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (search != null && search.isNotEmpty) 'search': search,
          if (activeOnly != null) 'active_only': activeOnly,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['groups'] ?? data;

      if (items is List) {
        return items.map((e) => Group.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get group by ID
  Future<Group> getGroup(int id) async {
    try {
      final response = await _dio.get(
        ApiConstants.groupById.replaceAll('{id}', id.toString()),
      );
      return Group.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get group students
  Future<List<Student>> getGroupStudents(int groupId) async {
    try {
      final response = await _dio.get(
        ApiConstants.groupStudents.replaceAll('{id}', groupId.toString()),
      );

      final data = response.data;
      final items = data['items'] ?? data['students'] ?? data;

      if (items is List) {
        return items.map((e) => Student.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // ATTENDANCE ENDPOINTS
  // ==========================================

  /// Get attendance records
  Future<List<Attendance>> getAttendance({
    int? groupId,
    int? studentId,
    String? date,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.attendance,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
          if (studentId != null) 'student_id': studentId,
          if (date != null) 'date': date,
          if (startDate != null) 'start_date': startDate,
          if (endDate != null) 'end_date': endDate,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['attendance'] ?? data;

      if (items is List) {
        return items.map((e) => Attendance.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark attendance
  Future<void> markAttendance(List<Map<String, dynamic>> records) async {
    try {
      await _dio.post(
        ApiConstants.attendance,
        data: {'records': records},
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get attendance statistics
  Future<AttendanceStats> getAttendanceStats({
    int? groupId,
    int? studentId,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.attendanceStats,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
          if (studentId != null) 'student_id': studentId,
          if (startDate != null) 'start_date': startDate,
          if (endDate != null) 'end_date': endDate,
        },
      );
      return AttendanceStats.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // SCHEDULE ENDPOINTS
  // ==========================================

  /// Get schedule
  Future<List<Schedule>> getSchedule({int? groupId, int? dayOfWeek}) async {
    try {
      final response = await _dio.get(
        ApiConstants.schedule,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
          if (dayOfWeek != null) 'day_of_week': dayOfWeek,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['schedule'] ?? data;

      if (items is List) {
        return items.map((e) => Schedule.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get today's schedule
  Future<List<Schedule>> getTodaySchedule() async {
    try {
      final response = await _dio.get(ApiConstants.scheduleToday);

      final data = response.data;
      final items = data['items'] ?? data['schedule'] ?? data;

      if (items is List) {
        return items.map((e) => Schedule.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // NOTIFICATIONS ENDPOINTS
  // ==========================================

  /// Get notifications
  Future<List<AppNotification>> getNotifications({
    int page = 1,
    int pageSize = 20,
    bool? unreadOnly,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.notifications,
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (unreadOnly != null) 'unread_only': unreadOnly,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['notifications'] ?? data;

      if (items is List) {
        return items.map((e) => AppNotification.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get unread count
  Future<int> getUnreadNotificationCount() async {
    try {
      final response = await _dio.get(ApiConstants.notificationUnreadCount);
      final data = response.data;
      return data['count'] as int? ?? data as int? ?? 0;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark notification as read
  Future<void> markNotificationRead(int id) async {
    try {
      await _dio.put(
        ApiConstants.notificationRead.replaceAll('{id}', id.toString()),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark all notifications as read
  Future<void> markAllNotificationsRead() async {
    try {
      await _dio.put(ApiConstants.notificationReadAll);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // DASHBOARD ENDPOINTS
  // ==========================================

  /// Get dashboard stats
  Future<DashboardStats> getDashboardStats() async {
    try {
      final response = await _dio.get(ApiConstants.dashboardStats);
      return DashboardStats.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // REPORTS ENDPOINTS
  // ==========================================

  /// Get reports
  Future<List<Report>> getReports({
    int page = 1,
    int pageSize = 20,
    int? groupId,
    String? status,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.reports,
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (groupId != null) 'group_id': groupId,
          if (status != null) 'status': status,
          if (startDate != null) 'start_date': startDate,
          if (endDate != null) 'end_date': endDate,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['reports'] ?? data;

      if (items is List) {
        return items.map((e) => Report.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Submit report
  Future<Report> submitReport(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post(ApiConstants.reportSubmit, data: data);
      return Report.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // CLUBS ENDPOINTS
  // ==========================================

  /// Get clubs
  Future<List<Club>> getClubs({bool? activeOnly}) async {
    try {
      final response = await _dio.get(
        ApiConstants.clubs,
        queryParameters: {
          if (activeOnly != null) 'active_only': activeOnly,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['clubs'] ?? data;

      if (items is List) {
        return items.map((e) => Club.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Join club
  Future<void> joinClub(int clubId) async {
    try {
      await _dio.post(
        ApiConstants.clubJoin.replaceAll('{id}', clubId.toString()),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Leave club
  Future<void> leaveClub(int clubId) async {
    try {
      await _dio.post(
        ApiConstants.clubLeave.replaceAll('{id}', clubId.toString()),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // TOURNAMENTS ENDPOINTS
  // ==========================================

  /// Get tournaments
  Future<List<Tournament>> getTournaments({String? status}) async {
    try {
      final response = await _dio.get(
        ApiConstants.tournaments,
        queryParameters: {
          if (status != null) 'status': status,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['tournaments'] ?? data;

      if (items is List) {
        return items.map((e) => Tournament.fromJson(e)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Register for tournament
  Future<void> registerForTournament(int tournamentId) async {
    try {
      await _dio.post(
        ApiConstants.tournamentRegister.replaceAll('{id}', tournamentId.toString()),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // ERROR HANDLING
  // ==========================================

  String _handleError(DioException e) {
    if (e.response != null) {
      final data = e.response!.data;
      if (data is Map<String, dynamic>) {
        // Backend xato xabarlarini olish
        final detail = data['detail'];
        if (detail is String) return detail;
        if (detail is Map) return detail['message']?.toString() ?? 'Xatolik yuz berdi';
        return data['error'] as String? ??
               data['message'] as String? ??
               'Xatolik yuz berdi';
      }
    }

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Ulanish vaqti tugadi. Internetni tekshiring.';
      case DioExceptionType.connectionError:
        return 'Serverga ulanib bo\'lmadi.\nInternet ulanishini tekshiring.';
      case DioExceptionType.badResponse:
        switch (e.response?.statusCode) {
          case 400:
            return 'Noto\'g\'ri so\'rov';
          case 401:
            return 'Login yoki parol noto\'g\'ri';
          case 403:
            return 'Ruxsat yo\'q';
          case 404:
            return 'Ma\'lumot topilmadi';
          case 422:
            return 'Noto\'g\'ri ma\'lumot formati';
          case 500:
            return 'Server xatosi';
          default:
            return 'Xatolik: ${e.response?.statusCode}';
        }
      default:
        return 'Noma\'lum xatolik yuz berdi';
    }
  }

  // ==========================================
  // MOBILE STUDENT ENDPOINTS
  // ==========================================

  /// Get student profile
  Future<Map<String, dynamic>> getStudentProfile() async {
    try {
      final response = await _dio.get(ApiConstants.studentProfile);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get student dashboard
  Future<Map<String, dynamic>> getStudentDashboard() async {
    try {
      final response = await _dio.get(ApiConstants.studentDashboard);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get student attendance history
  Future<List<dynamic>> getStudentAttendance({int days = 30}) async {
    try {
      final response = await _dio.get(
        ApiConstants.studentAttendance,
        queryParameters: {'days': days},
      );
      return response.data is List ? response.data : [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get student schedule for today
  Future<List<dynamic>> getStudentScheduleToday() async {
    try {
      final response = await _dio.get(ApiConstants.studentScheduleToday);
      return response.data is List ? response.data : [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get student schedule for week
  Future<Map<String, dynamic>> getStudentScheduleWeek() async {
    try {
      final response = await _dio.get(ApiConstants.studentScheduleWeek);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get student notifications
  Future<List<dynamic>> getStudentNotifications({int page = 1, int pageSize = 20}) async {
    try {
      final response = await _dio.get(
        ApiConstants.studentNotifications,
        queryParameters: {'page': page, 'page_size': pageSize},
      );
      final data = response.data;
      return data is List ? data : (data['items'] ?? []);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark student notification as read
  Future<void> markStudentNotificationRead(int id) async {
    try {
      await _dio.post(
        ApiConstants.studentNotificationRead.replaceAll('{id}', id.toString()),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // MOBILE LEADER ENDPOINTS
  // ==========================================

  /// Get leader dashboard
  Future<Map<String, dynamic>> getLeaderDashboard() async {
    try {
      final response = await _dio.get(ApiConstants.leaderDashboard);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get leader's group students
  Future<List<dynamic>> getLeaderStudents() async {
    try {
      final response = await _dio.get(ApiConstants.leaderStudents);
      return response.data is List ? response.data : [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get today's attendance for leader
  Future<Map<String, dynamic>> getLeaderAttendanceToday() async {
    try {
      final response = await _dio.get(ApiConstants.leaderAttendanceToday);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Quick mark attendance for single student
  Future<void> quickMarkAttendance({
    required int studentId,
    required String status,
    String? note,
  }) async {
    try {
      await _dio.post(
        ApiConstants.leaderAttendanceQuick,
        data: {
          'student_id': studentId,
          'status': status,
          if (note != null) 'note': note,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Bulk mark attendance for multiple students
  Future<void> bulkMarkAttendance(List<Map<String, dynamic>> attendanceList) async {
    try {
      await _dio.post(
        ApiConstants.leaderAttendanceBulk,
        data: {'attendance': attendanceList},
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get leader's schedule for today
  Future<List<dynamic>> getLeaderScheduleToday() async {
    try {
      final response = await _dio.get(ApiConstants.leaderScheduleToday);
      return response.data is List ? response.data : [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get leader's weekly stats
  Future<Map<String, dynamic>> getLeaderStatsWeek() async {
    try {
      final response = await _dio.get(ApiConstants.leaderStatsWeek);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Send notification to group
  Future<void> sendGroupNotification({
    required String title,
    required String message,
  }) async {
    try {
      await _dio.post(
        ApiConstants.leaderSendNotification,
        data: {
          'title': title,
          'message': message,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // PUSH NOTIFICATION ENDPOINTS
  // ==========================================

  /// Register device for push notifications
  Future<void> registerPushToken(String token, String deviceType) async {
    try {
      await _dio.post(
        ApiConstants.pushRegister,
        data: {
          'token': token,
          'device_type': deviceType,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
}

// Global instance
final apiService = ApiService();

