// components/favor-bar/index.js
const api = require('../../config/api.js').default;

Component({
  properties: {
    topicId: {
      type: String,
      value: ''
    },
    commentCount: {
      type: Number,
      value: 0
    },
    viewCount: {
      type: Number,
      value: 0
    },
    hasComment: {
      type: Boolean,
      value: false
    },
    hasView: {
      type: Boolean,
      value: false
    }
  },

  data: {
    // 互动统计
    starCount: 0,
    hugCount: 0,
    patCount: 0,
    // 用户互动状态
    hasStar: false,
    hasHug: false,
    hasPat: false,
    // 加载状态
    loading: false
  },

  methods: {
    /**
     * 加载互动统计
     */
    loadInteractionStats() {
      if (!this.properties.topicId) return;

      // 获取请求头（如果用户已登录，会包含Authorization）
      const app = getApp();
      const header = app.getHeader ? app.getHeader() : {};

      wx.request({
        url: `${api.starAPI}/stat/${this.properties.topicId}`,
        method: 'GET',
        header: header,
        success: (res) => {
          if (res.data.code === 0) {
            const { stats, user_interactions } = res.data.data;
            this.setData({
              starCount: stats.STAR || 0,
              hugCount: stats.HUG || 0,
              patCount: stats.PAT || 0,
              hasStar: user_interactions.includes('STAR'),
              hasHug: user_interactions.includes('HUG'),
              hasPat: user_interactions.includes('PAT')
            });
          }
        },
        fail: (err) => {
          console.error('加载互动统计失败:', err);
        }
      });
    },

    /**
     * 点击评论图标事件
     */
    onCommentIconTap() {
      this.triggerEvent('commentIconTap', {}, { bubbles: true, composed: true });
    },

    /**
     * 点击收藏图标事件
     */
    onStarIconTap() {
      this.handleInteraction('STAR');
    },

    /**
     * 点击拥抱图标事件
     */
    onHugIconTap() {
      this.handleInteraction('HUG');
    },

    /**
     * 点击拍拍图标事件
     */
    onPatIconTap() {
      this.handleInteraction('PAT');
    },

    /**
     * 点击浏览图标事件
     */
    onViewIconTap() {
      this.triggerEvent('viewIconTap', {}, { bubbles: true, composed: true });
    },

    /**
     * 处理互动
     */
    handleInteraction(type) {
      if (this.data.loading) return;

      // 从userDetail中获取token
      const app = getApp();
      const userDetail = wx.getStorageSync('userDetail') || app.globalData.userDetail;
      
      if (!userDetail || !userDetail.token) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        });
        // 跳转到登录页
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/auth/index'
          });
        }, 1500);
        return;
      }

      this.setData({ loading: true });

      // 使用app.getHeader()获取完整的请求头（包含Authorization）
      const header = app.getHeader ? app.getHeader() : {
        'Authorization': `Token ${userDetail.token}`,
        'Content-Type': 'application/json'
      };

      wx.request({
        url: api.starAPI + '/',
        method: 'POST',
        header: header,
        data: {
          topic_id: this.properties.topicId,
          interaction_type: type
        },
        success: (res) => {
          if (res.data.code === 0) {
            wx.showToast({
              title: res.data.msg,
              icon: 'success',
              duration: 1500
            });
            // 重新加载统计
            this.loadInteractionStats();
            // 触发事件通知父组件
            this.triggerEvent('interactionChange', { type: type });
          } else {
            wx.showToast({
              title: res.data.msg || '操作失败',
              icon: 'none'
            });
          }
        },
        fail: (err) => {
          console.error('互动失败:', err);
          wx.showToast({
            title: '网络错误',
            icon: 'none'
          });
        },
        complete: () => {
          this.setData({ loading: false });
        }
      });
    }
  },

  lifetimes: {
    attached() {
      // 组件加载时获取互动统计
      this.loadInteractionStats();
    }
  },

  observers: {
    'topicId': function(newVal) {
      // topicId变化时重新加载统计
      if (newVal) {
        this.loadInteractionStats();
      }
    }
  }
});
