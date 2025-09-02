import { defineStore } from 'pinia'

export const useLayoutStore = defineStore('layout', {
  state: () => ({
    sidebarCollapsed: false,
  }),
  
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    
    setSidebarCollapsed(collapsed: boolean) {
      this.sidebarCollapsed = collapsed
    }
  },
  
  getters: {
    sidebarWidth: (state) => {
      return state.sidebarCollapsed ? 80 : 280
    }
  }
})
