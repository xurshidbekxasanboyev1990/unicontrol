/// Notification Model
/// Bildirishnoma modeli
library;

import 'package:equatable/equatable.dart';
import '../../core/constants/app_constants.dart';

class AppNotification extends Equatable {
  final int id;
  final String title;
  final String message;
  final NotificationType type;
  final bool isRead;
  final int? senderId;
  final String? senderName;
  final int? recipientId;
  final String? link;
  final Map<String, dynamic>? data;
  final DateTime createdAt;
  final DateTime? readAt;

  const AppNotification({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    this.isRead = false,
    this.senderId,
    this.senderName,
    this.recipientId,
    this.link,
    this.data,
    required this.createdAt,
    this.readAt,
  });

  /// Type icon
  String get typeIcon {
    switch (type) {
      case NotificationType.info:
        return 'ℹ️';
      case NotificationType.warning:
        return '⚠️';
      case NotificationType.success:
        return '✅';
      case NotificationType.error:
        return '❌';
      case NotificationType.attendance:
        return '📋';
      case NotificationType.schedule:
        return '📅';
      case NotificationType.report:
        return '📊';
      case NotificationType.system:
        return '🔧';
    }
  }

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as int,
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? json['content'] as String? ?? '',
      type: NotificationType.fromString(json['type'] as String? ?? 'info'),
      isRead: json['is_read'] as bool? ?? json['read'] as bool? ?? false,
      senderId: json['sender_id'] as int?,
      senderName: json['sender_name'] as String?,
      recipientId: json['recipient_id'] as int?,
      link: json['link'] as String?,
      data: json['data'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String? ?? DateTime.now().toIso8601String()),
      readAt: json['read_at'] != null
          ? DateTime.tryParse(json['read_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'message': message,
      'type': type.value,
      'is_read': isRead,
      'sender_id': senderId,
      'sender_name': senderName,
      'recipient_id': recipientId,
      'link': link,
      'data': data,
      'created_at': createdAt.toIso8601String(),
      'read_at': readAt?.toIso8601String(),
    };
  }

  AppNotification copyWith({
    int? id,
    String? title,
    String? message,
    NotificationType? type,
    bool? isRead,
    int? senderId,
    String? senderName,
    int? recipientId,
    String? link,
    Map<String, dynamic>? data,
    DateTime? createdAt,
    DateTime? readAt,
  }) {
    return AppNotification(
      id: id ?? this.id,
      title: title ?? this.title,
      message: message ?? this.message,
      type: type ?? this.type,
      isRead: isRead ?? this.isRead,
      senderId: senderId ?? this.senderId,
      senderName: senderName ?? this.senderName,
      recipientId: recipientId ?? this.recipientId,
      link: link ?? this.link,
      data: data ?? this.data,
      createdAt: createdAt ?? this.createdAt,
      readAt: readAt ?? this.readAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        title,
        message,
        type,
        isRead,
        senderId,
        senderName,
        recipientId,
        link,
        data,
        createdAt,
        readAt,
      ];
}

