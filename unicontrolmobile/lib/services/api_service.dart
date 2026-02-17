/// API Service
/// Backend Mobile API bilan aloqa qilish uchun yagona servis
/// Barcha endpointlar /api/mobile orqali ishlaydi
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

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
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

        if (error.response?.statusCode == 401 && !_isRefreshing) {
          try {
            final refreshed = await refreshTokens();
            if (refreshed) {
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

    _loadTokens();
  }

  // ==========================================
  // TOKEN MANAGEMENT
  // ==========================================

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
  Future<User> login(String username, String password) async {
    try {
      final response = await _dio.post(
        ApiConstants.login,
        data: {
          'username': username,
          'password': password,
          'device_token': null,
          'device_type': 'android',
        },
      );

      final data = response.data;
      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String? ?? '';

      await _saveTokens(accessToken, refreshToken);
      await _storage.write(key: StorageKeys.isLoggedIn, value: 'true');

      final userData = data['user'] as Map<String, dynamic>;
      return User.fromJson(userData);
    } on DioException catch (e) {
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
  // DASHBOARD ENDPOINTS
  // ==========================================

  /// Get unified dashboard stats (role-based)
  Future<DashboardStats> getDashboardStats() async {
    try {
      final response = await _dio.get(ApiConstants.dashboardStats);
      return DashboardStats.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // STUDENT MOBILE ENDPOINTS
  // ==========================================

  /// Get student profile
  Future<Map<String, dynamic>> getStudentProfile() async {
    try {
      final response = await _dio.get(ApiConstants.studentProfile);
      return response.data;
    } on DioException catch (e) {
      _logger.e('getStudentProfile error: ${e.response?.statusCode}');
      return {'error': _handleError(e)};
    }
  }

  /// Get student dashboard
  Future<Map<String, dynamic>> getStudentDashboard() async {
    try {
      final response = await _dio.get(ApiConstants.studentDashboard);
      return response.data;
    } on DioException catch (e) {
      _logger.e('getStudentDashboard error: ${e.response?.statusCode}');
      return {
        'student_name': 'Foydalanuvchi',
        'today_status': 'not_marked',
        'attendance_rate': 0.0,
        'today_classes': 0,
        'unread_notifications': 0,
      };
    }
  }

  /// Get student attendance history
  Future<List<dynamic>> getStudentAttendance({int days = 30}) async {
    try {
      final response = await _dio.get(
        ApiConstants.studentAttendance,
        queryParameters: {'days': days},
      );
      return response.data is List ? response.data : (response.data['records'] ?? []);
    } on DioException catch (e) {
      _logger.e('getStudentAttendance error: ${e.response?.statusCode}');
      return [];
    }
  }

  /// Get student schedule for today
  Future<List<dynamic>> getStudentScheduleToday() async {
    try {
      final response = await _dio.get(ApiConstants.studentScheduleToday);
      final data = response.data;
      return data is List ? data : (data['classes'] ?? data['items'] ?? []);
    } on DioException catch (e) {
      _logger.e('getStudentScheduleToday error: ${e.response?.statusCode}');
      return [];
    }
  }

  /// Get student schedule for week
  Future<Map<String, dynamic>> getStudentScheduleWeek() async {
    try {
      final response = await _dio.get(ApiConstants.studentScheduleWeek);
      return response.data is Map<String, dynamic> ? response.data : {};
    } on DioException catch (e) {
      _logger.e('getStudentScheduleWeek error: ${e.response?.statusCode}');
      return {};
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
      return data is List ? data : (data['notifications'] ?? data['items'] ?? []);
    } on DioException catch (e) {
      _logger.e('getStudentNotifications error: ${e.response?.statusCode}');
      return [];
    }
  }

  /// Mark student notification as read
  Future<void> markStudentNotificationRead(int id) async {
    try {
      await _dio.post(
        ApiConstants.studentNotificationRead.replaceAll('{id}', id.toString()),
      );
    } on DioException catch (e) {
      _logger.e('markStudentNotificationRead error: ${e.response?.statusCode}');
    }
  }

  // ==========================================
  // LEADER MOBILE ENDPOINTS
  // ==========================================

  /// Get leader dashboard
  Future<Map<String, dynamic>> getLeaderDashboard() async {
    try {
      final response = await _dio.get(ApiConstants.leaderDashboard);
      return response.data;
    } on DioException catch (e) {
      _logger.e('getLeaderDashboard error: ${e.response?.statusCode}');
      return {
        'group': {'id': 0, 'name': 'Guruh', 'code': ''},
        'students_count': 0,
        'today_attendance': {'marked': 0, 'not_marked': 0, 'present': 0, 'absent': 0},
        'today_classes': 0,
      };
    }
  }

  /// Get leader's group students
  Future<List<dynamic>> getLeaderStudents() async {
    try {
      final response = await _dio.get(ApiConstants.leaderStudents);
      return response.data is List ? response.data : [];
    } on DioException catch (e) {
      _logger.e('getLeaderStudents error: ${e.response?.statusCode}');
      return [];
    }
  }

  /// Get today's attendance for leader
  Future<Map<String, dynamic>> getLeaderAttendanceToday() async {
    try {
      final response = await _dio.get(ApiConstants.leaderAttendanceToday);
      return response.data;
    } on DioException catch (e) {
      _logger.e('getLeaderAttendanceToday error: ${e.response?.statusCode}');
      return {'date': '', 'students': []};
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
      final data = response.data;
      return data is List ? data : (data['classes'] ?? data['items'] ?? []);
    } on DioException catch (e) {
      _logger.e('getLeaderScheduleToday error: ${e.response?.statusCode}');
      return [];
    }
  }

  /// Get leader's weekly stats
  Future<Map<String, dynamic>> getLeaderStatsWeek() async {
    try {
      final response = await _dio.get(ApiConstants.leaderStatsWeek);
      return response.data;
    } on DioException catch (e) {
      _logger.e('getLeaderStatsWeek error: ${e.response?.statusCode}');
      return {};
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
  // STUDENTS ENDPOINTS (GENERAL)
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
        return items.map((e) => Student.fromJson(e as Map<String, dynamic>)).toList();
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
        return items.map((e) => Group.fromJson(e as Map<String, dynamic>)).toList();
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
        return items.map((e) => Student.fromJson(e as Map<String, dynamic>)).toList();
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
    String? dateFrom,
    String? dateTo,
    String? status,
    int days = 30,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.attendance,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
          if (studentId != null) 'student_id': studentId,
          if (dateFrom != null) 'date_from': dateFrom,
          if (dateTo != null) 'date_to': dateTo,
          if (status != null) 'status': status,
          'days': days,
          'page': page,
          'page_size': pageSize,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['records'] ?? data;

      if (items is List) {
        return items.map((e) => Attendance.fromJson(e as Map<String, dynamic>)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark attendance (batch)
  Future<Map<String, dynamic>> markAttendance(List<Map<String, dynamic>> records) async {
    try {
      final response = await _dio.post(
        ApiConstants.attendanceBatch,
        data: records,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get attendance statistics
  Future<AttendanceStats> getAttendanceStats({
    int? groupId,
    int? studentId,
    int days = 30,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.attendanceStats,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
          if (studentId != null) 'student_id': studentId,
          'days': days,
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
  Future<List<Schedule>> getSchedule({int? groupId, String? day}) async {
    try {
      final response = await _dio.get(
        ApiConstants.schedule,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
          if (day != null) 'day': day,
        },
      );

      final data = response.data;
      
      // Format 1: {"schedule": [...]} (when group_id provided)
      final items = data['schedule'] ?? data['items'];
      if (items is List) {
        return items.map((e) => Schedule.fromJson(e as Map<String, dynamic>)).toList();
      }
      
      // Format 2: {"MONDAY": [...], "TUESDAY": [...], ...} (week dict without group_id)
      if (data is Map<String, dynamic>) {
        final allSchedules = <Schedule>[];
        final dayNames = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        for (final entry in data.entries) {
          if (entry.value is List && dayNames.contains(entry.key.toLowerCase())) {
            for (final item in entry.value) {
              if (item is Map<String, dynamic>) {
                // Inject day_of_week if not present
                final enriched = Map<String, dynamic>.from(item);
                enriched['day_of_week'] ??= entry.key;
                enriched['day'] ??= entry.key;
                allSchedules.add(Schedule.fromJson(enriched));
              }
            }
          }
        }
        if (allSchedules.isNotEmpty) return allSchedules;
      }
      
      // Format 3: raw list
      if (data is List) {
        return data.map((e) => Schedule.fromJson(e as Map<String, dynamic>)).toList();
      }
      
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get today's schedule
  Future<Map<String, dynamic>> getTodaySchedule() async {
    try {
      final response = await _dio.get(ApiConstants.scheduleToday);
      return response.data is Map<String, dynamic> ? response.data : {};
    } on DioException catch (e) {
      _logger.e('getTodaySchedule error: ${e.response?.statusCode}');
      return {};
    }
  }

  /// Get week schedule
  Future<Map<String, dynamic>> getWeekSchedule({int? groupId}) async {
    try {
      final response = await _dio.get(
        ApiConstants.scheduleWeek,
        queryParameters: {
          if (groupId != null) 'group_id': groupId,
        },
      );
      return response.data is Map<String, dynamic> ? response.data : {};
    } on DioException catch (e) {
      _logger.e('getWeekSchedule error: ${e.response?.statusCode}');
      return {};
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
        return items.map((e) => AppNotification.fromJson(e as Map<String, dynamic>)).toList();
      }
      return [];
    } on DioException catch (e) {
      _logger.e('getNotifications error: ${e.response?.statusCode}');
      return [];
    }
  }

  /// Get unread count
  Future<int> getUnreadNotificationCount() async {
    try {
      final response = await _dio.get(ApiConstants.notificationUnreadCount);
      final data = response.data;
      return data['count'] as int? ?? data['unread_count'] as int? ?? 0;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return 0;
      _logger.e('getUnreadNotificationCount error: ${e.response?.statusCode}');
      return 0;
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
  // REPORTS ENDPOINTS
  // ==========================================

  /// Get reports
  Future<List<Report>> getReports({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) async {
    try {
      final response = await _dio.get(
        ApiConstants.reports,
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (status != null) 'status': status,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['reports'] ?? data;

      if (items is List) {
        return items.map((e) => Report.fromJson(e as Map<String, dynamic>)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Submit report
  Future<Report> submitReport(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post(ApiConstants.reports, data: data);
      return Report.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get report detail
  Future<Report> getReport(int id) async {
    try {
      final response = await _dio.get(
        ApiConstants.reportById.replaceAll('{id}', id.toString()),
      );
      return Report.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ==========================================
  // CLUBS ENDPOINTS
  // ==========================================

  /// Get clubs
  Future<List<Club>> getClubs({bool? activeOnly, String? search}) async {
    try {
      final response = await _dio.get(
        ApiConstants.clubs,
        queryParameters: {
          if (activeOnly != null) 'active_only': activeOnly,
          if (search != null && search.isNotEmpty) 'search': search,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['clubs'] ?? data;

      if (items is List) {
        return items.map((e) => Club.fromJson(e as Map<String, dynamic>)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get club detail
  Future<Club> getClub(int id) async {
    try {
      final response = await _dio.get(
        ApiConstants.clubById.replaceAll('{id}', id.toString()),
      );
      return Club.fromJson(response.data);
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
      await _dio.delete(
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
  Future<List<Tournament>> getTournaments({String? status, String? search}) async {
    try {
      final response = await _dio.get(
        ApiConstants.tournaments,
        queryParameters: {
          if (status != null) 'status': status,
          if (search != null && search.isNotEmpty) 'search': search,
        },
      );

      final data = response.data;
      final items = data['items'] ?? data['tournaments'] ?? data;

      if (items is List) {
        return items.map((e) => Tournament.fromJson(e as Map<String, dynamic>)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get tournament detail
  Future<Tournament> getTournament(int id) async {
    try {
      final response = await _dio.get(
        ApiConstants.tournamentById.replaceAll('{id}', id.toString()),
      );
      return Tournament.fromJson(response.data);
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

  /// Unregister from tournament
  Future<void> unregisterFromTournament(int tournamentId) async {
    try {
      await _dio.delete(
        ApiConstants.tournamentUnregister.replaceAll('{id}', tournamentId.toString()),
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

  // ==========================================
  // LIBRARY ENDPOINTS
  // ==========================================

  /// Get books list
  Future<Map<String, dynamic>> getBooks({String? search, String? category, int page = 1}) async {
    final params = <String, dynamic>{'page': page, 'page_size': 20};
    if (search != null && search.isNotEmpty) params['search'] = search;
    if (category != null) params['category'] = category;
    final response = await _dio.get(ApiConstants.library, queryParameters: params);
    return response.data;
  }

  /// Get book categories
  Future<List<dynamic>> getBookCategories() async {
    final response = await _dio.get(ApiConstants.libraryCategories);
    return response.data;
  }

  /// Get book detail
  Future<Map<String, dynamic>> getBookDetail(int id) async {
    final response = await _dio.get(ApiConstants.libraryDetail(id));
    return response.data;
  }

  /// Get my borrows
  Future<Map<String, dynamic>> getMyBorrows({String? status, int page = 1}) async {
    final params = <String, dynamic>{'page': page};
    if (status != null) params['status'] = status;
    final response = await _dio.get(ApiConstants.libraryMyBorrows, queryParameters: params);
    return response.data;
  }

  /// Get library stats
  Future<Map<String, dynamic>> getLibraryStats() async {
    final response = await _dio.get(ApiConstants.libraryStats);
    return response.data;
  }

  /// Borrow a book
  Future<Map<String, dynamic>> borrowBook(int bookId) async {
    final response = await _dio.post(ApiConstants.libraryBorrow(bookId));
    return response.data;
  }

  // ==========================================
  // CANTEEN ENDPOINTS
  // ==========================================

  /// Get canteen categories
  Future<List<dynamic>> getCanteenCategories() async {
    final response = await _dio.get(ApiConstants.canteenCategories);
    return response.data;
  }

  /// Get canteen menu
  Future<Map<String, dynamic>> getCanteenMenu({int? categoryId, String? search}) async {
    final params = <String, dynamic>{};
    if (categoryId != null) params['category_id'] = categoryId;
    if (search != null && search.isNotEmpty) params['search'] = search;
    final response = await _dio.get(ApiConstants.canteenMenu, queryParameters: params);
    return response.data;
  }

  /// Create canteen order
  Future<Map<String, dynamic>> createOrder(List<Map<String, dynamic>> items, {String? notes}) async {
    final response = await _dio.post(ApiConstants.canteenOrders, data: {
      'items': items,
      if (notes != null) 'notes': notes,
    });
    return response.data;
  }

  /// Get my orders
  Future<Map<String, dynamic>> getMyOrders({String? status, int page = 1}) async {
    final params = <String, dynamic>{'page': page};
    if (status != null) params['status'] = status;
    final response = await _dio.get(ApiConstants.canteenOrders, queryParameters: params);
    return response.data;
  }

  // ==========================================
  // CONTRACTS ENDPOINTS
  // ==========================================

  /// Get my contract
  Future<Map<String, dynamic>> getMyContract() async {
    final response = await _dio.get(ApiConstants.contractsMy);
    return response.data;
  }

  /// Get group contracts
  Future<Map<String, dynamic>> getGroupContracts({int page = 1}) async {
    final response = await _dio.get(ApiConstants.contractsGroup, queryParameters: {'page': page});
    return response.data;
  }

  // ==========================================
  // HELP ENDPOINTS
  // ==========================================

  /// Get FAQ
  Future<Map<String, dynamic>> getFAQ({String? category, String? search}) async {
    final params = <String, dynamic>{};
    if (category != null) params['category'] = category;
    if (search != null && search.isNotEmpty) params['search'] = search;
    final response = await _dio.get(ApiConstants.help, queryParameters: params);
    return response.data;
  }

  // ==========================================
  // ERROR HANDLING
  // ==========================================

  String _handleError(DioException e) {
    if (e.response != null) {
      final data = e.response!.data;
      if (data is Map<String, dynamic>) {
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
}

// Global instance
final apiService = ApiService();

