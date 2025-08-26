from django.apps import AppConfig


class ApidataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apiData'
    
    def ready(self):
        """
        Django应用启动时调用
        启动定时任务调度器
        """
        # 避免在makemigrations、migrate和重新加载时启动调度器
        import sys
        import os
        
        # 检查是否是主进程（避免在自动重新加载时重复启动）
        if os.environ.get('RUN_MAIN') == 'true' and ('runserver' in sys.argv or 'gunicorn' in sys.argv[0]):
            from .views.function.scheduled_tasks_def import TaskScheduler
            scheduler = TaskScheduler()
            scheduler.start()
            print("✅ 定时任务调度器已在应用启动时启动")
