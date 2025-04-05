export const API_URL = process.env.NEXT_PUBLIC_API_URL;
export const API_ENDPOINTS = {
    LOGIN: '/token',
    SIGNUP: '/register',
    FORGOT_PASSWORD: '/forgot-password',
    RESET_PASSWORD: '/reset-password',
    USERS: '/users',
    PROFILE: '/profile-data',
    WORK_EXPERIENCE: '/work_experience',
    EDUCATION: '/education',
    PROJECTS: '/projects',
    SKILLS: '/skills',
    LANGUAGES: '/languages',
    CERTIFICATIONS: '/certifications',
    LOGOUT: '/logout',
    APPLICATIONS: '/applications/create-and-analyze',
    PROJECTS_AND_EXPERIENCES: '/projects-and-experiences',
    EDITOR_DATA: '/editor-data',
    EDITOR_DATA_FOR_FIRST_TIME: '/editor-data-new',
    PDF_STATUS: '/pdf-status',
    TRACKER_DATA: '/tracker-data',
    MANUAL_APPLICATION: '/manual-application',
    CSV: '/csv',
}

export const axiosConfig = {
    baseURL: API_URL,
    withCredentials: true, // Important for cookies
    headers: {
      'Content-Type': 'application/json',
    },
  };