/// Club Model
/// To'garak modeli
library;

import 'package:equatable/equatable.dart';

class Club extends Equatable {
  final int id;
  final String name;
  final String? description;
  final String? category;
  final String? imageUrl;
  final int? leaderId;
  final String? leaderName;
  final int memberCount;
  final int maxMembers;
  final String? schedule;
  final String? location;
  final bool isActive;
  final bool isJoined;
  final DateTime? createdAt;

  const Club({
    required this.id,
    required this.name,
    this.description,
    this.category,
    this.imageUrl,
    this.leaderId,
    this.leaderName,
    this.memberCount = 0,
    this.maxMembers = 0,
    this.schedule,
    this.location,
    this.isActive = true,
    this.isJoined = false,
    this.createdAt,
  });

  /// To'liq joy bormi
  bool get hasSpace => maxMembers == 0 || memberCount < maxMembers;

  /// To'liqlik foizi
  double get fillRate {
    if (maxMembers == 0) return 0;
    return (memberCount / maxMembers) * 100;
  }

  factory Club.fromJson(Map<String, dynamic> json) {
    return Club(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      category: json['category'] as String?,
      imageUrl: json['image_url'] as String? ?? json['image'] as String?,
      leaderId: json['leader_id'] as int?,
      leaderName: json['leader_name'] as String?,
      memberCount: json['member_count'] as int? ?? json['members_count'] as int? ?? 0,
      maxMembers: json['max_members'] as int? ?? 0,
      schedule: json['schedule'] as String?,
      location: json['location'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      isJoined: json['is_joined'] as bool? ?? false,
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
      'category': category,
      'image_url': imageUrl,
      'leader_id': leaderId,
      'leader_name': leaderName,
      'member_count': memberCount,
      'max_members': maxMembers,
      'schedule': schedule,
      'location': location,
      'is_active': isActive,
      'is_joined': isJoined,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  Club copyWith({
    int? id,
    String? name,
    String? description,
    String? category,
    String? imageUrl,
    int? leaderId,
    String? leaderName,
    int? memberCount,
    int? maxMembers,
    String? schedule,
    String? location,
    bool? isActive,
    bool? isJoined,
    DateTime? createdAt,
  }) {
    return Club(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      category: category ?? this.category,
      imageUrl: imageUrl ?? this.imageUrl,
      leaderId: leaderId ?? this.leaderId,
      leaderName: leaderName ?? this.leaderName,
      memberCount: memberCount ?? this.memberCount,
      maxMembers: maxMembers ?? this.maxMembers,
      schedule: schedule ?? this.schedule,
      location: location ?? this.location,
      isActive: isActive ?? this.isActive,
      isJoined: isJoined ?? this.isJoined,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        category,
        imageUrl,
        leaderId,
        leaderName,
        memberCount,
        maxMembers,
        schedule,
        location,
        isActive,
        isJoined,
        createdAt,
      ];
}

