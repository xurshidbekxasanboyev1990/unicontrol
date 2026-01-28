/**
 * ============================================
 * UNI CONTROL - Asosiy Ma'lumotlar Store
 * ============================================
 * 
 * Bu eng katta store bo'lib, barcha asosiy ma'lumotlarni saqlaydi.
 * Production'da bu ma'lumotlar backend API'dan keladi.
 * 
 * MA'LUMOTLAR TUZILISHI:
 * ======================
 * 
 * 1. DIRECTIONS (Yo'nalishlar)
 *    Ta'lim yo'nalishlari: KI, DI, TIB, IQT va h.k.
 *    Har bir guruh bitta yo'nalishga tegishli.
 * 
 * 2. SUBJECTS (Fanlar)
 *    Bellashuv fanlari: Informatika, Matematika, Fizika va h.k.
 *    Turnirlar fan bo'yicha o'tkazilishi mumkin.
 * 
 * 3. DIRECTION_SUBJECTS (Yo'nalish-Fan bog'lanishi)
 *    Qaysi yo'nalish qaysi fanlarda qatnashishi mumkinligini belgilaydi.
 *    Masalan: KI -> [Informatika, Matematika, Fizika, Dasturlash]
 * 
 * 4. GROUPS (Guruhlar)
 *    Talabalar guruhlari. Har bir guruhda:
 *    - directionId: Yo'nalish
 *    - leaderId: Sardor (null bo'lishi mumkin)
 *    - isActive: Faol/Bloklangan holat
 *    - contractAmount: Yillik kontrakt summasi
 * 
 * 5. STUDENTS (Talabalar)
 *    Talabalar ro'yxati. Har bir talabada:
 *    - studentId: Login uchun ID (masalan: ST-2024-001)
 *    - role: 'student' yoki 'leader'
 *    - contractPaid: To'langan summa
 *    - password: Login paroli
 * 
 * 6. SCHEDULE (Dars jadvali)
 *    Haftalik dars jadvali: kun, vaqt, fan, o'qituvchi, xona
 * 
 * 7. ATTENDANCE_RECORDS (Davomat)
 *    Kunlik davomat: present, absent, late
 * 
 * 8. REPORTS (Hisobotlar)
 *    Sardor/Admin tomonidan yaratilgan hisobotlar
 * 
 * 9. NOTIFICATIONS (Bildirishnomalar)
 *    Tizim xabarlari
 * 
 * 10. CLUBS (To'garaklar)
 *     Qo'shimcha ta'lim to'garaklari
 * 
 * 11. TOURNAMENTS (Turnirlar)
 *     Bellashuvlar va olimpiadalar.
 *     isSubjectBased: true bo'lsa, faqat tegishli yo'nalish qatnashadi
 * 
 * MUHIM METODLAR:
 * ===============
 * - assignGroupLeader(): Sardor tayinlash (student.role = 'leader')
 * - toggleGroupStatus(): Guruhni bloklash (login taqiqlanadi)
 * - getAvailableSubjectsForStudent(): Turnir uchun mavjud fanlar
 * - registerForTournament(): Turnirga ro'yxatdan o'tish
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDataStore = defineStore('data', () => {
  // ===================================================================
  // 1. YO'NALISHLAR (Ta'lim yo'nalishlari)
  // ===================================================================
  const directions = ref([
    { id: 1, code: 'KI', name: 'Kompyuter injiniringi', faculty: 'Axborot texnologiyalari', isActive: true },
    { id: 2, code: 'DI', name: 'Dasturiy injiniring', faculty: 'Axborot texnologiyalari', isActive: true },
    { id: 3, code: 'AT', name: 'Axborot tizimlari', faculty: 'Axborot texnologiyalari', isActive: true },
    { id: 4, code: 'TIB', name: 'Tibbiyot', faculty: 'Tibbiyot fakulteti', isActive: true },
    { id: 5, code: 'IQT', name: 'Iqtisodiyot', faculty: 'Iqtisodiyot fakulteti', isActive: true },
    { id: 6, code: 'HUQ', name: 'Huquqshunoslik', faculty: 'Huquq fakulteti', isActive: true },
    { id: 7, code: 'FIL', name: 'Filologiya', faculty: 'Filologiya fakulteti', isActive: true },
    { id: 8, code: 'FTO', name: 'Fizika-texnika', faculty: 'Fizika-matematika fakulteti', isActive: true },
    { id: 9, code: 'KIM', name: 'Kimyo', faculty: 'Tabiiy fanlar fakulteti', isActive: true },
    { id: 10, code: 'BIO', name: 'Biologiya', faculty: 'Tabiiy fanlar fakulteti', isActive: true }
  ])

  // Fanlar (Bellashuv fanlari)
  const subjects = ref([
    { id: 1, name: 'Informatika', icon: 'Monitor', color: 'blue', isActive: true },
    { id: 2, name: 'Matematika', icon: 'Calculator', color: 'indigo', isActive: true },
    { id: 3, name: 'Fizika', icon: 'Atom', color: 'amber', isActive: true },
    { id: 4, name: 'Kimyo', icon: 'FlaskConical', color: 'green', isActive: true },
    { id: 5, name: 'Biologiya', icon: 'Leaf', color: 'emerald', isActive: true },
    { id: 6, name: 'Ingliz tili', icon: 'Languages', color: 'red', isActive: true },
    { id: 7, name: 'Tarix', icon: 'BookText', color: 'yellow', isActive: true },
    { id: 8, name: 'Huquq asoslari', icon: 'Scale', color: 'slate', isActive: true },
    { id: 9, name: 'Iqtisodiyot asoslari', icon: 'Banknote', color: 'cyan', isActive: true },
    { id: 10, name: 'Adabiyot', icon: 'BookOpen', color: 'purple', isActive: true },
    { id: 11, name: 'Dasturlash', icon: 'Code', color: 'teal', isActive: true },
    { id: 12, name: 'Robototexnika', icon: 'Cpu', color: 'orange', isActive: true }
  ])

  // Yo'nalish - Fan bog'lanishi (Qaysi yo'nalish qaysi fanlardan qatnashishi mumkin)
  const directionSubjects = ref([
    // Kompyuter injiniringi -> Informatika, Matematika, Fizika, Dasturlash, Robototexnika, Ingliz tili
    { directionId: 1, subjectIds: [1, 2, 3, 11, 12, 6] },
    // Dasturiy injiniring -> Informatika, Matematika, Dasturlash, Ingliz tili
    { directionId: 2, subjectIds: [1, 2, 11, 6] },
    // Axborot tizimlari -> Informatika, Matematika, Dasturlash
    { directionId: 3, subjectIds: [1, 2, 11] },
    // Tibbiyot -> Kimyo, Biologiya, Ingliz tili
    { directionId: 4, subjectIds: [4, 5, 6] },
    // Iqtisodiyot -> Matematika, Iqtisodiyot asoslari, Ingliz tili
    { directionId: 5, subjectIds: [2, 9, 6] },
    // Huquqshunoslik -> Huquq asoslari, Tarix, Ingliz tili
    { directionId: 6, subjectIds: [8, 7, 6] },
    // Filologiya -> Ingliz tili, Adabiyot, Tarix
    { directionId: 7, subjectIds: [6, 10, 7] },
    // Fizika-texnika -> Fizika, Matematika, Informatika
    { directionId: 8, subjectIds: [3, 2, 1] },
    // Kimyo -> Kimyo, Biologiya, Matematika
    { directionId: 9, subjectIds: [4, 5, 2] },
    // Biologiya -> Biologiya, Kimyo
    { directionId: 10, subjectIds: [5, 4] }
  ])

  // Guruhlar
  const groups = ref([
    { id: 1, name: 'KI_25-04', faculty: 'Kompyuter injiniringi', directionId: 1, year: 1, leaderId: 2, leaderName: 'Karimov Sardor', contractAmount: 18411000, isActive: true },
    { id: 2, name: 'DI_25-21', faculty: 'Dasturiy injiniring', directionId: 2, year: 1, leaderId: null, leaderName: '', contractAmount: 18411000, isActive: true },
    { id: 3, name: 'FTO_24-03', faculty: 'Fizika-texnika', directionId: 8, year: 2, leaderId: null, leaderName: '', contractAmount: 16500000, isActive: false },
    { id: 4, name: 'SE_25-01', faculty: 'Dasturiy injiniring', directionId: 2, year: 1, leaderId: null, leaderName: '', contractAmount: 18411000, isActive: true },
    { id: 5, name: 'TIB_25-01', faculty: 'Tibbiyot', directionId: 4, year: 1, leaderId: null, leaderName: '', contractAmount: 25000000, isActive: true },
    { id: 6, name: 'IQT_25-02', faculty: 'Iqtisodiyot', directionId: 5, year: 1, leaderId: null, leaderName: '', contractAmount: 15000000, isActive: true }
  ])

  // Talabalar
  const students = ref([
    {
      id: 1,
      studentId: 'ST-2024-001',
      name: 'Aliyev Jasur Vali o\'g\'li',
      phone: '+998 90 123 45 67',
      address: 'Toshkent sh., Chilonzor tumani',
      commute: 'Avtobus #45',
      groupId: 1,
      group: 'KI_25-04',
      contractPaid: 18411000,
      passport: 'AA 1234567',
      jshshir: '12345678901234',
      birthDate: '27.01.2004',
      role: 'student',
      avatar: null,
      email: 'jasur@uni.uz',
      password: '123456'
    },
    {
      id: 2,
      studentId: 'ST-2024-002',
      name: 'Karimov Sardor',
      phone: '+998 91 234 56 78',
      address: 'Toshkent sh., Yunusobod tumani',
      commute: 'Metro',
      groupId: 1,
      group: 'KI_25-04',
      contractPaid: 18411000,
      passport: 'AB 2345678',
      jshshir: '23456789012345',
      birthDate: '15.03.2003',
      role: 'leader',
      avatar: null,
      email: 'sardor@uni.uz',
      password: '123456'
    },
    {
      id: 3,
      studentId: 'ST-2024-003',
      name: 'Toshmatov Alisher',
      phone: '+998 92 345 67 89',
      address: 'Toshkent sh., Mirzo Ulug\'bek tumani',
      commute: 'Piyoda',
      groupId: 1,
      group: 'KI_25-04',
      contractPaid: 13808250,
      passport: 'AC 3456789',
      jshshir: '34567890123456',
      birthDate: '08.07.2004',
      role: 'student',
      avatar: null,
      email: 'alisher@uni.uz',
      password: '123456'
    },
    {
      id: 4,
      studentId: 'ST-2024-004',
      name: 'Rahimov Bekzod',
      phone: '+998 93 456 78 90',
      address: 'Toshkent sh., Sergeli tumani',
      commute: 'Avtobus #67',
      groupId: 1,
      group: 'KI_25-04',
      contractPaid: 9205500,
      passport: 'AD 4567890',
      jshshir: '45678901234567',
      birthDate: '22.11.2003',
      role: 'student',
      avatar: null,
      email: 'bekzod@uni.uz',
      password: '123456'
    },
    {
      id: 5,
      studentId: 'ST-2024-005',
      name: 'Xolmatov Ulug\'bek',
      phone: '+998 94 567 89 01',
      address: 'Toshkent sh., Olmazor tumani',
      commute: 'Tramvay',
      groupId: 1,
      group: 'KI_25-04',
      contractPaid: 20000000,
      passport: 'AE 5678901',
      jshshir: '56789012345678',
      birthDate: '30.05.2004',
      role: 'student',
      avatar: null,
      email: 'ulugbek@uni.uz',
      password: '123456'
    }
  ])

  // Dars jadvali
  const schedule = ref([
    { id: 1, groupId: 1, day: 'Dushanba', time: '08:30-10:00', subject: 'Oliy matematika', teacher: 'Karimov A.', room: 'A-301', type: 'Ma\'ruza' },
    { id: 2, groupId: 1, day: 'Dushanba', time: '10:10-11:40', subject: 'Fizika', teacher: 'Saidov B.', room: 'B-205', type: 'Amaliy' },
    { id: 3, groupId: 1, day: 'Dushanba', time: '12:30-14:00', subject: 'Dasturlash', teacher: 'Toshmatov I.', room: 'Kompyuter xonasi', type: 'Laboratoriya' },
    { id: 4, groupId: 1, day: 'Seshanba', time: '08:30-10:00', subject: 'Ingliz tili', teacher: 'Johnson M.', room: 'C-102', type: 'Amaliy' },
    { id: 5, groupId: 1, day: 'Seshanba', time: '10:10-11:40', subject: 'Oliy matematika', teacher: 'Karimov A.', room: 'A-301', type: 'Amaliy' },
    { id: 6, groupId: 1, day: 'Chorshanba', time: '08:30-10:00', subject: 'Fizika', teacher: 'Saidov B.', room: 'Fizika laboratoriyasi', type: 'Laboratoriya' },
    { id: 7, groupId: 1, day: 'Chorshanba', time: '10:10-11:40', subject: 'Falsafa', teacher: 'Rahmonov S.', room: 'D-401', type: 'Ma\'ruza' },
    { id: 8, groupId: 1, day: 'Payshanba', time: '08:30-10:00', subject: 'Dasturlash', teacher: 'Toshmatov I.', room: 'Kompyuter xonasi', type: 'Ma\'ruza' },
    { id: 9, groupId: 1, day: 'Payshanba', time: '10:10-11:40', subject: 'Chiziqli algebra', teacher: 'Karimov A.', room: 'A-302', type: 'Ma\'ruza' },
    { id: 10, groupId: 1, day: 'Juma', time: '08:30-10:00', subject: 'Jismoniy tarbiya', teacher: 'Azimov R.', room: 'Sport zali', type: 'Amaliy' },
  ])

  // Davomat
  const attendanceRecords = ref([
    { id: 1, studentId: 1, date: '2024-01-22', status: 'present', note: '' },
    { id: 2, studentId: 2, date: '2024-01-22', status: 'present', note: '' },
    { id: 3, studentId: 3, date: '2024-01-22', status: 'absent', note: 'Kasal' },
    { id: 4, studentId: 4, date: '2024-01-22', status: 'present', note: '' },
    { id: 5, studentId: 5, date: '2024-01-22', status: 'late', note: '15 daqiqa kechikdi' },
  ])

  // Hisobotlar
  const reports = ref([
    { id: 1, title: 'Yanvar oyi davomat hisoboti', type: 'attendance', groupId: 1, createdBy: 2, date: '2024-01-31', status: 'completed' },
    { id: 2, title: 'KI_25-04 guruh haftalik hisoboti', type: 'weekly', groupId: 1, createdBy: 2, date: '2024-01-28', status: 'completed' },
    { id: 3, title: 'Dekabr oyi yakuniy hisobot', type: 'monthly', groupId: 1, createdBy: 2, date: '2024-12-31', status: 'completed' },
  ])

  // Bildirishnomalar
  const notifications = ref([
    { id: 1, title: 'Tizimga xush kelibsiz!', message: 'Uni Control tizimiga muvaffaqiyatli kirdingiz.', date: '2024-01-22', read: false },
  ])

  // To'garaklar
  const clubs = ref([
    { 
      id: 1, 
      name: 'Matematika to\'garagi', 
      teacher: 'Karimov Aziz Shavkatovich',
      phone: '+998 90 111 22 33',
      description: 'Oliy matematika, chiziqli algebra va matematik analiz bo\'yicha qo\'shimcha darslar',
      schedule: 'Dushanba, Chorshanba - 16:00',
      price: 200000,
      room: 'A-301',
      isActive: true,
      category: 'fan',
      image: null
    },
    { 
      id: 2, 
      name: 'Ingliz tili kursi', 
      teacher: 'Johnson Michael',
      phone: '+998 91 222 33 44',
      description: 'IELTS tayyorgarlik kursi. Speaking, Writing, Reading, Listening',
      schedule: 'Seshanba, Payshanba - 15:00',
      price: 350000,
      room: 'B-205',
      isActive: true,
      category: 'til',
      image: null
    },
    { 
      id: 3, 
      name: 'Dasturlash kursi', 
      teacher: 'Toshmatov Islom',
      phone: '+998 93 333 44 55',
      description: 'Python, JavaScript va Web dasturlash asoslari',
      schedule: 'Shanba - 10:00',
      price: 400000,
      room: 'Kompyuter xonasi',
      isActive: true,
      category: 'texnik',
      image: null
    },
    { 
      id: 4, 
      name: 'Futbol to\'garagi', 
      teacher: 'Azimov Rustam',
      phone: '+998 94 444 55 66',
      description: 'Professional murabbiy nazoratida futbol mashg\'ulotlari',
      schedule: 'Dushanba, Chorshanba, Juma - 17:00',
      price: 150000,
      room: 'Stadium',
      isActive: true,
      category: 'sport',
      image: null
    }
  ])

  // ===================================================================
  // 11. TURNIRLAR - YANGI TUZILISH
  // ===================================================================
  // 
  // YANGI MODEL:
  // - participationRules[]: Har bir yo'nalish uchun alohida qoidalar
  // - selectionMode: 'fixed' | 'single' | 'multiple'
  // - registration.selectedSubjectIds[]: Bir nechta fan tanlash imkoniyati
  //
  // SELECTION MODES:
  // - fixed: Tanlov yo'q, 1 ta fan avtomatik (masalan: KI -> Informatika)
  // - single: allowedSubjectIds ichidan faqat 1 ta tanlash (masalan: MED -> Bio YOKI Kimyo)
  // - multiple: allowedSubjectIds ichidan bir nechta tanlash (masalan: MED -> Bio VA Kimyo)
  //
  const tournaments = ref([
    {
      id: 1,
      title: 'Dasturlash olimpiadasi 2026',
      description: 'Universitet miqyosidagi dasturlash bellashuvi. Python, C++, Java tillarida algoritmik masalalar yechiladi.',
      category: 'intellektual',
      type: 'olimpiada',
      startDate: '2026-02-15',
      endDate: '2026-02-15',
      registrationDeadline: '2026-02-10',
      location: 'Kompyuter laboratoriyasi, A-korpus',
      maxParticipants: 50,
      prize: '1-o\'rin: 2,000,000 so\'m, 2-o\'rin: 1,000,000 so\'m, 3-o\'rin: 500,000 so\'m',
      organizer: 'IT fakulteti',
      contactPhone: '+998 90 123 45 67',
      isActive: true,
      image: null,
      // Qatnashish qoidalari - bu oddiy turnir, hamma qatnashishi mumkin (qoidalar bo'sh)
      participationRules: [],
      customFields: [
        { id: 1, name: 'Dasturlash tili', type: 'select', options: ['Python', 'C++', 'Java', 'JavaScript'], required: true },
        { id: 2, name: 'Tajriba darajasi', type: 'select', options: ['Boshlang\'ich', 'O\'rta', 'Yuqori'], required: true }
      ],
      registrations: []
    },
    {
      id: 2,
      title: 'Futbol chempionati',
      description: 'Fakultetlar o\'rtasida futbol bellashuvi. Har bir jamoa 11 nafardan iborat.',
      category: 'sport',
      type: 'chempionat',
      startDate: '2026-03-01',
      endDate: '2026-03-30',
      registrationDeadline: '2026-02-25',
      location: 'Universitet stadioni',
      maxParticipants: 100,
      prize: 'G\'olib jamoaga kubok va medallar',
      organizer: 'Sport bo\'limi',
      contactPhone: '+998 91 234 56 78',
      isActive: true,
      image: null,
      participationRules: [], // Hamma qatnashishi mumkin
      customFields: [
        { id: 1, name: 'Pozitsiya', type: 'select', options: ['Darvozabon', 'Himoyachi', 'Yarim himoyachi', 'Hujumchi'], required: true },
        { id: 2, name: 'Jamoa nomi', type: 'text', required: true },
        { id: 3, name: 'Futbolka raqami', type: 'number', required: true }
      ],
      registrations: []
    },
    {
      id: 3,
      title: 'Ingliz tili olimpiadasi',
      description: 'Speaking, Writing, Reading va Listening bo\'limlari bo\'yicha sinov',
      category: 'intellektual',
      type: 'olimpiada',
      startDate: '2026-02-20',
      endDate: '2026-02-20',
      registrationDeadline: '2026-02-15',
      location: 'Tillar fakulteti, B-korpus',
      maxParticipants: 80,
      prize: 'IELTS kursiga bepul yo\'llanma',
      organizer: 'Tillar fakulteti',
      contactPhone: '+998 93 345 67 89',
      isActive: true,
      image: null,
      participationRules: [], // Hamma qatnashishi mumkin
      customFields: [
        { id: 1, name: 'Ingliz tili darajasi', type: 'select', options: ['A1', 'A2', 'B1', 'B2', 'C1'], required: true },
        { id: 2, name: 'IELTS ball (agar mavjud)', type: 'text', required: false }
      ],
      registrations: []
    },
    {
      id: 4,
      title: 'Bilimlar bellashuvi 2026',
      description: 'Har bir yo\'nalish o\'z fanlaridan bellashadi. Yo\'nalishga qarab 1 yoki 2 ta fan tanlash mumkin.',
      category: 'intellektual',
      type: 'olimpiada',
      startDate: '2026-03-10',
      endDate: '2026-03-12',
      registrationDeadline: '2026-03-05',
      location: 'Bosh bino, barcha auditoriyalar',
      maxParticipants: 500,
      prize: 'Har bir fan bo\'yicha: 1-o\'rin: 1,500,000 so\'m, 2-o\'rin: 1,000,000 so\'m, 3-o\'rin: 500,000 so\'m',
      organizer: 'O\'quv bo\'limi',
      contactPhone: '+998 90 999 88 77',
      isActive: true,
      image: null,
      // ===== QATNASHISH QOIDALARI =====
      // Har bir yo'nalish uchun alohida qoida
      participationRules: [
        {
          id: 1,
          directionId: 1, // KI - Kompyuter injiniringi
          allowedSubjectIds: [1], // Faqat Informatika
          selectionMode: 'fixed', // Tanlov yo'q
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 2,
          directionId: 2, // DI - Dasturiy injiniring
          allowedSubjectIds: [1], // Faqat Informatika
          selectionMode: 'fixed',
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 3,
          directionId: 4, // TIB - Tibbiyot (MED)
          allowedSubjectIds: [4, 5], // Kimyo va Biologiya
          selectionMode: 'single', // 1 ta tanlash kerak
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 4,
          directionId: 5, // IQT - Iqtisodiyot
          allowedSubjectIds: [2], // Faqat Matematika
          selectionMode: 'fixed',
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 5,
          directionId: 6, // HUQ - Huquqshunoslik
          allowedSubjectIds: [7], // Faqat Tarix
          selectionMode: 'fixed',
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 6,
          directionId: 7, // FIL - Filologiya (Ingliz tili)
          allowedSubjectIds: [6], // Faqat Ingliz tili
          selectionMode: 'fixed',
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 7,
          directionId: 8, // FTO - Fizika-texnika
          allowedSubjectIds: [3], // Faqat Fizika
          selectionMode: 'fixed',
          minSelect: 1,
          maxSelect: 1
        },
        {
          id: 8,
          directionId: 9, // KIM - Kimyo
          allowedSubjectIds: [4, 5], // Kimyo va Biologiya
          selectionMode: 'multiple', // 1 yoki 2 ta tanlash mumkin
          minSelect: 1,
          maxSelect: 2
        },
        {
          id: 9,
          directionId: 10, // BIO - Biologiya
          allowedSubjectIds: [5, 4], // Biologiya va Kimyo
          selectionMode: 'multiple', // 1 yoki 2 ta tanlash mumkin
          minSelect: 1,
          maxSelect: 2
        }
      ],
      customFields: [],
      registrations: []
    }
  ])

  // Computed
  const getStudentsByGroup = computed(() => (groupId) => {
    return students.value.filter(s => s.groupId === groupId)
  })

  const getScheduleByGroup = computed(() => (groupId) => {
    return schedule.value.filter(s => s.groupId === groupId)
  })

  const getAttendanceByStudent = computed(() => (studentId) => {
    return attendanceRecords.value.filter(a => a.studentId === studentId)
  })

  const getAttendanceByDate = computed(() => (date) => {
    return attendanceRecords.value.filter(a => a.date === date)
  })

  const calculateContractPercentage = computed(() => (paid, total) => {
    return Math.round((paid / total) * 100)
  })

  // Student methods
  const addStudent = (student) => {
    const newId = students.value.length > 0 ? Math.max(...students.value.map(s => s.id)) + 1 : 1
    students.value.push({ id: newId, ...student })
    return newId
  }

  const updateStudent = (id, data) => {
    const index = students.value.findIndex(s => s.id === id)
    if (index !== -1) {
      students.value[index] = { ...students.value[index], ...data }
    }
  }

  const updateStudentFull = (id, data) => {
    const index = students.value.findIndex(s => s.id === id)
    if (index !== -1) {
      students.value[index] = { ...students.value[index], ...data }
    }
  }

  const deleteStudent = (id) => {
    const index = students.value.findIndex(s => s.id === id)
    if (index !== -1) {
      students.value.splice(index, 1)
    }
  }

  // Group methods
  const addGroup = (group) => {
    const newId = groups.value.length > 0 ? Math.max(...groups.value.map(g => g.id)) + 1 : 1
    groups.value.push({ id: newId, ...group, isActive: true })
    return newId
  }

  const updateGroup = (id, data) => {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value[index] = { ...groups.value[index], ...data }
    }
  }

  const deleteGroup = (id) => {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value.splice(index, 1)
    }
  }

  const updateGroupContract = (id, amount) => {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value[index].contractAmount = amount
    }
  }

  const assignGroupLeader = (groupId, studentId, studentName) => {
    const gIndex = groups.value.findIndex(g => g.id === groupId)
    if (gIndex !== -1) {
      groups.value[gIndex].leaderId = studentId
      groups.value[gIndex].leaderName = studentName
    }
    const sIndex = students.value.findIndex(s => s.id === studentId)
    if (sIndex !== -1) {
      students.value[sIndex].role = 'leader'
    }
  }

  const removeGroupLeader = (groupId) => {
    const group = groups.value.find(g => g.id === groupId)
    if (group && group.leaderId) {
      const sIndex = students.value.findIndex(s => s.id === group.leaderId)
      if (sIndex !== -1) {
        students.value[sIndex].role = 'student'
      }
      group.leaderId = null
      group.leaderName = ''
    }
  }

  const toggleGroupStatus = (id) => {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value[index].isActive = !groups.value[index].isActive
    }
  }

  const isGroupActive = (groupId) => {
    const group = groups.value.find(g => g.id === groupId)
    return group ? group.isActive : false
  }

  const importFromExcel = (data, groupId, groupName) => {
    data.forEach(row => {
      const newId = students.value.length > 0 ? Math.max(...students.value.map(s => s.id)) + 1 : 1
      students.value.push({
        id: newId,
        studentId: row.studentId || `ST-${Date.now()}-${newId}`,
        name: row.name,
        phone: row.phone || '',
        address: row.address || '',
        commute: row.commute || '',
        groupId: groupId,
        group: groupName,
        contractPaid: row.contractPaid || 0,
        passport: row.passport || '',
        jshshir: row.jshshir || '',
        birthDate: row.birthDate || '',
        role: 'student',
        avatar: null,
        email: row.email || '',
        password: '123456'
      })
    })
  }

  const updateStudentPassword = (studentId, newPassword) => {
    const index = students.value.findIndex(s => s.id === studentId)
    if (index !== -1) {
      students.value[index].password = newPassword
    }
  }

  const findStudentByStudentId = (studentIdCode) => {
    return students.value.find(s => s.studentId === studentIdCode)
  }

  // Attendance methods
  const addAttendanceRecord = (record) => {
    const newId = attendanceRecords.value.length > 0 ? Math.max(...attendanceRecords.value.map(a => a.id)) + 1 : 1
    attendanceRecords.value.push({ id: newId, ...record })
  }

  const updateAttendanceRecord = (id, data) => {
    const index = attendanceRecords.value.findIndex(a => a.id === id)
    if (index !== -1) {
      attendanceRecords.value[index] = { ...attendanceRecords.value[index], ...data }
    }
  }

  // Schedule methods
  const addScheduleItem = (item) => {
    const newId = schedule.value.length > 0 ? Math.max(...schedule.value.map(s => s.id)) + 1 : 1
    schedule.value.push({ id: newId, ...item })
  }

  const updateScheduleItem = (id, data) => {
    const index = schedule.value.findIndex(s => s.id === id)
    if (index !== -1) {
      schedule.value[index] = { ...schedule.value[index], ...data }
    }
  }

  const deleteScheduleItem = (id) => {
    const index = schedule.value.findIndex(s => s.id === id)
    if (index !== -1) {
      schedule.value.splice(index, 1)
    }
  }

  // Report methods
  const addReport = (report) => {
    const newId = reports.value.length > 0 ? Math.max(...reports.value.map(r => r.id)) + 1 : 1
    reports.value.push({ id: newId, ...report })
  }

  // Notification methods
  const addNotification = (notification) => {
    const newId = notifications.value.length > 0 ? Math.max(...notifications.value.map(n => n.id)) + 1 : 1
    notifications.value.push({ id: newId, ...notification, read: false })
  }

  const deleteNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  const sendNotification = (notification) => {
    addNotification(notification)
  }

  const importStudentsFromExcel = (studentsData, groupId, groupName) => {
    studentsData.forEach(row => {
      const newId = students.value.length > 0 ? Math.max(...students.value.map(s => s.id)) + 1 : 1
      students.value.push({
        id: newId,
        studentId: row.studentId || `ST-${Date.now()}-${newId}`,
        name: row.name,
        phone: row.phone || '',
        address: row.address || '',
        commute: row.commute || '',
        groupId: groupId,
        group: groupName,
        contractPaid: row.contractPaid || 0,
        passport: row.passport || '',
        jshshir: row.jshshir || '',
        birthDate: row.birthDate || '',
        role: 'student',
        avatar: null,
        email: row.email || '',
        password: '123456'
      })
    })
  }

  const getStatistics = () => {
    return {
      totalStudents: students.value.length,
      totalGroups: groups.value.length,
      activeGroups: groups.value.filter(g => g.isActive).length
    }
  }

  // Club methods
  const addClub = (club) => {
    const newId = clubs.value.length > 0 ? Math.max(...clubs.value.map(c => c.id)) + 1 : 1
    clubs.value.push({ id: newId, ...club, isActive: true })
    return newId
  }

  const updateClub = (id, data) => {
    const index = clubs.value.findIndex(c => c.id === id)
    if (index !== -1) {
      clubs.value[index] = { ...clubs.value[index], ...data }
    }
  }

  const deleteClub = (id) => {
    const index = clubs.value.findIndex(c => c.id === id)
    if (index !== -1) {
      clubs.value.splice(index, 1)
    }
  }

  const toggleClubStatus = (id) => {
    const index = clubs.value.findIndex(c => c.id === id)
    if (index !== -1) {
      clubs.value[index].isActive = !clubs.value[index].isActive
    }
  }

  const getActiveClubs = computed(() => {
    return clubs.value.filter(c => c.isActive)
  })

  // Tournament methods
  const addTournament = (tournament) => {
    const newId = tournaments.value.length > 0 ? Math.max(...tournaments.value.map(t => t.id)) + 1 : 1
    tournaments.value.push({ id: newId, ...tournament, registrations: [], isActive: true })
    return newId
  }

  const updateTournament = (id, data) => {
    const index = tournaments.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tournaments.value[index] = { ...tournaments.value[index], ...data }
    }
  }

  const deleteTournament = (id) => {
    const index = tournaments.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tournaments.value.splice(index, 1)
    }
  }

  const toggleTournamentStatus = (id) => {
    const index = tournaments.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tournaments.value[index].isActive = !tournaments.value[index].isActive
    }
  }

  const getActiveTournaments = computed(() => {
    return tournaments.value.filter(t => t.isActive)
  })

  // ========================================
  // YANGI TURNIR MODELI HELPER FUNKSIYALARI
  // ========================================

  /**
   * Yo'nalish uchun qatnashish qoidasini olish
   * @param {number} tournamentId - Turnir ID
   * @param {number} directionId - Yo'nalish ID
   * @returns {Object|null} - Qatnashish qoidasi yoki null
   */
  const getParticipationRuleForDirection = (tournamentId, directionId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    if (!tournament || !tournament.participationRules) return null
    return tournament.participationRules.find(r => r.directionId === directionId) || null
  }

  /**
   * Talaba uchun qatnashish qoidasini olish (groupId orqali)
   * @param {number} tournamentId - Turnir ID
   * @param {number} groupId - Guruh ID
   * @returns {Object|null} - Qatnashish qoidasi yoki null
   */
  const getParticipationRuleForStudent = (tournamentId, groupId) => {
    const direction = getDirectionByGroupId(groupId)
    if (!direction) return null
    return getParticipationRuleForDirection(tournamentId, direction.id)
  }

  /**
   * Turnirda qatnashish qoidalari borligini tekshirish
   * @param {number} tournamentId - Turnir ID
   * @returns {boolean}
   */
  const hasParticipationRules = (tournamentId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    return tournament?.participationRules?.length > 0
  }

  /**
   * Ro'yxatdan o'tish validatsiyasi
   * @param {number} tournamentId - Turnir ID
   * @param {number} directionId - Yo'nalish ID
   * @param {number[]} selectedSubjectIds - Tanlangan fanlar
   * @returns {Object} - { valid: boolean, message: string }
   */
  const validateTournamentRegistration = (tournamentId, directionId, selectedSubjectIds) => {
    const rule = getParticipationRuleForDirection(tournamentId, directionId)
    
    if (!rule) {
      return { valid: false, message: 'Sizning yo\'nalishingiz bu turnirda qatnasha olmaydi' }
    }

    // Tanlangan fanlar ruxsat etilgan fanlar ichida ekanligini tekshirish
    const invalidSubjects = selectedSubjectIds.filter(id => !rule.allowedSubjectIds.includes(id))
    if (invalidSubjects.length > 0) {
      return { valid: false, message: 'Tanlangan fanlardan ba\'zilari ruxsat etilmagan' }
    }

    // selectionMode bo'yicha tekshirish
    switch (rule.selectionMode) {
      case 'fixed':
        // Fixed rejimda faqat bitta ruxsat etilgan fan bo'ladi va u avtomatik tanlanadi
        if (selectedSubjectIds.length !== 1 || selectedSubjectIds[0] !== rule.allowedSubjectIds[0]) {
          return { valid: false, message: 'Bu yo\'nalish uchun fan avtomatik belgilangan' }
        }
        break
      
      case 'single':
        // Faqat bitta fan tanlash kerak
        if (selectedSubjectIds.length !== 1) {
          return { valid: false, message: 'Faqat bitta fan tanlashingiz kerak' }
        }
        break
      
      case 'multiple':
        // Min va max chegaralarni tekshirish
        if (selectedSubjectIds.length < rule.minSelect) {
          return { valid: false, message: `Kamida ${rule.minSelect} ta fan tanlashingiz kerak` }
        }
        if (selectedSubjectIds.length > rule.maxSelect) {
          return { valid: false, message: `Ko'pi bilan ${rule.maxSelect} ta fan tanlashingiz mumkin` }
        }
        break
      
      default:
        return { valid: false, message: 'Noma\'lum tanlash rejimi' }
    }

    return { valid: true, message: 'Validatsiya muvaffaqiyatli' }
  }

  /**
   * Turnirga ro'yxatdan o'tish (YANGI MODEL)
   * @param {number} tournamentId - Turnir ID
   * @param {Object} registration - Ro'yxatdan o'tish ma'lumotlari
   *   - studentId: Talaba ID
   *   - selectedSubjectIds: Tanlangan fanlar ro'yxati (agar qoidalar bo'lsa)
   */
  const registerForTournament = (tournamentId, registration) => {
    const index = tournaments.value.findIndex(t => t.id === tournamentId)
    if (index === -1) {
      return { success: false, message: 'Turnir topilmadi' }
    }

    const tournament = tournaments.value[index]
    const { studentId, selectedSubjectIds = [] } = registration

    // Tekshirish: allaqachon ro'yxatdan o'tganmi?
    if (tournament.registrations.some(r => r.studentId === studentId)) {
      return { success: false, message: 'Siz allaqachon ro\'yxatdan o\'tgansiz' }
    }

    // Talabani topish
    const student = students.value.find(s => s.id === studentId)
    if (!student) {
      return { success: false, message: 'Talaba topilmadi' }
    }

    // Talaba yo'nalishini aniqlash
    const direction = getDirectionByGroupId(student.groupId)
    
    let finalSelectedSubjectIds = selectedSubjectIds
    let selectedSubjectNames = []

    // Qatnashish qoidalarini tekshirish (agar mavjud bo'lsa)
    if (hasParticipationRules(tournamentId)) {
      if (!direction) {
        return { success: false, message: 'Talaba yo\'nalishi aniqlanmadi' }
      }

      const rule = getParticipationRuleForDirection(tournamentId, direction.id)
      
      if (!rule) {
        return { success: false, message: 'Sizning yo\'nalishingiz bu turnirda qatnasha olmaydi' }
      }

      // Fixed rejimda avtomatik fan belgilash
      if (rule.selectionMode === 'fixed') {
        finalSelectedSubjectIds = [...rule.allowedSubjectIds]
      }

      // Validatsiya
      const validation = validateTournamentRegistration(tournamentId, direction.id, finalSelectedSubjectIds)
      if (!validation.valid) {
        return { success: false, message: validation.message }
      }
    }

    // Tanlangan fanlar nomlarini olish
    if (finalSelectedSubjectIds.length > 0) {
      selectedSubjectNames = finalSelectedSubjectIds.map(id => {
        const subject = subjects.value.find(s => s.id === id)
        return subject?.name || 'Noma\'lum'
      })
    }
    
    const newId = tournament.registrations.length > 0
      ? Math.max(...tournament.registrations.map(r => r.id)) + 1
      : 1

    tournament.registrations.push({
      id: newId,
      studentId,
      studentName: student.name,
      directionId: direction?.id || null,
      directionName: direction?.name || null,
      selectedSubjectIds: finalSelectedSubjectIds,
      selectedSubjectNames,
      registeredAt: new Date().toISOString(),
      status: 'pending'
    })
    
    return { success: true, message: 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz' }
  }

  const cancelRegistration = (tournamentId, registrationId) => {
    const tIndex = tournaments.value.findIndex(t => t.id === tournamentId)
    if (tIndex !== -1) {
      const rIndex = tournaments.value[tIndex].registrations.findIndex(r => r.id === registrationId)
      if (rIndex !== -1) {
        tournaments.value[tIndex].registrations.splice(rIndex, 1)
        return true
      }
    }
    return false
  }

  const updateRegistrationStatus = (tournamentId, registrationId, status) => {
    const tIndex = tournaments.value.findIndex(t => t.id === tournamentId)
    if (tIndex !== -1) {
      const rIndex = tournaments.value[tIndex].registrations.findIndex(r => r.id === registrationId)
      if (rIndex !== -1) {
        tournaments.value[tIndex].registrations[rIndex].status = status
        return true
      }
    }
    return false
  }

  const isStudentRegistered = (tournamentId, studentId) => {
    const tournament = tournaments.value.find(t => t.id === tournamentId)
    if (tournament) {
      return tournament.registrations.some(r => r.studentId === studentId)
    }
    return false
  }

  const getStudentRegistrations = (studentId) => {
    const result = []
    tournaments.value.forEach(t => {
      const reg = t.registrations.find(r => r.studentId === studentId)
      if (reg) {
        result.push({ tournament: t, registration: reg })
      }
    })
    return result
  }

  // Yo'nalish va Fan funksiyalari
  const getDirectionById = (id) => {
    return directions.value.find(d => d.id === id)
  }

  const getSubjectById = (id) => {
    return subjects.value.find(s => s.id === id)
  }

  const getSubjectsByDirection = (directionId) => {
    const link = directionSubjects.value.find(ds => ds.directionId === directionId)
    if (link) {
      return subjects.value.filter(s => link.subjectIds.includes(s.id))
    }
    return []
  }

  const getDirectionByGroupId = (groupId) => {
    const group = groups.value.find(g => g.id === groupId)
    if (group && group.directionId) {
      return directions.value.find(d => d.id === group.directionId)
    }
    return null
  }

  const canStudentRegisterForSubject = (studentGroupId, subjectId) => {
    const group = groups.value.find(g => g.id === studentGroupId)
    if (!group || !group.directionId) return false
    
    const link = directionSubjects.value.find(ds => ds.directionId === group.directionId)
    if (link) {
      return link.subjectIds.includes(subjectId)
    }
    return false
  }

  const getAvailableSubjectsForStudent = (studentGroupId, tournamentSubjectIds) => {
    const group = groups.value.find(g => g.id === studentGroupId)
    if (!group || !group.directionId) return []
    
    const link = directionSubjects.value.find(ds => ds.directionId === group.directionId)
    if (link) {
      // Turnirdagi fanlar va talaba yo'nalishi fanlari kesishmasi
      return subjects.value.filter(s => 
        tournamentSubjectIds.includes(s.id) && link.subjectIds.includes(s.id)
      )
    }
    return []
  }

  // Direction CRUD
  const addDirection = (direction) => {
    const newId = directions.value.length > 0 ? Math.max(...directions.value.map(d => d.id)) + 1 : 1
    directions.value.push({ id: newId, ...direction, isActive: true })
    return newId
  }

  const updateDirection = (id, data) => {
    const index = directions.value.findIndex(d => d.id === id)
    if (index !== -1) {
      directions.value[index] = { ...directions.value[index], ...data }
    }
  }

  const deleteDirection = (id) => {
    const index = directions.value.findIndex(d => d.id === id)
    if (index !== -1) {
      directions.value.splice(index, 1)
    }
  }

  // Subject CRUD
  const addSubject = (subject) => {
    const newId = subjects.value.length > 0 ? Math.max(...subjects.value.map(s => s.id)) + 1 : 1
    subjects.value.push({ id: newId, ...subject, isActive: true })
    return newId
  }

  const updateSubject = (id, data) => {
    const index = subjects.value.findIndex(s => s.id === id)
    if (index !== -1) {
      subjects.value[index] = { ...subjects.value[index], ...data }
    }
  }

  const deleteSubject = (id) => {
    const index = subjects.value.findIndex(s => s.id === id)
    if (index !== -1) {
      subjects.value.splice(index, 1)
    }
  }

  // Direction-Subject link
  const updateDirectionSubjects = (directionId, subjectIds) => {
    const index = directionSubjects.value.findIndex(ds => ds.directionId === directionId)
    if (index !== -1) {
      directionSubjects.value[index].subjectIds = subjectIds
    } else {
      directionSubjects.value.push({ directionId, subjectIds })
    }
  }

  return {
    groups,
    students,
    schedule,
    attendanceRecords,
    reports,
    notifications,
    clubs,
    tournaments,
    directions,
    subjects,
    directionSubjects,
    getStudentsByGroup,
    getScheduleByGroup,
    getAttendanceByStudent,
    getAttendanceByDate,
    calculateContractPercentage,
    addStudent,
    updateStudent,
    updateStudentFull,
    deleteStudent,
    addGroup,
    updateGroup,
    deleteGroup,
    updateGroupContract,
    assignGroupLeader,
    removeGroupLeader,
    toggleGroupStatus,
    isGroupActive,
    importFromExcel,
    updateStudentPassword,
    findStudentByStudentId,
    addAttendanceRecord,
    updateAttendanceRecord,
    addScheduleItem,
    updateScheduleItem,
    deleteScheduleItem,
    addReport,
    addNotification,
    deleteNotification,
    sendNotification,
    importStudentsFromExcel,
    getStatistics,
    addClub,
    updateClub,
    deleteClub,
    toggleClubStatus,
    getActiveClubs,
    addTournament,
    updateTournament,
    deleteTournament,
    toggleTournamentStatus,
    getActiveTournaments,
    // Yangi turnir helper funksiyalari
    getParticipationRuleForDirection,
    getParticipationRuleForStudent,
    hasParticipationRules,
    validateTournamentRegistration,
    registerForTournament,
    cancelRegistration,
    updateRegistrationStatus,
    isStudentRegistered,
    getStudentRegistrations,
    getDirectionById,
    getSubjectById,
    getSubjectsByDirection,
    getDirectionByGroupId,
    canStudentRegisterForSubject,
    getAvailableSubjectsForStudent,
    addDirection,
    updateDirection,
    deleteDirection,
    addSubject,
    updateSubject,
    deleteSubject,
    updateDirectionSubjects
  }
})
