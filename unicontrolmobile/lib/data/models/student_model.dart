/// Student Model
/// Talaba ma'lumotlari modeli
library;

import 'package:equatable/equatable.dart';

class Student extends Equatable {
  final int id;
  final String studentId;
  final String name;
  final int? userId;
  final int? groupId;
  final String? groupName;
  final String? phone;
  final String? email;
  final String? address;
  final String? commute;
  final String? passport;
  final String? jshshir;
  final DateTime? birthDate;
  final String? gender;
  final double? contractAmount;
  final double? contractPaid;
  final DateTime? enrollmentDate;
  final DateTime? graduationDate;
  final bool isActive;
  final bool isGraduated;
  final String? hemisId;
  final String? avatar;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const Student({
    required this.id,
    required this.studentId,
    required this.name,
    this.userId,
    this.groupId,
    this.groupName,
    this.phone,
    this.email,
    this.address,
    this.commute,
    this.passport,
    this.jshshir,
    this.birthDate,
    this.gender,
    this.contractAmount,
    this.contractPaid,
    this.enrollmentDate,
    this.graduationDate,
    this.isActive = true,
    this.isGraduated = false,
    this.hemisId,
    this.avatar,
    this.createdAt,
    this.updatedAt,
  });

  /// Initialsni olish
  String get initials {
    if (name.isEmpty) return 'S';
    final words = name.trim().split(' ');
    if (words.length == 1) {
      return words[0][0].toUpperCase();
    }
    return '${words[0][0]}${words.last[0]}'.toUpperCase();
  }

  /// Kontrakt qoldig'i
  double get contractRemaining {
    final amount = contractAmount ?? 0;
    final paid = contractPaid ?? 0;
    return amount - paid;
  }

  /// Kontrakt to'langanlik foizi
  double get contractPercentage {
    if (contractAmount == null || contractAmount == 0) return 0;
    return ((contractPaid ?? 0) / contractAmount!) * 100;
  }

  /// Kontrakt to'liq to'langanmi
  bool get isContractPaid => contractRemaining <= 0;

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] as int,
      studentId: json['student_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      userId: json['user_id'] as int?,
      groupId: json['group_id'] as int?,
      groupName: json['group_name'] as String? ?? json['group'] as String?,
      phone: json['phone'] as String?,
      email: json['email'] as String?,
      address: json['address'] as String?,
      commute: json['commute'] as String?,
      passport: json['passport'] as String?,
      jshshir: json['jshshir'] as String?,
      birthDate: json['birth_date'] != null
          ? DateTime.tryParse(json['birth_date'] as String)
          : null,
      gender: json['gender'] as String?,
      contractAmount: (json['contract_amount'] as num?)?.toDouble(),
      contractPaid: (json['contract_paid'] as num?)?.toDouble(),
      enrollmentDate: json['enrollment_date'] != null
          ? DateTime.tryParse(json['enrollment_date'] as String)
          : null,
      graduationDate: json['graduation_date'] != null
          ? DateTime.tryParse(json['graduation_date'] as String)
          : null,
      isActive: json['is_active'] as bool? ?? true,
      isGraduated: json['is_graduated'] as bool? ?? false,
      hemisId: json['hemis_id'] as String?,
      avatar: json['avatar'] as String?,
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
      'name': name,
      'user_id': userId,
      'group_id': groupId,
      'group_name': groupName,
      'phone': phone,
      'email': email,
      'address': address,
      'commute': commute,
      'passport': passport,
      'jshshir': jshshir,
      'birth_date': birthDate?.toIso8601String(),
      'gender': gender,
      'contract_amount': contractAmount,
      'contract_paid': contractPaid,
      'enrollment_date': enrollmentDate?.toIso8601String(),
      'graduation_date': graduationDate?.toIso8601String(),
      'is_active': isActive,
      'is_graduated': isGraduated,
      'hemis_id': hemisId,
      'avatar': avatar,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  Student copyWith({
    int? id,
    String? studentId,
    String? name,
    int? userId,
    int? groupId,
    String? groupName,
    String? phone,
    String? email,
    String? address,
    String? commute,
    String? passport,
    String? jshshir,
    DateTime? birthDate,
    String? gender,
    double? contractAmount,
    double? contractPaid,
    DateTime? enrollmentDate,
    DateTime? graduationDate,
    bool? isActive,
    bool? isGraduated,
    String? hemisId,
    String? avatar,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Student(
      id: id ?? this.id,
      studentId: studentId ?? this.studentId,
      name: name ?? this.name,
      userId: userId ?? this.userId,
      groupId: groupId ?? this.groupId,
      groupName: groupName ?? this.groupName,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      address: address ?? this.address,
      commute: commute ?? this.commute,
      passport: passport ?? this.passport,
      jshshir: jshshir ?? this.jshshir,
      birthDate: birthDate ?? this.birthDate,
      gender: gender ?? this.gender,
      contractAmount: contractAmount ?? this.contractAmount,
      contractPaid: contractPaid ?? this.contractPaid,
      enrollmentDate: enrollmentDate ?? this.enrollmentDate,
      graduationDate: graduationDate ?? this.graduationDate,
      isActive: isActive ?? this.isActive,
      isGraduated: isGraduated ?? this.isGraduated,
      hemisId: hemisId ?? this.hemisId,
      avatar: avatar ?? this.avatar,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        studentId,
        name,
        userId,
        groupId,
        groupName,
        phone,
        email,
        address,
        commute,
        passport,
        jshshir,
        birthDate,
        gender,
        contractAmount,
        contractPaid,
        enrollmentDate,
        graduationDate,
        isActive,
        isGraduated,
        hemisId,
        avatar,
        createdAt,
        updatedAt,
      ];
}

