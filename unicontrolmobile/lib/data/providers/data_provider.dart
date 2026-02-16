/// Data Provider
/// Asosiy ma'lumotlar providerlari
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/models.dart';
import '../../services/api_service.dart';

// ==========================================
// STUDENTS PROVIDERS
// ==========================================

/// Students state
class StudentsState {
  final List<Student> students;
  final bool isLoading;
  final String? error;
  final int page;
  final int totalPages;
  final bool hasMore;

  const StudentsState({
    this.students = const [],
    this.isLoading = false,
    this.error,
    this.page = 1,
    this.totalPages = 1,
    this.hasMore = false,
  });

  StudentsState copyWith({
    List<Student>? students,
    bool? isLoading,
    String? error,
    int? page,
    int? totalPages,
    bool? hasMore,
  }) {
    return StudentsState(
      students: students ?? this.students,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      page: page ?? this.page,
      totalPages: totalPages ?? this.totalPages,
      hasMore: hasMore ?? this.hasMore,
    );
  }
}

/// Students notifier
class StudentsNotifier extends StateNotifier<StudentsState> {
  StudentsNotifier() : super(const StudentsState());

  Future<void> fetchStudents({
    String? search,
    int? groupId,
    bool refresh = false,
  }) async {
    if (state.isLoading && !refresh) return;

    final page = refresh ? 1 : state.page;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final students = await apiService.getStudents(
        page: page,
        search: search,
        groupId: groupId,
      );

      state = state.copyWith(
        students: refresh ? students : [...state.students, ...students],
        isLoading: false,
        page: page + 1,
        hasMore: students.length >= 20,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const StudentsState();
  }
}

final studentsProvider =
    StateNotifierProvider<StudentsNotifier, StudentsState>((ref) {
  return StudentsNotifier();
});

// ==========================================
// GROUPS PROVIDERS
// ==========================================

/// Groups state
class GroupsState {
  final List<Group> groups;
  final bool isLoading;
  final String? error;

  const GroupsState({
    this.groups = const [],
    this.isLoading = false,
    this.error,
  });

  GroupsState copyWith({
    List<Group>? groups,
    bool? isLoading,
    String? error,
  }) {
    return GroupsState(
      groups: groups ?? this.groups,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Groups notifier
class GroupsNotifier extends StateNotifier<GroupsState> {
  GroupsNotifier() : super(const GroupsState());

  Future<void> fetchGroups({String? search, bool? activeOnly}) async {
    if (state.isLoading) return;

    state = state.copyWith(isLoading: true, error: null);

    try {
      final groups = await apiService.getGroups(
        search: search,
        activeOnly: activeOnly,
      );
      state = state.copyWith(groups: groups, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final groupsProvider =
    StateNotifierProvider<GroupsNotifier, GroupsState>((ref) {
  return GroupsNotifier();
});

// ==========================================
// ATTENDANCE PROVIDERS
// ==========================================

/// Attendance state
class AttendanceState {
  final List<Attendance> records;
  final bool isLoading;
  final String? error;

  const AttendanceState({
    this.records = const [],
    this.isLoading = false,
    this.error,
  });

  AttendanceState copyWith({
    List<Attendance>? records,
    bool? isLoading,
    String? error,
  }) {
    return AttendanceState(
      records: records ?? this.records,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Attendance notifier
class AttendanceNotifier extends StateNotifier<AttendanceState> {
  AttendanceNotifier() : super(const AttendanceState());

  Future<void> fetchAttendance({
    int? groupId,
    int? studentId,
    String? dateFrom,
    String? dateTo,
    String? status,
    int days = 30,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final records = await apiService.getAttendance(
        groupId: groupId,
        studentId: studentId,
        dateFrom: dateFrom,
        dateTo: dateTo,
        status: status,
        days: days,
      );
      state = state.copyWith(records: records, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> markAttendance(List<Map<String, dynamic>> records) async {
    try {
      final result = await apiService.markAttendance(records);
      return (result['marked'] ?? 0) > 0;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }
}

final attendanceProvider =
    StateNotifierProvider<AttendanceNotifier, AttendanceState>((ref) {
  return AttendanceNotifier();
});

/// Attendance stats provider
final attendanceStatsProvider = FutureProvider.family<AttendanceStats, Map<String, dynamic>>(
  (ref, params) async {
    return apiService.getAttendanceStats(
      groupId: params['group_id'] as int?,
      studentId: params['student_id'] as int?,
      days: params['days'] as int? ?? 30,
    );
  },
);

// ==========================================
// SCHEDULE PROVIDERS
// ==========================================

/// Schedule provider
final scheduleProvider = FutureProvider.family<List<Schedule>, int?>(
  (ref, groupId) async {
    return apiService.getSchedule(groupId: groupId);
  },
);

/// Week schedule provider
final weekScheduleProvider = FutureProvider.family<Map<String, dynamic>, int?>(
  (ref, groupId) async {
    return apiService.getWeekSchedule(groupId: groupId);
  },
);

/// Today's schedule provider (returns raw map with date, day, classes)
final todayScheduleProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return apiService.getTodaySchedule();
});

// ==========================================
// NOTIFICATIONS PROVIDERS
// ==========================================

/// Notifications state
class NotificationsState {
  final List<AppNotification> notifications;
  final bool isLoading;
  final String? error;
  final int unreadCount;

  const NotificationsState({
    this.notifications = const [],
    this.isLoading = false,
    this.error,
    this.unreadCount = 0,
  });

  NotificationsState copyWith({
    List<AppNotification>? notifications,
    bool? isLoading,
    String? error,
    int? unreadCount,
  }) {
    return NotificationsState(
      notifications: notifications ?? this.notifications,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      unreadCount: unreadCount ?? this.unreadCount,
    );
  }
}

/// Notifications notifier
class NotificationsNotifier extends StateNotifier<NotificationsState> {
  NotificationsNotifier() : super(const NotificationsState());

  Future<void> fetchNotifications({bool? unreadOnly}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final notifications = await apiService.getNotifications(
        unreadOnly: unreadOnly,
      );
      final unreadCount = await apiService.getUnreadNotificationCount();

      state = state.copyWith(
        notifications: notifications,
        isLoading: false,
        unreadCount: unreadCount,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> markAsRead(int id) async {
    try {
      await apiService.markNotificationRead(id);

      final updated = state.notifications.map((n) {
        if (n.id == id) {
          return n.copyWith(isRead: true);
        }
        return n;
      }).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount: state.unreadCount > 0 ? state.unreadCount - 1 : 0,
      );
    } catch (e) {
      // Ignore
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await apiService.markAllNotificationsRead();

      final updated = state.notifications.map((n) {
        return n.copyWith(isRead: true);
      }).toList();

      state = state.copyWith(notifications: updated, unreadCount: 0);
    } catch (e) {
      // Ignore
    }
  }

  Future<void> refreshUnreadCount() async {
    try {
      final count = await apiService.getUnreadNotificationCount();
      state = state.copyWith(unreadCount: count);
    } catch (e) {
      // Ignore
    }
  }
}

final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, NotificationsState>((ref) {
  return NotificationsNotifier();
});

/// Unread count provider
final unreadNotificationCountProvider = Provider<int>((ref) {
  return ref.watch(notificationsProvider).unreadCount;
});

// ==========================================
// MOBILE DASHBOARD PROVIDERS
// ==========================================

/// Student mobile dashboard provider
final studentMobileDashboardProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return apiService.getStudentDashboard();
});

/// Leader mobile dashboard provider
final leaderMobileDashboardProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return apiService.getLeaderDashboard();
});

/// Dashboard stats provider (fallback)
final dashboardStatsProvider = FutureProvider<DashboardStats>((ref) async {
  try {
    return await apiService.getDashboardStats();
  } catch (e) {
    // Return empty stats if API fails
    return const DashboardStats(
      totalStudents: 0,
      activeGroups: 0,
      todayAttendanceRate: 0,
      totalReports: 0,
    );
  }
});

// ==========================================
// REPORTS PROVIDERS
// ==========================================

/// Reports state
class ReportsState {
  final List<Report> reports;
  final bool isLoading;
  final String? error;

  const ReportsState({
    this.reports = const [],
    this.isLoading = false,
    this.error,
  });

  ReportsState copyWith({
    List<Report>? reports,
    bool? isLoading,
    String? error,
  }) {
    return ReportsState(
      reports: reports ?? this.reports,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Reports notifier
class ReportsNotifier extends StateNotifier<ReportsState> {
  ReportsNotifier() : super(const ReportsState());

  Future<void> fetchReports({
    String? status,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final reports = await apiService.getReports(
        status: status,
      );
      state = state.copyWith(reports: reports, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> submitReport(Map<String, dynamic> data) async {
    try {
      final report = await apiService.submitReport(data);
      state = state.copyWith(reports: [report, ...state.reports]);
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }
}

final reportsProvider =
    StateNotifierProvider<ReportsNotifier, ReportsState>((ref) {
  return ReportsNotifier();
});

// ==========================================
// CLUBS PROVIDERS
// ==========================================

/// Clubs provider
final clubsProvider = FutureProvider<List<Club>>((ref) async {
  return apiService.getClubs(activeOnly: true);
});

// ==========================================
// TOURNAMENTS PROVIDERS
// ==========================================

/// Tournaments provider
final tournamentsProvider = FutureProvider<List<Tournament>>((ref) async {
  return apiService.getTournaments();
});

