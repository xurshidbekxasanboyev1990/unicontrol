/// Student Detail Screen
/// Talaba tafsilotlari
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../../../data/models/student_model.dart';
import '../../../services/api_service.dart';

class StudentDetailScreen extends ConsumerStatefulWidget {
  final int studentId;

  const StudentDetailScreen({super.key, required this.studentId});

  @override
  ConsumerState<StudentDetailScreen> createState() =>
      _StudentDetailScreenState();
}

class _StudentDetailScreenState extends ConsumerState<StudentDetailScreen> {
  Student? _student;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadStudent();
  }

  Future<void> _loadStudent() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final student = await apiService.getStudent(widget.studentId);
      setState(() {
        _student = student;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 48,
                        color: AppTheme.errorColor,
                      ),
                      const SizedBox(height: 8),
                      Text(_error!),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadStudent,
                        child: const Text('Qayta urinish'),
                      ),
                    ],
                  ),
                )
              : _student != null
                  ? _buildContent()
                  : const Center(child: Text('Talaba topilmadi')),
    );
  }

  Widget _buildContent() {
    final student = _student!;

    return CustomScrollView(
      slivers: [
        // Header
        SliverAppBar(
          expandedHeight: 220,
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
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.2),
                            blurRadius: 15,
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          student.initials,
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryColor,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      student.name,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      student.studentId,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white.withValues(alpha: 0.8),
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
              // Status card
              _buildStatusCard(student),
              const SizedBox(height: 16),

              // Personal info
              _buildSectionTitle('Shaxsiy ma\'lumotlar'),
              const SizedBox(height: 8),
              _buildInfoCard([
                if (student.groupName != null)
                  _InfoItem(
                    icon: Icons.group_outlined,
                    label: 'Guruh',
                    value: student.groupName!,
                  ),
                if (student.phone != null)
                  _InfoItem(
                    icon: Icons.phone_outlined,
                    label: 'Telefon',
                    value: student.phone!,
                  ),
                if (student.email != null)
                  _InfoItem(
                    icon: Icons.email_outlined,
                    label: 'Email',
                    value: student.email!,
                  ),
                if (student.address != null)
                  _InfoItem(
                    icon: Icons.location_on_outlined,
                    label: 'Manzil',
                    value: student.address!,
                  ),
                if (student.birthDate != null)
                  _InfoItem(
                    icon: Icons.cake_outlined,
                    label: 'Tug\'ilgan sana',
                    value: student.birthDate!.toDisplayDate(),
                  ),
              ]),

              const SizedBox(height: 16),

              // Contract info
              if (student.contractAmount != null &&
                  student.contractAmount! > 0) ...[
                _buildSectionTitle('Kontrakt ma\'lumotlari'),
                const SizedBox(height: 8),
                _buildContractCard(student),
              ],

              const SizedBox(height: 80),
            ]),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusCard(Student student) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Row(
        children: [
          _buildStatusItem(
            'Holat',
            student.isActive ? 'Faol' : 'Nofaol',
            student.isActive ? AppTheme.successColor : AppTheme.textTertiary,
          ),
          Container(
            width: 1,
            height: 40,
            color: AppTheme.borderColor,
          ),
          _buildStatusItem(
            'O\'qish',
            student.isGraduated ? 'Bitirgan' : 'Davom etmoqda',
            student.isGraduated ? AppTheme.primaryColor : AppTheme.infoColor,
          ),
          Container(
            width: 1,
            height: 40,
            color: AppTheme.borderColor,
          ),
          _buildStatusItem(
            'Kontrakt',
            student.isContractPaid ? 'To\'langan' : 'Qarz bor',
            student.isContractPaid
                ? AppTheme.successColor
                : AppTheme.warningColor,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusItem(String label, String value, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.textTertiary,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: AppTheme.textPrimary,
      ),
    );
  }

  Widget _buildInfoCard(List<_InfoItem> items) {
    if (items.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.borderColor),
        ),
        child: const Center(
          child: Text(
            'Ma\'lumot yo\'q',
            style: TextStyle(color: AppTheme.textTertiary),
          ),
        ),
      );
    }

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
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        item.icon,
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
                            item.label,
                            style: const TextStyle(
                              color: AppTheme.textTertiary,
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            item.value,
                            style: const TextStyle(
                              fontWeight: FontWeight.w500,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              if (!isLast) const Divider(height: 1, indent: 68),
            ],
          );
        }).toList(),
      ),
    );
  }

  Widget _buildContractCard(Student student) {
    final paid = student.contractPaid ?? 0;
    final total = student.contractAmount ?? 0;
    final remaining = student.contractRemaining;
    final percentage = student.contractPercentage;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        children: [
          // Progress bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'To\'langan: ${percentage.toStringAsFixed(1)}%',
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                paid.toCurrency(),
                style: const TextStyle(
                  color: AppTheme.successColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: percentage / 100,
              backgroundColor: AppTheme.borderColor,
              valueColor: AlwaysStoppedAnimation<Color>(
                percentage >= 100 ? AppTheme.successColor : AppTheme.primaryColor,
              ),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildContractItem(
                  'Jami',
                  total.toCurrency(),
                  AppTheme.textPrimary,
                ),
              ),
              Expanded(
                child: _buildContractItem(
                  'Qoldi',
                  remaining.toCurrency(),
                  remaining > 0 ? AppTheme.warningColor : AppTheme.successColor,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildContractItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: const TextStyle(
            color: AppTheme.textTertiary,
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ],
    );
  }
}

class _InfoItem {
  final IconData icon;
  final String label;
  final String value;

  const _InfoItem({
    required this.icon,
    required this.label,
    required this.value,
  });
}

