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
import { AuthService } from "@/services/auth";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth";
import { useToast } from "@/hooks/use-toast";
import { signupSchema } from "@/schemas/auth";
import { SignupFormValues } from "@/types/auth";
import { SignupRequest } from "@/types/auth";


export default function SignupPage() {
  const router = useRouter();
  const { login } = useAuth();
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: SignupRequest) => {
    try {
      const response = await AuthService.signup({
        name: data.name,
        email: data.email,
        password: data.password,
      });

      // Update auth context
      login(response.user_id, false); // New users are not onboarded

      toast({
        title: "Registration successful!",
        description: "Please complete your profile.",
      });
      console.log("Navigating to onboarding");
      router.push('/onboarding');
    } catch (error) {
      // ... error handling ...
    }
  };

  return (
    <AuthCard title="Create an account" description="Welcome to Career Refined">
      <p className="mb-4 text-center text-sm text-gray-500">
        Sign up with your details
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Name */}
        <div>
          <Label htmlFor="name" className="text-sm font-medium text-gray-700">
            Full Name
          </Label>
          <Input
            id="name"
            type="text"
            placeholder="John Doe"
            {...register("name")}
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        {/* Email */}
        <div>
          <Label htmlFor="email" className="text-sm font-medium text-gray-700">
            Email address
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="name@example.com"
            {...register("email")}
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
          )}
        </div>

        {/* Password */}
        <div>
          <Label htmlFor="password" className="text-sm font-medium text-gray-700">
            Password
          </Label>
          <Input
            id="password"
            type="password"
            placeholder="Enter your password"
            {...register("password")}
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
            Confirm Password
          </Label>
          <Input
            id="confirmPassword"
            type="password"
            placeholder="Re-enter your password"
            {...register("confirmPassword")}
          />
          {errors.confirmPassword && (
            <p className="mt-1 text-sm text-red-600">
              {errors.confirmPassword.message}
            </p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
        >
          Sign up
        </Button>
      </form>

      <div className="mt-4 text-center text-sm text-gray-600">
        Already have an account?{" "}
        <Link href="/auth/login" className="font-medium text-indigo-600 hover:underline">
          Login
        </Link>
      </div>
    </AuthCard>
  );
}