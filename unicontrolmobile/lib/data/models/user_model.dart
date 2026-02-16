/// User Model
/// Foydalanuvchi ma'lumotlari modeli
library;

import 'package:equatable/equatable.dart';
import '../../core/constants/app_constants.dart';

class User extends Equatable {
  final int id;
  final String login;
  final String? email;
  final String? name;
  final String? fullName;
  final String? phone;
  final String? avatar;
  final UserRole role;
  final int? studentId;
  final int? studentDbId;
  final int? groupId;
  final String? groupName;
  final String? managedGroup;
  final String? hemisId;
  final String? address;
  final bool isActive;
  final DateTime? createdAt;

  const User({
    required this.id,
    required this.login,
    this.email,
    this.name,
    this.fullName,
    this.phone,
    this.avatar,
    required this.role,
    this.studentId,
    this.studentDbId,
    this.groupId,
    this.groupName,
    this.managedGroup,
    this.hemisId,
    this.address,
    this.isActive = true,
    this.createdAt,
  });

  /// Foydalanuvchining to'liq ismi
  String get displayName => fullName ?? name ?? login;

  /// Foydalanuvchi initiallari
  String get initials {
    final displayText = displayName;
    if (displayText.isEmpty) return 'U';
    final words = displayText.trim().split(' ');
    if (words.length == 1) {
      return words[0][0].toUpperCase();
    }
    return '${words[0][0]}${words.last[0]}'.toUpperCase();
  }

  /// Rol nomi
  String get roleLabel => role.label;

  /// Student ekanligini tekshirish
  bool get isStudent => role == UserRole.student;

  /// Leader ekanligini tekshirish
  bool get isLeader => role == UserRole.leader;

  /// Admin ekanligini tekshirish
  bool get isAdmin => role == UserRole.admin;

  /// SuperAdmin ekanligini tekshirish
  bool get isSuperAdmin => role == UserRole.superadmin;

  /// Talabalarni boshqara oladimi
  bool get canManageStudents =>
      role == UserRole.leader ||
      role == UserRole.admin ||
      role == UserRole.superadmin;

  /// Guruhlarni boshqara oladimi
  bool get canManageGroups =>
      role == UserRole.admin || role == UserRole.superadmin;

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      login: json['login'] as String? ?? json['username'] as String? ?? '',
      email: json['email'] as String?,
      name: json['name'] as String?,
      fullName: json['full_name'] as String?,
      phone: json['phone'] as String?,
      avatar: json['avatar'] as String?,
      role: UserRole.fromString(json['role'] as String? ?? 'student'),
      studentId: json['student_id'] as int?,
      studentDbId: json['student_db_id'] as int?,
      groupId: json['group_id'] as int?,
      groupName: json['group_name'] as String? ?? json['group'] as String?,
      managedGroup: json['managed_group'] as String?,
      hemisId: json['hemis_id'] as String?,
      address: json['address'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'login': login,
      'email': email,
      'name': name,
      'full_name': fullName,
      'phone': phone,
      'avatar': avatar,
      'role': role.value,
      'student_id': studentId,
      'student_db_id': studentDbId,
      'group_id': groupId,
      'group_name': groupName,
      'managed_group': managedGroup,
      'hemis_id': hemisId,
      'address': address,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  User copyWith({
    int? id,
    String? login,
    String? email,
    String? name,
    String? fullName,
    String? phone,
    String? avatar,
    UserRole? role,
    int? studentId,
    int? studentDbId,
    int? groupId,
    String? groupName,
    String? managedGroup,
    String? hemisId,
    String? address,
    bool? isActive,
    DateTime? createdAt,
  }) {
    return User(
      id: id ?? this.id,
      login: login ?? this.login,
      email: email ?? this.email,
      name: name ?? this.name,
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      avatar: avatar ?? this.avatar,
      role: role ?? this.role,
      studentId: studentId ?? this.studentId,
      studentDbId: studentDbId ?? this.studentDbId,
      groupId: groupId ?? this.groupId,
      groupName: groupName ?? this.groupName,
      managedGroup: managedGroup ?? this.managedGroup,
      hemisId: hemisId ?? this.hemisId,
      address: address ?? this.address,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        login,
        email,
        name,
        fullName,
        phone,
        avatar,
        role,
        studentId,
        studentDbId,
        groupId,
        groupName,
        managedGroup,
        hemisId,
        address,
        isActive,
        createdAt,
      ];
}

