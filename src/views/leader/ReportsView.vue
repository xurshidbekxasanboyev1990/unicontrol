<template>
  <div class="space-y-6">
    <!-- ========================================
         ESLATMA BANNER (Deadline Reminder)
         ======================================== -->
    <div 
      v-if="showDeadlineReminder"
      class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 p-4 shadow-lg"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3 text-white">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-white/20">
            <Bell :size="20" class="animate-bounce" />
          </div>
          <div>
            <p class="font-semibold">Hisobot topshirish muddati 3 kun qoldi!</p>
            <p class="text-sm text-white/80">{{ currentMonth }} oyi hisobotini topshirishni unutmang</p>
          </div>
        </div>
        <button 
          @click.stop="closeDeadlineReminder"
          type="button"
          class="relative z-10 rounded-lg bg-white/20 p-2 text-white transition-all hover:bg-white/30"
        >
          <X :size="18" />
        </button>
      </div>
      <!-- Decorative circles -->
      <div class="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/10"></div>
      <div class="pointer-events-none absolute -bottom-4 -right-4 h-16 w-16 rounded-full bg-white/10"></div>
    </div>

    <!-- ========================================
         SARLAVHA (Header)
         ======================================== -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Hisobotlar</h1>
        <p class="text-slate-500">{{ currentGroup?.name }} - Guruh hisobotlari</p>
      </div>
      
      <button
        @click="openCreateModal"
        class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600"
      >
        <Plus :size="20" />
        Yangi hisobot
      </button>
    </div>

    <!-- ========================================
         FILTER TABS
         ======================================== -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex rounded-xl bg-slate-100 p-1">
        <button
          @click="activeTab = 'my'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'my' 
            ? 'bg-white text-emerald-600 shadow' 
            : 'text-slate-600 hover:text-slate-800'"
        >
          Mening hisobotlarim
        </button>
        <button
          @click="activeTab = 'others'"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === 'others' 
            ? 'bg-white text-emerald-600 shadow' 
            : 'text-slate-600 hover:text-slate-800'"
        >
          Boshqa guruhlar
        </button>
      </div>

      <!-- Month/Year filter -->
      <div class="flex items-center gap-3">
        <select 
          v-model="selectedMonth"
          class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-700 focus:border-emerald-500 focus:outline-none"
        >
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
        
        <select 
          v-model="selectedYear"
          class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-slate-700 focus:border-emerald-500 focus:outline-none"
        >
          <option value="2026">2026</option>
          <option value="2025">2025</option>
        </select>
      </div>
    </div>

    <!-- ========================================
         MENING HISOBOTLARIM (My Reports)
         ======================================== -->
    <div v-if="activeTab === 'my'" class="space-y-4">
      <div 
        v-for="report in myReports" 
        :key="report.id"
        class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-md"
      >
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex gap-4">
            <div 
              class="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl"
              :class="getStatusIconClass(report.status)"
            >
              <FileText :size="24" />
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-slate-800">{{ report.title }}</h3>
              <p class="mt-1 text-sm text-slate-500">{{ report.period }}</p>
              <div class="mt-2 flex flex-wrap items-center gap-2">
                <span 
                  class="rounded-lg px-2.5 py-1 text-xs font-medium"
                  :class="getStatusBadgeClass(report.status)"
                >
                  {{ getStatusText(report.status) }}
                </span>
                <span class="text-xs text-slate-400">
                  Yaratilgan: {{ report.createdAt }}
                </span>
                <!-- File indicators -->
                <span v-if="report.files?.images > 0" class="flex items-center gap-1 text-xs text-blue-500">
                  <ImageIcon :size="12" /> {{ report.files.images }}
                </span>
                <span v-if="report.files?.videos > 0" class="flex items-center gap-1 text-xs text-purple-500">
                  <Video :size="12" /> {{ report.files.videos }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button 
              @click="viewReport(report)"
              class="rounded-lg bg-slate-100 p-2.5 text-slate-600 transition-all hover:bg-slate-200"
              title="Ko'rish"
            >
              <Eye :size="18" />
            </button>
            <button 
              @click="downloadReport(report)"
              class="rounded-lg bg-emerald-100 p-2.5 text-emerald-600 transition-all hover:bg-emerald-200"
              title="Yuklab olish"
            >
              <Download :size="18" />
            </button>
            <button 
              v-if="report.status === 'draft'"
              @click="editReport(report)"
              class="rounded-lg bg-blue-100 p-2.5 text-blue-600 transition-all hover:bg-blue-200"
              title="Tahrirlash"
            >
              <Pencil :size="18" />
            </button>
            <button 
              @click="deleteReport(report)"
              class="rounded-lg bg-red-100 p-2.5 text-red-600 transition-all hover:bg-red-200"
              title="O'chirish"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-xl bg-green-50 p-3 text-center">
            <p class="text-xl font-bold text-green-600">{{ report.stats?.attendance || 0 }}%</p>
            <p class="text-xs text-green-600/70">Davomat</p>
          </div>
          <div class="rounded-xl bg-blue-50 p-3 text-center">
            <p class="text-xl font-bold text-blue-600">{{ report.stats?.contract || 0 }}%</p>
            <p class="text-xs text-blue-600/70">Kontrakt</p>
          </div>
          <div class="rounded-xl bg-purple-50 p-3 text-center">
            <p class="text-xl font-bold text-purple-600">{{ report.stats?.activities || 0 }}</p>
            <p class="text-xs text-purple-600/70">Tadbirlar</p>
          </div>
          <div class="rounded-xl bg-orange-50 p-3 text-center">
            <p class="text-xl font-bold text-orange-600">{{ report.stats?.meetings || 0 }}</p>
            <p class="text-xs text-orange-600/70">Yig'ilishlar</p>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div 
        v-if="myReports.length === 0"
        class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 py-16"
      >
        <FileText :size="48" class="mb-3 text-slate-300" />
        <p class="text-lg font-medium text-slate-500">Hisobotlar topilmadi</p>
        <p class="text-sm text-slate-400">Yangi hisobot yaratish uchun tugmani bosing</p>
        <button
          @click="openCreateModal"
          class="mt-4 flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white"
        >
          <Plus :size="18" />
          Yangi hisobot
        </button>
      </div>
    </div>

    <!-- ========================================
         BOSHQA GURUHLAR (Other Groups Tab)
         ======================================== -->
    <div v-if="activeTab === 'others'" class="space-y-4">
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <p class="mb-3 text-sm font-medium text-slate-600">Guruhni tanlang:</p>
        <div class="flex flex-wrap gap-2">
          <button
            @click="selectedOtherGroup = null"
            class="rounded-xl px-4 py-2 text-sm font-medium transition-all"
            :class="selectedOtherGroup === null
              ? 'bg-emerald-500 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
          >
            Barchasi
          </button>
          <button
            v-for="group in otherGroups"
            :key="group.id"
            @click="selectedOtherGroup = group.id"
            class="rounded-xl px-4 py-2 text-sm font-medium transition-all"
            :class="selectedOtherGroup === group.id
              ? 'bg-emerald-500 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
          >
            {{ group.name }}
          </button>
        </div>
      </div>

      <!-- Other groups reports list -->
      <div 
        v-for="report in otherGroupsReports" 
        :key="report.id"
        class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div class="flex items-start justify-between">
          <div class="flex gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
              <FileText :size="22" />
            </div>
            <div>
              <h3 class="font-semibold text-slate-800">{{ report.title }}</h3>
              <p class="text-sm text-slate-500">{{ report.groupName }} • {{ report.period }}</p>
            </div>
          </div>
          <button 
            @click="viewReport(report)"
            class="rounded-lg bg-slate-100 p-2 text-slate-600 hover:bg-slate-200"
          >
            <Eye :size="18" />
          </button>
        </div>
      </div>

      <div 
        v-if="otherGroupsReports.length === 0"
        class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 py-12"
      >
        <FileText :size="40" class="mb-2 text-slate-300" />
        <p class="text-slate-500">Boshqa guruhlar hisobotlari topilmadi</p>
      </div>
    </div>

    <!-- ========================================
         HISOBOT YARATISH MODAL
         ======================================== -->
    <div 
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 pt-10"
      @click.self="showCreateModal = false"
    >
      <div class="w-full max-w-4xl rounded-2xl bg-white shadow-2xl">
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-slate-200 p-6">
          <div>
            <h2 class="text-xl font-bold text-slate-800">Yangi hisobot yaratish</h2>
            <p class="text-sm text-slate-500">{{ currentGroup?.name }} - {{ getMonthLabel(newReport.month) }} {{ newReport.year }}</p>
          </div>
          <button 
            @click="showCreateModal = false"
            class="rounded-lg bg-slate-100 p-2 text-slate-500 hover:bg-slate-200"
          >
            <X :size="20" />
          </button>
        </div>

        <!-- Modal Body with Tabs -->
        <div class="max-h-[70vh] overflow-y-auto p-6">
          <!-- Section Tabs -->
          <div class="mb-6 flex flex-wrap gap-2 border-b border-slate-200 pb-4">
            <button
              v-for="section in reportSections"
              :key="section.id"
              @click="activeSection = section.id"
              class="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all"
              :class="activeSection === section.id
                ? 'bg-emerald-500 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            >
              <component :is="section.icon" :size="16" />
              {{ section.label }}
              <span 
                v-if="section.auto"
                class="rounded bg-white/20 px-1.5 py-0.5 text-xs"
              >
                Avto
              </span>
            </button>
          </div>

          <!-- ============ DAVOMAT SECTION (Auto) ============ -->
          <div v-if="activeSection === 'attendance'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-green-50 p-3 text-green-700">
              <CheckCircle :size="20" />
              <span class="text-sm">Bu ma'lumotlar tizim tomonidan avtomatik to'ldirilgan</span>
            </div>

            <!-- Attendance Stats Grid -->
            <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div class="rounded-xl border border-green-200 bg-green-50 p-4 text-center">
                <p class="text-3xl font-bold text-green-600">{{ autoData.attendance.rate }}%</p>
                <p class="text-sm text-green-600/70">Umumiy davomat</p>
              </div>
              <div class="rounded-xl border border-blue-200 bg-blue-50 p-4 text-center">
                <p class="text-3xl font-bold text-blue-600">{{ autoData.attendance.present }}</p>
                <p class="text-sm text-blue-600/70">Qatnashgan</p>
              </div>
              <div class="rounded-xl border border-orange-200 bg-orange-50 p-4 text-center">
                <p class="text-3xl font-bold text-orange-600">{{ autoData.attendance.late }}</p>
                <p class="text-sm text-orange-600/70">Kechikkan</p>
              </div>
              <div class="rounded-xl border border-red-200 bg-red-50 p-4 text-center">
                <p class="text-3xl font-bold text-red-600">{{ autoData.attendance.absent }}</p>
                <p class="text-sm text-red-600/70">Sababsiz</p>
              </div>
            </div>

            <!-- Students Attendance Table -->
            <div class="rounded-xl border border-slate-200">
              <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
                <h4 class="font-semibold text-slate-700">Talabalar davomati</h4>
              </div>
              <div class="divide-y divide-slate-100">
                <div 
                  v-for="student in autoData.studentsAttendance" 
                  :key="student.id"
                  class="flex items-center justify-between px-4 py-3"
                >
                  <span class="text-slate-700">{{ student.name }}</span>
                  <div class="flex items-center gap-4">
                    <span class="text-sm text-green-600">{{ student.present }} dars</span>
                    <span class="text-sm text-red-600">{{ student.absent }} yo'q</span>
                    <span 
                      class="rounded-lg px-2 py-1 text-sm font-medium"
                      :class="student.rate >= 80 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                    >
                      {{ student.rate }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ============ KONTRAKT SECTION (Auto) ============ -->
          <div v-if="activeSection === 'contract'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-green-50 p-3 text-green-700">
              <CheckCircle :size="20" />
              <span class="text-sm">Bu ma'lumotlar tizim tomonidan avtomatik to'ldirilgan</span>
            </div>

            <!-- Contract Stats -->
            <div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-center">
                <p class="text-3xl font-bold text-emerald-600">{{ autoData.contract.rate }}%</p>
                <p class="text-sm text-emerald-600/70">To'langan</p>
              </div>
              <div class="rounded-xl border border-blue-200 bg-blue-50 p-4 text-center">
                <p class="text-2xl font-bold text-blue-600">{{ formatMoney(autoData.contract.paid) }}</p>
                <p class="text-sm text-blue-600/70">To'langan summa</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
                <p class="text-2xl font-bold text-slate-600">{{ formatMoney(autoData.contract.total) }}</p>
                <p class="text-sm text-slate-600/70">Umumiy summa</p>
              </div>
            </div>

            <!-- Students Contract Table -->
            <div class="rounded-xl border border-slate-200">
              <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
                <h4 class="font-semibold text-slate-700">Talabalar kontrakt holati</h4>
              </div>
              <div class="divide-y divide-slate-100">
                <div 
                  v-for="student in autoData.studentsContract" 
                  :key="student.id"
                  class="flex items-center justify-between px-4 py-3"
                >
                  <span class="text-slate-700">{{ student.name }}</span>
                  <div class="flex items-center gap-4">
                    <div class="w-32">
                      <div class="h-2 overflow-hidden rounded-full bg-slate-200">
                        <div 
                          class="h-full rounded-full transition-all"
                          :class="student.rate >= 100 ? 'bg-emerald-500' : student.rate >= 50 ? 'bg-blue-500' : 'bg-red-500'"
                          :style="{ width: `${Math.min(student.rate, 100)}%` }"
                        ></div>
                      </div>
                    </div>
                    <span 
                      class="w-16 text-right text-sm font-medium"
                      :class="student.rate >= 100 ? 'text-emerald-600' : student.rate >= 50 ? 'text-blue-600' : 'text-red-600'"
                    >
                      {{ student.rate }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ============ GURUH FAOLIYATI SECTION (Manual) ============ -->
          <div v-if="activeSection === 'activities'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-700">
              <Pencil :size="20" />
              <span class="text-sm">Guruh tadbirlari va yutuqlarini qo'lda kiriting</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                O'tkazilgan tadbirlar
              </label>
              <textarea
                v-model="newReport.activities.events"
                rows="4"
                placeholder="Masalan: Sport musobaqasi, Ilmiy konferensiya, Volontyorlik..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Guruh yutuqlari
              </label>
              <textarea
                v-model="newReport.activities.achievements"
                rows="3"
                placeholder="Masalan: 1-o'rin olimpiadada, Grant yutildi..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Qo'shimcha izoh
              </label>
              <textarea
                v-model="newReport.activities.notes"
                rows="2"
                placeholder="Boshqa muhim ma'lumotlar..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>
          </div>

          <!-- ============ OTA-ONALAR SECTION (Manual) ============ -->
          <div v-if="activeSection === 'parents'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-700">
              <Pencil :size="20" />
              <span class="text-sm">Ota-onalar bilan ishlash haqida ma'lumot kiriting</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                O'tkazilgan yig'ilishlar
              </label>
              <textarea
                v-model="newReport.parents.meetings"
                rows="3"
                placeholder="Masalan: 15-yanvar - Ota-onalar yig'ilishi (20 nafar qatnashdi)..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Individual suhbatlar
              </label>
              <textarea
                v-model="newReport.parents.conversations"
                rows="3"
                placeholder="Masalan: Aliyev ota-onasi bilan davomat masalasida suhbat..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="mb-2 block text-sm font-medium text-slate-700">
                  Yig'ilishlar soni
                </label>
                <input
                  v-model.number="newReport.parents.meetingsCount"
                  type="number"
                  min="0"
                  class="w-full rounded-xl border border-slate-200 p-3 text-slate-700 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label class="mb-2 block text-sm font-medium text-slate-700">
                  Qatnashgan ota-onalar
                </label>
                <input
                  v-model.number="newReport.parents.attendedParents"
                  type="number"
                  min="0"
                  class="w-full rounded-xl border border-slate-200 p-3 text-slate-700 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          <!-- ============ MUAMMOLAR SECTION (Manual) ============ -->
          <div v-if="activeSection === 'problems'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-amber-50 p-3 text-amber-700">
              <AlertCircle :size="20" />
              <span class="text-sm">Guruhda mavjud muammolarni yozing</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Asosiy muammolar
              </label>
              <textarea
                v-model="newReport.problems.main"
                rows="4"
                placeholder="Masalan: Davomat muammosi, O'quv jarayonidagi qiyinchiliklar..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Yechim talab qiladigan masalalar
              </label>
              <textarea
                v-model="newReport.problems.needsSolution"
                rows="3"
                placeholder="Masalan: Admin yordam kerak, O'quv xona jihozlash..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>
          </div>

          <!-- ============ REJALAR SECTION (Manual) ============ -->
          <div v-if="activeSection === 'plans'" class="space-y-4">
            <div class="flex items-center gap-2 rounded-xl bg-purple-50 p-3 text-purple-700">
              <Calendar :size="20" />
              <span class="text-sm">Keyingi oy uchun rejalarni kiriting</span>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Rejalashtirilgan tadbirlar
              </label>
              <textarea
                v-model="newReport.plans.events"
                rows="3"
                placeholder="Masalan: Guruh sayohati, Ilmiy seminar..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Maqsadlar
              </label>
              <textarea
                v-model="newReport.plans.goals"
                rows="3"
                placeholder="Masalan: Davomat 95%ga ko'tarish, Kontrakt 100% to'lash..."
                class="w-full rounded-xl border border-slate-200 p-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              ></textarea>
            </div>
          </div>

          <!-- ============ FAYLLAR SECTION ============ -->
          <div v-if="activeSection === 'files'" class="space-y-6">
            <div class="flex items-center gap-2 rounded-xl bg-indigo-50 p-3 text-indigo-700">
              <Upload :size="20" />
              <span class="text-sm">Hisobotga tegishli rasm va videolarni yuklang</span>
            </div>

            <!-- Images Upload -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <ImageIcon :size="18" class="text-blue-500" />
                Rasmlar (max 10 ta)
              </label>
              <div class="grid grid-cols-2 gap-4 sm:grid-cols-5">
                <!-- Uploaded images preview -->
                <div 
                  v-for="(img, index) in uploadedImages" 
                  :key="index"
                  class="group relative aspect-square overflow-hidden rounded-xl border border-slate-200"
                >
                  <img :src="img.preview" class="h-full w-full object-cover" />
                  <button
                    @click="removeImage(index)"
                    class="absolute right-1 top-1 rounded-full bg-red-500 p-1 text-white opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    <X :size="14" />
                  </button>
                </div>
                <!-- Upload button -->
                <label 
                  v-if="uploadedImages.length < 10"
                  class="flex aspect-square cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 transition-all hover:border-emerald-400 hover:bg-emerald-50"
                >
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    class="hidden"
                    @change="handleImageUpload"
                  />
                  <Plus :size="24" class="text-slate-400" />
                  <span class="mt-1 text-xs text-slate-500">Qo'shish</span>
                </label>
              </div>
            </div>

            <!-- Videos Upload -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <Video :size="18" class="text-purple-500" />
                Videolar (max 3 ta, har biri 50MB gacha)
              </label>
              <div class="space-y-3">
                <!-- Uploaded videos -->
                <div 
                  v-for="(video, index) in uploadedVideos" 
                  :key="index"
                  class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3"
                >
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100">
                      <Video :size="20" class="text-purple-600" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-700">{{ video.name }}</p>
                      <p class="text-xs text-slate-500">{{ formatFileSize(video.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click="removeVideo(index)"
                    class="rounded-lg bg-red-100 p-2 text-red-600 hover:bg-red-200"
                  >
                    <X :size="16" />
                  </button>
                </div>

                <!-- Upload button -->
                <label 
                  v-if="uploadedVideos.length < 3"
                  class="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-6 transition-all hover:border-purple-400 hover:bg-purple-50"
                >
                  <input
                    type="file"
                    accept="video/*"
                    class="hidden"
                    @change="handleVideoUpload"
                  />
                  <Upload :size="20" class="text-slate-400" />
                  <span class="text-sm text-slate-500">Video yuklash</span>
                </label>
              </div>
            </div>

            <!-- Documents Upload -->
            <div>
              <label class="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <FileText :size="18" class="text-emerald-500" />
                Hujjatlar (PDF, Word - max 5 ta)
              </label>
              <div class="space-y-2">
                <!-- Uploaded documents -->
                <div 
                  v-for="(doc, index) in uploadedDocs" 
                  :key="index"
                  class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3"
                >
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                      <FileText :size="20" class="text-emerald-600" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-700">{{ doc.name }}</p>
                      <p class="text-xs text-slate-500">{{ formatFileSize(doc.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click="removeDoc(index)"
                    class="rounded-lg bg-red-100 p-2 text-red-600 hover:bg-red-200"
                  >
                    <X :size="16" />
                  </button>
                </div>

                <!-- Upload button -->
                <label 
                  v-if="uploadedDocs.length < 5"
                  class="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-4 transition-all hover:border-emerald-400 hover:bg-emerald-50"
                >
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    class="hidden"
                    @change="handleDocUpload"
                  />
                  <Upload :size="18" class="text-slate-400" />
                  <span class="text-sm text-slate-500">Hujjat yuklash</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex items-center justify-between border-t border-slate-200 p-6">
          <div class="flex items-center gap-4">
            <span class="text-sm text-slate-500">
              <span class="font-medium text-emerald-600">{{ completedSections }}</span> / {{ reportSections.length }} bo'lim to'ldirilgan
            </span>
          </div>
          <div class="flex gap-3">
            <button
              @click="saveDraft"
              class="rounded-xl border border-slate-200 px-5 py-2.5 font-medium text-slate-600 transition-all hover:bg-slate-100"
            >
              Qoralama saqlash
            </button>
            <button
              @click="submitReport"
              class="rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600"
            >
              Hisobotni topshirish
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================
         VIEW REPORT MODAL
         ======================================== -->
    <div 
      v-if="showViewModal && selectedReport"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 pt-10"
      @click.self="showViewModal = false"
    >
      <div class="w-full max-w-3xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 p-6">
          <div>
            <h2 class="text-xl font-bold text-slate-800">{{ selectedReport.title }}</h2>
            <p class="text-sm text-slate-500">{{ selectedReport.period }}</p>
          </div>
          <button 
            @click="showViewModal = false"
            class="rounded-lg bg-slate-100 p-2 text-slate-500 hover:bg-slate-200"
          >
            <X :size="20" />
          </button>
        </div>
        
        <div class="max-h-[70vh] overflow-y-auto p-6">
          <!-- Stats Summary -->
          <div class="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div class="rounded-xl bg-green-50 p-4 text-center">
              <p class="text-2xl font-bold text-green-600">{{ selectedReport.stats?.attendance || 0 }}%</p>
              <p class="text-xs text-green-600/70">Davomat</p>
            </div>
            <div class="rounded-xl bg-blue-50 p-4 text-center">
              <p class="text-2xl font-bold text-blue-600">{{ selectedReport.stats?.contract || 0 }}%</p>
              <p class="text-xs text-blue-600/70">Kontrakt</p>
            </div>
            <div class="rounded-xl bg-purple-50 p-4 text-center">
              <p class="text-2xl font-bold text-purple-600">{{ selectedReport.stats?.activities || 0 }}</p>
              <p class="text-xs text-purple-600/70">Tadbirlar</p>
            </div>
            <div class="rounded-xl bg-orange-50 p-4 text-center">
              <p class="text-2xl font-bold text-orange-600">{{ selectedReport.stats?.meetings || 0 }}</p>
              <p class="text-xs text-orange-600/70">Yig'ilishlar</p>
            </div>
          </div>

          <!-- Report Content -->
          <div v-if="selectedReport.content" class="space-y-4">
            <div v-if="selectedReport.content.activities" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">Guruh faoliyati</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.activities }}</p>
            </div>
            <div v-if="selectedReport.content.parents" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">Ota-onalar bilan ishlash</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.parents }}</p>
            </div>
            <div v-if="selectedReport.content.problems" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">Muammolar</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.problems }}</p>
            </div>
            <div v-if="selectedReport.content.plans" class="rounded-xl border border-slate-200 p-4">
              <h4 class="mb-2 font-semibold text-slate-700">Keyingi oy rejalari</h4>
              <p class="text-sm text-slate-600">{{ selectedReport.content.plans }}</p>
            </div>
          </div>

          <!-- Attached Files -->
          <div v-if="selectedReport.files" class="mt-4 flex flex-wrap gap-2">
            <span v-if="selectedReport.files.images > 0" class="flex items-center gap-1 rounded-lg bg-blue-100 px-3 py-1.5 text-sm text-blue-700">
              <ImageIcon :size="14" /> {{ selectedReport.files.images }} rasm
            </span>
            <span v-if="selectedReport.files.videos > 0" class="flex items-center gap-1 rounded-lg bg-purple-100 px-3 py-1.5 text-sm text-purple-700">
              <Video :size="14" /> {{ selectedReport.files.videos }} video
            </span>
            <span v-if="selectedReport.files.docs > 0" class="flex items-center gap-1 rounded-lg bg-emerald-100 px-3 py-1.5 text-sm text-emerald-700">
              <FileText :size="14" /> {{ selectedReport.files.docs }} hujjat
            </span>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t border-slate-200 p-6">
          <button
            @click="downloadReport(selectedReport)"
            class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 font-medium text-white"
          >
            <Download :size="18" />
            PDF yuklash
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ReportsView.vue - Guruh sardori hisobotlar sahifasi
 * 
 * Asosiy funksiyalar:
 * 1. Avtomatik ma'lumotlar - Davomat va Kontrakt (tizimdan)
 * 2. Qo'lda kiritish - Faoliyat, Ota-onalar, Muammolar, Rejalar
 * 3. Fayl yuklash - Rasmlar, Videolar, Hujjatlar
 * 4. Eslatma - Muddat yaqinlashganda ogohlantirish
 */

import { ref, computed, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { 
  Plus, FileText, Eye, Download, Trash2, Pencil, X, Bell,
  CheckCircle, AlertCircle, Calendar, Upload, 
  Image as ImageIcon, Video
} from 'lucide-vue-next'

// ============ STORES ============
const dataStore = useDataStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

// ============ STATE ============
const activeTab = ref('my')
const selectedMonth = ref(new Date().getMonth() + 1)
const selectedYear = ref('2026')
const selectedOtherGroup = ref(null)
const showCreateModal = ref(false)
const showViewModal = ref(false)
const selectedReport = ref(null)
const activeSection = ref('attendance')
const showDeadlineReminder = ref(true)

// File uploads
const uploadedImages = ref([])
const uploadedVideos = ref([])
const uploadedDocs = ref([])

// ============ REPORT FORM ============
const newReport = ref({
  month: new Date().getMonth() + 1,
  year: 2026,
  activities: {
    events: '',
    achievements: '',
    notes: ''
  },
  parents: {
    meetings: '',
    conversations: '',
    meetingsCount: 0,
    attendedParents: 0
  },
  problems: {
    main: '',
    needsSolution: ''
  },
  plans: {
    events: '',
    goals: ''
  }
})

// ============ REPORT SECTIONS CONFIG ============
const reportSections = [
  { id: 'attendance', label: 'Davomat', icon: CheckCircle, auto: true },
  { id: 'contract', label: 'Kontrakt', icon: FileText, auto: true },
  { id: 'activities', label: 'Guruh faoliyati', icon: Calendar, auto: false },
  { id: 'parents', label: 'Ota-onalar', icon: Bell, auto: false },
  { id: 'problems', label: 'Muammolar', icon: AlertCircle, auto: false },
  { id: 'plans', label: 'Rejalar', icon: Calendar, auto: false },
  { id: 'files', label: 'Fayllar', icon: Upload, auto: false }
]

// ============ MONTHS CONFIG ============
const months = [
  { value: 1, label: 'Yanvar' },
  { value: 2, label: 'Fevral' },
  { value: 3, label: 'Mart' },
  { value: 4, label: 'Aprel' },
  { value: 5, label: 'May' },
  { value: 6, label: 'Iyun' },
  { value: 7, label: 'Iyul' },
  { value: 8, label: 'Avgust' },
  { value: 9, label: 'Sentyabr' },
  { value: 10, label: 'Oktyabr' },
  { value: 11, label: 'Noyabr' },
  { value: 12, label: 'Dekabr' }
]

// ============ COMPUTED ============

// Joriy oy nomi
const currentMonth = computed(() => {
  return months.find(m => m.value === selectedMonth.value)?.label || ''
})

// Joriy guruh
const currentGroup = computed(() => {
  const groupId = authStore.user?.groupId
  if (groupId) {
    return dataStore.groups.find(g => g.id === groupId)
  }
  return dataStore.groups.find(g => g.leaderName === authStore.user?.name) || dataStore.groups[0]
})

// Boshqa guruhlar
const otherGroups = computed(() => {
  return dataStore.groups.filter(g => g.id !== currentGroup.value?.id)
})

// Guruh talabalari
const groupStudents = computed(() => {
  if (!currentGroup.value) return []
  return dataStore.students.filter(s => s.groupId === currentGroup.value.id)
})

// Avtomatik ma'lumotlar (Davomat va Kontrakt)
const autoData = computed(() => {
  const students = groupStudents.value
  const groupId = currentGroup.value?.id
  
  // Davomat statistikasi
  const attendanceRecords = dataStore.attendanceRecords.filter(r => {
    const student = dataStore.students.find(s => s.id === r.studentId)
    return student?.groupId === groupId
  })
  
  const present = attendanceRecords.filter(r => r.status === 'present').length
  const late = attendanceRecords.filter(r => r.status === 'late').length
  const absent = attendanceRecords.filter(r => r.status === 'absent').length
  const total = attendanceRecords.length
  const attendanceRate = total > 0 ? Math.round((present + late) / total * 100) : 0

  // Talabalar davomati
  const studentsAttendance = students.map(s => {
    const records = dataStore.attendanceRecords.filter(r => r.studentId === s.id)
    const sPresent = records.filter(r => r.status === 'present').length
    const sAbsent = records.filter(r => r.status === 'absent').length
    const sTotal = records.length
    return {
      id: s.id,
      name: s.name,
      present: sPresent,
      absent: sAbsent,
      rate: sTotal > 0 ? Math.round((sPresent / sTotal) * 100) : 0
    }
  })

  // Kontrakt statistikasi
  const contractTotal = students.length * (currentGroup.value?.contractAmount || 0)
  const contractPaid = students.reduce((sum, s) => sum + (s.contractPaid || 0), 0)
  const contractRate = contractTotal > 0 ? Math.round((contractPaid / contractTotal) * 100) : 0

  // Talabalar kontrakt holati
  const studentsContract = students.map(s => {
    const groupContract = currentGroup.value?.contractAmount || 18411000
    return {
      id: s.id,
      name: s.name,
      paid: s.contractPaid || 0,
      total: groupContract,
      rate: Math.round(((s.contractPaid || 0) / groupContract) * 100)
    }
  })

  return {
    attendance: {
      rate: attendanceRate,
      present,
      late,
      absent
    },
    studentsAttendance,
    contract: {
      rate: contractRate,
      paid: contractPaid,
      total: contractTotal
    },
    studentsContract
  }
})

// Mening hisobotlarim (demo data)
const myReports = ref([
  {
    id: 1,
    title: 'Yanvar oyi hisoboti',
    period: 'Yanvar 2026',
    status: 'approved',
    createdAt: '25.01.2026',
    stats: { attendance: 87, contract: 75, activities: 3, meetings: 2 },
    files: { images: 5, videos: 1, docs: 2 },
    content: {
      activities: 'Sport musobaqasi o\'tkazildi, 3 nafar talaba g\'olib bo\'ldi',
      parents: '2 marta ota-onalar yig\'ilishi, 15 oila qatnashdi',
      problems: 'Davomat bilan bog\'liq muammolar mavjud',
      plans: 'Fevralda davomat 95% ga ko\'tarish maqsad'
    }
  },
  {
    id: 2,
    title: 'Dekabr oyi hisoboti',
    period: 'Dekabr 2025',
    status: 'approved',
    createdAt: '28.12.2025',
    stats: { attendance: 92, contract: 68, activities: 2, meetings: 1 },
    files: { images: 3, videos: 0, docs: 1 },
    content: {
      activities: 'Yangi yil bayramiga tayyorgarlik',
      parents: '1 yig\'ilish o\'tkazildi',
      problems: 'Kontrakt to\'lovlari kechikmoqda',
      plans: 'Yanvarda kontrakt yig\'ish'
    }
  }
])

// Boshqa guruhlar hisobotlari
const otherGroupsReports = computed(() => {
  const demoReports = [
    { id: 101, title: 'Yanvar oyi hisoboti', groupName: 'DI_25-21', groupId: 2, period: 'Yanvar 2026' },
    { id: 102, title: 'Yanvar oyi hisoboti', groupName: 'FTO_24-03', groupId: 3, period: 'Yanvar 2026' },
  ]
  
  if (selectedOtherGroup.value) {
    return demoReports.filter(r => r.groupId === selectedOtherGroup.value)
  }
  return demoReports
})

// To'ldirilgan bo'limlar soni
const completedSections = computed(() => {
  let count = 2 // Davomat va Kontrakt doimo to'liq
  
  if (newReport.value.activities.events || newReport.value.activities.achievements) count++
  if (newReport.value.parents.meetings || newReport.value.parents.meetingsCount > 0) count++
  if (newReport.value.problems.main) count++
  if (newReport.value.plans.events || newReport.value.plans.goals) count++
  if (uploadedImages.value.length > 0 || uploadedVideos.value.length > 0) count++
  
  return count
})

// ============ METHODS ============

// Oy nomini olish
const getMonthLabel = (month) => {
  return months.find(m => m.value === month)?.label || ''
}

// Pul formatini chiqarish
const formatMoney = (amount) => {
  return new Intl.NumberFormat('uz-UZ').format(amount) + ' so\'m'
}

// Fayl hajmini formatlab chiqarish
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Status icon class
const getStatusIconClass = (status) => {
  const classes = {
    approved: 'bg-green-100 text-green-600',
    pending: 'bg-amber-100 text-amber-600',
    draft: 'bg-slate-100 text-slate-600',
    rejected: 'bg-red-100 text-red-600'
  }
  return classes[status] || classes.draft
}

// Status badge class
const getStatusBadgeClass = (status) => {
  const classes = {
    approved: 'bg-green-100 text-green-700',
    pending: 'bg-amber-100 text-amber-700',
    draft: 'bg-slate-100 text-slate-700',
    rejected: 'bg-red-100 text-red-700'
  }
  return classes[status] || classes.draft
}

// Status text
const getStatusText = (status) => {
  const texts = {
    approved: 'Tasdiqlangan',
    pending: 'Tekshirilmoqda',
    draft: 'Qoralama',
    rejected: 'Rad etilgan'
  }
  return texts[status] || 'Noma\'lum'
}

// Eslatmani yopish
const closeDeadlineReminder = () => {
  showDeadlineReminder.value = false
}

// ============ FILE HANDLERS ============

// Rasm yuklash
const handleImageUpload = (event) => {
  const files = event.target.files
  const remaining = 10 - uploadedImages.value.length
  
  for (let i = 0; i < Math.min(files.length, remaining); i++) {
    const file = files[i]
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadedImages.value.push({
        file,
        name: file.name,
        preview: e.target.result
      })
    }
    reader.readAsDataURL(file)
  }
  event.target.value = ''
}

// Rasm o'chirish
const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

// Video yuklash
const handleVideoUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 50MB limit
  if (file.size > 50 * 1024 * 1024) {
    toastStore.error('Video hajmi 50MB dan oshmasligi kerak')
    return
  }
  
  uploadedVideos.value.push({
    file,
    name: file.name,
    size: file.size
  })
  event.target.value = ''
}

// Video o'chirish
const removeVideo = (index) => {
  uploadedVideos.value.splice(index, 1)
}

// Hujjat yuklash
const handleDocUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  uploadedDocs.value.push({
    file,
    name: file.name,
    size: file.size
  })
  event.target.value = ''
}

// Hujjat o'chirish
const removeDoc = (index) => {
  uploadedDocs.value.splice(index, 1)
}

// ============ REPORT ACTIONS ============

// Modal ochish
const openCreateModal = () => {
  // Reset form
  newReport.value = {
    month: new Date().getMonth() + 1,
    year: 2026,
    activities: { events: '', achievements: '', notes: '' },
    parents: { meetings: '', conversations: '', meetingsCount: 0, attendedParents: 0 },
    problems: { main: '', needsSolution: '' },
    plans: { events: '', goals: '' }
  }
  uploadedImages.value = []
  uploadedVideos.value = []
  uploadedDocs.value = []
  activeSection.value = 'attendance'
  showCreateModal.value = true
}

// Qoralama saqlash
const saveDraft = () => {
  const report = {
    id: Date.now(),
    title: `${getMonthLabel(newReport.value.month)} oyi hisoboti`,
    period: `${getMonthLabel(newReport.value.month)} ${newReport.value.year}`,
    status: 'draft',
    createdAt: new Date().toLocaleDateString('uz-UZ'),
    stats: {
      attendance: autoData.value.attendance.rate,
      contract: autoData.value.contract.rate,
      activities: newReport.value.activities.events ? 1 : 0,
      meetings: newReport.value.parents.meetingsCount
    },
    files: {
      images: uploadedImages.value.length,
      videos: uploadedVideos.value.length,
      docs: uploadedDocs.value.length
    },
    content: {
      activities: newReport.value.activities.events,
      parents: newReport.value.parents.meetings,
      problems: newReport.value.problems.main,
      plans: newReport.value.plans.events
    }
  }
  
  myReports.value.unshift(report)
  showCreateModal.value = false
  toastStore.success('Qoralama saqlandi')
}

// Hisobot topshirish
const submitReport = () => {
  const report = {
    id: Date.now(),
    title: `${getMonthLabel(newReport.value.month)} oyi hisoboti`,
    period: `${getMonthLabel(newReport.value.month)} ${newReport.value.year}`,
    status: 'pending',
    createdAt: new Date().toLocaleDateString('uz-UZ'),
    stats: {
      attendance: autoData.value.attendance.rate,
      contract: autoData.value.contract.rate,
      activities: newReport.value.activities.events ? 1 : 0,
      meetings: newReport.value.parents.meetingsCount
    },
    files: {
      images: uploadedImages.value.length,
      videos: uploadedVideos.value.length,
      docs: uploadedDocs.value.length
    },
    content: {
      activities: newReport.value.activities.events,
      parents: newReport.value.parents.meetings,
      problems: newReport.value.problems.main,
      plans: newReport.value.plans.events
    }
  }
  
  myReports.value.unshift(report)
  showCreateModal.value = false
  toastStore.success('Hisobot muvaffaqiyatli topshirildi!')
}

// Hisobotni ko'rish
const viewReport = (report) => {
  selectedReport.value = report
  showViewModal.value = true
}

// Hisobotni tahrirlash
const editReport = (report) => {
  // Fill form with report data
  newReport.value.month = months.find(m => report.period.includes(m.label))?.value || 1
  newReport.value.activities.events = report.content?.activities || ''
  newReport.value.parents.meetings = report.content?.parents || ''
  newReport.value.problems.main = report.content?.problems || ''
  newReport.value.plans.events = report.content?.plans || ''
  
  showCreateModal.value = true
}

// Hisobotni yuklab olish (PDF)
const downloadReport = (report) => {
  toastStore.info(`"${report.title}" yuklab olinmoqda...`)
}

// Hisobotni o'chirish
const deleteReport = (report) => {
  if (confirm('Hisobotni o\'chirishni xohlaysizmi?')) {
    const index = myReports.value.findIndex(r => r.id === report.id)
    if (index !== -1) {
      myReports.value.splice(index, 1)
      toastStore.success('Hisobot o\'chirildi')
    }
  }
}
</script>
