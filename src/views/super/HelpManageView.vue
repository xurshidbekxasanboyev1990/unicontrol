<template>
  <div class="space-y-6">
    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <div class="h-8 w-56 bg-slate-200 rounded animate-pulse"></div>
          <div class="h-4 w-40 bg-slate-100 rounded mt-2 animate-pulse"></div>
        </div>
        <div class="h-12 w-40 bg-slate-200 rounded-xl animate-pulse"></div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="bg-white rounded-2xl border border-slate-200 p-6 animate-pulse">
          <div class="h-6 w-32 bg-slate-200 rounded mb-4"></div>
          <div class="space-y-3">
            <div class="h-12 bg-slate-100 rounded-xl"></div>
            <div class="h-12 bg-slate-100 rounded-xl"></div>
          </div>
        </div>
      </div>
    </div>

    <template v-else>
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Yordam bo'limini boshqarish</h1>
        <p class="text-slate-500">FAQ savollari va kontakt ma'lumotlarini tahrirlash</p>
      </div>
      <button 
        @click="openAddFaqModal"
        class="flex items-center gap-2 px-5 py-3 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors"
      >
        <Plus :size="20" />
        Yangi savol qo'shish
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 border-b border-slate-200">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === tab.id 
          ? 'text-amber-600 border-amber-500' 
          : 'text-slate-500 border-transparent hover:text-slate-700'"
      >
        <component :is="tab.icon" :size="18" />
        {{ tab.name }}
      </button>
    </div>

    <!-- FAQ Management Tab -->
    <div v-if="activeTab === 'faq'" class="space-y-6">
      <!-- Categories -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Folder :size="20" class="text-slate-400" />
            Kategoriyalar
          </h2>
          <button 
            @click="openAddCategoryModal"
            class="text-sm text-amber-600 hover:text-amber-700 font-medium flex items-center gap-1"
          >
            <Plus :size="16" />
            Kategoriya qo'shish
          </button>
        </div>
        <div class="flex flex-wrap gap-2">
          <div 
            v-for="category in categories" 
            :key="category.id"
            class="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-xl group"
          >
            <component :is="getCategoryIcon(category.icon)" :size="16" class="text-slate-500" />
            <span class="text-sm font-medium text-slate-700">{{ category.name }}</span>
            <span class="text-xs text-slate-400">({{ getCategoryFaqCount(category.id) }})</span>
            <button 
              @click="editCategory(category)"
              class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-amber-500 transition-all"
            >
              <Pencil :size="14" />
            </button>
            <button 
              @click="deleteCategory(category)"
              class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-all"
            >
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
      </div>

      <!-- FAQ List -->
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">FAQ Savollar ({{ faqs.length }})</h2>
          <div class="flex items-center gap-3">
            <select 
              v-model="filterCategory"
              class="text-sm border border-slate-200 rounded-lg px-3 py-2"
            >
              <option value="">Barcha kategoriyalar</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
        </div>

        <div v-if="filteredFaqs.length === 0" class="p-12 text-center">
          <HelpCircle :size="48" class="mx-auto mb-4 text-slate-300" />
          <p class="text-slate-500">Savollar topilmadi</p>
        </div>

        <draggable 
          v-else
          v-model="filteredFaqs" 
          item-key="id"
          handle=".drag-handle"
          class="divide-y divide-slate-100"
          @end="onDragEnd"
        >
          <template #item="{ element: faq }">
            <div class="p-4 hover:bg-slate-50 transition-colors">
              <div class="flex items-start gap-4">
                <div class="drag-handle cursor-move text-slate-300 hover:text-slate-500 mt-1">
                  <GripVertical :size="20" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs px-2 py-0.5 rounded-lg bg-slate-100 text-slate-600">
                      {{ getCategoryName(faq.category_id) }}
                    </span>
                    <span 
                      class="text-xs px-2 py-0.5 rounded-lg"
                      :class="faq.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'"
                    >
                      {{ faq.is_active ? 'Faol' : 'Nofaol' }}
                    </span>
                  </div>
                  <p class="font-medium text-slate-800">{{ faq.question }}</p>
                  <p class="text-sm text-slate-500 mt-1 line-clamp-2">{{ faq.answer }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <button 
                    @click="toggleFaqStatus(faq)"
                    class="p-2 rounded-lg hover:bg-slate-100 transition-colors"
                    :class="faq.is_active ? 'text-emerald-500' : 'text-slate-400'"
                  >
                    <Eye :size="18" />
                  </button>
                  <button 
                    @click="editFaq(faq)"
                    class="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-amber-500 transition-colors"
                  >
                    <Pencil :size="18" />
                  </button>
                  <button 
                    @click="deleteFaq(faq)"
                    class="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 :size="18" />
                  </button>
                </div>
              </div>
            </div>
          </template>
        </draggable>
      </div>
    </div>

    <!-- Contact Info Tab -->
    <div v-if="activeTab === 'contact'" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Phone Numbers -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Phone :size="20" class="text-slate-400" />
              Telefon raqamlar
            </h2>
            <button 
              @click="addContactField('phones')"
              class="text-sm text-amber-600 hover:text-amber-700 font-medium flex items-center gap-1"
            >
              <Plus :size="16" />
              Qo'shish
            </button>
          </div>
          <div class="space-y-3">
            <div 
              v-for="(phone, index) in contactInfo.phones" 
              :key="index"
              class="flex items-center gap-2"
            >
              <input 
                v-model="contactInfo.phones[index]"
                type="text"
                placeholder="+998 XX XXX XX XX"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
              <button 
                @click="removeContactField('phones', index)"
                class="p-2 text-slate-400 hover:text-red-500"
              >
                <X :size="20" />
              </button>
            </div>
          </div>
        </div>

        <!-- Email Addresses -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Mail :size="20" class="text-slate-400" />
              Email manzillar
            </h2>
            <button 
              @click="addContactField('emails')"
              class="text-sm text-amber-600 hover:text-amber-700 font-medium flex items-center gap-1"
            >
              <Plus :size="16" />
              Qo'shish
            </button>
          </div>
          <div class="space-y-3">
            <div 
              v-for="(email, index) in contactInfo.emails" 
              :key="index"
              class="flex items-center gap-2"
            >
              <input 
                v-model="contactInfo.emails[index]"
                type="email"
                placeholder="email@example.com"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
              <button 
                @click="removeContactField('emails', index)"
                class="p-2 text-slate-400 hover:text-red-500"
              >
                <X :size="20" />
              </button>
            </div>
          </div>
        </div>

        <!-- Social Media -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Share2 :size="20" class="text-slate-400" />
              Ijtimoiy tarmoqlar
            </h2>
          </div>
          <div class="space-y-3">
            <div class="flex items-center gap-2">
              <div class="w-24 text-sm text-slate-500">Telegram:</div>
              <input 
                v-model="contactInfo.telegram"
                type="text"
                placeholder="@username"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
            <div class="flex items-center gap-2">
              <div class="w-24 text-sm text-slate-500">Instagram:</div>
              <input 
                v-model="contactInfo.instagram"
                type="text"
                placeholder="@username"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
            <div class="flex items-center gap-2">
              <div class="w-24 text-sm text-slate-500">Facebook:</div>
              <input 
                v-model="contactInfo.facebook"
                type="text"
                placeholder="facebook.com/page"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
            <div class="flex items-center gap-2">
              <div class="w-24 text-sm text-slate-500">YouTube:</div>
              <input 
                v-model="contactInfo.youtube"
                type="text"
                placeholder="youtube.com/channel"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
          </div>
        </div>

        <!-- Address -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-4">
            <MapPin :size="20" class="text-slate-400" />
            Manzil
          </h2>
          <div class="space-y-3">
            <textarea 
              v-model="contactInfo.address"
              rows="3"
              placeholder="To'liq manzil..."
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none resize-none"
            ></textarea>
            <div class="flex items-center gap-2">
              <div class="w-24 text-sm text-slate-500">Ish vaqti:</div>
              <input 
                v-model="contactInfo.working_hours"
                type="text"
                placeholder="Dush-Jum: 9:00 - 18:00"
                class="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Save Contact Button -->
      <div class="flex justify-end">
        <button 
          @click="saveContactInfo"
          :disabled="isSaving"
          class="px-6 py-3 bg-amber-500 text-white rounded-xl font-medium hover:bg-amber-600 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <Loader2 v-if="isSaving" class="w-5 h-5 animate-spin" />
          <Save v-else class="w-5 h-5" />
          {{ isSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
        </button>
      </div>
    </div>

    <!-- Support Messages Tab -->
    <div v-if="activeTab === 'messages'" class="space-y-4">
      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">Foydalanuvchi murojaatlari ({{ messages.length }})</h2>
          <select 
            v-model="messageFilter"
            class="text-sm border border-slate-200 rounded-lg px-3 py-2"
          >
            <option value="">Barchasi</option>
            <option value="new">Yangi</option>
            <option value="in_progress">Ko'rilmoqda</option>
            <option value="resolved">Hal qilindi</option>
          </select>
        </div>

        <div v-if="filteredMessages.length === 0" class="p-12 text-center">
          <MessageCircle :size="48" class="mx-auto mb-4 text-slate-300" />
          <p class="text-slate-500">Murojaatlar yo'q</p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div 
            v-for="msg in filteredMessages" 
            :key="msg.id"
            class="p-4 hover:bg-slate-50 transition-colors cursor-pointer"
            @click="openMessageModal(msg)"
          >
            <div class="flex items-start gap-4">
              <div 
                class="flex h-10 w-10 items-center justify-center rounded-xl text-white font-bold"
                :class="getStatusColor(msg.status)"
              >
                {{ (msg.user_name || 'F').charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-medium text-slate-800">{{ msg.user_name }}</span>
                  <span 
                    class="text-xs px-2 py-0.5 rounded-lg"
                    :class="getStatusBadge(msg.status)"
                  >
                    {{ getStatusLabel(msg.status) }}
                  </span>
                </div>
                <p class="text-sm text-slate-600 font-medium">{{ msg.subject }}</p>
                <p class="text-sm text-slate-500 line-clamp-1 mt-1">{{ msg.message }}</p>
                <p class="text-xs text-slate-400 mt-2">{{ formatDate(msg.created_at) }}</p>
              </div>
              <ChevronRight :size="20" class="text-slate-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
    </template>

    <!-- Add/Edit FAQ Modal -->
    <Teleport to="body">
      <div 
        v-if="showFaqModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showFaqModal = false"
      >
        <div class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">
              {{ editingFaq ? 'Savolni tahrirlash' : 'Yangi savol qo\'shish' }}
            </h2>
            <button @click="showFaqModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Kategoriya</label>
              <select 
                v-model="faqForm.category_id"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              >
                <option value="">Kategoriya tanlang</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Savol</label>
              <input 
                v-model="faqForm.question"
                type="text"
                placeholder="Savol matnini kiriting"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Javob</label>
              <textarea 
                v-model="faqForm.answer"
                rows="5"
                placeholder="Javob matnini kiriting"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none resize-none"
              ></textarea>
            </div>

            <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
              <input 
                type="checkbox" 
                v-model="faqForm.is_active"
                id="faqActive"
                class="w-5 h-5 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
              />
              <label for="faqActive" class="text-sm text-slate-700">Faol (foydalanuvchilarga ko'rinadi)</label>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button 
              @click="showFaqModal = false"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200"
            >
              Bekor qilish
            </button>
            <button 
              @click="saveFaq"
              :disabled="!faqForm.question || !faqForm.answer || isSaving"
              class="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white hover:bg-amber-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
              {{ isSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Add/Edit Category Modal -->
    <Teleport to="body">
      <div 
        v-if="showCategoryModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showCategoryModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">
              {{ editingCategory ? 'Kategoriyani tahrirlash' : 'Yangi kategoriya' }}
            </h2>
            <button @click="showCategoryModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Kategoriya nomi</label>
              <input 
                v-model="categoryForm.name"
                type="text"
                placeholder="Masalan: Davomat"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Ikonka</label>
              <div class="grid grid-cols-6 gap-2">
                <button
                  v-for="icon in availableIcons"
                  :key="icon.name"
                  @click="categoryForm.icon = icon.name"
                  class="p-3 rounded-xl border transition-colors"
                  :class="categoryForm.icon === icon.name ? 'border-amber-500 bg-amber-50' : 'border-slate-200 hover:bg-slate-50'"
                >
                  <component :is="icon.component" :size="20" class="mx-auto text-slate-600" />
                </button>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button 
              @click="showCategoryModal = false"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200"
            >
              Bekor qilish
            </button>
            <button 
              @click="saveCategory"
              :disabled="!categoryForm.name || isSaving"
              class="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white hover:bg-amber-600 disabled:opacity-50"
            >
              Saqlash
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Message Detail Modal -->
    <Teleport to="body">
      <div 
        v-if="showMessageModal" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click.self="showMessageModal = false"
      >
        <div class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-800">Murojaat tafsilotlari</h2>
            <button @click="showMessageModal = false" class="text-slate-400 hover:text-slate-600">
              <X :size="24" />
            </button>
          </div>
          
          <div v-if="selectedMessage" class="space-y-4">
            <div class="flex items-center gap-4 p-4 bg-slate-50 rounded-xl">
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-amber-600 font-bold text-lg">
                {{ (selectedMessage.user_name || 'F').charAt(0) }}
              </div>
              <div>
                <p class="font-semibold text-slate-800">{{ selectedMessage.user_name }}</p>
                <p class="text-sm text-slate-500">{{ selectedMessage.user_email }}</p>
              </div>
              <div class="ml-auto">
                <select 
                  v-model="selectedMessage.status"
                  @change="updateMessageStatus"
                  class="text-sm border border-slate-200 rounded-lg px-3 py-2"
                >
                  <option value="new">Yangi</option>
                  <option value="in_progress">Ko'rilmoqda</option>
                  <option value="resolved">Hal qilindi</option>
                </select>
              </div>
            </div>

            <div class="p-4 border border-slate-200 rounded-xl">
              <p class="text-xs text-slate-400 mb-1">Mavzu</p>
              <p class="font-medium text-slate-800">{{ selectedMessage.subject }}</p>
            </div>

            <div class="p-4 border border-slate-200 rounded-xl">
              <p class="text-xs text-slate-400 mb-1">Xabar</p>
              <p class="text-slate-700 whitespace-pre-wrap">{{ selectedMessage.message }}</p>
            </div>

            <div class="p-4 bg-slate-50 rounded-xl">
              <p class="text-xs text-slate-400 mb-2">Javob yozish</p>
              <textarea 
                v-model="replyMessage"
                rows="4"
                placeholder="Javobingizni yozing..."
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none resize-none"
              ></textarea>
            </div>
          </div>
          
          <div class="mt-6 flex gap-3">
            <button 
              @click="showMessageModal = false"
              class="flex-1 rounded-xl bg-slate-100 py-3 font-medium text-slate-700 hover:bg-slate-200"
            >
              Yopish
            </button>
            <button 
              @click="sendReply"
              :disabled="!replyMessage || isSaving"
              class="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white hover:bg-amber-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Send :size="18" />
              Javob yuborish
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * HelpManageView.vue - Yordam bo'limini boshqarish
 * 
 * Super admin imkoniyatlari:
 * - FAQ savollarni qo'shish/tahrirlash/o'chirish
 * - Kategoriyalarni boshqarish
 * - Kontakt ma'lumotlarini tahrirlash
 * - Foydalanuvchi murojaatlarini ko'rish va javob berish
 */

import { ref, reactive, computed, onMounted, markRaw } from 'vue'
import api from '@/services/api'
import { useToastStore } from '@/stores/toast'
import {
  Plus,
  Pencil,
  Trash2,
  X,
  Save,
  Loader2,
  HelpCircle,
  Folder,
  Phone,
  Mail,
  Share2,
  MapPin,
  MessageCircle,
  Send,
  Eye,
  GripVertical,
  ChevronRight,
  // Category icons
  BookOpen,
  CreditCard,
  Calendar,
  ClipboardCheck,
  Users,
  Bell,
  Settings,
  Shield,
  FileText
} from 'lucide-vue-next'

// Draggable import (agar mavjud bo'lmasa oddiy div ishlatamiz)
const draggable = {
  name: 'draggable',
  template: '<div><slot></slot></div>',
  props: ['modelValue', 'itemKey', 'handle'],
  emits: ['update:modelValue', 'end']
}

const toast = useToastStore()

// State
const isLoading = ref(true)
const isSaving = ref(false)
const activeTab = ref('faq')

// Tabs
const tabs = [
  { id: 'faq', name: 'FAQ Savollar', icon: markRaw(HelpCircle) },
  { id: 'contact', name: 'Kontakt ma\'lumotlari', icon: markRaw(Phone) },
  { id: 'messages', name: 'Murojaatlar', icon: markRaw(MessageCircle) }
]

// Available icons for categories
const availableIcons = [
  { name: 'BookOpen', component: markRaw(BookOpen) },
  { name: 'CreditCard', component: markRaw(CreditCard) },
  { name: 'Calendar', component: markRaw(Calendar) },
  { name: 'ClipboardCheck', component: markRaw(ClipboardCheck) },
  { name: 'Users', component: markRaw(Users) },
  { name: 'Bell', component: markRaw(Bell) },
  { name: 'Settings', component: markRaw(Settings) },
  { name: 'Shield', component: markRaw(Shield) },
  { name: 'FileText', component: markRaw(FileText) },
  { name: 'HelpCircle', component: markRaw(HelpCircle) },
  { name: 'Phone', component: markRaw(Phone) },
  { name: 'Mail', component: markRaw(Mail) }
]

// FAQ data
const categories = ref([])

const faqs = ref([])

const filterCategory = ref('')

const filteredFaqs = computed(() => {
  if (!filterCategory.value) return faqs.value
  return faqs.value.filter(f => f.category_id === filterCategory.value)
})

// Contact info
const contactInfo = reactive({
  phones: [],
  emails: [],
  telegram: '',
  instagram: '',
  facebook: '',
  youtube: '',
  address: '',
  working_hours: ''
})

// Messages
const messages = ref([])

const messageFilter = ref('')
const filteredMessages = computed(() => {
  if (!messageFilter.value) return messages.value
  return messages.value.filter(m => m.status === messageFilter.value)
})

// Modals
const showFaqModal = ref(false)
const showCategoryModal = ref(false)
const showMessageModal = ref(false)
const editingFaq = ref(null)
const editingCategory = ref(null)
const selectedMessage = ref(null)
const replyMessage = ref('')

const faqForm = reactive({
  category_id: '',
  question: '',
  answer: '',
  is_active: true
})

const categoryForm = reactive({
  name: '',
  icon: 'HelpCircle'
})

// Helper functions
const getCategoryIcon = (iconName) => {
  const icon = availableIcons.find(i => i.name === iconName)
  return icon ? icon.component : HelpCircle
}

const getCategoryName = (categoryId) => {
  const cat = categories.value.find(c => c.id === categoryId)
  return cat ? cat.name : 'Noma\'lum'
}

const getCategoryFaqCount = (categoryId) => {
  return faqs.value.filter(f => f.category_id === categoryId).length
}

const getStatusColor = (status) => {
  const colors = {
    new: 'bg-blue-500',
    in_progress: 'bg-amber-500',
    resolved: 'bg-emerald-500'
  }
  return colors[status] || 'bg-slate-500'
}

const getStatusBadge = (status) => {
  const badges = {
    new: 'bg-blue-100 text-blue-700',
    in_progress: 'bg-amber-100 text-amber-700',
    resolved: 'bg-emerald-100 text-emerald-700'
  }
  return badges[status] || 'bg-slate-100 text-slate-700'
}

const getStatusLabel = (status) => {
  const labels = {
    new: 'Yangi',
    in_progress: 'Ko\'rilmoqda',
    resolved: 'Hal qilindi'
  }
  return labels[status] || status
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('uz-UZ', { 
    day: 'numeric', 
    month: 'short', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// FAQ functions
const openAddFaqModal = () => {
  editingFaq.value = null
  faqForm.category_id = ''
  faqForm.question = ''
  faqForm.answer = ''
  faqForm.is_active = true
  showFaqModal.value = true
}

const editFaq = (faq) => {
  editingFaq.value = faq
  faqForm.category_id = faq.category_id
  faqForm.question = faq.question
  faqForm.answer = faq.answer
  faqForm.is_active = faq.is_active
  showFaqModal.value = true
}

const saveFaq = async () => {
  if (!faqForm.question || !faqForm.answer) return
  
  isSaving.value = true
  try {
    if (editingFaq.value) {
      // Update via API
      const response = await api.updateFaq(editingFaq.value.id, {
        category_id: faqForm.category_id,
        question: faqForm.question,
        answer: faqForm.answer,
        is_active: faqForm.is_active
      })
      const index = faqs.value.findIndex(f => f.id === editingFaq.value.id)
      if (index !== -1) {
        faqs.value[index] = { ...faqs.value[index], ...faqForm }
      }
      toast.success('Muvaffaqiyat', 'Savol yangilandi')
    } else {
      // Create via API
      const response = await api.createFaq({
        category_id: faqForm.category_id,
        question: faqForm.question,
        answer: faqForm.answer,
        is_active: faqForm.is_active
      })
      const newFaq = {
        id: response?.id || Date.now(),
        ...faqForm,
        order: faqs.value.length + 1
      }
      faqs.value.push(newFaq)
      toast.success('Muvaffaqiyat', 'Yangi savol qo\'shildi')
    }
    showFaqModal.value = false
  } catch (error) {
    toast.error('Xatolik', error.message || 'Saqlashda xatolik yuz berdi')
  } finally {
    isSaving.value = false
  }
}

const deleteFaq = async (faq) => {
  if (confirm(`"${faq.question}" savolini o'chirishni xohlaysizmi?`)) {
    try {
      await api.deleteFaq(faq.id)
      faqs.value = faqs.value.filter(f => f.id !== faq.id)
      toast.success('O\'chirildi', 'Savol o\'chirildi')
    } catch (error) {
      toast.error('Xatolik', error.message || 'O\'chirishda xatolik')
    }
  }
}

const toggleFaqStatus = (faq) => {
  faq.is_active = !faq.is_active
  toast.info('Yangilandi', faq.is_active ? 'Savol faollashtirildi' : 'Savol nofaol qilindi')
}

const onDragEnd = () => {
  // Update order
  filteredFaqs.value.forEach((faq, index) => {
    faq.order = index + 1
  })
}

// Category functions
const openAddCategoryModal = () => {
  editingCategory.value = null
  categoryForm.name = ''
  categoryForm.icon = 'HelpCircle'
  showCategoryModal.value = true
}

const editCategory = (category) => {
  editingCategory.value = category
  categoryForm.name = category.name
  categoryForm.icon = category.icon
  showCategoryModal.value = true
}

const saveCategory = () => {
  if (!categoryForm.name) return
  
  if (editingCategory.value) {
    const index = categories.value.findIndex(c => c.id === editingCategory.value.id)
    if (index !== -1) {
      categories.value[index] = { ...categories.value[index], ...categoryForm }
    }
    toast.success('Muvaffaqiyat', 'Kategoriya yangilandi')
  } else {
    categories.value.push({
      id: Date.now(),
      ...categoryForm
    })
    toast.success('Muvaffaqiyat', 'Yangi kategoriya qo\'shildi')
  }
  showCategoryModal.value = false
}

const deleteCategory = (category) => {
  const faqCount = getCategoryFaqCount(category.id)
  if (faqCount > 0) {
    toast.warning('Diqqat', `Bu kategoriyada ${faqCount} ta savol bor. Avval savollarni o'chiring.`)
    return
  }
  if (confirm(`"${category.name}" kategoriyasini o'chirishni xohlaysizmi?`)) {
    categories.value = categories.value.filter(c => c.id !== category.id)
    toast.success('O\'chirildi', 'Kategoriya o\'chirildi')
  }
}

// Contact functions
const addContactField = (field) => {
  contactInfo[field].push('')
}

const removeContactField = (field, index) => {
  contactInfo[field].splice(index, 1)
}

const saveContactInfo = async () => {
  isSaving.value = true
  try {
    await api.updateContactInfo({
      phones: contactInfo.phones,
      emails: contactInfo.emails,
      telegram: contactInfo.telegram,
      instagram: contactInfo.instagram,
      facebook: contactInfo.facebook,
      youtube: contactInfo.youtube,
      address: contactInfo.address,
      working_hours: contactInfo.working_hours
    })
    toast.success('Muvaffaqiyat', 'Kontakt ma\'lumotlari saqlandi')
  } catch (error) {
    toast.error('Xatolik', error.message || 'Saqlashda xatolik yuz berdi')
  } finally {
    isSaving.value = false
  }
}

// Message functions
const openMessageModal = (msg) => {
  selectedMessage.value = msg
  replyMessage.value = ''
  showMessageModal.value = true
}

const updateMessageStatus = () => {
  toast.info('Yangilandi', 'Status yangilandi')
}

const sendReply = async () => {
  if (!replyMessage.value) return
  
  isSaving.value = true
  try {
    // API call to send reply
    await api.replySupportMessage(selectedMessage.value.id, replyMessage.value)
    selectedMessage.value.status = 'resolved'
    toast.success('Yuborildi', 'Javob yuborildi')
    showMessageModal.value = false
  } catch (error) {
    toast.error('Xatolik', error.message || 'Yuborishda xatolik')
  } finally {
    isSaving.value = false
  }
}

// Load data
const loadData = async () => {
  try {
    // Load FAQs from API
    const faqsRes = await api.getFaqs()
    if (Array.isArray(faqsRes)) {
      faqs.value = faqsRes.map(f => ({
        id: f.id,
        category_id: f.category_id || 1,
        question: f.question,
        answer: f.answer,
        is_active: f.is_active !== false,
        order: f.order || 1
      }))
    } else if (faqsRes?.data) {
      faqs.value = faqsRes.data.map(f => ({
        id: f.id,
        category_id: f.category_id || 1,
        question: f.question,
        answer: f.answer,
        is_active: f.is_active !== false,
        order: f.order || 1
      }))
    }

    // Load contact info
    try {
      const contactRes = await api.getContactInfo()
      if (contactRes) {
        contactInfo.phones = contactRes.phones || []
        contactInfo.emails = contactRes.emails || []
        contactInfo.telegram = contactRes.telegram || ''
        contactInfo.instagram = contactRes.instagram || ''
        contactInfo.facebook = contactRes.facebook || ''
        contactInfo.youtube = contactRes.youtube || ''
        contactInfo.address = contactRes.address || ''
        contactInfo.working_hours = contactRes.working_hours || ''
      }
    } catch (e) {
      console.log('Contact info not available')
    }

    // Load support messages
    try {
      const messagesRes = await api.getSupportMessages()
      if (Array.isArray(messagesRes)) {
        messages.value = messagesRes
      } else if (messagesRes?.data) {
        messages.value = messagesRes.data
      }
    } catch (e) {
      console.log('Support messages not available')
    }

    // Set default categories if none exist
    if (categories.value.length === 0) {
      categories.value = [
        { id: 1, name: 'Umumiy', icon: 'HelpCircle' },
        { id: 2, name: 'Davomat', icon: 'ClipboardCheck' },
        { id: 3, name: 'To\'lov', icon: 'CreditCard' },
        { id: 4, name: 'Dars jadvali', icon: 'Calendar' },
        { id: 5, name: 'Texnik yordam', icon: 'Settings' }
      ]
    }
  } catch (error) {
    console.error('Error loading data:', error)
    toast.error('Xatolik', 'Ma\'lumotlar yuklanmadi')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
