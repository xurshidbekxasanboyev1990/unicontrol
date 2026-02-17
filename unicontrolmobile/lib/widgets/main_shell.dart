/// Main Shell
/// Zamonaviy Bottom navigation bilan asosiy layout
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/theme/app_colors.dart';
import '../data/providers/auth_provider.dart';
import '../data/providers/data_provider.dart';

class MainShell extends ConsumerStatefulWidget {
  final Widget child;

  const MainShell({super.key, required this.child});

  @override
  ConsumerState<MainShell> createState() => _MainShellState();
}

class _MainShellState extends ConsumerState<MainShell> {
  int _currentIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<_NavItem> _studentNavItems = [
    _NavItem(
      path: '/dashboard',
      icon: Icons.dashboard_outlined,
      activeIcon: Icons.dashboard_rounded,
      label: 'Bosh sahifa',
    ),
    _NavItem(
      path: '/schedule',
      icon: Icons.calendar_today_outlined,
      activeIcon: Icons.calendar_today_rounded,
      label: 'Jadval',
    ),
    _NavItem(
      path: '/attendance',
      icon: Icons.fact_check_outlined,
      activeIcon: Icons.fact_check_rounded,
      label: 'Davomat',
    ),
    _NavItem(
      path: '/profile',
      icon: Icons.person_outline_rounded,
      activeIcon: Icons.person_rounded,
      label: 'Profil',
    ),
  ];

  final List<_NavItem> _leaderNavItems = [
    _NavItem(
      path: '/dashboard',
      icon: Icons.dashboard_outlined,
      activeIcon: Icons.dashboard_rounded,
      label: 'Bosh sahifa',
    ),
    _NavItem(
      path: '/attendance',
      icon: Icons.fact_check_outlined,
      activeIcon: Icons.fact_check_rounded,
      label: 'Davomat',
    ),
    _NavItem(
      path: '/schedule',
      icon: Icons.calendar_today_outlined,
      activeIcon: Icons.calendar_today_rounded,
      label: 'Jadval',
    ),
    _NavItem(
      path: '/profile',
      icon: Icons.person_outline_rounded,
      activeIcon: Icons.person_rounded,
      label: 'Profil',
    ),
  ];

  final List<_NavItem> _adminNavItems = [
    _NavItem(
      path: '/dashboard',
      icon: Icons.dashboard_outlined,
      activeIcon: Icons.dashboard_rounded,
      label: 'Dashboard',
    ),
    _NavItem(
      path: '/attendance',
      icon: Icons.fact_check_outlined,
      activeIcon: Icons.fact_check_rounded,
      label: 'Davomat',
    ),
    _NavItem(
      path: '/schedule',
      icon: Icons.calendar_today_outlined,
      activeIcon: Icons.calendar_today_rounded,
      label: 'Jadval',
    ),
    _NavItem(
      path: '/profile',
      icon: Icons.person_outline_rounded,
      activeIcon: Icons.person_rounded,
      label: 'Profil',
    ),
  ];

  List<_NavItem> get _navItems {
    final user = ref.read(currentUserProvider);
    if (user == null) return _studentNavItems;

    switch (user.role.value) {
      case 'leader':
        return _leaderNavItems;
      case 'admin':
      case 'superadmin':
        return _adminNavItems;
      default:
        return _studentNavItems;
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _updateIndex();
  }

  void _updateIndex() {
    final location = GoRouterState.of(context).matchedLocation;
    final navItems = _navItems;

    for (int i = 0; i < navItems.length; i++) {
      if (location.startsWith(navItems[i].path)) {
        if (_currentIndex != i) {
          setState(() => _currentIndex = i);
        }
        break;
      }
    }
  }

  void _onItemTapped(int index) {
    if (index != _currentIndex) {
      HapticFeedback.lightImpact();
      setState(() => _currentIndex = index);
      context.go(_navItems[index].path);
    }
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = ref.watch(unreadNotificationCountProvider);
    final navItems = _navItems;
    final user = ref.read(currentUserProvider);
    final isLeader = user?.isLeader == true;
    final isAdmin = user?.isAdmin == true || user?.isSuperAdmin == true;

    return Scaffold(
      key: _scaffoldKey,
      body: widget.child,
      extendBody: true,
      drawer: _buildDrawer(user, isLeader, isAdmin, unreadCount),
      bottomNavigationBar: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 30,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: navItems.asMap().entries.map((entry) {
                final index = entry.key;
                final item = entry.value;
                final isSelected = _currentIndex == index;

                return _NavBarItem(
                  icon: isSelected ? item.activeIcon : item.icon,
                  label: item.label,
                  isSelected: isSelected,
                  badge: item.path == '/notifications' && unreadCount > 0
                      ? unreadCount
                      : null,
                  onTap: () => _onItemTapped(index),
                );
              }).toList(),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDrawer(dynamic user, bool isLeader, bool isAdmin, int unreadCount) {
    final userName = user != null ? '${user.firstName ?? ''} ${user.lastName ?? ''}'.trim() : 'Foydalanuvchi';
    final userRole = user?.role?.value ?? 'student';

    return Drawer(
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.horizontal(right: Radius.circular(24)),
      ),
      child: SafeArea(
        child: Column(
          children: [
            // User header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(20, 24, 20, 20),
              decoration: const BoxDecoration(gradient: AppColors.primaryGradient),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CircleAvatar(
                    radius: 32,
                    backgroundColor: Colors.white.withOpacity(0.2),
                    child: Text(
                      userName.isNotEmpty ? userName[0].toUpperCase() : '?',
                      style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    userName,
                    style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _getRoleName(userRole),
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),

            // Menu items
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(vertical: 8),
                children: [
                  _DrawerItem(icon: Icons.dashboard_rounded, label: 'Bosh sahifa', onTap: () => _navigateFromDrawer('/dashboard')),
                  _DrawerItem(icon: Icons.calendar_today_rounded, label: 'Jadval', onTap: () => _navigateFromDrawer('/schedule')),
                  _DrawerItem(icon: Icons.fact_check_rounded, label: 'Davomat', onTap: () => _navigateFromDrawer('/attendance')),
                  _DrawerItem(
                    icon: Icons.notifications_rounded,
                    label: 'Bildirishnomalar',
                    badge: unreadCount > 0 ? unreadCount : null,
                    onTap: () => _navigateFromDrawer('/notifications'),
                  ),
                  const Divider(height: 1, indent: 16, endIndent: 16),
                  _DrawerItem(icon: Icons.menu_book_rounded, label: 'Kutubxona', color: const Color(0xFF8E24AA), onTap: () => _navigateFromDrawer('/library')),
                  _DrawerItem(icon: Icons.restaurant_rounded, label: 'Oshxona', color: const Color(0xFFE65100), onTap: () => _navigateFromDrawer('/canteen')),
                  _DrawerItem(icon: Icons.receipt_long_rounded, label: 'Kontrakt', color: const Color(0xFF00897B), onTap: () => _navigateFromDrawer('/contracts')),
                  _DrawerItem(icon: Icons.emoji_events_rounded, label: 'Turnirlar', color: const Color(0xFFF9A825), onTap: () => _navigateFromDrawer('/tournaments')),
                  _DrawerItem(icon: Icons.groups_rounded, label: 'To\'garaklar', color: const Color(0xFF7C4DFF), onTap: () => _navigateFromDrawer('/clubs')),
                  const Divider(height: 1, indent: 16, endIndent: 16),
                  if (isLeader || isAdmin) ...[
                    _DrawerItem(icon: Icons.people_rounded, label: 'Talabalar', onTap: () => _navigateFromDrawer('/students')),
                    _DrawerItem(icon: Icons.groups_2_rounded, label: 'Guruhlar', onTap: () => _navigateFromDrawer('/groups')),
                    _DrawerItem(icon: Icons.bar_chart_rounded, label: 'Hisobotlar', onTap: () => _navigateFromDrawer('/reports')),
                    _DrawerItem(icon: Icons.send_rounded, label: 'Xabar yuborish', color: const Color(0xFF00ACC1), onTap: () => _navigateFromDrawer('/notifications/compose')),
                    const Divider(height: 1, indent: 16, endIndent: 16),
                  ],
                  _DrawerItem(icon: Icons.help_outline_rounded, label: 'Yordam', color: const Color(0xFF5C6BC0), onTap: () => _navigateFromDrawer('/help')),
                  _DrawerItem(icon: Icons.settings_rounded, label: 'Sozlamalar', onTap: () => _navigateFromDrawer('/settings')),
                ],
              ),
            ),

            // Profile
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                border: Border(top: BorderSide(color: AppColors.border)),
              ),
              child: ListTile(
                leading: const Icon(Icons.person_rounded, color: AppColors.primary),
                title: const Text('Profil', style: TextStyle(fontWeight: FontWeight.w600)),
                trailing: const Icon(Icons.chevron_right_rounded, color: AppColors.textTertiary),
                contentPadding: EdgeInsets.zero,
                onTap: () => _navigateFromDrawer('/profile'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateFromDrawer(String path) {
    Navigator.pop(context); // Close drawer
    if (path == '/dashboard' || path == '/schedule' || path == '/attendance' || path == '/profile') {
      context.go(path);
    } else {
      context.push(path);
    }
  }

  String _getRoleName(String role) {
    switch (role) {
      case 'leader': return 'Guruh sardori';
      case 'admin': return 'Administrator';
      case 'superadmin': return 'Super Admin';
      default: return 'Talaba';
    }
  }
}

class _DrawerItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color? color;
  final int? badge;
  final VoidCallback onTap;

  const _DrawerItem({required this.icon, required this.label, this.color, this.badge, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Stack(
        clipBehavior: Clip.none,
        children: [
          Icon(icon, color: color ?? AppColors.textSecondary, size: 22),
          if (badge != null)
            Positioned(
              right: -6,
              top: -4,
              child: Container(
                padding: const EdgeInsets.all(3),
                decoration: const BoxDecoration(color: AppColors.error, shape: BoxShape.circle),
                constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                child: Text(
                  badge! > 99 ? '99+' : badge.toString(),
                  style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
        ],
      ),
      title: Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
      dense: true,
      contentPadding: const EdgeInsets.symmetric(horizontal: 20),
      onTap: onTap,
    );
  }
}

class _NavItem {
  final String path;
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const _NavItem({
    required this.path,
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}

class _NavBarItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final int? badge;
  final VoidCallback onTap;

  const _NavBarItem({
    required this.icon,
    required this.label,
    required this.isSelected,
    this.badge,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOutCubic,
        padding: EdgeInsets.symmetric(
          horizontal: isSelected ? 18 : 14,
          vertical: 10,
        ),
        decoration: BoxDecoration(
          gradient: isSelected ? AppColors.primaryGradient : null,
          borderRadius: BorderRadius.circular(16),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : null,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Stack(
              clipBehavior: Clip.none,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  child: Icon(
                    icon,
                    color: isSelected ? Colors.white : AppColors.textTertiary,
                    size: isSelected ? 26 : 24,
                  ),
                ),
                if (badge != null)
                  Positioned(
                    right: -10,
                    top: -6,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [AppColors.error, AppColors.rose],
                        ),
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.error.withOpacity(0.4),
                            blurRadius: 6,
                          ),
                        ],
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Text(
                        badge! > 99 ? '99+' : badge.toString(),
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
            AnimatedSize(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeOutCubic,
              child: SizedBox(
                width: isSelected ? null : 0,
                child: AnimatedOpacity(
                  duration: const Duration(milliseconds: 200),
                  opacity: isSelected ? 1 : 0,
                  child: Padding(
                    padding: EdgeInsets.only(left: isSelected ? 10 : 0),
                    child: Text(
                      label,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.clip,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
