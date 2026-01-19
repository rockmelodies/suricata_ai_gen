#!/usr/bin/env python
# encoding: utf-8
"""
User Model - 用户数据模型
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json


class UserModel:
    """用户模型"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_table()
    
    def init_table(self):
        """初始化用户表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                avatar TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 创建默认管理员账户
        self.create_default_admin()
    
    def create_default_admin(self):
        """创建默认管理员账户"""
        try:
            admin = self.get_by_username('admin')
            if not admin:
                self.create_user(
                    username='admin',
                    password='admin123',
                    email='admin@example.com',
                    role='admin'
                )
                print("✓ 默认管理员账户已创建 (username: admin, password: admin123)")
        except Exception as e:
            print(f"创建默认管理员失败: {e}")
    
    def create_user(self, username, password, email=None, role='user'):
        """创建用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"用户名或邮箱已存在: {str(e)}")
        finally:
            conn.close()
    
    def get_by_id(self, user_id):
        """根据ID获取用户"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_by_username(self, username):
        """根据用户名获取用户"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def verify_password(self, username, password):
        """验证密码"""
        user = self.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    def get_all_users(self, page=1, per_page=20):
        """获取所有用户（分页）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT id, username, email, role, is_active, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        users = [dict(row) for row in cursor.fetchall()]
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) as total FROM users')
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    def update_user(self, user_id, **kwargs):
        """更新用户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        allowed_fields = ['username', 'email', 'role', 'is_active']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                values.append(kwargs[field])
        
        if not updates:
            conn.close()
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(sql, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            raise ValueError("用户名或邮箱已存在")
    
    def update_password(self, user_id, new_password):
        """更新密码"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_user(self, user_id):
        """删除用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def to_safe_dict(self, user):
        """转换为安全的字典（移除敏感信息）"""
        if not user:
            return None
        
        safe_user = user.copy()
        safe_user.pop('password_hash', None)
        return safe_user
