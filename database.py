import sqlite3
from datetime import datetime, timedelta
from config import DB_FILE


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id       INTEGER PRIMARY KEY,
                username      TEXT,
                first_name    TEXT,
                goal          TEXT DEFAULT 'maintain',
                gender        TEXT,
                weight        REAL,
                height        REAL,
                age           INTEGER,
                notifications INTEGER DEFAULT 1,
                ai_provider   TEXT DEFAULT 'auto',
                is_banned     INTEGER DEFAULT 0,
                referrer_id   INTEGER,
                joined_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id     INTEGER PRIMARY KEY,
                plan        TEXT DEFAULT 'trial',
                expires_at  TIMESTAMP,
                stars_paid  INTEGER DEFAULT 0,
                trial_used  INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS progress (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                weight      REAL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS workouts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER,
                workout_type TEXT,
                note         TEXT,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS calories_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                calories    INTEGER,
                note        TEXT DEFAULT '',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS food_diary (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                meal_type   TEXT,
                food_name   TEXT,
                calories    INTEGER,
                protein     REAL DEFAULT 0,
                carbs       REAL DEFAULT 0,
                fats        REAL DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS water_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                ml          INTEGER,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS measurements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                chest       REAL,
                waist       REAL,
                hips        REAL,
                bicep       REAL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS payments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                plan        TEXT,
                stars       INTEGER,
                telegram_payment_id TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS bot_settings (
                key         TEXT PRIMARY KEY,
                value       TEXT
            );
            CREATE TABLE IF NOT EXISTS referrals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                bonus_days  INTEGER DEFAULT 7,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.conn.commit()
        self._init_settings()

    def _migrate(self):
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(users)").fetchall()]
        for col, defval in [
            ("is_banned", "0"),
            ("referrer_id", "NULL"),
            ("ai_provider", "'auto'"),
        ]:
            if col not in cols:
                self.conn.execute(f"ALTER TABLE users ADD COLUMN {col} {'INTEGER DEFAULT ' + defval if col != 'referrer_id' and col != 'ai_provider' else 'TEXT DEFAULT ' + defval}")
        sub_cols = [r[1] for r in self.conn.execute("PRAGMA table_info(subscriptions)").fetchall()]
        if "trial_used" not in sub_cols:
            self.conn.execute("ALTER TABLE subscriptions ADD COLUMN trial_used INTEGER DEFAULT 0")
        self.conn.commit()

    def _init_settings(self):
        defaults = {
            "trial_days": "3",
            "price_month_stars": "75",
            "price_3month_stars": "175",
            "price_year_stars": "499",
            "welcome_text": "👋 Добро пожаловать в FITNESS AI PRO!",
            "referral_bonus_days": "7",
        }
        for k, v in defaults.items():
            self.conn.execute("INSERT OR IGNORE INTO bot_settings(key,value) VALUES(?,?)", (k, v))
        self.conn.commit()

    # ── Настройки бота ────────────────────────────────────
    def get_setting(self, key: str, default="") -> str:
        row = self.conn.execute("SELECT value FROM bot_settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        self.conn.execute("INSERT OR REPLACE INTO bot_settings(key,value) VALUES(?,?)", (key, value))
        self.conn.commit()

    def get_all_settings(self) -> dict:
        rows = self.conn.execute("SELECT key, value FROM bot_settings").fetchall()
        return {r["key"]: r["value"] for r in rows}

    # ── Пользователи ─────────────────────────────────────
    def add_user(self, uid, username=None, first_name=None, referrer_id=None):
        self.conn.execute(
            'INSERT OR IGNORE INTO users(user_id, username, first_name, goal, referrer_id) VALUES(?,?,?,?,?)',
            (uid, username, first_name, 'maintain', referrer_id)
        )
        self.conn.commit()
        # Активируем trial если новый пользователь
        if not self.get_subscription(uid):
            trial_days = int(self.get_setting("trial_days", "3"))
            self._activate_trial(uid, trial_days)

    def _activate_trial(self, uid: int, days: int):
        expires = datetime.now() + timedelta(days=days)
        self.conn.execute('''
            INSERT OR IGNORE INTO subscriptions(user_id, plan, expires_at, trial_used)
            VALUES(?,?,?,?)
        ''', (uid, 'trial', expires.isoformat(), 1))
        self.conn.commit()

    def get_user(self, uid):
        row = self.conn.execute('SELECT * FROM users WHERE user_id=?', (uid,)).fetchone()
        return dict(row) if row else {}

    def update_user(self, uid, **kwargs):
        for k, v in kwargs.items():
            self.conn.execute(f'UPDATE users SET {k}=? WHERE user_id=?', (v, uid))
        self.conn.commit()

    def profile_complete(self, uid):
        u = self.get_user(uid)
        return bool(u.get('weight') and u.get('height') and u.get('age') and u.get('gender'))

    def get_all_users(self):
        rows = self.conn.execute('SELECT * FROM users ORDER BY joined_at DESC').fetchall()
        return [dict(r) for r in rows]

    def get_users_with_notifications(self):
        rows = self.conn.execute('SELECT user_id FROM users WHERE notifications=1 AND is_banned=0').fetchall()
        return [r['user_id'] for r in rows]

    def get_total_users(self):
        row = self.conn.execute('SELECT COUNT(*) as cnt FROM users').fetchone()
        return row['cnt'] if row else 0

    def get_new_users_today(self):
        today = datetime.now().strftime('%Y-%m-%d')
        row = self.conn.execute("SELECT COUNT(*) as cnt FROM users WHERE DATE(joined_at)=?", (today,)).fetchone()
        return row['cnt'] if row else 0

    def ban_user(self, uid: int):
        self.conn.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (uid,))
        self.conn.commit()

    def unban_user(self, uid: int):
        self.conn.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (uid,))
        self.conn.commit()

    def is_banned(self, uid: int) -> bool:
        row = self.conn.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,)).fetchone()
        return bool(row and row['is_banned'])

    # ── Подписки ─────────────────────────────────────────
    def get_subscription(self, uid):
        row = self.conn.execute('SELECT * FROM subscriptions WHERE user_id=?', (uid,)).fetchone()
        return dict(row) if row else None

    def is_active(self, uid) -> bool:
        """Подписка активна (trial или premium)"""
        if uid in [260182231]:  # admins always active
            return True
        sub = self.get_subscription(uid)
        if not sub:
            return False
        if sub['expires_at']:
            return datetime.fromisoformat(sub['expires_at']) > datetime.now()
        return False

    def is_premium(self, uid) -> bool:
        """Платная подписка (не trial)"""
        if uid in [260182231]:
            return True
        sub = self.get_subscription(uid)
        if not sub:
            return False
        if sub['plan'] == 'premium' and sub['expires_at']:
            return datetime.fromisoformat(sub['expires_at']) > datetime.now()
        return False

    def is_trial(self, uid) -> bool:
        sub = self.get_subscription(uid)
        if not sub:
            return False
        return sub['plan'] == 'trial' and self.is_active(uid)

    def days_left(self, uid) -> int:
        sub = self.get_subscription(uid)
        if not sub or not sub['expires_at']:
            return 0
        diff = datetime.fromisoformat(sub['expires_at']) - datetime.now()
        return max(0, diff.days)

    def activate_premium(self, uid, days: int, stars: int, payment_id: str = ''):
        existing = self.get_subscription(uid)
        if existing and existing['expires_at']:
            base = datetime.fromisoformat(existing['expires_at'])
            new_expires = (base if base > datetime.now() else datetime.now()) + timedelta(days=days)
        else:
            new_expires = datetime.now() + timedelta(days=days)

        self.conn.execute('''
            INSERT INTO subscriptions(user_id, plan, expires_at, stars_paid)
            VALUES(?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
                plan='premium',
                expires_at=excluded.expires_at,
                stars_paid=stars_paid+excluded.stars_paid
        ''', (uid, 'premium', new_expires.isoformat(), stars))

        if payment_id:
            plan_label = f"{days}d"
            self.conn.execute(
                'INSERT INTO payments(user_id, plan, stars, telegram_payment_id) VALUES(?,?,?,?)',
                (uid, plan_label, stars, payment_id)
            )
        self.conn.commit()

        # Бонус рефереру
        user = self.get_user(uid)
        if user.get('referrer_id') and stars > 0:
            bonus = int(self.get_setting("referral_bonus_days", "7"))
            self.grant_premium(user['referrer_id'], bonus)
            self.conn.execute(
                'INSERT OR IGNORE INTO referrals(referrer_id, referred_id, bonus_days) VALUES(?,?,?)',
                (user['referrer_id'], uid, bonus)
            )
            self.conn.commit()

        return new_expires

    def grant_premium(self, uid, days: int):
        existing = self.get_subscription(uid)
        if existing and existing['expires_at']:
            base = datetime.fromisoformat(existing['expires_at'])
            new_expires = (base if base > datetime.now() else datetime.now()) + timedelta(days=days)
        else:
            new_expires = datetime.now() + timedelta(days=days)
        self.conn.execute('''
            INSERT INTO subscriptions(user_id, plan, expires_at, stars_paid)
            VALUES(?,?,?,0)
            ON CONFLICT(user_id) DO UPDATE SET
                plan='premium', expires_at=excluded.expires_at
        ''', (uid, 'premium', new_expires.isoformat()))
        self.conn.commit()
        return new_expires

    def revoke_premium(self, uid):
        self.conn.execute(
            "UPDATE subscriptions SET plan='free', expires_at=NULL WHERE user_id=?", (uid,)
        )
        self.conn.commit()

    def get_premium_users_count(self):
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM subscriptions WHERE plan='premium' AND expires_at > ?",
            (datetime.now().isoformat(),)
        ).fetchone()
        return row['cnt'] if row else 0

    def get_trial_users_count(self):
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM subscriptions WHERE plan='trial' AND expires_at > ?",
            (datetime.now().isoformat(),)
        ).fetchone()
        return row['cnt'] if row else 0

    def get_all_payments(self, limit=50):
        rows = self.conn.execute(
            'SELECT p.*, u.username, u.first_name FROM payments p '
            'LEFT JOIN users u ON p.user_id=u.user_id ORDER BY p.created_at DESC LIMIT ?', (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_revenue_stars(self):
        row = self.conn.execute('SELECT SUM(stars) as total FROM payments').fetchone()
        return row['total'] or 0

    def get_revenue_today(self):
        today = datetime.now().strftime('%Y-%m-%d')
        row = self.conn.execute(
            "SELECT SUM(stars) as total FROM payments WHERE DATE(created_at)=?", (today,)
        ).fetchone()
        return row['total'] or 0

    # ── Вес ──────────────────────────────────────────────
    def add_weight(self, uid, weight):
        self.conn.execute('INSERT INTO progress(user_id, weight) VALUES(?,?)', (uid, weight))
        self.conn.execute('UPDATE users SET weight=? WHERE user_id=?', (weight, uid))
        self.conn.commit()

    def get_weight_history(self, uid, limit=10):
        rows = self.conn.execute(
            'SELECT weight, created_at FROM progress WHERE user_id=? ORDER BY created_at DESC LIMIT ?',
            (uid, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Тренировки ────────────────────────────────────────
    def add_workout(self, uid, workout_type, note=''):
        self.conn.execute(
            'INSERT INTO workouts(user_id, workout_type, note) VALUES(?,?,?)', (uid, workout_type, note)
        )
        self.conn.commit()

    def get_workout_history(self, uid, limit=10):
        rows = self.conn.execute(
            'SELECT workout_type, note, created_at FROM workouts WHERE user_id=? ORDER BY created_at DESC LIMIT ?',
            (uid, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_workout_count(self, uid):
        row = self.conn.execute('SELECT COUNT(*) as cnt FROM workouts WHERE user_id=?', (uid,)).fetchone()
        return row['cnt'] if row else 0

    def get_workout_streak(self, uid) -> int:
        rows = self.conn.execute(
            "SELECT DATE(created_at) as d FROM workouts WHERE user_id=? GROUP BY DATE(created_at) ORDER BY d DESC LIMIT 30",
            (uid,)
        ).fetchall()
        if not rows:
            return 0
        dates = [r['d'] for r in rows]
        streak = 0
        today = datetime.now().date()
        for i, d in enumerate(dates):
            expected = str(today - timedelta(days=i))
            if d == expected:
                streak += 1
            else:
                break
        return streak

    # ── Калории ───────────────────────────────────────────
    def add_calories(self, uid, calories, note=''):
        self.conn.execute('INSERT INTO calories_log(user_id, calories, note) VALUES(?,?,?)', (uid, calories, note))
        self.conn.commit()

    def get_calories_history(self, uid, limit=7):
        rows = self.conn.execute(
            'SELECT calories, note, created_at FROM calories_log WHERE user_id=? ORDER BY created_at DESC LIMIT ?',
            (uid, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_avg_calories(self, uid):
        row = self.conn.execute('SELECT AVG(calories) as avg FROM calories_log WHERE user_id=?', (uid,)).fetchone()
        return round(row['avg']) if row and row['avg'] else 0

    def get_today_calories(self, uid):
        today = datetime.now().strftime('%Y-%m-%d')
        row = self.conn.execute(
            "SELECT SUM(calories) as total FROM calories_log WHERE user_id=? AND DATE(created_at)=?",
            (uid, today)
        ).fetchone()
        return row['total'] or 0

    # ── Дневник питания ───────────────────────────────────
    def add_food_entry(self, uid, meal_type, food_name, calories, protein=0, carbs=0, fats=0):
        self.conn.execute(
            'INSERT INTO food_diary(user_id,meal_type,food_name,calories,protein,carbs,fats) VALUES(?,?,?,?,?,?,?)',
            (uid, meal_type, food_name, calories, protein, carbs, fats)
        )
        self.conn.commit()

    def get_today_diary(self, uid):
        today = datetime.now().strftime('%Y-%m-%d')
        rows = self.conn.execute(
            "SELECT * FROM food_diary WHERE user_id=? AND DATE(created_at)=? ORDER BY created_at",
            (uid, today)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Вода ─────────────────────────────────────────────
    def add_water(self, uid, ml: int):
        self.conn.execute('INSERT INTO water_log(user_id, ml) VALUES(?,?)', (uid, ml))
        self.conn.commit()

    def get_today_water(self, uid) -> int:
        today = datetime.now().strftime('%Y-%m-%d')
        row = self.conn.execute(
            "SELECT SUM(ml) as total FROM water_log WHERE user_id=? AND DATE(created_at)=?",
            (uid, today)
        ).fetchone()
        return row['total'] or 0

    # ── Замеры ────────────────────────────────────────────
    def add_measurement(self, uid, chest=None, waist=None, hips=None, bicep=None):
        self.conn.execute(
            'INSERT INTO measurements(user_id,chest,waist,hips,bicep) VALUES(?,?,?,?,?)',
            (uid, chest, waist, hips, bicep)
        )
        self.conn.commit()

    def get_measurements(self, uid, limit=5):
        rows = self.conn.execute(
            'SELECT * FROM measurements WHERE user_id=? ORDER BY created_at DESC LIMIT ?',
            (uid, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Рефералы ─────────────────────────────────────────
    def get_referral_count(self, uid) -> int:
        row = self.conn.execute('SELECT COUNT(*) as cnt FROM referrals WHERE referrer_id=?', (uid,)).fetchone()
        return row['cnt'] if row else 0

    def get_referral_bonus_days(self, uid) -> int:
        row = self.conn.execute('SELECT SUM(bonus_days) as total FROM referrals WHERE referrer_id=?', (uid,)).fetchone()
        return row['total'] or 0

    # ── Статистика ───────────────────────────────────────
    def get_stats(self, uid):
        weights = self.get_weight_history(uid, limit=2)
        return {
            'workouts_total': self.get_workout_count(uid),
            'avg_calories': self.get_avg_calories(uid),
            'weight_change': round(weights[0]['weight'] - weights[-1]['weight'], 1) if len(weights) >= 2 else None,
            'current_weight': weights[0]['weight'] if weights else None,
            'streak': self.get_workout_streak(uid),
            'today_water': self.get_today_water(uid),
        }
