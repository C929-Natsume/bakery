import { Mind } from '../../models/mind'

// 湖北省武汉市洪山区华中科技大学附近（备用坐标：定位失败时使用）
const FALLBACK_COORD = { lat: 30.518, lng: 114.414, radius: 3000 }
// 是否强制以华科为中心：现在切换为按设备定位
const FORCE_HUST_AS_BASE = false

Page({
  data:{
    item:{},
    nearby:{ items: [] },
    radiusOptions: [3000, 5000, 10000],
    radiusIndex: 1, // 默认 5km
    lastCoord: null
  },
  async onLoad(options){
    const id = options.id
    const item = await Mind.getKnowledgeDetail(id)
    this.setData({ item })
    if (FORCE_HUST_AS_BASE){
      // 统一以华中科技大学为中心检索（仅当强制开关为 true 时）
      this.setData({ lastCoord: { lat: FALLBACK_COORD.lat, lng: FALLBACK_COORD.lng } })
      await this.fetchNearbyByCurrentRadius()
      return
    }
    // 默认：按设备定位
    try {
      const res = await this.requestLocation()
      const { latitude, longitude } = res
      this.setData({ lastCoord: { lat: latitude, lng: longitude } })
    } catch (e){
      // 用户拒绝或无法获取时，提示打开设置，并使用备用坐标
      wx.showModal({
        title: '需要定位权限',
        content: '用于展示你附近的心理咨询点，可在设置中开启“位置信息”。',
        confirmText: '去开启',
        cancelText: '暂不',
        success: (r)=>{
          if (r.confirm){ wx.openSetting({}) }
        }
      })
      this.setData({ lastCoord: { lat: FALLBACK_COORD.lat, lng: FALLBACK_COORD.lng } })
      wx.showToast({ title: '定位不可用，已使用备用位置', icon: 'none' })
    }
    await this.fetchNearbyByCurrentRadius()
  },
  requestLocation(){
    return new Promise((resolve, reject)=>{
      wx.getLocation({ type: 'gcj02', isHighAccuracy: true, success: resolve, fail: reject })
    })
  },
  getRadius(){
    // 固定华科为中心时，优先使用 FALLBACK_COORD.radius 作为检索半径
    if (FORCE_HUST_AS_BASE) return FALLBACK_COORD.radius
    return this.data.radiusOptions[this.data.radiusIndex] || 5000
  },
  async fetchNearbyByCurrentRadius(){
    const radius = this.getRadius()
    let coord = this.data.lastCoord
    if (!coord){
      try{
        const res = await new Promise((resolve, reject)=>{
          wx.getLocation({ type: 'gcj02', isHighAccuracy: true, success: resolve, fail: reject })
        })
        const { latitude, longitude } = res
        coord = { lat: latitude, lng: longitude }
        this.setData({ lastCoord: coord })
      }catch(e){
        coord = { lat: FALLBACK_COORD.lat, lng: FALLBACK_COORD.lng }
        this.setData({ lastCoord: coord })
      }
    }
  const nearby = await Mind.getNearby(coord.lat, coord.lng, radius, '心理咨询')
    this.setData({ nearby })
  },
  async reloadNearby(){
    // 仅重新获取附近机构，不刷新正文
    if (FORCE_HUST_AS_BASE){
      this.setData({ lastCoord: { lat: FALLBACK_COORD.lat, lng: FALLBACK_COORD.lng } })
      await this.fetchNearbyByCurrentRadius()
      return
    }
    if (this.data.lastCoord){
      await this.fetchNearbyByCurrentRadius()
      return
    }
    wx.getLocation({ type: 'gcj02', isHighAccuracy: true, success: async (res)=>{
      const { latitude, longitude } = res
      this.setData({ lastCoord: { lat: latitude, lng: longitude } })
      await this.fetchNearbyByCurrentRadius()
    }, fail: async ()=>{
      wx.showModal({
        title: '需要定位权限',
        content: '用于展示你附近的心理咨询点，可在设置中开启“位置信息”。',
        confirmText: '去开启',
        cancelText: '暂不',
        success: (r)=>{ if (r.confirm) wx.openSetting({}) }
      })
      this.setData({ lastCoord: { lat: FALLBACK_COORD.lat, lng: FALLBACK_COORD.lng } })
      await this.fetchNearbyByCurrentRadius()
      wx.showToast({ title: '定位不可用，已使用备用位置', icon: 'none' })
    } })
  },
  async toggleStar(){
    const { item } = this.data
    if (!item || !item.id) return
    try {
      const res = await Mind.starOrCancel(item.id)
      if (res && res.code === 0){
        item.starred = !item.starred
        this.setData({ item })
        wx.showToast({ title: item.starred ? '已收藏' : '已取消', icon: 'success' })
      } else {
        wx.showToast({ title: (res && res.msg) ? res.msg : '操作失败', icon: 'none' })
      }
    } catch (e){
      // 未登录或服务器拒绝时，友好提示（避免控制台大量 500 红字）
      wx.showToast({ title: '请先登录后再收藏', icon: 'none' })
    }
  },
  callTel(e){
    const tel = e.currentTarget.dataset.tel
    if (!tel) return
    wx.makePhoneCall({ phoneNumber: tel })
  },
  copyTel(e){
    const tel = e.currentTarget.dataset.tel
    if (!tel) return
    wx.setClipboardData({ data: tel })
  },
  selectRadius(e){
    const idx = Number(e.currentTarget.dataset.index)
    if (isNaN(idx) || idx === this.data.radiusIndex) return
    this.setData({ radiusIndex: idx })
    this.fetchNearbyByCurrentRadius()
  },
  openMap(e){
    const { lat, lng, name, address } = e.currentTarget.dataset
    if (lat == null || lng == null || lat === '' || lng === ''){
      wx.showToast({ title: '缺少坐标，无法导航', icon: 'none' });
      return
    }
    wx.openLocation({
      latitude: Number(lat),
      longitude: Number(lng),
      name: name || '目的地',
      address: address || ''
    })
  },
  onShareAppMessage(){
    const { item } = this.data
    return { title: item.title || '心灵配方', path: `/pages/mind-recipes/detail?id=${item.id}` }
  }
})
