<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <RefreshCw class="w-12 h-12 text-emerald-500 animate-spin mx-auto mb-4" />
        <p class="text-slate-600">Ma'lumotlar yuklanmoqda...</p>
      </div>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 rounded-2xl p-4 sm:p-6 text-white">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-xl sm:text-2xl font-bold">Landing sahifa sozlamalari</h1>
            <p class="text-emerald-100 mt-1 text-sm sm:text-base">Landing page kontentini boshqarish</p>
          </div>
          <div class="flex items-center gap-3">
            <a href="/" target="_blank" class="flex items-center gap-2 bg-white/20 backdrop-blur px-4 py-2 rounded-xl text-sm font-medium hover:bg-white/30 transition-colors">
              <ExternalLink class="w-4 h-4" />
              Ko'rish
            </a>
            <div class="hidden sm:flex w-14 h-14 bg-white/20 backdrop-blur rounded-2xl items-center justify-center">
              <Globe class="w-7 h-7" />
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="flex overflow-x-auto border-b border-slate-200 scrollbar-hide">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm font-medium transition-all border-b-2 -mb-px whitespace-nowrap',
              activeTab === tab.id
                ? 'border-emerald-500 text-emerald-600 bg-emerald-50/50'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
            ]"
          >
            <component :is="tab.icon" class="w-4 h-4" />
            <span class="hidden sm:inline">{{ tab.label }}</span>
            <span class="sm:hidden">{{ tab.shortLabel || tab.label.split(' ')[0] }}</span>
          </button>
        </div>

        <div class="p-4 sm:p-6">

          <!-- =================== CARDS TAB =================== -->
          <div v-if="activeTab === 'cards'" class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">Landing Kartalar</h3>
              <button @click="openCardModal()" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                <Plus class="w-4 h-4" />
                Yangi karta
              </button>
            </div>

            <div v-if="featureCards.length === 0" class="text-center py-12 text-slate-400">
              <LayoutGrid class="w-12 h-12 mx-auto mb-3" />
              <p>Kartalar mavjud emas</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="card in featureCards"
                :key="card.id"
                class="bg-slate-50 rounded-xl p-4 border border-slate-200 hover:border-emerald-300 transition-colors group"
              >
                <div class="flex items-start justify-between mb-3">
                  <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', card.iconBg || 'bg-emerald-100']">
                    <component :is="getIcon(card.icon)" :class="['w-5 h-5', card.iconColor || 'text-emerald-600']" />
                  </div>
                  <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openCardModal(card)" class="p-1.5 text-slate-400 hover:text-emerald-500 hover:bg-white rounded-lg transition-colors">
                      <Pencil class="w-4 h-4" />
                    </button>
                    <button @click="deleteCard(card.id)" class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-white rounded-lg transition-colors">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <h4 class="font-semibold text-slate-800 mb-1">{{ card.title }}</h4>
                <p class="text-sm text-slate-500 line-clamp-2">{{ card.description }}</p>
                <div class="mt-3 flex items-center gap-2">
                  <span class="text-xs px-2 py-1 bg-slate-200 text-slate-600 rounded-full">{{ card.section }}</span>
                  <span v-if="card.active" class="text-xs px-2 py-1 bg-emerald-100 text-emerald-600 rounded-full">Faol</span>
                  <span v-else class="text-xs px-2 py-1 bg-slate-200 text-slate-400 rounded-full">Nofaol</span>
                </div>
              </div>
            </div>
          </div>

          <!-- =================== SOCIAL LINKS TAB =================== -->
          <div v-if="activeTab === 'social'" class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">Ijtimoiy Tarmoqlar</h3>
              <button @click="saveSocialLinks" :disabled="saving" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50">
                <Save v-if="!saving" class="w-4 h-4" />
                <RefreshCw v-else class="w-4 h-4 animate-spin" />
                Saqlash
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="social in socialLinks" :key="social.name" class="space-y-2">
                <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <component :is="getIcon(social.icon)" class="w-4 h-4" />
                  {{ social.name }}
                </label>
                <input
                  v-model="social.url"
                  type="url"
                  :placeholder="social.placeholder || social.name + ' URL'"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all"
                />
              </div>
            </div>
          </div>

          <!-- =================== TEAM TAB =================== -->
          <div v-if="activeTab === 'team'" class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">Loyiha Jamoasi</h3>
              <button @click="openTeamModal()" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                <UserPlus class="w-4 h-4" />
                Qo'shish
              </button>
            </div>

            <div v-if="teamMembers.length === 0" class="text-center py-12 text-slate-400">
              <Users class="w-12 h-12 mx-auto mb-3" />
              <p>Jamoa a'zolari mavjud emas</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="member in teamMembers"
                :key="member.id"
                class="bg-slate-50 rounded-xl p-4 border border-slate-200 hover:border-emerald-300 transition-colors group"
              >
                <div class="flex items-start gap-3">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-lg shrink-0">
                    {{ member.name?.charAt(0) || '?' }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between">
                      <div>
                        <h4 class="font-semibold text-slate-800">{{ member.name }}</h4>
                        <p class="text-sm text-slate-500">{{ member.position }}</p>
                      </div>
                      <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button @click="openTeamModal(member)" class="p-1.5 text-slate-400 hover:text-emerald-500 hover:bg-white rounded-lg transition-colors">
                          <Pencil class="w-4 h-4" />
                        </button>
                        <button @click="deleteTeamMember(member.id)" class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-white rounded-lg transition-colors">
                          <Trash2 class="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span :class="['text-xs px-2 py-1 rounded-full', getRoleColor(member.type)]">
                    {{ getRoleLabel(member.type) }}
                  </span>
                </div>
                <div v-if="member.social" class="mt-3 flex gap-2">
                  <a v-if="member.social.github" :href="member.social.github" target="_blank" class="text-slate-400 hover:text-slate-600 transition-colors">
                    <Github class="w-4 h-4" />
                  </a>
                  <a v-if="member.social.linkedin" :href="member.social.linkedin" target="_blank" class="text-slate-400 hover:text-blue-600 transition-colors">
                    <Linkedin class="w-4 h-4" />
                  </a>
                  <a v-if="member.social.telegram" :href="member.social.telegram" target="_blank" class="text-slate-400 hover:text-sky-500 transition-colors">
                    <Send class="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- =================== CONTACT TAB =================== -->
          <div v-if="activeTab === 'contact'" class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">Aloqa Ma'lumotlari</h3>
              <button @click="saveContactInfo" :disabled="saving" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50">
                <Save v-if="!saving" class="w-4 h-4" />
                <RefreshCw v-else class="w-4 h-4 animate-spin" />
                Saqlash
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Mail class="w-4 h-4" />
                  Email
                </label>
                <input v-model="contactInfo.email" type="email" placeholder="info@unicontrol.uz" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all" />
              </div>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Phone class="w-4 h-4" />
                  Telefon
                </label>
                <input v-model="contactInfo.phone" type="tel" placeholder="+998 90 123 45 67" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all" />
              </div>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Send class="w-4 h-4" />
                  Telegram
                </label>
                <input v-model="contactInfo.telegram" type="text" placeholder="@unicontrol_uz" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all" />
              </div>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <MapPin class="w-4 h-4" />
                  Manzil
                </label>
                <input v-model="contactInfo.address" type="text" placeholder="Toshkent sh., Chilonzor t." class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all" />
              </div>
            </div>
          </div>

          <!-- =================== HERO & ABOUT STATS TAB =================== -->
          <div v-if="activeTab === 'hero'" class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">Hero va About Statistika</h3>
              <button @click="saveHeroAndAbout" :disabled="saving" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50">
                <Save v-if="!saving" class="w-4 h-4" />
                <RefreshCw v-else class="w-4 h-4 animate-spin" />
                Saqlash
              </button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Hero Stats -->
              <div class="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-4">
                <h4 class="font-medium text-slate-700 flex items-center gap-2">
                  <Sparkles class="w-4 h-4 text-emerald-500" />
                  Hero bo'lim raqamlari
                </h4>
                <div class="space-y-3">
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Talabalar soni</label>
                    <input v-model="heroStats.students_count" type="text" placeholder="500+" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Guruhlar soni</label>
                    <input v-model="heroStats.groups_count" type="text" placeholder="50+" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Natija foizi</label>
                    <input v-model="heroStats.result_percent" type="text" placeholder="99%" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                </div>
              </div>

              <!-- About Stats -->
              <div class="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-4">
                <h4 class="font-medium text-slate-700 flex items-center gap-2">
                  <Info class="w-4 h-4 text-teal-500" />
                  Biz haqimizda raqamlari
                </h4>
                <div class="space-y-3">
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Tashkil etilgan sana</label>
                    <input v-model="aboutStats.founded" type="text" placeholder="01.10.2025" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Universitetlar soni</label>
                    <input v-model="aboutStats.universities" type="text" placeholder="1" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Foydalanuvchilar</label>
                    <input v-model="aboutStats.users" type="text" placeholder="500+" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                  <div class="space-y-1">
                    <label class="text-sm text-slate-600">Qo'llab-quvvatlash</label>
                    <input v-model="aboutStats.support" type="text" placeholder="24/7" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Preview -->
            <div class="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-5 border border-emerald-200">
              <h4 class="font-medium text-emerald-700 mb-4">Ko'rinishi (Preview)</h4>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div class="text-center">
                  <div class="text-2xl font-bold text-emerald-600">{{ heroStats.students_count || '-' }}</div>
                  <div class="text-sm text-slate-500">Talabalar</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-teal-600">{{ heroStats.groups_count || '-' }}</div>
                  <div class="text-sm text-slate-500">Guruhlar</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-cyan-600">{{ heroStats.result_percent || '-' }}</div>
                  <div class="text-sm text-slate-500">Natija</div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </template>

    <!-- Card Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCardModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showCardModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
            <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">{{ editingCard ? 'Kartani tahrirlash' : 'Yangi karta' }}</h3>
              <button @click="showCardModal = false" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg"><X class="w-5 h-5" /></button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Sarlavha</label>
                <input v-model="cardForm.title" type="text" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" placeholder="Karta sarlavhasi" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Tavsif</label>
                <textarea v-model="cardForm.description" rows="3" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 resize-none" placeholder="Karta tavsifi"></textarea>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Bo'lim</label>
                  <select v-model="cardForm.section" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300">
                    <option value="features">Xususiyatlar</option>
                    <option value="how-it-works">Qanday ishlaydi</option>
                    <option value="testimonials">Fikrlar</option>
                    <option value="faq">FAQ</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Ikon</label>
                  <select v-model="cardForm.icon" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300">
                    <option value="Zap">Zap</option>
                    <option value="Users">Users</option>
                    <option value="Calendar">Calendar</option>
                    <option value="BarChart3">BarChart</option>
                    <option value="Brain">Brain</option>
                    <option value="Shield">Shield</option>
                    <option value="Bell">Bell</option>
                    <option value="BookOpen">BookOpen</option>
                  </select>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <input type="checkbox" v-model="cardForm.active" id="cardActive" class="w-5 h-5 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500" />
                <label for="cardActive" class="text-sm text-slate-700">Faol holat</label>
              </div>
            </div>
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
              <button @click="showCardModal = false" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl text-sm font-medium transition-colors">Bekor qilish</button>
              <button @click="saveCard" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-sm font-medium transition-colors">
                {{ editingCard ? 'Saqlash' : "Qo'shish" }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Team Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showTeamModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showTeamModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
            <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">{{ editingMember ? 'Tahrirlash' : "Yangi a'zo" }}</h3>
              <button @click="showTeamModal = false" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg"><X class="w-5 h-5" /></button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Ism Familiya</label>
                <input v-model="teamForm.name" type="text" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" placeholder="To'liq ism" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Lavozim</label>
                <input v-model="teamForm.position" type="text" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10" placeholder="Masalan: Senior Developer" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Turi</label>
                <select v-model="teamForm.type" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300">
                  <option value="backend">Backend dasturchi</option>
                  <option value="frontend">Frontend dasturchi</option>
                  <option value="mobile">Mobil dasturchi</option>
                  <option value="fullstack">Full Stack dasturchi</option>
                  <option value="designer">UI/UX dizayner</option>
                  <option value="devops">DevOps muhandis</option>
                  <option value="pm">Loyiha menejeri</option>
                  <option value="qa">QA muhandis</option>
                </select>
              </div>
              <div class="space-y-3">
                <label class="block text-sm font-medium text-slate-700">Ijtimoiy tarmoqlar</label>
                <div class="flex items-center gap-2">
                  <Github class="w-4 h-4 text-slate-400 shrink-0" />
                  <input v-model="teamForm.social.github" type="url" class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-emerald-300" placeholder="GitHub URL" />
                </div>
                <div class="flex items-center gap-2">
                  <Linkedin class="w-4 h-4 text-slate-400 shrink-0" />
                  <input v-model="teamForm.social.linkedin" type="url" class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-emerald-300" placeholder="LinkedIn URL" />
                </div>
                <div class="flex items-center gap-2">
                  <Send class="w-4 h-4 text-slate-400 shrink-0" />
                  <input v-model="teamForm.social.telegram" type="url" class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-emerald-300" placeholder="Telegram URL" />
                </div>
              </div>
            </div>
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
              <button @click="showTeamModal = false" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl text-sm font-medium transition-colors">Bekor qilish</button>
              <button @click="saveTeamMember" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-sm font-medium transition-colors">
                {{ editingMember ? 'Saqlash' : "Qo'shish" }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * Super Admin — Landing Page Settings
 * Real API bilan ishlaydi: GET/PUT /landing
 */
import {
  BarChart3, Bell, BookOpen, Brain, Calendar,
  ExternalLink, Github, Globe, Info, LayoutGrid,
  Linkedin, Mail, MapPin, Pencil, Phone, Plus,
  RefreshCw, Save, Send, Share2, Shield, ShieldCheck,
  Sparkles, Trash2, UserPlus, Users, X, Zap
} from 'lucide-vue-next'
import { markRaw, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useToastStore } from '../../stores/toast'

const toast = useToastStore()

// === State ===
const loading = ref(true)
const saving = ref(false)
const activeTab = ref('cards')

// Data from API
const featureCards = ref([])
const socialLinks = ref([])
const teamMembers = ref([])
const contactInfo = reactive({ email: '', phone: '', telegram: '', address: '' })
const heroStats = reactive({ students_count: '', groups_count: '', result_percent: '' })
const aboutStats = reactive({ founded: '', universities: '', users: '', support: '' })

// Tabs
const tabs = [
  { id: 'cards', label: 'Kartalar', icon: markRaw(LayoutGrid) },
  { id: 'social', label: 'Ijtimoiy tarmoqlar', shortLabel: 'Tarmoqlar', icon: markRaw(Share2) },
  { id: 'team', label: 'Jamoa', icon: markRaw(Users) },
  { id: 'contact', label: 'Aloqa', icon: markRaw(Phone) },
  { id: 'hero', label: 'Statistika', icon: markRaw(Sparkles) }
]

// Icons map
const iconComponents = {
  Zap: markRaw(Zap), Users: markRaw(Users), Calendar: markRaw(Calendar),
  BarChart3: markRaw(BarChart3), Brain: markRaw(Brain), Shield: markRaw(Shield),
  Bell: markRaw(Bell), BookOpen: markRaw(BookOpen), Github: markRaw(Github),
  Linkedin: markRaw(Linkedin), Send: markRaw(Send), Globe: markRaw(Globe),
  LayoutGrid: markRaw(LayoutGrid), Share2: markRaw(Share2), ShieldCheck: markRaw(ShieldCheck)
}
const getIcon = (name) => iconComponents[name] || iconComponents.Zap

// === Card Modal ===
const showCardModal = ref(false)
const editingCard = ref(null)
const cardForm = reactive({ title: '', description: '', section: 'features', icon: 'Zap', active: true })

const openCardModal = (card = null) => {
  if (card) {
    editingCard.value = card
    Object.assign(cardForm, { title: card.title, description: card.description, section: card.section, icon: card.icon, active: card.active })
  } else {
    editingCard.value = null
    Object.assign(cardForm, { title: '', description: '', section: 'features', icon: 'Zap', active: true })
  }
  showCardModal.value = true
}

const saveCard = async () => {
  if (!cardForm.title.trim()) {
    toast.error('Sarlavha kiritilishi kerak')
    return
  }
  if (editingCard.value) {
    const idx = featureCards.value.findIndex(c => c.id === editingCard.value.id)
    if (idx > -1) featureCards.value[idx] = { ...featureCards.value[idx], ...cardForm }
  } else {
    featureCards.value.push({ id: Date.now(), ...cardForm, iconBg: 'bg-emerald-100', iconColor: 'text-emerald-600' })
  }
  showCardModal.value = false
  await saveFeatureCards()
}

const deleteCard = async (id) => {
  if (!confirm("Kartani o'chirmoqchimisiz?")) return
  featureCards.value = featureCards.value.filter(c => c.id !== id)
  await saveFeatureCards()
}

const saveFeatureCards = async () => {
  try {
    saving.value = true
    await api.updateLandingFeatureCards(featureCards.value)
    toast.success('Kartalar saqlandi!')
  } catch (e) {
    console.error('Save feature cards error:', e)
    toast.error("Xatolik: Saqlab bo'lmadi")
  } finally {
    saving.value = false
  }
}

// === Team Modal ===
const showTeamModal = ref(false)
const editingMember = ref(null)
const teamForm = reactive({ name: '', position: '', type: 'fullstack', social: { github: '', linkedin: '', telegram: '' } })

const openTeamModal = (member = null) => {
  if (member) {
    editingMember.value = member
    Object.assign(teamForm, {
      name: member.name,
      position: member.position,
      type: member.type || 'fullstack',
      social: { github: '', linkedin: '', telegram: '', ...(member.social || {}) }
    })
  } else {
    editingMember.value = null
    Object.assign(teamForm, { name: '', position: '', type: 'fullstack', social: { github: '', linkedin: '', telegram: '' } })
  }
  showTeamModal.value = true
}

const saveTeamMember = async () => {
  if (!teamForm.name.trim()) {
    toast.error('Ism kiritilishi kerak')
    return
  }
  if (editingMember.value) {
    const idx = teamMembers.value.findIndex(m => m.id === editingMember.value.id)
    if (idx > -1) teamMembers.value[idx] = { ...teamMembers.value[idx], name: teamForm.name, position: teamForm.position, type: teamForm.type, social: { ...teamForm.social } }
  } else {
    teamMembers.value.push({ id: Date.now(), name: teamForm.name, position: teamForm.position, type: teamForm.type, social: { ...teamForm.social } })
  }
  showTeamModal.value = false
  await saveTeamMembers()
}

const deleteTeamMember = async (id) => {
  if (!confirm("A'zoni o'chirmoqchimisiz?")) return
  teamMembers.value = teamMembers.value.filter(m => m.id !== id)
  await saveTeamMembers()
}

const saveTeamMembers = async () => {
  try {
    saving.value = true
    await api.updateLandingTeamMembers(teamMembers.value)
    toast.success('Jamoa saqlandi!')
  } catch (e) {
    console.error('Save team members error:', e)
    toast.error("Xatolik: Saqlab bo'lmadi")
  } finally {
    saving.value = false
  }
}

// === Save Social Links ===
const saveSocialLinks = async () => {
  try {
    saving.value = true
    await api.updateLandingSocialLinks(socialLinks.value)
    toast.success('Ijtimoiy tarmoqlar saqlandi!')
  } catch (e) {
    console.error('Save social links error:', e)
    toast.error("Xatolik: Saqlab bo'lmadi")
  } finally {
    saving.value = false
  }
}

// === Save Contact Info ===
const saveContactInfo = async () => {
  try {
    saving.value = true
    await api.updateLandingContactInfo({ ...contactInfo })
    toast.success("Aloqa ma'lumotlari saqlandi!")
  } catch (e) {
    console.error('Save contact info error:', e)
    toast.error("Xatolik: Saqlab bo'lmadi")
  } finally {
    saving.value = false
  }
}

// === Save Hero & About Stats ===
const saveHeroAndAbout = async () => {
  try {
    saving.value = true
    await Promise.all([
      api.updateLandingHeroStats({ ...heroStats }),
      api.updateLandingAboutStats({ ...aboutStats })
    ])
    toast.success('Statistika saqlandi!')
  } catch (e) {
    console.error('Save hero/about error:', e)
    toast.error("Xatolik: Saqlab bo'lmadi")
  } finally {
    saving.value = false
  }
}

// === Helpers ===
const getRoleColor = (type) => {
  const colors = {
    backend: 'bg-blue-100 text-blue-600', frontend: 'bg-amber-100 text-amber-600',
    mobile: 'bg-violet-100 text-violet-600', fullstack: 'bg-emerald-100 text-emerald-600',
    designer: 'bg-pink-100 text-pink-600', devops: 'bg-orange-100 text-orange-600',
    pm: 'bg-cyan-100 text-cyan-600', qa: 'bg-red-100 text-red-600'
  }
  return colors[type] || 'bg-slate-100 text-slate-600'
}

const getRoleLabel = (type) => {
  const labels = {
    backend: 'Backend', frontend: 'Frontend', mobile: 'Mobile', fullstack: 'Full Stack',
    designer: 'UI/UX', devops: 'DevOps', pm: 'PM', qa: 'QA'
  }
  return labels[type] || type
}

// === Load Data from API ===
const loadData = async () => {
  loading.value = true
  try {
    const data = await api.getLandingSettings()

    featureCards.value = data.feature_cards || []
    socialLinks.value = data.social_links || []
    teamMembers.value = data.team_members || []

    if (data.contact_info) Object.assign(contactInfo, data.contact_info)
    if (data.hero_stats) Object.assign(heroStats, data.hero_stats)
    if (data.about_stats) Object.assign(aboutStats, data.about_stats)
  } catch (e) {
    console.error('Landing settings load error:', e)
    toast.error("Ma'lumotlarni yuklashda xatolik")
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .relative, .modal-leave-to .relative { transform: scale(0.95) translateY(10px); }
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
