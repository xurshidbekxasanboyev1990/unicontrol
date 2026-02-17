/// Tournament Model
/// Turnir modeli
library;

import 'package:equatable/equatable.dart';

class Tournament extends Equatable {
  final int id;
  final String name;
  final String? description;
  final int? subjectId;
  final String? subjectName;
  final DateTime? startDate;
  final DateTime? endDate;
  final DateTime? registrationDeadline;
  final int participantCount;
  final int maxParticipants;
  final String? prize;
  final String? rules;
  final String? imageUrl;
  final String status; // upcoming, ongoing, completed, cancelled
  final bool isRegistered;
  final bool isActive;
  final DateTime? createdAt;

  const Tournament({
    required this.id,
    required this.name,
    this.description,
    this.subjectId,
    this.subjectName,
    this.startDate,
    this.endDate,
    this.registrationDeadline,
    this.participantCount = 0,
    this.maxParticipants = 0,
    this.prize,
    this.rules,
    this.imageUrl,
    this.status = 'upcoming',
    this.isRegistered = false,
    this.isActive = true,
    this.createdAt,
  });

  /// Ro'yxatdan o'tish mumkinmi
  bool get canRegister {
    if (!isActive || isRegistered) return false;
    if (maxParticipants > 0 && participantCount >= maxParticipants) return false;
    if (registrationDeadline != null && DateTime.now().isAfter(registrationDeadline!)) return false;
    return status == 'upcoming' || status == 'ongoing';
  }

  /// Status label
  String get statusLabel {
    switch (status.toLowerCase()) {
      case 'upcoming':
        return 'Kutilmoqda';
      case 'ongoing':
        return 'Davom etmoqda';
      case 'completed':
        return 'Tugallangan';
      case 'cancelled':
        return 'Bekor qilingan';
      default:
        return status;
    }
  }

  /// Status color
  String get statusColor {
    switch (status.toLowerCase()) {
      case 'upcoming':
        return 'blue';
      case 'ongoing':
        return 'green';
      case 'completed':
        return 'gray';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  }

  factory Tournament.fromJson(Map<String, dynamic> json) {
    return Tournament(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      subjectId: json['subject_id'] as int?,
      subjectName: json['subject_name'] as String?,
      startDate: json['start_date'] != null
          ? DateTime.tryParse(json['start_date'] as String)
          : null,
      endDate: json['end_date'] != null
          ? DateTime.tryParse(json['end_date'] as String)
          : null,
      registrationDeadline: json['registration_deadline'] != null
          ? DateTime.tryParse(json['registration_deadline'] as String)
          : null,
      participantCount: json['participant_count'] as int? ?? 0,
      maxParticipants: json['max_participants'] as int? ?? 0,
      prize: json['prize'] as String?,
      rules: json['rules'] as String?,
      imageUrl: json['image_url'] as String?,
      status: json['status'] as String? ?? 'upcoming',
      isRegistered: json['is_registered'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'subject_id': subjectId,
      'subject_name': subjectName,
      'start_date': startDate?.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'registration_deadline': registrationDeadline?.toIso8601String(),
      'participant_count': participantCount,
      'max_participants': maxParticipants,
      'prize': prize,
      'rules': rules,
      'image_url': imageUrl,
      'status': status,
      'is_registered': isRegistered,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        subjectId,
        subjectName,
        startDate,
        endDate,
        registrationDeadline,
        participantCount,
        maxParticipants,
        prize,
        rules,
        imageUrl,
        status,
        isRegistered,
        isActive,
        createdAt,
      ];
}

