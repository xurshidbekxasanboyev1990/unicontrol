/// Tournaments Screen
/// Turnirlar ekrani
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../../../data/providers/data_provider.dart';
import '../../../data/models/tournament_model.dart';
import '../../../services/api_service.dart';

class TournamentsScreen extends ConsumerStatefulWidget {
  const TournamentsScreen({super.key});

  @override
  ConsumerState<TournamentsScreen> createState() => _TournamentsScreenState();
}

class _TournamentsScreenState extends ConsumerState<TournamentsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  List<Tournament> _filterTournaments(List<Tournament> all, int tabIndex) {
    switch (tabIndex) {
      case 0: // Faol (upcoming + ongoing)
        return all.where((t) => t.status == 'upcoming' || t.status == 'ongoing').toList();
      case 1: // Tugallangan
        return all.where((t) => t.status == 'completed' || t.status == 'cancelled').toList();
      default: // Barchasi
        return all;
    }
  }

  @override
  Widget build(BuildContext context) {
    final tournamentsAsync = ref.watch(tournamentsProvider);

    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      appBar: AppBar(
        title: const Text('Turnirlar'),
        backgroundColor: AppTheme.backgroundLight,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primaryColor,
          labelColor: AppTheme.primaryColor,
          unselectedLabelColor: AppTheme.textSecondary,
          indicatorWeight: 3,
          tabs: const [
            Tab(text: 'Faol'),
            Tab(text: 'Tugallangan'),
            Tab(text: 'Barchasi'),
          ],
        ),
      ),
      body: tournamentsAsync.when(
        data: (tournaments) {
          final filtered = _filterTournaments(tournaments, _tabController.index);

          if (filtered.isEmpty) {
            return _buildEmptyState(_tabController.index);
          }

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(tournamentsProvider);
            },
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                return _buildTournamentCard(context, ref, filtered[index]);
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 48,
                color: AppTheme.errorColor,
              ),
              const SizedBox(height: 8),
              Text('Xatolik: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(tournamentsProvider),
                child: const Text('Qayta urinish'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState([int tabIndex = 0]) {
    final messages = [
      ['Faol turnirlar yo\'q', 'Yangi turnirlar tez orada e\'lon qilinadi'],
      ['Tugallangan turnirlar yo\'q', 'Hali birorta turnir tugallanmagan'],
      ['Turnirlar yo\'q', 'Yangi turnirlar tez orada e\'lon qilinadi'],
    ];
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: AppTheme.warningColor.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.emoji_events_outlined,
              size: 48,
              color: AppTheme.warningColor,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            messages[tabIndex][0],
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            messages[tabIndex][1],
            style: const TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildTournamentCard(
      BuildContext context, WidgetRef ref, Tournament tournament) {
    final statusColor = _getStatusColor(tournament.status);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderColor),
        boxShadow: [
          BoxShadow(
            color: statusColor.withValues(alpha: 0.08),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  AppTheme.warningColor,
                  AppTheme.warningColor.withValues(alpha: 0.7),
                ],
              ),
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(20),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.emoji_events,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        tournament.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          tournament.statusLabel,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Content
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (tournament.description != null) ...[
                  Text(
                    tournament.description!,
                    style: const TextStyle(
                      color: AppTheme.textSecondary,
                      fontSize: 14,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 16),
                ],

                // Info
                Wrap(
                  spacing: 16,
                  runSpacing: 8,
                  children: [
                    if (tournament.startDate != null)
                      _buildInfoItem(
                        Icons.calendar_today,
                        tournament.startDate!.toDisplayDate(),
                      ),
                    _buildInfoItem(
                      Icons.people,
                      '${tournament.participantCount}/${tournament.maxParticipants > 0 ? tournament.maxParticipants : '∞'}',
                    ),
                  ],
                ),

                if (tournament.prize != null) ...[
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(
                        Icons.stars,
                        size: 18,
                        color: AppTheme.warningColor,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Sovrin: ${tournament.prize}',
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: AppTheme.warningColor,
                        ),
                      ),
                    ],
                  ),
                ],

                const SizedBox(height: 16),

                // Register button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: tournament.canRegister
                        ? () async {
                            try {
                              await apiService
                                  .registerForTournament(tournament.id);
                              ref.invalidate(tournamentsProvider);
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                        'Turnirga ro\'yxatdan o\'tdingiz!'),
                                    backgroundColor: AppTheme.successColor,
                                  ),
                                );
                              }
                            } catch (e) {
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('Xatolik: $e'),
                                    backgroundColor: AppTheme.errorColor,
                                  ),
                                );
                              }
                            }
                          }
                        : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: tournament.isRegistered
                          ? AppTheme.successColor
                          : tournament.canRegister
                              ? AppTheme.primaryColor
                              : AppTheme.textTertiary,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      tournament.isRegistered
                          ? 'Ro\'yxatdan o\'tgansiz ✓'
                          : tournament.canRegister
                              ? 'Ro\'yxatdan o\'tish'
                              : tournament.status == 'completed'
                                  ? 'Tugallangan'
                                  : tournament.status == 'cancelled'
                                      ? 'Bekor qilingan'
                                      : (tournament.maxParticipants > 0 && tournament.participantCount >= tournament.maxParticipants)
                                          ? 'Joylar to\'lgan'
                                          : (tournament.registrationDeadline != null && DateTime.now().isAfter(tournament.registrationDeadline!))
                                              ? 'Muddat tugagan'
                                              : 'Ro\'yxatdan o\'tish',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppTheme.textTertiary),
        const SizedBox(width: 6),
        Text(
          text,
          style: const TextStyle(
            color: AppTheme.textSecondary,
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'ongoing':
        return AppTheme.successColor;
      case 'upcoming':
        return AppTheme.infoColor;
      case 'completed':
        return AppTheme.textTertiary;
      case 'cancelled':
        return AppTheme.errorColor;
      default:
        return AppTheme.primaryColor;
    }
  }
}

