/// Utils - Helpers and Extensions
/// Barcha yordamchi funksiyalar va extensionlar
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../constants/app_constants.dart';

// ==========================================
// DATE/TIME EXTENSIONS
// ==========================================

extension DateTimeExtension on DateTime {
  /// Format: 16.02.2026
  String toDisplayDate() {
    return DateFormat(AppConstants.dateFormat).format(this);
  }

  /// Format: 09:30
  String toDisplayTime() {
    return DateFormat(AppConstants.timeFormat).format(this);
  }

  /// Format: 16.02.2026 09:30
  String toDisplayDateTime() {
    return DateFormat(AppConstants.dateTimeFormat).format(this);
  }

  /// Format: 2026-02-16
  String toApiDate() {
    return DateFormat(AppConstants.apiDateFormat).format(this);
  }

  /// Format: 2026-02-16T09:30:00
  String toApiDateTime() {
    return DateFormat(AppConstants.apiDateTimeFormat).format(this);
  }

  /// Bugun ekanligini tekshirish
  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  /// Kecha ekanligini tekshirish
  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year && month == yesterday.month && day == yesterday.day;
  }

  /// Hafta boshi (Dushanba)
  DateTime get startOfWeek {
    return subtract(Duration(days: weekday - 1));
  }

  /// Hafta oxiri (Yakshanba)
  DateTime get endOfWeek {
    return add(Duration(days: 7 - weekday));
  }

  /// Oy boshi
  DateTime get startOfMonth {
    return DateTime(year, month, 1);
  }

  /// Oy oxiri
  DateTime get endOfMonth {
    return DateTime(year, month + 1, 0);
  }

  /// Nisbiy vaqt (1 soat oldin, kecha, ...)
  String toRelativeTime() {
    final now = DateTime.now();
    final difference = now.difference(this);

    if (difference.inSeconds < 60) {
      return 'Hozirgina';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} daqiqa oldin';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} soat oldin';
    } else if (isYesterday) {
      return 'Kecha';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} kun oldin';
    } else if (difference.inDays < 30) {
      return '${(difference.inDays / 7).floor()} hafta oldin';
    } else if (difference.inDays < 365) {
      return '${(difference.inDays / 30).floor()} oy oldin';
    } else {
      return '${(difference.inDays / 365).floor()} yil oldin';
    }
  }
}

// ==========================================
// STRING EXTENSIONS
// ==========================================

extension StringExtension on String {
  /// Birinchi harfni katta qilish
  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }

  /// Har bir so'zning birinchi harfini katta qilish
  String titleCase() {
    if (isEmpty) return this;
    return split(' ').map((word) => word.capitalize()).join(' ');
  }

  /// Email formatini tekshirish
  bool get isValidEmail {
    return RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(this);
  }

  /// Telefon formatini tekshirish (+998XXXXXXXXX)
  bool get isValidPhone {
    return RegExp(r'^\+?998[0-9]{9}$').hasMatch(replaceAll(' ', '').replaceAll('-', ''));
  }

  /// Bo'sh yoki null emasligini tekshirish
  bool get isNotNullOrEmpty => isNotEmpty;

  /// Initialsni olish (Anvar Sanayev -> AS)
  String get initials {
    if (isEmpty) return '';
    final words = trim().split(' ');
    if (words.length == 1) {
      return words[0][0].toUpperCase();
    }
    return '${words[0][0]}${words.last[0]}'.toUpperCase();
  }

  /// Matnni qisqartirish
  String truncate(int maxLength, {String ellipsis = '...'}) {
    if (length <= maxLength) return this;
    return '${substring(0, maxLength - ellipsis.length)}$ellipsis';
  }
}

// ==========================================
// NUMBER EXTENSIONS
// ==========================================

extension NumberExtension on num {
  /// Pul formatida ko'rsatish (1,234,567.00)
  String toCurrency({String symbol = "so'm", int decimals = 0}) {
    final formatter = NumberFormat.currency(
      locale: 'uz_UZ',
      symbol: symbol,
      decimalDigits: decimals,
    );
    return formatter.format(this);
  }

  /// Kompakt formatda (1.2K, 3.4M)
  String toCompact() {
    final formatter = NumberFormat.compact(locale: 'en');
    return formatter.format(this);
  }

  /// Foizda ko'rsatish
  String toPercent({int decimals = 1}) {
    return '${toStringAsFixed(decimals)}%';
  }
}

// ==========================================
// LIST EXTENSIONS
// ==========================================

extension ListExtension<T> on List<T> {
  /// Xavfsiz indeks bilan olish
  T? getOrNull(int index) {
    if (index < 0 || index >= length) return null;
    return this[index];
  }

  /// Birinchi elementni xavfsiz olish
  T? get firstOrNull => isEmpty ? null : first;

  /// Oxirgi elementni xavfsiz olish
  T? get lastOrNull => isEmpty ? null : last;
}

// ==========================================
// CONTEXT EXTENSIONS
// ==========================================

extension ContextExtension on BuildContext {
  /// Screen size
  Size get screenSize => MediaQuery.of(this).size;
  double get screenWidth => screenSize.width;
  double get screenHeight => screenSize.height;

  /// Safe area padding
  EdgeInsets get safePadding => MediaQuery.of(this).padding;
  double get safeTop => safePadding.top;
  double get safeBottom => safePadding.bottom;

  /// Theme
  ThemeData get theme => Theme.of(this);
  TextTheme get textTheme => theme.textTheme;
  ColorScheme get colorScheme => theme.colorScheme;

  /// Media query
  bool get isDarkMode => theme.brightness == Brightness.dark;
  bool get isTablet => screenWidth >= 600;
  bool get isDesktop => screenWidth >= 1200;

  /// Show snackbar
  void showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : null,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Show success snackbar
  void showSuccess(String message) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.white),
            const SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Show error snackbar
  void showError(String message) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error, color: Colors.white),
            const SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// Show loading dialog
  void showLoading({String? message}) {
    showDialog(
      context: this,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Text(message ?? 'Yuklanmoqda...'),
          ],
        ),
      ),
    );
  }

  /// Hide loading dialog
  void hideLoading() {
    Navigator.of(this).pop();
  }
}

// ==========================================
// COLOR EXTENSIONS
// ==========================================

extension ColorExtension on Color {
  /// Rangni och qilish
  Color lighten([double amount = 0.1]) {
    assert(amount >= 0 && amount <= 1);
    return Color.lerp(this, Colors.white, amount)!;
  }

  /// Rangni to'q qilish
  Color darken([double amount = 0.1]) {
    assert(amount >= 0 && amount <= 1);
    return Color.lerp(this, Colors.black, amount)!;
  }
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================

/// Null-safe parse functions
int? parseInt(dynamic value) {
  if (value == null) return null;
  if (value is int) return value;
  if (value is String) return int.tryParse(value);
  return null;
}

double? parseDouble(dynamic value) {
  if (value == null) return null;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
}

DateTime? parseDateTime(dynamic value) {
  if (value == null) return null;
  if (value is DateTime) return value;
  if (value is String) return DateTime.tryParse(value);
  return null;
}

/// Debouncer class
class Debouncer {
  final Duration delay;
  VoidCallback? _action;
  bool _isDebouncing = false;

  Debouncer({this.delay = const Duration(milliseconds: 500)});

  void call(VoidCallback action) {
    _action = action;
    if (!_isDebouncing) {
      _isDebouncing = true;
      Future.delayed(delay, () {
        _action?.call();
        _isDebouncing = false;
      });
    }
  }

  void dispose() {
    _action = null;
  }
}

