import { Mind } from '../../models/mind'

Page({
  data:{ id:'', title:'', category:'', tagsStr:'', source:'', content:'' },
  async onLoad(options){
    if(options && options.id){
      const item = await Mind.getKnowledgeDetail(options.id)
      if(item){
        this.setData({
          id: item.id,
          title: item.title || '',
          category: item.category || '',
          source: item.source || '',
          content: item.content || '',
          tagsStr: (item.tags||[]).join(',')
        })
        wx.setNavigationBarTitle({ title: '编辑配方' })
      }
    }else{
      wx.setNavigationBarTitle({ title: '新增配方' })
    }
  },
  bindInput(e){
    const key = e.currentTarget.dataset.key
    this.setData({ [key]: e.detail.value })
  },
  async save(){
    const { id, title, category, source, content, tagsStr } = this.data
    if(!title || !content){ return wx.showToast({ title:'标题/内容必填', icon:'none' }) }
    const data = { title, category, source, content, tags: tagsStr }
    let res
    if(id){ res = await Mind.updateKnowledge(id, data) }
    else{ res = await Mind.createKnowledge(data) }
    if(res && (res.code===0 || res.msg)){
      wx.showToast({ title:'已保存', icon:'success' })
      setTimeout(()=> wx.navigateBack(), 600)
    }else{
      wx.showToast({ title: (res && res.msg) || '保存失败', icon:'none' })
    }
  },
  async remove(){
    const { id } = this.data
    if(!id) return
    wx.showModal({ title:'删除确认', content:'确定要删除该内容吗？', success: async (r)=>{
      if(r.confirm){
        const res = await Mind.deleteKnowledge(id)
        if(res && res.code===0){ wx.showToast({ title:'已删除', icon:'success' }); setTimeout(()=> wx.navigateBack(), 600) }
        else { wx.showToast({ title: (res && res.msg) || '删除失败', icon:'none' }) }
      }
    } })
  }
})
