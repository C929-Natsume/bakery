// pages/profile/index.js
import api from '../../config/api'
import wxutil from '../../miniprogram_npm/@yyjeffrey/wxutil/index'
import { init, upload } from '../../utils/qiniuUploader'
import { User } from '../../models/user'
import { Topic } from '../../models/topic'
import { Comment } from '../../models/comment'
import { Star } from '../../models/star'
import { Message } from '../../models/message'
import { OSS } from '../../models/oss'

import { Soul } from '../../models/soul'

const app = getApp()

Page({
  data: {
    user: null,
    topics: [],
    comments: [],
    stars: [],
    tabIndex: 0,  // Tabs选中的栏目
    tabsTop: 300, // Tabs距离顶部的高度
    showImageClipper: false, // 是否显示图片裁剪器
    tmpAvatar: '', // 头像临时文件
    messageBrief: null, // 动态消息概要
    topicPaging: null,  // 话题分页器
    commentPaging: null,  // 评论分页器
    starPaging: null, // 收藏分页器
    hasMoreTopic: true, // 是否还有更多话题
    hasMoreComment: true, // 是否还有更多评论
    hasMoreStar: true, // 是否还有更多收藏
    tabsFixed: false, // Tabs是否吸顶
    loading: false,
    //cocobegin
    showSoulPopup: false, // 是否显示心灵鸡汤弹窗
    soulMessage: {}, // 当前心灵鸡汤内容
    soulLoading: false, // 是否正在加载
    soulTabIndex: 0, // Tab索引：0-查看，1-添加
    customMessage: '', // 自定义句子输入
    customMessages: [] // 保存的自定义句子列表
    //cocobegin
  },

  onLoad() {
    this.getUserInfo()
  },

  onShow() {
    this.getUserInfo(false)
    this.getMessages()
  },

  /**
   * 计算Tabs距离顶部的高度
   */
  getTabsTop() {
    const query = wx.createSelectorQuery()
    query.select('#tabs').boundingClientRect((res) => {
      this.setData({
        tabsTop: res.top
      })
    }).exec()
  },

  /**
   * 获取用户信息
   */
  async getUserInfo(loadPage = true) {
    let userDetail = app.globalData.userDetail
    if (!userDetail) {
      this.setData({
        user: null,
        topics: [],
        comments: [],
        stars: []
      })
      return
    }

    const userId = userDetail.id
    const user = await User.getUserInfo(userId)
    // 更新缓存
    userDetail = Object.assign(userDetail, user)
    const deadtime = wxutil.getStorage('userDetail_deadtime')
    wxutil.setStorage('userDetail', userDetail)
    wxutil.setStorage('userDetail_deadtime', deadtime)

    app.globalData.userDetail = userDetail
    this.setData({
      user: userDetail
    })

    if (loadPage) {
      this.getTabsTop()
      wx.setNavigationBarTitle({
        title: userDetail.nickname
      })
    }

    this.initTopics(userId)
    this.initComments(userId)
    this.initStars(userId)
  },

  /**
   * 初始化七牛云配置
   */
  async initQiniu() {
    const uptoken = await OSS.getQiniu()
    const options = {
      region: 'ECN',
      uptoken: uptoken,
      domain: api.ossDomain,
      shouldUseQiniuFileName: false
    }
    init(options)
  },

  //cocobegin
    /**
   * 打开心灵鸡汤弹窗 - 使用智能推送
   * 根据识别出的情绪标签智能推送鸡汤句子
   */
  async openSoulMessage() {
    // 等待分析时显示的随机鼓励句子
    const waitingMessages = [
      "Life is like a box of chocolates, you never know what you're gonna get."
    ]
    
    // 先显示一个随机鼓励句子
    const randomWaiting = waitingMessages[Math.floor(Math.random() * waitingMessages.length)]
    
    // 显示加载状态，先显示等待句子
    this.setData({
      showSoulPopup: true,
      soulTabIndex: 0, // 默认显示查看模式
      soulLoading: true,
      soulMessage: {
        content: randomWaiting,
        push_id: null,
        source: 'waiting'
      }
    })

    try {
      // 调用智能推送API - 自动识别用户情绪标签并推送匹配的句子
      const res = await Soul.getSmartPush()
      
      if (res && res.code === 0 && res.data) {
        const data = res.data
        // 格式化置信度为百分比
        const confidencePercent = data.confidence ? Math.round(data.confidence * 100) : 0
        
        this.setData({
          soulMessage: {
            push_id: data.push_id,
            content: data.content,
            emotion_label: data.emotion_label,
            confidence: data.confidence,
            confidence_percent: confidencePercent, // 格式化后的百分比
            source: data.source,
            is_collected: false // 默认未收藏
          },
          soulLoading: false
        })
        
        // 如果有情绪标签信息，可以显示给用户
        if (data.emotion_label && data.emotion_label.name) {
          console.log(`智能识别到情绪: ${data.emotion_label.name} (置信度: ${confidencePercent}%)`)
        }
      } else {
        // 如果智能推送失败，保持显示的等待句子
        this.setData({
          soulLoading: false
        })
      }
    } catch (error) {
      console.error('获取智能推送失败:', error)
      // 保持显示的等待句子
      this.setData({
        soulLoading: false
      })
    }
  },

  /**
   * 关闭心灵鸡汤弹窗
   */
  closeSoulPopup() {
    this.setData({
      showSoulPopup: false,
      soulMessage: {}
    })
  },

  /**
   * 阻止冒泡（防止点击内容区域关闭弹窗）
   */
  preventClose() {
    // 空函数，阻止事件冒泡
  },

  /**
   * 收藏心灵鸡汤
   */
  async collectSoulMessage() {
    if (!this.data.soulMessage.push_id) {
      return
    }

    try {
      const res = await Soul.toggleCollect(this.data.soulMessage.push_id)
      if (res.code === 0) {
        this.setData({
          'soulMessage.is_collected': res.data.is_collected
        })
        wx.showToast({
          title: res.data.is_collected ? '收藏成功' : '已取消收藏',
          icon: 'success'
        })
      }
    } catch (error) {
      console.error('收藏失败:', error)
      wx.showToast({
        title: '操作失败',
        icon: 'none'
      })
    }
  },
  /**
 * 切换Tab
 */
  switchSoulTab(e) {
    const index = parseInt(e.currentTarget.dataset.index)
    this.setData({
      soulTabIndex: index,
      customMessage: '' // 切换时清空输入
    })
    
    // 如果切换到查看模式，加载一条消息
    if (index === 0) {
      this.loadRandomOrCustomMessage()
    }
  },

  /**
   * 自定义句子输入
   */
  onCustomMessageInput(e) {
    this.setData({
      customMessage: e.detail.value
    })
  },

  /**
   * 保存自定义句子
   */
/**
 * 保存自定义句子
 */
async saveCustomMessage() {
  const message = this.data.customMessage.trim()
  
  if (!message) {
    wx.showToast({
      title: '请输入句子',
      icon: 'none'
    })
    return
  }
  
  if (message.length > 500) {
    wx.showToast({
      title: '句子太长，最多500字',
      icon: 'none'
    })
    return
  }
  
  wx.showLoading({
    title: '保存中...'
  })
  
  try {
    // 调用API保存到后端（后端会调用情绪识别功能）
    const res = await Soul.saveCustom(message)
    
    if (res.code === 0) {
      const data = res.data
      const createdCount = data.created_count || 1
      
      wx.showToast({
        title: `保存成功（已创建${createdCount}条记录）`,
        icon: 'success',
        duration: 2000
      })
      
      // 清空输入，切换到查看模式，显示刚保存的句子
      this.setData({
        customMessage: '',
        soulTabIndex: 0,
        soulMessage: {
          push_id: data.push_id,
          content: data.content,
          emotion_label: data.emotion_label,
          emotion_name: data.emotion_name, // 识别出的情绪名称
          source: 'user_custom',
          is_collected: false
        },
        soulLoading: false
      })
      
      // 如果有情绪标签信息，记录日志
      if (data.emotion_label && data.emotion_label.name) {
        console.log(`保存的自定义句子识别为: ${data.emotion_label.name}, 创建了${createdCount}条记录`)
      } else if (data.emotion_name) {
        console.log(`保存的自定义句子识别为: ${data.emotion_name}, 创建了${createdCount}条记录`)
      }
    } else {
      wx.showToast({
        title: res.msg || '保存失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('保存自定义句子失败:', error)
    wx.showToast({
      title: '网络错误',
      icon: 'none'
    })
  } finally {
    wx.hideLoading()
  }
},

/**
 * 取消添加
 */
cancelAddMessage() {
  this.setData({
    customMessage: '',
    soulTabIndex: 0
  })
  // 加载一条消息
  this.loadRandomOrCustomMessage()
},

/**
 * 加载随机或自定义消息
 * 改为使用智能推送（匹配数据库中情绪标签一致的句子）
 */
async loadRandomOrCustomMessage() {
  // 直接使用智能推送
  this.getRandomMessage()
},

/**
 * 获取随机消息 - 根据已识别的情绪标签获取另一条句子（换一条）
 */
async getRandomMessage() {
  // 获取当前保存的情绪标签ID和句子ID
  const currentEmotionLabel = this.data.soulMessage?.emotion_label
  const currentPushId = this.data.soulMessage?.push_id
  
  // 等待分析时显示的随机鼓励句子
  const waitingMessages = [
    "Life is like a box of chocolates, you never know what you're gonna get."
  ]
  
  // 先显示一个随机鼓励句子
  const randomWaiting = waitingMessages[Math.floor(Math.random() * waitingMessages.length)]
  
  this.setData({
    soulLoading: true,
    soulMessage: {
      ...this.data.soulMessage,
      content: randomWaiting,
      push_id: null,
      source: 'waiting'
    }
  })
  
  // 如果有已识别的情绪标签，使用它获取另一条句子
  if (currentEmotionLabel && currentEmotionLabel.id) {
    try {
      // 根据已识别的情绪标签获取另一条句子（排除当前显示的句子）
      const res = await Soul.getAnotherSmartPush(currentEmotionLabel.id, currentPushId)
      
      if (res && res.code === 0 && res.data) {
        const data = res.data
        
        this.setData({
          soulMessage: {
            push_id: data.push_id,
            content: data.content,
            emotion_label: data.emotion_label,
            confidence: this.data.soulMessage?.confidence, // 保持原有的置信度
            confidence_percent: this.data.soulMessage?.confidence_percent, // 保持原有的置信度百分比
            source: data.source,
            is_collected: false // 默认未收藏
          },
          soulLoading: false
        })
        
        console.log(`根据已识别情绪标签获取另一条句子: ${data.emotion_label?.name}`)
        return
      }
    } catch (error) {
      console.error('获取另一条句子失败:', error)
      // 继续下面的逻辑，可能没有已识别的标签，需要重新分析
    }
  }
  
  // 如果没有已识别的情绪标签，调用智能推送接口（重新分析）
  try {
    const res = await Soul.getSmartPush()
    
    if (res && res.code === 0 && res.data) {
      const data = res.data
      // 格式化置信度为百分比
      const confidencePercent = data.confidence ? Math.round(data.confidence * 100) : 0
      
      this.setData({
        soulMessage: {
          push_id: data.push_id,
          content: data.content,
          emotion_label: data.emotion_label,
          confidence: data.confidence,
          confidence_percent: confidencePercent,
          source: data.source,
          is_collected: false // 默认未收藏
        },
        soulLoading: false
      })
      
      // 如果有情绪标签信息，记录日志
      if (data.emotion_label && data.emotion_label.name) {
        console.log(`智能识别到情绪: ${data.emotion_label.name} (置信度: ${confidencePercent}%)`)
      }
    } else {
      // 如果智能推送失败，保持显示的等待句子
      this.setData({
        soulLoading: false
      })
    }
  } catch (error) {
    console.error('获取智能推送失败:', error)
    // 保持显示的等待句子
    this.setData({
      soulLoading: false
    })
  }
},

/**
 * 查看全部自定义消息
 */
/**
 * 查看全部自定义消息
 */
async viewAllMessages() {
  wx.showLoading({
    title: '加载中...'
  })
  
  try {
    const data = await Soul.getCustomList({ page: 1, size: 50 })
    
    if (!data || !data.items || data.items.length === 0) {
      wx.showToast({
        title: '还没有自定义句子',
        icon: 'none'
      })
      wx.hideLoading()
      return
    }
    
    // 显示列表供选择
    const itemList = data.items.map((msg, index) => {
      const content = msg.content.length > 20 
        ? msg.content.substring(0, 20) + '...' 
        : msg.content
      return `${index + 1}. ${content}`
    })
    
    wx.hideLoading()
    
    wx.showActionSheet({
      itemList: itemList,
      success: (res) => {
        this.setData({
          soulMessage: {
            push_id: data.items[res.tapIndex].id,
            content: data.items[res.tapIndex].content,
            is_custom: true
          }
        })
      }
    })
  } catch (error) {
    wx.hideLoading()
    console.error('获取自定义句子列表失败:', error)
    wx.showToast({
      title: '加载失败',
      icon: 'none'
    })
  }
},
//cocobegin

  /**
   * 媒体文件上传至OSS
   */
  sendMedia(imageFile, path) {
    return new Promise((resolve, reject) => {
      upload(imageFile, (res) => {
        resolve(res.imageURL)
      }, (error) => {
        reject(error)
      }, {
        region: 'ECN',
        uptoken: null,
        domain: null,
        shouldUseQiniuFileName: false,
        key: path + '/' + wxutil.getUUID(false)
      })
    })
  },

  /**
   * 初始化话题
   */
  async initTopics(userId) {
    const topicPaging = await Topic.getTopicPaging({ user_id: userId })
    this.setData({
      topicPaging: topicPaging
    })
    await this.getMoreTopics(topicPaging)
  },

  /**
   * 获取更多话题
   */
  async getMoreTopics(topicPaging) {
    const data = await topicPaging.getMore()
    if (!data) {
      return
    }
    this.setData({
      topics: data.accumulator,
      hasMoreTopic: data.hasMore
    })
  },

  /**
   * 初始化评论
   */
  async initComments(userId) {
    const commentPaging = await Comment.getCommentPaging({ user_id: userId })
    this.setData({
      commentPaging: commentPaging
    })
    await this.getMoreComments(commentPaging)
  },

  /**
   * 获取更多评论
   */
  async getMoreComments(commentPaging) {
    const data = await commentPaging.getMore()
    if (!data) {
      return
    }
    this.setData({
      comments: data.accumulator,
      hasMoreComment: data.hasMore
    })
  },

  /**
   * 初始化用户收藏
   */
  async initStars(userId) {
    const starPaging = await Star.getStarPaging({ user_id: userId })
    this.setData({
      starPaging: starPaging
    })
    await this.getMoreStars(starPaging)
  },

  /**
   * 获取更多收藏
   */
  async getMoreStars(starPaging) {
    const data = await starPaging.getMore()
    if (!data) {
      return
    }
    this.setData({
      stars: data.accumulator,
      hasMoreStar: data.hasMore
    })
  },

  /**
   * 获取消息并标红点
   */
  async getMessages() {
    if (!app.globalData.userDetail) {
      return
    }

    const data = await Message.getMessages()
    if (data && data.length > 0) {
      this.setData({
        messageBrief: data
      })
      wx.setTabBarBadge({
        index: 2,
        text: data.length.toString()
      })
    } else {
      this.setData({
        messageBrief: null
      })
      wx.removeTabBarBadge({
        index: 2
      })
    }
  },

  /**
   * Tab切换
   */
  changeTabs(event) {
    const tabIndex = event.detail.currentIndex
    this.setData({
      tabIndex: tabIndex
    })
    if (this.data.tabsFixed) {
      wx.pageScrollTo({
        scrollTop: this.data.tabsTop
      })
    }
  },

  /**
   * 跳转消息页
   */
  gotoMessage() {
    wx.navigateTo({
      url: '/pages/message/index'
    })
  },

  /**
   * 修改封面
   */
  async changePoster() {
    if (!this.data.user) {
      return
    }
    wx.lin.showMessage({
      content: '设置封面图片'
    })

    // 上传封面
    wxutil.image.choose(1).then(async res => {
      if (res.errMsg !== 'chooseImage:ok') {
        return
      }

      wxutil.showLoading('上传中...')
      await this.initQiniu()
      const poster = await this.sendMedia(res.tempFilePaths[0], 'poster')

      const data = {
        avatar: this.data.user.avatar,
        nickname: this.data.user.nickname,
        signature: this.data.user.signature,
        gender: this.data.user.gender,
        poster: poster
      }
      const info = await User.updateUser(data)
      if (info.code === 2) {
        this.getUserInfo(false)

        wx.lin.showMessage({
          type: 'success',
          content: '封面修改成功！',
        })
      } else {
        wx.lin.showMessage({
          type: 'error',
          content: '封面修改失败！'
        })
      }
      wx.hideLoading()
    })
  },

  /**
   * 修改头像
   */
  changeAvatar(event) {
    if (!this.data.user) {
      return
    }
    wx.lin.showMessage({
      content: '设置头像图片'
    })
    this.setData({
      tmpAvatar: event.detail.detail.avatarUrl,
      showImageClipper: true
    })
  },

  /**
   * 头像裁剪上传
   */
  async onClipTap(event) {
    wxutil.showLoading('上传中...')
    await this.initQiniu()
    const avatar = await this.sendMedia(event.detail.url, 'avatar')

    // 更新用户信息
    const data = {
      avatar: avatar,
      nickname: this.data.user.nickname,
      signature: this.data.user.signature,
      gender: this.data.user.gender
    }
    const res = await User.updateUser(data)
    if (res.code === 2) {
      this.getUserInfo(false)

      wx.lin.showMessage({
        type: 'success',
        content: '头像修改成功！',
      })
    } else {
      wx.lin.showMessage({
        type: 'error',
        content: '头像修改失败！'
      })
    }
    wx.hideLoading()

    this.setData({
      showImageClipper: false,
    })
  },

  /**
   * 触底加载
   */
  async onReachBottom() {
    const tabIndex = this.data.tabIndex
    this.setData({
      loading: true
    })
    if (tabIndex === 0) {
      await this.getMoreTopics(this.data.topicPaging)
    }
    else if (tabIndex === 1) {
      await this.getMoreComments(this.data.commentPaging)
    }
    else if (tabIndex === 2) {
      await this.getMoreStars(this.data.starPaging)
    }
    this.setData({
      loading: false
    })
  },

  /**
   * 删除话题
   */
  deleteTopic(event) {
    const dialog = this.selectComponent('#dialog')

    dialog.linShow({
      type: 'confirm',
      title: '提示',
      content: '确定要删除该话题？',
      success: async (res) => {
        if (res.confirm) {
          const topics = this.data.topics
          const index = event.detail.index

          const res = await Topic.deleteTopic(topics[index].id)
          if (res.code === 3) {
            topics.splice(index, 1)
            this.setData({
              topics: topics
            })

            wx.lin.showMessage({
              type: 'success',
              content: '删除成功！'
            })
          } else {
            wx.lin.showMessage({
              type: 'error',
              content: '删除失败！'
            })
          }
        }
      }
    })
  },

  /**
   * 删除评论
   */
  deleteComment(event) {
    const dialog = this.selectComponent('#dialog')

    dialog.linShow({
      type: 'confirm',
      title: '提示',
      content: '确定要删除该评论？',
      success: async (res) => {
        if (res.confirm) {
          const comments = this.data.comments
          const index = event.detail.index

          const res = await Comment.deleteComment(comments[index].id)
          if (res.code === 3) {
            comments.splice(index, 1)
            this.setData({
              comments: comments
            })

            wx.lin.showMessage({
              type: 'success',
              content: '删除成功！'
            })
          } else {
            wx.lin.showMessage({
              type: 'error',
              content: '删除失败！'
            })
          }
        }
      }
    })
  },

  /**
   * 取消收藏
   */
  deleteStar(event) {
    const dialog = this.selectComponent('#dialog')

    dialog.linShow({
      type: 'confirm',
      title: '提示',
      content: '确定要取消收藏该话题？',
      success: async (res) => {
        if (res.confirm) {
          const stars = this.data.stars
          const index = event.detail.index

          const res = await Star.starOrCancel(stars[index].topic.id)
          if (res.code === 0) {
            stars.splice(index, 1)
            this.setData({
              stars: stars
            })

            wx.lin.showMessage({
              type: 'success',
              content: '取消成功！'
            })
          } else {
            wx.lin.showMessage({
              type: 'error',
              content: '取消失败！'
            })
          }
        }
      }
    })
  },

  onPageScroll(event) {
    if (event.scrollTop >= this.data.tabsTop) {
      this.setData({
        tabsFixed: true
      })
    } else {
      this.setData({
        tabsFixed: false
      })
    }
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.getUserInfo(false)
    this.getMessages()
    wx.stopPullDownRefresh()
    wx.vibrateShort()
  },

  onShareAppMessage() {
    return {
      title: '个人中心',
      path: '/pages/profile/index'
    }
  }
})
