import { defineStore } from 'pinia'
import { ref } from 'vue'

// 定义一个存储用例模块相关状态的 store
export const useCaseModuleStore = defineStore('caseModule', () => {
  // 当前选中的模块ID
  const selectedModuleId = ref<string>('')
  
  // 当前选中的项目ID
  const selectedProjectId = ref<number | null>(null)

  // 设置当前选中的模块ID
  function setSelectedModuleId(id: string) {
    selectedModuleId.value = id
  }
  
  // 设置当前选中的项目ID
  function setSelectedProjectId(id: number | null) {
    selectedProjectId.value = id
  }

  return {
    selectedModuleId,
    selectedProjectId,
    setSelectedModuleId,
    setSelectedProjectId
  }
})
