<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 md:text-3xl">🍽️ Oshxona menyusi</h1>
        <p class="text-slate-500">Bugun nimani tanovul qilmoqchisiz?</p>
      </div>
      
      <div class="flex items-center gap-3">
        <!-- Cart -->
        <button 
          @click="showCart = true" 
          class="relative flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-white hover:bg-emerald-600 transition-all"
        >
          <ShoppingCart :size="20" />
          <span>Savatcha</span>
          <span 
            v-if="cartItemsCount > 0" 
            class="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-xs font-bold"
          >
            {{ cartItemsCount }}
          </span>
        </button>
      </div>
    </div>

    <!-- Categories -->
    <div class="flex gap-3 overflow-x-auto pb-2">
      <button
        @click="selectedCategory = null"
        class="flex-shrink-0 flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all"
        :class="selectedCategory === null 
          ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30' 
          : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'"
      >
        <Utensils :size="18" />
        Barchasi
      </button>
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="selectedCategory = cat.id"
        class="flex-shrink-0 flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all"
        :class="selectedCategory === cat.id 
          ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30' 
          : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'"
      >
        <component :is="getCategoryIcon(cat.icon)" :size="18" />
        {{ cat.name }}
      </button>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Taomlarni qidirish..."
        class="w-full rounded-xl border border-slate-200 bg-white py-3 pl-12 pr-4 text-slate-700 placeholder-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Loader2 :size="32" class="animate-spin text-emerald-500" />
    </div>

    <!-- Menu Items -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="group rounded-2xl border border-slate-200 bg-white p-4 transition-all hover:shadow-lg hover:border-emerald-200"
      >
        <!-- Image -->
        <div class="relative mb-4 aspect-square overflow-hidden rounded-xl bg-slate-100">
          <img 
            v-if="item.image_url" 
            :src="item.image_url" 
            :alt="item.name"
            class="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
          <div v-else class="flex h-full items-center justify-center">
            <UtensilsCrossed :size="48" class="text-slate-300" />
          </div>
          
          <!-- Badges -->
          <div class="absolute top-2 left-2 flex flex-col gap-1">
            <span v-if="item.is_vegetarian" class="rounded-lg bg-green-500 px-2 py-1 text-xs font-medium text-white">
              🥬 Vegetarian
            </span>
            <span v-if="!item.is_available" class="rounded-lg bg-red-500 px-2 py-1 text-xs font-medium text-white">
              Mavjud emas
            </span>
          </div>
        </div>

        <!-- Info -->
        <div class="space-y-2">
          <h3 class="font-semibold text-slate-800 line-clamp-1">{{ item.name }}</h3>
          <p v-if="item.description" class="text-sm text-slate-500 line-clamp-2">{{ item.description }}</p>
          
          <div class="flex items-center justify-between">
            <div>
              <span class="text-lg font-bold text-emerald-600">{{ formatPrice(item.price) }}</span>
              <span class="text-sm text-slate-400"> so'm</span>
            </div>
            
            <div v-if="item.calories" class="flex items-center gap-1 text-xs text-slate-400">
              <Flame :size="14" />
              {{ item.calories }} kkal
            </div>
          </div>
          
          <!-- Preparation time -->
          <div v-if="item.preparation_time" class="flex items-center gap-1 text-xs text-slate-400">
            <Clock :size="14" />
            {{ item.preparation_time }} daqiqa
          </div>
        </div>

        <!-- Add to cart -->
        <button
          @click="addToCart(item)"
          :disabled="!item.is_available"
          class="mt-4 w-full flex items-center justify-center gap-2 rounded-xl py-3 font-medium transition-all"
          :class="item.is_available 
            ? 'bg-emerald-500 text-white hover:bg-emerald-600' 
            : 'bg-slate-100 text-slate-400 cursor-not-allowed'"
        >
          <Plus :size="18" />
          Savatchaga qo'shish
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && filteredItems.length === 0" class="text-center py-12">
      <UtensilsCrossed :size="48" class="mx-auto text-slate-300 mb-4" />
      <p class="text-slate-500">Hech narsa topilmadi</p>
    </div>

    <!-- Cart Modal -->
    <Teleport to="body">
      <div
        v-if="showCart"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="showCart = false"
      >
        <div class="w-full max-w-lg max-h-[90vh] rounded-t-3xl sm:rounded-2xl bg-white overflow-hidden flex flex-col">
          <!-- Header -->
          <div class="flex items-center justify-between border-b border-slate-200 p-4">
            <div>
              <h2 class="text-lg font-bold text-slate-800">Savatcha</h2>
              <p class="text-sm text-slate-500">{{ cartItemsCount }} ta mahsulot</p>
            </div>
            <button @click="showCart = false" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
              <X :size="20" />
            </button>
          </div>

          <!-- Cart Items -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div v-if="cart.length === 0" class="text-center py-8">
              <ShoppingCart :size="48" class="mx-auto text-slate-300 mb-4" />
              <p class="text-slate-500">Savatcha bo'sh</p>
            </div>

            <div
              v-for="item in cart"
              :key="item.id"
              class="flex items-center gap-4 rounded-xl border border-slate-200 p-3"
            >
              <div class="h-16 w-16 flex-shrink-0 rounded-lg bg-slate-100 overflow-hidden">
                <img 
                  v-if="item.image_url" 
                  :src="item.image_url" 
                  :alt="item.name"
                  class="h-full w-full object-cover"
                />
                <div v-else class="flex h-full items-center justify-center">
                  <Utensils :size="24" class="text-slate-300" />
                </div>
              </div>

              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-slate-800 truncate">{{ item.name }}</h4>
                <p class="text-sm text-emerald-600 font-semibold">{{ formatPrice(item.price) }} so'm</p>
              </div>

              <div class="flex items-center gap-2">
                <button
                  @click="updateQuantity(item.id, item.quantity - 1)"
                  class="h-8 w-8 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 flex items-center justify-center"
                >
                  <Minus :size="16" />
                </button>
                <span class="w-8 text-center font-medium">{{ item.quantity }}</span>
                <button
                  @click="updateQuantity(item.id, item.quantity + 1)"
                  class="h-8 w-8 rounded-lg bg-emerald-100 text-emerald-600 hover:bg-emerald-200 flex items-center justify-center"
                >
                  <Plus :size="16" />
                </button>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div class="px-4 pb-4" v-if="cart.length > 0">
            <textarea
              v-model="orderNotes"
              placeholder="Izoh qo'shish (ixtiyoriy)..."
              class="w-full rounded-xl border border-slate-200 p-3 text-sm resize-none focus:border-emerald-500 focus:outline-none"
              rows="2"
            ></textarea>
          </div>

          <!-- Footer -->
          <div class="border-t border-slate-200 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-slate-600">Jami summa:</span>
              <span class="text-xl font-bold text-slate-800">{{ formatPrice(cartTotal) }} so'm</span>
            </div>
            
            <button
              @click="submitOrder"
              :disabled="cart.length === 0 || submitting"
              class="w-full flex items-center justify-center gap-2 rounded-xl bg-emerald-500 py-3.5 font-semibold text-white hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Loader2 v-if="submitting" :size="20" class="animate-spin" />
              <ShoppingBag v-else :size="20" />
              {{ submitting ? 'Buyurtma berilmoqda...' : 'Buyurtma berish' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- My Orders Modal -->
    <Teleport to="body">
      <div
        v-if="showOrders"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="showOrders = false"
      >
        <div class="w-full max-w-2xl max-h-[90vh] rounded-2xl bg-white overflow-hidden flex flex-col">
          <div class="flex items-center justify-between border-b border-slate-200 p-4">
            <h2 class="text-lg font-bold text-slate-800">Mening buyurtmalarim</h2>
            <button @click="showOrders = false" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100">
              <X :size="20" />
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <div v-if="ordersLoading" class="flex items-center justify-center py-12">
              <Loader2 :size="32" class="animate-spin text-emerald-500" />
            </div>
            
            <div v-else-if="myOrders.length === 0" class="text-center py-12">
              <Package :size="48" class="mx-auto text-slate-300 mb-4" />
              <p class="text-slate-500">Buyurtmalar yo'q</p>
            </div>

            <div
              v-else
              v-for="order in myOrders"
              :key="order.id"
              class="rounded-xl border border-slate-200 p-4"
            >
              <div class="flex items-center justify-between mb-3">
                <div>
                  <span class="text-lg font-bold text-slate-800">{{ order.order_number }}</span>
                  <p class="text-sm text-slate-500">{{ formatDateTime(order.created_at) }}</p>
                </div>
                <span 
                  class="rounded-lg px-3 py-1 text-sm font-medium"
                  :class="getStatusClass(order.status)"
                >
                  {{ getStatusText(order.status) }}
                </span>
              </div>
              
              <div class="space-y-2 mb-3">
                <div v-for="item in order.items" :key="item.id" class="flex justify-between text-sm">
                  <span class="text-slate-600">{{ item.item_name }} x{{ item.quantity }}</span>
                  <span class="text-slate-800">{{ formatPrice(item.total_price) }} so'm</span>
                </div>
              </div>
              
              <div class="flex justify-between items-center pt-3 border-t border-slate-100">
                <span class="text-slate-600">Jami:</span>
                <span class="font-bold text-emerald-600">{{ formatPrice(order.total_amount) }} so'm</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- My Orders Button (Fixed) -->
    <button
      @click="openMyOrders"
      class="fixed bottom-6 left-6 flex items-center gap-2 rounded-full bg-slate-800 px-4 py-3 text-white shadow-lg hover:bg-slate-700 transition-all"
    >
      <Package :size="20" />
      <span>Buyurtmalarim</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api'
import {
  ShoppingCart, ShoppingBag, Search, Plus, Minus, X,
  Utensils, UtensilsCrossed, Coffee, Pizza, Salad,
  Sandwich, Soup, Beef, Fish, Cake, Cookie,
  Clock, Flame, Package, Loader2, ChefHat
} from 'lucide-vue-next'

const toast = useToastStore()

// State
const loading = ref(true)
const categories = ref([])
const menuItems = ref([])
const selectedCategory = ref(null)
const searchQuery = ref('')
const showCart = ref(false)
const showOrders = ref(false)
const cart = ref([])
const orderNotes = ref('')
const submitting = ref(false)
const myOrders = ref([])
const ordersLoading = ref(false)

// Icon mapping
const iconMap = {
  Utensils: Utensils,
  Coffee: Coffee,
  Pizza: Pizza,
  Salad: Salad,
  Sandwich: Sandwich,
  Soup: Soup,
  Beef: Beef,
  Fish: Fish,
  Cake: Cake,
  Cookie: Cookie,
  ChefHat: ChefHat
}

function getCategoryIcon(iconName) {
  return iconMap[iconName] || Utensils
}

// Computed
const filteredItems = computed(() => {
  let items = menuItems.value
  
  if (selectedCategory.value) {
    items = items.filter(item => item.category_id === selectedCategory.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    items = items.filter(item => 
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }
  
  return items
})

const cartItemsCount = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.quantity, 0)
})

const cartTotal = computed(() => {
  return cart.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

// Methods
async function loadData() {
  loading.value = true
  try {
    const [categoriesRes, menuRes] = await Promise.all([
      api.getCanteenCategories(),
      api.getCanteenMenu({ is_available: true })
    ])
    
    categories.value = categoriesRes.items || []
    menuItems.value = menuRes.items || []
  } catch (error) {
    console.error('Error loading canteen data:', error)
    toast.error('Ma\'lumotlarni yuklashda xatolik')
  } finally {
    loading.value = false
  }
}

function addToCart(item) {
  const existing = cart.value.find(i => i.id === item.id)
  if (existing) {
    existing.quantity++
  } else {
    cart.value.push({
      id: item.id,
      name: item.name,
      price: parseFloat(item.price),
      image_url: item.image_url,
      quantity: 1
    })
  }
  toast.success(`"${item.name}" savatchaga qo'shildi`)
}

function updateQuantity(itemId, quantity) {
  if (quantity <= 0) {
    cart.value = cart.value.filter(i => i.id !== itemId)
  } else {
    const item = cart.value.find(i => i.id === itemId)
    if (item) {
      item.quantity = quantity
    }
  }
}

async function submitOrder() {
  if (cart.value.length === 0) return
  
  submitting.value = true
  try {
    const orderData = {
      items: cart.value.map(item => ({
        menu_item_id: item.id,
        quantity: item.quantity
      })),
      notes: orderNotes.value || null
    }
    
    const response = await api.createCanteenOrder(orderData)
    
    toast.success(`Buyurtma ${response.order_number} muvaffaqiyatli berildi!`)
    
    // Clear cart
    cart.value = []
    orderNotes.value = ''
    showCart.value = false
  } catch (error) {
    console.error('Order error:', error)
    toast.error(error.message || 'Buyurtma berishda xatolik')
  } finally {
    submitting.value = false
  }
}

async function openMyOrders() {
  showOrders.value = true
  ordersLoading.value = true
  
  try {
    const response = await api.getMyCanteenOrders({ page_size: 20 })
    myOrders.value = response.items || []
  } catch (error) {
    console.error('Error loading orders:', error)
    toast.error('Buyurtmalarni yuklashda xatolik')
  } finally {
    ordersLoading.value = false
  }
}

function formatPrice(price) {
  return new Intl.NumberFormat('uz-UZ').format(price)
}

function formatDateTime(dateStr) {
  return new Date(dateStr).toLocaleString('uz-UZ', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getStatusClass(status) {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-700',
    preparing: 'bg-blue-100 text-blue-700',
    ready: 'bg-emerald-100 text-emerald-700',
    completed: 'bg-slate-100 text-slate-700',
    cancelled: 'bg-red-100 text-red-700'
  }
  return classes[status] || 'bg-slate-100 text-slate-700'
}

function getStatusText(status) {
  const texts = {
    pending: 'Kutilmoqda',
    preparing: 'Tayyorlanmoqda',
    ready: 'Tayyor',
    completed: 'Bajarildi',
    cancelled: 'Bekor qilindi'
  }
  return texts[status] || status
}

// Initialize
onMounted(() => {
  loadData()
})
</script>
