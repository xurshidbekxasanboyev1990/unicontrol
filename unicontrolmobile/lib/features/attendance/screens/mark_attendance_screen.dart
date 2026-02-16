/// Mark Attendance Screen
/// Davomat olish ekrani (Leader/Admin uchun)
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/constants/app_constants.dart';
import '../../../data/providers/auth_provider.dart';
import '../../../data/providers/data_provider.dart';
import '../../../data/models/student_model.dart';
import '../../../services/api_service.dart';

class MarkAttendanceScreen extends ConsumerStatefulWidget {
  final int? groupId;

  const MarkAttendanceScreen({super.key, this.groupId});

  @override
  ConsumerState<MarkAttendanceScreen> createState() =>
      _MarkAttendanceScreenState();
}

class _MarkAttendanceScreenState extends ConsumerState<MarkAttendanceScreen> {
  DateTime _selectedDate = DateTime.now();
  List<Student> _students = [];
  Map<int, AttendanceStatus> _attendanceMap = {};
  bool _isLoading = false;
  bool _isSaving = false;
  int? _selectedGroupId;

  @override
  void initState() {
    super.initState();
    _selectedGroupId = widget.groupId;
    _loadData();
  }

  Future<void> _loadData() async {
    final user = ref.read(currentUserProvider);

    // Agar sardor bo'lsa, o'z guruhini yuklash
    if (user?.isLeader == true && user?.groupId != null) {
      _selectedGroupId = user!.groupId;
    }

    // Guruhlar ro'yxatini yuklash
    await ref.read(groupsProvider.notifier).fetchGroups();

    if (_selectedGroupId != null) {
      await _loadStudents();
    }
  }

  Future<void> _loadStudents() async {
    if (_selectedGroupId == null) return;

    setState(() => _isLoading = true);

    try {
      final students = await apiService.getGroupStudents(_selectedGroupId!);
      setState(() {
        _students = students;
        // Barchani "keldi" qilib belgilash
        _attendanceMap = {
          for (var student in students)
            student.id: AttendanceStatus.present
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Xatolik: $e')),
        );
      }
    }
  }

  void _updateStatus(int studentId, AttendanceStatus status) {
    setState(() {
      _attendanceMap[studentId] = status;
    });
  }

  Future<void> _saveAttendance() async {
    if (_students.isEmpty) return;

    setState(() => _isSaving = true);

    try {
      final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);
      final records = _attendanceMap.entries.map((entry) {
        return {
          'student_id': entry.key,
          'date': dateStr,
          'status': entry.value.value,
        };
      }).toList();

      await apiService.markAttendance(records);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Davomat muvaffaqiyatli saqlandi!'),
            backgroundColor: AppTheme.successColor,
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Xatolik: $e'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    }

    setState(() => _isSaving = false);
  }

  void _markAll(AttendanceStatus status) {
    setState(() {
      for (var student in _students) {
        _attendanceMap[student.id] = status;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final groupsState = ref.watch(groupsProvider);
    final user = ref.watch(currentUserProvider);
    final isLeader = user?.isLeader == true;

    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      appBar: AppBar(
        title: const Text('Davomat olish'),
        backgroundColor: AppTheme.backgroundLight,
        actions: [
          if (_students.isNotEmpty)
            PopupMenuButton<AttendanceStatus>(
              icon: const Icon(Icons.more_vert),
              onSelected: _markAll,
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: AttendanceStatus.present,
                  child: Row(
                    children: [
                      Icon(Icons.check_circle, color: AppTheme.presentColor),
                      SizedBox(width: 8),
                      Text('Barchasini "Keldi"'),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: AttendanceStatus.absent,
                  child: Row(
                    children: [
                      Icon(Icons.cancel, color: AppTheme.absentColor),
                      SizedBox(width: 8),
                      Text('Barchasini "Kelmadi"'),
                    ],
                  ),
                ),
              ],
            ),
        ],
      ),
      body: Column(
        children: [
          // Date and Group Selector
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Column(
              children: [
                // Date
                GestureDetector(
                  onTap: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _selectedDate,
                      firstDate: DateTime(2024),
                      lastDate: DateTime.now(),
                    );
                    if (picked != null) {
                      setState(() => _selectedDate = picked);
                    }
                  },
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      border: Border.all(color: AppTheme.borderColor),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.calendar_today,
                          color: AppTheme.primaryColor,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          DateFormat('d MMMM, yyyy').format(_selectedDate),
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const Spacer(),
                        const Icon(
                          Icons.arrow_drop_down,
                          color: AppTheme.textSecondary,
                        ),
                      ],
                    ),
                  ),
                ),

                // Group selector (only for admin)
                if (!isLeader) ...[
                  const SizedBox(height: 12),
                  DropdownButtonFormField<int>(
                    value: _selectedGroupId,
                    decoration: InputDecoration(
                      labelText: 'Guruhni tanlang',
                      prefixIcon: const Icon(Icons.group),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    items: groupsState.groups.map((group) {
                      return DropdownMenuItem(
                        value: group.id,
                        child: Text(group.name),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() => _selectedGroupId = value);
                      _loadStudents();
                    },
                  ),
                ],
              ],
            ),
          ),

          // Stats bar
          if (_students.isNotEmpty) _buildStatsBar(),

          // Students list
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _students.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.people_outline,
                              size: 64,
                              color: AppTheme.textTertiary.withValues(alpha: 0.5),
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'Guruhni tanlang',
                              style: TextStyle(
                                color: AppTheme.textSecondary,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _students.length,
                        itemBuilder: (context, index) {
                          final student = _students[index];
                          final status = _attendanceMap[student.id] ??
                              AttendanceStatus.present;
                          return _buildStudentCard(student, status);
                        },
                      ),
          ),
        ],
      ),
      bottomNavigationBar: _students.isNotEmpty
          ? Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    offset: const Offset(0, -5),
                  ),
                ],
              ),
              child: SafeArea(
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _isSaving ? null : _saveAttendance,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isSaving
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Text(
                            'Saqlash',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),
              ),
            )
          : null,
    );
  }

  Widget _buildStatsBar() {
    final present =
        _attendanceMap.values.where((s) => s == AttendanceStatus.present).length;
    final absent =
        _attendanceMap.values.where((s) => s == AttendanceStatus.absent).length;
    final late =
        _attendanceMap.values.where((s) => s == AttendanceStatus.late).length;
    final excused =
        _attendanceMap.values.where((s) => s == AttendanceStatus.excused).length;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.white,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildMiniStat('✅ $present', AppTheme.presentColor),
          _buildMiniStat('❌ $absent', AppTheme.absentColor),
          _buildMiniStat('⏰ $late', AppTheme.lateColor),
          _buildMiniStat('📋 $excused', AppTheme.excusedColor),
        ],
      ),
    );
  }

  Widget _buildMiniStat(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildStudentCard(Student student, AttendanceStatus status) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(
                student.initials,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),

          // Name
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  student.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                Text(
                  student.studentId,
                  style: const TextStyle(
                    color: AppTheme.textTertiary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),

          // Status buttons
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildStatusButton(
                student.id,
                AttendanceStatus.present,
                status,
                '✅',
              ),
              _buildStatusButton(
                student.id,
                AttendanceStatus.absent,
                status,
                '❌',
              ),
              _buildStatusButton(
                student.id,
                AttendanceStatus.late,
                status,
                '⏰',
              ),
              _buildStatusButton(
                student.id,
                AttendanceStatus.excused,
                status,
                '📋',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusButton(
    int studentId,
    AttendanceStatus buttonStatus,
    AttendanceStatus currentStatus,
    String emoji,
  ) {
    final isSelected = buttonStatus == currentStatus;

    return GestureDetector(
      onTap: () => _updateStatus(studentId, buttonStatus),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        width: 36,
        height: 36,
        margin: const EdgeInsets.only(left: 4),
        decoration: BoxDecoration(
          color: isSelected
              ? _getStatusColor(buttonStatus).withValues(alpha: 0.2)
              : Colors.grey.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
          border: isSelected
              ? Border.all(color: _getStatusColor(buttonStatus), width: 2)
              : null,
        ),
        child: Center(
          child: Text(
            emoji,
            style: TextStyle(
              fontSize: isSelected ? 18 : 14,
            ),
          ),
        ),
      ),
    );
  }

  Color _getStatusColor(AttendanceStatus status) {
    switch (status) {
      case AttendanceStatus.present:
        return AppTheme.presentColor;
      case AttendanceStatus.absent:
        return AppTheme.absentColor;
      case AttendanceStatus.late:
        return AppTheme.lateColor;
      case AttendanceStatus.excused:
        return AppTheme.excusedColor;
    }
  }
}

