import api from '../config/api'
import wxutil from '../miniprogram_npm/@yyjeffrey/wxutil/index'
import { Paging } from '../utils/paging'

class Mind {
  // 列表分页
  static async getKnowledgePaging(params) {
    return new Paging(api.mindAPI + '/knowledge', params)
  }

  // 详情
  static async getKnowledgeDetail(id) {
    const res = await wxutil.request.get(`${api.mindAPI}/knowledge/${id}`)
    if (res && res.code === 0) return res.data
    return null
  }

  // 附近机构
  static async getNearby(lat, lng, radius = 3000, keyword = '心理咨询,心理咨询中心') {
    const res = await wxutil.request.get(`${api.mindAPI}/nearby`, { lat, lng, radius, keyword })
    if (res && res.code === 0) return res.data
    return { items: [], source: 'mock' }
  }

  static async starOrCancel(id){
    return await wxutil.request.post(`${api.mindAPI}/star`, { knowledge_id: id })
  }

  // 元数据：分类与热门标签
  static async getMeta(){
    const res = await wxutil.request.get(`${api.mindAPI}/meta`)
    if (res && res.code === 0) return res.data
    return { categories: [], tags: [] }
  }

  // 我的收藏分页
  static getMyStarPaging(params={}){
    return new Paging(api.mindAPI + '/star/mine', params)
  }

  // 管理：新增
  static async createKnowledge(data){
    return await wxutil.request.post(`${api.mindAPI}/knowledge`, data)
  }
  // 管理：更新
  static async updateKnowledge(id, data){
    return await wxutil.request.put(`${api.mindAPI}/knowledge/${id}`, data)
  }
  // 管理：删除
  static async deleteKnowledge(id){
    return await wxutil.request.delete(`${api.mindAPI}/knowledge/${id}`)
  }
}

export { Mind }
