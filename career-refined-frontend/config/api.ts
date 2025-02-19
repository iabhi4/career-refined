export const API_URL = process.env.NEXT_PUBLIC_API_URL;
export const API_ENDPOINTS = {
    LOGIN: '/token',
    SIGNUP: '/register',
    FORGOT_PASSWORD: '/forgot-password',
    RESET_PASSWORD: '/reset-password',
    USERS: '/users',
    WORK_EXPERIENCE: '/work_experience',
    EDUCATION: '/education',
    PROJECTS: '/projects',
    LOGOUT: '/logout',
}

export const axiosConfig = {
    baseURL: API_URL,
    withCredentials: true, // Important for cookies
    headers: {
      'Content-Type': 'application/json',
    },
  };