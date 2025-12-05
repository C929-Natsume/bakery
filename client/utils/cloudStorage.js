/**
 * 微信云开发存储上传工具
 */

/**
 * 上传图片到云存储
 * @param {String} filePath 本地临时文件路径
 * @param {String} folder 存储目录，如 'topic', 'avatar' 等
 * @returns {Promise} 返回 {fileID, cloudPath}
 */
export function uploadImage(filePath, folder = 'images') {
  return new Promise((resolve, reject) => {
    wx.cloud.uploadFile({
      cloudPath: `${folder}/${Date.now()}-${Math.random().toString(36).substr(2, 9)}.jpg`,
      filePath: filePath,
      success: res => {
        console.log('云存储上传成功:', res.fileID)
        resolve({
          fileID: res.fileID,
          cloudPath: res.fileID,
          // 云存储URL可以直接使用fileID访问
          url: res.fileID
        })
      },
      fail: err => {
        console.error('云存储上传失败:', err)
        reject(err)
      }
    })
  })
}

/**
 * 批量上传图片
 * @param {Array} filePaths 本地临时文件路径数组
 * @param {String} folder 存储目录
 * @returns {Promise} 返回文件ID数组
 */
export function uploadImages(filePaths, folder = 'images') {
  return Promise.all(filePaths.map(filePath => uploadImage(filePath, folder)))
}

/**
 * 上传视频到云存储
 * @param {String} filePath 本地临时文件路径
 * @param {String} folder 存储目录
 * @returns {Promise} 返回 {fileID, cloudPath}
 */
export function uploadVideo(filePath, folder = 'videos') {
  return new Promise((resolve, reject) => {
    const timestamp = Date.now()
    const randomStr = Math.random().toString(36).substr(2, 9)
    
    wx.cloud.uploadFile({
      cloudPath: `${folder}/${timestamp}-${randomStr}.mp4`,
      filePath: filePath,
      success: res => {
        console.log('云存储视频上传成功:', res.fileID)
        resolve({
          fileID: res.fileID,
          cloudPath: res.fileID,
          url: res.fileID
        })
      },
      fail: err => {
        console.error('云存储视频上传失败:', err)
        reject(err)
      }
    })
  })
}

