import time
from user.models import UserCfg
from utils.constant import RUNNING, WAITING, INTERRUPT

def monitor_interrupt(user_id, actuator_obj):
    """
    监控线程：检查用例执行状态，处理中断请求
    """
    while True:
        time.sleep(3)
        # 检查执行器状态和用户配置
        exec_status = UserCfg.objects.filter(user_id=user_id).values_list('exec_status', flat=True).first()
        
        # 如果执行器已完成或用户要求中断，则停止监控
        if actuator_obj.status not in (RUNNING, WAITING) or exec_status in (INTERRUPT, WAITING):
            print('监控线程结束，状态:', actuator_obj.status)
            if exec_status == INTERRUPT:
                actuator_obj.status = INTERRUPT
            break
            
        # 只有在调试模式或需要时输出状态
        # print('monitor_interrupt', actuator_obj.status)
