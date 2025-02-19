import { z } from 'zod';
import { 
  loginSchema, 
  signupSchema, 
  forgotPasswordSchema, 
  resetPasswordSchema 
} from '@/schemas/auth';

export type LoginFormValues = z.infer<typeof loginSchema>;
export type SignupFormValues = z.infer<typeof signupSchema>;
export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

export interface SignupRequest {
    name: string;
    email: string;
    password: string;
}

export interface AuthResponse {
  user_id: number;
  is_onboarded: boolean;
}