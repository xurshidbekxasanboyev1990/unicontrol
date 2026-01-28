<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Turnirlar va Musobaqalar</h1>
        <p class="text-slate-500 mt-1">Bellashuvlarni e'lon qiling va ro'yxatdan o'tishlarni boshqaring</p>
      </div>
      <button
        @click="openCreateModal"
        class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/30 transition-all"
      >
        <Plus class="w-5 h-5" />
        Yangi turnir
      </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="selectedCategory = cat.value"
        :class="[
          'px-4 py-2 rounded-xl text-sm font-medium transition-all',
          selectedCategory === cat.value
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg'
            : 'bg-white border border-slate-200 text-slate-600 hover:border-emerald-300'
        ]"
      >
        <component :is="cat.icon" class="w-4 h-4 inline mr-2" />
        {{ cat.label }}
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <Trophy class="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ dataStore.tournaments.length }}</p>
            <p class="text-xs text-slate-500">Jami turnirlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <Zap class="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ activeTournaments.length }}</p>
            <p class="text-xs text-slate-500">Faol turnirlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
            <Users class="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ totalRegistrations }}</p>
            <p class="text-xs text-slate-500">Jami ro'yxatlar</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
            <Calendar class="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p class="text-2xl font-bold text-slate-800">{{ upcomingCount }}</p>
            <p class="text-xs text-slate-500">Kelayotgan</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tournaments Grid -->
    <div class="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div
        v-for="tournament in filteredTournaments"
        :key="tournament.id"
        class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl hover:border-emerald-200 transition-all group"
      >
        <!-- Header -->
        <div :class="['p-4 text-white relative overflow-hidden', getCategoryGradient(tournament.category)]">
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div class="relative">
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-2">
                <component :is="getCategoryIcon(tournament.category)" class="w-5 h-5" />
                <span class="text-sm font-medium opacity-90">{{ getCategoryLabel(tournament.category) }}</span>
              </div>
              <span :class="[
                'px-2.5 py-1 text-xs font-bold rounded-lg',
                tournament.isActive ? 'bg-white/20 text-white' : 'bg-red-500/80 text-white'
              ]">
                {{ tournament.isActive ? 'Faol' : 'Nofaol' }}
              </span>
            </div>
            <h3 class="text-lg font-bold mt-2 line-clamp-2">{{ tournament.title }}</h3>
          </div>
        </div>

        <!-- Body -->
        <div class="p-4 space-y-3">
          <p class="text-sm text-slate-600 line-clamp-2">{{ tournament.description }}</p>

          <div class="space-y-2">
            <div class="flex items-center gap-2 text-sm">
              <Calendar class="w-4 h-4 text-slate-400" />
              <span class="text-slate-600">{{ formatDate(tournament.startDate) }}</span>
              <span v-if="tournament.startDate !== tournament.endDate" class="text-slate-400">
                - {{ formatDate(tournament.endDate) }}
              </span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <MapPin class="w-4 h-4 text-slate-400" />
              <span class="text-slate-600">{{ tournament.location }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <Clock class="w-4 h-4 text-slate-400" />
              <span :class="isDeadlinePassed(tournament.registrationDeadline) ? 'text-red-500' : 'text-emerald-600'">
                Ro'yxat: {{ formatDate(tournament.registrationDeadline) }}
              </span>
            </div>
          </div>

          <!-- Registration stats -->
          <div class="flex items-center justify-between pt-3 border-t border-slate-100">
            <div class="flex items-center gap-2">
              <Users class="w-4 h-4 text-slate-400" />
              <span class="text-sm text-slate-600">
                {{ tournament.registrations.length }} / {{ tournament.maxParticipants }}
              </span>
            </div>
            <div class="flex items-center gap-1">
              <div class="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"
                  :style="{ width: `${(tournament.registrations.length / tournament.maxParticipants) * 100}%` }"
                ></div>
              </div>
              <span class="text-xs text-slate-500">
                {{ Math.round((tournament.registrations.length / tournament.maxParticipants) * 100) }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="px-4 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-2">
          <button
            @click="viewRegistrations(tournament)"
            class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
          >
            <ClipboardList class="w-4 h-4" />
            Ro'yxatlar ({{ tournament.registrations.length }})
          </button>
          <div class="flex items-center gap-1">
            <button
              @click="editTournament(tournament)"
              class="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Pencil class="w-4 h-4" />
            </button>
            <button
              @click="toggleStatus(tournament.id)"
              :class="[
                'p-2 rounded-lg transition-colors',
                tournament.isActive 
                  ? 'text-slate-400 hover:text-amber-500 hover:bg-amber-50'
                  : 'text-amber-500 hover:text-emerald-500 hover:bg-emerald-50'
              ]"
            >
              <Power class="w-4 h-4" />
            </button>
            <button
              @click="confirmDelete(tournament)"
              class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="filteredTournaments.length === 0" class="text-center py-16 bg-white rounded-2xl border border-slate-200">
      <Trophy class="w-16 h-16 mx-auto text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-slate-600">Turnirlar topilmadi</h3>
      <p class="text-slate-400 mt-1">Yangi turnir yarating</p>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="closeModal"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden">
            <!-- Modal header -->
            <div class="flex items-center justify-between p-6 border-b border-slate-100">
              <h3 class="text-xl font-bold text-slate-800">
                {{ isEditing ? 'Turnirni tahrirlash' : 'Yangi turnir yaratish' }}
              </h3>
              <button @click="closeModal" class="p-2 hover:bg-slate-100 rounded-xl transition-colors">
                <X class="w-5 h-5 text-slate-400" />
              </button>
            </div>

            <!-- Modal body -->
            <div class="p-6 overflow-y-auto max-h-[calc(90vh-180px)] space-y-6">
              <!-- Basic info -->
              <div class="space-y-4">
                <h4 class="font-semibold text-slate-700 flex items-center gap-2">
                  <FileText class="w-4 h-4" />
                  Asosiy ma'lumotlar
                </h4>
                
                <div class="grid md:grid-cols-2 gap-4">
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-slate-700 mb-1">Turnir nomi *</label>
                    <input
                      v-model="form.title"
                      type="text"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                      placeholder="Masalan: Dasturlash olimpiadasi"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Kategoriya *</label>
                    <select v-model="form.category" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                      <option value="intellektual">🧠 Intellektual</option>
                      <option value="sport">⚽ Sport</option>
                      <option value="ijodiy">🎨 Ijodiy</option>
                      <option value="ilmiy">🔬 Ilmiy</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Turi *</label>
                    <select v-model="form.type" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500">
                      <option value="olimpiada">Olimpiada</option>
                      <option value="chempionat">Chempionat</option>
                      <option value="tanlov">Tanlov</option>
                      <option value="festival">Festival</option>
                      <option value="boshqa">Boshqa</option>
                    </select>
                  </div>

                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-slate-700 mb-1">Tavsif *</label>
                    <textarea
                      v-model="form.description"
                      rows="3"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                      placeholder="Turnir haqida batafsil ma'lumot..."
                    ></textarea>
                  </div>
                </div>
              </div>

              <!-- Date & Location -->
              <div class="space-y-4">
                <h4 class="font-semibold text-slate-700 flex items-center gap-2">
                  <Calendar class="w-4 h-4" />
                  Sana va joy
                </h4>
                
                <div class="grid md:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Boshlanish sanasi *</label>
                    <input
                      v-model="form.startDate"
                      type="date"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Tugash sanasi *</label>
                    <input
                      v-model="form.endDate"
                      type="date"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Ro'yxat muddati *</label>
                    <input
                      v-model="form.registrationDeadline"
                      type="date"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    />
                  </div>
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-slate-700 mb-1">Manzil *</label>
                    <input
                      v-model="form.location"
                      type="text"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                      placeholder="Masalan: A-korpus, 301-xona"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Max ishtirokchilar *</label>
                    <input
                      v-model.number="form.maxParticipants"
                      type="number"
                      min="1"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    />
                  </div>
                </div>
              </div>

              <!-- Additional info -->
              <div class="space-y-4">
                <h4 class="font-semibold text-slate-700 flex items-center gap-2">
                  <Gift class="w-4 h-4" />
                  Qo'shimcha
                </h4>
                
                <div class="grid md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Sovrin</label>
                    <input
                      v-model="form.prize"
                      type="text"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                      placeholder="Masalan: 1,000,000 so'm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Tashkilotchi</label>
                    <input
                      v-model="form.organizer"
                      type="text"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                      placeholder="Masalan: IT fakulteti"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Bog'lanish telefoni</label>
                    <input
                      v-model="form.contactPhone"
                      type="text"
                      class="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                      placeholder="+998 90 123 45 67"
                    />
                  </div>
                </div>
              </div>

              <!-- Custom fields -->
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <h4 class="font-semibold text-slate-700 flex items-center gap-2">
                    <ListPlus class="w-4 h-4" />
                    Ro'yxatdan o'tish maydonlari
                  </h4>
                  <button
                    @click="addCustomField"
                    class="text-sm text-emerald-600 hover:text-emerald-700 font-medium flex items-center gap-1"
                  >
                    <Plus class="w-4 h-4" />
                    Maydon qo'shish
                  </button>
                </div>

                <div class="space-y-3">
                  <!-- Default fields info -->
                  <div class="p-3 bg-slate-50 rounded-xl text-sm text-slate-600">
                    <p class="font-medium mb-1">Standart maydonlar (avtomatik):</p>
                    <p class="text-slate-500">Ism, Familiya, Telefon, Guruh, Izoh</p>
                  </div>

                  <!-- Custom fields list -->
                  <div
                    v-for="(field, index) in form.customFields"
                    :key="index"
                    class="p-4 bg-white border border-slate-200 rounded-xl space-y-3"
                  >
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-slate-700">Maydon #{{ index + 1 }}</span>
                      <button
                        @click="removeCustomField(index)"
                        class="p-1.5 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                      >
                        <X class="w-4 h-4" />
                      </button>
                    </div>
                    
                    <div class="grid grid-cols-3 gap-3">
                      <div>
                        <label class="block text-xs text-slate-500 mb-1">Maydon nomi</label>
                        <input
                          v-model="field.name"
                          type="text"
                          class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                          placeholder="Masalan: Sport turi"
                        />
                      </div>
                      <div>
                        <label class="block text-xs text-slate-500 mb-1">Turi</label>
                        <select
                          v-model="field.type"
                          class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                        >
                          <option value="text">Matn</option>
                          <option value="number">Raqam</option>
                          <option value="select">Tanlash</option>
                          <option value="textarea">Katta matn</option>
                        </select>
                      </div>
                      <div class="flex items-end">
                        <label class="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" v-model="field.required" class="w-4 h-4 text-emerald-500 rounded" />
                          <span class="text-sm text-slate-600">Majburiy</span>
                        </label>
                      </div>
                    </div>

                    <!-- Options for select type -->
                    <div v-if="field.type === 'select'" class="space-y-2">
                      <label class="block text-xs text-slate-500">Variantlar (vergul bilan ajrating)</label>
                      <input
                        v-model="field.optionsText"
                        type="text"
                        class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                        placeholder="Variant 1, Variant 2, Variant 3"
                        @input="updateFieldOptions(field)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Modal footer -->
            <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-100 bg-slate-50">
              <button
                @click="closeModal"
                class="px-5 py-2.5 text-slate-600 hover:bg-slate-200 rounded-xl font-medium transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="saveTournament"
                class="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all"
              >
                {{ isEditing ? 'Saqlash' : 'Yaratish' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Registrations Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showRegistrationsModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showRegistrationsModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <!-- Modal header -->
            <div class="flex items-center justify-between p-6 border-b border-slate-100">
              <div>
                <h3 class="text-xl font-bold text-slate-800">Ro'yxatdan o'tganlar</h3>
                <p class="text-sm text-slate-500 mt-1">{{ selectedTournament?.title }}</p>
              </div>
              <button @click="showRegistrationsModal = false" class="p-2 hover:bg-slate-100 rounded-xl transition-colors">
                <X class="w-5 h-5 text-slate-400" />
              </button>
            </div>

            <!-- Modal body -->
            <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div v-if="selectedTournament?.registrations.length === 0" class="text-center py-12">
                <Users class="w-16 h-16 mx-auto text-slate-300 mb-4" />
                <p class="text-slate-500">Hali hech kim ro'yxatdan o'tmagan</p>
              </div>

              <div v-else class="space-y-4">
                <!-- Stats -->
                <div class="grid grid-cols-3 gap-4 mb-6">
                  <div class="bg-amber-50 rounded-xl p-4 text-center">
                    <p class="text-2xl font-bold text-amber-600">
                      {{ selectedTournament?.registrations.filter(r => r.status === 'pending').length }}
                    </p>
                    <p class="text-sm text-amber-700">Kutilmoqda</p>
                  </div>
                  <div class="bg-emerald-50 rounded-xl p-4 text-center">
                    <p class="text-2xl font-bold text-emerald-600">
                      {{ selectedTournament?.registrations.filter(r => r.status === 'approved').length }}
                    </p>
                    <p class="text-sm text-emerald-700">Tasdiqlangan</p>
                  </div>
                  <div class="bg-rose-50 rounded-xl p-4 text-center">
                    <p class="text-2xl font-bold text-rose-600">
                      {{ selectedTournament?.registrations.filter(r => r.status === 'rejected').length }}
                    </p>
                    <p class="text-sm text-rose-700">Rad etilgan</p>
                  </div>
                </div>

                <!-- Registrations list -->
                <div class="overflow-x-auto">
                  <table class="w-full">
                    <thead>
                      <tr class="text-left text-sm text-slate-500 border-b border-slate-200">
                        <th class="pb-3 font-medium">#</th>
                        <th class="pb-3 font-medium">Ism Familiya</th>
                        <th class="pb-3 font-medium">Telefon</th>
                        <th class="pb-3 font-medium">Guruh</th>
                        <th class="pb-3 font-medium">Holat</th>
                        <th class="pb-3 font-medium">Sana</th>
                        <th class="pb-3 font-medium">Amallar</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(reg, index) in selectedTournament?.registrations"
                        :key="reg.id"
                        class="border-b border-slate-100 hover:bg-slate-50"
                      >
                        <td class="py-3 text-sm text-slate-600">{{ index + 1 }}</td>
                        <td class="py-3">
                          <p class="font-medium text-slate-800">{{ reg.firstName }} {{ reg.lastName }}</p>
                          <button
                            v-if="reg.customFieldValues && Object.keys(reg.customFieldValues).length > 0"
                            @click="toggleRegDetails(reg.id)"
                            class="text-xs text-emerald-600 hover:underline"
                          >
                            {{ expandedReg === reg.id ? 'Yopish' : 'Batafsil' }}
                          </button>
                        </td>
                        <td class="py-3 text-sm text-slate-600">{{ reg.phone }}</td>
                        <td class="py-3 text-sm text-slate-600">{{ reg.group }}</td>
                        <td class="py-3">
                          <span :class="[
                            'px-2.5 py-1 text-xs font-medium rounded-lg',
                            reg.status === 'pending' && 'bg-amber-100 text-amber-700',
                            reg.status === 'approved' && 'bg-emerald-100 text-emerald-700',
                            reg.status === 'rejected' && 'bg-rose-100 text-rose-700'
                          ]">
                            {{ reg.status === 'pending' ? 'Kutilmoqda' : reg.status === 'approved' ? 'Tasdiqlangan' : 'Rad etilgan' }}
                          </span>
                        </td>
                        <td class="py-3 text-sm text-slate-500">{{ formatDateTime(reg.registeredAt) }}</td>
                        <td class="py-3">
                          <div class="flex items-center gap-1">
                            <button
                              v-if="reg.status !== 'approved'"
                              @click="updateStatus(selectedTournament.id, reg.id, 'approved')"
                              class="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                              title="Tasdiqlash"
                            >
                              <Check class="w-4 h-4" />
                            </button>
                            <button
                              v-if="reg.status !== 'rejected'"
                              @click="updateStatus(selectedTournament.id, reg.id, 'rejected')"
                              class="p-1.5 text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                              title="Rad etish"
                            >
                              <X class="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                      <!-- Expanded details row -->
                      <tr v-if="expandedReg" v-for="reg in selectedTournament?.registrations.filter(r => r.id === expandedReg)" :key="'detail-' + reg.id">
                        <td colspan="7" class="py-3 bg-slate-50">
                          <div class="px-4 space-y-2">
                            <div v-for="(value, key) in reg.customFieldValues" :key="key" class="flex gap-2 text-sm">
                              <span class="text-slate-500">{{ key }}:</span>
                              <span class="text-slate-800 font-medium">{{ value }}</span>
                            </div>
                            <div v-if="reg.comment" class="flex gap-2 text-sm">
                              <span class="text-slate-500">Izoh:</span>
                              <span class="text-slate-800">{{ reg.comment }}</span>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showDeleteModal = false"></div>
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-md p-6">
            <div class="text-center">
              <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle class="w-8 h-8 text-rose-500" />
              </div>
              <h3 class="text-xl font-bold text-slate-800 mb-2">O'chirishni tasdiqlang</h3>
              <p class="text-slate-500 mb-6">
                "{{ tournamentToDelete?.title }}" turnirini o'chirmoqchimisiz?
                Bu amalni qaytarib bo'lmaydi.
              </p>
              <div class="flex gap-3">
                <button
                  @click="showDeleteModal = false"
                  class="flex-1 px-5 py-2.5 border border-slate-200 text-slate-600 rounded-xl font-medium hover:bg-slate-50 transition-colors"
                >
                  Bekor qilish
                </button>
                <button
                  @click="deleteTournament"
                  class="flex-1 px-5 py-2.5 bg-rose-500 text-white rounded-xl font-semibold hover:bg-rose-600 transition-colors"
                >
                  O'chirish
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  Plus, Trophy, Users, Calendar, MapPin, Clock, Pencil, Trash2, Power, X,
  FileText, Gift, ListPlus, ClipboardList, Check, AlertTriangle, Zap,
  Brain, Dumbbell, Palette, FlaskConical
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

const showModal = ref(false)
const showRegistrationsModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedCategory = ref('all')
const selectedTournament = ref(null)
const tournamentToDelete = ref(null)
const expandedReg = ref(null)

const categories = [
  { value: 'all', label: 'Barchasi', icon: Trophy },
  { value: 'intellektual', label: 'Intellektual', icon: Brain },
  { value: 'sport', label: 'Sport', icon: Dumbbell },
  { value: 'ijodiy', label: 'Ijodiy', icon: Palette },
  { value: 'ilmiy', label: 'Ilmiy', icon: FlaskConical }
]

const defaultForm = {
  title: '',
  description: '',
  category: 'intellektual',
  type: 'olimpiada',
  startDate: '',
  endDate: '',
  registrationDeadline: '',
  location: '',
  maxParticipants: 50,
  prize: '',
  organizer: '',
  contactPhone: '',
  customFields: []
}

const form = ref({ ...defaultForm })

const filteredTournaments = computed(() => {
  if (selectedCategory.value === 'all') {
    return dataStore.tournaments
  }
  return dataStore.tournaments.filter(t => t.category === selectedCategory.value)
})

const activeTournaments = computed(() => {
  return dataStore.tournaments.filter(t => t.isActive)
})

const totalRegistrations = computed(() => {
  return dataStore.tournaments.reduce((sum, t) => sum + t.registrations.length, 0)
})

const upcomingCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return dataStore.tournaments.filter(t => t.startDate >= today).length
})

const getCategoryIcon = (category) => {
  const icons = {
    intellektual: Brain,
    sport: Dumbbell,
    ijodiy: Palette,
    ilmiy: FlaskConical
  }
  return icons[category] || Trophy
}

const getCategoryLabel = (category) => {
  const labels = {
    intellektual: 'Intellektual',
    sport: 'Sport',
    ijodiy: 'Ijodiy',
    ilmiy: 'Ilmiy'
  }
  return labels[category] || category
}

const getCategoryGradient = (category) => {
  const gradients = {
    intellektual: 'bg-gradient-to-r from-blue-500 to-indigo-500',
    sport: 'bg-gradient-to-r from-emerald-500 to-teal-500',
    ijodiy: 'bg-gradient-to-r from-purple-500 to-pink-500',
    ilmiy: 'bg-gradient-to-r from-amber-500 to-orange-500'
  }
  return gradients[category] || 'bg-gradient-to-r from-slate-500 to-slate-600'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const isDeadlinePassed = (deadline) => {
  return new Date(deadline) < new Date()
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = { ...defaultForm, customFields: [] }
  showModal.value = true
}

const editTournament = (tournament) => {
  isEditing.value = true
  form.value = {
    ...tournament,
    customFields: tournament.customFields.map(f => ({
      ...f,
      optionsText: f.options ? f.options.join(', ') : ''
    }))
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const addCustomField = () => {
  form.value.customFields.push({
    id: Date.now(),
    name: '',
    type: 'text',
    required: false,
    options: [],
    optionsText: ''
  })
}

const removeCustomField = (index) => {
  form.value.customFields.splice(index, 1)
}

const updateFieldOptions = (field) => {
  field.options = field.optionsText.split(',').map(o => o.trim()).filter(o => o)
}

const saveTournament = () => {
  if (!form.value.title || !form.value.description || !form.value.startDate || !form.value.registrationDeadline) {
    toast.error('Majburiy maydonlarni to\'ldiring')
    return
  }

  const data = {
    ...form.value,
    customFields: form.value.customFields.map(f => ({
      id: f.id,
      name: f.name,
      type: f.type,
      required: f.required,
      options: f.type === 'select' ? f.options : []
    }))
  }

  if (isEditing.value) {
    dataStore.updateTournament(form.value.id, data)
    toast.success('Turnir yangilandi')
  } else {
    dataStore.addTournament(data)
    toast.success('Turnir yaratildi')
  }
  closeModal()
}

const confirmDelete = (tournament) => {
  tournamentToDelete.value = tournament
  showDeleteModal.value = true
}

const deleteTournament = () => {
  dataStore.deleteTournament(tournamentToDelete.value.id)
  toast.success('Turnir o\'chirildi')
  showDeleteModal.value = false
  tournamentToDelete.value = null
}

const toggleStatus = (id) => {
  dataStore.toggleTournamentStatus(id)
}

const viewRegistrations = (tournament) => {
  selectedTournament.value = tournament
  expandedReg.value = null
  showRegistrationsModal.value = true
}

const toggleRegDetails = (regId) => {
  expandedReg.value = expandedReg.value === regId ? null : regId
}

const updateStatus = (tournamentId, regId, status) => {
  dataStore.updateRegistrationStatus(tournamentId, regId, status)
  toast.success(status === 'approved' ? 'Tasdiqlandi' : 'Rad etildi')
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95) translateY(10px);
}
</style>
