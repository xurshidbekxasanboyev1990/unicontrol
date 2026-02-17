<template>
  <div class="space-y-6">

    <!-- ================ ACCESS LOADING ================ -->
    <div v-if="accessLoading" class="flex items-center justify-center py-32">
      <Loader2 :size="32" class="animate-spin text-indigo-500" />
    </div>

    <!-- ================ SUBSCRIPTION REQUIRED SCREEN ================ -->
    <div v-else-if="!hasAccess" class="flex items-center justify-center py-12">
      <div class="w-full max-w-lg text-center">
        <!-- Lock Icon -->
        <div class="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-violet-100 to-indigo-100 shadow-lg shadow-indigo-100/50">
          <Lock :size="40" class="text-indigo-500" />
        </div>

        <!-- Title -->
        <h2 class="mb-2 text-2xl font-bold text-slate-800 flex items-center justify-center gap-2">{{ $t('quiz.lockedTitle') }} <Lock :size="20" class="text-slate-400" /></h2>
        <p class="mb-6 text-sm text-slate-500 leading-relaxed">
          {{ $t('quiz.lockedDesc') }}
        </p>

        <!-- Plan Cards -->
        <div class="mb-8 grid grid-cols-3 gap-3">
          <!-- Plus -->
          <div class="rounded-2xl border-2 border-violet-200 bg-gradient-to-b from-violet-50 to-white p-4 transition-all hover:shadow-lg hover:shadow-violet-100/50 hover:-translate-y-1">
            <div class="mb-2 flex h-10 w-10 mx-auto items-center justify-center rounded-xl bg-violet-100">
              <Zap :size="20" class="text-violet-600" />
            </div>
            <h3 class="text-sm font-bold text-violet-700">Plus</h3>
            <p class="mt-1 text-xs text-slate-400">{{ $t('quiz.basicFeatures') }}</p>
          </div>
          <!-- Pro -->
          <div class="rounded-2xl border-2 border-amber-200 bg-gradient-to-b from-amber-50 to-white p-4 transition-all hover:shadow-lg hover:shadow-amber-100/50 hover:-translate-y-1">
            <div class="mb-2 flex h-10 w-10 mx-auto items-center justify-center rounded-xl bg-amber-100">
              <Crown :size="20" class="text-amber-600" />
            </div>
            <h3 class="text-sm font-bold text-amber-700">Pro</h3>
            <p class="mt-1 text-xs text-slate-400">{{ $t('quiz.extended') }}</p>
          </div>
          <!-- Unlimited -->
          <div class="rounded-2xl border-2 border-emerald-200 bg-gradient-to-b from-emerald-50 to-white p-4 transition-all hover:shadow-lg hover:shadow-emerald-100/50 hover:-translate-y-1">
            <div class="mb-2 flex h-10 w-10 mx-auto items-center justify-center rounded-xl bg-emerald-100">
              <Sparkles :size="20" class="text-emerald-600" />
            </div>
            <h3 class="text-sm font-bold text-emerald-700">Unlimited</h3>
            <p class="mt-1 text-xs text-slate-400">{{ $t('quiz.unlimited') }}</p>
          </div>
        </div>

        <!-- Features -->
        <div class="mb-8 rounded-2xl border border-slate-100 bg-slate-50 p-5 text-left">
          <h4 class="mb-3 text-sm font-semibold text-slate-700 flex items-center gap-1.5"><Sparkles :size="16" class="text-indigo-500" /> {{ $t('quiz.featureTitle') }}:</h4>
          <ul class="space-y-2 text-sm text-slate-600">
            <li class="flex items-center gap-2">
              <div class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-xs text-indigo-600">✓</div>
              {{ $t('quiz.featureCards') }}
            </li>
            <li class="flex items-center gap-2">
              <div class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-xs text-indigo-600">✓</div>
              {{ $t('quiz.featureFlashcard') }}
            </li>
            <li class="flex items-center gap-2">
              <div class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-xs text-indigo-600">✓</div>
              {{ $t('quiz.featureTest') }}
            </li>
            <li class="flex items-center gap-2">
              <div class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-xs text-indigo-600">✓</div>
              {{ $t('quiz.featureShare') }}
            </li>
          </ul>
        </div>

        <!-- Action Button -->
        <button
          @click="goToSubscription"
          class="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-indigo-500 to-violet-500 px-8 py-3.5 font-semibold text-white shadow-lg shadow-indigo-500/30 transition-all hover:from-indigo-600 hover:to-violet-600 hover:shadow-xl hover:-translate-y-0.5"
        >
          <ArrowUpCircle :size="20" />
          {{ $t('quiz.upgradeSubscription') }}
        </button>
      </div>
    </div>

    <!-- ================ MAIN CONTENT (HAS ACCESS) ================ -->
    <template v-else>
    <!-- ================ HEADER ================ -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800 flex items-center gap-2"><BookOpen :size="24" class="text-indigo-500" /> {{ $t('quiz.title') }}</h1>
        <p class="text-sm text-slate-500">{{ $t('quiz.subtitle') }}</p>
      </div>
      <button
        @click="openCreateModal"
        class="flex items-center gap-2 rounded-xl bg-indigo-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-indigo-500/30 transition-all hover:bg-indigo-600"
      >
        <Plus :size="20" />
        {{ $t('quiz.newSet') }}
      </button>
    </div>

    <!-- ================ TABS ================ -->
    <div class="flex items-center gap-3">
      <div class="flex rounded-xl bg-slate-100 p-1">
        <button
          @click="activeTab = 'all'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'all' ? 'bg-white text-indigo-600 shadow' : 'text-slate-600 hover:text-slate-800'"
        >
          {{ $t('quiz.groupSets') }}
        </button>
        <button
          @click="activeTab = 'my'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'my' ? 'bg-white text-indigo-600 shadow' : 'text-slate-600 hover:text-slate-800'"
        >
          {{ $t('quiz.mySets') }}
        </button>
      </div>

      <div class="relative ml-auto">
        <Search :size="18" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          type="text"
          :placeholder="$t('quiz.searchPlaceholder')"
          class="w-48 rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm focus:border-indigo-500 focus:outline-none sm:w-64"
        />
      </div>
    </div>

    <!-- ================ LOADING ================ -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-indigo-500" />
    </div>

    <!-- ================ QUIZ SETS GRID ================ -->
    <div v-else-if="quizSets.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="set in quizSets"
        :key="set.id"
        class="group relative cursor-pointer overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:shadow-lg hover:-translate-y-1"
        @click="openSet(set)"
      >
        <!-- Color Bar -->
        <div class="h-2" :style="{ background: set.color || '#3b82f6' }"></div>
        
        <div class="p-5">
          <!-- Title & Subject -->
          <div class="mb-3 flex items-start justify-between">
            <div>
              <h3 class="text-lg font-bold text-slate-800">{{ set.title }}</h3>
              <p v-if="set.subject" class="text-sm text-indigo-500">{{ set.subject }}</p>
            </div>
            <div v-if="set.creator_id === userId" class="opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click.stop="editSet(set)" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-indigo-600">
                <Pencil :size="16" />
              </button>
            </div>
          </div>

          <!-- Description -->
          <p v-if="set.description" class="mb-3 line-clamp-2 text-sm text-slate-500">{{ set.description }}</p>

          <!-- Stats -->
          <div class="flex items-center gap-4 text-sm">
            <span class="flex items-center gap-1 text-slate-500">
              <Layers :size="14" />
              {{ set.cards_count }} {{ $t('quiz.cards') }}
            </span>
            <span class="flex items-center gap-1 text-slate-500">
              <Play :size="14" />
              {{ set.play_count }} {{ $t('quiz.times') }}
            </span>
          </div>

          <!-- Footer -->
          <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
            <div class="flex items-center gap-2">
              <div class="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-600">
                {{ (set.creator_name || '?')[0] }}
              </div>
              <span class="text-xs text-slate-400">{{ set.creator_name }}</span>
            </div>
            <div class="flex gap-1">
              <button
                @click.stop="startFlashcard(set)"
                class="rounded-lg bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-600 transition-all hover:bg-emerald-100"
                :title="$t('quiz.cardMode')"
              >
                <BookOpen :size="14" />
              </button>
              <button
                @click.stop="startQuiz(set)"
                class="rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-600 transition-all hover:bg-indigo-100"
                :title="$t('quiz.testMode')"
              >
                <Zap :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ================ EMPTY STATE ================ -->
    <div v-else class="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 py-20">
      <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-100">
        <BookOpen :size="28" class="text-indigo-500" />
      </div>
      <h3 class="mb-1 text-lg font-semibold text-slate-700">{{ $t('quiz.noSets') }}</h3>
      <p class="mb-4 text-sm text-slate-400">{{ $t('quiz.createFirst') }}</p>
      <button
        @click="openCreateModal"
        class="rounded-xl bg-indigo-500 px-6 py-2.5 font-medium text-white hover:bg-indigo-600"
      >
        + {{ $t('quiz.newSet') }}
      </button>
    </div>

    <!-- ===============================================================
         CREATE / EDIT SET MODAL
         =============================================================== -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="showCreateModal = false">
      <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <!-- Header -->
        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white p-5">
          <h2 class="text-xl font-bold text-slate-800">
            {{ editingSet ? $t('quiz.editSet') : $t('quiz.createSet') }}
          </h2>
          <button @click="showCreateModal = false" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100">
            <X :size="20" />
          </button>
        </div>

        <div class="space-y-5 p-5">
          <!-- Title -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">{{ $t('quiz.setTitle') }} *</label>
            <input
              v-model="formData.title"
              type="text"
              placeholder="Masalan: Biologiya - 3-bob savollari"
              class="w-full rounded-xl border border-slate-200 p-3 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <!-- Subject + Color -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">{{ $t('quiz.subjectName') }}</label>
              <input
                v-model="formData.subject"
                type="text"
                placeholder="Biologiya, Matematika..."
                class="w-full rounded-xl border border-slate-200 p-3 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">{{ $t('quiz.color') }}</label>
              <div class="flex gap-2 pt-1.5">
                <button
                  v-for="c in colors"
                  :key="c"
                  @click="formData.color = c"
                  class="h-8 w-8 rounded-full border-2 transition-all"
                  :style="{ background: c }"
                  :class="formData.color === c ? 'border-slate-800 scale-110' : 'border-transparent'"
                ></button>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">{{ $t('quiz.descriptionLabel') }}</label>
            <textarea
              v-model="formData.description"
              rows="2"
              placeholder="Qisqacha tavsif..."
              class="w-full rounded-xl border border-slate-200 p-3 focus:border-indigo-500 focus:outline-none"
            ></textarea>
          </div>

          <!-- Cards -->
          <div>
            <div class="mb-3 flex items-center justify-between">
              <label class="text-sm font-medium text-slate-700">Kartochkalar ({{ formData.cards.length }})</label>
              <button
                @click="addCardToForm"
                class="flex items-center gap-1 rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-600 hover:bg-indigo-100"
              >
                <Plus :size="14" /> Kartochka qo'shish
              </button>
            </div>

            <div class="space-y-3">
              <div
                v-for="(card, idx) in formData.cards"
                :key="idx"
                class="relative rounded-xl border border-slate-200 bg-slate-50 p-4"
              >
                <div class="mb-2 flex items-center justify-between">
                  <span class="text-xs font-medium text-slate-500">#{{ idx + 1 }}</span>
                  <div class="flex items-center gap-2">
                    <!-- Answer type selector -->
                    <select
                      v-model="card.answer_type"
                      class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs focus:border-indigo-500 focus:outline-none"
                    >
                      <option value="text">Matn javob</option>
                      <option value="multiple_choice">Test (A,B,C,D)</option>
                      <option value="true_false">To'g'ri/Noto'g'ri</option>
                    </select>
                    <button @click="removeCardFromForm(idx)" class="rounded-lg p-1 text-red-400 hover:bg-red-50">
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </div>

                <!-- Question -->
                <input
                  v-model="card.question"
                  type="text"
                  placeholder="Savol..."
                  class="mb-2 w-full rounded-lg border border-slate-200 bg-white p-2.5 text-sm focus:border-indigo-500 focus:outline-none"
                />

                <!-- Text answer -->
                <input
                  v-if="card.answer_type === 'text'"
                  v-model="card.answer"
                  type="text"
                  placeholder="Javob..."
                  class="w-full rounded-lg border border-emerald-200 bg-emerald-50 p-2.5 text-sm focus:border-emerald-500 focus:outline-none"
                />

                <!-- Multiple choice -->
                <div v-if="card.answer_type === 'multiple_choice'" class="space-y-2">
                  <div v-for="(opt, oi) in (card.options || ['', '', '', ''])" :key="oi" class="flex items-center gap-2">
                    <button
                      @click="card.correct_option = oi; card.answer = card.options[oi]"
                      class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold transition-all"
                      :class="card.correct_option === oi ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300 text-slate-400'"
                    >
                      {{ String.fromCharCode(65 + oi) }}
                    </button>
                    <input
                      :value="card.options?.[oi] || ''"
                      @input="updateOption(card, oi, $event.target.value)"
                      type="text"
                      :placeholder="`${String.fromCharCode(65 + oi)} variant...`"
                      class="w-full rounded-lg border border-slate-200 bg-white p-2 text-sm focus:border-indigo-500 focus:outline-none"
                    />
                  </div>
                </div>

                <!-- True/False -->
                <div v-if="card.answer_type === 'true_false'" class="flex gap-3">
                  <button
                    @click="card.answer = 'true'; card.correct_option = 0"
                    class="flex-1 rounded-lg border-2 py-2 text-sm font-medium transition-all"
                    :class="card.answer === 'true' ? 'border-emerald-500 bg-emerald-50 text-emerald-600' : 'border-slate-200 text-slate-500'"
                  >
                    <CheckCircle :size="16" class="inline" /> To'g'ri
                  </button>
                  <button
                    @click="card.answer = 'false'; card.correct_option = 1"
                    class="flex-1 rounded-lg border-2 py-2 text-sm font-medium transition-all"
                    :class="card.answer === 'false' ? 'border-red-500 bg-red-50 text-red-600' : 'border-slate-200 text-slate-500'"
                  >
                    <XCircle2 :size="16" class="inline" /> Noto'g'ri
                  </button>
                </div>

                <!-- Hint -->
                <input
                  v-model="card.hint"
                  type="text"
                  placeholder="Maslahat (ixtiyoriy)..."
                  class="mt-2 w-full rounded-lg border border-slate-200 bg-white p-2 text-xs text-slate-500 focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 flex items-center justify-end gap-3 border-t border-slate-200 bg-white p-5">
          <button @click="showCreateModal = false" class="rounded-xl border border-slate-200 px-5 py-2.5 text-slate-600 hover:bg-slate-50">
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="saveSet"
            :disabled="saving || !formData.title || formData.cards.length === 0"
            class="flex items-center gap-2 rounded-xl bg-indigo-500 px-6 py-2.5 font-medium text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-600 disabled:opacity-50"
          >
            <Loader2 v-if="saving" :size="18" class="animate-spin" />
            {{ editingSet ? 'Saqlash' : 'Yaratish' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===============================================================
         VIEW SET MODAL (Cards list)
         =============================================================== -->
    <div v-if="showViewModal && selectedSet" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="showViewModal = false">
      <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <!-- Header -->
        <div class="sticky top-0 z-10 border-b border-slate-200 bg-white p-5">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-bold text-slate-800">{{ selectedSet.title }}</h2>
              <p v-if="selectedSet.subject" class="text-sm text-indigo-500">{{ selectedSet.subject }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="selectedSet.creator_id === userId"
                @click="editSet(selectedSet)"
                class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-indigo-600"
              >
                <Pencil :size="18" />
              </button>
              <button
                v-if="selectedSet.creator_id === userId"
                @click="confirmDeleteSet(selectedSet)"
                class="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600"
              >
                <Trash2 :size="18" />
              </button>
              <button @click="showViewModal = false" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100">
                <X :size="20" />
              </button>
            </div>
          </div>
          <div class="mt-3 flex gap-2">
            <button
              @click="startFlashcard(selectedSet)"
              class="flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
            >
              <BookOpen :size="16" /> Kartochka rejimi
            </button>
            <button
              @click="startQuiz(selectedSet)"
              class="flex items-center gap-2 rounded-xl bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-600"
            >
              <Zap :size="16" /> Test rejimi
            </button>
          </div>
        </div>

        <!-- Cards list -->
        <div class="divide-y divide-slate-100 p-5">
          <div v-for="(card, idx) in selectedSet.cards" :key="card.id" class="py-4 first:pt-0">
            <div class="flex items-start gap-3">
              <span class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-600">
                {{ idx + 1 }}
              </span>
              <div class="flex-1">
                <p class="font-medium text-slate-800">{{ card.question }}</p>
                <p class="mt-1 text-sm text-emerald-600">
                  <span v-if="card.answer_type === 'multiple_choice' && card.options">
                    {{ String.fromCharCode(65 + (card.correct_option || 0)) }}. {{ card.options[card.correct_option || 0] }}
                  </span>
                  <span v-else-if="card.answer_type === 'true_false'">
                    {{ card.answer === 'true' ? "To'g'ri" : "Noto'g'ri" }}
                  </span>
                  <span v-else>{{ card.answer }}</span>
                </p>
                <p v-if="card.hint" class="mt-1 text-xs italic text-slate-400 flex items-center gap-1"><Lightbulb :size="12" /> {{ card.hint }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===============================================================
         FLASHCARD MODE
         =============================================================== -->
    <div v-if="showFlashcard && flashcardSet" class="fixed inset-0 z-50 flex flex-col bg-gradient-to-br from-indigo-50 to-purple-50">
      <!-- Top bar -->
      <div class="flex items-center justify-between px-6 py-4">
        <div>
          <h2 class="text-lg font-bold text-slate-800">{{ flashcardSet.title }}</h2>
          <p class="text-sm text-slate-500">{{ flashcardIndex + 1 }} / {{ flashcardSet.cards.length }}</p>
        </div>
        <button @click="closeFlashcard" class="rounded-xl bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow hover:bg-slate-50">
          Yopish
        </button>
      </div>

      <!-- Progress bar -->
      <div class="mx-6 h-2 overflow-hidden rounded-full bg-white/60">
        <div
          class="h-full rounded-full bg-indigo-500 transition-all duration-500"
          :style="{ width: `${((flashcardIndex + 1) / flashcardSet.cards.length) * 100}%` }"
        ></div>
      </div>

      <!-- Card -->
      <div class="flex flex-1 items-center justify-center px-6 py-8">
        <div
          class="relative w-full max-w-lg cursor-pointer"
          @click="flashcardFlipped = !flashcardFlipped"
          style="perspective: 1000px; min-height: 300px"
        >
          <div
            class="absolute inset-0 transition-transform duration-500"
            :style="{ transformStyle: 'preserve-3d', transform: flashcardFlipped ? 'rotateY(180deg)' : '' }"
          >
            <!-- Front (Question) -->
            <div
              class="absolute inset-0 flex flex-col items-center justify-center rounded-3xl bg-white p-8 shadow-xl"
              style="backface-visibility: hidden"
            >
              <p class="mb-3 text-xs font-medium uppercase tracking-wider text-indigo-400">Savol</p>
              <p class="text-center text-xl font-medium text-slate-800 sm:text-2xl">
                {{ flashcardSet.cards[flashcardIndex]?.question }}
              </p>
              <p class="mt-6 text-sm text-slate-400">Javobni ko'rish uchun bosing</p>
            </div>

            <!-- Back (Answer) -->
            <div
              class="absolute inset-0 flex flex-col items-center justify-center rounded-3xl bg-emerald-500 p-8 text-white shadow-xl"
              style="backface-visibility: hidden; transform: rotateY(180deg)"
            >
              <p class="mb-3 text-xs font-medium uppercase tracking-wider text-emerald-100">Javob</p>
              <p class="text-center text-xl font-medium sm:text-2xl">
                {{ getFlashcardAnswer(flashcardSet.cards[flashcardIndex]) }}
              </p>
              <p v-if="flashcardSet.cards[flashcardIndex]?.hint" class="mt-4 text-sm text-emerald-100 flex items-center justify-center gap-1">
                <Lightbulb :size="14" /> {{ flashcardSet.cards[flashcardIndex].hint }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex items-center justify-center gap-4 px-6 pb-8">
        <button
          @click="prevFlashcard"
          :disabled="flashcardIndex === 0"
          class="flex h-12 w-12 items-center justify-center rounded-full bg-white text-slate-600 shadow-lg transition-all hover:bg-slate-50 disabled:opacity-30"
        >
          <ChevronLeft :size="24" />
        </button>
        <button
          @click="shuffleFlashcards"
          class="flex h-12 w-12 items-center justify-center rounded-full bg-white text-purple-600 shadow-lg transition-all hover:bg-purple-50"
          :title="$t('quiz.shuffle')"
        >
          <Shuffle :size="20" />
        </button>
        <button
          @click="nextFlashcard"
          :disabled="flashcardIndex >= flashcardSet.cards.length - 1"
          class="flex h-12 w-12 items-center justify-center rounded-full bg-white text-slate-600 shadow-lg transition-all hover:bg-slate-50 disabled:opacity-30"
        >
          <ChevronRight :size="24" />
        </button>
      </div>
    </div>

    <!-- ===============================================================
         QUIZ (TEST) MODE
         =============================================================== -->
    <div v-if="showQuiz && quizData" class="fixed inset-0 z-50 flex flex-col bg-gradient-to-br from-indigo-50 to-blue-50">
      <!-- Top bar -->
      <div class="flex items-center justify-between px-6 py-4">
        <div>
          <h2 class="text-lg font-bold text-slate-800">{{ quizData.title }}</h2>
          <p class="text-sm text-slate-500">{{ quizCurrentIndex + 1 }} / {{ quizData.cards.length }} savol</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="rounded-full bg-white px-3 py-1 text-sm font-medium text-indigo-600 shadow">
            ⏱ {{ formatTime(quizTimer) }}
          </span>
          <button @click="endQuiz" class="rounded-xl bg-white px-4 py-2 text-sm font-medium text-red-500 shadow hover:bg-red-50">
            Tugatish
          </button>
        </div>
      </div>

      <!-- Progress -->
      <div class="mx-6 h-2 overflow-hidden rounded-full bg-white/60">
        <div
          class="h-full rounded-full bg-indigo-500 transition-all"
          :style="{ width: `${((quizCurrentIndex + 1) / quizData.cards.length) * 100}%` }"
        ></div>
      </div>

      <!-- Question -->
      <div v-if="!quizFinished" class="flex flex-1 flex-col items-center justify-center px-6 py-8">
        <div class="w-full max-w-lg">
          <div class="mb-8 rounded-2xl bg-white p-6 shadow-xl">
            <p class="text-center text-xl font-medium text-slate-800">
              {{ quizData.cards[quizCurrentIndex]?.question }}
            </p>
            <p v-if="quizShowHint && quizData.cards[quizCurrentIndex]?.hint" class="mt-3 text-center text-sm italic text-amber-500 flex items-center justify-center gap-1">
              <Lightbulb :size="14" /> {{ quizData.cards[quizCurrentIndex].hint }}
            </p>
          </div>

          <!-- Answer Options -->
          <div class="space-y-3">
            <!-- Multiple Choice -->
            <template v-if="currentQuizCard?.answer_type === 'multiple_choice' && currentQuizCard?.options">
              <button
                v-for="(opt, oi) in currentQuizCard.options"
                :key="oi"
                @click="selectQuizAnswer(oi)"
                class="w-full rounded-xl border-2 p-4 text-left font-medium transition-all"
                :class="getQuizOptionClass(oi)"
                :disabled="quizAnswered"
              >
                <span class="mr-3 inline-flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-xs font-bold">
                  {{ String.fromCharCode(65 + oi) }}
                </span>
                {{ opt }}
              </button>
            </template>

            <!-- True/False -->
            <template v-else-if="currentQuizCard?.answer_type === 'true_false'">
              <div class="grid grid-cols-2 gap-4">
                <button
                  @click="selectQuizAnswer('true')"
                  class="rounded-xl border-2 p-4 text-center font-medium transition-all"
                  :class="getQuizTFClass('true')"
                  :disabled="quizAnswered"
                >
                  <CheckCircle :size="16" class="inline" /> To'g'ri
                </button>
                <button
                  @click="selectQuizAnswer('false')"
                  class="rounded-xl border-2 p-4 text-center font-medium transition-all"
                  :class="getQuizTFClass('false')"
                  :disabled="quizAnswered"
                >
                  <XCircle2 :size="16" class="inline" /> Noto'g'ri
                </button>
              </div>
            </template>

            <!-- Text answer -->
            <template v-else>
              <input
                v-model="quizTextAnswer"
                @keyup.enter="checkTextAnswer"
                type="text"
                placeholder="Javobingizni yozing..."
                class="w-full rounded-xl border-2 border-slate-200 p-4 text-center text-lg focus:border-indigo-500 focus:outline-none"
                :disabled="quizAnswered"
              />
              <button
                v-if="!quizAnswered"
                @click="checkTextAnswer"
                class="w-full rounded-xl bg-indigo-500 py-3 font-medium text-white hover:bg-indigo-600"
              >
                Tekshirish
              </button>
              <div v-if="quizAnswered" class="rounded-xl p-3 text-center text-sm"
                :class="quizAnswerCorrect ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'"
              >
                {{ quizAnswerCorrect ? 'To\'g\'ri!' : `Noto'g'ri. Javob: ${currentQuizCard?.answer}` }}
              </div>
            </template>
          </div>

          <!-- Next Button (after answering) -->
          <div v-if="quizAnswered" class="mt-6 flex justify-center">
            <button
              @click="nextQuizQuestion"
              class="rounded-xl bg-indigo-500 px-8 py-3 font-medium text-white shadow-lg hover:bg-indigo-600"
            >
              {{ quizCurrentIndex < quizData.cards.length - 1 ? 'Keyingi savol →' : 'Natijalarni ko\'rish' }}
            </button>
          </div>

          <!-- Hint button -->
          <div v-if="!quizAnswered && currentQuizCard?.hint" class="mt-4 text-center">
            <button @click="quizShowHint = true" class="text-sm text-amber-500 hover:underline flex items-center gap-1 mx-auto">
              <Lightbulb :size="14" /> Maslahat ko'rish
            </button>
          </div>
        </div>
      </div>

      <!-- Results screen -->
      <div v-if="quizFinished" class="flex flex-1 flex-col items-center justify-center px-6 py-8">
        <div class="w-full max-w-md text-center">
          <div class="mb-6">
            <div
              class="mx-auto flex h-24 w-24 items-center justify-center rounded-full"
              :class="quizScore >= 80 ? 'bg-emerald-100' : quizScore >= 50 ? 'bg-amber-100' : 'bg-red-100'"
            >
              <Trophy v-if="quizScore >= 80" :size="40" class="text-emerald-500" />
              <ThumbsUp v-else-if="quizScore >= 50" :size="40" class="text-amber-500" />
              <BookOpen v-else :size="40" class="text-red-500" />
            </div>
          </div>
          <h2 class="mb-2 text-3xl font-bold text-slate-800">{{ quizScore }}%</h2>
          <p class="mb-6 text-slate-500">
            {{ quizCorrectCount }} / {{ quizData.cards.length }} to'g'ri javob
            <br />
            <span class="text-sm">⏱ {{ formatTime(quizTimer) }} vaqt sarflandi</span>
          </p>

          <div class="flex justify-center gap-3">
            <button
              @click="startQuiz(quizData)"
              class="rounded-xl bg-indigo-500 px-6 py-2.5 font-medium text-white hover:bg-indigo-600"
            >
              Qaytadan
            </button>
            <button
              @click="showQuiz = false; quizFinished = false"
              class="rounded-xl border border-slate-200 px-6 py-2.5 font-medium text-slate-600 hover:bg-slate-50"
            >
              Yopish
            </button>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import {
    ArrowUpCircle,
    BookOpen,
    CheckCircle,
    ChevronLeft, ChevronRight,
    Crown,
    Layers,
    Lightbulb,
    Loader2,
    Lock,
    Pencil,
    Play,
    Plus, Search,
    Shuffle,
    Sparkles,
    ThumbsUp,
    Trash2,
    Trophy,
    X,
    XCircle as XCircle2,
    Zap,
} from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const userId = computed(() => authStore.user?.id)
const userRole = computed(() => authStore.user?.role)

// ============ Subscription Access ============
const hasAccess = ref(true)
const accessLoading = ref(true)
const accessReason = ref(null)

// ============ State ============
const loading = ref(false)
const saving = ref(false)
const activeTab = ref('all')
const searchQuery = ref('')
const quizSets = ref([])

const showCreateModal = ref(false)
const showViewModal = ref(false)
const selectedSet = ref(null)
const editingSet = ref(null)

const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']

const formData = ref({
  title: '',
  description: '',
  subject: '',
  color: '#3b82f6',
  cards: [],
})

// ============ Flashcard State ============
const showFlashcard = ref(false)
const flashcardSet = ref(null)
const flashcardIndex = ref(0)
const flashcardFlipped = ref(false)

// ============ Quiz State ============
const showQuiz = ref(false)
const quizData = ref(null)
const quizCurrentIndex = ref(0)
const quizAnswered = ref(false)
const quizAnswerCorrect = ref(false)
const quizSelectedAnswer = ref(null)
const quizTextAnswer = ref('')
const quizCorrectCount = ref(0)
const quizFinished = ref(false)
const quizTimer = ref(0)
const quizShowHint = ref(false)
let quizTimerInterval = null

const currentQuizCard = computed(() => quizData.value?.cards?.[quizCurrentIndex.value])
const quizScore = computed(() => {
  if (!quizData.value?.cards?.length) return 0
  return Math.round((quizCorrectCount.value / quizData.value.cards.length) * 100)
})

// ============ Search ============
let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => loadSets(), 400)
}

// ============ Data Loading ============
const loadSets = async () => {
  loading.value = true
  try {
    const params = { page_size: 50 }
    if (searchQuery.value) params.search = searchQuery.value
    if (activeTab.value === 'my') params.my_only = true
    
    const res = await api.request(`/quizzes${buildQuery(params)}`)
    quizSets.value = res.items || []
  } catch (e) {
    console.error('Error loading quiz sets:', e)
  } finally {
    loading.value = false
  }
}

function buildQuery(params) {
  const cleaned = {}
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') cleaned[k] = v
  }
  if (!Object.keys(cleaned).length) return ''
  return '?' + new URLSearchParams(cleaned).toString()
}

// ============ Create / Edit ============
const openCreateModal = () => {
  editingSet.value = null
  formData.value = {
    title: '',
    description: '',
    subject: '',
    color: '#3b82f6',
    cards: [{ question: '', answer: '', answer_type: 'text', options: ['', '', '', ''], correct_option: 0, hint: '' }],
  }
  showCreateModal.value = true
}

const editSet = (set) => {
  editingSet.value = set
  formData.value = {
    title: set.title,
    description: set.description || '',
    subject: set.subject || '',
    color: set.color || '#3b82f6',
    cards: (set.cards || []).map(c => ({
      id: c.id,
      question: c.question,
      answer: c.answer,
      answer_type: c.answer_type || 'text',
      options: c.options || ['', '', '', ''],
      correct_option: c.correct_option ?? 0,
      hint: c.hint || '',
    })),
  }
  showViewModal.value = false
  showCreateModal.value = true
}

const addCardToForm = () => {
  formData.value.cards.push({
    question: '', answer: '', answer_type: 'text',
    options: ['', '', '', ''], correct_option: 0, hint: '',
  })
}

const removeCardFromForm = (idx) => {
  formData.value.cards.splice(idx, 1)
}

const updateOption = (card, index, value) => {
  if (!card.options) card.options = ['', '', '', '']
  card.options[index] = value
}

const saveSet = async () => {
  if (!formData.value.title || formData.value.cards.length === 0) return
  saving.value = true
  try {
    const payload = {
      title: formData.value.title,
      description: formData.value.description || null,
      subject: formData.value.subject || null,
      color: formData.value.color,
      cards: formData.value.cards.map((c, i) => ({
        question: c.question,
        answer: c.answer || (c.answer_type === 'multiple_choice' ? (c.options?.[c.correct_option] || '') : ''),
        answer_type: c.answer_type,
        options: c.answer_type === 'multiple_choice' ? c.options : null,
        correct_option: c.correct_option,
        hint: c.hint || null,
        order: i,
      })),
    }

    if (editingSet.value) {
      // Delete existing set and recreate (simpler than partial updates)
      await api.request(`/quizzes/${editingSet.value.id}`, { method: 'DELETE' })
      await api.request('/quizzes', { method: 'POST', body: JSON.stringify(payload) })
    } else {
      await api.request('/quizzes', { method: 'POST', body: JSON.stringify(payload) })
    }

    showCreateModal.value = false
    await loadSets()
  } catch (e) {
    console.error('Error saving quiz set:', e)
  } finally {
    saving.value = false
  }
}

const confirmDeleteSet = async (set) => {
  if (!confirm(`"${set.title}" to'plamini o'chirmoqchimisiz?`)) return
  try {
    await api.request(`/quizzes/${set.id}`, { method: 'DELETE' })
    showViewModal.value = false
    await loadSets()
  } catch (e) {
    console.error('Error deleting set:', e)
  }
}

// ============ View Set ============
const openSet = async (set) => {
  try {
    const fullSet = await api.request(`/quizzes/${set.id}`)
    selectedSet.value = fullSet
    showViewModal.value = true
  } catch (e) {
    console.error('Error loading set:', e)
  }
}

// ============ Flashcard Mode ============
const startFlashcard = (set) => {
  flashcardSet.value = { ...set, cards: [...(set.cards || [])] }
  flashcardIndex.value = 0
  flashcardFlipped.value = false
  showViewModal.value = false
  showFlashcard.value = true
}

const prevFlashcard = () => {
  if (flashcardIndex.value > 0) {
    flashcardIndex.value--
    flashcardFlipped.value = false
  }
}

const nextFlashcard = () => {
  if (flashcardIndex.value < flashcardSet.value.cards.length - 1) {
    flashcardIndex.value++
    flashcardFlipped.value = false
  }
}

const shuffleFlashcards = () => {
  const cards = [...flashcardSet.value.cards]
  for (let i = cards.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [cards[i], cards[j]] = [cards[j], cards[i]]
  }
  flashcardSet.value = { ...flashcardSet.value, cards }
  flashcardIndex.value = 0
  flashcardFlipped.value = false
}

const closeFlashcard = () => {
  showFlashcard.value = false
}

const getFlashcardAnswer = (card) => {
  if (!card) return ''
  if (card.answer_type === 'multiple_choice' && card.options) {
    return `${String.fromCharCode(65 + (card.correct_option || 0))}. ${card.options[card.correct_option || 0]}`
  }
  if (card.answer_type === 'true_false') {
    return card.answer === 'true' ? "To'g'ri" : "Noto'g'ri"
  }
  return card.answer
}

// ============ Quiz Mode ============
const startQuiz = (set) => {
  // Shuffle cards for quiz
  const cards = [...(set.cards || [])]
  for (let i = cards.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [cards[i], cards[j]] = [cards[j], cards[i]]
  }
  
  quizData.value = { ...set, cards }
  quizCurrentIndex.value = 0
  quizCorrectCount.value = 0
  quizAnswered.value = false
  quizAnswerCorrect.value = false
  quizSelectedAnswer.value = null
  quizTextAnswer.value = ''
  quizFinished.value = false
  quizTimer.value = 0
  quizShowHint.value = false
  showViewModal.value = false
  showQuiz.value = true

  // Start timer
  clearInterval(quizTimerInterval)
  quizTimerInterval = setInterval(() => {
    quizTimer.value++
  }, 1000)
}

const selectQuizAnswer = (answer) => {
  if (quizAnswered.value) return
  quizSelectedAnswer.value = answer
  quizAnswered.value = true

  const card = currentQuizCard.value
  if (card.answer_type === 'multiple_choice') {
    quizAnswerCorrect.value = answer === card.correct_option
  } else if (card.answer_type === 'true_false') {
    quizAnswerCorrect.value = answer === card.answer
  }
  
  if (quizAnswerCorrect.value) quizCorrectCount.value++
}

const checkTextAnswer = () => {
  if (quizAnswered.value || !quizTextAnswer.value.trim()) return
  quizAnswered.value = true
  
  const card = currentQuizCard.value
  const userAnswer = quizTextAnswer.value.trim().toLowerCase()
  const correctAnswer = (card.answer || '').trim().toLowerCase()
  
  quizAnswerCorrect.value = userAnswer === correctAnswer
  if (quizAnswerCorrect.value) quizCorrectCount.value++
}

const nextQuizQuestion = () => {
  if (quizCurrentIndex.value < quizData.value.cards.length - 1) {
    quizCurrentIndex.value++
    quizAnswered.value = false
    quizAnswerCorrect.value = false
    quizSelectedAnswer.value = null
    quizTextAnswer.value = ''
    quizShowHint.value = false
  } else {
    // Finish quiz
    quizFinished.value = true
    clearInterval(quizTimerInterval)
    
    // Save result
    api.request('/quizzes/results', {
      method: 'POST',
      body: JSON.stringify({
        quiz_set_id: quizData.value.id,
        total_questions: quizData.value.cards.length,
        correct_answers: quizCorrectCount.value,
        score_percentage: quizScore.value,
        time_spent_seconds: quizTimer.value,
        mode: 'quiz',
      }),
    }).catch(e => console.error('Error saving result:', e))
  }
}

const endQuiz = () => {
  clearInterval(quizTimerInterval)
  quizFinished.value = true
}

const getQuizOptionClass = (optionIndex) => {
  if (!quizAnswered.value) {
    return quizSelectedAnswer.value === optionIndex
      ? 'border-indigo-500 bg-indigo-50'
      : 'border-slate-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/50'
  }
  const card = currentQuizCard.value
  if (optionIndex === card.correct_option) {
    return 'border-emerald-500 bg-emerald-50 text-emerald-700'
  }
  if (optionIndex === quizSelectedAnswer.value && !quizAnswerCorrect.value) {
    return 'border-red-500 bg-red-50 text-red-700'
  }
  return 'border-slate-200 bg-white opacity-50'
}

const getQuizTFClass = (value) => {
  if (!quizAnswered.value) {
    return 'border-slate-200 bg-white hover:border-indigo-300'
  }
  const card = currentQuizCard.value
  if (value === card.answer) {
    return 'border-emerald-500 bg-emerald-50 text-emerald-700'
  }
  if (value === quizSelectedAnswer.value && !quizAnswerCorrect.value) {
    return 'border-red-500 bg-red-50 text-red-700'
  }
  return 'border-slate-200 bg-white opacity-50'
}

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

// ============ Subscription Check ============
const checkAccess = async () => {
  // Admin and superadmin always have access
  if (userRole.value === 'admin' || userRole.value === 'superadmin') {
    hasAccess.value = true
    accessLoading.value = false
    return true
  }
  try {
    const res = await api.request('/quizzes/check-access')
    hasAccess.value = res.has_access
    accessReason.value = res.reason
  } catch (e) {
    hasAccess.value = false
    accessReason.value = 'quiz_subscription_required'
  }
  accessLoading.value = false
  return hasAccess.value
}

const goToSubscription = () => {
  const role = userRole.value
  if (role === 'leader') {
    router.push('/leader/subscription')
  } else {
    router.push('/student/subscription')
  }
}

// ============ Tab watcher ============
const loadOnTabChange = () => loadSets()

// ============ Lifecycle ============
onMounted(async () => {
  const ok = await checkAccess()
  if (ok) loadSets()
})

onUnmounted(() => {
  clearInterval(quizTimerInterval)
})

// Watch tab change
import { watch } from 'vue'
watch(activeTab, loadOnTabChange)
</script>
