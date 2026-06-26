import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('data/tokyo.db')
        self.c = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # ====== التحذيرات ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reason TEXT,
            moderator_id INTEGER,
            timestamp TEXT
        )''')
        
        # ====== الأدمن ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )''')
        
        # ====== المستويات ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS levels (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            total_messages INTEGER DEFAULT 0
        )''')
        
        # ====== التكتات ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS tickets (
            channel_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            status TEXT DEFAULT 'open',
            assigned_to INTEGER DEFAULT NULL,
            created_at TEXT
        )''')
        
        # ====== الردود التلقائية ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS autoreply (
            trigger TEXT PRIMARY KEY,
            response TEXT
        )''')
        
        # ====== نشاط الفويس ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS voice_activity (
            user_id INTEGER PRIMARY KEY,
            total_minutes INTEGER DEFAULT 0,
            last_join TEXT
        )''')
        
        # ====== الاقتراحات ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            suggestion TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            message_id INTEGER
        )''')
        
        # ====== السحوبات ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS giveaways (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER,
            prize TEXT,
            winners INTEGER,
            end_time TEXT,
            participants TEXT DEFAULT '',
            message_id INTEGER
        )''')
        
        # ====== الرومات المؤقتة ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS temp_channels (
            channel_id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            created_at TEXT
        )''')
        
        self.conn.commit()
    
    # ====== دوال مساعدة ======
    
    # --- التحذيرات ---
    def add_warning(self, user_id, reason, moderator_id):
        self.c.execute(
            "INSERT INTO warnings (user_id, reason, moderator_id, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, reason, moderator_id, datetime.now().isoformat())
        )
        self.conn.commit()
        return self.c.lastrowid
    
    def get_warnings(self, user_id):
        self.c.execute("SELECT * FROM warnings WHERE user_id = ? ORDER BY id DESC", (user_id,))
        return self.c.fetchall()
    
    def delete_warning(self, warn_id, user_id):
        self.c.execute("DELETE FROM warnings WHERE id = ? AND user_id = ?", (warn_id, user_id))
        self.conn.commit()
    
    # --- الأدمن ---
    def is_admin(self, user_id):
        self.c.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
        return self.c.fetchone() is not None
    
    def add_admin(self, user_id):
        self.c.execute("INSERT OR IGNORE INTO admins VALUES (?)", (user_id,))
        self.conn.commit()
    
    def remove_admin(self, user_id):
        self.c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def get_admins(self):
        self.c.execute("SELECT user_id FROM admins")
        return [row[0] for row in self.c.fetchall()]
    
    # --- المستويات ---
    def get_level_data(self, user_id):
        self.c.execute("SELECT xp, level FROM levels WHERE user_id = ?", (user_id,))
        return self.c.fetchone()
    
    def update_level(self, user_id, xp, level):
        self.c.execute(
            "INSERT INTO levels (user_id, xp, level) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET xp = ?, level = ?",
            (user_id, xp, level, xp, level)
        )
        self.conn.commit()
    
    def get_leaderboard(self, limit=10):
        self.c.execute("SELECT user_id, level, xp FROM levels ORDER BY level DESC, xp DESC LIMIT ?", (limit,))
        return self.c.fetchall()
    
    # --- التكتات ---
    def create_ticket(self, channel_id, user_id):
        self.c.execute(
            "INSERT INTO tickets (channel_id, user_id, created_at) VALUES (?, ?, ?)",
            (channel_id, user_id, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def close_ticket(self, channel_id):
        self.c.execute("UPDATE tickets SET status = 'closed' WHERE channel_id = ?", (channel_id,))
        self.conn.commit()
    
    def assign_ticket(self, channel_id, admin_id):
        self.c.execute("UPDATE tickets SET assigned_to = ? WHERE channel_id = ?", (admin_id, channel_id))
        self.conn.commit()
    
    def unassign_ticket(self, channel_id):
        self.c.execute("UPDATE tickets SET assigned_to = NULL WHERE channel_id = ?", (channel_id,))
        self.conn.commit()
    
    def get_ticket(self, channel_id):
        self.c.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel_id,))
        return self.c.fetchone()
    
    def get_open_tickets(self):
        self.c.execute("SELECT * FROM tickets WHERE status = 'open'")
        return self.c.fetchall()
    
    # --- الردود التلقائية ---
    def add_reply(self, trigger, response):
        self.c.execute("INSERT OR REPLACE INTO autoreply VALUES (?, ?)", (trigger.lower(), response))
        self.conn.commit()
    
    def delete_reply(self, trigger):
        self.c.execute("DELETE FROM autoreply WHERE trigger = ?", (trigger.lower(),))
        self.conn.commit()
    
    def get_reply(self, trigger):
        self.c.execute("SELECT response FROM autoreply WHERE trigger = ?", (trigger.lower(),))
        result = self.c.fetchone()
        return result[0] if result else None
    
    def get_all_replies(self):
        self.c.execute("SELECT * FROM autoreply")
        return self.c.fetchall()
    
    # --- الاقتراحات ---
    def add_suggestion(self, user_id, suggestion):
        self.c.execute(
            "INSERT INTO suggestions (user_id, suggestion) VALUES (?, ?)",
            (user_id, suggestion)
        )
        self.conn.commit()
        return self.c.lastrowid
    
    def vote_suggestion(self, suggestion_id, vote_type):
        if vote_type == 'up':
            self.c.execute("UPDATE suggestions SET upvotes = upvotes + 1 WHERE id = ?", (suggestion_id,))
        elif vote_type == 'down':
            self.c.execute("UPDATE suggestions SET downvotes = downvotes + 1 WHERE id = ?", (suggestion_id,))
        self.conn.commit()
    
    # --- السحوبات ---
    def create_giveaway(self, channel_id, prize, winners, end_time, message_id):
        self.c.execute(
            "INSERT INTO giveaways (channel_id, prize, winners, end_time, message_id) VALUES (?, ?, ?, ?, ?)",
            (channel_id, prize, winners, end_time, message_id)
        )
        self.conn.commit()
        return self.c.lastrowid
    
    def add_participant(self, giveaway_id, user_id):
        self.c.execute("SELECT participants FROM giveaways WHERE id = ?", (giveaway_id,))
        result = self.c.fetchone()
        if result:
            participants = result[0].split(',') if result[0] else []
            if str(user_id) not in participants:
                participants.append(str(user_id))
                self.c.execute(
                    "UPDATE giveaways SET participants = ? WHERE id = ?",
                    (','.join(participants), giveaway_id)
                )
                self.conn.commit()
