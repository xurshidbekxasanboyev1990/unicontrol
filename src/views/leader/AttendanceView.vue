<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Davomat olish</h1>
        <p class="text-slate-500">Bugungi dars uchun davomat yozish</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="selectedDate" class="px-4 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all">
          <option v-for="date in recentDates" :key="date" :value="date">
            {{ formatDate(date) }}
          </option>
        </select>
        <select v-model="selectedSubject" class="px-4 py-2.5 rounded-xl border border-slate-200 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all">
          <option value="">Barcha fanlar</option>
          <option v-for="subject in subjects" :key="subject" :value="subject">
            {{ subject }}
          </option>
        </select>
      </div>
    </div>

    <!-- Rules Info Banner -->
    <div class="rounded-2xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-5">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <AlertCircle class="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h3 class="font-semibold text-blue-900 mb-1">Davomat qoidalari</h3>
          <ul class="text-sm text-blue-700 space-y-1">
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
              Davomat har bir dars boshlanishida belgilanadi
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
              Dars tugaganidan keyin o'zgartirish uchun asosli sabab talab qilinadi
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-amber-400 rounded-full"></span>
              O'zgartirishlar admin tomonidan tasdiqlanishi kerak
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Lesson Status / Can Edit? -->
    <div v-if="isLessonEnded" class="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-5">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <Clock class="w-6 h-6 text-amber-600" />
        </div>
        <div class="flex-1">
          <h3 class="font-semibold text-amber-900">Dars tugagan</h3>
          <p class="text-sm text-amber-700">Ushbu kun uchun davomat allaqachon yozilgan. O'zgartirishlar admin tasdiqlashidan keyin kuchga kiradi.</p>
        </div>
        <div class="flex items-center gap-2 text-amber-700">
          <Lock class="w-5 h-5" />
          <span class="text-sm font-medium">Tahrirlash cheklangan</span>
        </div>
      </div>
    </div>

    <!-- Pending Changes Banner -->
    <div v-if="pendingChanges.length > 0" class="rounded-2xl border border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 p-5">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
            <ClipboardCheck class="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 class="font-semibold text-purple-900">Kutilayotgan o'zgartirishlar</h3>
            <p class="text-sm text-purple-700">{{ pendingChanges.length }} ta o'zgartirish admin tasdiqlashini kutmoqda</p>
          </div>
        </div>
        <button @click="showPendingModal = true" class="px-4 py-2 bg-purple-500 text-white rounded-xl text-sm font-medium hover:bg-purple-600 transition-colors">
          Ko'rish
        </button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl p-5 border border-emerald-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-emerald-600">{{ presentCount }}</p>
            <p class="text-sm text-emerald-700 font-medium">Kelgan</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
            <CheckCircle class="w-6 h-6 text-emerald-600" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-2xl p-5 border border-amber-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-amber-600">{{ lateCount }}</p>
            <p class="text-sm text-amber-700 font-medium">Kechikkan</p>
          </div>
          <div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
            <Clock class="w-6 h-6 text-amber-600" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-rose-50 to-rose-100/50 rounded-2xl p-5 border border-rose-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-rose-600">{{ absentCount }}</p>
            <p class="text-sm text-rose-700 font-medium">Kelmagan</p>
          </div>
          <div class="w-12 h-12 bg-rose-500/20 rounded-xl flex items-center justify-center">
            <XCircle class="w-6 h-6 text-rose-600" />
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-5 border border-blue-200/50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-3xl font-bold text-blue-600">{{ excusedCount }}</p>
            <p class="text-sm text-blue-700 font-medium">Sababli</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
            <FileText class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div class="bg-white rounded-2xl border border-slate-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <span class="text-sm font-medium text-slate-600">Tez harakatlar:</span>
        <button 
          @click="markAllAs('present')" 
          :disabled="isLessonEnded"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2',
            isLessonEnded ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-emerald-100 hover:bg-emerald-200 text-emerald-700'
          ]"
        >
          <CheckCircle class="w-4 h-4" />
          Barchasini keldi
        </button>
        <button 
          @click="markAllAs('absent')" 
          :disabled="isLessonEnded"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2',
            isLessonEnded ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-rose-100 hover:bg-rose-200 text-rose-700'
          ]"
        >
          <XCircle class="w-4 h-4" />
          Barchasini kelmadi
        </button>
        <button @click="resetAll" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-medium transition-colors flex items-center gap-2">
          <RotateCcw class="w-4 h-4" />
          Tozalash
        </button>
      </div>
    </div>

    <!-- Students List -->
    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-lg font-semibold text-slate-800">Talabalar ro'yxati</h2>
          <p class="text-sm text-slate-500">Jami: {{ groupStudents.length }} ta talaba</p>
        </div>
        <button 
          @click="saveAttendance"
          :disabled="saving"
          class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save v-if="!saving" class="w-5 h-5" />
          <Loader2 v-else class="w-5 h-5 animate-spin" />
          <span>{{ saving ? 'Saqlanmoqda...' : (isLessonEnded ? 'O\'zgartirish so\'rovi' : 'Saqlash') }}</span>
        </button>
      </div>

      <div class="divide-y divide-slate-100">
        <div 
          v-for="(student, index) in groupStudents" 
          :key="student.id"
          class="p-4 lg:p-5 hover:bg-slate-50/50 transition-colors"
        >
          <div class="flex flex-col lg:flex-row lg:items-center gap-4">
            <!-- Student Info -->
            <div class="flex items-center gap-4 flex-1">
              <span class="w-8 h-8 flex items-center justify-center text-sm font-bold text-slate-400 bg-slate-100 rounded-lg">{{ index + 1 }}</span>
              
              <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                <User class="w-5 h-5 text-slate-500" />
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <p class="font-semibold text-slate-800">{{ student.name }}</p>
                  <!-- Pending change indicator -->
                  <span 
                    v-if="hasPendingChange(student.id)" 
                    class="px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 rounded-full flex items-center gap-1"
                  >
                    <Clock class="w-3 h-3" />
                    Kutilmoqda
                  </span>
                </div>
                <p class="text-sm text-slate-500">{{ student.studentId }}</p>
              </div>
            </div>

            <!-- Status Buttons -->
            <div class="flex items-center gap-2 flex-wrap">
              <!-- Keldi -->
              <button
                @click="handleStatusChange(student.id, 'present')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'present' 
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30 scale-105' 
                    : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 hover:scale-105'
                ]"
              >
                <CheckCircle class="w-4 h-4" />
                <span class="hidden sm:inline">Keldi</span>
              </button>
              <!-- Kelmadi -->
              <button
                @click="handleStatusChange(student.id, 'absent')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'absent' 
                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30 scale-105' 
                    : 'bg-rose-100 text-rose-700 hover:bg-rose-200 hover:scale-105'
                ]"
              >
                <XCircle class="w-4 h-4" />
                <span class="hidden sm:inline">Kelmadi</span>
              </button>
              <!-- Kech qoldi -->
              <button
                @click="handleStatusChange(student.id, 'late')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'late' 
                    ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/30 scale-105' 
                    : 'bg-amber-100 text-amber-700 hover:bg-amber-200 hover:scale-105'
                ]"
              >
                <Clock class="w-4 h-4" />
                <span class="hidden sm:inline">Kech qoldi</span>
              </button>
              <!-- Sababli -->
              <button
                @click="handleStatusChange(student.id, 'excused')"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
                  attendance[student.id]?.status === 'excused' 
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30 scale-105' 
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200 hover:scale-105'
                ]"
              >
                <FileText class="w-4 h-4" />
                <span class="hidden sm:inline">Sababli</span>
              </button>
            </div>
          </div>

          <!-- Kelmadi sababi input -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="attendance[student.id]?.status === 'absent' || attendance[student.id]?.status === 'excused'" class="mt-4 ml-12 lg:ml-20">
              <div class="flex items-center gap-3 p-4 bg-rose-50 rounded-xl border border-rose-200">
                <MessageSquare class="w-5 h-5 text-rose-500 flex-shrink-0" />
                <div class="flex-1">
                  <label class="block text-sm font-medium text-rose-700 mb-1.5">Kelmaganlik sababi</label>
                  <input
                    v-model="attendance[student.id].reason"
                    type="text"
                    placeholder="Masalan: Kasallik, oilaviy sabab..."
                    class="w-full px-4 py-2.5 rounded-lg border border-rose-200 bg-white focus:border-rose-400 focus:ring-2 focus:ring-rose-400/20 outline-none text-sm transition-all"
                  />
                </div>
              </div>
            </div>
          </Transition>

          <!-- Kechikish input -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="attendance[student.id]?.status === 'late'" class="mt-4 ml-12 lg:ml-20">
              <div class="flex items-center gap-3 p-4 bg-amber-50 rounded-xl border border-amber-200">
                <Timer class="w-5 h-5 text-amber-500 flex-shrink-0" />
                <div class="flex-1 flex flex-col sm:flex-row sm:items-center gap-3">
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-amber-700 mb-1.5">Necha daqiqa kechikdi?</label>
                    <div class="flex items-center gap-2">
                      <input
                        v-model.number="attendance[student.id].lateMinutes"
                        type="number"
                        min="1"
                        max="90"
                        placeholder="0"
                        class="w-24 px-4 py-2.5 rounded-lg border border-amber-200 bg-white focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm text-center transition-all"
                      />
                      <span class="text-sm text-amber-600 font-medium">daqiqa</span>
                    </div>
                  </div>
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-amber-700 mb-1.5">Sabab (ixtiyoriy)</label>
                    <input
                      v-model="attendance[student.id].reason"
                      type="text"
                      placeholder="Masalan: Transport muammosi..."
                      class="w-full px-4 py-2.5 rounded-lg border border-amber-200 bg-white focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm transition-all"
                    />
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Summary Modal -->
    <Teleport to="body">
      <div v-if="showSummary" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="showSummary = false">
        <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden">
          <div class="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 text-white text-center">
            <div class="w-16 h-16 bg-white/20 rounded-2xl mx-auto flex items-center justify-center mb-4">
              <CheckCircle class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold">{{ isLessonEnded ? 'O\'zgartirish so\'rovi yuborildi!' : 'Davomat saqlandi!' }}</h3>
            <p class="text-emerald-100 mt-1">{{ formatDate(selectedDate) }}</p>
          </div>
          <div class="p-6 space-y-4">
            <div v-if="isLessonEnded" class="p-4 bg-amber-50 rounded-xl border border-amber-200 text-center">
              <p class="text-sm text-amber-700">O'zgartirishlar admin tasdiqlashini kutmoqda</p>
            </div>
            <div class="flex items-center justify-between p-3 bg-emerald-50 rounded-xl">
              <span class="text-emerald-700 font-medium">Kelgan</span>
              <span class="text-2xl font-bold text-emerald-600">{{ presentCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-amber-50 rounded-xl">
              <span class="text-amber-700 font-medium">Kechikkan</span>
              <span class="text-2xl font-bold text-amber-600">{{ lateCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-rose-50 rounded-xl">
              <span class="text-rose-700 font-medium">Kelmagan</span>
              <span class="text-2xl font-bold text-rose-600">{{ absentCount }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-blue-50 rounded-xl">
              <span class="text-blue-700 font-medium">Sababli</span>
              <span class="text-2xl font-bold text-blue-600">{{ excusedCount }}</span>
            </div>
          </div>
          <div class="px-6 pb-6">
            <button @click="showSummary = false" class="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">Yopish</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Change Reason Modal -->
    <Teleport to="body">
      <div v-if="showReasonModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="cancelReasonModal">
        <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden">
          <div class="bg-gradient-to-r from-amber-500 to-orange-500 p-6 text-white">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
                <AlertCircle class="w-7 h-7" />
              </div>
              <div>
                <h3 class="text-xl font-bold">O'zgartirish sababi</h3>
                <p class="text-amber-100 text-sm mt-1">Dars tugagan, sabab kiritish talab etiladi</p>
              </div>
            </div>
          </div>
          <div class="p-6">
            <div class="mb-4 p-4 bg-slate-50 rounded-xl">
              <div class="flex items-center gap-3">
                <User class="w-5 h-5 text-slate-500" />
                <span class="font-medium text-slate-800">{{ pendingReasonStudent?.name }}</span>
              </div>
              <div class="mt-2 flex items-center gap-2 text-sm text-slate-600">
                <span>{{ getStatusLabel(pendingReasonData?.oldStatus) }}</span>
                <ArrowRight class="w-4 h-4" />
                <span class="font-medium text-slate-800">{{ getStatusLabel(pendingReasonData?.newStatus) }}</span>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">O'zgartirish sababi *</label>
              <textarea
                v-model="changeReason"
                rows="3"
                placeholder="Nima uchun davomat o'zgartirilmoqda? Batafsil yozing..."
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 outline-none text-sm transition-all resize-none"
              ></textarea>
              <p class="mt-2 text-xs text-slate-500">Bu sabab admin tomonidan ko'rib chiqiladi</p>
            </div>
          </div>
          <div class="px-6 pb-6 flex gap-3">
            <button @click="cancelReasonModal" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">
              Bekor qilish
            </button>
            <button 
              @click="confirmChange" 
              :disabled="!changeReason.trim()"
              class="flex-1 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Yuborish
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Pending Changes Modal -->
    <Teleport to="body">
      <div v-if="showPendingModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="showPendingModal = false">
        <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-hidden flex flex-col">
          <div class="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-white">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
                <ClipboardCheck class="w-7 h-7" />
              </div>
              <div>
                <h3 class="text-xl font-bold">Kutilayotgan o'zgartirishlar</h3>
                <p class="text-purple-100 text-sm mt-1">Admin tasdiqlashini kutmoqda</p>
              </div>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-3">
            <div 
              v-for="change in pendingChanges" 
              :key="change.id"
              class="p-4 bg-slate-50 rounded-xl border border-slate-200"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <User class="w-5 h-5 text-slate-500" />
                  <span class="font-medium text-slate-800">{{ change.studentName }}</span>
                </div>
                <span class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full flex items-center gap-1">
                  <Clock class="w-3 h-3" />
                  Kutilmoqda
                </span>
              </div>
              <div class="flex items-center gap-2 text-sm text-slate-600 mb-2">
                <span :class="getStatusColor(change.oldStatus)">{{ getStatusLabel(change.oldStatus) }}</span>
                <ArrowRight class="w-4 h-4" />
                <span :class="getStatusColor(change.newStatus)" class="font-medium">{{ getStatusLabel(change.newStatus) }}</span>
              </div>
              <div class="p-3 bg-white rounded-lg border border-slate-100">
                <p class="text-xs text-slate-500 mb-1">Sabab:</p>
                <p class="text-sm text-slate-700">{{ change.reason }}</p>
              </div>
              <p class="mt-2 text-xs text-slate-400">{{ formatDateTime(change.requestedAt) }}</p>
            </div>
            
            <div v-if="pendingChanges.length === 0" class="text-center py-8">
              <CheckCircle class="w-12 h-12 text-emerald-500 mx-auto mb-3" />
              <p class="text-slate-600">Kutilayotgan o'zgartirish yo'q</p>
            </div>
          </div>
          <div class="p-6 border-t border-slate-100">
            <button @click="showPendingModal = false" class="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors">
              Yopish
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * AttendanceView.vue - Davomat olish sahifasi (Leader)
 * 
 * QOIDALAR:
 * 1. Davomat har bir dars boshlanishida belgilanadi
 * 2. Dars tugaganidan keyin o'zgartirish uchun asosli sabab talab qilinadi
 * 3. O'zgartirishlar admin tomonidan tasdiqlanishi kerak
 */

import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useDataStore } from '../../stores/data'
import { useToastStore } from '../../stores/toast'
import {
  User,
  CheckCircle,
  Clock,
  XCircle,
  FileText,
  Save,
  Loader2,
  MessageSquare,
  Timer,
  RotateCcw,
  AlertCircle,
  Lock,
  ClipboardCheck,
  ArrowRight
} from 'lucide-vue-next'

const dataStore = useDataStore()
const toast = useToastStore()

// ============ STATE ============
const saving = ref(false)
const showSummary = ref(false)
const showReasonModal = ref(false)
const showPendingModal = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedSubject = ref('')
const changeReason = ref('')
const pendingReasonStudent = ref(null)
const pendingReasonData = ref(null)

// Simulated pending changes (in real app, from backend)
const pendingChanges = ref([
  {
    id: 1,
    studentId: 2,
    studentName: 'Karimov Bobur',
    oldStatus: 'present',
    newStatus: 'absent',
    reason: 'Talaba aslida darsda bo\'lmagan, ro\'yxatda xato belgilangan',
    requestedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
  }
])

// Check if lesson is ended (past date or current date after class time)
const isLessonEnded = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  if (selectedDate.value < today) return true
  
  // For today, check if it's after 18:00 (class usually ends by then)
  if (selectedDate.value === today) {
    const now = new Date()
    const endHour = 18
    return now.getHours() >= endHour
  }
  return false
})

// Original attendance data (to track what was changed)
const originalAttendance = ref({})

const groupStudents = computed(() => {
  return dataStore.students.filter(s => s.groupId === 1)
})

const subjects = computed(() => {
  return [...new Set(dataStore.schedule.filter(s => s.groupId === 1).map(s => s.subject))]
})

const recentDates = computed(() => {
  const dates = []
  for (let i = 0; i < 14; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
  }
  return dates
})

const attendance = reactive({})

const initializeAttendance = () => {
  groupStudents.value.forEach(student => {
    const existing = dataStore.attendanceRecords.find(
      r => r.studentId === student.id && r.date === selectedDate.value
    )
    if (existing) {
      const data = {
        status: existing.status,
        reason: existing.note || '',
        lateMinutes: existing.lateMinutes || 0
      }
      attendance[student.id] = { ...data }
      originalAttendance.value[student.id] = { ...data }
    } else {
      const data = {
        status: 'present',
        reason: '',
        lateMinutes: 0
      }
      attendance[student.id] = { ...data }
      originalAttendance.value[student.id] = { ...data }
    }
  })
}

watch(selectedDate, () => initializeAttendance())
onMounted(() => initializeAttendance())

// ============ STATUS CHANGE HANDLING ============
const handleStatusChange = (studentId, newStatus) => {
  if (isLessonEnded.value) {
    // Need to provide reason for changes after lesson ends
    const student = groupStudents.value.find(s => s.id === studentId)
    const oldStatus = attendance[studentId]?.status
    
    if (oldStatus !== newStatus) {
      pendingReasonStudent.value = student
      pendingReasonData.value = {
        studentId,
        oldStatus,
        newStatus
      }
      changeReason.value = ''
      showReasonModal.value = true
    }
  } else {
    // Direct change during class
    setStatus(studentId, newStatus)
  }
}

const setStatus = (studentId, status) => {
  attendance[studentId] = {
    ...attendance[studentId],
    status,
    reason: status === 'present' ? '' : attendance[studentId]?.reason || '',
    lateMinutes: status === 'late' ? (attendance[studentId]?.lateMinutes || 5) : 0
  }
}

const confirmChange = () => {
  if (!changeReason.value.trim()) {
    toast.error('Sabab kiritilmagan', 'O\'zgartirish uchun sabab kiritish majburiy')
    return
  }
  
  // Add to pending changes
  const newPending = {
    id: Date.now(),
    studentId: pendingReasonData.value.studentId,
    studentName: pendingReasonStudent.value.name,
    oldStatus: pendingReasonData.value.oldStatus,
    newStatus: pendingReasonData.value.newStatus,
    reason: changeReason.value.trim(),
    requestedAt: new Date().toISOString()
  }
  
  pendingChanges.value.unshift(newPending)
  
  // Update local state (with pending indicator)
  setStatus(pendingReasonData.value.studentId, pendingReasonData.value.newStatus)
  
  toast.info('So\'rov yuborildi', 'O\'zgartirish admin tasdiqlashini kutmoqda')
  showReasonModal.value = false
  changeReason.value = ''
  pendingReasonStudent.value = null
  pendingReasonData.value = null
}

const cancelReasonModal = () => {
  showReasonModal.value = false
  changeReason.value = ''
  pendingReasonStudent.value = null
  pendingReasonData.value = null
}

const hasPendingChange = (studentId) => {
  return pendingChanges.value.some(c => c.studentId === studentId)
}

const markAllAs = (status) => {
  if (isLessonEnded.value) {
    toast.warning('Cheklangan', 'Dars tugagandan keyin ommaviy o\'zgartirish mumkin emas')
    return
  }
  groupStudents.value.forEach(student => setStatus(student.id, status))
  toast.info('Hammasi belgilandi', `Barcha talabalar "${status === 'present' ? 'Keldi' : 'Kelmadi'}" deb belgilandi`)
}

const resetAll = () => {
  initializeAttendance()
  toast.info('Tozalandi', 'Barcha belgilar boshlang\'ich holatga qaytarildi')
}

// ============ COMPUTED COUNTS ============
const presentCount = computed(() => Object.values(attendance).filter(a => a?.status === 'present').length)
const lateCount = computed(() => Object.values(attendance).filter(a => a?.status === 'late').length)
const absentCount = computed(() => Object.values(attendance).filter(a => a?.status === 'absent').length)
const excusedCount = computed(() => Object.values(attendance).filter(a => a?.status === 'excused').length)

// ============ HELPERS ============
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'long',
    weekday: 'long'
  })
}

const formatDateTime = (dateStr) => {
  return new Date(dateStr).toLocaleString('uz-UZ', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusLabel = (status) => {
  const labels = {
    present: 'Keldi',
    absent: 'Kelmadi',
    late: 'Kech qoldi',
    excused: 'Sababli'
  }
  return labels[status] || status
}

const getStatusColor = (status) => {
  const colors = {
    present: 'text-emerald-600',
    absent: 'text-rose-600',
    late: 'text-amber-600',
    excused: 'text-blue-600'
  }
  return colors[status] || 'text-slate-600'
}

// ============ SAVE ============
const saveAttendance = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    if (!isLessonEnded.value) {
      // Direct save during class
      groupStudents.value.forEach(student => {
        const record = attendance[student.id]
        dataStore.addAttendanceRecord({
          studentId: student.id,
          date: selectedDate.value,
          subject: selectedSubject.value || 'Umumiy',
          status: record.status,
          note: record.reason,
          lateMinutes: record.status === 'late' ? record.lateMinutes : 0
        })
      })
      toast.success('Muvaffaqiyatli saqlandi!', `${groupStudents.value.length} ta talaba uchun davomat yozildi`)
    } else {
      // Changes will be pending approval
      toast.info('So\'rov yuborildi', 'O\'zgartirishlar admin tasdiqlashini kutmoqda')
    }
    
    showSummary.value = true
  } catch (error) {
    toast.error('Xatolik!', 'Davomatni saqlashda xatolik yuz berdi')
  } finally {
    saving.value = false
  }
}
</script>

