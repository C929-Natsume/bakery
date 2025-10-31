// cocobegin
// models/soul.js
import api from '../config/api'
import wxutil from '../miniprogram_npm/@yyjeffrey/wxutil/index'

class Soul {
  /**
   * 获取随机心灵鸡汤
   */
  static async getRandom() {
    const res = await wxutil.request.get(`${api.soulAPI}/random`)
    if (res.code === 0) {
      return res.data
    }
    return null
  }

  /**
   * 获取每日推送
   */
  static async getDaily() {
    const res = await wxutil.request.get(`${api.soulAPI}/daily`)
    if (res.code === 0) {
      return res.data
    }
    return null
  }

  /**
   * 生成推送（基于特定内容）
   */
  static async generatePush(data) {
    return await wxutil.request.post(`${api.soulAPI}/push`, data)
  }

  /**
   * 收藏/取消收藏推送
   */
  static async toggleCollect(pushId) {
    return await wxutil.request.post(`${api.soulAPI}/push/${pushId}/collect`)
  }

  /**
   * 获取推送历史
   */
  static async getHistory(params = {}) {
    const res = await wxutil.request.get(`${api.soulAPI}/history`, params)
    if (res.code === 0) {
      return res.data
    }
    return null
  }

  /**
 * 保存自定义句子
 */
  static async saveCustom(content) {
    return await wxutil.request.post(`${api.soulAPI}/custom`, { content })
  }

  /**
   * 删除自定义句子
   */
  static async deleteCustom(pushId) {
    return await wxutil.request.delete(`${api.soulAPI}/custom/${pushId}`)
  }

  /**
   * 获取自定义句子列表
   */
  static async getCustomList(params = {}) {
    const res = await wxutil.request.get(`${api.soulAPI}/custom/list`, params)
    if (res.code === 0) {
      return res.data
    }
    return null
  }

  /**
   * 从公共句子库获取随机句子
   * @param {string} emotionLabelId - 可选的情绪标签ID
   */
  static async getPublicRandom(emotionLabelId = null) {
    const params = emotionLabelId ? { emotion_label_id: emotionLabelId } : {}
    const res = await wxutil.request.get(`${api.soulAPI}/public/random`, params)
    if (res.code === 0) {
      return res
    }
    return null
  }

  /**
   * 根据情绪标签获取公共句子
   * @param {string} emotionLabelId - 情绪标签ID
   */
  static async getPublicByEmotion(emotionLabelId) {
    const res = await wxutil.request.get(`${api.soulAPI}/public/emotion/${emotionLabelId}`)
    if (res.code === 0) {
      return res
    }
    return null
  }
}

export { Soul }

// cocoend