# UniControl Mobile

UniControl - University Control System mobil ilovasi. Flutter da yozilgan, iOS va Android uchun.

## 📱 Xususiyatlar

- 🔐 **Autentifikatsiya** - JWT tokens bilan xavfsiz login
- 📊 **Dashboard** - Statistika va tezkor amallar
- ✅ **Davomat** - Davomat ko'rish va olish (sardorlar uchun)
- 📅 **Dars jadvali** - Haftalik dars jadvali
- 👥 **Talabalar** - Talabalar ro'yxati va tafsilotlari
- 🔔 **Bildirishnomalar** - Push bildirishnomalar
- 📋 **Hisobotlar** - Davomat hisobotlari
- 🏆 **Turnirlar** - Bellashuvlarga ro'yxatdan o'tish
- 👥 **To'garaklar** - To'garaklarga qo'shilish
- ⚙️ **Sozlamalar** - Til, tema, parol

## 🛠 Texnologiyalar

- **Flutter** 3.12+
- **Riverpod** - State management
- **Go Router** - Navigation
- **Dio** - HTTP client
- **Flutter Secure Storage** - Xavfsiz saqlash
- **FL Chart** - Grafiklar

## 📁 Loyiha Strukturasi

```
lib/
├── core/
│   ├── constants/      # API va app konstantalari
│   ├── theme/          # App tema
│   ├── utils/          # Yordamchi funksiyalar
│   └── router.dart     # Go Router konfiguratsiyasi
├── data/
│   ├── models/         # Data modellari
│   └── providers/      # Riverpod providerlar
├── features/
│   ├── auth/           # Login, splash
│   ├── dashboard/      # Bosh sahifa
│   ├── attendance/     # Davomat
│   ├── schedule/       # Dars jadvali
│   ├── students/       # Talabalar
│   ├── groups/         # Guruhlar
│   ├── notifications/  # Bildirishnomalar
│   ├── reports/        # Hisobotlar
│   ├── clubs/          # To'garaklar
│   ├── tournaments/    # Turnirlar
│   ├── profile/        # Profil
│   └── settings/       # Sozlamalar
├── services/
│   └── api_service.dart  # Backend API service
├── widgets/
│   └── main_shell.dart   # Bottom navigation
└── main.dart             # Entry point
```

## 🚀 Ishga Tushirish

### 1. Paketlarni yuklash
```bash
cd unicontrolmobile
flutter pub get
```

### 2. API URL ni sozlash
`lib/core/constants/api_constants.dart` faylida:
```dart
static const String baseUrl = 'http://YOUR_SERVER_IP:8000/api/v1';
```

### 3. Ilovani ishga tushirish
```bash
flutter run
```

### 4. Build qilish
```bash
# Android APK
flutter build apk --release

# iOS
flutter build ios --release
```

## 👥 Foydalanuvchi Rollari

| Rol | Imkoniyatlar |
|-----|--------------|
| **Talaba** | Dashboard, jadval, davomat, to'garaklar, turnirlar |
| **Sardor** | Talaba + davomat olish, guruh boshqarish |
| **Admin** | Sardor + barcha guruhlar, foydalanuvchilar |
| **SuperAdmin** | Admin + tizim sozlamalari |

## 📄 Litsenziya

UniControl © 2026
