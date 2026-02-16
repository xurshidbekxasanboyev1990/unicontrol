/// Auth Provider
/// Autentifikatsiya holati va foydalanuvchi ma'lumotlarini boshqarish
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../core/constants/api_constants.dart';
import '../../data/models/user_model.dart';
import '../../services/api_service.dart';
import 'dart:convert';

/// Auth state class
class AuthState {
  final User? user;
  final bool isLoading;
  final bool isAuthenticated;
  final String? error;

  const AuthState({
    this.user,
    this.isLoading = false,
    this.isAuthenticated = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    bool? isLoading,
    bool? isAuthenticated,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      error: error,
    );
  }

  factory AuthState.initial() => const AuthState();

  factory AuthState.loading() => const AuthState(isLoading: true);

  factory AuthState.authenticated(User user) => AuthState(
    user: user,
    isAuthenticated: true,
  );

  factory AuthState.error(String message) => AuthState(error: message);
}

/// Auth Notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  AuthNotifier() : super(AuthState.initial()) {
    checkAuth();
  }

  /// Check if user is authenticated
  Future<void> checkAuth() async {
    state = state.copyWith(isLoading: true);

    try {
      final isLoggedIn = await _storage.read(key: StorageKeys.isLoggedIn);

      if (isLoggedIn == 'true') {
        // Cached user data
        final userJson = await _storage.read(key: StorageKeys.user);
        if (userJson != null) {
          final user = User.fromJson(jsonDecode(userJson));
          state = AuthState.authenticated(user);

          // Background da yangilash
          _refreshUser();
        } else {
          // API dan olish
          await _refreshUser();
        }
      } else {
        state = AuthState.initial();
      }
    } catch (e) {
      state = AuthState.initial();
    }
  }

  /// Refresh user data from API
  Future<void> _refreshUser() async {
    try {
      final user = await apiService.getMe();
      await _storage.write(key: StorageKeys.user, value: jsonEncode(user.toJson()));
      state = AuthState.authenticated(user);
    } catch (e) {
      // Token muddati tugagan bo'lishi mumkin
      await logout();
    }
  }

  /// Login
  Future<bool> login(String loginText, String password) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // Login returns user directly from response
      final user = await apiService.login(loginText, password);

      await _storage.write(key: StorageKeys.user, value: jsonEncode(user.toJson()));

      state = AuthState.authenticated(user);
      return true;
    } catch (e) {
      state = AuthState.error(e.toString());
      return false;
    }
  }

  /// Logout
  Future<void> logout() async {
    state = state.copyWith(isLoading: true);

    try {
      await apiService.logout();
    } catch (e) {
      // Ignore logout errors
    }

    state = AuthState.initial();
  }

  /// Change password
  Future<bool> changePassword(String currentPassword, String newPassword) async {
    try {
      await apiService.changePassword(currentPassword, newPassword);
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Auth provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

/// Is authenticated provider
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isAuthenticated;
});

/// Current user provider
final currentUserProvider = Provider<User?>((ref) {
  return ref.watch(authProvider).user;
});

/// User role provider
final userRoleProvider = Provider<String?>((ref) {
  return ref.watch(currentUserProvider)?.role.value;
});

