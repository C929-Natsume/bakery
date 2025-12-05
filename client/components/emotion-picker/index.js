// components/emotion-picker/index.js
const app = getApp();

Component({
  /**
   * 组件的属性列表
   */
  properties: {
    // 当前选中的情绪标签ID
    selectedId: {
      type: String,
      value: ''
    }
  },

  /**
   * 组件的初始数据
   */
  data: {
    emotions: [], // 情绪标签列表
    loading: true
  },

  /**
   * 组件的方法列表
   */
  methods: {
    /**
     * 加载情绪标签列表
     */
    loadEmotions() {
      // 先尝试从全局缓存获取
      if (app.globalData.emotionLabels) {
        this.setData({
          emotions: app.globalData.emotionLabels,
          loading: false
        });
        return;
      }

      // 从API获取
      const api = require('../../config/api.js').default;
      wx.request({
        url: api.emotionAPI + '/label',
        method: 'GET',
        success: (res) => {
          if (res.data.code === 0) {
            const systemLabels = res.data.data.system_labels || [];
            // 缓存到全局
            app.globalData.emotionLabels = systemLabels;
            this.setData({
              emotions: systemLabels,
              loading: false
            });
          }
        },
        fail: (err) => {
          console.error('加载情绪标签失败:', err);
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          });
          this.setData({ loading: false });
        }
      });
    },

    /**
     * 选择情绪标签
     */
    onSelectEmotion(e) {
      const { id, name, icon, color } = e.currentTarget.dataset;
      
      // 如果点击的是已选中的标签，则取消选择
      if (id === this.properties.selectedId) {
        this.triggerEvent('select', {
          id: '',
          name: '',
          icon: '',
          color: ''
        });
      } else {
        // 否则选中该标签
        this.triggerEvent('select', {
          id: id,
          name: name,
          icon: icon,
          color: color
        });
      }
    }
  },

  /**
   * 组件生命周期
   */
  lifetimes: {
    attached() {
      this.loadEmotions();
    }
  }
});

