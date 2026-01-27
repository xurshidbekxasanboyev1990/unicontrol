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
    },
    {
      id: 6,
      studentId: 'ST-2024-006',
      name: 'Normatov Amir',
      phone: '+998 95 678 90 12',
      address: 'Toshkent sh., Yakkasaroy tumani',
      commute: 'Metro',
      groupId: 2,
      group: 'DI_25-21',
      contractPaid: 18411000,
      passport: 'AF 6789012',
      jshshir: '67890123456789',
      birthDate: '14.02.2003',
      role: 'student',
      avatar: null,
      email: 'amir@uni.uz',
      password: '123456'
    },
    {
      id: 7,
      studentId: 'ST-2024-007',
      name: 'Qodirov Shoxrux',
      phone: '+998 96 789 01 23',
      address: 'Toshkent sh., Bektemir tumani',
      commute: 'Avtobus #12',
      groupId: 2,
      group: 'DI_25-21',
      contractPaid: 14000000,
      passport: 'AG 7890123',
      jshshir: '78901234567890',
      birthDate: '03.09.2004',
      role: 'student',
      avatar: null,
      email: 'shoxrux@uni.uz',
      password: '123456'
    },
    {
      id: 8,
      studentId: 'ST-2024-008',
      name: 'Yusupova Nilufar',
      phone: '+998 97 890 12 34',
      address: 'Toshkent sh., Shayxontohur tumani',
      commute: 'Piyoda',
      groupId: 3,
      group: 'FTO_24-03',
      contractPaid: 16500000,
      passport: 'AH 8901234',
      jshshir: '89012345678901',
      birthDate: '19.12.2003',
      role: 'student',
      avatar: null,
      email: 'nilufar@uni.uz',
      password: '123456'
    }
  ])

  // Dars jadvali
  const schedule = ref([
    { id: 1, day: 'Dushanba', time: '08:30-09:50', subject: 'Matematika', teacher: 'Karimov A.', room: 'A-401', groupId: 1 },
    { id: 2, day: 'Dushanba', time: '10:00-11:20', subject: 'Dasturlash', teacher: 'Toshmatov I.', room: 'B-302', groupId: 1 },
    { id: 3, day: 'Dushanba', time: '11:30-12:50', subject: 'Fizika', teacher: 'Raximov S.', room: 'C-201', groupId: 1 },
    { id: 4, day: 'Seshanba', time: '08:30-09:50', subject: 'Ingliz tili', teacher: 'Johnson M.', room: 'D-105', groupId: 1 },
    { id: 5, day: 'Seshanba', time: '10:00-11:20', subject: 'Algoritm', teacher: 'Karimov A.', room: 'A-401', groupId: 1 },
    { id: 6, day: 'Chorshanba', time: '08:30-09:50', subject: 'Ma\'lumotlar bazasi', teacher: 'Normatov U.', room: 'B-302', groupId: 1 },
    { id: 7, day: 'Chorshanba', time: '10:00-11:20', subject: 'Web dasturlash', teacher: 'Toshmatov I.', room: 'B-303', groupId: 1 },
    { id: 8, day: 'Payshanba', time: '08:30-09:50', subject: 'Matematika', teacher: 'Karimov A.', room: 'A-401', groupId: 1 },
    { id: 9, day: 'Payshanba', time: '10:00-11:20', subject: 'Jismoniy tarbiya', teacher: 'Salimov B.', room: 'Sport zal', groupId: 1 },
    { id: 10, day: 'Juma', time: '08:30-09:50', subject: 'Dasturlash', teacher: 'Toshmatov I.', room: 'B-302', groupId: 1 },
    { id: 11, day: 'Juma', time: '10:00-11:20', subject: 'Falsafa', teacher: 'Xolmatov R.', room: 'C-401', groupId: 1 },
  ])

  // Davomat yozuvlari
  const attendanceRecords = ref([
    // Matematika - Dushanba
    { id: 1, studentId: 1, date: '2024-01-22', subject: 'Matematika', status: 'present', note: '' },
    { id: 2, studentId: 2, date: '2024-01-22', subject: 'Matematika', status: 'present', note: '' },
    { id: 3, studentId: 3, date: '2024-01-22', subject: 'Matematika', status: 'late', note: 'Transport muammosi' },
    { id: 4, studentId: 4, date: '2024-01-22', subject: 'Matematika', status: 'absent', note: '' },
    { id: 5, studentId: 5, date: '2024-01-22', subject: 'Matematika', status: 'present', note: '' },
    // Dasturlash - Dushanba
    { id: 6, studentId: 1, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
    { id: 7, studentId: 2, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
    { id: 8, studentId: 3, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
    { id: 9, studentId: 4, date: '2024-01-22', subject: 'Dasturlash', status: 'absent', note: '' },
    { id: 10, studentId: 5, date: '2024-01-22', subject: 'Dasturlash', status: 'present', note: '' },
    // Previous days...
    { id: 11, studentId: 1, date: '2024-01-21', subject: 'Ingliz tili', status: 'present', note: '' },
    { id: 12, studentId: 2, date: '2024-01-21', subject: 'Ingliz tili', status: 'late', note: '' },
    { id: 13, studentId: 3, date: '2024-01-21', subject: 'Ingliz tili', status: 'present', note: '' },
    { id: 14, studentId: 4, date: '2024-01-21', subject: 'Ingliz tili', status: 'present', note: '' },
    { id: 15, studentId: 5, date: '2024-01-21', subject: 'Ingliz tili', status: 'absent', note: 'Kasallik' },
  ])

  // Hisobotlar
  const reports = ref([
    { id: 1, title: 'Yanvar oyi davomat hisoboti', type: 'attendance', groupId: 1, createdBy: 2, date: '2024-01-31', status: 'completed' },
    { id: 2, title: 'KI_25-04 guruh haftalik hisoboti', type: 'weekly', groupId: 1, createdBy: 2, date: '2024-01-28', status: 'completed' },
    { id: 3, title: 'Dekabr oyi yakuniy hisobot', type: 'monthly', groupId: 1, createdBy: 2, date: '2024-12-31', status: 'completed' },
  ])

  // Push bildirishnomalar
  const notifications = ref([
    { id: 1, title: 'Tizimga xush kelibsiz!', message: 'Uni Control tizimiga muvaffaqiyatli kirdingiz.', date: '2024-01-22', read: false },
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

  const getAttendanceByDate = computed(() => (date, groupId) => {
    const groupStudents = students.value.filter(s => s.groupId === groupId).map(s => s.id)
    return attendanceRecords.value.filter(a => a.date === date && groupStudents.includes(a.studentId))
  })

  const calculateContractPercentage = (paidAmount, groupId) => {
    const group = groups.value.find(g => g.id === groupId)
    if (!group) return 0
    return Math.round((paidAmount / group.contractAmount) * 100)
  }

  // Actions
  const addStudent = (student) => {
    const newId = Math.max(...students.value.map(s => s.id)) + 1
    const newStudentId = `ST-2024-${String(newId).padStart(3, '0')}`
    students.value.push({
      ...student,
      id: newId,
      studentId: newStudentId
    })
  }

  const updateStudent = (id, updates) => {
    const index = students.value.findIndex(s => s.id === id)
    if (index !== -1) {
      // studentId va name o'zgartirilmaydi
      const { studentId, name, ...allowedUpdates } = updates
      students.value[index] = { ...students.value[index], ...allowedUpdates }
    }
  }

  const updateStudentFull = (id, updates) => {
    const index = students.value.findIndex(s => s.id === id)
    if (index !== -1) {
      students.value[index] = { ...students.value[index], ...updates }
    }
  }

  const addGroup = (group) => {
    const newId = Math.max(...groups.value.map(g => g.id)) + 1
    groups.value.push({ ...group, id: newId })
  }

  const updateGroupContract = (groupId, amount) => {
    const index = groups.value.findIndex(g => g.id === groupId)
    if (index !== -1) {
      groups.value[index].contractAmount = amount
    }
  }

  const assignGroupLeader = (groupId, studentId) => {
    const groupIndex = groups.value.findIndex(g => g.id === groupId)
    const group = groups.value[groupIndex]
    
    // Eski sardorni oddiy talabaga aylantirish
    if (group && group.leaderId) {
      const oldLeaderIndex = students.value.findIndex(s => s.id === group.leaderId)
      if (oldLeaderIndex !== -1) {
        students.value[oldLeaderIndex].role = 'student'
      }
    }
    
    // Yangi sardorni belgilash
    if (groupIndex !== -1) {
      const student = students.value.find(s => s.id === studentId)
      groups.value[groupIndex].leaderId = studentId
      groups.value[groupIndex].leaderName = student?.name || ''
    }
    const studentIndex = students.value.findIndex(s => s.id === studentId)
    if (studentIndex !== -1) {
      students.value[studentIndex].role = 'leader'
    }
  }

  // Sardorlikni olib tashlash
  const removeGroupLeader = (groupId) => {
    const groupIndex = groups.value.findIndex(g => g.id === groupId)
    if (groupIndex !== -1) {
      const leaderId = groups.value[groupIndex].leaderId
      if (leaderId) {
        const studentIndex = students.value.findIndex(s => s.id === leaderId)
        if (studentIndex !== -1) {
          students.value[studentIndex].role = 'student'
        }
      }
      groups.value[groupIndex].leaderId = null
      groups.value[groupIndex].leaderName = ''
    }
  }

  // Guruh holatini o'zgartirish (yoqish/o'chirish)
  const toggleGroupStatus = (groupId) => {
    const index = groups.value.findIndex(g => g.id === groupId)
    if (index !== -1) {
      groups.value[index].isActive = !groups.value[index].isActive
    }
  }

  // Guruh holatini tekshirish
  const isGroupActive = (groupName) => {
    const group = groups.value.find(g => g.name === groupName)
    return group ? group.isActive : false
  }

  // Excel'dan guruh va talabalarni import qilish
  const importFromExcel = (data) => {
    // data = [{ group: 'KI_25-04', faculty: 'Kompyuter injiniringi', students: [...] }, ...]
    data.forEach(item => {
      // Guruh mavjudligini tekshirish
      let group = groups.value.find(g => g.name === item.group)
      
      if (!group) {
        // Yangi guruh qo'shish
        const newGroupId = groups.value.length > 0 ? Math.max(...groups.value.map(g => g.id)) + 1 : 1
        group = {
          id: newGroupId,
          name: item.group,
          faculty: item.faculty || 'Noma\'lum',
          year: item.year || 1,
          leaderId: null,
          leaderName: '',
          contractAmount: item.contractAmount || 18411000,
          isActive: true
        }
        groups.value.push(group)
      }
      
      // Talabalarni qo'shish
      if (item.students && Array.isArray(item.students)) {
        item.students.forEach(studentData => {
          // Talaba mavjudligini tekshirish (studentId bo'yicha)
          const existingStudent = students.value.find(s => s.studentId === studentData.studentId)
          if (!existingStudent) {
            const newId = students.value.length > 0 ? Math.max(...students.value.map(s => s.id)) + 1 : 1
            students.value.push({
              id: newId,
              studentId: studentData.studentId || `ST-${Date.now()}-${newId}`,
              name: studentData.name,
              phone: studentData.phone || '',
              address: studentData.address || '',
              commute: studentData.commute || '',
              groupId: group.id,
              group: group.name,
              contractPaid: studentData.contractPaid || 0,
              passport: studentData.passport || '',
              jshshir: studentData.jshshir || '',
              birthDate: studentData.birthDate || '',
              role: 'student',
              avatar: null,
              email: studentData.email || '',
              password: studentData.password || '123456'
            })
          }
        })
      }
    })
  }

  // Talaba parolini yangilash
  const updateStudentPassword = (studentId, newPassword) => {
    const student = students.value.find(s => s.id === studentId || s.studentId === studentId)
    if (student) {
      student.password = newPassword
      return true
    }
    return false
  }

  // Talaba ID bo'yicha topish
  const findStudentByStudentId = (studentId) => {
    return students.value.find(s => s.studentId === studentId)
  }

  const addAttendanceRecord = (record) => {
    const newId = Math.max(...attendanceRecords.value.map(a => a.id)) + 1
    attendanceRecords.value.push({ ...record, id: newId })
  }

  const updateAttendanceRecord = (id, updates) => {
    const index = attendanceRecords.value.findIndex(a => a.id === id)
    if (index !== -1) {
      attendanceRecords.value[index] = { ...attendanceRecords.value[index], ...updates }
    }
  }

  const addScheduleItem = (item) => {
    const newId = Math.max(...schedule.value.map(s => s.id)) + 1
    schedule.value.push({ ...item, id: newId })
  }

  const updateScheduleItem = (id, updates) => {
    const index = schedule.value.findIndex(s => s.id === id)
    if (index !== -1) {
      schedule.value[index] = { ...schedule.value[index], ...updates }
    }
  }

  const deleteScheduleItem = (id) => {
    const index = schedule.value.findIndex(s => s.id === id)
    if (index !== -1) {
      schedule.value.splice(index, 1)
    }
  }

  const addReport = (report) => {
    const newId = Math.max(...reports.value.map(r => r.id)) + 1
    reports.value.push({ ...report, id: newId, date: new Date().toISOString().split('T')[0] })
  }

  const addNotification = (notification) => {
    const newId = Math.max(...notifications.value.map(n => n.id), 0) + 1
    notifications.value.unshift({ 
      ...notification, 
      id: newId, 
      createdAt: new Date().toISOString()
    })
  }

  const deleteNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  const sendNotification = (notification) => {
    const newId = Math.max(...notifications.value.map(n => n.id)) + 1
    notifications.value.unshift({ ...notification, id: newId, date: new Date().toISOString().split('T')[0], read: false })
  }

  const updateGroup = (id, updates) => {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value[index] = { ...groups.value[index], ...updates }
    }
  }

  const deleteGroup = (id) => {
    const index = groups.value.findIndex(g => g.id === id)
    if (index !== -1) {
      groups.value.splice(index, 1)
    }
  }

  const deleteStudent = (id) => {
    const index = students.value.findIndex(s => s.id === id)
    if (index !== -1) {
      students.value.splice(index, 1)
    }
  }

  const importStudentsFromExcel = (studentsData) => {
    studentsData.forEach(student => {
      addStudent(student)
    })
  }

  // Statistikalar
  const getStatistics = computed(() => {
    const totalStudents = students.value.length
    const totalGroups = groups.value.length
    
    const presentCount = attendanceRecords.value.filter(a => a.status === 'present').length
    const totalRecords = attendanceRecords.value.length
    const attendanceRate = totalRecords > 0 ? Math.round((presentCount / totalRecords) * 100) : 0
    
    const totalContract = students.value.reduce((sum, s) => {
      const group = groups.value.find(g => g.id === s.groupId)
      return sum + (group?.contractAmount || 0)
    }, 0)
    
    const paidContract = students.value.reduce((sum, s) => sum + s.contractPaid, 0)
    const contractRate = totalContract > 0 ? Math.round((paidContract / totalContract) * 100) : 0

    return {
      totalStudents,
      totalGroups,
      attendanceRate,
      contractRate,
      totalContract,
      paidContract
    }
  })

  return {
    groups,
    students,
    schedule,
    attendanceRecords,
    reports,
    notifications,
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
    getStatistics
  }
})
