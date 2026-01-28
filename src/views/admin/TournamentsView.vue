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
                    <CustomSelect
                      v-model="form.category"
                      :options="categoryOptions"
                      placeholder="Kategoriya tanlang"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Turi *</label>
                    <CustomSelect
                      v-model="form.type"
                      :options="typeOptions"
                      placeholder="Turi tanlang"
                    />
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

              <!-- Qatnashish qoidalari (YANGI MODEL) -->
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <h4 class="font-semibold text-slate-700 flex items-center gap-2">
                    <BookOpen class="w-4 h-4" />
                    Yo'nalishlar bo'yicha fan tanlash
                  </h4>
                  <button
                    @click="addParticipationRule"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500 text-white text-sm rounded-lg font-medium hover:bg-emerald-600 transition-colors"
                  >
                    <Plus class="w-4 h-4" />
                    Qo'shish
                  </button>
                </div>

                <!-- Tushunarli izoh -->
                <div class="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200 text-sm text-amber-700">
                  <AlertTriangle class="w-5 h-5 shrink-0 mt-0.5" />
                  <span>Har bir yo'nalish talabalari qaysi fanlardan qatnashishini belgilang. 
                  Qo'shilmasa — barcha yo'nalishlar erkin qatnashadi.</span>
                </div>

                <!-- Qoidalar ro'yxati -->
                <div v-if="form.participationRules.length > 0" class="space-y-4">
                  <div
                    v-for="(rule, index) in form.participationRules"
                    :key="rule.id || index"
                    class="bg-white border-2 border-slate-200 rounded-2xl overflow-hidden hover:border-emerald-300 transition-colors"
                  >
                    <!-- Kartochka sarlavhasi -->
                    <div class="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200">
                      <div class="flex items-center gap-3">
                        <span class="w-7 h-7 bg-emerald-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {{ index + 1 }}
                        </span>
                        <CustomSelect
                          v-model="rule.directionId"
                          :options="getDirectionOptions(rule.directionId)"
                          placeholder="Yo'nalish tanlang"
                          size="sm"
                          class="min-w-[220px]"
                        />
                      </div>
                      <button
                        @click="removeParticipationRule(index)"
                        class="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                        title="O'chirish"
                      >
                        <Trash2 class="w-4 h-4" />
                      </button>
                    </div>

                    <!-- Kartochka tanasi -->
                    <div class="p-4 space-y-4">
                      <!-- Tanlash turi -->
                      <div>
                        <label class="block text-xs font-medium text-slate-500 mb-2 uppercase tracking-wide">
                          Talaba qanday tanlaydi?
                        </label>
                        <div class="grid grid-cols-3 gap-2">
                          <label
                            :class="[
                              'flex flex-col items-center gap-2 p-3 rounded-xl border-2 cursor-pointer transition-all text-center',
                              rule.selectionMode === 'fixed'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-slate-200 hover:border-blue-300'
                            ]"
                          >
                            <input type="radio" v-model="rule.selectionMode" value="fixed" class="sr-only" />
                            <Lock :class="['w-6 h-6', rule.selectionMode === 'fixed' ? 'text-blue-500' : 'text-slate-400']" />
                            <span class="text-xs font-medium">Avtomatik</span>
                            <span class="text-[10px] text-slate-500">Tanlash yo'q</span>
                          </label>
                          <label
                            :class="[
                              'flex flex-col items-center gap-2 p-3 rounded-xl border-2 cursor-pointer transition-all text-center',
                              rule.selectionMode === 'single'
                                ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                                : 'border-slate-200 hover:border-emerald-300'
                            ]"
                          >
                            <input type="radio" v-model="rule.selectionMode" value="single" class="sr-only" />
                            <MousePointer :class="['w-6 h-6', rule.selectionMode === 'single' ? 'text-emerald-500' : 'text-slate-400']" />
                            <span class="text-xs font-medium">Bittasini</span>
                            <span class="text-[10px] text-slate-500">1 ta tanlaydi</span>
                          </label>
                          <label
                            :class="[
                              'flex flex-col items-center gap-2 p-3 rounded-xl border-2 cursor-pointer transition-all text-center',
                              rule.selectionMode === 'multiple'
                                ? 'border-purple-500 bg-purple-50 text-purple-700'
                                : 'border-slate-200 hover:border-purple-300'
                            ]"
                          >
                            <input type="radio" v-model="rule.selectionMode" value="multiple" class="sr-only" />
                            <List :class="['w-6 h-6', rule.selectionMode === 'multiple' ? 'text-purple-500' : 'text-slate-400']" />
                            <span class="text-xs font-medium">Bir nechta</span>
                            <span class="text-[10px] text-slate-500">Ko'p tanlaydi</span>
                          </label>
                        </div>
                      </div>

                      <!-- Fanlar tanlash -->
                      <div>
                        <label class="block text-xs font-medium text-slate-500 mb-2 uppercase tracking-wide">
                          Qaysi fanlardan? 
                          <span class="text-emerald-500 normal-case">({{ rule.allowedSubjectIds?.length || 0 }} ta)</span>
                        </label>
                        <div class="flex flex-wrap gap-2">
                          <label
                            v-for="subject in dataStore.subjects"
                            :key="subject.id"
                            :class="[
                              'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border-2 cursor-pointer transition-all text-sm',
                              rule.allowedSubjectIds?.includes(subject.id)
                                ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                                : 'border-slate-200 bg-white hover:border-emerald-300 text-slate-600'
                            ]"
                          >
                            <input
                              type="checkbox"
                              :value="subject.id"
                              v-model="rule.allowedSubjectIds"
                              class="sr-only"
                            />
                            <BookOpen class="w-3.5 h-3.5" />
                            <span>{{ subject.name }}</span>
                            <Check v-if="rule.allowedSubjectIds?.includes(subject.id)" class="w-3.5 h-3.5" />
                          </label>
                        </div>
                      </div>

                      <!-- Multiple uchun min/max -->
                      <div v-if="rule.selectionMode === 'multiple'" class="flex items-center gap-3 p-3 bg-purple-50 rounded-xl">
                        <span class="text-sm text-purple-700">Talaba</span>
                        <input
                          v-model.number="rule.minSelect"
                          type="number"
                          min="1"
                          class="w-14 px-2 py-1 text-center border border-purple-300 rounded-lg text-sm font-medium"
                        />
                        <span class="text-sm text-purple-700">dan</span>
                        <input
                          v-model.number="rule.maxSelect"
                          type="number"
                          :min="rule.minSelect || 1"
                          class="w-14 px-2 py-1 text-center border border-purple-300 rounded-lg text-sm font-medium"
                        />
                        <span class="text-sm text-purple-700">gacha fan tanlaydi</span>
                      </div>

                      <!-- Natija preview -->
                      <div class="p-3 bg-slate-100 rounded-xl text-sm text-slate-600">
                        <strong class="text-slate-800">{{ getDirectionCode(rule.directionId) }}</strong> talabasi: 
                        <span v-if="!rule.directionId" class="text-amber-600">Yo'nalish tanlanmagan</span>
                        <span v-else-if="!rule.allowedSubjectIds?.length" class="text-amber-600">Fan tanlanmagan</span>
                        <span v-else-if="rule.selectionMode === 'fixed'" class="text-blue-600">
                          {{ getFirstSubjectName(rule.allowedSubjectIds) }} fanidan qatnashadi (avtomatik)
                        </span>
                        <span v-else-if="rule.selectionMode === 'single'" class="text-emerald-600">
                          {{ rule.allowedSubjectIds.length }} fandan bittasini tanlaydi
                        </span>
                        <span v-else class="text-purple-600">
                          {{ rule.allowedSubjectIds.length }} fandan {{ rule.minSelect }}-{{ rule.maxSelect }} tasini tanlaydi
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Bo'sh holat -->
                <div v-else class="p-8 bg-slate-50 rounded-2xl text-center border-2 border-dashed border-slate-200">
                  <GraduationCap class="w-12 h-12 mx-auto text-slate-300 mb-3" />
                  <p class="text-slate-600 font-medium">Hozircha barcha yo'nalishlar qatnashadi</p>
                  <p class="text-sm text-slate-400 mt-1">
                    Faqat ma'lum yo'nalishlar qatnashishi kerak bo'lsa, yuqoridagi "Qo'shish" tugmasini bosing
                  </p>
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
                    <p class="text-slate-500">Ism, Familiya, Telefon, Guruh, Izoh{{ form.isSubjectBased ? ', Fan' : '' }}</p>
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
                        <CustomSelect
                          v-model="field.type"
                          :options="fieldTypeOptions"
                          placeholder="Turi"
                          size="sm"
                        />
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
  Brain, Dumbbell, Palette, FlaskConical, BookOpen, ChevronDown,
  Award, Star, PartyPopper, FileQuestion, Type, Hash, List, AlignLeft,
  Lock, MousePointer, Pointer, GraduationCap
} from 'lucide-vue-next'
import CustomSelect from '../../components/ui/CustomSelect.vue'

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
const activeSubjectDropdown = ref(null) // Fan dropdown uchun

const categories = [
  { value: 'all', label: 'Barchasi', icon: Trophy },
  { value: 'intellektual', label: 'Intellektual', icon: Brain },
  { value: 'sport', label: 'Sport', icon: Dumbbell },
  { value: 'ijodiy', label: 'Ijodiy', icon: Palette },
  { value: 'ilmiy', label: 'Ilmiy', icon: FlaskConical }
]

// CustomSelect uchun options (Lucide icons)
const categoryOptions = [
  { value: 'intellektual', label: 'Intellektual', icon: Brain },
  { value: 'sport', label: 'Sport', icon: Dumbbell },
  { value: 'ijodiy', label: 'Ijodiy', icon: Palette },
  { value: 'ilmiy', label: 'Ilmiy', icon: FlaskConical }
]

const typeOptions = [
  { value: 'olimpiada', label: 'Olimpiada', icon: Trophy },
  { value: 'chempionat', label: 'Chempionat', icon: Award },
  { value: 'tanlov', label: 'Tanlov', icon: Star },
  { value: 'festival', label: 'Festival', icon: PartyPopper },
  { value: 'boshqa', label: 'Boshqa', icon: FileQuestion }
]

const fieldTypeOptions = [
  { value: 'text', label: 'Matn', icon: Type },
  { value: 'number', label: 'Raqam', icon: Hash },
  { value: 'select', label: 'Tanlash', icon: List },
  { value: 'textarea', label: 'Katta matn', icon: AlignLeft }
]

const defaultForm = {
  title: '',
  description: '',
  category: 'intellektual',
  type: 'olimpiada',
  // YANGI MODEL: participationRules o'rniga isSubjectBased va subjectIds
  participationRules: [],
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

// Barcha fanlarni olish
const subjects = computed(() => dataStore.subjects.filter(s => s.isActive))

// ==========================================
// YANGI MODEL FUNKSIYALARI
// ==========================================

// Qatnashish qoidasi qo'shish
const addParticipationRule = () => {
  const newId = Date.now()
  form.value.participationRules.push({
    id: newId,
    directionId: null,
    allowedSubjectIds: [],
    selectionMode: 'single',
    minSelect: 1,
    maxSelect: 1
  })
}

// Qatnashish qoidasini o'chirish
const removeParticipationRule = (index) => {
  form.value.participationRules.splice(index, 1)
}

// Mavjud (tanlangan bo'lmagan) yo'nalishlarni olish
const getAvailableDirections = (currentDirectionId) => {
  const usedDirectionIds = form.value.participationRules
    .map(r => r.directionId)
    .filter(id => id !== null && id !== currentDirectionId)
  
  return dataStore.directions.filter(d => 
    d.isActive && !usedDirectionIds.includes(d.id)
  )
}

// Yo'nalish options generatori (CustomSelect uchun)
const getDirectionOptions = (currentDirectionId) => {
  const availableDirections = getAvailableDirections(currentDirectionId)
  return availableDirections.map(dir => ({
    value: dir.id,
    label: `${dir.code} - ${dir.name}`,
    icon: GraduationCap
  }))
}

// Yo'nalish nomini olish
const getDirectionName = (directionId) => {
  if (!directionId) return 'Tanlanmagan'
  const direction = dataStore.getDirectionById(directionId)
  return direction ? `${direction.code} - ${direction.name}` : 'Noma\'lum'
}

// Birinchi fan nomini olish (fixed rejim uchun)
const getFirstSubjectName = (subjectIds) => {
  if (!subjectIds || subjectIds.length === 0) return 'Tanlanmagan'
  const subject = dataStore.getSubjectById(subjectIds[0])
  return subject?.name || 'Noma\'lum'
}

// Fan nomini olish
const getSubjectName = (subjectId) => {
  const subject = dataStore.getSubjectById(subjectId)
  return subject?.name || ''
}

// Yo'nalish kodini olish
const getDirectionCode = (directionId) => {
  if (!directionId) return '—'
  const direction = dataStore.getDirectionById(directionId)
  return direction?.code || '—'
}

// Fan dropdown toggle
const toggleSubjectDropdown = (index) => {
  activeSubjectDropdown.value = activeSubjectDropdown.value === index ? null : index
}

// Modal yopilganda dropdown ham yopilsin
const closeModal = () => {
  showModal.value = false
  activeSubjectDropdown.value = null
}

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
  form.value = { 
    ...defaultForm, 
    customFields: [], 
    participationRules: [] // YANGI MODEL
  }
  showModal.value = true
}

const editTournament = (tournament) => {
  isEditing.value = true
  form.value = {
    ...tournament,
    // YANGI MODEL: participationRules ni ko'chirish
    participationRules: tournament.participationRules 
      ? tournament.participationRules.map(r => ({
          ...r,
          allowedSubjectIds: r.allowedSubjectIds || []
        }))
      : [],
    customFields: (tournament.customFields || []).map(f => ({
      ...f,
      optionsText: f.options ? f.options.join(', ') : ''
    }))
  }
  showModal.value = true
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

  // YANGI MODEL: Qatnashish qoidalarini validatsiya qilish
  for (const rule of form.value.participationRules) {
    if (!rule.directionId) {
      toast.error('Barcha qoidalar uchun yo\'nalish tanlang')
      return
    }
    if (!rule.allowedSubjectIds || rule.allowedSubjectIds.length === 0) {
      toast.error('Barcha qoidalar uchun kamida bitta fan tanlang')
      return
    }
    if (rule.selectionMode === 'fixed' && rule.allowedSubjectIds.length > 1) {
      toast.error('Fixed rejimda faqat bitta fan tanlanishi kerak')
      return
    }
    if (rule.selectionMode === 'multiple') {
      if (rule.minSelect < 1) {
        toast.error('Minimum tanlash 1 dan kam bo\'lishi mumkin emas')
        return
      }
      if (rule.maxSelect < rule.minSelect) {
        toast.error('Maximum tanlash minimum dan kam bo\'lishi mumkin emas')
        return
      }
    }
  }

  const data = {
    ...form.value,
    // YANGI MODEL
    participationRules: form.value.participationRules.map(r => ({
      id: r.id,
      directionId: r.directionId,
      allowedSubjectIds: r.allowedSubjectIds,
      selectionMode: r.selectionMode,
      minSelect: r.selectionMode === 'multiple' ? r.minSelect : 1,
      maxSelect: r.selectionMode === 'multiple' ? r.maxSelect : 1
    })),
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

/* Custom Select Styling */
.custom-select {
  @apply w-full pl-4 pr-10 py-3 text-sm font-medium text-slate-700 
         bg-gradient-to-b from-white to-slate-50 
         border-2 border-slate-200 rounded-xl 
         appearance-none cursor-pointer
         transition-all duration-200 ease-out
         hover:border-emerald-400 hover:shadow-md hover:shadow-emerald-100
         focus:outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10;
}

.custom-select-sm {
  @apply py-2 pl-3 pr-9 text-sm rounded-lg;
}

.custom-select option {
  @apply py-3 px-4 text-slate-700 bg-white;
}

.custom-select option:checked {
  @apply bg-emerald-50 text-emerald-700;
}

.custom-select option:hover {
  @apply bg-emerald-50;
}

.select-icon {
  @apply absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none
         transition-transform duration-200;
}

.custom-select:focus + .select-icon {
  @apply text-emerald-500 rotate-180;
}

.custom-select:hover + .select-icon {
  @apply text-emerald-400;
}
</style>
