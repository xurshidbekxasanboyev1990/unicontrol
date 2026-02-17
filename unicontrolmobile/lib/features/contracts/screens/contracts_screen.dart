/// Contracts Screen
/// Kontrakt ma'lumotlari
library;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../services/api_service.dart';

class ContractsScreen extends StatefulWidget {
  const ContractsScreen({super.key});

  @override
  State<ContractsScreen> createState() => _ContractsScreenState();
}

class _ContractsScreenState extends State<ContractsScreen> with SingleTickerProviderStateMixin {
  final _apiService = ApiService();
  late TabController _tabController;

  Map<String, dynamic>? _myContract;
  Map<String, dynamic>? _groupContracts;
  bool _isLoading = true;
  bool _isLeader = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      _myContract = await _apiService.getMyContract();

      // Try group contracts (leader only)
      try {
        _groupContracts = await _apiService.getGroupContracts();
        _isLeader = (_groupContracts?['items'] as List?)?.isNotEmpty ?? false;
      } catch (_) {
        _isLeader = false;
      }

      setState(() => _isLoading = false);
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : CustomScrollView(
              slivers: [
                // Header
                SliverAppBar(
                  expandedHeight: 200,
                  pinned: true,
                  backgroundColor: Colors.transparent,
                  flexibleSpace: FlexibleSpaceBar(
                    background: Container(
                      decoration: const BoxDecoration(gradient: AppColors.primaryGradient),
                      child: SafeArea(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(20, 60, 20, 20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                '💰 Kontrakt',
                                style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 16),
                              if (_myContract?['has_contract'] == true) ...[
                                _buildProgressBar(),
                              ] else
                                const Text(
                                  'Kontrakt ma\'lumotlari mavjud emas',
                                  style: TextStyle(color: Colors.white70, fontSize: 14),
                                ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  leading: IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),

                // Tab Bar (if leader)
                if (_isLeader)
                  SliverToBoxAdapter(
                    child: Container(
                      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: TabBar(
                        controller: _tabController,
                        onTap: (i) => setState(() {}),
                        indicator: BoxDecoration(
                          gradient: AppColors.primaryGradient,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        indicatorSize: TabBarIndicatorSize.tab,
                        labelColor: Colors.white,
                        unselectedLabelColor: AppColors.textSecondary,
                        dividerHeight: 0,
                        tabs: const [
                          Tab(text: 'Mening kontraktim'),
                          Tab(text: 'Guruh'),
                        ],
                      ),
                    ),
                  ),

                // Content
                SliverToBoxAdapter(
                  child: _isLeader && _tabController.index == 1
                      ? _buildGroupContracts()
                      : _buildMyContract(),
                ),
              ],
            ),
    );
  }

  Widget _buildProgressBar() {
    final basic = _myContract?['basic'] ?? {};
    final percentage = (basic['contract_percentage'] ?? 0).toDouble();

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'To\'langan: ${_formatMoney(basic['contract_paid'] ?? 0)}',
              style: const TextStyle(color: Colors.white, fontSize: 13),
            ),
            Text(
              '${percentage.toStringAsFixed(1)}%',
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: LinearProgressIndicator(
            value: percentage / 100,
            minHeight: 10,
            backgroundColor: Colors.white.withOpacity(0.2),
            valueColor: const AlwaysStoppedAnimation(Colors.white),
          ),
        ),
        const SizedBox(height: 6),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Jami: ${_formatMoney(basic['contract_amount'] ?? 0)}',
              style: const TextStyle(color: Colors.white70, fontSize: 12),
            ),
            Text(
              'Qoldiq: ${_formatMoney(basic['contract_remaining'] ?? 0)}',
              style: const TextStyle(color: Colors.white70, fontSize: 12),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMyContract() {
    if (_myContract?['has_contract'] != true) {
      return const Padding(
        padding: EdgeInsets.all(40),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.receipt_long_outlined, size: 64, color: AppColors.textTertiary),
              SizedBox(height: 16),
              Text('Kontrakt topilmadi', style: TextStyle(color: AppColors.textSecondary, fontSize: 16)),
            ],
          ),
        ),
      );
    }

    final basic = _myContract!['basic'] ?? {};
    final contracts = (_myContract!['contracts'] as List?) ?? [];
    final student = _myContract!['student'] ?? {};

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Summary cards
          Row(
            children: [
              Expanded(child: _SummaryCard(
                label: 'Kontrakt',
                value: _formatMoney(basic['contract_amount'] ?? 0),
                icon: Icons.receipt_long_rounded,
                color: AppColors.info,
              )),
              const SizedBox(width: 12),
              Expanded(child: _SummaryCard(
                label: 'To\'langan',
                value: _formatMoney(basic['contract_paid'] ?? 0),
                icon: Icons.check_circle_rounded,
                color: AppColors.success,
              )),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _SummaryCard(
                label: 'Qoldiq',
                value: _formatMoney(basic['contract_remaining'] ?? 0),
                icon: Icons.pending_rounded,
                color: AppColors.warning,
              )),
              const SizedBox(width: 12),
              Expanded(child: _SummaryCard(
                label: 'Foiz',
                value: '${(basic['contract_percentage'] ?? 0).toStringAsFixed(1)}%',
                icon: Icons.pie_chart_rounded,
                color: AppColors.primary,
              )),
            ],
          ),

          // Contract history
          if (contracts.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Kontrakt tarixi',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
            ),
            const SizedBox(height: 12),
            ...contracts.map((c) => _ContractHistoryCard(contract: c)),
          ],
        ],
      ),
    );
  }

  Widget _buildGroupContracts() {
    final items = (_groupContracts?['items'] as List?) ?? [];
    final summary = _groupContracts?['summary'] ?? {};
    final groupName = _groupContracts?['group_name'] ?? '';

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Group summary
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(groupName, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _MiniStat(label: 'Talabalar', value: '${summary['total_students'] ?? 0}'),
                    _MiniStat(label: 'To\'langan', value: '${summary['fully_paid'] ?? 0}', color: AppColors.success),
                    _MiniStat(label: 'Qarzdor', value: '${summary['with_debt'] ?? 0}', color: AppColors.error),
                    _MiniStat(label: 'Foiz', value: '${(summary['payment_rate'] ?? 0).toStringAsFixed(0)}%'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Students list
          ...items.map((s) => Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: s['is_paid'] == true
                  ? Border.all(color: AppColors.success.withOpacity(0.3))
                  : Border.all(color: AppColors.error.withOpacity(0.2)),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: s['is_paid'] == true ? AppColors.successLight : AppColors.errorLight,
                  child: Icon(
                    s['is_paid'] == true ? Icons.check_rounded : Icons.warning_rounded,
                    color: s['is_paid'] == true ? AppColors.success : AppColors.error,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(s['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      const SizedBox(height: 4),
                      Text(
                        'Qarz: ${_formatMoney(s['debt'] ?? 0)}',
                        style: TextStyle(
                          fontSize: 12,
                          color: (s['debt'] ?? 0) > 0 ? AppColors.error : AppColors.success,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  '${(s['percentage'] ?? 0).toStringAsFixed(0)}%',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: (s['percentage'] ?? 0) >= 100 ? AppColors.success : AppColors.warning,
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  String _formatMoney(dynamic amount) {
    final num val = amount is num ? amount : 0;
    if (val >= 1000000) {
      return '${(val / 1000000).toStringAsFixed(1)} mln';
    } else if (val >= 1000) {
      return '${(val / 1000).toStringAsFixed(0)} ming';
    }
    return val.toStringAsFixed(0);
  }
}

class _SummaryCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _SummaryCard({required this.label, required this.value, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 18),
              ),
              const Spacer(),
            ],
          ),
          const SizedBox(height: 10),
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        ],
      ),
    );
  }
}

class _ContractHistoryCard extends StatelessWidget {
  final dynamic contract;

  const _ContractHistoryCard({required this.contract});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.calendar_today_rounded, size: 16, color: AppColors.textSecondary),
              const SizedBox(width: 8),
              Text(
                contract['academic_year'] ?? '',
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.infoLight,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${contract['course'] ?? ''}-kurs',
                  style: const TextStyle(fontSize: 11, color: AppColors.info, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          _InfoRow('Kontrakt', '${(contract['contract_amount'] ?? 0).toStringAsFixed(0)} so\'m'),
          _InfoRow('To\'langan', '${(contract['total_paid'] ?? 0).toStringAsFixed(0)} so\'m'),
          _InfoRow('Grant', '${(contract['grant_percentage'] ?? 0).toStringAsFixed(0)}%'),
          _InfoRow('Qarz', '${(contract['debt_amount'] ?? 0).toStringAsFixed(0)} so\'m'),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;

  const _MiniStat({required this.label, required this.value, this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color ?? AppColors.textPrimary)),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
      ],
    );
  }
}
