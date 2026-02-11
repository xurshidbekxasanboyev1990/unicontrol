<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-amber-500 animate-spin" />
      <span class="ml-3 text-slate-600">{{ $t('common.loading') }}</span>
    </div>

    <template v-else>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">{{ $t('admins.title') }}</h1>
        <p class="text-sm text-slate-500">{{ admins.length }} ta admin</p>
      </div>
      <button 
        @click="openModal()"
        class="w-full sm:w-auto px-4 py-2.5 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center justify-center gap-2"
      >
        <UserPlus class="w-5 h-5" />
        Yangi admin
      </button>
    </div>

    <!-- Admins Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="admin in admins" 
        :key="admin.id"
        class="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-4">
            <div 
              class="w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold"
              :class="admin.role === 'super' ? 'bg-gradient-to-br from-amber-500 to-orange-600' : 'bg-gradient-to-br from-violet-500 to-purple-600'"
            >
              {{ admin.name.charAt(0) }}
            </div>
            <div>
              <h3 class="font-semibold text-slate-800">{{ admin.name }}</h3>
              <p class="text-sm text-slate-500">{{ admin.email }}</p>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Shield class="w-4 h-4" />
              Rol
            </span>
            <span 
              class="px-2 py-0.5 rounded-lg text-xs font-medium"
              :class="admin.role === 'super' ? 'bg-amber-100 text-amber-700' : 'bg-violet-100 text-violet-700'"
            >
              {{ admin.role === 'super' ? 'Super Admin' : 'Admin' }}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Calendar class="w-4 h-4" />
              Qo'shilgan
            </span>
            <span class="text-slate-700">{{ formatDate(admin.createdAt) }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500 flex items-center gap-2">
              <Activity class="w-4 h-4" />
              Holat
            </span>
            <span 
              class="flex items-center gap-1 font-medium"
              :class="admin.active ? 'text-emerald-600' : 'text-slate-400'"
            >
              <span class="w-2 h-2 rounded-full" :class="admin.active ? 'bg-emerald-500' : 'bg-slate-300'"></span>
              {{ admin.active ? 'Faol' : 'Nofaol' }}
            </span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-100 flex gap-2">
          <button 
            @click="openModal(admin)"
            class="flex-1 px-3 py-2 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
          >
            <Pencil class="w-4 h-4" />
            Tahrirlash
          </button>
          <button 
            v-if="admin.role !== 'super'"
            @click="confirmDelete(admin)"
            class="px-3 py-2 bg-rose-100 text-rose-700 rounded-xl text-sm font-medium hover:bg-rose-200 transition-colors"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    </template>

    <!-- Add/Edit Modal -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto"
        @click.self="showModal = false"
      >
        <div class="bg-white rounded-2xl max-w-2xl w-full my-8">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-800">
              {{ editingAdmin ? 'Adminni tahrirlash' : 'Yangi admin qo\'shish' }}
            </h2>
            <button @click="showModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <form @submit.prevent="saveAdmin" class="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
            <!-- Asosiy ma'lumotlar -->
            <div class="space-y-4">
              <h3 class="text-sm font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-2">
                <User class="w-4 h-4" />
                Asosiy ma'lumotlar
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">F.I.O</label>
                  <input 
                    v-model="form.name"
                    type="text"
                    required
                    class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                    placeholder="Ism familiya"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <input 
                    v-model="form.email"
                    type="email"
                    required
                    class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                    placeholder="admin@example.com"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Username</label>
                  <input 
                    v-model="form.username"
                    type="text"
                    required
                    class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                    placeholder="admin_username"
                  />
                </div>
                <div v-if="!editingAdmin">
                  <label class="block text-sm font-medium text-slate-700 mb-2">Parol</label>
                  <input 
                    v-model="form.password"
                    type="password"
                    required
                    class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                    placeholder="••••••••"
                  />
                </div>
              </div>
              <div class="flex items-center gap-6">
                <div class="flex items-center gap-3">
                  <input 
                    v-model="form.active"
                    type="checkbox"
                    id="active"
                    class="w-5 h-5 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
                  />
                  <label for="active" class="text-sm text-slate-700">Faol holat</label>
                </div>
                <div class="flex items-center gap-3">
                  <input 
                    v-model="form.isSuperAdmin"
                    type="checkbox"
                    id="isSuperAdmin"
                    class="w-5 h-5 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
                  />
                  <label for="isSuperAdmin" class="text-sm text-slate-700">Super Admin</label>
                </div>
              </div>
            </div>

            <!-- Ruxsatlar -->
            <div v-if="!form.isSuperAdmin" class="space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-2">
                  <ShieldCheck class="w-4 h-4" />
                  Ruxsatlar
                </h3>
                <button 
                  type="button"
                  @click="toggleAllPermissions"
                  class="text-xs text-amber-600 hover:text-amber-700 font-medium"
                >
                  {{ allPermissionsEnabled ? 'Barchasini o\'chirish' : 'Barchasini yoqish' }}
                </button>
              </div>

              <!-- Permission Groups -->
              <div class="space-y-3">
                <div 
                  v-for="group in permissionGroups" 
                  :key="group.id"
                  class="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden"
                >
                  <div 
                    class="px-4 py-3 bg-slate-100 flex items-center justify-between cursor-pointer"
                    @click="group.expanded = !group.expanded"
                  >
                    <div class="flex items-center gap-3">
                      <component :is="group.icon" class="w-5 h-5 text-slate-600" />
                      <span class="font-medium text-slate-800">{{ group.name }}</span>
                      <span class="text-xs text-slate-500">({{ getEnabledCount(group) }}/{{ group.permissions.length }})</span>
                    </div>
                    <div class="flex items-center gap-3">
                      <label class="flex items-center gap-2" @click.stop>
                        <input 
                          type="checkbox"
                          :checked="isGroupAllChecked(group)"
                          @change="toggleGroupPermissions(group, $event)"
                          class="w-4 h-4 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
                        />
                        <span class="text-xs text-slate-500">Hammasi</span>
                      </label>
                      <ChevronDown 
                        :class="['w-5 h-5 text-slate-400 transition-transform', group.expanded && 'rotate-180']" 
                      />
                    </div>
                  </div>
                  
                  <Transition
                    enter-active-class="transition-all duration-200"
                    enter-from-class="opacity-0 max-h-0"
                    enter-to-class="opacity-100 max-h-96"
                    leave-active-class="transition-all duration-200"
                    leave-from-class="opacity-100 max-h-96"
                    leave-to-class="opacity-0 max-h-0"
                  >
                    <div v-if="group.expanded" class="p-2 sm:p-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <label 
                        v-for="perm in group.permissions" 
                        :key="perm.id"
                        class="flex items-start gap-2 sm:gap-3 p-2 sm:p-3 bg-white rounded-lg border border-slate-100 hover:border-amber-200 cursor-pointer transition-colors"
                      >
                        <input 
                          type="checkbox"
                          v-model="form.permissions[perm.id]"
                          class="w-4 h-4 mt-0.5 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
                        />
                        <div>
                          <p class="text-sm font-medium text-slate-700">{{ perm.label }}</p>
                          <p class="text-xs text-slate-400">{{ perm.description }}</p>
                        </div>
                      </label>
                    </div>
                  </Transition>
                </div>
              </div>
            </div>

            <!-- Super Admin uchun -->
            <div v-else class="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <div class="flex items-center gap-3 text-amber-700">
                <Crown class="w-5 h-5" />
                <p class="text-sm font-medium">Super Admin barcha ruxsatlarga ega bo'ladi</p>
              </div>
            </div>

            <div class="flex gap-3 pt-4 border-t border-slate-100">
              <button 
                type="button"
                @click="showModal = false"
                class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
              >
                Bekor qilish
              </button>
              <button 
                type="submit"
                class="flex-1 px-4 py-3 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center justify-center gap-2"
              >
                <Save class="w-5 h-5" />
                Saqlash
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Delete Confirmation -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showDeleteConfirm = false"
      >
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 text-center">
          <div class="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle class="w-8 h-8 text-rose-500" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 mb-2">O'chirishni tasdiqlang</h3>
          <p class="text-slate-500 mb-6">
            {{ deletingAdmin?.name }} adminini o'chirmoqchimisiz?
          </p>
          <div class="flex gap-3">
            <button 
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              @click="deleteAdmin"
              class="flex-1 px-4 py-3 bg-rose-500 text-white rounded-xl font-medium hover:bg-rose-600 transition-colors"
            >
              O'chirish
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {
    Activity,
    AlertTriangle,
    BarChart3,
    Bell,
    BookOpen,
    Calendar,
    ChevronDown,
    ClipboardCheck,
    Crown,
    Layers,
    Library,
    Loader2,
    Palette,
    Pencil,
    Save,
    Settings,
    Shield,
    ShieldCheck,
    Trash2,
    Trophy,
    User,
    UserPlus,
    Users,
    UtensilsCrossed,
    Wallet,
    X
} from 'lucide-vue-next'
import { computed, markRaw, onMounted, reactive, ref } from 'vue'
import api from '../../services/api'
import { useToastStore } from '../../stores/toast'

const toast = useToastStore()
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingAdmin = ref(null)
const deletingAdmin = ref(null)
const loading = ref(true)
const saving = ref(false)

const admins = ref([])

// Permission Groups
const permissionGroups = ref([
  {
    id: 'students',
    name: 'Talabalar boshqaruvi',
    icon: markRaw(Users),
    expanded: true,
    permissions: [
      { id: 'students_view', label: 'Ko\'rish', description: 'Talabalar ro\'yxatini ko\'rish' },
      { id: 'students_create', label: 'Qo\'shish', description: 'Yangi talaba qo\'shish' },
      { id: 'students_edit', label: 'Tahrirlash', description: 'Talaba ma\'lumotlarini o\'zgartirish' },
      { id: 'students_delete', label: 'O\'chirish', description: 'Talabani o\'chirish' },
      { id: 'students_export', label: 'Eksport', description: 'Talabalar ro\'yxatini yuklab olish' },
      { id: 'students_import', label: 'Import', description: 'Excel dan talabalar yuklash' },
      { id: 'students_attendance', label: 'Davomat', description: 'Talabalar davomatini ko\'rish' },
      { id: 'students_grades', label: 'Baholar', description: 'Talabalar baholarini ko\'rish' }
    ]
  },
  {
    id: 'groups',
    name: 'Guruhlar boshqaruvi',
    icon: markRaw(Layers),
    expanded: false,
    permissions: [
      { id: 'groups_view', label: 'Ko\'rish', description: 'Guruhlar ro\'yxatini ko\'rish' },
      { id: 'groups_create', label: 'Yaratish', description: 'Yangi guruh yaratish' },
      { id: 'groups_edit', label: 'Tahrirlash', description: 'Guruh ma\'lumotlarini o\'zgartirish' },
      { id: 'groups_delete', label: 'O\'chirish', description: 'Guruhni o\'chirish' },
      { id: 'groups_assign_leader', label: 'Sardor tayinlash', description: 'Guruhga sardor tayinlash' },
      { id: 'groups_manage_students', label: 'Talabalar', description: 'Guruh tarkibini boshqarish' },
      { id: 'groups_schedule', label: 'Jadval', description: 'Guruh jadvalini ko\'rish/o\'zgartirish' }
    ]
  },
  {
    id: 'users',
    name: 'Foydalanuvchilar',
    icon: markRaw(User),
    expanded: false,
    permissions: [
      { id: 'users_view', label: 'Ko\'rish', description: 'Foydalanuvchilar ro\'yxati' },
      { id: 'users_create', label: 'Yaratish', description: 'Yangi foydalanuvchi yaratish' },
      { id: 'users_edit', label: 'Tahrirlash', description: 'Foydalanuvchi ma\'lumotlarini o\'zgartirish' },
      { id: 'users_delete', label: 'O\'chirish', description: 'Foydalanuvchini o\'chirish' },
      { id: 'users_reset_password', label: 'Parol tiklash', description: 'Foydalanuvchi parolini tiklash' },
      { id: 'users_block', label: 'Bloklash', description: 'Foydalanuvchini bloklash/aktivlashtirish' },
      { id: 'users_roles', label: 'Rollar', description: 'Foydalanuvchi rolini o\'zgartirish' }
    ]
  },
  {
    id: 'attendance',
    name: 'Davomat tizimi',
    icon: markRaw(ClipboardCheck),
    expanded: false,
    permissions: [
      { id: 'attendance_view', label: 'Ko\'rish', description: 'Davomat ma\'lumotlarini ko\'rish' },
      { id: 'attendance_mark', label: 'Belgilash', description: 'Davomat belgilash' },
      { id: 'attendance_edit', label: 'Tahrirlash', description: 'Davomat o\'zgartirish' },
      { id: 'attendance_reports', label: 'Hisobotlar', description: 'Davomat hisobotlari' },
      { id: 'attendance_export', label: 'Eksport', description: 'Davomatni yuklab olish' }
    ]
  },
  {
    id: 'schedule',
    name: 'Dars jadvali',
    icon: markRaw(Calendar),
    expanded: false,
    permissions: [
      { id: 'schedule_view', label: 'Ko\'rish', description: 'Dars jadvalini ko\'rish' },
      { id: 'schedule_create', label: 'Yaratish', description: 'Yangi dars qo\'shish' },
      { id: 'schedule_edit', label: 'Tahrirlash', description: 'Dars jadvalini o\'zgartirish' },
      { id: 'schedule_delete', label: 'O\'chirish', description: 'Darsni o\'chirish' },
      { id: 'schedule_rooms', label: 'Xonalar', description: 'Xonalarni boshqarish' }
    ]
  },
  {
    id: 'subjects',
    name: 'Fanlar',
    icon: markRaw(BookOpen),
    expanded: false,
    permissions: [
      { id: 'subjects_view', label: 'Ko\'rish', description: 'Fanlar ro\'yxati' },
      { id: 'subjects_create', label: 'Qo\'shish', description: 'Yangi fan qo\'shish' },
      { id: 'subjects_edit', label: 'Tahrirlash', description: 'Fan ma\'lumotlarini o\'zgartirish' },
      { id: 'subjects_delete', label: 'O\'chirish', description: 'Fanni o\'chirish' },
      { id: 'subjects_teachers', label: 'O\'qituvchilar', description: 'Fanga o\'qituvchi biriktirish' }
    ]
  },
  {
    id: 'reports',
    name: 'Hisobotlar',
    icon: markRaw(BarChart3),
    expanded: false,
    permissions: [
      { id: 'reports_view', label: 'Ko\'rish', description: 'Hisobotlarni ko\'rish' },
      { id: 'reports_create', label: 'Yaratish', description: 'Yangi hisobot yaratish' },
      { id: 'reports_export', label: 'Eksport', description: 'Hisobotlarni yuklab olish' },
      { id: 'reports_analytics', label: 'Analitika', description: 'Statistik ma\'lumotlar' },
      { id: 'reports_financial', label: 'Moliyaviy', description: 'Moliyaviy hisobotlar' }
    ]
  },
  {
    id: 'notifications',
    name: 'Bildirishnomalar',
    icon: markRaw(Bell),
    expanded: false,
    permissions: [
      { id: 'notifications_view', label: 'Ko\'rish', description: 'Bildirishnomalarni ko\'rish' },
      { id: 'notifications_send', label: 'Yuborish', description: 'Bildirishnoma yuborish' },
      { id: 'notifications_send_all', label: 'Ommaviy', description: 'Barcha foydalanuvchilarga yuborish' },
      { id: 'notifications_templates', label: 'Shablonlar', description: 'Shablon yaratish/tahrirlash' },
      { id: 'notifications_schedule', label: 'Rejalashtirish', description: 'Bildirishnoma rejalashtirish' }
    ]
  },
  {
    id: 'clubs',
    name: 'To\'garaklar',
    icon: markRaw(Palette),
    expanded: false,
    permissions: [
      { id: 'clubs_view', label: 'Ko\'rish', description: 'To\'garaklar ro\'yxati' },
      { id: 'clubs_create', label: 'Yaratish', description: 'Yangi to\'garak yaratish' },
      { id: 'clubs_edit', label: 'Tahrirlash', description: 'To\'garak ma\'lumotlarini o\'zgartirish' },
      { id: 'clubs_delete', label: 'O\'chirish', description: 'To\'garakni o\'chirish' },
      { id: 'clubs_members', label: 'A\'zolar', description: 'To\'garak a\'zolarini boshqarish' },
      { id: 'clubs_events', label: 'Tadbirlar', description: 'Tadbirlarni boshqarish' }
    ]
  },
  {
    id: 'tournaments',
    name: 'Turnirlar',
    icon: markRaw(Trophy),
    expanded: false,
    permissions: [
      { id: 'tournaments_view', label: 'Ko\'rish', description: 'Turnirlar ro\'yxati' },
      { id: 'tournaments_create', label: 'Yaratish', description: 'Yangi turnir yaratish' },
      { id: 'tournaments_edit', label: 'Tahrirlash', description: 'Turnir ma\'lumotlarini o\'zgartirish' },
      { id: 'tournaments_delete', label: 'O\'chirish', description: 'Turnirni o\'chirish' },
      { id: 'tournaments_results', label: 'Natijalar', description: 'Natijalarni kiritish' },
      { id: 'tournaments_prizes', label: 'Sovrinlar', description: 'Sovrinlarni boshqarish' }
    ]
  },
  {
    id: 'library',
    name: 'Kutubxona',
    icon: markRaw(Library),
    expanded: false,
    permissions: [
      { id: 'library_view', label: 'Ko\'rish', description: 'Kutubxona resurslarini ko\'rish' },
      { id: 'library_add', label: 'Qo\'shish', description: 'Yangi resurs qo\'shish' },
      { id: 'library_edit', label: 'Tahrirlash', description: 'Resurs ma\'lumotlarini o\'zgartirish' },
      { id: 'library_delete', label: 'O\'chirish', description: 'Resursni o\'chirish' },
      { id: 'library_borrow', label: 'Berish', description: 'Kitob berish/olish' }
    ]
  },
  {
    id: 'canteen',
    name: 'Oshxona',
    icon: markRaw(UtensilsCrossed),
    expanded: false,
    permissions: [
      { id: 'canteen_view', label: 'Ko\'rish', description: 'Menyu va buyurtmalarni ko\'rish' },
      { id: 'canteen_menu', label: 'Menyu', description: 'Menyuni boshqarish' },
      { id: 'canteen_orders', label: 'Buyurtmalar', description: 'Buyurtmalarni boshqarish' },
      { id: 'canteen_reports', label: 'Hisobotlar', description: 'Oshxona hisobotlari' }
    ]
  },
  {
    id: 'finance',
    name: 'Moliya',
    icon: markRaw(Wallet),
    expanded: false,
    permissions: [
      { id: 'finance_view', label: 'Ko\'rish', description: 'Moliyaviy ma\'lumotlarni ko\'rish' },
      { id: 'finance_payments', label: 'To\'lovlar', description: 'To\'lovlarni boshqarish' },
      { id: 'finance_scholarships', label: 'Stipendiyalar', description: 'Stipendiyalarni boshqarish' },
      { id: 'finance_reports', label: 'Hisobotlar', description: 'Moliyaviy hisobotlar' },
      { id: 'finance_debts', label: 'Qarzdorlik', description: 'Qarzdorlikni kuzatish' }
    ]
  },
  {
    id: 'settings',
    name: 'Tizim sozlamalari',
    icon: markRaw(Settings),
    expanded: false,
    permissions: [
      { id: 'settings_view', label: 'Ko\'rish', description: 'Sozlamalarni ko\'rish' },
      { id: 'settings_general', label: 'Umumiy', description: 'Umumiy sozlamalar' },
      { id: 'settings_academic', label: 'O\'quv yili', description: 'O\'quv yili sozlamalari' },
      { id: 'settings_backup', label: 'Zaxira', description: 'Zaxira nusxa yaratish' },
      { id: 'settings_logs', label: 'Loglar', description: 'Tizim loglarini ko\'rish' },
      { id: 'landing_edit', label: 'Landing sahifa', description: 'Asosiy sahifani boshqarish' }
    ]
  }
])

const form = reactive({
  name: '',
  email: '',
  username: '',
  password: '',
  active: true,
  isSuperAdmin: false,
  permissions: {}
})

// Initialize default permissions
const initPermissions = () => {
  const perms = {}
  permissionGroups.value.forEach(group => {
    group.permissions.forEach(perm => {
      perms[perm.id] = false
    })
  })
  return perms
}

// Computed
const allPermissionsEnabled = computed(() => {
  return permissionGroups.value.every(group => 
    group.permissions.every(perm => form.permissions[perm.id])
  )
})

const getEnabledCount = (group) => {
  return group.permissions.filter(perm => form.permissions[perm.id]).length
}

const isGroupAllChecked = (group) => {
  return group.permissions.every(perm => form.permissions[perm.id])
}

// Methods
const toggleAllPermissions = () => {
  const newValue = !allPermissionsEnabled.value
  permissionGroups.value.forEach(group => {
    group.permissions.forEach(perm => {
      form.permissions[perm.id] = newValue
    })
  })
}

const toggleGroupPermissions = (group, event) => {
  const checked = event.target.checked
  group.permissions.forEach(perm => {
    form.permissions[perm.id] = checked
  })
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const openModal = (admin = null) => {
  // Reset permission groups expanded state
  permissionGroups.value.forEach((g, i) => g.expanded = i === 0)
  
  if (admin) {
    editingAdmin.value = admin
    form.name = admin.name
    form.email = admin.email
    form.username = admin.username
    form.active = admin.active
    form.isSuperAdmin = admin.role === 'super'
    form.password = ''
    form.permissions = { ...initPermissions(), ...admin.permissions }
  } else {
    editingAdmin.value = null
    form.name = ''
    form.email = ''
    form.username = ''
    form.password = ''
    form.active = true
    form.isSuperAdmin = false
    form.permissions = initPermissions()
  }
  showModal.value = true
}

const saveAdmin = async () => {
  saving.value = true
  try {
    const adminData = {
      name: form.name,
      email: form.email,
      role: form.isSuperAdmin ? 'superadmin' : 'admin',
      is_active: form.active,
      phone: form.phone || null
    }

    if (editingAdmin.value) {
      // Update existing admin via API
      const updated = await api.updateAdmin(editingAdmin.value.id, adminData)
      const index = admins.value.findIndex(a => a.id === editingAdmin.value.id)
      if (index !== -1) {
        admins.value[index] = mapAdminFromApi(updated)
      }
      toast.success('Admin yangilandi')
    } else {
      // Create new admin via API  
      const created = await api.createAdmin({
        ...adminData,
        password: form.password
      })
      admins.value.push(mapAdminFromApi(created))
      toast.success('Yangi admin qo\'shildi')
    }
    showModal.value = false
  } catch (err) {
    console.error('Error saving admin:', err)
    toast.error(err.message || 'Admin saqlashda xatolik')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (admin) => {
  deletingAdmin.value = admin
  showDeleteConfirm.value = true
}

const deleteAdmin = async () => {
  if (deletingAdmin.value) {
    try {
      await api.deleteAdmin(deletingAdmin.value.id)
      admins.value = admins.value.filter(a => a.id !== deletingAdmin.value.id)
      toast.success('Admin o\'chirildi')
    } catch (err) {
      console.error('Error deleting admin:', err)
      toast.error(err.message || 'Admin o\'chirishda xatolik')
    }
  }
  showDeleteConfirm.value = false
  deletingAdmin.value = null
}

// Map backend user response to frontend admin format
const mapAdminFromApi = (user) => ({
  id: user.id,
  name: user.name || user.full_name || '',
  email: user.email || '',
  username: user.email?.split('@')[0] || '',
  role: user.role === 'superadmin' ? 'super' : 'admin',
  active: user.is_active !== false,
  createdAt: user.created_at || new Date().toISOString(),
  permissions: user.permissions || {}
})

// Load admins from API
const loadAdmins = async () => {
  loading.value = true
  try {
    const response = await api.getAdmins()
    const adminsList = Array.isArray(response) ? response : (response?.items || response?.data || [])
    admins.value = adminsList.map(mapAdminFromApi)
  } catch (err) {
    console.error('Error loading admins:', err)
    toast.error('Adminlarni yuklashda xatolik')
    
    // Fallback: try getting users with admin role
    try {
      const usersResp = await api.getUsers({ role: 'admin', page_size: 100 })
      const superResp = await api.getUsers({ role: 'superadmin', page_size: 100 })
      const allAdmins = [
        ...(superResp?.items || []),
        ...(usersResp?.items || [])
      ]
      admins.value = allAdmins.map(mapAdminFromApi)
    } catch (e2) {
      console.error('Fallback also failed:', e2)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAdmins()
})
</script>
