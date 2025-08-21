from django.urls import path

from apiData.views import caseGroup, module_tree,caseStep

app_name = "apiData"

urlpatterns = [
    # 模块树
    path('tree-case-module', module_tree.tree_case_module),
    path('tree-cascader-module-case', module_tree.tree_cascader_module_case),
    path('tree-api-module', module_tree.tree_api_module),
    path('case-module-view', module_tree.CaseModuleViews.as_view()),
    path('api-module-view',  module_tree.ApiModuleViews.as_view()),
    

    # 用例组
    path('case-view', caseGroup.ApiCaseViews.as_view()),#一直在用这个接口

    path('delete-selected-cases', caseGroup.delete_selected_cases),
    path('stop-casing', caseGroup.stop_casing),
    path('copy-cases', caseGroup.copy_cases),
    path('merge-cases', caseGroup.merge_cases),
    path('copy-step-to-other-case', caseGroup.copy_step_to_other_case),
    path('case-sort-list', caseGroup.case_sort_list),
    path('set-case-position', caseGroup.set_case_position),
    path('clean-deleted-cases', caseGroup.clean_deleted_cases),


    # 测试步骤
    path('api-view', caseStep.ApiViews.as_view()),# 开始用到了
    #已用到功能
    # 保存单步骤

    path('search-api', caseStep.search_api),
    path('run-api-cases', caseStep.run_api_cases),
    path('run-api-case-step', caseStep.run_api_case_step),
    path('test-api-data', caseStep.test_api_data),
    path('test-api-data', caseStep.test_api_data),
    path('search-case-by-api', caseStep.search_case_by_api),


]
