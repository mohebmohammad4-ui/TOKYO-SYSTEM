import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.conn = sqlite3.connect('data/tokyo.db')
        self.c = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # ====== الجداول الأساسية ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reason TEXT,
            moderator_id INTEGER,
            timestamp TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS levels (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            total_messages INTEGER DEFAULT 0
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS tickets (
            channel_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            status TEXT DEFAULT 'open',
            assigned_to INTEGER DEFAULT NULL,
            created_at TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS autoreply (
            trigger TEXT PRIMARY KEY,
            response TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS voice_activity (
            user_id INTEGER PRIMARY KEY,
            total_minutes INTEGER DEFAULT 0,
            last_join TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS auto_roles (
            level INTEGER PRIMARY KEY,
            role_id INTEGER
        )''')
        
        # ====== الجداول الجديدة ======
        self.c.execute('''CREATE TABLE IF NOT EXISTS mod_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            target_id INTEGER,
            moderator_id INTEGER,
            reason TEXT,
            timestamp TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS self_roles (
            role_id INTEGER PRIMARY KEY,
            emoji TEXT
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT,
            identifier TEXT,
            channel_id INTEGER
        )''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS starboard_messages (
            message_id INTEGER PRIMARY KEY,
            content TEXT,
            author_id INTEGER,
            stars INTEGER,
            timestamp TEXT
        )''')
        
        self.conn.commit()
    
    # ====== دوال الإعدادات ======
    def set_setting(self, key, value):
        if value is None:
            self.c.execute("DELETE FROM settings WHERE key = ?", (key,))
        else:
            self.c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        self.c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.c.fetchone()
        return result[0] if result else default
    
    def get_all_settings(self):
        self.c.execute("SELECT * FROM settings")
        return {key: value for key, value in self.c.fetchall()}
    
    # ====== دوال الرتب التلقائية ======
    def add_auto_role(self, level, role_id):
        self.c.execute("INSERT OR REPLACE INTO auto_roles (level, role_id) VALUES (?, ?)", (level, role_id))
        self.conn.commit()
    
    def get_auto_roles(self):
        self.c.execute("SELECT level, role_id FROM auto_roles ORDER BY level ASC")
        return self.c.fetchall()
    
    def remove_auto_role(self, level):
        self.c.execute("DELETE FROM auto_roles WHERE level = ?", (level,))
        self.conn.commit()
    
    # ====== دوال الأدمن ======
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
    
    # ====== دوال المستويات ======
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
    
    # ====== دوال التحذيرات ======
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
    
    # ====== دوال التكتات ======
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
    
    # ====== دوال الردود التلقائية ======
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
    
    # ====== دوال سجل الإدارة ======
    def add_mod_action(self, action, target_id, moderator_id, reason):
        self.c.execute(
            "INSERT INTO mod_actions (action, target_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
            (action, target_id, moderator_id, reason, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_mod_actions(self, limit=50):
        self.c.execute("SELECT * FROM mod_actions ORDER BY id DESC LIMIT ?", (limit,))
        return self.c.fetchall()
    
    # ====== دوال الرتب الاختيارية ======
    def add_self_role(self, role_id, emoji=None):
        self.c.execute("INSERT OR REPLACE INTO self_roles (role_id, emoji) VALUES (?, ?)", (role_id, emoji))
        self.conn.commit()
    
    def remove_self_role(self, role_id):
        self.c.execute("DELETE FROM self_roles WHERE role_id = ?", (role_id,))
        self.conn.commit()
    
    def get_self_roles(self):
        self.c.execute("SELECT role_id, emoji FROM self_roles")
        return self.c.fetchall()
    
    def is_self_role(self, role_id):
        self.c.execute("SELECT * FROM self_roles WHERE role_id = ?", (role_id,))
        return self.c.fetchone() is not None
    
    # ====== دوال الإشعارات ======
    def add_notification(self, service, identifier, channel_id):
        self.c.execute(
            "INSERT OR REPLACE INTO notifications (service, identifier, channel_id) VALUES (?, ?, ?)",
            (service, identifier, channel_id)
        )
        self.conn.commit()
    
    def remove_notification(self, service, identifier):
        self.c.execute("DELETE FROM notifications WHERE service = ? AND identifier = ?", (service, identifier))
        self.conn.commit()
    
    def get_notifications(self, service=None):
        if service:
            self.c.execute("SELECT * FROM notifications WHERE service = ?", (service,))
        else:
            self.c.execute("SELECT * FROM notifications")
        return self.c.fetchall()
    
    # ====== دوال Starboard ======
    def add_starred_message(self, message_id, content, author_id, stars):
        self.c.execute(
            "INSERT OR REPLACE INTO starboard_messages (message_id, content, author_id, stars, timestamp) VALUES (?, ?, ?, ?, ?)",
            (message_id, content, author_id, stars, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_starred_messages(self, limit=10):
        self.c.execute("SELECT * FROM starboard_messages ORDER BY timestamp DESC LIMIT ?", (limit,))
        return self.c.fetchall()
