/// Dashboard Screen
/// Zamonaviy bosh sahifa - asosiy statistika va ma'lumotlar
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/custom_widgets.dart';
import '../../../data/providers/auth_provider.dart';
import '../../../data/providers/data_provider.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOut,
    );
    _animController.forward();

    // Ma'lumotlarni yuklash
    Future.microtask(() {
      if (mounted) {
        ref.read(notificationsProvider.notifier).refreshUnreadCount();
      }
    });
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(currentUserProvider);
    final unreadCount = ref.watch(unreadNotificationCountProvider);

    // Role-ga qarab dashboard provider tanlash
    final isLeader = user?.isLeader == true || user?.isAdmin == true || user?.isSuperAdmin == true;
    final mobileDashboard = isLeader
        ? ref.watch(leaderMobileDashboardProvider)
        : ref.watch(studentMobileDashboardProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            HapticFeedback.mediumImpact();
            if (isLeader) {
              ref.invalidate(leaderMobileDashboardProvider);
            } else {
              ref.invalidate(studentMobileDashboardProvider);
            }
            await ref.read(notificationsProvider.notifier).refreshUnreadCount();
          },
          color: AppColors.primary,
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              // Custom App Bar
              SliverToBoxAdapter(
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: _buildHeader(user, unreadCount),
                ),
              ),

              // Content
              SliverPadding(
                padding: const EdgeInsets.all(20),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    // Stats Section
                    mobileDashboard.when(
                      data: (data) => _buildMobileStats(data, user, isLeader),
                      loading: () => _buildStatsLoading(),
                      error: (e, __) => _buildStatsError(e.toString()),
                    ),

                    const SizedBox(height: 28),

                    // Quick Actions
                    _buildQuickActions(user),

                    const SizedBox(height: 28),

                    // Today's Schedule Preview
                    _buildSchedulePreview(),


                    const SizedBox(height: 100),
                  ]),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(dynamic user, int unreadCount) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Center(
              child: Text(
                _getInitials(user?.displayName ?? 'U'),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 14),

          // Greeting
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _getGreeting(),
                  style: TextStyle(
                    fontSize: 13,
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  user?.displayName ?? 'Foydalanuvchi',
                  style: const TextStyle(
                    fontSize: 18,
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),

          // Notification Button
          _buildNotificationButton(unreadCount),
        ],
      ),
    );
  }

  Widget _buildNotificationButton(int unreadCount) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        context.push('/notifications');
      },
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: AppColors.slate100,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Icon(
              Icons.notifications_outlined,
              color: AppColors.textPrimary,
              size: 24,
            ),
            if (unreadCount > 0)
              Positioned(
                right: 10,
                top: 10,
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppColors.error, AppColors.rose],
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.error.withOpacity(0.4),
                        blurRadius: 6,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  constraints: const BoxConstraints(
                    minWidth: 18,
                    minHeight: 18,
                  ),
                  child: Text(
                    unreadCount > 99 ? '99+' : unreadCount.toString(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  String _getInitials(String name) {
    final parts = name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.substring(0, name.length >= 2 ? 2 : 1).toUpperCase();
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Xayrli tong!';
    } else if (hour < 17) {
      return 'Xayrli kun!';
    } else {
      return 'Xayrli kech!';
    }
  }

  Widget _buildMobileStats(Map<String, dynamic> data, user, bool isLeader) {
    if (data.containsKey('error')) {
      return _buildStatsError(data['error']);
    }

    if (isLeader) {
      return _buildLeaderStats(data);
    } else {
      return _buildStudentStats(data);
    }
  }

  Widget _buildLeaderStats(Map<String, dynamic> data) {
    final group = data['group'] as Map<String, dynamic>? ?? {};
    final todayAttendance = data['today_attendance'] as Map<String, dynamic>? ?? {};
    final total = (todayAttendance['present'] ?? 0) + (todayAttendance['absent'] ?? 0) + (todayAttendance['late'] ?? 0);
    final presentRate = total > 0 ? ((todayAttendance['present'] ?? 0) / total * 100) : 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Group Info Card
        if (group['name'] != null)
          GradientCard(
            gradient: AppColors.primaryGradient,
            padding: const EdgeInsets.all(20),
            margin: const EdgeInsets.only(bottom: 20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(
                    Icons.groups_rounded,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Sizning guruhingiz',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 13,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        group['name'],
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${data['students_count'] ?? 0} talaba',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
          ),

        // Attendance Progress Card
        AnimatedProgressCard(
          title: 'Bugungi davomat',
          percentage: presentRate.toDouble(),
          color: AppColors.primary,
          icon: Icons.trending_up_rounded,
          label: '${todayAttendance['present'] ?? 0} keldi, ${todayAttendance['absent'] ?? 0} kelmadi',
        ),

        const SizedBox(height: 16),

        // Stats Grid
        SectionHeader(title: 'Statistika'),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 14,
          crossAxisSpacing: 14,
          childAspectRatio: 1.0,
          children: [
            ModernStatCard(
              title: 'Talabalar',
              value: '${data['students_count'] ?? 0}',
              icon: Icons.people_rounded,
              color: AppColors.indigo,
              onTap: () => context.push('/students'),
              showArrow: true,
            ),
            ModernStatCard(
              title: 'Bugungi darslar',
              value: '${data['today_classes'] ?? 0}',
              icon: Icons.menu_book_rounded,
              color: AppColors.teal,
              onTap: () => context.go('/schedule'),
              showArrow: true,
            ),
            ModernStatCard(
              title: 'Keldi',
              value: '${todayAttendance['present'] ?? 0}',
              icon: Icons.check_circle_rounded,
              color: AppColors.success,
            ),
            ModernStatCard(
              title: 'Kelmadi',
              value: '${todayAttendance['absent'] ?? 0}',
              icon: Icons.cancel_rounded,
              color: AppColors.error,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStudentStats(Map<String, dynamic> data) {
    final attendanceRate = (data['attendance_rate'] ?? 0).toDouble();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Attendance Progress
        AnimatedProgressCard(
          title: 'Davomat ko\'rsatkichi',
          percentage: attendanceRate,
          color: _getAttendanceColor(attendanceRate),
          icon: Icons.trending_up_rounded,
          label: 'Oxirgi 30 kun davomida',
        ),

        const SizedBox(height: 16),

        // Stats Grid
        SectionHeader(title: 'Bugungi holat'),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 14,
          crossAxisSpacing: 14,
          childAspectRatio: 1.0,
          children: [
            ModernStatCard(
              title: 'Holat',
              value: _getStatusLabel(data['today_status']),
              icon: _getStatusIcon(data['today_status']),
              color: _getStatusColor(data['today_status']),
            ),
            ModernStatCard(
              title: 'Darslar',
              value: '${data['today_classes'] ?? 0}',
              icon: Icons.menu_book_rounded,
              color: AppColors.indigo,
              onTap: () => context.go('/schedule'),
              showArrow: true,
            ),
            ModernStatCard(
              title: 'Davomat',
              value: '${attendanceRate.toStringAsFixed(0)}%',
              icon: Icons.insert_chart_rounded,
              color: AppColors.teal,
              onTap: () => context.go('/attendance'),
              showArrow: true,
            ),
            ModernStatCard(
              title: 'Bildirishnomalar',
              value: '${data['unread_notifications'] ?? 0}',
              icon: Icons.notifications_rounded,
              color: AppColors.warning,
              onTap: () => context.push('/notifications'),
              showArrow: true,
            ),
          ],
        ),
      ],
    );
  }

  Color _getAttendanceColor(double rate) {
    if (rate >= 80) return AppColors.success;
    if (rate >= 60) return AppColors.warning;
    return AppColors.error;
  }

  String _getStatusLabel(String? status) {
    switch (status) {
      case 'present': return 'Keldi';
      case 'absent': return 'Kelmadi';
      case 'late': return 'Kechikdi';
      case 'excused': return 'Sababli';
      default: return '—';
    }
  }

  IconData _getStatusIcon(String? status) {
    switch (status) {
      case 'present': return Icons.check_circle_rounded;
      case 'absent': return Icons.cancel_rounded;
      case 'late': return Icons.access_time_rounded;
      case 'excused': return Icons.info_rounded;
      default: return Icons.help_outline_rounded;
    }
  }

  Color _getStatusColor(String? status) {
    switch (status) {
      case 'present': return AppColors.success;
      case 'absent': return AppColors.error;
      case 'late': return AppColors.warning;
      case 'excused': return AppColors.info;
      default: return AppColors.textTertiary;
    }
  }

  Widget _buildStatsLoading() {
    return Column(
      children: [
        ShimmerBox(width: double.infinity, height: 100, borderRadius: 20),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 14,
          crossAxisSpacing: 14,
          childAspectRatio: 1.0,
          children: List.generate(4, (_) =>
            ShimmerBox(width: double.infinity, height: 100, borderRadius: 20),
          ),
        ),
      ],
    );
  }

  Widget _buildStatsError([String? message]) {
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: AppColors.errorLight,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.error.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.error.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.cloud_off_rounded,
              color: AppColors.error,
              size: 40,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Ma\'lumotlarni yuklashda xatolik',
            style: TextStyle(
              color: AppColors.error,
              fontWeight: FontWeight.w600,
              fontSize: 16,
            ),
          ),
          if (message != null) ...[
            const SizedBox(height: 8),
            Text(
              message,
              style: TextStyle(
                color: AppColors.error.withOpacity(0.8),
                fontSize: 13,
              ),
              textAlign: TextAlign.center,
            ),
          ],
          const SizedBox(height: 16),
          ModernButton(
            text: 'Qayta urinish',
            onPressed: () {
              final user = ref.read(currentUserProvider);
              final isLeader = user?.isLeader == true || user?.isAdmin == true;
              if (isLeader) {
                ref.invalidate(leaderMobileDashboardProvider);
              } else {
                ref.invalidate(studentMobileDashboardProvider);
              }
            },
            outlined: true,
            color: AppColors.error,
            height: 48,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(dynamic user) {
    final isLeader = user?.isLeader == true;
    final isAdmin = user?.isAdmin == true || user?.isSuperAdmin == true;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(title: 'Tezkor amallar'),
        const SizedBox(height: 14),
        GridView.count(
          crossAxisCount: 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
          childAspectRatio: 1.0,
          children: [
            if (isLeader || isAdmin)
              QuickActionButton(
                icon: Icons.how_to_reg_rounded,
                label: 'Davomat',
                color: AppColors.primary,
                compact: true,
                onTap: () {
                  HapticFeedback.lightImpact();
                  context.push('/attendance/mark');
                },
              ),
            QuickActionButton(
              icon: Icons.calendar_month_rounded,
              label: 'Jadval',
              color: AppColors.indigo,
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.go('/schedule');
              },
            ),
            if (isLeader || isAdmin)
              QuickActionButton(
                icon: Icons.people_rounded,
                label: 'Talabalar',
                color: AppColors.teal,
                compact: true,
                onTap: () {
                  HapticFeedback.lightImpact();
                  context.push('/students');
                },
              ),
            QuickActionButton(
              icon: Icons.emoji_events_rounded,
              label: 'Turnirlar',
              color: AppColors.warning,
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/tournaments');
              },
            ),
            QuickActionButton(
              icon: Icons.groups_rounded,
              label: 'To\'garaklar',
              color: AppColors.violet,
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/clubs');
              },
            ),
            QuickActionButton(
              icon: Icons.bar_chart_rounded,
              label: 'Hisobotlar',
              color: AppColors.cyan,
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/reports');
              },
            ),
            QuickActionButton(
              icon: Icons.settings_rounded,
              label: 'Sozlamalar',
              color: AppColors.slate500,
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/settings');
              },
            ),
            QuickActionButton(
              icon: Icons.menu_book_rounded,
              label: 'Kutubxona',
              color: const Color(0xFF8E24AA),
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/library');
              },
            ),
            QuickActionButton(
              icon: Icons.restaurant_rounded,
              label: 'Oshxona',
              color: const Color(0xFFE65100),
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/canteen');
              },
            ),
            QuickActionButton(
              icon: Icons.receipt_long_rounded,
              label: 'Kontrakt',
              color: const Color(0xFF00897B),
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/contracts');
              },
            ),
            QuickActionButton(
              icon: Icons.help_outline_rounded,
              label: 'Yordam',
              color: const Color(0xFF5C6BC0),
              compact: true,
              onTap: () {
                HapticFeedback.lightImpact();
                context.push('/help');
              },
            ),
            if (isLeader || isAdmin)
              QuickActionButton(
                icon: Icons.send_rounded,
                label: 'Xabar',
                color: const Color(0xFF00ACC1),
                compact: true,
                onTap: () {
                  HapticFeedback.lightImpact();
                  context.push('/notifications/compose');
                },
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildSchedulePreview() {
    final todaySchedule = ref.watch(todayScheduleProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionHeader(
          title: 'Bugungi darslar',
          actionText: 'Barchasi',
          actionIcon: Icons.arrow_forward_ios_rounded,
          onAction: () => context.go('/schedule'),
        ),
        const SizedBox(height: 14),
        todaySchedule.when(
          data: (data) {
            // Extract classes list from the response map
            final classes = data['classes'] as List<dynamic>? ?? [];

            if (classes.isEmpty) {
              return Container(
                padding: const EdgeInsets.all(32),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.slate100,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.event_available_rounded,
                        size: 36,
                        color: AppColors.textTertiary,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Bugun darslar yo\'q',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Dam oling!',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              );
            }

            return Column(
              children: classes.take(3).map((lesson) {
                return _buildLessonCard(lesson);
              }).toList(),
            );
          },
          loading: () => Column(
            children: List.generate(2, (_) =>
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: ShimmerBox(width: double.infinity, height: 80, borderRadius: 16),
              ),
            ),
          ),
          error: (_, __) => Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.errorLight,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Text(
              'Jadvalni yuklashda xatolik',
              style: TextStyle(color: AppColors.error),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLessonCard(dynamic lesson) {
    // Support both Schedule objects and raw Map from API
    final String subjectText = lesson is Map ? (lesson['subject'] ?? '') : lesson.subject;
    final String startTimeText = lesson is Map ? (lesson['start_time'] ?? '') : lesson.startTime;
    final String endTimeText = lesson is Map ? (lesson['end_time'] ?? '') : lesson.endTime;
    final String? teacherText = lesson is Map ? lesson['teacher'] : lesson.teacher;
    final String? roomText = lesson is Map ? lesson['room'] : lesson.room;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        children: [
          // Time indicator
          Container(
            width: 5,
            height: 56,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(3),
            ),
          ),
          const SizedBox(width: 16),

          // Lesson info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  subjectText,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 16,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(
                      Icons.access_time_rounded,
                      size: 14,
                      color: AppColors.textTertiary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '$startTimeText - $endTimeText',
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    if (teacherText != null) ...[
                      const SizedBox(width: 12),
                      Icon(
                        Icons.person_outline_rounded,
                        size: 14,
                        color: AppColors.textTertiary,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          teacherText,
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 13,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),

          // Room badge
          if (roomText != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppColors.primary.withOpacity(0.1),
                    AppColors.teal.withOpacity(0.1),
                  ],
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppColors.primary.withOpacity(0.2),
                ),
              ),
              child: Text(
                roomText,
                style: const TextStyle(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

