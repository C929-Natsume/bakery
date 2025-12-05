// pages/diary-edit/index.js
const app = getApp();

Page({
  data: {
    diaryId: '',
    date: '',
    dateDisplay: '',
    content: '',
    selectedEmotionId: '',
    selectedEmotionName: '',
    isPublic: false,
    isEdit: false
  },

  onLoad(options) {
    const { id, date } = options;
    
    if (id) {
      // 编辑模式
      this.setData({ diaryId: id, isEdit: true });
      this.loadDiary(id);
    } else if (date) {
      // 创建模式
      this.setData({ date: date });
      this.formatDate(date);
    } else {
      // 默认今天
      const today = new Date();
      const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      this.setData({ date: dateStr });
      this.formatDate(dateStr);
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
        const dateStr = diary.diary_date || diary.date || '';
        this.setData({
          date: dateStr.split(' ')[0],
          content: diary.content,
          selectedEmotionId: diary.emotion_label ? diary.emotion_label.id : '',
          selectedEmotionName: diary.emotion_label ? diary.emotion_label.name : '',
          isPublic: diary.is_public
        });
        this.formatDate(dateStr);
      } else {
        wx.showToast({ title: res.data.msg || '加载失败', icon: 'none' });
      }
    } catch (error) {
      console.error('加载日记失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  /**
   * 选择情绪标签
   */
  onEmotionSelect(e) {
    const { id, name } = e.detail;
    console.log('选中情绪标签:', id, name);
    this.setData({
      selectedEmotionId: id,
      selectedEmotionName: name
    });
  },

  /**
   * 输入内容
   */
  onContentInput(e) {
    this.setData({ content: e.detail.value });
  },

  /**
   * 切换隐私设置
   */
  onPrivacyChange(e) {
    this.setData({ isPublic: e.detail.value });
  },

  /**
   * 保存日记
   */
  async onSave() {
    const { diaryId, date, content, selectedEmotionId, isPublic, isEdit } = this.data;

    // 验证
    if (!content || content.trim() === '') {
      wx.showToast({ title: '请输入日记内容', icon: 'none' });
      return;
    }

    if (!selectedEmotionId) {
      wx.showToast({ title: '请选择心情', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '保存中', mask: true });
    try {
      const api = require('../../config/api.js').default;
      const method = isEdit ? 'PUT' : 'POST';
      const url = isEdit ? `${api.diaryAPI}/${diaryId}` : api.diaryAPI;
      
      // 获取请求头（包含Authorization token）
      const app = getApp();
      const header = app.getHeader ? app.getHeader() : {};
      
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: url,
          method: method,
          header: header,
          data: {
            diary_date: date,  // 后端使用 diary_date 字段
            content: content.trim(),
            emotion_label_id: selectedEmotionId,
            is_public: isPublic
          },
          success: resolve,
          fail: reject
        });
      });

      if (res.data.code === 0 || res.data.code === 1) {
        wx.showToast({ 
          title: isEdit ? '更新成功' : '保存成功', 
          icon: 'success' 
        });
        
        // 延迟返回，让用户看到成功提示
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      } else {
        wx.showToast({ title: res.data.msg || '保存失败', icon: 'none' });
      }
    } catch (error) {
      console.error('保存日记失败:', error);
      wx.showToast({ title: '保存失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  }
});
