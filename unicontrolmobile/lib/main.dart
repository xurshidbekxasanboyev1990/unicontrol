/// UniControl Mobile - Main Entry Point
/// Asosiy ilova kirish nuqtasi
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/date_symbol_data_local.dart';

import 'core/router.dart';
import 'core/theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Locale ma'lumotlarini ishga tushirish
  await initializeDateFormatting('uz_UZ', null);
  await initializeDateFormatting('ru_RU', null);
  await initializeDateFormatting('en_US', null);

  // Status bar rangini sozlash
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      statusBarBrightness: Brightness.light,
      systemNavigationBarColor: AppTheme.surfaceLight,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  // Ekran oriyentatsiyasini sozlash
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(
    const ProviderScope(
      child: UniControlApp(),
    ),
  );
}

class UniControlApp extends ConsumerWidget {
  const UniControlApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'UniControl',
      debugShowCheckedModeBanner: false,

      // Theme
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.light,

      // Router
      routerConfig: router,
    );
  }
}
