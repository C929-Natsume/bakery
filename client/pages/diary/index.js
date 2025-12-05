// pages/diary/index.js
const app = getApp();

Page({
  data: {
    currentYear: 0,
    currentMonth: 0,
    currentDay: 0,
    calendar: [],
    diaries: [],
    todayDiary: null,
    loading: true
  },

  onLoad() {
    const date = new Date();
    this.setData({
      currentYear: date.getFullYear(),
      currentMonth: date.getMonth() + 1,
      currentDay: date.getDate()
    });
    this.loadDiaries();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadDiaries();
  },

  /**
   * 加载日记列表
   */
  async loadDiaries() {
    console.log('开始加载日记列表...');
    wx.showLoading({ title: '加载中', mask: true });
    try {
      const api = require('../../config/api.js').default;
      const url = `${api.diaryAPI}/list`;  // 修改：使用 /list 路由
      console.log('请求URL:', url);
      console.log('请求参数:', {
        year: this.data.currentYear,
        month: this.data.currentMonth
      });

      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: url,
          method: 'GET',
          data: {
            page: 1,
            size: 100  // 获取足够多的数据
          },
          success: resolve,
          fail: reject
        });
      });

      console.log('API响应:', res);

      if (res.data.code === 0 || res.data.code === 1) {  // 兼容不同的成功码
        // 从分页数据中提取items
        const items = res.data.data.items || [];
        // 过滤出当前月份的日记
        const { currentYear, currentMonth } = this.data;
        const diaries = items.filter(diary => {
          const date = new Date(diary.diary_date || diary.date);
          return date.getFullYear() === currentYear && date.getMonth() + 1 === currentMonth;
        });
        
        console.log('日记总数:', items.length, '当月日记:', diaries.length);
        this.setData({ diaries });
        this.generateCalendar();
        this.loadTodayDiary();
      } else {
        console.error('API返回错误:', res.data);
        wx.showToast({ title: res.data.msg || '加载失败', icon: 'none' });
        // 即使API失败，也生成空日历
        this.setData({ diaries: [] });
        this.generateCalendar();
      }
    } catch (error) {
      console.error('加载日记失败:', error);
      wx.showToast({ title: '网络请求失败', icon: 'none' });
      // 即使请求失败，也生成空日历
      this.setData({ diaries: [] });
      this.generateCalendar();
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  },

  /**
   * 生成日历数据
   */
  generateCalendar() {
    const { currentYear, currentMonth, diaries } = this.data;
    const firstDay = new Date(currentYear, currentMonth - 1, 1);
    const lastDay = new Date(currentYear, currentMonth, 0);
    const daysInMonth = lastDay.getDate();
    const startWeekDay = firstDay.getDay();

    // 获取今天的日期信息（用于高亮）
    const today = new Date();
    const todayYear = today.getFullYear();
    const todayMonth = today.getMonth() + 1;
    const todayDay = today.getDate();
    
    console.log('生成日历:', {
      year: currentYear,
      month: currentMonth,
      daysInMonth: daysInMonth,
      startWeekDay: startWeekDay,
      diariesCount: diaries.length,
      todayInfo: {
        year: todayYear,
        month: todayMonth,
        day: todayDay
      }
    });

    // 创建日记映射
    const diaryMap = {};
    diaries.forEach(diary => {
      // 兼容不同的日期字段名
      const dateStr = diary.diary_date || diary.date || '';
      const date = dateStr.split(' ')[0]; // 取日期部分
      if (date) {
        const day = parseInt(date.split('-')[2]);
        diaryMap[day] = diary;
      }
    });

    // 生成日历数组
    const calendar = [];
    let week = [];

    // 填充月初空白
    for (let i = 0; i < startWeekDay; i++) {
      week.push(null);
    }

    // 填充日期
    
    for (let day = 1; day <= daysInMonth; day++) {
      const diary = diaryMap[day];
      week.push({
        day: day,
        date: `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
        hasDiary: !!diary,
        emotion: diary ? diary.emotion_label : null,
        isToday: day === todayDay && 
                 currentMonth === todayMonth && 
                 currentYear === todayYear
      });

      if (week.length === 7) {
        calendar.push(week);
        week = [];
      }
    }

    // 填充月末空白
    if (week.length > 0) {
      while (week.length < 7) {
        week.push(null);
      }
      calendar.push(week);
    }

    console.log('日历生成完成，周数:', calendar.length);
    this.setData({ calendar });
  },

  /**
   * 加载今日日记
   */
  loadTodayDiary() {
    const { diaries, currentDay, currentYear, currentMonth } = this.data;
    const todayDiary = diaries.find(diary => {
      const dateStr = diary.diary_date || diary.date || '';
      const date = dateStr.split(' ')[0];
      if (!date) return false;
      
      const [year, month, day] = date.split('-').map(Number);
      return year === currentYear && month === currentMonth && day === currentDay;
    });
    this.setData({ todayDiary: todayDiary || null });  // 修复：使用null代替undefined
  },

  /**
   * 切换到上个月
   */
  onPrevMonth() {
    let { currentYear, currentMonth } = this.data;
    currentMonth--;
    if (currentMonth < 1) {
      currentMonth = 12;
      currentYear--;
    }
    this.setData({ currentYear, currentMonth });
    this.loadDiaries();
  },

  /**
   * 切换到下个月
   */
  onNextMonth() {
    let { currentYear, currentMonth } = this.data;
    currentMonth++;
    if (currentMonth > 12) {
      currentMonth = 1;
      currentYear++;
    }
    this.setData({ currentYear, currentMonth });
    this.loadDiaries();
  },

  /**
   * 点击日期
   */
  onDateTap(e) {
    const { date } = e.currentTarget.dataset;
    if (!date) return;

    // 查找该日期的日记
    const diary = this.data.diaries.find(d => {
      const dateStr = d.diary_date || d.date || '';
      if (!dateStr) return false;
      const diaryDate = dateStr.split(' ')[0];
      return diaryDate === date;
    });

    if (diary) {
      // 跳转到日记详情页
      wx.navigateTo({
        url: `/pages/diary-detail/index?id=${diary.id}`
      });
    } else {
      // 跳转到创建日记页
      wx.navigateTo({
        url: `/pages/diary-edit/index?date=${date}`
      });
    }
  },

  /**
   * 创建今日日记
   */
  onCreateTodayDiary() {
    const { currentYear, currentMonth, currentDay } = this.data;
    const date = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(currentDay).padStart(2, '0')}`;
    wx.navigateTo({
      url: `/pages/diary-edit/index?date=${date}`
    });
  },

  /**
   * 查看今日日记
   */
  onViewTodayDiary() {
    if (this.data.todayDiary) {
      wx.navigateTo({
        url: `/pages/diary-detail/index?id=${this.data.todayDiary.id}`
      });
    }
  }
});
