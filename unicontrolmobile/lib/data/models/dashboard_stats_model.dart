/// Dashboard Stats Model
/// Dashboard statistika modeli
library;

import 'package:equatable/equatable.dart';

class DashboardStats extends Equatable {
  // Umumiy statistika
  final int totalStudents;
  final int totalGroups;
  final int activeStudents;
  final int activeGroups;

  // Davomat statistikasi
  final int todayPresent;
  final int todayAbsent;
  final int todayLate;
  final int todayExcused;
  final double todayAttendanceRate;
  final double weekAttendanceRate;
  final double monthAttendanceRate;

  // Kontrakt statistikasi
  final double totalContractAmount;
  final double totalContractPaid;
  final double contractPaymentRate;
  final int studentsWithDebt;

  // Hisobot statistikasi
  final int pendingReports;
  final int approvedReports;
  final int rejectedReports;
  final int totalReports;

  // Bildirishnomalar
  final int unreadNotifications;
  final int totalNotifications;

  // Bugungi jadval
  final int todayLessons;
  final String? nextLesson;
  final String? nextLessonTime;

  // Turnirlar
  final int activeTournaments;
  final int upcomingTournaments;

  // To'garaklar
  final int activeClubs;
  final int joinedClubs;

  const DashboardStats({
    this.totalStudents = 0,
    this.totalGroups = 0,
    this.activeStudents = 0,
    this.activeGroups = 0,
    this.todayPresent = 0,
    this.todayAbsent = 0,
    this.todayLate = 0,
    this.todayExcused = 0,
    this.todayAttendanceRate = 0,
    this.weekAttendanceRate = 0,
    this.monthAttendanceRate = 0,
    this.totalContractAmount = 0,
    this.totalContractPaid = 0,
    this.contractPaymentRate = 0,
    this.studentsWithDebt = 0,
    this.pendingReports = 0,
    this.approvedReports = 0,
    this.rejectedReports = 0,
    this.totalReports = 0,
    this.unreadNotifications = 0,
    this.totalNotifications = 0,
    this.todayLessons = 0,
    this.nextLesson,
    this.nextLessonTime,
    this.activeTournaments = 0,
    this.upcomingTournaments = 0,
    this.activeClubs = 0,
    this.joinedClubs = 0,
  });

  /// Bugungi jami talabalar (davomat bo'yicha)
  int get todayTotal => todayPresent + todayAbsent + todayLate + todayExcused;

  /// Kontrakt qoldig'i
  double get contractRemaining => totalContractAmount - totalContractPaid;

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalStudents: json['total_students'] as int? ?? 0,
      totalGroups: json['total_groups'] as int? ?? 0,
      activeStudents: json['active_students'] as int? ?? 0,
      activeGroups: json['active_groups'] as int? ?? 0,
      todayPresent: json['today_present'] as int? ?? json['present'] as int? ?? 0,
      todayAbsent: json['today_absent'] as int? ?? json['absent'] as int? ?? 0,
      todayLate: json['today_late'] as int? ?? json['late'] as int? ?? 0,
      todayExcused: json['today_excused'] as int? ?? json['excused'] as int? ?? 0,
      todayAttendanceRate: (json['today_attendance_rate'] as num?)?.toDouble() ??
          (json['attendance_rate'] as num?)?.toDouble() ?? 0,
      weekAttendanceRate: (json['week_attendance_rate'] as num?)?.toDouble() ?? 0,
      monthAttendanceRate: (json['month_attendance_rate'] as num?)?.toDouble() ?? 0,
      totalContractAmount: (json['total_contract_amount'] as num?)?.toDouble() ?? 0,
      totalContractPaid: (json['total_contract_paid'] as num?)?.toDouble() ?? 0,
      contractPaymentRate: (json['contract_payment_rate'] as num?)?.toDouble() ?? 0,
      studentsWithDebt: json['students_with_debt'] as int? ?? 0,
      pendingReports: json['pending_reports'] as int? ?? 0,
      approvedReports: json['approved_reports'] as int? ?? 0,
      rejectedReports: json['rejected_reports'] as int? ?? 0,
      totalReports: json['total_reports'] as int? ?? 0,
      unreadNotifications: json['unread_notifications'] as int? ?? 0,
      totalNotifications: json['total_notifications'] as int? ?? 0,
      todayLessons: json['today_lessons'] as int? ?? 0,
      nextLesson: json['next_lesson'] as String?,
      nextLessonTime: json['next_lesson_time'] as String?,
      activeTournaments: json['active_tournaments'] as int? ?? 0,
      upcomingTournaments: json['upcoming_tournaments'] as int? ?? 0,
      activeClubs: json['active_clubs'] as int? ?? 0,
      joinedClubs: json['joined_clubs'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_students': totalStudents,
      'total_groups': totalGroups,
      'active_students': activeStudents,
      'active_groups': activeGroups,
      'today_present': todayPresent,
      'today_absent': todayAbsent,
      'today_late': todayLate,
      'today_excused': todayExcused,
      'today_attendance_rate': todayAttendanceRate,
      'week_attendance_rate': weekAttendanceRate,
      'month_attendance_rate': monthAttendanceRate,
      'total_contract_amount': totalContractAmount,
      'total_contract_paid': totalContractPaid,
      'contract_payment_rate': contractPaymentRate,
      'students_with_debt': studentsWithDebt,
      'pending_reports': pendingReports,
      'approved_reports': approvedReports,
      'rejected_reports': rejectedReports,
      'total_reports': totalReports,
      'unread_notifications': unreadNotifications,
      'total_notifications': totalNotifications,
      'today_lessons': todayLessons,
      'next_lesson': nextLesson,
      'next_lesson_time': nextLessonTime,
      'active_tournaments': activeTournaments,
      'upcoming_tournaments': upcomingTournaments,
      'active_clubs': activeClubs,
      'joined_clubs': joinedClubs,
    };
  }

  @override
  List<Object?> get props => [
        totalStudents,
        totalGroups,
        activeStudents,
        activeGroups,
        todayPresent,
        todayAbsent,
        todayLate,
        todayExcused,
        todayAttendanceRate,
        weekAttendanceRate,
        monthAttendanceRate,
        totalContractAmount,
        totalContractPaid,
        contractPaymentRate,
        studentsWithDebt,
        pendingReports,
        approvedReports,
        rejectedReports,
        totalReports,
        unreadNotifications,
        totalNotifications,
        todayLessons,
        nextLesson,
        nextLessonTime,
        activeTournaments,
        upcomingTournaments,
        activeClubs,
        joinedClubs,
      ];
}

