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

  /**
   * 智能推送 - 根据识别出的情绪标签智能推送鸡汤句子
   * 自动识别用户最近的情绪标签并推送匹配的句子
   */
  static async getSmartPush() {
    const res = await wxutil.request.get(`${api.soulAPI}/smart`)
    if (res.code === 0) {
      return res
    }
    return null
  }

  /**
   * 根据已识别的情绪标签，获取数据库中的另一条句子（换一条）
   * @param {string} emotionLabelId - 情绪标签ID
   * @param {string} excludePushId - 要排除的句子ID（可选）
   */
  static async getAnotherSmartPush(emotionLabelId, excludePushId = null) {
    const params = { emotion_label_id: emotionLabelId }
    if (excludePushId) {
      params.exclude_push_id = excludePushId
    }
    const res = await wxutil.request.get(`${api.soulAPI}/smart/another`, params)
    if (res.code === 0) {
      return res
    }
    return null
  }
}

export { Soul }

// cocoend