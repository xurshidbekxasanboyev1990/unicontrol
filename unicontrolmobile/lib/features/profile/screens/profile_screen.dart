/// Profile Screen
/// Foydalanuvchi profili
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../data/providers/auth_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);

    if (user == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      body: CustomScrollView(
        slivers: [
          // Header with gradient
          SliverAppBar(
            expandedHeight: 260,
            pinned: true,
            backgroundColor: AppTheme.primaryColor,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(height: 40),
                      // Avatar
                      Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.2),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: Center(
                          child: Text(
                            user.initials,
                            style: const TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      // Name
                      Text(
                        user.displayName,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      // Role badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          user.roleLabel,
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Content
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Info Card
                _buildInfoCard([
                  if (user.email != null)
                    _buildInfoRow(
                      Icons.email_outlined,
                      'Email',
                      user.email!,
                    ),
                  if (user.phone != null)
                    _buildInfoRow(
                      Icons.phone_outlined,
                      'Telefon',
                      user.phone!,
                    ),
                  if (user.groupName != null)
                    _buildInfoRow(
                      Icons.group_outlined,
                      'Guruh',
                      user.groupName!,
                    ),
                  if (user.address != null)
                    _buildInfoRow(
                      Icons.location_on_outlined,
                      'Manzil',
                      user.address!,
                    ),
                ]),

                const SizedBox(height: 16),

                // Menu items
                _buildMenuCard(context, ref, [
                  _MenuItem(
                    icon: Icons.notifications_outlined,
                    title: 'Bildirishnomalar',
                    onTap: () => context.push('/notifications'),
                  ),
                  _MenuItem(
                    icon: Icons.bar_chart_outlined,
                    title: 'Hisobotlar',
                    onTap: () => context.push('/reports'),
                  ),
                  _MenuItem(
                    icon: Icons.groups_outlined,
                    title: 'To\'garaklar',
                    onTap: () => context.push('/clubs'),
                  ),
                  _MenuItem(
                    icon: Icons.emoji_events_outlined,
                    title: 'Turnirlar',
                    onTap: () => context.push('/tournaments'),
                  ),
                ]),

                const SizedBox(height: 16),

                // Settings & Logout
                _buildMenuCard(context, ref, [
                  _MenuItem(
                    icon: Icons.settings_outlined,
                    title: 'Sozlamalar',
                    onTap: () => context.push('/settings'),
                  ),
                  _MenuItem(
                    icon: Icons.help_outline,
                    title: 'Yordam',
                    onTap: () {
                      // TODO: Show help dialog
                    },
                  ),
                  _MenuItem(
                    icon: Icons.logout,
                    title: 'Chiqish',
                    isDestructive: true,
                    onTap: () => _showLogoutDialog(context, ref),
                  ),
                ]),

                const SizedBox(height: 24),

                // Version
                Center(
                  child: Text(
                    'UniControl v1.0.0',
                    style: TextStyle(
                      color: AppTheme.textTertiary.withValues(alpha: 0.7),
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(height: 80),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(List<Widget> children) {
    if (children.isEmpty) return const SizedBox.shrink();

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        children: children
            .map((child) => Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  child: child,
                ))
            .toList(),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: AppTheme.primaryColor,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: AppTheme.textTertiary,
                  fontSize: 12,
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 15,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMenuCard(
    BuildContext context,
    WidgetRef ref,
    List<_MenuItem> items,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        children: items.asMap().entries.map((entry) {
          final index = entry.key;
          final item = entry.value;
          final isLast = index == items.length - 1;

          return Column(
            children: [
              ListTile(
                leading: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: item.isDestructive
                        ? AppTheme.errorColor.withValues(alpha: 0.1)
                        : AppTheme.primaryColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    item.icon,
                    color: item.isDestructive
                        ? AppTheme.errorColor
                        : AppTheme.primaryColor,
                    size: 20,
                  ),
                ),
                title: Text(
                  item.title,
                  style: TextStyle(
                    fontWeight: FontWeight.w500,
                    color: item.isDestructive
                        ? AppTheme.errorColor
                        : AppTheme.textPrimary,
                  ),
                ),
                trailing: Icon(
                  Icons.chevron_right,
                  color: AppTheme.textTertiary,
                ),
                onTap: item.onTap,
              ),
              if (!isLast)
                const Divider(height: 1, indent: 68),
            ],
          );
        }).toList(),
      ),
    );
  }

  void _showLogoutDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: const Text('Chiqish'),
        content: const Text(
          'Haqiqatan ham tizimdan chiqmoqchimisiz?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Bekor qilish'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) {
                context.go('/login');
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.errorColor,
            ),
            child: const Text('Chiqish'),
          ),
        ],
      ),
    );
  }
}

class _MenuItem {
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final bool isDestructive;

  const _MenuItem({
    required this.icon,
    required this.title,
    required this.onTap,
    this.isDestructive = false,
  });
}

