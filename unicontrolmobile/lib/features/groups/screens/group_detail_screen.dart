/// Group Detail Screen
/// Guruh tafsilotlari - talabalar ro'yxati bilan
library;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../services/api_service.dart';

class GroupDetailScreen extends StatefulWidget {
  final int groupId;

  const GroupDetailScreen({super.key, required this.groupId});

  @override
  State<GroupDetailScreen> createState() => _GroupDetailScreenState();
}

class _GroupDetailScreenState extends State<GroupDetailScreen> {
  final _apiService = ApiService();
  final _searchController = TextEditingController();

  Map<String, dynamic>? _group;
  List<dynamic> _students = [];
  List<dynamic> _filteredStudents = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadGroupData();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadGroupData() async {
    setState(() => _isLoading = true);
    try {
      final groupData = await _apiService.getGroupDetail(widget.groupId);
      final studentsData = await _apiService.getGroupStudents(widget.groupId);

      setState(() {
        _group = groupData;
        _students = (studentsData['items'] as List?) ?? studentsData is List ? studentsData as List : [];
        _filteredStudents = _students;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _filterStudents(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredStudents = _students;
      } else {
        _filteredStudents = _students.where((s) {
          final name = '${s['first_name'] ?? ''} ${s['last_name'] ?? ''}'.toLowerCase();
          return name.contains(query.toLowerCase());
        }).toList();
      }
    });
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
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [Color(0xFF5C6BC0), Color(0xFF3949AB)],
                        ),
                      ),
                      child: SafeArea(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(20, 60, 20, 20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: Colors.white.withOpacity(0.2),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: const Icon(Icons.group_rounded, color: Colors.white, size: 28),
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          _group?['name'] ?? 'Guruh',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 24,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        if (_group?['course'] != null)
                                          Text(
                                            '${_group!['course']}-kurs',
                                            style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 14),
                                          ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              // Stats
                              Row(
                                children: [
                                  _HeaderStat(icon: Icons.people, label: '${_students.length} talaba'),
                                  const SizedBox(width: 16),
                                  if (_group?['leader_name'] != null)
                                    _HeaderStat(icon: Icons.star, label: 'Sardor: ${_group!['leader_name']}'),
                                ],
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

                // Search
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 10)],
                      ),
                      child: TextField(
                        controller: _searchController,
                        onChanged: _filterStudents,
                        decoration: const InputDecoration(
                          hintText: 'Talaba qidirish...',
                          prefixIcon: Icon(Icons.search_rounded, color: AppColors.textSecondary),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                      ),
                    ),
                  ),
                ),

                // Count
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                    child: Text(
                      '${_filteredStudents.length} talaba topildi',
                      style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                    ),
                  ),
                ),

                // Students list
                if (_filteredStudents.isEmpty)
                  const SliverFillRemaining(
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.person_search_rounded, size: 64, color: AppColors.textTertiary),
                          SizedBox(height: 16),
                          Text('Talaba topilmadi', style: TextStyle(color: AppColors.textSecondary)),
                        ],
                      ),
                    ),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
                    sliver: SliverList(
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final student = _filteredStudents[index];
                          return _StudentCard(
                            student: student,
                            index: index + 1,
                            onTap: () {
                              final id = student['id'];
                              if (id != null) {
                                Navigator.pushNamed(context, '/students/$id');
                              }
                            },
                          );
                        },
                        childCount: _filteredStudents.length,
                      ),
                    ),
                  ),
              ],
            ),
    );
  }
}

class _HeaderStat extends StatelessWidget {
  final IconData icon;
  final String label;

  const _HeaderStat({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.white70),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(color: Colors.white70, fontSize: 13)),
      ],
    );
  }
}

class _StudentCard extends StatelessWidget {
  final dynamic student;
  final int index;
  final VoidCallback? onTap;

  const _StudentCard({required this.student, required this.index, this.onTap});

  @override
  Widget build(BuildContext context) {
    final firstName = student['first_name'] ?? '';
    final lastName = student['last_name'] ?? '';
    final fullName = '$firstName $lastName'.trim();
    final initial = fullName.isNotEmpty ? fullName[0].toUpperCase() : '?';
    final hemis = student['hemis_id'] ?? student['student_id'] ?? '';
    final phone = student['phone'] ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                // Number
                SizedBox(
                  width: 28,
                  child: Text(
                    '$index',
                    style: const TextStyle(
                      color: AppColors.textTertiary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ),
                // Avatar
                CircleAvatar(
                  radius: 22,
                  backgroundColor: AppColors.primary.withOpacity(0.1),
                  child: Text(
                    initial,
                    style: const TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        fullName,
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                      const SizedBox(height: 3),
                      Row(
                        children: [
                          if (hemis.toString().isNotEmpty) ...[
                            const Icon(Icons.badge_outlined, size: 13, color: AppColors.textTertiary),
                            const SizedBox(width: 4),
                            Text(
                              hemis.toString(),
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                            ),
                          ],
                          if (phone.toString().isNotEmpty) ...[
                            const SizedBox(width: 12),
                            const Icon(Icons.phone_outlined, size: 13, color: AppColors.textTertiary),
                            const SizedBox(width: 4),
                            Text(
                              phone.toString(),
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right_rounded, color: AppColors.textTertiary, size: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
