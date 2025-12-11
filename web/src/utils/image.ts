/**
 * 图片URL处理工具
 */

/**
 * 获取完整的图片URL
 * @param url 图片URL（可能是相对路径或绝对路径）
 * @returns 完整的图片URL
 */
export function getImageUrl(url: string | null | undefined): string {
  if (!url) {
    return '';
  }

  // 如果已经是完整的URL（http://或https://开头），直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // 如果是以 // 开头的协议相对URL，直接返回
  if (url.startsWith('//')) {
    return url;
  }

  // 如果是相对路径（如 /uploads/avatars/xxx.jpg），需要拼接后端服务器地址
  if (url.startsWith('/uploads/')) {
    // 获取后端服务器地址
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    return `${baseURL}${url}`;
  }

  // 其他情况，返回原URL
  return url;
}

/**
 * 获取头像URL
 * @param avatar 头像路径
 * @returns 完整的头像URL
 */
export function getAvatarUrl(avatar: string | null | undefined): string {
  return getImageUrl(avatar);
}

