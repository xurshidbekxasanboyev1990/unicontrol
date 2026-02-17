<template>
  <div class="canteen-coming-soon">
    <div class="canteen-hero">
      <div class="canteen-icon">🍽️</div>
      <h1>Oshxona</h1>
      <p class="subtitle">Tez orada! Yangi oshxona sahifasi tayyorlanmoqda.</p>
    </div>
    <div class="canteen-info">
      <p>
        Bu sahifa orqali siz maktab oshxonasidagi menyu, narxlar va buyurtmalar haqida ma'lumot olishingiz mumkin bo'ladi.
      </p>
      <ul>
        <li>Haftalik va kunlik menyu</li>
        <li>Ovqatlar tarkibi va allergenlar</li>
        <li>Onlayn buyurtma va to'lov</li>
        <li>Ota-onalar uchun nazorat</li>
      </ul>
      <div class="soon-badge">Tez kunda!</div>
    </div>
  </div>
</template>

<script setup>
// Hozircha faqat placeholder
</script>

<style scoped>
.canteen-coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: 32px 12px;
  background: #f8fafc;
}
.canteen-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}
.canteen-icon {
  font-size: 80px;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 16px #e0e7ef);
}
.canteen-hero h1 {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}
.subtitle {
  color: #64748b;
  font-size: 1.1rem;
  margin-bottom: 0;
}
.canteen-info {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 2px 16px #e0e7ef44;
  padding: 28px 24px;
  max-width: 420px;
  text-align: left;
}
.canteen-info p {
  color: #334155;
  font-size: 1.05rem;
  margin-bottom: 18px;
}
.canteen-info ul {
  color: #475569;
  margin-bottom: 18px;
  padding-left: 20px;
}
.canteen-info li {
  margin-bottom: 6px;
  font-size: 1rem;
}
.soon-badge {
  display: inline-block;
  background: linear-gradient(90deg, #fbbf24, #f59e42);
  color: #fff;
  font-weight: 600;
  border-radius: 8px;
  padding: 6px 18px;
  font-size: 1.1rem;
  margin-top: 10px;
  box-shadow: 0 2px 8px #fbbf2433;
}
</style>
