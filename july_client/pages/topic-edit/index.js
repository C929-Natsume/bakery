// pages/topic-edit/index.js
import api from '../../config/api'
import template from '../../config/template'
import wxutil from '../../miniprogram_npm/@yyjeffrey/wxutil/index'
import { uploadImage, uploadImages, uploadVideo } from '../../utils/cloudStorage'
import { Label } from '../../models/label'
import { Topic } from '../../models/topic'
import { Video } from '../../models/video'

Page({
  data: {
    labels: [],
    imageFiles: [],
    labelsActive: [], // 选中的标签
    height: 1000,  // 内容区高度
    canAnon: false, // 是否可匿名
    isAnon: false,  // 是否为匿名话题
    content: null,
    video: null,
    // Week 2新增：情绪标签
    selectedEmotionId: '',
    selectedEmotionName: ''
  },

  onLoad() {
    this.getLabels()
    this.getScrollHeight()
  },

  /**
   * 获取窗口高度
   */
  getScrollHeight() {
    const systemInfo = wx.getSystemInfoSync()
    const windowHeight = systemInfo.windowHeight

    const query = wx.createSelectorQuery()
    query.select('.btn-send').boundingClientRect(rect => {
      const btnHeight = rect.height
      this.setData({
        height: windowHeight - btnHeight
      })
    }).exec()
  },

  /**
   * 获取标签
   */
  async getLabels() {
    const data = await Label.getLabelList()
    this.setData({
      labels: data
    })
  },


  /**
   * 设置内容
   */
  setContent(event) {
    this.setData({
      content: event.detail.value
    })
  },

  /**
   * 设置匿名
   */
  onAnonTap(event) {
    this.setData({
      isAnon: event.detail.checked
    })
  },

  /**
   * Week 2新增：选择情绪标签
   */
  onEmotionSelect(e) {
    const { id, name } = e.detail;
    console.log('选中情绪标签 ID:', id, '名称:', name);  // 添加这行
    
    this.setData({
      selectedEmotionId: id,
      selectedEmotionName: name
    });
  },

  /**
   * 选择图片
   */
  onChangeImage(event) {
    this.setData({
      imageFiles: event.detail.all
    })
  },

  /**
   * 选择标签
   */
  onTagTap(event) {
    const labelId = event.currentTarget.dataset.label
    const labels = this.data.labels
    let labelsActive = this.data.labelsActive
    let canAnon = true

    // 当前标签
    const label = labels.find(item => {
      return item.id === labelId
    })

    if (!label.active && labelsActive.length >= 3) {
      wx.lin.showMessage({
        type: 'error',
        content: '最多选择3个标签！'
      })
      return
    }
    label.active = !label.active

    // 激活的标签
    labelsActive = []
    labels.forEach(item => {
      if (item.active) {
        labelsActive.push(item.id)
        if (!item.allowed_anon) {
          canAnon = false
        }
      }
    })

    if (labelsActive.length === 0) {
      canAnon = false
    }

    this.setData({
      labels: labels,
      labelsActive: labelsActive,
      canAnon: canAnon
    })
  },

  /**
   * 多图上传到云存储
   */
  async sendImages(imageFiles) {
    try {
      const results = await uploadImages(imageFiles, 'topic')
      return results.map(r => r.url)
    } catch (error) {
      console.error('批量上传图片失败:', error)
      throw error
    }
  },

  /**
   * 上传单张图片到云存储
   */
  async sendMedia(imageFile, path = 'topic') {
    try {
      const result = await uploadImage(imageFile, path)
      return result.url
    } catch (error) {
      console.error('上传图片失败:', error)
      throw error
    }
  },

  /**
   * 选择视频
   */
  onChangeVideo() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['video'],
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      camera: 'back',
      success: (res) => {
        const videoRes = res.tempFiles[0]
        this.setData({
          video: {
            src: videoRes.tempFilePath,
            cover: videoRes.thumbTempFilePath,
            duration: videoRes.duration,
            height: videoRes.height,
            width: videoRes.width,
            size: videoRes.size,
          }
        })
      }
    })
  },

  /**
   * 删除视频
   */
  onDelVideo() {
    this.setData({
      video: null
    })
  },

  /**
   * 点击发布
   */
  sumitTopic() {
    const content = this.data.content

    if (!wxutil.isNotNull(content)) {
      wx.lin.showMessage({
        type: 'error',
        content: '内容不能为空！'
      })
      return
    }

    const imageFiles = this.data.imageFiles
    let video = this.data.video

    // 授权订阅消息
    wx.requestSubscribeMessage({
      tmplIds: [template.messageTemplateId],
      complete: async () => {
        wxutil.showLoading('发布中...')
        console.log('准备发布，emotion_label_id:', this.data.selectedEmotionId);  // 添加这行
        const data = {
          content: content,
          is_anon: this.data.isAnon,
          images: [],
          labels: this.data.labelsActive,
          emotion_label_id: this.data.selectedEmotionId || null  // Week 2新增
        }
        console.log('发布数据:', JSON.stringify(data));  // 添加这行
        // 发布图文
        if (imageFiles.length > 0) {
          try {
            const imageUrls = await this.sendImages(imageFiles)
            data.images = imageUrls
            this.uploadTopic(data)
          } catch (error) {
            wx.hideLoading()
            wx.lin.showMessage({
              type: 'error',
              content: '图片上传失败，请重试'
            })
          }
        }
        // 发布视文
        else if (video) {
          try {
            const videoResult = await uploadVideo(video.src, 'video')
            const coverResult = await uploadImage(video.cover, 'video-cover')
            video.src = videoResult.url
            video.cover = coverResult.url
            this.setData({ video: video })
            const res = await Video.uploadVideo(video)
            if (res.code === 1) {
              data.video_id = res.data.video_id
              this.uploadTopic(data)
            }
          } catch (error) {
            wx.hideLoading()
            wx.lin.showMessage({
              type: 'error',
              content: '视频上传失败，请重试'
            })
          }
        }
        // 发布纯文
        else {
          this.uploadTopic(data)
        }
      }
    })
  },

  /**
   * 上传话题
   */
  async uploadTopic(data) {
    console.log('=== 开始上传话题 ===');
    console.log('上传数据:', JSON.stringify(data));
    
    const res = await Topic.sendTopic(data)
    
    console.log('=== 后端响应 ===');
    console.log('完整响应:', JSON.stringify(res));
    console.log('res.code:', res.code);
    console.log('res.msg:', res.msg);
    console.log('res.data:', res.data);
    
    wx.hideLoading()
    if (res.code === 1) {
      console.log('✅ 判断为成功，准备显示成功提示');
      wx.lin.showMessage({
        type: 'success',
        content: '发布成功！',
        success: () => {
          wxutil.setStorage('refreshTopics', true)
          wx.navigateBack()
        }
      })
    } else {
      console.log('❌ 判断为失败，res.code =', res.code);
      wx.lin.showMessage({
        type: 'error',
        content: `发布失败！错误码: ${res.code}, 消息: ${res.msg}`
      })
    }
  },

  onShareAppMessage() {
    return {
      title: '主页',
      path: '/pages/topic/index'
    }
  }
})
