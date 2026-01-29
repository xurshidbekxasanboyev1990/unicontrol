<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 rounded-2xl p-4 sm:p-6 text-white">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold">Asosiy Sahifa Sozlamalari</h1>
          <p class="text-emerald-100 mt-1 text-sm sm:text-base">Landing page kontentini boshqarish</p>
        </div>
        <div class="hidden sm:flex w-14 h-14 bg-white/20 backdrop-blur rounded-2xl items-center justify-center">
          <Globe class="w-7 h-7" />
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

      <!-- Tab Content -->
      <div class="p-4 sm:p-6">
        <!-- Cards Tab -->
        <div v-if="activeTab === 'cards'" class="space-y-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">Landing Kartalar</h3>
            <button
              @click="openCardModal()"
              class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
            >
              <Plus class="w-4 h-4" />
              Yangi karta
            </button>
          </div>

          <!-- Cards Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="card in landingCards"
              :key="card.id"
              class="bg-slate-50 rounded-xl p-4 border border-slate-200 hover:border-emerald-300 transition-colors group"
            >
              <div class="flex items-start justify-between mb-3">
                <div :class="[
                  'w-10 h-10 rounded-lg flex items-center justify-center',
                  card.iconBg || 'bg-emerald-100'
                ]">
                  <component :is="getIcon(card.icon)" :class="['w-5 h-5', card.iconColor || 'text-emerald-600']" />
                </div>
                <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    @click="openCardModal(card)"
                    class="p-1.5 text-slate-400 hover:text-emerald-500 hover:bg-white rounded-lg transition-colors"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteCard(card.id)"
                    class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-white rounded-lg transition-colors"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <h4 class="font-semibold text-slate-800 mb-1">{{ card.title }}</h4>
              <p class="text-sm text-slate-500 line-clamp-2">{{ card.description }}</p>
              <div class="mt-3 flex items-center gap-2">
                <span class="text-xs px-2 py-1 bg-slate-200 text-slate-600 rounded-full">{{ card.section }}</span>
                <span v-if="card.active" class="text-xs px-2 py-1 bg-emerald-100 text-emerald-600 rounded-full">Faol</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Social Links Tab -->
        <div v-if="activeTab === 'social'" class="space-y-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">Ijtimoiy Tarmoqlar</h3>
            <button
              @click="saveSocialLinks"
              class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
            >
              <Save class="w-4 h-4" />
              Saqlash
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="social in socialLinks" :key="social.id" class="space-y-2">
              <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
                <component :is="getIcon(social.icon)" class="w-4 h-4" />
                {{ social.name }}
              </label>
              <input
                v-model="social.url"
                type="url"
                :placeholder="social.placeholder"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 transition-all"
              />
            </div>
          </div>
        </div>

        <!-- Team Tab -->
        <div v-if="activeTab === 'team'" class="space-y-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">Loyiha Jamoasi</h3>
            <button
              @click="openTeamModal()"
              class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
            >
              <UserPlus class="w-4 h-4" />
              A'zo qo'shish
            </button>
          </div>

          <!-- Team Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="member in teamMembers"
              :key="member.id"
              class="bg-slate-50 rounded-xl p-4 border border-slate-200 hover:border-emerald-300 transition-colors group"
            >
              <div class="flex items-start gap-3">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-bold text-lg">
                  {{ member.name.charAt(0) }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div>
                      <h4 class="font-semibold text-slate-800">{{ member.name }}</h4>
                      <p class="text-sm text-slate-500">{{ member.position }}</p>
                    </div>
                    <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        @click="openTeamModal(member)"
                        class="p-1.5 text-slate-400 hover:text-emerald-500 hover:bg-white rounded-lg transition-colors"
                      >
                        <Pencil class="w-4 h-4" />
                      </button>
                      <button
                        @click="deleteTeamMember(member.id)"
                        class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-white rounded-lg transition-colors"
                      >
                        <Trash2 class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="mt-3 flex flex-wrap gap-2">
                <span :class="[
                  'text-xs px-2 py-1 rounded-full',
                  getRoleColor(member.type)
                ]">
                  {{ getRoleLabel(member.type) }}
                </span>
              </div>
              <div v-if="member.social" class="mt-3 flex gap-2">
                <a v-if="member.social.github" :href="member.social.github" target="_blank" class="text-slate-400 hover:text-slate-600">
                  <Github class="w-4 h-4" />
                </a>
                <a v-if="member.social.linkedin" :href="member.social.linkedin" target="_blank" class="text-slate-400 hover:text-blue-600">
                  <Linkedin class="w-4 h-4" />
                </a>
                <a v-if="member.social.telegram" :href="member.social.telegram" target="_blank" class="text-slate-400 hover:text-sky-500">
                  <Send class="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Permissions Tab -->
        <div v-if="activeTab === 'permissions'" class="space-y-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">Admin Ruxsatlari</h3>
            <p class="text-sm text-slate-500">Yangi admin qo'shishda ruxsatlarni belgilang</p>
          </div>

          <!-- Permission Groups -->
          <div class="space-y-4">
            <div
              v-for="group in permissionGroups"
              :key="group.id"
              class="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden"
            >
              <div class="px-4 py-3 bg-slate-100 border-b border-slate-200 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <component :is="getIcon(group.icon)" class="w-5 h-5 text-slate-600" />
                  <h4 class="font-semibold text-slate-800">{{ group.name }}</h4>
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <span class="text-sm text-slate-500">Barchasi</span>
                  <input
                    type="checkbox"
                    :checked="isAllChecked(group.permissions)"
                    @change="toggleAll(group.permissions, $event)"
                    class="w-5 h-5 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500"
                  />
                </label>
              </div>
              <div class="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <label
                  v-for="perm in group.permissions"
                  :key="perm.id"
                  class="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-100 hover:border-emerald-200 cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox"
                    v-model="perm.enabled"
                    class="w-5 h-5 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500"
                  />
                  <div>
                    <p class="text-sm font-medium text-slate-700">{{ perm.label }}</p>
                    <p class="text-xs text-slate-400">{{ perm.description }}</p>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="flex justify-end">
            <button
              @click="savePermissions"
              class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
            >
              <Save class="w-5 h-5" />
              Ruxsatlarni saqlash
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Card Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCardModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showCardModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
            <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 class="text-lg font-semibold text-slate-800">
                {{ editingCard ? 'Kartani tahrirlash' : 'Yangi karta' }}
              </h3>
              <button @click="showCardModal = false" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg">
                <X class="w-5 h-5" />
              </button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Sarlavha</label>
                <input
                  v-model="cardForm.title"
                  type="text"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10"
                  placeholder="Karta sarlavhasi"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Tavsif</label>
                <textarea
                  v-model="cardForm.description"
                  rows="3"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10 resize-none"
                  placeholder="Karta tavsifi"
                ></textarea>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Bo'lim</label>
                  <select
                    v-model="cardForm.section"
                    class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300"
                  >
                    <option value="features">Xususiyatlar</option>
                    <option value="how-it-works">Qanday ishlaydi</option>
                    <option value="testimonials">Fikrlar</option>
                    <option value="faq">FAQ</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">Ikon</label>
                  <select
                    v-model="cardForm.icon"
                    class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300"
                  >
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
                <input
                  type="checkbox"
                  v-model="cardForm.active"
                  id="cardActive"
                  class="w-5 h-5 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500"
                />
                <label for="cardActive" class="text-sm text-slate-700">Faol holat</label>
              </div>
            </div>
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
              <button
                @click="showCardModal = false"
                class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl text-sm font-medium transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="saveCard"
                class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-sm font-medium transition-colors"
              >
                {{ editingCard ? 'Saqlash' : 'Qo\'shish' }}
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
              <h3 class="text-lg font-semibold text-slate-800">
                {{ editingMember ? 'A\'zoni tahrirlash' : 'Yangi a\'zo' }}
              </h3>
              <button @click="showTeamModal = false" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg">
                <X class="w-5 h-5" />
              </button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Ism Familiya</label>
                <input
                  v-model="teamForm.name"
                  type="text"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10"
                  placeholder="To'liq ism"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Lavozim</label>
                <input
                  v-model="teamForm.position"
                  type="text"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300 focus:ring-4 focus:ring-emerald-500/10"
                  placeholder="Masalan: Senior Developer"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Turi</label>
                <select
                  v-model="teamForm.type"
                  class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-emerald-300"
                >
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
                  <Github class="w-4 h-4 text-slate-400" />
                  <input
                    v-model="teamForm.social.github"
                    type="url"
                    class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-emerald-300"
                    placeholder="GitHub URL"
                  />
                </div>
                <div class="flex items-center gap-2">
                  <Linkedin class="w-4 h-4 text-slate-400" />
                  <input
                    v-model="teamForm.social.linkedin"
                    type="url"
                    class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-emerald-300"
                    placeholder="LinkedIn URL"
                  />
                </div>
                <div class="flex items-center gap-2">
                  <Send class="w-4 h-4 text-slate-400" />
                  <input
                    v-model="teamForm.social.telegram"
                    type="url"
                    class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-emerald-300"
                    placeholder="Telegram URL"
                  />
                </div>
              </div>
            </div>
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
              <button
                @click="showTeamModal = false"
                class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl text-sm font-medium transition-colors"
              >
                Bekor qilish
              </button>
              <button
                @click="saveTeamMember"
                class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-sm font-medium transition-colors"
              >
                {{ editingMember ? 'Saqlash' : 'Qo\'shish' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, markRaw } from 'vue'
import {
  Globe, LayoutGrid, Share2, Users, ShieldCheck, Plus, Pencil, Trash2, Save,
  X, UserPlus, Github, Linkedin, Send, Zap, Calendar, BarChart3, Brain, Shield,
  Bell, BookOpen
} from 'lucide-vue-next'

// Tabs
const tabs = [
  { id: 'cards', label: 'Kartalar', icon: markRaw(LayoutGrid) },
  { id: 'social', label: 'Ijtimoiy tarmoqlar', icon: markRaw(Share2) },
  { id: 'team', label: 'Jamoa', icon: markRaw(Users) },
  { id: 'permissions', label: 'Ruxsatlar', icon: markRaw(ShieldCheck) }
]

const activeTab = ref('cards')

// Icons map
const iconComponents = {
  Zap: markRaw(Zap),
  Users: markRaw(Users),
  Calendar: markRaw(Calendar),
  BarChart3: markRaw(BarChart3),
  Brain: markRaw(Brain),
  Shield: markRaw(Shield),
  Bell: markRaw(Bell),
  BookOpen: markRaw(BookOpen),
  Github: markRaw(Github),
  Linkedin: markRaw(Linkedin),
  Send: markRaw(Send),
  Globe: markRaw(Globe),
  LayoutGrid: markRaw(LayoutGrid),
  Share2: markRaw(Share2),
  ShieldCheck: markRaw(ShieldCheck)
}

const getIcon = (name) => iconComponents[name] || iconComponents.Zap

// Landing Cards
const landingCards = ref([
  { id: 1, title: 'Tezkor ishlash', description: 'Barcha ma\'lumotlarga bir joydan kirishingiz mumkin', icon: 'Zap', iconBg: 'bg-amber-100', iconColor: 'text-amber-600', section: 'features', active: true },
  { id: 2, title: 'Dars jadvali', description: 'Real vaqtda yangilanuvchi interaktiv jadval', icon: 'Calendar', iconBg: 'bg-blue-100', iconColor: 'text-blue-600', section: 'features', active: true },
  { id: 3, title: 'AI Tahlil', description: 'Sun\'iy intellekt yordamida o\'qishingizni tahlil qiling', icon: 'Brain', iconBg: 'bg-violet-100', iconColor: 'text-violet-600', section: 'features', active: true },
  { id: 4, title: 'Ro\'yxatdan o\'ting', description: 'Tizimga kirish uchun birinchi qadam', icon: 'Users', iconBg: 'bg-emerald-100', iconColor: 'text-emerald-600', section: 'how-it-works', active: true },
  { id: 5, title: 'Ma\'lumotlar xavfsiz', description: 'Barcha ma\'lumotlar shifrlangan holda saqlanadi', icon: 'Shield', iconBg: 'bg-rose-100', iconColor: 'text-rose-600', section: 'faq', active: true }
])

// Card Modal
const showCardModal = ref(false)
const editingCard = ref(null)
const cardForm = reactive({
  title: '',
  description: '',
  section: 'features',
  icon: 'Zap',
  active: true
})

const openCardModal = (card = null) => {
  if (card) {
    editingCard.value = card
    cardForm.title = card.title
    cardForm.description = card.description
    cardForm.section = card.section
    cardForm.icon = card.icon
    cardForm.active = card.active
  } else {
    editingCard.value = null
    cardForm.title = ''
    cardForm.description = ''
    cardForm.section = 'features'
    cardForm.icon = 'Zap'
    cardForm.active = true
  }
  showCardModal.value = true
}

const saveCard = () => {
  if (editingCard.value) {
    const idx = landingCards.value.findIndex(c => c.id === editingCard.value.id)
    if (idx > -1) {
      landingCards.value[idx] = { ...landingCards.value[idx], ...cardForm }
    }
  } else {
    landingCards.value.push({
      id: Date.now(),
      ...cardForm,
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600'
    })
  }
  showCardModal.value = false
}

const deleteCard = (id) => {
  if (confirm('Kartani o\'chirmoqchimisiz?')) {
    landingCards.value = landingCards.value.filter(c => c.id !== id)
  }
}

// Social Links
const socialLinks = ref([
  { id: 1, name: 'Telegram', icon: 'Send', url: 'https://t.me/unicontrol', placeholder: 'https://t.me/username' },
  { id: 2, name: 'Instagram', icon: 'Globe', url: '', placeholder: 'https://instagram.com/username' },
  { id: 3, name: 'YouTube', icon: 'Globe', url: '', placeholder: 'https://youtube.com/@channel' },
  { id: 4, name: 'GitHub', icon: 'Github', url: 'https://github.com/unicontrol', placeholder: 'https://github.com/username' },
  { id: 5, name: 'LinkedIn', icon: 'Linkedin', url: '', placeholder: 'https://linkedin.com/company/name' },
  { id: 6, name: 'Website', icon: 'Globe', url: '', placeholder: 'https://example.com' }
])

const saveSocialLinks = () => {
  alert('Ijtimoiy tarmoq linklari saqlandi!')
}

// Team Members
const teamMembers = ref([
  { id: 1, name: 'Xurshidbek Xasanboyev', position: 'Full Stack Developer', type: 'fullstack', social: { github: 'https://github.com', telegram: 'https://t.me' } },
  { id: 2, name: 'Sardor Aliyev', position: 'Backend Developer', type: 'backend', social: { github: 'https://github.com' } },
  { id: 3, name: 'Malika Karimova', position: 'UI/UX Designer', type: 'designer', social: { linkedin: 'https://linkedin.com' } }
])

const showTeamModal = ref(false)
const editingMember = ref(null)
const teamForm = reactive({
  name: '',
  position: '',
  type: 'fullstack',
  social: {
    github: '',
    linkedin: '',
    telegram: ''
  }
})

const openTeamModal = (member = null) => {
  if (member) {
    editingMember.value = member
    teamForm.name = member.name
    teamForm.position = member.position
    teamForm.type = member.type
    teamForm.social = { ...member.social }
  } else {
    editingMember.value = null
    teamForm.name = ''
    teamForm.position = ''
    teamForm.type = 'fullstack'
    teamForm.social = { github: '', linkedin: '', telegram: '' }
  }
  showTeamModal.value = true
}

const saveTeamMember = () => {
  if (editingMember.value) {
    const idx = teamMembers.value.findIndex(m => m.id === editingMember.value.id)
    if (idx > -1) {
      teamMembers.value[idx] = { ...teamMembers.value[idx], ...teamForm }
    }
  } else {
    teamMembers.value.push({
      id: Date.now(),
      ...teamForm,
      social: { ...teamForm.social }
    })
  }
  showTeamModal.value = false
}

const deleteTeamMember = (id) => {
  if (confirm('A\'zoni o\'chirmoqchimisiz?')) {
    teamMembers.value = teamMembers.value.filter(m => m.id !== id)
  }
}

const getRoleColor = (type) => {
  const colors = {
    backend: 'bg-blue-100 text-blue-600',
    frontend: 'bg-amber-100 text-amber-600',
    mobile: 'bg-violet-100 text-violet-600',
    fullstack: 'bg-emerald-100 text-emerald-600',
    designer: 'bg-pink-100 text-pink-600',
    devops: 'bg-orange-100 text-orange-600',
    pm: 'bg-cyan-100 text-cyan-600',
    qa: 'bg-red-100 text-red-600'
  }
  return colors[type] || 'bg-slate-100 text-slate-600'
}

const getRoleLabel = (type) => {
  const labels = {
    backend: 'Backend',
    frontend: 'Frontend',
    mobile: 'Mobile',
    fullstack: 'Full Stack',
    designer: 'UI/UX',
    devops: 'DevOps',
    pm: 'PM',
    qa: 'QA'
  }
  return labels[type] || type
}

// Permissions
const permissionGroups = ref([
  {
    id: 'students',
    name: 'Talabalar boshqaruvi',
    icon: 'Users',
    permissions: [
      { id: 'students_view', label: 'Ko\'rish', description: 'Talabalar ro\'yxatini ko\'rish', enabled: true },
      { id: 'students_create', label: 'Qo\'shish', description: 'Yangi talaba qo\'shish', enabled: true },
      { id: 'students_edit', label: 'Tahrirlash', description: 'Talaba ma\'lumotlarini o\'zgartirish', enabled: true },
      { id: 'students_delete', label: 'O\'chirish', description: 'Talabani o\'chirish', enabled: false }
    ]
  },
  {
    id: 'groups',
    name: 'Guruhlar boshqaruvi',
    icon: 'LayoutGrid',
    permissions: [
      { id: 'groups_view', label: 'Ko\'rish', description: 'Guruhlar ro\'yxatini ko\'rish', enabled: true },
      { id: 'groups_create', label: 'Qo\'shish', description: 'Yangi guruh yaratish', enabled: true },
      { id: 'groups_edit', label: 'Tahrirlash', description: 'Guruh ma\'lumotlarini o\'zgartirish', enabled: false },
      { id: 'groups_delete', label: 'O\'chirish', description: 'Guruhni o\'chirish', enabled: false }
    ]
  },
  {
    id: 'reports',
    name: 'Hisobotlar',
    icon: 'BarChart3',
    permissions: [
      { id: 'reports_view', label: 'Ko\'rish', description: 'Hisobotlarni ko\'rish', enabled: true },
      { id: 'reports_create', label: 'Yaratish', description: 'Yangi hisobot yaratish', enabled: true },
      { id: 'reports_export', label: 'Eksport', description: 'Hisobotlarni yuklab olish', enabled: true }
    ]
  },
  {
    id: 'settings',
    name: 'Tizim sozlamalari',
    icon: 'ShieldCheck',
    permissions: [
      { id: 'settings_view', label: 'Ko\'rish', description: 'Sozlamalarni ko\'rish', enabled: false },
      { id: 'settings_edit', label: 'O\'zgartirish', description: 'Sozlamalarni o\'zgartirish', enabled: false },
      { id: 'landing_edit', label: 'Landing sahifa', description: 'Asosiy sahifani boshqarish', enabled: false }
    ]
  }
])

const isAllChecked = (permissions) => {
  return permissions.every(p => p.enabled)
}

const toggleAll = (permissions, event) => {
  const checked = event.target.checked
  permissions.forEach(p => p.enabled = checked)
}

const savePermissions = () => {
  alert('Admin ruxsatlari saqlandi!')
}
</script>

<style scoped>
/* Modal Animation */
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

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
