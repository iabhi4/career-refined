import axios from 'axios';
import { API_URL, API_ENDPOINTS, axiosConfig } from '@/config/api';
import { LoginFormValues, SignupFormValues, AuthResponse, SignupRequest } from '@/types/auth';

// Configure axios to include credentials
const axiosInstance = axios.create(axiosConfig);

export class AuthService {
  static async login(credentials: LoginFormValues): Promise<AuthResponse> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await axiosInstance.post<AuthResponse>(
        API_ENDPOINTS.LOGIN,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  static async signup(credentials: SignupRequest): Promise<AuthResponse> {
    try {
      const response = await axiosInstance.post<AuthResponse>(
        API_ENDPOINTS.SIGNUP, 
        credentials
      );
      return response.data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  }

  static async logout(): Promise<void> {
    try {
      await axiosInstance.post(API_ENDPOINTS.LOGOUT);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }
}