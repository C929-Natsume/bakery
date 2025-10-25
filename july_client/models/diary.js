// models/diary.js
import wxutil from '../miniprogram_npm/@yyjeffrey/wxutil/index';
import api from '../config/api';

class Diary {
  /**
   * 获取日记列表
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @param {boolean} isPublic - 是否公开（null=全部）
   */
  static async getDiaryList(year, month, isPublic = null) {
    const params = { year, month };
    if (isPublic !== null) {
      params.is_public = isPublic;
    }
    return await wxutil.request.get(api.diaryAPI, params);
  }

  /**
   * 获取日记详情
   * @param {string} diaryId - 日记ID
   */
  static async getDiaryDetail(diaryId) {
    return await wxutil.request.get(`${api.diaryAPI}/${diaryId}`);
  }

  /**
   * 创建日记
   * @param {string} date - 日期 (YYYY-MM-DD)
   * @param {string} content - 内容
   * @param {string} emotionLabelId - 情绪标签ID
   * @param {boolean} isPublic - 是否公开
   */
  static async createDiary(date, content, emotionLabelId, isPublic = false) {
    return await wxutil.request.post(api.diaryAPI, {
      date,
      content,
      emotion_label_id: emotionLabelId,
      is_public: isPublic
    });
  }

  /**
   * 更新日记
   * @param {string} diaryId - 日记ID
   * @param {string} date - 日期
   * @param {string} content - 内容
   * @param {string} emotionLabelId - 情绪标签ID
   * @param {boolean} isPublic - 是否公开
   */
  static async updateDiary(diaryId, date, content, emotionLabelId, isPublic) {
    return await wxutil.request.put(`${api.diaryAPI}/${diaryId}`, {
      date,
      content,
      emotion_label_id: emotionLabelId,
      is_public: isPublic
    });
  }

  /**
   * 删除日记
   * @param {string} diaryId - 日记ID
   */
  static async deleteDiary(diaryId) {
    return await wxutil.request.delete(`${api.diaryAPI}/${diaryId}`);
  }

  /**
   * 获取日记统计
   * @param {number} year - 年份
   * @param {number} month - 月份
   */
  static async getDiaryStats(year, month) {
    return await wxutil.request.get(`${api.diaryAPI}/stats`, { year, month });
  }
}

export { Diary };

