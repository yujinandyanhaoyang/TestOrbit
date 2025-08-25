from django.urls import path

from apiData.views import caseGroup, module_tree, caseStep, case_steps

app_name = "apiData"

urlpatterns = [
    # 模块树
    path('tree-case-module', module_tree.tree_case_module),
    path('tree-cascader-module-case', module_tree.tree_cascader_module_case),
    path('tree-api-module', module_tree.tree_api_module),
    path('case-module-view', module_tree.CaseModuleViews.as_view()),
    path('api-module-view',  module_tree.ApiModuleViews.as_view()),
    

    # 用例组
    # 用例组CRUD完成
    path('case-view', caseGroup.ApiCaseViews.as_view()),#一直在用这个接口
    # 运行整个用例组
    path('run-api-cases', caseGroup.run_api_cases),
    # 批量运行选中的用例组（支持并行或串行）
    path('batch-run-api-cases', caseGroup.batch_run_api_cases),
    
    # 复制用例组
    path('copy-cases', caseGroup.copy_cases),
    # 标记选中用例组为删除状态
    path('delete-selected-cases', caseGroup.delete_selected_cases),
    # 清理删除状态的用例组
    path('clean-deleted-cases', caseGroup.clean_deleted_cases),
    # 恢复被标记为删除的用例组
    path('restore-deleted-cases', caseGroup.restore_deleted_cases),



    path('stop-casing', caseGroup.stop_casing),
    
    path('merge-cases', caseGroup.merge_cases),
    path('copy-step-to-other-case', caseGroup.copy_step_to_other_case),
    path('case-sort-list', caseGroup.case_sort_list),
    path('set-case-position', caseGroup.set_case_position),


    # 测试步骤 步骤CURD完成
    # 保存单步骤
    # 获取单步骤详情信息
    path('api-view', caseStep.ApiViews.as_view()),# 开始用到了
    # 运行单步测试用例
    path('steps/test-api-data', caseStep.test_api_data),#
    # 复制步骤
    path('steps/copy-step', caseStep.copy_step),
    # 调整步骤顺序
    path('steps/reorder', case_steps.reorder_steps), 
    # 删除步骤
    path('steps/delete', case_steps.delete_step),          


    path('search-api', caseStep.search_api),

    path('run-api-case-step', caseStep.run_api_case_step),


    path('search-case-by-api', caseStep.search_case_by_api),

    # 用例步骤管理
    path('steps/add', case_steps.add_steps),            # 添加步骤
    path('steps/update', case_steps.update_step),       # 更新步骤
    
    
]
