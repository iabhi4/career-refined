import * as z from "zod";

export const loginSchema = z.object({
  email: z.string().email("Invalid email address").max(100, "Email too long"),
  password: z.string().min(6, "Password must be at least 6 characters").max(128, "Password too long"),
});

export const signupSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Invalid email address").max(100, "Email too long"),
    password: z.string().min(6, "Password must be at least 6 characters").max(128, "Password too long"),
    confirmPassword: z.string().min(6, "Password must be at least 6 characters").max(128, "Password too long"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export const forgotPasswordSchema = z.object({
  email: z.string().email("Invalid email address").max(100, "Email too long"),
});

export const resetPasswordSchema = z
  .object({
    password: z.string().min(6, "Password must be at least 6 characters").max(128, "Password too long"),
    confirmPassword: z.string().min(6, "Password must be at least 6 characters").max(128, "Password too long"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });