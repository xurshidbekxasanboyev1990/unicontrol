<template>
  <div class="min-h-screen bg-slate-900 relative overflow-hidden">
    <!-- Animated Background -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-emerald-500/15 rounded-full blur-[150px] animate-blob"></div>
      <div class="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-teal-500/15 rounded-full blur-[150px] animate-blob animation-delay-2000"></div>
      <div class="absolute top-[40%] left-[30%] w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[150px] animate-blob animation-delay-4000"></div>
      
      <!-- Grid -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:72px_72px]"></div>
      
      <!-- Gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-b from-slate-900/50 via-transparent to-slate-900"></div>
    </div>

    <!-- ========== NAVBAR ========== -->
    <nav class="relative z-50 px-4 sm:px-6 lg:px-20 py-4 sm:py-5 sticky top-0 bg-slate-900/80 backdrop-blur-xl border-b border-white/5">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center gap-2 sm:gap-3 group cursor-pointer">
          <div class="relative">
            <div class="absolute inset-0 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-xl sm:rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
            <div class="relative w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-xl">
              <GraduationCap class="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
          </div>
          <div class="flex flex-col">
            <span class="text-lg sm:text-xl font-bold text-white tracking-tight">Uni Control</span>
            <span class="text-[9px] sm:text-[10px] text-slate-500 font-medium tracking-wider uppercase hidden sm:block">Education Platform</span>
          </div>
        </div>

        <!-- Nav Links - Desktop -->
        <div class="hidden lg:flex items-center gap-1 bg-white/5 backdrop-blur-sm rounded-2xl p-1.5 border border-white/5">
          <a href="#features" class="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Xususiyatlar</a>
          <a href="#how-it-works" class="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Qanday ishlaydi</a>
          <a href="#about" class="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Biz haqimizda</a>
          <a href="#contact" class="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Bog'lanish</a>
        </div>

        <!-- Mobile Menu Button + CTA -->
        <div class="flex items-center gap-2 sm:gap-3">
          <!-- Mobile Menu Button -->
          <button 
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="lg:hidden p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl transition-colors"
          >
            <Menu v-if="!mobileMenuOpen" class="w-6 h-6" />
            <X v-else class="w-6 h-6" />
          </button>

          <!-- CTA -->
          <router-link to="/login" class="group relative">
            <div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
            <div class="relative flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 px-4 sm:px-6 py-2.5 sm:py-3 rounded-xl font-semibold text-white text-sm transition-all">
              <LogIn class="w-4 h-4" />
              <span class="hidden sm:inline">Kirish</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Mobile Menu -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-4"
      >
        <div v-if="mobileMenuOpen" class="lg:hidden absolute left-4 right-4 top-full mt-2 bg-slate-800/95 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-xl">
          <div class="space-y-1">
            <a href="#features" @click="mobileMenuOpen = false" class="block px-4 py-3 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Xususiyatlar</a>
            <a href="#how-it-works" @click="mobileMenuOpen = false" class="block px-4 py-3 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Qanday ishlaydi</a>
            <a href="#about" @click="mobileMenuOpen = false" class="block px-4 py-3 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Biz haqimizda</a>
            <a href="#contact" @click="mobileMenuOpen = false" class="block px-4 py-3 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all">Bog'lanish</a>
          </div>
        </div>
      </Transition>
    </nav>

    <!-- ========== HERO ========== -->
    <section class="relative z-10 px-4 sm:px-6 lg:px-20 pt-10 sm:pt-16 lg:pt-24 pb-12 sm:pb-20">
      <div class="max-w-7xl mx-auto">
        <div class="grid lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16 items-center">
          <!-- Left -->
          <div class="space-y-6 sm:space-y-8 text-center lg:text-left">
            <!-- Badge -->
            <div class="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full pl-2 pr-3 sm:pr-4 py-1 sm:py-1.5 animate-fade-in">
              <span class="flex items-center justify-center w-5 h-5 sm:w-6 sm:h-6 bg-emerald-500 rounded-full">
                <Zap class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-white" />
              </span>
              <span class="text-emerald-400 text-xs sm:text-sm font-medium">Yangi avlod ta'lim tizimi</span>
            </div>

            <!-- Title -->
            <div class="space-y-4 animate-fade-in animation-delay-200">
              <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-[1.1] tracking-tight">
                Zamonaviy usulda
                <br />
                <span class="relative inline-block">
                  <span class="relative z-10 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400">Ta'limni</span>
                  <span class="absolute bottom-2 left-0 w-full h-3 bg-emerald-500/20 -skew-x-6"></span>
                </span>
                boshqaring
              </h1>
              <p class="text-lg text-slate-400 leading-relaxed max-w-lg">
                Dars jadvali, davomat va o'quv jarayonini yagona platformada nazorat qiling. 
                Vaqtni tejang, samaradorlikni oshiring.
              </p>
            </div>

            <!-- CTA -->
            <div class="flex flex-wrap items-center gap-4 animate-fade-in animation-delay-400">
              <router-link to="/login" class="group relative overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl"></div>
                <div class="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div class="absolute inset-0 translate-y-full group-hover:translate-y-0 bg-white/10 transition-transform duration-300"></div>
                <div class="relative flex items-center gap-3 px-8 py-4 font-semibold text-white">
                  <Rocket class="w-5 h-5" />
                  <span>Boshlash</span>
                  <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </router-link>

              <a href="#how-it-works" class="group flex items-center gap-3 px-6 py-4 text-slate-300 hover:text-white font-medium transition-colors">
                <div class="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-white/10 group-hover:border-white/20 transition-all">
                  <Play class="w-5 h-5 text-emerald-400 ml-0.5" />
                </div>
                <span>Qanday ishlaydi?</span>
              </a>
            </div>

            <!-- Stats -->
            <div class="flex flex-wrap items-center justify-center lg:justify-start gap-4 sm:gap-6 lg:gap-8 pt-6 sm:pt-8 animate-fade-in animation-delay-600">
              <div class="flex items-center gap-2 sm:gap-3">
                <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-emerald-500/10 flex items-center justify-center">
                  <Users class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-400" />
                </div>
                <div>
                  <div class="text-xl sm:text-2xl font-bold text-white">500+</div>
                  <div class="text-[10px] sm:text-xs text-slate-500">Talabalar</div>
                </div>
              </div>
              <div class="w-px h-10 sm:h-12 bg-white/10 hidden sm:block"></div>
              <div class="flex items-center gap-2 sm:gap-3">
                <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-teal-500/10 flex items-center justify-center">
                  <Layers class="w-5 h-5 sm:w-6 sm:h-6 text-teal-400" />
                </div>
                <div>
                  <div class="text-xl sm:text-2xl font-bold text-white">50+</div>
                  <div class="text-[10px] sm:text-xs text-slate-500">Guruhlar</div>
                </div>
              </div>
              <div class="w-px h-10 sm:h-12 bg-white/10 hidden sm:block"></div>
              <div class="flex items-center gap-2 sm:gap-3">
                <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-cyan-500/10 flex items-center justify-center">
                  <TrendingUp class="w-5 h-5 sm:w-6 sm:h-6 text-cyan-400" />
                </div>
                <div>
                  <div class="text-xl sm:text-2xl font-bold text-white">99%</div>
                  <div class="text-[10px] sm:text-xs text-slate-500">Natija</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right - Dashboard Preview -->
          <div class="hidden lg:block relative animate-fade-in animation-delay-400">
            <!-- Glow -->
            <div class="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-cyan-500/20 rounded-[40px] blur-3xl opacity-50"></div>
            
            <!-- Main Card -->
            <div class="relative bg-slate-800/50 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl">
              <!-- Header -->
              <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full bg-rose-500"></div>
                  <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                  <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
                </div>
                <div class="text-xs text-slate-500 font-medium">Talaba Dashboard</div>
              </div>

              <!-- User Info -->
              <div class="flex items-center gap-4 p-4 bg-white/5 rounded-2xl mb-5">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-lg">JA</div>
                <div class="flex-1">
                  <div class="font-semibold text-white">Javohir Abdullayev</div>
                  <div class="text-sm text-slate-500">2-kurs • 21-01 guruh</div>
                </div>
                <div class="text-right">
                  <div class="text-2xl font-bold text-emerald-400">92%</div>
                  <div class="text-xs text-slate-500">Davomat</div>
                </div>
              </div>

              <!-- Schedule -->
              <div class="space-y-3 mb-5">
                <div class="text-xs text-slate-500 font-medium uppercase tracking-wider mb-3">Bugungi darslar</div>
                <div class="flex items-center gap-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                  <div class="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                    <BookOpen class="w-5 h-5 text-emerald-400" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-white text-sm truncate">Matematika</div>
                    <div class="text-xs text-slate-500">08:00 - 09:30 • 204-xona</div>
                  </div>
                  <div class="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-lg">Hozir</div>
                </div>
                <div class="flex items-center gap-3 p-3 bg-white/5 border border-white/5 rounded-xl">
                  <div class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
                    <Code class="w-5 h-5 text-slate-400" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-white text-sm truncate">Dasturlash</div>
                    <div class="text-xs text-slate-500">10:00 - 11:30 • Lab-3</div>
                  </div>
                </div>
              </div>

              <!-- Progress -->
              <div class="p-4 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/10 rounded-xl">
                <div class="flex items-center justify-between mb-3">
                  <span class="text-sm font-medium text-white">Haftalik progress</span>
                  <span class="text-sm font-bold text-emerald-400">85%</span>
                </div>
                <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full w-[85%] bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full relative">
                    <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Floating Elements -->
            <div class="absolute -top-6 -right-6 w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-500/30 animate-float">
              <Bell class="w-8 h-8 text-white" />
              <span class="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 rounded-full flex items-center justify-center text-xs font-bold text-white">3</span>
            </div>
            
            <div class="absolute -bottom-4 -left-4 bg-slate-800/80 backdrop-blur border border-white/10 rounded-2xl p-4 shadow-xl animate-float animation-delay-2000">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                  <CheckCircle class="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <div class="text-sm font-medium text-white">Davomat belgilandi</div>
                  <div class="text-xs text-slate-500">Matematika • Hozirgina</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== TRUSTED BY ========== -->
    <section class="relative z-10 px-6 lg:px-20 py-16 border-t border-white/5">
      <div class="max-w-7xl mx-auto reveal-on-scroll">
        <p class="text-center text-slate-500 text-sm font-medium mb-10">Bizga ishonch bildirgan tashkilot</p>
        <div class="flex flex-wrap items-center justify-center gap-12">
          <div class="flex items-center gap-4 bg-white/5 border border-white/10 rounded-2xl px-8 py-5 hover-lift reveal-scale">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <GraduationCap class="w-7 h-7 text-white" />
            </div>
            <div>
              <span class="text-xl font-bold text-white">KUAF</span>
              <p class="text-sm text-slate-400">Kokand universiteti Andijon filiali</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== HOW IT WORKS ========== -->
    <section id="how-it-works" class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-16 reveal-on-scroll">
          <div class="inline-flex items-center gap-2 bg-teal-500/10 border border-teal-500/20 rounded-full px-4 py-2 mb-6">
            <Settings class="w-4 h-4 text-teal-400" />
            <span class="text-sm text-teal-400">Oddiy va tushunarli</span>
          </div>
          <h2 class="text-3xl lg:text-5xl font-bold text-white mb-4">Qanday ishlaydi?</h2>
          <p class="text-slate-400 max-w-2xl mx-auto text-lg">Atigi 3 oddiy qadamda tizimdan foydalanishni boshlang</p>
        </div>

        <!-- Steps - 3D Stacked Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 perspective-container">
          <!-- Step 1 -->
          <div class="relative group card-stack stagger-child" style="--index: 0">
            <div class="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div class="relative bg-slate-800/50 backdrop-blur border border-white/5 rounded-3xl p-8 h-full hover-lift">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-emerald-500/30">1</div>
                <div class="h-1 flex-1 bg-gradient-to-r from-emerald-500/50 to-transparent rounded-full"></div>
              </div>
              <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-6">
                <UserPlus class="w-8 h-8 text-emerald-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Ro'yxatdan o'ting</h3>
              <p class="text-slate-400 leading-relaxed">Admin sizni tizimga qo'shadi va login ma'lumotlarini beradi. Shaxsiy kabinet yaratiladi.</p>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="relative group card-stack stagger-child" style="--index: 1">
            <div class="absolute -inset-1 bg-gradient-to-r from-teal-500/20 to-cyan-500/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div class="relative bg-slate-800/50 backdrop-blur border border-white/5 rounded-3xl p-8 h-full hover-lift">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-teal-500/30">2</div>
                <div class="h-1 flex-1 bg-gradient-to-r from-teal-500/50 to-transparent rounded-full"></div>
              </div>
              <div class="w-16 h-16 rounded-2xl bg-teal-500/10 flex items-center justify-center mb-6">
                <Smartphone class="w-8 h-8 text-teal-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Tizimga kiring</h3>
              <p class="text-slate-400 leading-relaxed">Telefon yoki kompyuter orqali tizimga kiring. Barcha ma'lumotlar real vaqtda yangilanadi.</p>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="relative group card-stack stagger-child" style="--index: 2">
            <div class="absolute -inset-1 bg-gradient-to-r from-cyan-500/20 to-violet-500/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div class="relative bg-slate-800/50 backdrop-blur border border-white/5 rounded-3xl p-8 h-full hover-lift">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-cyan-500/30">3</div>
                <div class="h-1 flex-1 bg-gradient-to-r from-cyan-500/50 to-transparent rounded-full"></div>
              </div>
              <div class="w-16 h-16 rounded-2xl bg-cyan-500/10 flex items-center justify-center mb-6">
                <Sparkles class="w-8 h-8 text-cyan-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Foydalaning</h3>
              <p class="text-slate-400 leading-relaxed">Dars jadvali, davomat, bildirishnomalar - hammasi bir joyda. O'qishni oson nazorat qiling.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== FEATURES ========== -->
    <section id="features" class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-16 reveal-on-scroll">
          <div class="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2 mb-6">
            <Sparkles class="w-4 h-4 text-emerald-400" />
            <span class="text-sm text-slate-400">Platformamiz imkoniyatlari</span>
          </div>
          <h2 class="text-3xl lg:text-5xl font-bold text-white mb-4">Asosiy xususiyatlar</h2>
          <p class="text-slate-400 max-w-2xl mx-auto text-lg">Talabalar va o'qituvchilar uchun barcha kerakli vositalar</p>
        </div>

        <!-- Features Grid - 3D Stacked Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 perspective-container">
          <div class="group relative bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 hover:border-emerald-500/30 transition-all duration-500 card-stack stagger-child hover-lift" style="--index: 0">
            <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                <Calendar class="w-8 h-8 text-emerald-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Dars jadvali</h3>
              <p class="text-slate-400 leading-relaxed">Haftalik va oylik darslar tartibli ko'rinishda. Real-time yangilanishlar.</p>
            </div>
          </div>

          <div class="group relative bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 hover:border-teal-500/30 transition-all duration-500 card-stack stagger-child hover-lift" style="--index: 1">
            <div class="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500/20 to-teal-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                <BarChart3 class="w-8 h-8 text-teal-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Davomat nazorati</h3>
              <p class="text-slate-400 leading-relaxed">Qoldirilgan darslar avtomatik hisoblanadi. Statistika har doim qo'l ostida.</p>
            </div>
          </div>

          <div class="group relative bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 hover:border-cyan-500/30 transition-all duration-500 card-stack stagger-child hover-lift" style="--index: 2">
            <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                <Brain class="w-8 h-8 text-cyan-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">AI tahlil</h3>
              <p class="text-slate-400 leading-relaxed">Sun'iy intellekt yordamida o'quv natijalarini tahlil qiling.</p>
            </div>
          </div>

          <div class="group relative bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 hover:border-violet-500/30 transition-all duration-500 card-stack stagger-child hover-lift" style="--index: 3">
            <div class="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-violet-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                <Bell class="w-8 h-8 text-violet-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Bildirishnomalar</h3>
              <p class="text-slate-400 leading-relaxed">Muhim yangiliklar va eslatmalar haqida xabar oling.</p>
            </div>
          </div>

          <div class="group relative bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 hover:border-amber-500/30 transition-all duration-500 card-stack stagger-child hover-lift" style="--index: 4">
            <div class="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500/20 to-amber-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                <Trophy class="w-8 h-8 text-amber-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Turnirlar</h3>
              <p class="text-slate-400 leading-relaxed">Sport musobaqalari va intellektual o'yinlar uchun oson va qulay ro'yxatdan o'tish.</p>
            </div>
          </div>

          <div class="group relative bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 hover:border-rose-500/30 transition-all duration-500 card-stack stagger-child hover-lift" style="--index: 5">
            <div class="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="relative">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-rose-500/20 to-rose-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                <Shield class="w-8 h-8 text-rose-400" />
              </div>
              <h3 class="text-xl font-bold text-white mb-3">Xavfsizlik</h3>
              <p class="text-slate-400 leading-relaxed">Ma'lumotlar himoyasi va shaxsiy kabinetga xavfsiz kirish.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== ABOUT US ========== -->
    <section id="about" class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-7xl mx-auto">
        <div class="grid lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16 items-center">
          <!-- Left - Image/Visual -->
          <div class="relative reveal-left reveal-on-scroll">
            <div class="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-[40px] blur-3xl opacity-50"></div>
            <div class="relative bg-slate-800/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover-scale">
              <!-- Mission Card -->
              <div class="mb-6">
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                    <Target class="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h4 class="text-lg font-bold text-white">Bizning maqsadimiz</h4>
                    <p class="text-sm text-slate-500">Ta'limni zamonaviylashtirish</p>
                  </div>
                </div>
                <p class="text-slate-400 leading-relaxed">O'zbekiston ta'lim tizimini raqamlashtirish va jahon standartlariga yetkazish.</p>
              </div>

              <!-- Stats Grid -->
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-white/5 rounded-2xl p-5 text-center stagger-child">
                  <div class="text-2xl font-bold text-emerald-400 mb-1">01.10.2025</div>
                  <div class="text-sm text-slate-500">Tashkil etilgan</div>
                </div>
                <div class="bg-white/5 rounded-2xl p-5 text-center stagger-child">
                  <div class="text-3xl font-bold text-teal-400 mb-1">1</div>
                  <div class="text-sm text-slate-500">Universitet</div>
                </div>
                <div class="bg-white/5 rounded-2xl p-5 text-center stagger-child">
                  <div class="text-3xl font-bold text-cyan-400 mb-1">500+</div>
                  <div class="text-sm text-slate-500">Foydalanuvchilar</div>
                </div>
                <div class="bg-white/5 rounded-2xl p-5 text-center stagger-child">
                  <div class="text-3xl font-bold text-violet-400 mb-1">24/7</div>
                  <div class="text-sm text-slate-500">Qo'llab-quvvatlash</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right - Content -->
          <div class="space-y-8 reveal-right reveal-on-scroll">
            <div class="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-2">
              <Heart class="w-4 h-4 text-emerald-400" />
              <span class="text-sm text-emerald-400">Biz haqimizda</span>
            </div>

            <h2 class="text-3xl lg:text-5xl font-bold text-white leading-tight">
              Ta'limga yangicha 
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">yondashuv</span>
            </h2>

            <p class="text-lg text-slate-400 leading-relaxed">
              Uni Control - KUAF StartUP loyihalar bilan ishlash bo'limi tomonidan yaratilgan zamonaviy ta'lim boshqaruv platformasi. 
              Biz talabalar, o'qituvchilar va administratorlar uchun qulay va samarali vositalar yaratamiz.
            </p>

            <div class="space-y-4">
              <div class="flex items-start gap-4 stagger-child">
                <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Check class="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h4 class="font-semibold text-white mb-1">Mahalliy ishlab chiqarish</h4>
                  <p class="text-slate-400 text-sm">O'zbek dasturchilari tomonidan yaratilgan, mahalliy ehtiyojlarga moslangan</p>
                </div>
              </div>

              <div class="flex items-start gap-4 stagger-child">
                <div class="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Check class="w-5 h-5 text-teal-400" />
                </div>
                <div>
                  <h4 class="font-semibold text-white mb-1">Doimiy yangilanishlar</h4>
                  <p class="text-slate-400 text-sm">Har oy yangi funksiyalar va yaxshilanishlar qo'shiladi</p>
                </div>
              </div>

              <div class="flex items-start gap-4 stagger-child">
                <div class="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Check class="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h4 class="font-semibold text-white mb-1">Professional qo'llab-quvvatlash</h4>
                  <p class="text-slate-400 text-sm">Texnik yordam jamoasi doimo aloqada</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== TESTIMONIALS ========== -->
    <section class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-16 reveal-on-scroll">
          <div class="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-2 mb-6">
            <Star class="w-4 h-4 text-amber-400" />
            <span class="text-sm text-amber-400">Foydalanuvchilar fikri</span>
          </div>
          <h2 class="text-3xl lg:text-5xl font-bold text-white mb-4">Ular nima deyishadi?</h2>
          <p class="text-slate-400 max-w-2xl mx-auto text-lg">Platformamiz foydalanuvchilarining fikrlari</p>
        </div>

        <!-- Testimonials Grid - 3D Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 perspective-container">
          <!-- Testimonial 1 -->
          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 card-stack stagger-child hover-lift" style="--index: 0">
            <div class="flex items-center gap-1 mb-4">
              <Star v-for="i in 5" :key="i" class="w-5 h-5 text-amber-400 fill-amber-400" />
            </div>
            <p class="text-slate-300 leading-relaxed mb-6">
              "Dars jadvalini kuzatish juda oson bo'lib qoldi. Endi hech qachon darsni o'tkazib yubormayapman!"
            </p>
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold">SA</div>
              <div>
                <div class="font-semibold text-white">Sardor Aliyev</div>
                <div class="text-sm text-slate-500">2-kurs talabasi, KUAF</div>
              </div>
            </div>
          </div>

          <!-- Testimonial 2 -->
          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 card-stack stagger-child hover-lift" style="--index: 1">
            <div class="flex items-center gap-1 mb-4">
              <Star v-for="i in 5" :key="i" class="w-5 h-5 text-amber-400 fill-amber-400" />
            </div>
            <p class="text-slate-300 leading-relaxed mb-6">
              "Guruh sardori sifatida davomat yuritish ancha osonlashdi. Vaqt tejash katta foyda!"
            </p>
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center text-white font-bold">MK</div>
              <div>
                <div class="font-semibold text-white">Madina Karimova</div>
                <div class="text-sm text-slate-500">Guruh sardori, KUAF</div>
              </div>
            </div>
          </div>

          <!-- Testimonial 3 -->
          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-3xl p-8 card-stack stagger-child hover-lift" style="--index: 2">
            <div class="flex items-center gap-1 mb-4">
              <Star v-for="i in 5" :key="i" class="w-5 h-5 text-amber-400 fill-amber-400" />
            </div>
            <p class="text-slate-300 leading-relaxed mb-6">
              "Barcha guruhlarni boshqarish bir joydan mumkin. Juda qulay va zamonaviy tizim!"
            </p>
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center text-white font-bold">AJ</div>
              <div>
                <div class="font-semibold text-white">Aziz Jabborov</div>
                <div class="text-sm text-slate-500">Admin, KUAF</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== FAQ ========== -->
    <section class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-16 reveal-on-scroll">
          <div class="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-4 py-2 mb-6">
            <HelpCircle class="w-4 h-4 text-violet-400" />
            <span class="text-sm text-violet-400">Ko'p so'raladigan savollar</span>
          </div>
          <h2 class="text-3xl lg:text-5xl font-bold text-white mb-4">FAQ</h2>
          <p class="text-slate-400 max-w-2xl mx-auto text-lg">Eng ko'p beriladigan savollarga javoblar</p>
        </div>

        <!-- FAQ Items - 3D Stacked -->
        <div class="space-y-4 perspective-container">
          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors card-stack stagger-child hover-lift" style="--index: 0">
            <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-3">
              <ChevronRight class="w-5 h-5 text-emerald-400" />
              Tizimdan kim foydalanishi mumkin?
            </h4>
            <p class="text-slate-400 pl-8">Tizimdan talabalar, guruh sardorlari va administratorlar foydalanishi mumkin. Universitet admini sizni tizimga qo'shadi.</p>
          </div>

          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors card-stack stagger-child hover-lift" style="--index: 1">
            <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-3">
              <ChevronRight class="w-5 h-5 text-emerald-400" />
              Tizimga qanday ro'yxatdan o'taman?
            </h4>
            <p class="text-slate-400 pl-8">Sizning universitet admini tizimga qo'shadi va login ma'lumotlarini beradi. Keyin shaxsiy kabinet orqali kirish mumkin.</p>
          </div>

          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors card-stack stagger-child hover-lift" style="--index: 2">
            <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-3">
              <ChevronRight class="w-5 h-5 text-emerald-400" />
              Mobil ilova bormi?
            </h4>
            <p class="text-slate-400 pl-8">Hozircha web versiya mavjud, lekin u to'liq mobil qurilmalarga moslangan. Mobil ilova tez orada chiqariladi.</p>
          </div>

          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors card-stack stagger-child hover-lift" style="--index: 3">
            <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-3">
              <ChevronRight class="w-5 h-5 text-emerald-400" />
              Ma'lumotlarim xavfsizmi?
            </h4>
            <p class="text-slate-400 pl-8">Albatta! Barcha ma'lumotlar shifrlangan holda saqlanadi va faqat ruxsat berilgan foydalanuvchilar ko'ra oladi.</p>
          </div>

          <div class="bg-slate-800/30 backdrop-blur border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-colors card-stack stagger-child hover-lift" style="--index: 4">
            <h4 class="text-lg font-semibold text-white mb-3 flex items-center gap-3">
              <ChevronRight class="w-5 h-5 text-emerald-400" />
              Qo'llab-quvvatlash xizmati bormi?
            </h4>
            <p class="text-slate-400 pl-8">Ha, bizning texnik yordam jamoamiz 24/7 aloqada. Telegram bot yoki email orqali murojaat qilishingiz mumkin.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== CTA SECTION ========== -->
    <section class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-5xl mx-auto reveal-scale">
        <div class="relative overflow-hidden rounded-[40px] hover-scale">
          <!-- Background -->
          <div class="absolute inset-0 bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600"></div>
          <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]"></div>
          
          <!-- Content -->
          <div class="relative px-6 py-12 sm:px-8 sm:py-16 lg:px-16 lg:py-20 text-center">
            <h2 class="text-2xl sm:text-3xl lg:text-5xl font-bold text-white mb-4 sm:mb-6">
              Hoziroq boshlang!
            </h2>
            <p class="text-xl text-white/80 mb-10 max-w-2xl mx-auto">
              Minglab talabalar allaqachon Uni Control'dan foydalanmoqda. 
              Siz ham qo'shiling!
            </p>
            <div class="flex flex-wrap items-center justify-center gap-4">
              <router-link to="/login" class="group bg-white text-emerald-600 px-8 py-4 rounded-2xl font-bold text-lg hover:bg-white/90 transition-all flex items-center gap-3 hover-lift">
                <Rocket class="w-6 h-6" />
                <span>Boshlash</span>
                <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </router-link>
              <a href="#contact" class="text-white/90 hover:text-white px-6 py-4 font-semibold flex items-center gap-2 transition-colors">
                <MessageCircle class="w-5 h-5" />
                <span>Bog'lanish</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== CONTACT ========== -->
    <section id="contact" class="relative z-10 px-4 sm:px-6 lg:px-20 py-16 sm:py-24 border-t border-white/5">
      <div class="max-w-7xl mx-auto">
        <div class="grid lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16">
          <!-- Left -->
          <div class="space-y-8 reveal-left reveal-on-scroll">
            <div class="inline-flex items-center gap-2 bg-rose-500/10 border border-rose-500/20 rounded-full px-4 py-2">
              <MapPin class="w-4 h-4 text-rose-400" />
              <span class="text-sm text-rose-400">Bog'lanish</span>
            </div>

            <h2 class="text-3xl lg:text-5xl font-bold text-white leading-tight">
              Biz bilan 
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">bog'laning</span>
            </h2>

            <p class="text-lg text-slate-400 leading-relaxed">
              Savollaringiz bormi? Biz bilan bog'laning, tez orada javob beramiz!
            </p>

            <!-- Contact Info -->
            <div class="space-y-6">
              <div class="flex items-center gap-4 stagger-child hover-lift p-2 -m-2 rounded-2xl transition-all">
                <div class="w-14 h-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                  <Mail class="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <div class="text-sm text-slate-500 mb-1">Email</div>
                  <a href="mailto:info@unicontrol.uz" class="text-lg font-semibold text-white hover:text-emerald-400 transition-colors">info@unicontrol.uz</a>
                </div>
              </div>

              <div class="flex items-center gap-4 stagger-child hover-lift p-2 -m-2 rounded-2xl transition-all">
                <div class="w-14 h-14 rounded-2xl bg-teal-500/10 flex items-center justify-center">
                  <Phone class="w-6 h-6 text-teal-400" />
                </div>
                <div>
                  <div class="text-sm text-slate-500 mb-1">Telefon</div>
                  <a href="tel:+998901234567" class="text-lg font-semibold text-white hover:text-teal-400 transition-colors">+998 90 123 45 67</a>
                </div>
              </div>

              <div class="flex items-center gap-4 stagger-child hover-lift p-2 -m-2 rounded-2xl transition-all">
                <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 flex items-center justify-center">
                  <MessageCircle class="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <div class="text-sm text-slate-500 mb-1">Telegram</div>
                  <a href="https://t.me/unicontrol_uz" target="_blank" class="text-lg font-semibold text-white hover:text-cyan-400 transition-colors">@unicontrol_uz</a>
                </div>
              </div>

              <div class="flex items-center gap-4 stagger-child hover-lift p-2 -m-2 rounded-2xl transition-all">
                <div class="w-14 h-14 rounded-2xl bg-violet-500/10 flex items-center justify-center">
                  <MapPin class="w-6 h-6 text-violet-400" />
                </div>
                <div>
                  <div class="text-sm text-slate-500 mb-1">Manzil</div>
                  <p class="text-lg font-semibold text-white">Toshkent sh., Chilonzor t.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Right - Contact Form -->
          <div class="relative reveal-right reveal-on-scroll">
            <div class="absolute -inset-4 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-[40px] blur-3xl"></div>
            <div class="relative bg-slate-800/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover-scale">
              <h3 class="text-2xl font-bold text-white mb-6">Xabar yuborish</h3>
              <form class="space-y-5">
                <div class="stagger-child">
                  <label class="block text-sm font-medium text-slate-400 mb-2">Ismingiz</label>
                  <input type="text" placeholder="Ismingizni kiriting" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all" />
                </div>
                <div class="stagger-child">
                  <label class="block text-sm font-medium text-slate-400 mb-2">Email</label>
                  <input type="email" placeholder="email@example.com" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all" />
                </div>
                <div class="stagger-child">
                  <label class="block text-sm font-medium text-slate-400 mb-2">Xabar</label>
                  <textarea rows="4" placeholder="Xabaringizni yozing..." class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all resize-none"></textarea>
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-semibold py-4 rounded-xl transition-all flex items-center justify-center gap-2 stagger-child hover-lift">
                  <Send class="w-5 h-5" />
                  <span>Yuborish</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== FOOTER ========== -->
    <footer class="relative z-10 px-4 sm:px-6 lg:px-20 py-8 sm:py-12 border-t border-white/5">
      <div class="max-w-7xl mx-auto reveal-on-scroll">
        <!-- Top -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-10 mb-8 sm:mb-12">
          <!-- Brand -->
          <div class="md:col-span-2 space-y-4 stagger-child">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center">
                <GraduationCap class="w-6 h-6 text-white" />
              </div>
              <span class="text-xl font-bold text-white">Uni Control</span>
            </div>
            <p class="text-slate-400 max-w-sm leading-relaxed">
              KUAF (Kokand universiteti Andijon filiali) uchun zamonaviy ta'lim boshqaruv platformasi. 
              Dars jadvali, davomat va o'quv jarayonini bir joydan boshqaring.
            </p>
            <div class="flex items-center gap-3">
              <a href="#" class="w-10 h-10 rounded-xl bg-white/5 hover:bg-emerald-500/20 border border-white/5 hover:border-emerald-500/30 flex items-center justify-center transition-all group hover-lift">
                <svg class="w-5 h-5 text-slate-400 group-hover:text-emerald-400 transition-colors" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/></svg>
              </a>
              <a href="#" class="w-10 h-10 rounded-xl bg-white/5 hover:bg-emerald-500/20 border border-white/5 hover:border-emerald-500/30 flex items-center justify-center transition-all group hover-lift">
                <svg class="w-5 h-5 text-slate-400 group-hover:text-emerald-400 transition-colors" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
              </a>
              <a href="#" class="w-10 h-10 rounded-xl bg-white/5 hover:bg-emerald-500/20 border border-white/5 hover:border-emerald-500/30 flex items-center justify-center transition-all group hover-lift">
                <svg class="w-5 h-5 text-slate-400 group-hover:text-emerald-400 transition-colors" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
              </a>
            </div>
          </div>

          <!-- Links -->
          <div class="stagger-child">
            <h4 class="font-semibold text-white mb-4">Sahifalar</h4>
            <ul class="space-y-3">
              <li><a href="#features" class="text-slate-400 hover:text-emerald-400 transition-colors">Xususiyatlar</a></li>
              <li><a href="#how-it-works" class="text-slate-400 hover:text-emerald-400 transition-colors">Qanday ishlaydi</a></li>
              <li><a href="#about" class="text-slate-400 hover:text-emerald-400 transition-colors">Biz haqimizda</a></li>
              <li><a href="#contact" class="text-slate-400 hover:text-emerald-400 transition-colors">Bog'lanish</a></li>
            </ul>
          </div>

          <!-- Legal -->
          <div class="stagger-child">
            <h4 class="font-semibold text-white mb-4">Qo'shimcha</h4>
            <ul class="space-y-3">
              <li><a href="#" class="text-slate-400 hover:text-emerald-400 transition-colors">Maxfiylik siyosati</a></li>
              <li><a href="#" class="text-slate-400 hover:text-emerald-400 transition-colors">Foydalanish shartlari</a></li>
              <li><a href="#" class="text-slate-400 hover:text-emerald-400 transition-colors">Yordam markazi</a></li>
              <li><router-link to="/login" class="text-slate-400 hover:text-emerald-400 transition-colors">Kirish</router-link></li>
            </ul>
          </div>
        </div>

        <!-- Team Section -->
        <div class="pt-8 border-t border-white/5 mb-8">
          <h4 class="font-semibold text-white mb-6 text-center">Loyiha jamoasi</h4>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <div class="bg-white/5 rounded-2xl p-4 text-center stagger-child hover-lift">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mx-auto mb-3">
                <Crown class="w-6 h-6 text-white" />
              </div>
              <div class="font-semibold text-white text-sm">Javlonbek To'ychiyev</div>
              <div class="text-xs text-slate-500">Bo'lim boshlig'i</div>
            </div>
            <div class="bg-white/5 rounded-2xl p-4 text-center stagger-child hover-lift">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mx-auto mb-3">
                <Palette class="w-6 h-6 text-white" />
              </div>
              <div class="font-semibold text-white text-sm">Obidjonov Behruzbek</div>
              <div class="text-xs text-slate-500">UI Dizayner</div>
            </div>
            <div class="bg-white/5 rounded-2xl p-4 text-center stagger-child hover-lift">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center mx-auto mb-3">
                <Code class="w-6 h-6 text-white" />
              </div>
              <div class="font-semibold text-white text-sm">Mannobov Xojisaid</div>
              <div class="text-xs text-slate-500">Frontend Dasturchi</div>
            </div>
            <div class="bg-white/5 rounded-2xl p-4 text-center stagger-child hover-lift">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mx-auto mb-3">
                <Server class="w-6 h-6 text-white" />
              </div>
              <div class="font-semibold text-white text-sm">Xasanboyev Xurshidbek</div>
              <div class="text-xs text-slate-500">Backend Dasturchi</div>
            </div>
          </div>
        </div>

        <!-- Bottom -->
        <div class="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-slate-500 text-sm">© 2026 Uni Control. Barcha huquqlar himoyalangan.</p>
          <p class="text-slate-500 text-sm">KUAF StartUP loyihalar bilan ishlash bo'limi tomonidan ishlab chiqilgan</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  GraduationCap, LogIn, ArrowRight, Play, Zap, Rocket, Users, Layers, TrendingUp,
  Calendar, BarChart3, Brain, Bell, Trophy, Shield, CheckCircle, Sparkles,
  BookOpen, Code, Globe, MessageCircle, Phone, Mail, Building2, Settings,
  UserPlus, Smartphone, Heart, Check, Target, Star, HelpCircle, ChevronRight,
  MapPin, Send, Crown, Palette, Server, Menu, X
} from 'lucide-vue-next'

// Mobile menu state
const mobileMenuOpen = ref(false)

let observer = null

onMounted(() => {
  // Optimal Intersection Observer - GPU optimized
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed')
        
        // Stagger children with requestAnimationFrame for smoothness
        const children = entry.target.querySelectorAll('.stagger-child')
        children.forEach((child, index) => {
          requestAnimationFrame(() => {
            setTimeout(() => {
              child.classList.add('revealed')
            }, index * 100)
          })
        })
      } else {
        // Reset when out of view
        entry.target.classList.remove('revealed')
        entry.target.querySelectorAll('.stagger-child').forEach(child => {
          child.classList.remove('revealed')
        })
      }
    })
  }, { 
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  })

  // Observe animated elements
  requestAnimationFrame(() => {
    document.querySelectorAll('.reveal-on-scroll, .reveal-left, .reveal-right, .reveal-scale, .card-stack, .perspective-container').forEach(el => {
      observer.observe(el)
    })
  })
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
/* ===== GPU OPTIMIZED ANIMATIONS - Apple Style ===== */

/* Force GPU acceleration */
.reveal-on-scroll,
.reveal-left,
.reveal-right,
.reveal-scale,
.card-stack,
.stagger-child {
  will-change: transform, opacity;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
}

/* ===== PERSPECTIVE CONTAINER ===== */
.perspective-container {
  perspective: 1000px;
  perspective-origin: center center;
}

/* ===== BASE REVEAL - Minimal fade up ===== */
.reveal-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}

.reveal-on-scroll.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* ===== CARD STACK - 3D Taxlangan Kartalar (Minimal) ===== */
.card-stack {
  opacity: 0;
  transform: 
    translateY(60px) 
    rotateX(25deg) 
    scale(0.92);
  transform-origin: center bottom;
  transition: 
    opacity 0.5s ease,
    transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: calc(var(--index, 0) * 0.12s);
}

.card-stack.revealed {
  opacity: 1;
  transform: 
    translateY(0) 
    rotateX(0deg) 
    scale(1);
}

/* Stagger children - Minimal */
.stagger-child {
  opacity: 0;
  transform: 
    translateY(40px) 
    rotateX(15deg);
  transform-origin: center bottom;
  transition: 
    opacity 0.4s ease,
    transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: calc(var(--index, 0) * 0.1s);
}

.stagger-child.revealed {
  opacity: 1;
  transform: 
    translateY(0) 
    rotateX(0deg);
}

/* ===== SLIDE FROM LEFT ===== */
.reveal-left {
  opacity: 0;
  transform: translate3d(-60px, 0, 0);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.reveal-left.revealed {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

/* ===== SLIDE FROM RIGHT ===== */
.reveal-right {
  opacity: 0;
  transform: translate3d(60px, 0, 0);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.reveal-right.revealed {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

/* ===== SCALE UP ===== */
.reveal-scale {
  opacity: 0;
  transform: scale3d(0.9, 0.9, 1);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.reveal-scale.revealed {
  opacity: 1;
  transform: scale3d(1, 1, 1);
}

/* ===== SMOOTH ANIMATIONS ===== */
@keyframes blob {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
  33% { transform: translate3d(15px, -20px, 0) scale(1.03); }
  66% { transform: translate3d(-15px, 15px, 0) scale(0.97); }
}

@keyframes float {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(0, -10px, 0); }
}

@keyframes fade-in {
  from { opacity: 0; transform: translate3d(0, 15px, 0); }
  to { opacity: 1; transform: translate3d(0, 0, 0); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
  50% { box-shadow: 0 0 35px rgba(16, 185, 129, 0.5); }
}

.animate-blob {
  animation: blob 15s ease-in-out infinite;
}

.animate-float {
  animation: float 4s ease-in-out infinite;
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out forwards;
}

.animation-delay-200 { animation-delay: 0.2s; opacity: 0; }
.animation-delay-400 { animation-delay: 0.4s; opacity: 0; }
.animation-delay-600 { animation-delay: 0.6s; opacity: 0; }
.animation-delay-2000 { animation-delay: 2s; }
.animation-delay-4000 { animation-delay: 4s; }

/* ===== HOVER EFFECTS - Minimal ===== */
.hover-lift {
  transition: transform 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
}

.hover-scale {
  transition: transform 0.3s ease;
}

.hover-scale:hover {
  transform: scale(1.015);
}

/* Smooth scroll */
html {
  scroll-behavior: smooth;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #0f172a;
}

::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
</style>
