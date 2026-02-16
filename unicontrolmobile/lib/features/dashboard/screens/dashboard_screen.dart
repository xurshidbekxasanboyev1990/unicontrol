/// Dashboard Screen
/// Bosh sahifa - asosiy statistika va ma'lumotlar
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../data/providers/auth_provider.dart';
import '../../../data/providers/data_provider.dart';
import '../widgets/stat_card.dart';
import '../widgets/quick_action_card.dart';
import '../widgets/attendance_chart.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    // Ma'lumotlarni yuklash
    Future.microtask(() {
      ref.read(notificationsProvider.notifier).refreshUnreadCount();
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(currentUserProvider);
    final dashboardStats = ref.watch(dashboardStatsProvider);
    final unreadCount = ref.watch(unreadNotificationCountProvider);

    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(dashboardStatsProvider);
            await ref.read(notificationsProvider.notifier).refreshUnreadCount();
          },
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverAppBar(
                floating: true,
                backgroundColor: AppTheme.backgroundLight,
                elevation: 0,
                title: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getGreeting(),
                      style: const TextStyle(
                        fontSize: 14,
                        color: AppTheme.textSecondary,
                        fontWeight: FontWeight.normal,
                      ),
                    ),
                    Text(
                      user?.displayName ?? 'Foydalanuvchi',
                      style: const TextStyle(
                        fontSize: 20,
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                actions: [
                  // Notifications button
                  Stack(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.notifications_outlined),
                        color: AppTheme.textPrimary,
                        onPressed: () => context.push('/notifications'),
                      ),
                      if (unreadCount > 0)
                        Positioned(
                          right: 8,
                          top: 8,
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: const BoxDecoration(
                              color: AppTheme.errorColor,
                              shape: BoxShape.circle,
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
                  const SizedBox(width: 8),
                ],
              ),

              // Content
              SliverPadding(
                padding: const EdgeInsets.all(16),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    // Statistics Cards
                    dashboardStats.when(
                      data: (stats) => _buildStatsSection(stats, user),
                      loading: () => _buildStatsLoading(),
                      error: (_, __) => _buildStatsError(),
                    ),

                    const SizedBox(height: 24),

                    // Quick Actions
                    _buildQuickActions(user),

                    const SizedBox(height: 24),

                    // Today's Schedule Preview
                    _buildSchedulePreview(),

                    const SizedBox(height: 24),

                    // Attendance Chart (for leader/admin)
                    if (user?.canManageStudents == true)
                      dashboardStats.when(
                        data: (stats) => AttendanceChartWidget(stats: stats),
                        loading: () => const SizedBox.shrink(),
                        error: (_, __) => const SizedBox.shrink(),
                      ),

                    const SizedBox(height: 80),
                  ]),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Xayrli tong! 🌅';
    } else if (hour < 17) {
      return 'Xayrli kun! ☀️';
    } else {
      return 'Xayrli kech! 🌙';
    }
  }

  Widget _buildStatsSection(dynamic stats, dynamic user) {
    final isLeaderOrAdmin = user?.canManageStudents == true;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Statistika',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.5,
          children: [
            StatCard(
              title: 'Davomat',
              value: '${stats.todayAttendanceRate.toStringAsFixed(1)}%',
              subtitle: 'Bugungi',
              icon: Icons.fact_check_outlined,
              color: AppTheme.primaryColor,
            ),
            if (isLeaderOrAdmin)
              StatCard(
                title: 'Talabalar',
                value: '${stats.totalStudents}',
                subtitle: '${stats.activeStudents} faol',
                icon: Icons.people_outline,
                color: AppTheme.secondaryColor,
              )
            else
              StatCard(
                title: 'Darslar',
                value: '${stats.todayLessons}',
                subtitle: 'Bugungi',
                icon: Icons.book_outlined,
                color: AppTheme.secondaryColor,
              ),
            StatCard(
              title: 'Keldi',
              value: '${stats.todayPresent}',
              subtitle: 'Bugun',
              icon: Icons.check_circle_outline,
              color: AppTheme.successColor,
            ),
            StatCard(
              title: 'Kelmadi',
              value: '${stats.todayAbsent}',
              subtitle: 'Bugun',
              icon: Icons.cancel_outlined,
              color: AppTheme.errorColor,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatsLoading() {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: List.generate(
        4,
        (_) => Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.borderColor),
          ),
          child: const Center(
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      ),
    );
  }

  Widget _buildStatsError() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.errorColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Column(
        children: [
          Icon(Icons.error_outline, color: AppTheme.errorColor, size: 48),
          SizedBox(height: 8),
          Text(
            'Ma\'lumotlarni yuklashda xatolik',
            style: TextStyle(color: AppTheme.errorColor),
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
        const Text(
          'Tezkor amallar',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              if (isLeader || isAdmin)
                QuickActionCard(
                  icon: Icons.how_to_reg,
                  label: 'Davomat olish',
                  color: AppTheme.primaryColor,
                  onTap: () => context.push('/attendance/mark'),
                ),
              QuickActionCard(
                icon: Icons.calendar_today,
                label: 'Jadval',
                color: AppTheme.secondaryColor,
                onTap: () => context.go('/schedule'),
              ),
              if (isLeader || isAdmin)
                QuickActionCard(
                  icon: Icons.people,
                  label: 'Talabalar',
                  color: AppTheme.tealColor,
                  onTap: () => context.push('/students'),
                ),
              QuickActionCard(
                icon: Icons.emoji_events,
                label: 'Turnirlar',
                color: AppTheme.warningColor,
                onTap: () => context.push('/tournaments'),
              ),
              QuickActionCard(
                icon: Icons.groups,
                label: 'To\'garaklar',
                color: AppTheme.accentColor,
                onTap: () => context.push('/clubs'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSchedulePreview() {
    final todaySchedule = ref.watch(todayScheduleProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Bugungi darslar',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary,
              ),
            ),
            TextButton(
              onPressed: () => context.go('/schedule'),
              child: const Text('Barchasi'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        todaySchedule.when(
          data: (schedule) {
            if (schedule.isEmpty) {
              return Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.borderColor),
                ),
                child: const Center(
                  child: Column(
                    children: [
                      Icon(
                        Icons.event_busy,
                        size: 48,
                        color: AppTheme.textTertiary,
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Bugun darslar yo\'q',
                        style: TextStyle(color: AppTheme.textSecondary),
                      ),
                    ],
                  ),
                ),
              );
            }

            return Column(
              children: schedule.take(3).map((lesson) {
                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.borderColor),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 4,
                        height: 50,
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              lesson.subject,
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 15,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${lesson.startTime} - ${lesson.endTime}',
                              style: const TextStyle(
                                color: AppTheme.textSecondary,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ),
                      if (lesson.room != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryColor.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            lesson.room!,
                            style: const TextStyle(
                              color: AppTheme.primaryColor,
                              fontWeight: FontWeight.w500,
                              fontSize: 12,
                            ),
                          ),
                        ),
                    ],
                  ),
                );
              }).toList(),
            );
          },
          loading: () => const Center(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          ),
          error: (_, __) => const Center(
            child: Text('Jadvalni yuklashda xatolik'),
          ),
        ),
      ],
    );
  }
}

