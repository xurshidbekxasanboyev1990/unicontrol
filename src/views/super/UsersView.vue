<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">Foydalanuvchilar boshqaruvi</h1>
        <p class="text-sm text-slate-500">Jami: {{ totalUsers }} ta foydalanuvchi</p>
      </div>
      <button 
        @click="openCreateModal()"
        class="w-full sm:w-auto px-4 py-2.5 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center justify-center gap-2"
      >
        <UserPlus class="w-5 h-5" />
        Yangi foydalanuvchi
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !users.length" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-amber-500 animate-spin" />
      <span class="ml-3 text-slate-600">Yuklanmoqda...</span>
    </div>

    <template v-else>
    <!-- Search & Filter Section -->
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100">
          <Search :size="24" class="text-amber-600" />
        </div>
        <div>
          <h2 class="font-semibold text-slate-800">Foydalanuvchilarni qidirish</h2>
          <p class="text-sm text-slate-500">Ism, login yoki talaba ID bo'yicha qidiring</p>
        </div>
      </div>
      
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="relative flex-1">
          <Search class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Ism, login yoki ID kiriting..."
            class="w-full rounded-xl border border-slate-200 py-3 pl-12 pr-4 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/20"
            @input="onSearchInput"
          />
        </div>
        <select 
          v-model="filterRole"
          class="rounded-xl border border-slate-200 px-4 py-3 focus:border-amber-400 focus:outline-none"
          @change="onFilterChange"
        >
          <option value="">Barcha rollar</option>
          <option value="student">Talaba</option>
          <option value="leader">Sardor</option>
          <option value="admin">Admin</option>
          <option value="superadmin">Super Admin</option>
        </select>
        <select 
          v-model="filterActive"
          class="rounded-xl border border-slate-200 px-4 py-3 focus:border-amber-400 focus:outline-none"
          @change="onFilterChange"
        >
          <option value="">Barchasi</option>
          <option value="true">Faol</option>
          <option value="false">Nofaol</option>
        </select>
      </div>
    </div>

    <!-- Results Table -->
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div class="border-b border-slate-100 bg-slate-50 p-4 flex items-center justify-between">
        <h3 class="font-semibold text-slate-700">
          Foydalanuvchilar: {{ totalUsers }}
        </h3>
        <div v-if="loading" class="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 class="w-4 h-4 animate-spin" />
          Yuklanmoqda...
        </div>
      </div>
      
      <div v-if="users.length === 0 && !loading" class="p-12 text-center">
        <UserX :size="48" class="mx-auto mb-4 text-slate-300" />
        <p class="text-slate-500">Foydalanuvchi topilmadi</p>
        <p class="text-sm text-slate-400 mt-1">Boshqa qidiruv so'zini sinab ko'ring</p>
      </div>
      
      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">#</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">F.I.O</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Login</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Parol</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Rol</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Holat</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Guruh</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Telefon</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Amallar</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr 
              v-for="(user, index) in users" 
              :key="user.id"
              class="hover:bg-slate-50 transition-colors"
              :class="{ 'opacity-50': !user.isActive }"
            >
              <td class="px-4 py-3 text-sm text-slate-500">
                {{ (currentPage - 1) * pageSize + index + 1 }}
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div 
                    class="flex h-9 w-9 items-center justify-center rounded-lg text-sm font-bold text-white flex-shrink-0"
                    :class="getRoleColor(user.role)"
                  >
                    {{ user.name.charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium text-slate-800 text-sm">{{ user.name }}</p>
                    <p v-if="user.email" class="text-xs text-slate-400">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <span class="font-mono text-sm text-slate-700">{{ user.login || '-' }}</span>
                  <button 
                    v-if="user.login"
                    @click="copyToClipboard(user.login)"
                    class="text-slate-300 hover:text-amber-500 transition-colors"
                  >
                    <Copy :size="14" />
                  </button>
                </div>
              </td>
              <td class="px-4 py-3">
                <!-- SuperAdmin can see passwords for ALL users below superadmin -->
                <div v-if="user.role !== 'superadmin' && user.plainPassword" class="flex items-center gap-1">
                  <span v-if="!user.showPassword" class="font-mono text-sm text-slate-500">••••••</span>
                  <span v-else class="font-mono text-sm text-amber-700 font-medium">{{ user.plainPassword }}</span>
                  <button 
                    @click="user.showPassword = !user.showPassword"
                    class="text-slate-300 hover:text-amber-500 transition-colors"
                  >
                    <Eye v-if="!user.showPassword" :size="14" />
                    <EyeOff v-else :size="14" />
                  </button>
                  <button 
                    @click="copyToClipboard(user.plainPassword)"
                    class="text-slate-300 hover:text-amber-500 transition-colors"
                  >
                    <Copy :size="14" />
                  </button>
                </div>
                <span v-else-if="user.role === 'superadmin'" class="text-xs text-slate-400">
                  <Lock :size="14" class="inline" /> Yashirin
                </span>
                <span v-else class="text-xs text-slate-400">
                  O'rnatilmagan
                </span>
              </td>
              <td class="px-4 py-3">
                <span 
                  class="rounded-lg px-2 py-0.5 text-xs font-medium"
                  :class="getRoleBadge(user.role)"
                >
                  {{ getRoleLabel(user.role) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span 
                  class="flex items-center gap-1 text-xs font-medium"
                  :class="user.isActive ? 'text-emerald-600' : 'text-rose-500'"
                >
                  <span class="w-2 h-2 rounded-full" :class="user.isActive ? 'bg-emerald-500' : 'bg-rose-400'"></span>
                  {{ user.isActive ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ user.group || '-' }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ user.phone || '-' }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1">
                  <button 
                    @click="viewUserDetails(user)"
                    class="p-2 rounded-lg text-slate-400 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                    title="Batafsil"
                  >
                    <Eye :size="16" />
                  </button>
                  <button 
                    @click="openEditModal(user)"
                    class="p-2 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                    title="Tahrirlash"
                  >
                    <Pencil :size="16" />
                  </button>
                  <button 
                    @click="resetPasswordModal(user)"
                    class="p-2 rounded-lg text-slate-400 hover:text-violet-600 hover:bg-violet-50 transition-colors"
                    title="Parolni tiklash"
                  >
                    <RefreshCw :size="16" />
                  </button>
                  <button 
                    v-if="user.isActive"
                    @click="toggleUserActive(user, false)"
                    class="p-2 rounded-lg text-slate-400 hover:text-orange-600 hover:bg-orange-50 transition-colors"
                    title="O'chirish"
                  >
                    <UserMinus :size="16" />
                  </button>
                  <button 
                    v-else
                    @click="toggleUserActive(user, true)"
                    class="p-2 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                    title="Faollashtirish"
                  >
                    <UserCheck :size="16" />
                  </button>
                  <button 
                    v-if="user.role !== 'superadmin'"
                    @click="confirmDeleteUser(user)"
                    class="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    title="O'chirish"
                  >
                    <Trash2 :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="border-t border-slate-200 bg-slate-50 px-4 py-3 flex items-center justify-between">
        <div class="text-sm text-slate-500">
          {{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, totalUsers) }} / {{ totalUsers }}
        </div>
        <div class="flex items-center gap-1">
          <button 
            @click="goToPage(1)"
            :disabled="currentPage === 1"
            class="px-2 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="currentPage === 1 ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:bg-white hover:shadow-sm'"
          >
            <ChevronsLeft :size="16" />
          </button>
          <button 
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-2 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="currentPage === 1 ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:bg-white hover:shadow-sm'"
          >
            <ChevronLeft :size="16" />
          </button>
          
          <template v-for="page in visiblePages" :key="page">
            <span v-if="page === '...'" class="px-2 py-1.5 text-sm text-slate-400">...</span>
            <button 
              v-else
              @click="goToPage(page)"
              class="min-w-[36px] px-2 py-1.5 rounded-lg text-sm font-medium transition-colors"
              :class="page === currentPage 
                ? 'bg-amber-500 text-white shadow-sm' 
                : 'text-slate-600 hover:bg-white hover:shadow-sm'"
            >
              {{ page }}
            </button>
          </template>
          
          <button 
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-2 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="currentPage === totalPages ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:bg-white hover:shadow-sm'"
          >
            <ChevronRight :size="16" />
          </button>
          <button 
            @click="goToPage(totalPages)"
            :disabled="currentPage === totalPages"
            class="px-2 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="currentPage === totalPages ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:bg-white hover:shadow-sm'"
          >
            <ChevronsRight :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <Teleport to="body">
      <div 
        v-if="showDetailsModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showDetailsModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">Foydalanuvchi ma'lumotlari</h2>
            <button @click="showDetailsModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div v-if="selectedUser" class="space-y-4">
            <div class="flex items-center gap-4 rounded-xl bg-slate-50 p-4">
              <div 
                class="flex h-14 w-14 items-center justify-center rounded-xl text-xl font-bold text-white"
                :class="getRoleColor(selectedUser.role)"
              >
                {{ selectedUser.name.charAt(0) }}
              </div>
              <div>
                <p class="font-semibold text-slate-800">{{ selectedUser.name }}</p>
                <p class="text-sm text-slate-500">{{ getRoleLabel(selectedUser.role) }}</p>
              </div>
            </div>
            
            <div class="space-y-3">
              <div class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Login</label>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-slate-800">{{ selectedUser.login || '-' }}</span>
                  <button 
                    v-if="selectedUser.login"
                    @click="copyToClipboard(selectedUser.login)"
                    class="text-slate-400 hover:text-amber-500"
                  >
                    <Copy :size="16" />
                  </button>
                </div>
              </div>
              
              <div v-if="selectedUser.role !== 'superadmin' && selectedUser.plainPassword" class="rounded-xl border border-amber-200 bg-amber-50 p-4">
                <label class="mb-1 block text-xs font-medium text-amber-600">Parol</label>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-lg font-bold text-amber-700">{{ selectedUser.plainPassword }}</span>
                  <button 
                    @click="copyToClipboard(selectedUser.plainPassword)"
                    class="text-amber-400 hover:text-amber-600"
                  >
                    <Copy :size="16" />
                  </button>
                </div>
              </div>
              <div v-else class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Parol</label>
                <span class="text-sm text-slate-500">
                  {{ selectedUser.role === 'superadmin' ? 'Xavfsizlik sababli yashirin' : 'O\'rnatilmagan' }}
                </span>
              </div>
              
              <div v-if="selectedUser.email" class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Email</label>
                <span class="text-slate-800">{{ selectedUser.email }}</span>
              </div>
              
              <div v-if="selectedUser.studentId" class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Talaba ID</label>
                <span class="text-slate-800">{{ selectedUser.studentId }}</span>
              </div>
              
              <div v-if="selectedUser.group" class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Guruh</label>
                <span class="text-slate-800">{{ selectedUser.group }}</span>
              </div>
              
              <div v-if="selectedUser.phone" class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Telefon</label>
                <span class="text-slate-800">{{ selectedUser.phone }}</span>
              </div>

              <div class="rounded-xl border border-slate-200 p-4">
                <label class="mb-1 block text-xs font-medium text-slate-500">Holat</label>
                <span :class="selectedUser.isActive ? 'text-emerald-600' : 'text-rose-500'" class="font-medium">
                  {{ selectedUser.isActive ? 'Faol' : 'Nofaol' }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button 
              @click="showDetailsModal = false"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200"
            >
              Yopish
            </button>
            <button 
              @click="showDetailsModal = false; openEditModal(selectedUser)"
              class="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white hover:bg-amber-600 flex items-center justify-center gap-2"
            >
              <Pencil :size="16" />
              Tahrirlash
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Create/Edit User Modal -->
    <Teleport to="body">
      <div 
        v-if="showFormModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm overflow-y-auto"
        @click.self="showFormModal = false"
      >
        <div class="w-full max-w-lg rounded-2xl bg-white shadow-2xl my-8">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">
              {{ editingUser ? 'Foydalanuvchini tahrirlash' : 'Yangi foydalanuvchi qo\'shish' }}
            </h2>
            <button @click="showFormModal = false" class="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <X class="w-5 h-5 text-slate-500" />
            </button>
          </div>
          
          <form @submit.prevent="saveUser" class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">F.I.O *</label>
                <input 
                  v-model="form.name"
                  type="text"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                  placeholder="Ism familiya"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Email *</label>
                <input 
                  v-model="form.email"
                  type="email"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                  placeholder="email@example.com"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Login</label>
                <input 
                  v-model="form.login"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                  placeholder="Login"
                />
              </div>
              <div v-if="!editingUser">
                <label class="block text-sm font-medium text-slate-700 mb-2">Parol *</label>
                <input 
                  v-model="form.password"
                  type="text"
                  :required="!editingUser"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                  placeholder="Parol"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Rol *</label>
                <select 
                  v-model="form.role"
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                >
                  <option value="student">Talaba</option>
                  <option value="leader">Sardor</option>
                  <option value="admin">Admin</option>
                  <option value="superadmin">Super Admin</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Telefon</label>
                <input 
                  v-model="form.phone"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
                  placeholder="+998901234567"
                />
              </div>
            </div>

            <div v-if="editingUser" class="flex items-center gap-3 p-4 rounded-xl bg-slate-50">
              <input 
                type="checkbox"
                v-model="form.is_active"
                id="isActive"
                class="w-4 h-4 text-amber-500 border-slate-300 rounded focus:ring-amber-500"
              />
              <label for="isActive" class="text-sm font-medium text-slate-700">Faol holat</label>
            </div>
            
            <div class="flex gap-3 pt-4">
              <button 
                type="button"
                @click="showFormModal = false"
                :disabled="saving"
                class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
              >
                Bekor qilish
              </button>
              <button 
                type="submit"
                :disabled="saving"
                class="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white hover:bg-amber-600 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
                {{ saving ? 'Saqlanmoqda...' : (editingUser ? 'Saqlash' : 'Qo\'shish') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Reset Password Modal -->
    <Teleport to="body">
      <div 
        v-if="showResetModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showResetModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">Parolni tiklash</h2>
            <button @click="showResetModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div v-if="selectedUser" class="space-y-4">
            <div class="rounded-xl bg-slate-50 p-4 text-center">
              <p class="text-slate-600">
                <strong>{{ selectedUser.name }}</strong> uchun yangi parol o'rnating
              </p>
            </div>
            
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Yangi parol</label>
              <input 
                v-model="newPassword"
                type="text"
                placeholder="Yangi parol kiriting"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/20"
              />
            </div>
            
            <div class="flex gap-3">
              <button 
                @click="generatePassword"
                class="flex-1 rounded-xl border border-slate-200 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Avtomatik yaratish
              </button>
              <button 
                @click="newPassword = '123456'"
                class="flex-1 rounded-xl border border-slate-200 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Standart (123456)
              </button>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button 
              @click="showResetModal = false"
              :disabled="resetting"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
            >
              Bekor qilish
            </button>
            <button 
              @click="confirmReset"
              :disabled="!newPassword || resetting"
              class="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white hover:bg-amber-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Loader2 v-if="resetting" class="w-4 h-4 animate-spin" />
              {{ resetting ? 'Saqlanmoqda...' : 'Saqlash' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div 
        v-if="showDeleteModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showDeleteModal = false"
      >
        <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
          <div class="text-center mb-4">
            <div class="mx-auto w-16 h-16 rounded-full bg-rose-100 flex items-center justify-center mb-4">
              <AlertTriangle :size="32" class="text-rose-500" />
            </div>
            <h2 class="text-lg font-bold text-slate-800">O'chirishni tasdiqlang</h2>
            <p class="text-sm text-slate-500 mt-2" v-if="selectedUser">
              <strong>{{ selectedUser.name }}</strong> foydalanuvchisini o'chirmoqchimisiz?
              Bu amalni qaytarib bo'lmaydi.
            </p>
          </div>
          
          <div class="flex gap-3">
            <button 
              @click="showDeleteModal = false"
              :disabled="deleting"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
            >
              Bekor qilish
            </button>
            <button 
              @click="deleteUser"
              :disabled="deleting"
              class="flex-1 rounded-xl bg-rose-500 py-3 font-medium text-white hover:bg-rose-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Loader2 v-if="deleting" class="w-4 h-4 animate-spin" />
              {{ deleting ? 'O\'chirilmoqda...' : 'O\'chirish' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
    </template>
  </div>
</template>

<script setup>
/**
 * Super Admin UsersView.vue - Full User Management
 * 
 * SuperAdmin privileges:
 * - View ALL users (including admins)
 * - Create/Edit/Delete users
 * - Change user roles (including to admin)
 * - See passwords for all users below superadmin
 * - Activate/Deactivate users
 * - Reset passwords
 * - Server-side pagination (50 per page)
 * - Server-side search
 */

import api from '@/services/api'
import { useToastStore } from '@/stores/toast'
import {
    AlertTriangle,
    ChevronLeft,
    ChevronRight,
    ChevronsLeft,
    ChevronsRight,
    Copy,
    Eye,
    EyeOff,
    Loader2,
    Lock,
    Pencil,
    RefreshCw,
    Search,
    Trash2,
    UserCheck,
    UserMinus,
    UserPlus,
    UserX,
    X
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

const toast = useToastStore()

// Pagination state
const currentPage = ref(1)
const pageSize = 50
const totalUsers = ref(0)
const totalPages = ref(0)
const users = ref([])
const loading = ref(true)

// Search & filter
const searchQuery = ref('')
const filterRole = ref('')
const filterActive = ref('')
let searchTimeout = null

// Modals
const showDetailsModal = ref(false)
const showFormModal = ref(false)
const showResetModal = ref(false)
const showDeleteModal = ref(false)
const selectedUser = ref(null)
const editingUser = ref(null)
const newPassword = ref('')
const resetting = ref(false)
const saving = ref(false)
const deleting = ref(false)

// Form
const form = ref({
  name: '',
  email: '',
  login: '',
  password: '',
  role: 'student',
  phone: '',
  is_active: true
})

// Visible pagination pages
const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }
  
  pages.push(1)
  if (current > 3) pages.push('...')
  
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  
  if (current < total - 2) pages.push('...')
  pages.push(total)
  
  return pages
})

// Load users from server
async function loadUsers() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    if (filterRole.value) {
      params.role = filterRole.value
    }
    if (filterActive.value !== '') {
      params.is_active = filterActive.value === 'true'
    }
    
    const response = await api.getUsers(params)
    const items = response?.items || []
    
    users.value = items.map(u => ({
      id: u.id,
      name: u.full_name || u.name || 'Noma\'lum',
      studentId: u.student_id || '',
      phone: u.phone || '',
      group: u.group_name || '',
      role: u.role || 'student',
      login: u.login || '',
      email: u.email || '',
      plainPassword: u.plain_password || null,
      isActive: u.is_active !== false,
      showPassword: false
    }))
    
    totalUsers.value = response?.total || 0
    totalPages.value = response?.total_pages || 1
  } catch (err) {
    console.error('Error loading users:', err)
    toast.error('Foydalanuvchilarni yuklashda xatolik')
  } finally {
    loading.value = false
  }
}

// Search with debounce
function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadUsers()
  }, 400)
}

// Filter change
function onFilterChange() {
  currentPage.value = 1
  loadUsers()
}

// Navigate to page
function goToPage(page) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  loadUsers()
}

// Role helpers
function getRoleColor(role) {
  const colors = {
    student: 'bg-gradient-to-br from-blue-400 to-blue-600',
    leader: 'bg-gradient-to-br from-emerald-400 to-emerald-600',
    admin: 'bg-gradient-to-br from-violet-400 to-violet-600',
    superadmin: 'bg-gradient-to-br from-amber-400 to-orange-600'
  }
  return colors[role] || colors.student
}

function getRoleBadge(role) {
  const badges = {
    student: 'bg-blue-100 text-blue-700',
    leader: 'bg-emerald-100 text-emerald-700',
    admin: 'bg-violet-100 text-violet-700',
    superadmin: 'bg-amber-100 text-amber-700'
  }
  return badges[role] || badges.student
}

function getRoleLabel(role) {
  const labels = {
    student: 'Talaba',
    leader: 'Sardor',
    admin: 'Admin',
    superadmin: 'Super Admin'
  }
  return labels[role] || 'Foydalanuvchi'
}

// View user details
function viewUserDetails(user) {
  selectedUser.value = user
  showDetailsModal.value = true
}

// Create user modal
function openCreateModal() {
  editingUser.value = null
  form.value = {
    name: '',
    email: '',
    login: '',
    password: '',
    role: 'student',
    phone: '',
    is_active: true
  }
  showFormModal.value = true
}

// Edit user modal
function openEditModal(user) {
  editingUser.value = user
  form.value = {
    name: user.name,
    email: user.email,
    login: user.login,
    password: '',
    role: user.role,
    phone: user.phone || '',
    is_active: user.isActive
  }
  showFormModal.value = true
}

// Save user (create or update)
async function saveUser() {
  saving.value = true
  try {
    if (editingUser.value) {
      // Update
      const updateData = {
        name: form.value.name,
        email: form.value.email,
        role: form.value.role,
        phone: form.value.phone || null,
        is_active: form.value.is_active
      }
      await api.updateUser(editingUser.value.id, updateData)
      toast.success('Yangilandi', `${form.value.name} ma'lumotlari yangilandi`)
    } else {
      // Create
      const createData = {
        name: form.value.name,
        email: form.value.email,
        login: form.value.login || form.value.email,
        password: form.value.password,
        role: form.value.role,
        phone: form.value.phone || null
      }
      await api.createUser(createData)
      toast.success('Qo\'shildi', `${form.value.name} muvaffaqiyatli qo'shildi`)
    }
    
    showFormModal.value = false
    loadUsers()
  } catch (err) {
    console.error('Error saving user:', err)
    const msg = err?.response?.data?.detail || err?.message || 'Xatolik yuz berdi'
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

// Reset password modal
function resetPasswordModal(user) {
  selectedUser.value = user
  newPassword.value = ''
  showResetModal.value = true
}

// Generate password
function generatePassword() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  let password = ''
  for (let i = 0; i < 8; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  newPassword.value = password
}

// Confirm reset password
async function confirmReset() {
  if (!newPassword.value) return
  
  resetting.value = true
  try {
    await api.resetUserPassword(selectedUser.value.id, newPassword.value)
    
    // Update local user data
    const user = users.value.find(u => u.id === selectedUser.value.id)
    if (user && user.role !== 'superadmin') {
      user.plainPassword = newPassword.value
    }
    
    toast.success('Parol yangilandi', `${selectedUser.value.name} uchun yangi parol o'rnatildi`)
    showResetModal.value = false
  } catch (err) {
    console.error('Error resetting password:', err)
    toast.error('Parolni tiklashda xatolik')
  } finally {
    resetting.value = false
  }
}

// Toggle user active status
async function toggleUserActive(user, activate) {
  try {
    if (activate) {
      await api.request(`/users/${user.id}/activate`, { method: 'POST' })
      user.isActive = true
      toast.success('Faollashtirildi', `${user.name} faollashtirildi`)
    } else {
      await api.request(`/users/${user.id}/deactivate`, { method: 'POST' })
      user.isActive = false
      toast.success('O\'chirildi', `${user.name} nofaol qilindi`)
    }
  } catch (err) {
    console.error('Error toggling user:', err)
    toast.error('Xatolik yuz berdi')
  }
}

// Confirm delete
function confirmDeleteUser(user) {
  selectedUser.value = user
  showDeleteModal.value = true
}

// Delete user
async function deleteUser() {
  if (!selectedUser.value) return
  
  deleting.value = true
  try {
    await api.deleteUser(selectedUser.value.id)
    toast.success('O\'chirildi', `${selectedUser.value.name} o'chirildi`)
    showDeleteModal.value = false
    loadUsers()
  } catch (err) {
    console.error('Error deleting user:', err)
    const msg = err?.response?.data?.detail || err?.message || 'O\'chirishda xatolik'
    toast.error(msg)
  } finally {
    deleting.value = false
  }
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
  toast.info('Nusxalandi', 'Ma\'lumot clipboard\'ga nusxalandi')
}

// Load on mount
onMounted(() => {
  loadUsers()
})
</script>
