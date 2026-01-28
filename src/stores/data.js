import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDataStore = defineStore('data', () => {
  // Guruhlar
  const groups = ref([
    { id: 1, name: 'KI_25-04', faculty: 'Kompyuter injiniringi', year: 1, leaderId: 2, leaderName: 'Karimov Sardor', contractAmount: 18411000, isActive: true },
    { id: 2, name: 'DI_25-21', faculty: 'Dasturiy injiniring', year: 1, leaderId: null, leaderName: '', contractAmount: 18411000, isActive: true },
    { id: 3, name: 'FTO_24-03', faculty: 'Fizika-texnika', year: 2, leaderId: null, leaderName: '', contractAmount: 16500000, isActive: false },
    { id: 4, name: 'SE_25-01', faculty: 'Dasturiy injiniring', year: 1, leaderId: null, leaderName: '', contractAmount: 18411000, isActive: true },
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

  // Turnirlar
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
      customFields: [
        { id: 1, name: 'Ingliz tili darajasi', type: 'select', options: ['A1', 'A2', 'B1', 'B2', 'C1'], required: true },
        { id: 2, name: 'IELTS ball (agar mavjud)', type: 'text', required: false }
      ],
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

  const registerForTournament = (tournamentId, registration) => {
    const index = tournaments.value.findIndex(t => t.id === tournamentId)
    if (index !== -1) {
      const newId = tournaments.value[index].registrations.length > 0
        ? Math.max(...tournaments.value[index].registrations.map(r => r.id)) + 1
        : 1
      tournaments.value[index].registrations.push({
        id: newId,
        ...registration,
        registeredAt: new Date().toISOString(),
        status: 'pending'
      })
      return true
    }
    return false
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

  return {
    groups,
    students,
    schedule,
    attendanceRecords,
    reports,
    notifications,
    clubs,
    tournaments,
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
    registerForTournament,
    cancelRegistration,
    updateRegistrationStatus,
    isStudentRegistered,
    getStudentRegistrations
  }
})
