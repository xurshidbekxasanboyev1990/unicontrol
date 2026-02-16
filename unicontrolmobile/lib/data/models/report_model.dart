/// Report Model
/// Hisobot modeli
library;

import 'package:equatable/equatable.dart';
import '../../core/constants/app_constants.dart';

class Report extends Equatable {
  final int id;
  final int? groupId;
  final String? groupName;
  final int? submittedBy;
  final String? submittedByName;
  final DateTime date;
  final ReportStatus status;
  final String? content;
  final String? notes;
  final int presentCount;
  final int absentCount;
  final int lateCount;
  final int excusedCount;
  final int totalCount;
  final int? approvedBy;
  final String? approvedByName;
  final DateTime? approvedAt;
  final String? rejectionReason;
  final List<ReportAttachment>? attachments;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const Report({
    required this.id,
    this.groupId,
    this.groupName,
    this.submittedBy,
    this.submittedByName,
    required this.date,
    required this.status,
    this.content,
    this.notes,
    this.presentCount = 0,
    this.absentCount = 0,
    this.lateCount = 0,
    this.excusedCount = 0,
    this.totalCount = 0,
    this.approvedBy,
    this.approvedByName,
    this.approvedAt,
    this.rejectionReason,
    this.attachments,
    this.createdAt,
    this.updatedAt,
  });

  /// Davomat foizi
  double get attendanceRate {
    if (totalCount == 0) return 0;
    return (presentCount / totalCount) * 100;
  }

  /// Kutilmoqda
  bool get isPending => status == ReportStatus.pending;

  /// Tasdiqlangan
  bool get isApproved => status == ReportStatus.approved;

  /// Rad etilgan
  bool get isRejected => status == ReportStatus.rejected;

  factory Report.fromJson(Map<String, dynamic> json) {
    return Report(
      id: json['id'] as int,
      groupId: json['group_id'] as int?,
      groupName: json['group_name'] as String?,
      submittedBy: json['submitted_by'] as int?,
      submittedByName: json['submitted_by_name'] as String?,
      date: DateTime.parse(json['date'] as String),
      status: ReportStatus.fromString(json['status'] as String? ?? 'pending'),
      content: json['content'] as String?,
      notes: json['notes'] as String?,
      presentCount: json['present_count'] as int? ?? 0,
      absentCount: json['absent_count'] as int? ?? 0,
      lateCount: json['late_count'] as int? ?? 0,
      excusedCount: json['excused_count'] as int? ?? 0,
      totalCount: json['total_count'] as int? ?? 0,
      approvedBy: json['approved_by'] as int?,
      approvedByName: json['approved_by_name'] as String?,
      approvedAt: json['approved_at'] != null
          ? DateTime.tryParse(json['approved_at'] as String)
          : null,
      rejectionReason: json['rejection_reason'] as String?,
      attachments: (json['attachments'] as List<dynamic>?)
          ?.map((e) => ReportAttachment.fromJson(e as Map<String, dynamic>))
          .toList(),
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
      'group_id': groupId,
      'group_name': groupName,
      'submitted_by': submittedBy,
      'submitted_by_name': submittedByName,
      'date': date.toIso8601String().split('T')[0],
      'status': status.value,
      'content': content,
      'notes': notes,
      'present_count': presentCount,
      'absent_count': absentCount,
      'late_count': lateCount,
      'excused_count': excusedCount,
      'total_count': totalCount,
      'approved_by': approvedBy,
      'approved_by_name': approvedByName,
      'approved_at': approvedAt?.toIso8601String(),
      'rejection_reason': rejectionReason,
      'attachments': attachments?.map((e) => e.toJson()).toList(),
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [
        id,
        groupId,
        groupName,
        submittedBy,
        submittedByName,
        date,
        status,
        content,
        notes,
        presentCount,
        absentCount,
        lateCount,
        excusedCount,
        totalCount,
        approvedBy,
        approvedByName,
        approvedAt,
        rejectionReason,
        attachments,
        createdAt,
        updatedAt,
      ];
}

class ReportAttachment extends Equatable {
  final int id;
  final String fileName;
  final String fileUrl;
  final String? fileType;
  final int? fileSize;

  const ReportAttachment({
    required this.id,
    required this.fileName,
    required this.fileUrl,
    this.fileType,
    this.fileSize,
  });

  factory ReportAttachment.fromJson(Map<String, dynamic> json) {
    return ReportAttachment(
      id: json['id'] as int,
      fileName: json['file_name'] as String? ?? '',
      fileUrl: json['file_url'] as String? ?? '',
      fileType: json['file_type'] as String?,
      fileSize: json['file_size'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'file_name': fileName,
      'file_url': fileUrl,
      'file_type': fileType,
      'file_size': fileSize,
    };
  }

  @override
  List<Object?> get props => [id, fileName, fileUrl, fileType, fileSize];
}

