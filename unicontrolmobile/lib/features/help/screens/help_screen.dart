/// Help / FAQ Screen
/// Yordam markazi
library;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../services/api_service.dart';

class HelpScreen extends StatefulWidget {
  const HelpScreen({super.key});

  @override
  State<HelpScreen> createState() => _HelpScreenState();
}

class _HelpScreenState extends State<HelpScreen> {
  final _apiService = ApiService();
  final _searchController = TextEditingController();

  List<dynamic> _faqs = [];
  List<dynamic> _filteredFaqs = [];
  String _selectedCategory = 'all';
  bool _isLoading = true;
  final Set<int> _expandedItems = {};

  final List<Map<String, dynamic>> _categories = [
    {'id': 'all', 'name': 'Barchasi', 'icon': Icons.list_rounded},
    {'id': 'general', 'name': 'Umumiy', 'icon': Icons.info_rounded},
    {'id': 'attendance', 'name': 'Davomat', 'icon': Icons.fact_check_rounded},
    {'id': 'schedule', 'name': 'Jadval', 'icon': Icons.calendar_today_rounded},
    {'id': 'library', 'name': 'Kutubxona', 'icon': Icons.menu_book_rounded},
    {'id': 'canteen', 'name': 'Oshxona', 'icon': Icons.restaurant_rounded},
    {'id': 'contract', 'name': 'Kontrakt', 'icon': Icons.receipt_long_rounded},
    {'id': 'clubs', 'name': 'Klublar', 'icon': Icons.emoji_events_rounded},
    {'id': 'notifications', 'name': 'Bildirishnomalar', 'icon': Icons.notifications_rounded},
    {'id': 'technical', 'name': 'Texnik', 'icon': Icons.settings_rounded},
  ];

  @override
  void initState() {
    super.initState();
    _loadFaqs();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadFaqs() async {
    setState(() => _isLoading = true);
    try {
      final data = await _apiService.getFAQ();
      setState(() {
        _faqs = (data['items'] as List?) ?? [];
        _filteredFaqs = _faqs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _filterFaqs() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      _filteredFaqs = _faqs.where((faq) {
        final matchCategory = _selectedCategory == 'all' || faq['category'] == _selectedCategory;
        final matchSearch = query.isEmpty ||
            (faq['question'] ?? '').toLowerCase().contains(query) ||
            (faq['answer'] ?? '').toLowerCase().contains(query);
        return matchCategory && matchSearch;
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          // Header
          SliverAppBar(
            expandedHeight: 160,
            pinned: true,
            backgroundColor: Colors.transparent,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF00BFA5), Color(0xFF00897B)],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 50, 20, 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.help_outline_rounded, color: Colors.white, size: 28),
                            const SizedBox(width: 10),
                            const Text(
                              'Yordam markazi',
                              style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          '${_faqs.length} ta savol-javob',
                          style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 14),
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
                  onChanged: (_) => _filterFaqs(),
                  decoration: InputDecoration(
                    hintText: 'Savol qidirish...',
                    hintStyle: TextStyle(color: AppColors.textTertiary),
                    prefixIcon: const Icon(Icons.search_rounded, color: AppColors.textSecondary),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.close_rounded, size: 20),
                            onPressed: () {
                              _searchController.clear();
                              _filterFaqs();
                            },
                          )
                        : null,
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  ),
                ),
              ),
            ),
          ),

          // Categories
          SliverToBoxAdapter(
            child: SizedBox(
              height: 50,
              child: ListView.builder(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                scrollDirection: Axis.horizontal,
                itemCount: _categories.length,
                itemBuilder: (context, index) {
                  final cat = _categories[index];
                  final isSelected = cat['id'] == _selectedCategory;
                  return GestureDetector(
                    onTap: () {
                      _selectedCategory = cat['id'];
                      _filterFaqs();
                    },
                    child: Container(
                      margin: const EdgeInsets.only(right: 8),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        gradient: isSelected
                            ? const LinearGradient(colors: [Color(0xFF00BFA5), Color(0xFF00897B)])
                            : null,
                        color: isSelected ? null : Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: isSelected ? null : Border.all(color: AppColors.border),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(cat['icon'] as IconData, size: 16, color: isSelected ? Colors.white : AppColors.textSecondary),
                          const SizedBox(width: 6),
                          Text(
                            cat['name'],
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: isSelected ? Colors.white : AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),

          // FAQ List
          if (_isLoading)
            const SliverFillRemaining(child: Center(child: CircularProgressIndicator(color: Color(0xFF00BFA5))))
          else if (_filteredFaqs.isEmpty)
            SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.help_outline_rounded, size: 64, color: AppColors.textTertiary),
                    const SizedBox(height: 16),
                    const Text('Savol topilmadi', style: TextStyle(color: AppColors.textSecondary, fontSize: 16)),
                    const SizedBox(height: 8),
                    Text(
                      'Boshqa kalit so\'z bilan qidiring',
                      style: TextStyle(color: AppColors.textTertiary, fontSize: 13),
                    ),
                  ],
                ),
              ),
            )
          else
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final faq = _filteredFaqs[index];
                    final faqId = faq['id'] ?? index;
                    final isExpanded = _expandedItems.contains(faqId);

                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: isExpanded
                            ? Border.all(color: const Color(0xFF00BFA5).withOpacity(0.3), width: 1.5)
                            : null,
                        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
                      ),
                      child: Material(
                        color: Colors.transparent,
                        borderRadius: BorderRadius.circular(14),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(14),
                          onTap: () {
                            setState(() {
                              if (isExpanded) {
                                _expandedItems.remove(faqId);
                              } else {
                                _expandedItems.add(faqId);
                              }
                            });
                          },
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF00BFA5).withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: const Icon(
                                        Icons.help_outline_rounded,
                                        color: Color(0xFF00BFA5),
                                        size: 18,
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Text(
                                        faq['question'] ?? '',
                                        style: const TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w600,
                                          color: AppColors.textPrimary,
                                        ),
                                      ),
                                    ),
                                    AnimatedRotation(
                                      turns: isExpanded ? 0.5 : 0,
                                      duration: const Duration(milliseconds: 200),
                                      child: const Icon(
                                        Icons.keyboard_arrow_down_rounded,
                                        color: AppColors.textSecondary,
                                      ),
                                    ),
                                  ],
                                ),
                                if (isExpanded) ...[
                                  const Divider(height: 24),
                                  Text(
                                    faq['answer'] ?? '',
                                    style: const TextStyle(
                                      fontSize: 13,
                                      height: 1.6,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF00BFA5).withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Text(
                                          _getCategoryName(faq['category']),
                                          style: const TextStyle(fontSize: 11, color: Color(0xFF00BFA5), fontWeight: FontWeight.w600),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ],
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                  childCount: _filteredFaqs.length,
                ),
              ),
            ),
        ],
      ),
    );
  }

  String _getCategoryName(String? id) {
    return _categories.firstWhere(
      (c) => c['id'] == id,
      orElse: () => {'name': 'Umumiy'},
    )['name'];
  }
}
