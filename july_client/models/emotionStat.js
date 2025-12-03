// models/emotionStat.js
import { Paging } from '../utils/paging'
import api from '../config/api'
import wxutil from '../miniprogram_npm/@yyjeffrey/wxutil/index'

class EmotionStat {
  /**
   * 获取情绪统计分页
   */
  static async getEmotionStatPaging(params) {
    return new Paging(api.emotionAPI + '/stat', params)
  }

  /**
   * 获取图表数据
   */
  static async getCharts(params) {
    try {
      // 使用 /stat 端点获取数据，该端点返回 distribution 和 trend
      const res = await wxutil.request.get(api.emotionAPI + '/stat', params)
      if (res.code === 0) {
        // 提取图表需要的数据
        return {
          distribution: res.data.distribution || [],
          trend: res.data.trend || {}
        }
      } else {
        throw new Error(res.msg || '获取图表数据失败')
      }
    } catch (error) {
      console.error('获取图表数据失败:', error)
      throw error
    }
  }

  /**
   * 删除情绪统计
   */
  static async deleteEmotionStat(id) {
    try {
      const res = await wxutil.request.delete(api.emotionAPI + '/stat/' + id)
      return res
    } catch (error) {
      console.error('删除情绪统计失败:', error)
      throw error
    }
  }

  /**
   * 获取情绪波动数据
   */
  static async getWaveData(params) {
    try {
      const res = await wxutil.request.get(api.emotionAPI + '/wave', params)
      if (res.code === 0) {
        return res.data
      } else {
        throw new Error(res.msg || '获取波动数据失败')
      }
    } catch (error) {
      console.error('获取波动数据失败:', error)
      throw error
    }
  }

  /**
   * 获取情绪分布
   */
  static async getDistribution(params) {
    try {
      const res = await wxutil.request.get(api.emotionAPI + '/stat', params)
      if (res.code === 0) {
        return res.data.distribution
      } else {
        throw new Error(res.msg || '获取分布数据失败')
      }
    } catch (error) {
      console.error('获取分布数据失败:', error)
      throw error
    }
  }
}

export { EmotionStat }