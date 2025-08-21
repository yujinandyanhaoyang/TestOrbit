from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('apiData', '0005_alter_apiforeachstep_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- SQL脚本：修改 ApiData 表结构，将 project_id 字段替换为 env_id 字段

            -- 步骤1：添加新的 env_id 字段
            ALTER TABLE api_data ADD COLUMN env_id smallint NULL;

            -- 步骤2：将 project_id 的值复制到 env_id
            UPDATE api_data SET env_id = project_id;

            -- 步骤3：移除外键约束（如果存在）
            -- 由于 Django 的迁移系统会自动处理外键约束，此处不需要显式删除

            -- 步骤4：删除 project_id 字段
            ALTER TABLE api_data DROP COLUMN project_id;

            -- 步骤5：添加外键约束
            ALTER TABLE api_data ADD CONSTRAINT fk_api_data_env
                FOREIGN KEY (env_id) REFERENCES environment (id)
                ON DELETE SET NULL;

            -- 步骤6：修改唯一性约束
            DROP INDEX IF EXISTS api_data_project_id_path_method_uniq;
            CREATE UNIQUE INDEX api_data_env_id_path_method_uniq
                ON api_data(env_id, path, method)
                WHERE env_id IS NOT NULL;
            """,
            """
            -- 回滚操作（如果需要）
            ALTER TABLE api_data ADD COLUMN project_id integer NOT NULL DEFAULT 1;
            UPDATE api_data SET project_id = env_id WHERE env_id IS NOT NULL;
            ALTER TABLE api_data DROP COLUMN env_id;
            ALTER TABLE api_data ADD CONSTRAINT fk_api_data_project
                FOREIGN KEY (project_id) REFERENCES project (id)
                ON DELETE CASCADE;
            DROP INDEX IF EXISTS api_data_env_id_path_method_uniq;
            CREATE UNIQUE INDEX api_data_project_id_path_method_uniq
                ON api_data(project_id, path, method);
            """
        ),
    ]
