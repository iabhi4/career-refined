"use client";

import Link from "next/link";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// react-hook-form + zod
import { useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth";
import { AuthService } from "@/services/auth";
import axios from "axios";
import { loginSchema } from "@/schemas/auth";
import { LoginFormValues } from "@/types/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      const response = await AuthService.login({
        email: data.email,
        password: data.password,
      });

      // Update auth context
      login(response.user_id, response.is_onboarded);

      toast({
        title: "Login successful!",
        description: "Welcome back!",
        duration: 3000,
      });

      // Redirect based on onboarding status
      if (!response.is_onboarded) {
        router.push('/onboarding');
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      toast({
        title: "Login failed",
        description: axios.isAxiosError(error)
          ? error.response?.data?.detail || "Invalid credentials"
          : "An error occurred",
        variant: "destructive",
      });
    }
  };

  return (
    <AuthCard title="Career Refined" description="Welcome back">
      <p className="mb-4 text-center text-sm text-muted-foreground">
        Sign in to your account to continue
      </p>

      {/* The actual form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Email */}
        <div>
          <Label htmlFor="email" className="text-sm font-medium text-card-foreground">
            Email address
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="name@example.com"
            {...register("email")}
            className="bg-background"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-destructive-foreground">{errors.email.message}</p>
          )}
        </div>

        {/* Password */}
        <div>
          <Label htmlFor="password" className="text-sm font-medium text-card-foreground">
            Password
          </Label>
          <Input
            id="password"
            type="password"
            placeholder="Enter your password"
            {...register("password")}
            className="bg-background"
          />
          {errors.password && (
            <p className="mt-1 text-sm text-destructive-foreground">{errors.password.message}</p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Sign in
        </Button>
      </form>

      {/* Links at the bottom */}
      <div className="mt-4 flex flex-col items-center justify-center gap-2 text-sm text-muted-foreground sm:flex-row sm:justify-between">
        <Link
          href="/auth/forgot-password"
          className="font-medium text-primary hover:underline"
        >
          Forgot your password?
        </Link>
        <p>
          Don&apos;t have an account?{" "}
          <Link
            href="/auth/signup"
            className="font-medium text-primary hover:underline"
          >
            Sign up
          </Link>
        </p>
      </div>
    </AuthCard>
  );
}