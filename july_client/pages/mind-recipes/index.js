import { Mind } from '../../models/mind'

Page({
  data: {
    items: [],
    paging: null,
    hasMore: true,
    loading: false,
    keyword: '',
    category: '',
    tag: '',
    categories: [],
    tags: []
  },
  async onLoad() {
    await this.loadMeta()
    await this.reload()
  },
  async loadMeta(){
    let meta = { categories: [], tags: [] }
    try {
      meta = await Mind.getMeta()
    } catch (err) {
      // 请求失败也要继续走本地回退，避免页面空白
      console.warn('[mind-recipes] loadMeta failed:', err)
    }
    // log meta for debugging when tags/categories appear missing in the UI
    console.log('[mind-recipes] meta:', meta)
    // 如果后端没有返回 categories，则使用本地 fallback（仅用于本地开发调试）
    const fallbackCategories = ['焦虑','科普','抑郁','求助','睡眠','行为建议']
    const categories = (meta && Array.isArray(meta.categories) && meta.categories.length > 0) ? meta.categories : fallbackCategories
    const tags = (meta && Array.isArray(meta.tags) && meta.tags.length > 0) ? meta.tags : ['#焦虑','#科普','#抑郁']
    this.setData({ categories, tags })
  },
  async reload(){
    const { keyword, category, tag } = this.data
    const paging = await Mind.getKnowledgePaging({ keyword, category, tag })
    this.setData({ paging, items: [], hasMore: true })
    await this.getMore()
  },
  async getMore() {
    const { paging } = this.data
    if (!paging) return
    this.setData({ loading: true })
    let data = null
    try {
      data = await paging.getMore()
      if (data) {
        this.setData({ items: data.accumulator, hasMore: data.hasMore })
      }
    } catch (e) {
      console.warn('[mind-recipes] getMore failed:', e)
      // 临时本地 fallback：在后端不可用时快速显示几条示例知识，确保页面不一直加载空白
      const fallbackItems = [
        { id: 'local-1', title: '认识焦虑：症状与自助方法', content: '焦虑是一种常见情绪……（示例正文）', category: '焦虑', tag: '科普', starred: false },
        { id: 'local-2', title: '睡眠问题的认知行为建议', content: '良好的睡眠习惯包括……（示例正文）', category: '睡眠', tag: '技巧', starred: false }
      ]
      this.setData({ items: fallbackItems, hasMore: false })
    }
    this.setData({ loading: false })
  },
  async onReachBottom() { await this.getMore() },
  gotoDetail(e) {
    const id = e.currentTarget.dataset.id
    // 在跳转前把当前 item 缓存到本地存储，避免在 detail 页面因后端未返回正文而空白
    try {
      const item = this.data.items.find(it => it.id === id)
      if (item) wx.setStorageSync('mind_detail_item', item)
    } catch (e) {
      console.warn('gotoDetail setStorageSync failed', e)
    }
    wx.navigateTo({ url: `/pages/mind-recipes/detail?id=${id}` })
  },
  onPullDownRefresh() {
    this.reload(); wx.stopPullDownRefresh(); wx.vibrateShort()
  },
  onInput(e){ this.setData({ keyword: e.detail.value }) },
  onSearch(){ this.reload() },
  selectCategory(e){
    const c = e.currentTarget.dataset.value
    this.setData({ category: this.data.category === c ? '' : c })
    this.reload()
  },
  selectTag(e){
    const t = e.currentTarget.dataset.value
    this.setData({ tag: this.data.tag === t ? '' : t })
    this.reload()
  },
  gotoStars(){ wx.navigateTo({ url: '/pages/mind-recipes/stars' }) }
})
