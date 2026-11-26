# -*- coding: utf-8 -*-
"""OCR 数据访问层（mapper）：MySQL tb_ocr_task 读写（迁移自 storage.py）"""
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../py-genai-pg')))
from mysql_adapter import mysql_dsn, connect, rows as my_rows, one as my_one, run as my_run, execute_script

DSN = mysql_dsn('genai_ocr')


def conn():
    """兼容旧接口：返回 pymysql 连接"""
    import pymysql
    cfg = dict(DSN)
    cfg['cursorclass'] = pymysql.cursors.DictCursor
    return pymysql.connect(**cfg)


def init_db():
    execute_script(DSN, """
        CREATE TABLE IF NOT EXISTS tb_ocr_task(
          id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(512) NOT NULL,
          engine VARCHAR(64) DEFAULT 'auto', size INT DEFAULT 0,
          status VARCHAR(32) DEFAULT 'pending',
          text TEXT, error TEXT, cost_ms INT DEFAULT 0,
          prompt TEXT, image_path VARCHAR(1024),
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
        """)


def rows(sql, args=()):
    return my_rows(DSN, sql, args)


def run(sql, args=()):
    return my_run(DSN, sql, args)


def one(sql, args=()):
    return my_one(DSN, sql, args)


def delete(tid: int):
    run("DELETE FROM tb_ocr_task WHERE id=?", (tid,))
