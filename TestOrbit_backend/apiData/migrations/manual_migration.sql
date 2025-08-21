-- 手动数据库迁移脚本
-- 将 ApiData 表中的 project_id 字段替换为 env_id 字段

-- 1. 添加新的 env_id 列（如果不存在）
ALTER TABLE api_data ADD COLUMN IF NOT EXISTS env_id smallint NULL;

-- 2. 将 project_id 的值复制到 env_id
UPDATE api_data SET env_id = project_id;

-- 3. 删除与 project_id 相关的外键约束（如果存在）
-- 注意：您可能需要先查询约束名称，再运行这一步
-- 示例：SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS 
--       WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' AND TABLE_NAME = 'api_data' AND CONSTRAINT_NAME LIKE '%project_id%';
-- 然后对每个约束：ALTER TABLE api_data DROP FOREIGN KEY constraint_name;

-- 4. 删除 project_id 列
ALTER TABLE api_data DROP COLUMN project_id;

-- 5. 添加外键约束
ALTER TABLE api_data ADD CONSTRAINT fk_api_data_env
    FOREIGN KEY (env_id) REFERENCES environment (id)
    ON DELETE SET NULL;

-- 6. 添加唯一性约束
ALTER TABLE api_data ADD CONSTRAINT api_data_env_path_method_uniq 
    UNIQUE (env_id, path, method);

-- 7. 在Django迁移记录表中添加记录（可选）
INSERT INTO django_migrations (app, name, applied)
VALUES ('apiData', '0006_auto_replace_project_with_env', NOW());

-- 完成！
-- 如果执行中遇到错误，请检查错误信息并相应调整脚本
