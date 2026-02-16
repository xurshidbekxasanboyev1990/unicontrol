/// Settings Screen
/// Sozlamalar ekrani
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_theme.dart';
import '../../../data/providers/auth_provider.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _darkMode = false;
  String _selectedLanguage = 'uz';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      appBar: AppBar(
        title: const Text('Sozlamalar'),
        backgroundColor: AppTheme.backgroundLight,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Account section
          _buildSectionTitle('Hisob'),
          _buildSettingsCard([
            _buildSettingsItem(
              icon: Icons.lock_outline,
              title: 'Parolni o\'zgartirish',
              onTap: () => _showChangePasswordDialog(),
            ),
          ]),

          const SizedBox(height: 24),

          // Notifications section
          _buildSectionTitle('Bildirishnomalar'),
          _buildSettingsCard([
            _buildSwitchItem(
              icon: Icons.notifications_outlined,
              title: 'Push bildirishnomalar',
              value: _notificationsEnabled,
              onChanged: (value) {
                setState(() => _notificationsEnabled = value);
              },
            ),
          ]),

          const SizedBox(height: 24),

          // Appearance section
          _buildSectionTitle('Ko\'rinish'),
          _buildSettingsCard([
            _buildSwitchItem(
              icon: Icons.dark_mode_outlined,
              title: 'Tungi rejim',
              subtitle: 'Tez orada',
              value: _darkMode,
              onChanged: null, // Disabled for now
            ),
            _buildDivider(),
            _buildDropdownItem(
              icon: Icons.language,
              title: 'Til',
              value: _selectedLanguage,
              items: const [
                DropdownMenuItem(value: 'uz', child: Text('O\'zbek')),
                DropdownMenuItem(value: 'ru', child: Text('Русский')),
                DropdownMenuItem(value: 'en', child: Text('English')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _selectedLanguage = value);
                }
              },
            ),
          ]),

          const SizedBox(height: 24),

          // About section
          _buildSectionTitle('Ilova haqida'),
          _buildSettingsCard([
            _buildSettingsItem(
              icon: Icons.info_outline,
              title: 'Versiya',
              trailing: const Text(
                '1.0.0',
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            ),
            _buildDivider(),
            _buildSettingsItem(
              icon: Icons.description_outlined,
              title: 'Foydalanish shartlari',
              onTap: () {
                // TODO: Show terms
              },
            ),
            _buildDivider(),
            _buildSettingsItem(
              icon: Icons.privacy_tip_outlined,
              title: 'Maxfiylik siyosati',
              onTap: () {
                // TODO: Show privacy policy
              },
            ),
          ]),

          const SizedBox(height: 32),

          // Developer info
          Center(
            child: Column(
              children: [
                Text(
                  'UniControl Mobile',
                  style: TextStyle(
                    color: AppTheme.textTertiary.withValues(alpha: 0.7),
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '© 2026 UniControl Team',
                  style: TextStyle(
                    color: AppTheme.textTertiary.withValues(alpha: 0.5),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppTheme.textSecondary,
        ),
      ),
    );
  }

  Widget _buildSettingsCard(List<Widget> children) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(children: children),
    );
  }

  Widget _buildSettingsItem({
    required IconData icon,
    required String title,
    String? subtitle,
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: AppTheme.primaryColor, size: 20),
      ),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.w500),
      ),
      subtitle: subtitle != null
          ? Text(subtitle, style: const TextStyle(fontSize: 12))
          : null,
      trailing: trailing ??
          (onTap != null
              ? const Icon(Icons.chevron_right, color: AppTheme.textTertiary)
              : null),
      onTap: onTap,
    );
  }

  Widget _buildSwitchItem({
    required IconData icon,
    required String title,
    String? subtitle,
    required bool value,
    required ValueChanged<bool>? onChanged,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: AppTheme.primaryColor, size: 20),
      ),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.w500),
      ),
      subtitle: subtitle != null
          ? Text(subtitle, style: const TextStyle(fontSize: 12))
          : null,
      trailing: Switch(
        value: value,
        onChanged: onChanged,
        activeTrackColor: AppTheme.primaryColor.withValues(alpha: 0.5),
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return AppTheme.primaryColor;
          }
          return null;
        }),
      ),
    );
  }

  Widget _buildDropdownItem<T>({
    required IconData icon,
    required String title,
    required T value,
    required List<DropdownMenuItem<T>> items,
    required ValueChanged<T?>? onChanged,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: AppTheme.primaryColor, size: 20),
      ),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.w500),
      ),
      trailing: DropdownButton<T>(
        value: value,
        items: items,
        onChanged: onChanged,
        underline: const SizedBox.shrink(),
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(height: 1, indent: 68);
  }

  void _showChangePasswordDialog() {
    final currentPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final confirmPasswordController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: const Text('Parolni o\'zgartirish'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: currentPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Joriy parol',
                prefixIcon: Icon(Icons.lock_outline),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: newPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Yangi parol',
                prefixIcon: Icon(Icons.lock_outline),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: confirmPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Parolni tasdiqlang',
                prefixIcon: Icon(Icons.lock_outline),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Bekor qilish'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (newPasswordController.text !=
                  confirmPasswordController.text) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Parollar mos kelmadi'),
                    backgroundColor: AppTheme.errorColor,
                  ),
                );
                return;
              }

              final success =
                  await ref.read(authProvider.notifier).changePassword(
                        currentPasswordController.text,
                        newPasswordController.text,
                      );

              if (context.mounted) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      success
                          ? 'Parol muvaffaqiyatli o\'zgartirildi'
                          : 'Parolni o\'zgartirishda xatolik',
                    ),
                    backgroundColor:
                        success ? AppTheme.successColor : AppTheme.errorColor,
                  ),
                );
              }
            },
            child: const Text('Saqlash'),
          ),
        ],
      ),
    );
  }
}

