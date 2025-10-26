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
    const meta = await Mind.getMeta()
    this.setData({ categories: meta.categories || [], tags: meta.tags || [] })
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
    const data = await paging.getMore()
    if (data) {
      this.setData({ items: data.accumulator, hasMore: data.hasMore })
    }
    this.setData({ loading: false })
  },
  async onReachBottom() { await this.getMore() },
  gotoDetail(e) {
    const id = e.currentTarget.dataset.id
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
