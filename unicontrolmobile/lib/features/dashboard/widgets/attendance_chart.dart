/// Attendance Chart Widget
/// Davomat diagrammasi
library;

import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../../core/theme/app_theme.dart';
import '../../../data/models/dashboard_stats_model.dart';

class AttendanceChartWidget extends StatelessWidget {
  final DashboardStats stats;

  const AttendanceChartWidget({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    final total = stats.todayTotal;
    if (total == 0) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Bugungi davomat',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              // Pie Chart
              SizedBox(
                width: 120,
                height: 120,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 2,
                    centerSpaceRadius: 30,
                    sections: [
                      PieChartSectionData(
                        value: stats.todayPresent.toDouble(),
                        color: AppTheme.presentColor,
                        title: '',
                        radius: 25,
                      ),
                      PieChartSectionData(
                        value: stats.todayAbsent.toDouble(),
                        color: AppTheme.absentColor,
                        title: '',
                        radius: 25,
                      ),
                      PieChartSectionData(
                        value: stats.todayLate.toDouble(),
                        color: AppTheme.lateColor,
                        title: '',
                        radius: 25,
                      ),
                      PieChartSectionData(
                        value: stats.todayExcused.toDouble(),
                        color: AppTheme.excusedColor,
                        title: '',
                        radius: 25,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 24),
              // Legend
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildLegendItem(
                      'Keldi',
                      stats.todayPresent,
                      total,
                      AppTheme.presentColor,
                    ),
                    const SizedBox(height: 8),
                    _buildLegendItem(
                      'Kelmadi',
                      stats.todayAbsent,
                      total,
                      AppTheme.absentColor,
                    ),
                    const SizedBox(height: 8),
                    _buildLegendItem(
                      'Kechikdi',
                      stats.todayLate,
                      total,
                      AppTheme.lateColor,
                    ),
                    const SizedBox(height: 8),
                    _buildLegendItem(
                      'Sababli',
                      stats.todayExcused,
                      total,
                      AppTheme.excusedColor,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, int value, int total, Color color) {
    final percentage = total > 0 ? (value / total * 100) : 0.0;

    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 13,
              color: AppTheme.textSecondary,
            ),
          ),
        ),
        Text(
          '$value',
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          '(${percentage.toStringAsFixed(0)}%)',
          style: const TextStyle(
            fontSize: 11,
            color: AppTheme.textTertiary,
          ),
        ),
      ],
    );
  }
}

