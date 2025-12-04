import { Mind } from '../../models/mind'

// 湖北省武汉市洪山区华中科技大学附近（备用坐标：定位失败时使用）
const FALLBACK_COORD = { lat: 30.518, lng: 114.414, radius: 3000 }
// 是否强制以华科为中心：现在切换为按设备定位
// 临时开关：开发/调试时可以设为 true 强制使用备用坐标以验证后端
const FORCE_HUST_AS_BASE = true

// 是否使用静态的心理咨询中心列表（绕过 LBS 调用）
const STATIC_NEARBY_ENABLED = true

// 静态机构列表（第一条为华中科技大学心理健康教育中心）
const STATIC_NEARBY = [
  {
    id: 'hust-0001',
    name: '华中科技大学心理健康教育中心',
    address: '湖北省武汉市洪山区珞喻路1037号（华中科技大学）',
    tel: '027-87543567',
    location: { lat: 30.5179, lng: 114.4127 }
  },
  {
    id: '1728896750642733446',
    name: '竹影心理工作室',
    address: '湖北省武汉市洪山区珞南街道泛悦城2期15栋303室',
    tel: '18271489616',
    location: { lat: null, lng: null }
  },
  {
    id: '9308093382902413957',
    name: '安肯心理咨询(光谷华科大店)',
    address: '湖北省武汉市洪山区雄楚大道1008号万科锦程三期1号楼16层办公05A号',
    tel: '',
    location: { lat: null, lng: null }
  },
  {
    id: '1779669497955061739',
    name: '素桐教育|心理健康与咨询',
    address: '湖北省武汉市洪山区长航蓝晶国际B区12栋813',
    tel: '13554064129',
    location: { lat: null, lng: null }
  },
  {
    id: '3389381460974143428',
    name: '同道心理咨询中心',
    address: '湖北省武汉市洪山区柒零社区10栋1单元102室',
    tel: '13808670736',
    location: { lat: null, lng: null }
  }
]

Page({
  data:{
    item:{},
    nearby:{ items: [] },
    radiusOptions: [3000, 5000, 10000],
    radiusIndex: 1, // 默认 5km
    lastCoord: null,
    // 导航失败时在开发者工具内的地图预览
    mapPreview: false,
    mapCenter: null,
    mapMarkers: []
  },
  async onLoad(options){
    const id = options.id
    // 优先从本地缓存读取完整 item（由列表页在跳转前写入），以实现快速且更可靠的正文展示。
    let item = null
    try {
      const cached = wx.getStorageSync('mind_detail_item')
      if (cached && cached.id && String(cached.id) === String(id)) {
        item = cached
      }
    } catch (e) {
      console.warn('read cached mind_detail_item failed', e)
    }
    // 若本地缓存不存在，再请求后端详情；如果后端返回成功则覆盖 cached（以最新为准）
    try {
      const remote = await Mind.getKnowledgeDetail(id)
      if (remote) item = remote
    } catch (e) {
      console.warn('Mind.getKnowledgeDetail failed', e)
    }
    // 将原始正文分段并生成 rich-text 所需的节点结构，避免在页面显示为一整段文字
    const richNodes = []
    try {
      const content = item.content || ''
      // 按连续空行分段（兼容 Windows/Unix 换行）
      const paragraphs = content.split(/\n\s*\n/).filter(p => p && p.trim())
      if (paragraphs.length === 0 && content.trim()) {
        // 若没有双换行但有内容，则按单换行分割
        paragraphs.push(...content.split(/\n/).filter(p => p && p.trim()))
      }
      for (const p of paragraphs) {
        // 按段落内容生成节点（不在文本中插入额外空格，样式可通过 CSS 控制）
        richNodes.push({ name: 'p', attrs: {}, children: [{ type: 'text', text: p.trim() }] })
      }
      // 如果没有任何段落节点，放入一组更合理分段的保底文本（避免一大段）
  if (richNodes.length === 0) {
    const fallbackParagraphs = [
      '焦虑是一种对未来不确定性或潜在威胁的警觉反应，在适度时有助于我们预见风险并做好准备，但当焦虑持续、强烈或超出情境所需，就可能干扰生活与工作。',
      '常见表现包括持续的担忧、注意力难以集中、肌肉紧张、易疲劳、睡眠困难以及心悸或胃肠不适等。引发焦虑的因素既有外在压力（如工作、学习、人际冲突）也有内在因素（如遗传、神经递质波动、认知模式）。',
      '应对焦虑可从认识、认知、行为和生理四个层面入手：允许并接纳情绪，区分合理预警与过度反应；用事实检验自动化的负面想法，逐步纠正灾难化倾向。',
      '实践技巧包括将焦虑任务拆成小步骤并逐步暴露、记录每次成功经验以建立自信；结合规律作息、适度运动和呼吸放松练习来降低生理唤起。若自助方法不足，应主动寻求专业帮助（如认知行为治疗或精神科评估）。'
    ]
    for (const p of fallbackParagraphs) {
      richNodes.push({ name: 'p', attrs: {}, children: [{ type: 'text', text: p }] })
    }
  }
    } catch (e) {
      // 保底解析失败：优先使用缓存中的 item.content（如果有），避免用同一段长文作为所有条目的固定回退。
      try {
        const cachedContent = item && item.content ? item.content : ''
        if (cachedContent && cachedContent.trim()) {
          const paras = cachedContent.split(/\n\s*\n/).filter(p=>p && p.trim())
          for (const p of paras) {
            richNodes.push({ name: 'p', attrs: {}, children: [{ type: 'text', text: p.trim() }] })
          }
        } else {
          // 若无缓存内容，则显示简短占位并在后台重试一次远程请求
          richNodes.push({ name: 'p', attrs: {}, children: [{ type: 'text', text: '内容正在加载，如多次失败请检查网络或稍后重试。' }] })
          // 异步重试一次远端请求（不阻塞界面）
          setTimeout(async ()=>{
            try {
              const remote = await Mind.getKnowledgeDetail(id)
              if (remote && remote.content){
                const paragraphs = remote.content.split(/\n\s*\n/).filter(p=>p&&p.trim())
                const newNodes = []
                for (const p of paragraphs) newNodes.push({ name: 'p', attrs: {}, children: [{ type: 'text', text: p.trim() }] })
                this.setData({ richNodes: newNodes, item: remote })
              }
            }catch(_){}
          }, 1500)
        }
      } catch (e2) {
        richNodes.push({ name: 'p', attrs: {}, children: [{ type: 'text', text: '内容暂不可用' }] })
      }
    }
  this.setData({ item, richNodes })
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
      // 记录失败原因，便于在控制台/DevTools 观察
      console.warn('requestLocation failed:', e)
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
    // 如果启用了静态列表，直接使用静态数据并返回（优先级最高）
    if (STATIC_NEARBY_ENABLED){
      this.setData({ nearby: { items: STATIC_NEARBY } })
      return
    }

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
        // 记录获取位置信息失败的具体原因
        console.warn('fetchNearbyByCurrentRadius getLocation failed:', e)
        coord = { lat: FALLBACK_COORD.lat, lng: FALLBACK_COORD.lng }
        this.setData({ lastCoord: coord })
      }
    }
  const nearby = await Mind.getNearby(coord.lat, coord.lng, radius, '心理咨询')
    this.setData({ nearby })
  },
  async reloadNearby(){
    // 仅重新获取附近机构，不刷新正文
    if (STATIC_NEARBY_ENABLED){
      this.setData({ nearby: { items: STATIC_NEARBY } })
      return
    }

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
    }, fail: async (err)=>{
      // 打印失败原因以便排查（用户拒绝、权限被禁或设备不支持）
      console.warn('reloadNearby getLocation fail:', err)
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
      address: address || '',
      fail: ()=>{
        // DevTools 环境可能不支持直接调起地图，提供地图组件预览兜底
        const center = { lat: Number(lat), lng: Number(lng) }
        const markers = [{ id: 1, latitude: center.lat, longitude: center.lng, title: name || '目的地' }]
        this.setData({ mapPreview: true, mapCenter: center, mapMarkers: markers })
        wx.showToast({ title: '开发者工具不支持导航，已打开地图预览', icon: 'none' })
      }
    })
  },
  closeMapPreview(){ this.setData({ mapPreview: false }) },
  onShareAppMessage(){
    const { item } = this.data
    return { title: item.title || '心灵配方', path: `/pages/mind-recipes/detail?id=${item.id}` }
  }
})
