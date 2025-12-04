// components/topic-item/index.js
Component({
  externalClasses: ['topic-item-class'],
  properties: {
    topic: {
      type: Object,
      value: {},
      observer: function(newVal) {
        // 确保 topic 的相关属性正确
        if (newVal) {
          // 确保 images 是数组
          if (newVal.images && !Array.isArray(newVal.images)) {
            newVal.images = []
          }
          // 确保 labels 是数组
          if (newVal.labels && !Array.isArray(newVal.labels)) {
            newVal.labels = []
          }
          // 确保 content 是字符串
          if (newVal.content && typeof newVal.content !== 'string') {
            newVal.content = String(newVal.content)
          }
          // 确保 user 对象存在
          if (!newVal.user) {
            newVal.user = {}
          }
        }
      }
    },
    labels: {
      type: Array,
      value: [],
      observer: function(newVal) {
        // 确保 labels 是数组
        if (newVal && !Array.isArray(newVal)) {
          console.warn('topic-item: labels 需要是数组类型，当前值：', newVal)
          this.setData({ labels: [] })
        }
      }
    },
    // 最大内容显示字数
    maxContentLen: {
      type: Number,
      value: 180
    },
    // 是否为内容所有者
    isOwner: {
      type: Boolean,
      value: false
    },
    // 是否可跳转详情页
    isLink: {
      type: Boolean,
      value: true
    },
    // 是否显示全部内容
    showDetail: {
      type: Boolean,
      value: false
    },
    // 是否显示标签栏
    showTags: {
      type: Boolean,
      value: false
    },
    // 是否自动播放视频
    autoplay: {
      type: Boolean,
      value: false
    },
    // 是否静音播放视频
    muted: {
      type: Boolean,
      value: false
    }
  },
  data: {
    expand: false,  // 是否展开内容
  },
  lifetimes: {
    attached() {
      // 确保初始化时 labels 是数组
      if (!Array.isArray(this.data.labels)) {
        console.warn('topic-item: 初始化时 labels 不是数组，设置为空数组')
        this.setData({ labels: [] })
      }
      
      // 确保 topic 对象存在
      if (!this.data.topic) {
        this.setData({ topic: {} })
      }
    }
  },
  methods: {
    /**
     * 点击更多图标事件
     */
    onMoreIconTap() {
      console.log('topic-item: 更多图标点击')
      this.triggerEvent('moreIconTap', {
        topicId: this.data.topic.id,
        topic: this.data.topic
      })
    },

    /**
     * 点击标签事件
     */
    onTagTap(event) {
      const labelId = event.currentTarget.dataset.labelId
      console.log('topic-item: 标签点击, labelId:', labelId)
      this.triggerEvent('tagTap', { 
        labelId: labelId,
        topicId: this.data.topic.id
      })
    },

    /**
     * 切换内容展开状态
     */
    onExpandTap() {
      const topic = this.data.topic
      if (!topic) return
      
      const expand = !this.data.expand
      
      console.log('topic-item: 切换展开状态, expand:', expand)

      this.setData({
        expand: expand
      })
      
      this.triggerEvent('expandChange', { 
        expand: expand,
        topicId: topic.id
      })
    },

    /**
     * 跳转话题详情页
     */
    gotoTopicDetail() {
      if (!this.data.isLink || !this.data.topic || !this.data.topic.id) {
        return
      }

      const topic = this.data.topic
      console.log('topic-item: 跳转详情页, topicId:', topic.id)
      
      // 增加点击计数
      const updatedTopic = {
        ...topic,
        click_count: (topic.click_count || 0) + 1
      }

      this.setData({
        topic: updatedTopic
      })

      // 通知父组件
      this.triggerEvent('gotoDetail', { 
        topicId: topic.id,
        topic: topic
      })
      
      // 跳转到详情页
      wx.navigateTo({
        url: `/pages/topic-detail/index?topicId=${topic.id}`
      })
    },

    /**
     * 图片预览
     */
    previewImage(event) {
      const current = event.currentTarget.dataset.src
      const topic = this.data.topic
      const urls = topic.images || []
      
      if (!current || !urls.length) {
        return
      }
      
      console.log('topic-item: 预览图片, current:', current)
      
      wx.previewImage({
        current: current,
        urls: urls
      })
      
      this.triggerEvent('previewImage', { 
        current: current, 
        urls: urls,
        topicId: topic.id
      })
    },

    /**
     * 无操作事件
     */
    doNothing() {
      // 阻止事件冒泡的空函数
    },
    
    /**
     * 处理评论图标点击事件
     * 这是 favor-bar 组件触发的
     */
    onCommentIconTap(e) {
      const detail = e.detail || {}
      console.log('topic-item: 评论图标点击, detail:', detail)
      
      this.triggerEvent('commentIconTap', {
        ...detail,
        topicId: this.data.topic.id,
        topic: this.data.topic
      })
    },
    
    /**
     * 处理查看图标点击事件
     * 这是 favor-bar 组件触发的
     */
    onViewIconTap(e) {
      const detail = e.detail || {}
      console.log('topic-item: 查看图标点击, detail:', detail)
      
      this.triggerEvent('viewIconTap', {
        ...detail,
        topicId: this.data.topic.id,
        topic: this.data.topic
      })
    },
    
    /**
     * 处理交互变化事件
     * 这是 favor-bar 组件触发的（如点赞状态变化）
     */
    onInteractionChange(e) {
      const detail = e.detail || {}
      console.log('topic-item: 交互状态变化, detail:', detail)
      
      this.triggerEvent('interactionChange', {
        ...detail,
        topicId: this.data.topic.id,
        topic: this.data.topic
      })
      
      // 如果需要更新本地数据，可以在这里处理
      if (detail.type === 'favor' && this.data.topic) {
        const topic = this.data.topic
        const updatedTopic = {
          ...topic,
          has_favor: detail.value,
          favor_count: detail.value ? 
            (topic.favor_count || 0) + 1 : 
            Math.max(0, (topic.favor_count || 1) - 1)
        }
        
        this.setData({
          topic: updatedTopic
        })
      }
    },
    
    /**
     * 处理视频播放/暂停等事件
     */
    onVideoEvent(e) {
      const type = e.type
      console.log('topic-item: 视频事件, type:', type)
      
      this.triggerEvent('videoEvent', {
        type: type,
        detail: e.detail,
        topicId: this.data.topic.id
      })
    }
  }
})