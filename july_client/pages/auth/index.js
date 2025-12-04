// pages/auth/index.js
import wxutil from '../../miniprogram_npm/@yyjeffrey/wxutil/index'
import { Auth } from '../../models/auth'
const app = getApp()

Page({
  data: {
    code: null,
    goto: null
  },

  onLoad(options) {
    if (options.goto) {
      this.setData({
        goto: decodeURIComponent(options.goto)
      })
    }
    this.getCode()
  },

  /**
   * 获取小程序code
   */
  getCode() {
    wx.login({
      success: (res) => {
        this.setData({
          code: res.code
        })
      }
    })
  },

  /**
   * 主动授权登录
   */
  auth() {
    app.globalData.userDetail = null
    
    // 先获取新的 code
    this.getCode()

    wx.getUserProfile({
      desc: '授权信息将用于绑定用户',
      lang: 'zh_CN',
      success: async (res) => {
        try {
          const data = {
            encrypted_data: res.encryptedData,
            iv: res.iv,
            code: this.data.code,
            app_id: app.globalData.appId
          }

          const info = await Auth.initiative(data)
          if (info.code === 0) {
            const userDetail = info.data
            wxutil.setStorage('userDetail', userDetail, app.globalData.tokenExpires)
            app.globalData.userDetail = userDetail

            // 先执行跳转
            if (this.data.goto) {
              wx.redirectTo({
                url: this.data.goto
              })
            } else {
              wx.navigateBack()
            }
            
            // 显示成功消息（不依赖回调）
            wx.lin.showMessage({
              type: 'success',
              content: '授权成功'
            })
          } else {
            wx.lin.showMessage({
              type: 'error',
              content: info.msg || '授权失败，请重试'
            })
          }
        } catch (err) {
          console.error('授权请求失败:', err)
          wx.lin.showMessage({
            type: 'error',
            content: '网络请求失败，请检查网络后重试'
          })
        }
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err)
        wx.lin.showMessage({
          type: 'error',
          content: '获取用户信息失败，请重试'
        })
      },
      complete: () => {
        // complete 中不再调用 getCode()，因为已经提前调用了
      }
    })
  },

  onShareAppMessage() {
    return {
      title: '授权',
      path: '/pages/auth/index'
    }
  }
})
