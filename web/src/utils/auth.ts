const TOKEN_KEY = 'token';

const isLogin = () => {
  // 检查 localStorage 或 sessionStorage 中是否有 token
  return !!(
    localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
  );
};

const getToken = () => {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
};

const setToken = (token: string) => {
  // 根据 userInfo 的存储位置来决定 token 的存储位置
  // 如果 localStorage 中有 userInfo，则 token 也存到 localStorage
  // 否则存到 sessionStorage
  if (localStorage.getItem('userInfo')) {
    localStorage.setItem(TOKEN_KEY, token);
  } else if (sessionStorage.getItem('userInfo')) {
    sessionStorage.setItem(TOKEN_KEY, token);
  } else {
    // 默认存储到 localStorage
    localStorage.setItem(TOKEN_KEY, token);
  }
};

const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
};

export { isLogin, getToken, setToken, clearToken };
