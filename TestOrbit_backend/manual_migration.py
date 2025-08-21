"""
手动处理数据库迁移，将 ApiData 表中的 project_id 字段替换为 env_id 字段。
由于存在 Django 迁移系统的问题，我们直接使用 SQL 进行修改。
"""

import os
import django
import sys
from django.conf import settings
from django.db import connection

# 设置环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

def execute_migration():
    """执行数据库迁移操作"""
    print("开始执行数据库迁移...")
    
    # 使用Django的数据库连接
    conn = connection
    
    try:
        with conn.cursor() as cursor:
            print("检查 env_id 列是否已存在...")
            cursor.execute("SHOW COLUMNS FROM api_data LIKE 'env_id'")
            if cursor.fetchone():
                print("env_id 列已存在，跳过创建...")
            else:
                print("添加 env_id 列...")
                cursor.execute("ALTER TABLE api_data ADD COLUMN env_id smallint NULL;")
                print("成功添加 env_id 列")
            
            print("检查 project_id 列是否仍然存在...")
            cursor.execute("SHOW COLUMNS FROM api_data LIKE 'project_id'")
            if cursor.fetchone():
                print("将 project_id 的值复制到 env_id...")
                cursor.execute("UPDATE api_data SET env_id = project_id;")
                print("成功复制数据")
            else:
                print("project_id 列已不存在，跳过数据复制...")
            
            print("检查并删除可能存在的外键约束...")
            cursor.execute("""
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' 
            AND TABLE_NAME = 'api_data' 
            AND TABLE_SCHEMA = DATABASE();
            """)
            
            fk_constraints = cursor.fetchall()
            for constraint in fk_constraints:
                constraint_name = constraint[0]
                print(f"检查外键约束: {constraint_name}")
                
                # 检查约束是否与 project_id 相关
                cursor.execute("""
                SELECT COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE CONSTRAINT_NAME = %s
                AND TABLE_NAME = 'api_data'
                AND TABLE_SCHEMA = DATABASE();
                """, (constraint_name,))
                
                columns = cursor.fetchall()
                for column in columns:
                    if 'project_id' in column[0]:
                        print(f"删除与 project_id 相关的外键约束: {constraint_name}")
                        try:
                            cursor.execute(f"ALTER TABLE api_data DROP FOREIGN KEY `{constraint_name}`;")
                            print(f"成功删除外键约束: {constraint_name}")
                        except Exception as e:
                            print(f"删除外键约束 {constraint_name} 时出错: {e}")
                        break
            
            print("删除唯一性约束...")
            try:
                # 查找所有包含 project_id 的唯一性约束
                cursor.execute("""
                SELECT CONSTRAINT_NAME
                FROM information_schema.TABLE_CONSTRAINTS 
                WHERE CONSTRAINT_TYPE = 'UNIQUE' 
                AND TABLE_NAME = 'api_data' 
                AND TABLE_SCHEMA = DATABASE();
                """)
                
                unique_constraints = cursor.fetchall()
                for constraint in unique_constraints:
                    constraint_name = constraint[0]
                    print(f"检查唯一性约束: {constraint_name}")
                    
                    # 检查是否包含 project_id
                    cursor.execute("""
                    SELECT COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE CONSTRAINT_NAME = %s
                    AND TABLE_NAME = 'api_data'
                    AND TABLE_SCHEMA = DATABASE();
                    """, (constraint_name,))
                    
                    columns = [col[0] for col in cursor.fetchall()]
                    if 'project_id' in columns:
                        print(f"删除包含 project_id 的唯一性约束: {constraint_name}")
                        try:
                            cursor.execute(f"ALTER TABLE api_data DROP INDEX `{constraint_name}`")
                            print(f"成功删除约束: {constraint_name}")
                        except Exception as e:
                            print(f"删除约束 {constraint_name} 时出错: {e}")
                            
            except Exception as e:
                print(f"处理唯一性约束时出错 (非致命): {e}")
            
            print("检查 project_id 列是否仍然存在...")
            cursor.execute("SHOW COLUMNS FROM api_data LIKE 'project_id'")
            if cursor.fetchone():
                print("删除 project_id 列...")
                cursor.execute("ALTER TABLE api_data DROP COLUMN project_id;")
                print("成功删除 project_id 列")
            else:
                print("project_id 列已不存在，跳过删除...")
            
            print("检查是否需要添加外键约束...")
            cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' 
            AND TABLE_NAME = 'api_data' 
            AND CONSTRAINT_NAME = 'fk_api_data_env'
            AND TABLE_SCHEMA = DATABASE();
            """)
            
            if cursor.fetchone()[0] == 0:
                print("添加外键约束...")
                cursor.execute("""
                ALTER TABLE api_data ADD CONSTRAINT fk_api_data_env
                    FOREIGN KEY (env_id) REFERENCES environment (id)
                    ON DELETE SET NULL;
                """)
                print("成功添加外键约束")
            else:
                print("外键约束已存在，跳过添加...")
        
            print("检查是否需要添加新的唯一性约束...")
            cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_TYPE = 'UNIQUE' 
            AND TABLE_NAME = 'api_data' 
            AND CONSTRAINT_NAME = 'api_data_env_id_path_method_uniq'
            AND TABLE_SCHEMA = DATABASE();
            """)
            
            if cursor.fetchone()[0] == 0:
                print("添加新的唯一性约束...")
                cursor.execute("""
                CREATE UNIQUE INDEX api_data_env_id_path_method_uniq
                    ON api_data(env_id, path, method);
                """)
                print("成功添加唯一性约束")
            else:
                print("唯一性约束已存在，跳过添加...")
            
            print("更新 Django 迁移记录...")
            try:
                cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('apiData', '0006_manual_sql_migration', NOW());
                """)
            except Exception as e:
                print(f"更新迁移记录时出错 (非致命): {e}")
            
            # 提交事务
            conn.commit()
            
            print("数据库迁移成功完成！")
    
    except Exception as e:
        conn.rollback()
        print(f"迁移过程中发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")

if __name__ == "__main__":
    execute_migration()
