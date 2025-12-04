import { Mind } from '../../models/mind'

Page({
  data:{ items: [], paging: null, hasMore: true, loading: false },
  async onLoad(){
    const paging = await Mind.getMyStarPaging({})
    this.setData({ paging })
    await this.getMore()
  },
  async getMore(){
    const { paging } = this.data
    if (!paging) return
    this.setData({ loading: true })
    const data = await paging.getMore()
    if (data){ this.setData({ items: data.accumulator, hasMore: data.hasMore }) }
    this.setData({ loading: false })
  },
  async onReachBottom(){ await this.getMore() },
  gotoDetail(e){
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/mind-recipes/detail?id=${id}` })
  }
})
