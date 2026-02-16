/// Attendance Model
/// Davomat ma'lumotlari modeli
library;

import 'package:equatable/equatable.dart';
import '../../core/constants/app_constants.dart';

class Attendance extends Equatable {
  final int id;
  final int studentId;
  final String? studentName;
  final int? groupId;
  final String? groupName;
  final DateTime date;
  final AttendanceStatus status;
  final String? reason;
  final String? notes;
  final int? markedBy;
  final String? markedByName;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const Attendance({
    required this.id,
    required this.studentId,
    this.studentName,
    this.groupId,
    this.groupName,
    required this.date,
    required this.status,
    this.reason,
    this.notes,
    this.markedBy,
    this.markedByName,
    this.createdAt,
    this.updatedAt,
  });

  /// Status emoji
  String get statusEmoji => status.emoji;

  /// Status label
  String get statusLabel => status.label;

  /// Keldi mi
  bool get isPresent => status == AttendanceStatus.present;

  /// Kelmadi mi
  bool get isAbsent => status == AttendanceStatus.absent;

  /// Kechikdi mi
  bool get isLate => status == AttendanceStatus.late;

  /// Sababli mi
  bool get isExcused => status == AttendanceStatus.excused;

  factory Attendance.fromJson(Map<String, dynamic> json) {
    return Attendance(
      id: json['id'] as int,
      studentId: json['student_id'] as int,
      studentName: json['student_name'] as String?,
      groupId: json['group_id'] as int?,
      groupName: json['group_name'] as String?,
      date: DateTime.parse(json['date'] as String),
      status: AttendanceStatus.fromString(json['status'] as String? ?? 'absent'),
      reason: json['reason'] as String?,
      notes: json['notes'] as String?,
      markedBy: json['marked_by'] as int?,
      markedByName: json['marked_by_name'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'student_id': studentId,
      'student_name': studentName,
      'group_id': groupId,
      'group_name': groupName,
      'date': date.toIso8601String().split('T')[0],
      'status': status.value,
      'reason': reason,
      'notes': notes,
      'marked_by': markedBy,
      'marked_by_name': markedByName,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  Attendance copyWith({
    int? id,
    int? studentId,
    String? studentName,
    int? groupId,
    String? groupName,
    DateTime? date,
    AttendanceStatus? status,
    String? reason,
    String? notes,
    int? markedBy,
    String? markedByName,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Attendance(
      id: id ?? this.id,
      studentId: studentId ?? this.studentId,
      studentName: studentName ?? this.studentName,
      groupId: groupId ?? this.groupId,
      groupName: groupName ?? this.groupName,
      date: date ?? this.date,
      status: status ?? this.status,
      reason: reason ?? this.reason,
      notes: notes ?? this.notes,
      markedBy: markedBy ?? this.markedBy,
      markedByName: markedByName ?? this.markedByName,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        studentId,
        studentName,
        groupId,
        groupName,
        date,
        status,
        reason,
        notes,
        markedBy,
        markedByName,
        createdAt,
        updatedAt,
      ];
}

/// Attendance statistics model
class AttendanceStats extends Equatable {
  final int totalDays;
  final int presentDays;
  final int absentDays;
  final int lateDays;
  final int excusedDays;
  final double attendanceRate;

  const AttendanceStats({
    this.totalDays = 0,
    this.presentDays = 0,
    this.absentDays = 0,
    this.lateDays = 0,
    this.excusedDays = 0,
    this.attendanceRate = 0,
  });

  factory AttendanceStats.fromJson(Map<String, dynamic> json) {
    return AttendanceStats(
      totalDays: json['total_days'] as int? ?? 0,
      presentDays: json['present_days'] as int? ?? json['present'] as int? ?? 0,
      absentDays: json['absent_days'] as int? ?? json['absent'] as int? ?? 0,
      lateDays: json['late_days'] as int? ?? json['late'] as int? ?? 0,
      excusedDays: json['excused_days'] as int? ?? json['excused'] as int? ?? 0,
      attendanceRate: (json['attendance_rate'] as num?)?.toDouble() ?? 0,
    );
  }

  @override
  List<Object?> get props => [
        totalDays,
        presentDays,
        absentDays,
        lateDays,
        excusedDays,
        attendanceRate,
      ];
}

