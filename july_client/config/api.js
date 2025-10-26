const baseAPI = 'http://127.0.0.1:8000/v2'
const socketAPI = 'ws://127.0.0.1:8000/ws'
const ossDomain = 'https://t4dbz3ztq.hd-bkt.clouddn.com'

export default {
  baseAPI, // 根接口
  socketAPI: socketAPI, // Socket接口
  ossDomain: ossDomain, // 对象存储域名
  mindAPI: baseAPI + '/mind', // 心灵配方根路径
  authAPI: baseAPI + '/auth', // 授权接口
  chatResAPI: baseAPI + '/chat', // 聊天记录接口
  commentAPI: baseAPI + '/comment', // 评论接口
  followingAPI: baseAPI + '/following', // 关注接口
  holeAPI: baseAPI + '/hole', // 树洞接口
  labelAPI: baseAPI + '/label', // 标签接口
  messageAPI: baseAPI + '/message', // 消息接口
  ossAPI: baseAPI + '/oss', // 对象存储接口
  starAPI: baseAPI + '/star', // 收藏接口
  topicAPI: baseAPI + '/topic', // 话题接口
  userAPI: baseAPI + '/user', // 用户接口
  videoAPI: baseAPI + '/video', // 视频接口
  chatAPI: socketAPI + '/chat', // 聊天室接口
  // Week 2 新增接口
  emotionAPI: baseAPI + '/emotion', // 情绪标签接口
  diaryAPI: baseAPI + '/diary', // 日记接口
  soulAPI: baseAPI + '/soul' // 心灵鸡汤接口
}
