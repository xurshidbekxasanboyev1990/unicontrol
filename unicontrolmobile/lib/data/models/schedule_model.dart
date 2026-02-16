/// Schedule Model
/// Dars jadvali modeli
library;

import 'package:equatable/equatable.dart';
import '../../core/constants/app_constants.dart';

class Schedule extends Equatable {
  final int id;
  final int? groupId;
  final String? groupName;
  final int dayOfWeek;
  final String startTime;
  final String endTime;
  final String subject;
  final String? teacher;
  final String? room;
  final String? building;
  final String? type; // lecture, practice, lab
  final bool isActive;
  final DateTime? createdAt;

  const Schedule({
    required this.id,
    this.groupId,
    this.groupName,
    required this.dayOfWeek,
    required this.startTime,
    required this.endTime,
    required this.subject,
    this.teacher,
    this.room,
    this.building,
    this.type,
    this.isActive = true,
    this.createdAt,
  });

  /// Kun nomi
  String get dayName => DayOfWeek.fromInt(dayOfWeek).label;

  /// Qisqa kun nomi
  String get dayShortName => DayOfWeek.fromInt(dayOfWeek).shortLabel;

  /// Vaqt oralig'i
  String get timeRange => '$startTime - $endTime';

  /// Dars turi nomi
  String get typeLabel {
    switch (type?.toLowerCase()) {
      case 'lecture':
        return 'Ma\'ruza';
      case 'practice':
        return 'Amaliyot';
      case 'lab':
        return 'Laboratoriya';
      default:
        return 'Dars';
    }
  }

  /// Xona bilan bino
  String get location {
    if (room != null && building != null) {
      return '$building, $room-xona';
    } else if (room != null) {
      return '$room-xona';
    } else if (building != null) {
      return building!;
    }
    return '';
  }

  factory Schedule.fromJson(Map<String, dynamic> json) {
    // Handle day_of_week: can be int or string (e.g., "MONDAY")
    int parsedDayOfWeek = 1;
    final dayValue = json['day_of_week'] ?? json['day'];
    if (dayValue is int) {
      parsedDayOfWeek = dayValue;
    } else if (dayValue is String) {
      // Map string day names to int (1=Monday ... 7=Sunday)
      final dayMap = {
        'monday': 1, 'MONDAY': 1,
        'tuesday': 2, 'TUESDAY': 2,
        'wednesday': 3, 'WEDNESDAY': 3,
        'thursday': 4, 'THURSDAY': 4,
        'friday': 5, 'FRIDAY': 5,
        'saturday': 6, 'SATURDAY': 6,
        'sunday': 7, 'SUNDAY': 7,
      };
      parsedDayOfWeek = dayMap[dayValue] ?? int.tryParse(dayValue) ?? 1;
    }

    return Schedule(
      id: json['id'] as int,
      groupId: json['group_id'] as int?,
      groupName: json['group_name'] as String?,
      dayOfWeek: parsedDayOfWeek,
      startTime: json['start_time'] as String? ?? '',
      endTime: json['end_time'] as String? ?? '',
      subject: json['subject'] as String? ?? json['subject_name'] as String? ?? '',
      teacher: json['teacher'] as String? ?? json['teacher_name'] as String?,
      room: json['room'] as String?,
      building: json['building'] as String?,
      type: json['type'] as String?,
      isActive: json['is_active'] as bool? ?? json['is_cancelled'] != true,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'group_id': groupId,
      'group_name': groupName,
      'day_of_week': dayOfWeek,
      'start_time': startTime,
      'end_time': endTime,
      'subject': subject,
      'teacher': teacher,
      'room': room,
      'building': building,
      'type': type,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  Schedule copyWith({
    int? id,
    int? groupId,
    String? groupName,
    int? dayOfWeek,
    String? startTime,
    String? endTime,
    String? subject,
    String? teacher,
    String? room,
    String? building,
    String? type,
    bool? isActive,
    DateTime? createdAt,
  }) {
    return Schedule(
      id: id ?? this.id,
      groupId: groupId ?? this.groupId,
      groupName: groupName ?? this.groupName,
      dayOfWeek: dayOfWeek ?? this.dayOfWeek,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      subject: subject ?? this.subject,
      teacher: teacher ?? this.teacher,
      room: room ?? this.room,
      building: building ?? this.building,
      type: type ?? this.type,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        groupId,
        groupName,
        dayOfWeek,
        startTime,
        endTime,
        subject,
        teacher,
        room,
        building,
        type,
        isActive,
        createdAt,
      ];
}

