import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

import App from './App.vue'
import router from './router'
import './assets/main.css'

import 'primeicons/primeicons.css'

const zh = {
  firstDayOfWeek: 1,
  dayNames: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
  dayNamesShort: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
  dayNamesMin: ['日', '一', '二', '三', '四', '五', '六'],
  monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
  monthNamesShort: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
  today: '今天',
  clear: '清空',
  dateFormat: 'yy/mm/dd',
  weekHeader: '周',
  weak: '弱',
  medium: '中',
  strong: '强',
  emptyFilterMessage: '未找到匹配结果',
  emptyMessage: '暂无数据',
  search: '搜索',
  noResults: '无结果',
  showPassword: '显示密码',
  hidePassword: '隐藏密码',
  emptySelectionMessage: '未选择任何项',
  loadingMessage: '加载中...',
  aria: {
    cancel: '取消',
    close: '关闭',
    closeAriaLabel: '关闭',
    edit: '编辑',
    previousPage: '上一页',
    nextPage: '下一页',
    firstPage: '首页',
    lastPage: '末页',
    selectAll: '全选',
    selectAllAriaLabel: '全选',
    selectRow: '选择行',
    unselectRow: '取消选择行',
    rowsPerPage: '每页条数',
    previousMonth: '上一月',
    nextMonth: '下一月',
    selectDate: '选择日期',
    previousYear: '上一年',
    nextYear: '下一年',
    previousDecade: '上一个十年',
    nextDecade: '下一个十年',
  },
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: false,
    },
  },
  locale: zh,
})
app.use(ToastService)
app.use(ConfirmationService)

app.mount('#app')
