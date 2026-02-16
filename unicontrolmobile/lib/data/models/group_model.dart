/// Group Model
/// Guruh ma'lumotlari modeli
library;

import 'package:equatable/equatable.dart';

class Group extends Equatable {
  final int id;
  final String name;
  final String? directionId;
  final String? directionName;
  final int? course;
  final int? leaderId;
  final String? leaderName;
  final int studentCount;
  final bool isActive;
  final bool isBlocked;
  final String? blockReason;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const Group({
    required this.id,
    required this.name,
    this.directionId,
    this.directionName,
    this.course,
    this.leaderId,
    this.leaderName,
    this.studentCount = 0,
    this.isActive = true,
    this.isBlocked = false,
    this.blockReason,
    this.createdAt,
    this.updatedAt,
  });

  /// Guruh to'liq nomi (kurs bilan)
  String get displayName {
    if (course != null) {
      return '$name ($course-kurs)';
    }
    return name;
  }

  /// Sardor tayinlanganmi
  bool get hasLeader => leaderId != null;

  factory Group.fromJson(Map<String, dynamic> json) {
    return Group(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      directionId: json['direction_id']?.toString(),
      directionName: json['direction_name'] as String? ?? json['direction'] as String?,
      course: json['course'] as int?,
      leaderId: json['leader_id'] as int?,
      leaderName: json['leader_name'] as String? ?? json['leader'] as String?,
      studentCount: json['student_count'] as int? ?? json['students_count'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      isBlocked: json['is_blocked'] as bool? ?? false,
      blockReason: json['block_reason'] as String?,
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
      'name': name,
      'direction_id': directionId,
      'direction_name': directionName,
      'course': course,
      'leader_id': leaderId,
      'leader_name': leaderName,
      'student_count': studentCount,
      'is_active': isActive,
      'is_blocked': isBlocked,
      'block_reason': blockReason,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  Group copyWith({
    int? id,
    String? name,
    String? directionId,
    String? directionName,
    int? course,
    int? leaderId,
    String? leaderName,
    int? studentCount,
    bool? isActive,
    bool? isBlocked,
    String? blockReason,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Group(
      id: id ?? this.id,
      name: name ?? this.name,
      directionId: directionId ?? this.directionId,
      directionName: directionName ?? this.directionName,
      course: course ?? this.course,
      leaderId: leaderId ?? this.leaderId,
      leaderName: leaderName ?? this.leaderName,
      studentCount: studentCount ?? this.studentCount,
      isActive: isActive ?? this.isActive,
      isBlocked: isBlocked ?? this.isBlocked,
      blockReason: blockReason ?? this.blockReason,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        name,
        directionId,
        directionName,
        course,
        leaderId,
        leaderName,
        studentCount,
        isActive,
        isBlocked,
        blockReason,
        createdAt,
        updatedAt,
      ];
}

