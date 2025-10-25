// pages/diary-detail/index.js
Page({
  data: {
    diaryId: '',
    diary: null,
    dateDisplay: '',
    loading: true
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.setData({ diaryId: id });
      this.loadDiary(id);
    } else {
      wx.showToast({ title: '日记不存在', icon: 'none' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  /**
   * 页面显示时重新加载数据
   */
  onShow() {
    // 如果已经有diaryId，重新加载数据（从编辑页返回时）
    if (this.data.diaryId) {
      this.loadDiary(this.data.diaryId);
    }
  },

  /**
   * 加载日记详情
   */
  async loadDiary(id) {
    wx.showLoading({ title: '加载中', mask: true });
    try {
      const api = require('../../config/api.js').default;
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${api.diaryAPI}/${id}`,
          method: 'GET',
          success: resolve,
          fail: reject
        });
      });

      if (res.data.code === 0 || res.data.code === 1) {
        const diary = res.data.data;
        this.setData({ diary });
        const dateStr = diary.diary_date || diary.date || '';
        this.formatDate(dateStr);
      } else {
        wx.showToast({ title: res.data.msg || '加载失败', icon: 'none' });
      }
    } catch (error) {
      console.error('加载日记失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  },

  /**
   * 格式化日期显示
   */
  formatDate(dateStr) {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
    const weekDay = weekDays[date.getDay()];
    
    const dateDisplay = `${year}年${month}月${day}日 星期${weekDay}`;
    this.setData({ dateDisplay });
  },

  /**
   * 编辑日记
   */
  onEdit() {
    wx.navigateTo({
      url: `/pages/diary-edit/index?id=${this.data.diaryId}`
    });
  },

  /**
   * 删除日记
   */
  onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这篇日记吗？',
      confirmColor: '#ff4444',
      success: (res) => {
        if (res.confirm) {
          this.deleteDiary();
        }
      }
    });
  },

  /**
   * 执行删除
   */
  async deleteDiary() {
    wx.showLoading({ title: '删除中', mask: true });
    try {
      const api = require('../../config/api.js').default;
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${api.diaryAPI}/${this.data.diaryId}`,
          method: 'DELETE',
          success: resolve,
          fail: reject
        });
      });

      if (res.data.code === 0 || res.data.code === 1) {
        wx.showToast({ title: '删除成功', icon: 'success' });
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      } else {
        wx.showToast({ title: res.data.msg || '删除失败', icon: 'none' });
      }
    } catch (error) {
      console.error('删除日记失败:', error);
      wx.showToast({ title: '删除失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  }
});
