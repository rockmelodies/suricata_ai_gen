#!/usr/bin/env python
# encoding: utf-8
# Database management for Suricata Rule Generator

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_path='suricata_rules.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vuln_name TEXT NOT NULL,
                vuln_type TEXT,
                description TEXT,
                original_rule TEXT NOT NULL,
                current_rule TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'draft'
            )
        ''')
        
        # Optimization history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER NOT NULL,
                original_rule TEXT NOT NULL,
                optimized_rule TEXT NOT NULL,
                feedback TEXT,
                ai_suggestion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rule_id) REFERENCES rules(id)
            )
        ''')
        
        # Validation results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER NOT NULL,
                pcap_path TEXT NOT NULL,
                matched BOOLEAN NOT NULL,
                alert_count INTEGER DEFAULT 0,
                details TEXT,
                sid_stats TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rule_id) REFERENCES rules(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_vuln_name ON rules(vuln_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_status ON rules(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_optimization_rule_id ON optimization_history(rule_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_validation_rule_id ON validation_results(rule_id)')
        
        conn.commit()
        conn.close()
    
    def insert_rule(self, vuln_name: str, original_rule: str, current_rule: str, 
                   vuln_type: str = '', description: str = '') -> int:
        """Insert new rule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rules (vuln_name, vuln_type, description, original_rule, current_rule)
            VALUES (?, ?, ?, ?, ?)
        ''', (vuln_name, vuln_type, description, original_rule, current_rule))
        
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rule_id
    
    def update_rule(self, rule_id: int, current_rule: str, status: str = None):
        """Update rule content and status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                UPDATE rules 
                SET current_rule = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (current_rule, status, rule_id))
        else:
            cursor.execute('''
                UPDATE rules 
                SET current_rule = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (current_rule, rule_id))
        
        conn.commit()
        conn.close()
    
    def get_rule_by_id(self, rule_id: int) -> Optional[Dict]:
        """Get rule by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rules WHERE id = ?', (rule_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_rules(self, page: int = 1, per_page: int = 20) -> List[Dict]:
        """Get all rules with pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT * FROM rules 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_rules_count(self) -> int:
        """Get total count of rules"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM rules')
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
    
    def insert_optimization_history(self, rule_id: int, original_rule: str, 
                                    optimized_rule: str, feedback: str = '', 
                                    ai_suggestion: str = '') -> int:
        """Insert optimization history record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO optimization_history 
            (rule_id, original_rule, optimized_rule, feedback, ai_suggestion)
            VALUES (?, ?, ?, ?, ?)
        ''', (rule_id, original_rule, optimized_rule, feedback, ai_suggestion))
        
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return history_id
    
    def get_optimization_history(self, rule_id: int) -> List[Dict]:
        """Get optimization history for a rule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM optimization_history 
            WHERE rule_id = ? 
            ORDER BY created_at DESC
        ''', (rule_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def insert_validation_result(self, rule_id: int, pcap_path: str, matched: bool, 
                                 alert_count: int = 0, details: str = '', 
                                 sid_stats: str = '') -> int:
        """Insert validation result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO validation_results 
            (rule_id, pcap_path, matched, alert_count, details, sid_stats)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (rule_id, pcap_path, matched, alert_count, details, sid_stats))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return result_id
    
    def get_validation_results(self, rule_id: int) -> List[Dict]:
        """Get validation results for a rule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM validation_results 
            WHERE rule_id = ? 
            ORDER BY created_at DESC
        ''', (rule_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
