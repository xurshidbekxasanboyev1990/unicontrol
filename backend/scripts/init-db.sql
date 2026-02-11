-- ========================================
-- UniControl - Database Initialization
-- ========================================
-- Bu fayl PostgreSQL konteyneri birinchi marta ishga tushganda avtomatik bajariladi
-- Jadvallar yaratiladi va boshlang'ich ma'lumotlar qo'shiladi

-- ============================================
-- Create user_role ENUM (if not exists via DO block)
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('student', 'leader', 'admin', 'superadmin');
    END IF;
END$$;

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    avatar VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_first_login BOOLEAN DEFAULT FALSE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    refresh_token VARCHAR(500),
    settings TEXT,
    device_tokens JSON
);

-- ============================================
-- GROUPS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    faculty VARCHAR(255),
    course_year INTEGER DEFAULT 1,
    education_type VARCHAR(50) DEFAULT 'kunduzgi',
    contract_amount DECIMAL(15,2) DEFAULT 0,
    leader_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STUDENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(100) UNIQUE,
    hemis_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    passport VARCHAR(20),
    jshshir VARCHAR(20),
    birth_date DATE,
    gender VARCHAR(10),
    contract_amount DECIMAL(15,2) DEFAULT 0,
    contract_paid DECIMAL(15,2) DEFAULT 0,
    commute VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ATTENDANCE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'present',
    reason TEXT,
    subject VARCHAR(255),
    lesson_number INTEGER,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SCHEDULE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL,
    subject VARCHAR(255) NOT NULL,
    teacher VARCHAR(255),
    room VARCHAR(50),
    start_time TIME,
    end_time TIME,
    lesson_type VARCHAR(50) DEFAULT 'lecture',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    recipient_type VARCHAR(50) DEFAULT 'all',
    recipient_id INTEGER,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CLUBS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    teacher VARCHAR(255),
    phone VARCHAR(50),
    schedule VARCHAR(255),
    room VARCHAR(50),
    price DECIMAL(15,2) DEFAULT 0,
    max_students INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SUBJECTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    credits INTEGER DEFAULT 0,
    hours INTEGER DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DIRECTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS directions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    faculty VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TOURNAMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tournaments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    start_date DATE,
    end_date DATE,
    registration_deadline DATE,
    location VARCHAR(255),
    prize VARCHAR(255),
    max_participants INTEGER,
    status VARCHAR(50) DEFAULT 'upcoming',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TOURNAMENT REGISTRATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tournament_registrations (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, student_id)
);

-- ============================================
-- CANTEEN CATEGORIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS canteen_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CANTEEN MENU ITEMS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS canteen_menu_items (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES canteen_categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(15,2) NOT NULL,
    image_url VARCHAR(500),
    calories INTEGER,
    preparation_time INTEGER,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CANTEEN ORDERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS canteen_orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    student_id INTEGER REFERENCES students(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CANTEEN ORDER ITEMS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS canteen_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES canteen_orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES canteen_menu_items(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    price DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SYSTEM LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SYSTEM SETTINGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- FAQS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category_id INTEGER,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_students_group_id ON students(group_id);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_schedules_group_id ON schedules(group_id);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- ============================================
-- SEED DATA - Super Admin
-- ============================================
-- Password: superadmin123 (bcrypt hash)
INSERT INTO users (login, email, password_hash, role, name, phone, is_active, is_verified, is_first_login)
VALUES (
    'superadmin',
    'superadmin@unicontrol.uz',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCJzPvX.q',
    'SUPERADMIN',
    'Super Admin',
    '+998901234567',
    TRUE,
    TRUE,
    FALSE
) ON CONFLICT (login) DO NOTHING;

-- ============================================
-- SEED DATA - Admin
-- ============================================
-- Password: admin123 (bcrypt hash)
INSERT INTO users (login, email, password_hash, role, name, phone, is_active, is_verified, is_first_login)
VALUES (
    'admin',
    'admin@unicontrol.uz',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiABCDEFGH.q',
    'ADMIN',
    'Administrator',
    '+998901111111',
    TRUE,
    TRUE,
    FALSE
) ON CONFLICT (login) DO NOTHING;

-- ============================================
-- SEED DATA - Default Settings
-- ============================================
INSERT INTO system_settings (key, value, type, description) VALUES
    ('system_name', 'UniControl', 'string', 'Tizim nomi'),
    ('university_name', 'KUAF', 'string', 'Universitet nomi'),
    ('academic_year', '2025-2026', 'string', 'O''quv yili'),
    ('semester', '2', 'string', 'Joriy semestr'),
    ('min_attendance', '70', 'number', 'Minimal davomat foizi'),
    ('late_threshold', '15', 'number', 'Kechikish chegarasi (daqiqa)')
ON CONFLICT (key) DO NOTHING;

-- ============================================
-- SEED DATA - Canteen Categories
-- ============================================
INSERT INTO canteen_categories (name, icon, sort_order) VALUES
    ('Birinchi taomlar', 'Soup', 1),
    ('Ikkinchi taomlar', 'UtensilsCrossed', 2),
    ('Salatlar', 'Salad', 3),
    ('Ichimliklar', 'Coffee', 4),
    ('Shirinliklar', 'Cake', 5)
ON CONFLICT DO NOTHING;

-- ============================================
-- DONE
-- ============================================
SELECT 'Database initialized successfully!' as status;
