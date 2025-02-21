"use client";

import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { userOnboardingSchema } from "@/schemas/onboarding";
import { ChipsInput } from "@/components/onboarding/chips-input";
import { useRouter } from "next/navigation";

// shadcn/ui components
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// icons
import { AiOutlinePlus, AiOutlineDelete } from "react-icons/ai";
import { OnboardingService } from "@/services/onboarding";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/auth";
import { useEffect } from "react";

type OnboardingFormValues = z.infer<typeof userOnboardingSchema>;

export default function OnboardingPage() {
  const { userId, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const {
    register,
    control,  
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<OnboardingFormValues>({
    resolver: zodResolver(userOnboardingSchema),
    defaultValues: {
      work_experiences: [],
      education: [],
      projects: [],
      skills: [],
    },
  });

  // Work Experience field array
  const {
    fields: workFields,
    append: workAppend,
    remove: workRemove,
  } = useFieldArray({
    control,
    name: "work_experiences",
  });

  // Education field array
  const {
    fields: eduFields,
    append: eduAppend,
    remove: eduRemove,
  } = useFieldArray({
    control,
    name: "education",
  });

  // Projects field array
  const {
    fields: projectFields,
    append: projectAppend,
    remove: projectRemove,
  } = useFieldArray({
    control,
    name: "projects",
  });

  useEffect(() => {
    if (!isAuthenticated || !userId) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, userId, router]);

  // Submit handler
  const onSubmit = handleSubmit(async (formData: OnboardingFormValues) => {
    console.log("Entered onSubmit");
    if (!userId) {
      toast({
        title: "Error",
        description: "User ID not found. Please login again.",
        variant: "destructive",
      });
      router.push('/auth/login');
      return;
    }
    console.log("User ID found");
    try {
      console.log("Submitting onboarding data");
      await OnboardingService.submitOnboardingData(formData, userId);

      toast({
        title: "Success!",
        description: "Your profile has been updated successfully.",
      });
      console.log("Successfully submitted onboarding data");

      router.push('/dashboard');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save your profile. Please try again.",
        variant: "destructive",
      });
    }
  });

  return (
    <div className="min-h-screen bg-[#F9FAFB] p-4">
      <div className="mx-auto max-w-screen-lg">
      <div className="flex justify-end mb-4">
        <Button
          variant="outline"
          onClick={() => {
            // Call your logout function from the auth context
            // and then redirect to login
            logout(); // assuming you destructure logout from useAuth()
            router.push("/auth/login");
          }}
        >
          Logout
        </Button>
      </div>
        <h1 className="mb-6 text-2xl font-bold">Onboarding</h1>

        <form onSubmit={onSubmit} className="space-y-8">
          {/* ========== Basic User Info ========== */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="text-xl">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Name */}
              <div>
                <Label htmlFor="name">Name</Label>
                <Input id="name" {...register("name")} placeholder="John Doe" />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.name.message}
                  </p>
                )}
              </div>

              {/* Email */}
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" {...register("email")} placeholder="you@example.com" />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Phone */}
              <div>
                <Label htmlFor="phone_number">Phone Number</Label>
                <Input id="phone_number" {...register("phone_number")} placeholder="+1 234 567 890" />
                {errors.phone_number && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.phone_number.message}
                  </p>
                )}
              </div>

              {/* Location */}
              <div>
                <Label htmlFor="location">Location</Label>
                <Input id="location" {...register("location")} placeholder="City, Country" />
                {errors.location && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.location.message}
                  </p>
                )}
              </div>

              {/* Portfolio, LinkedIn, GitHub */}
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div>
                  <Label htmlFor="portfolio_link">Portfolio Link</Label>
                  <Input
                    id="portfolio_link"
                    {...register("portfolio_link")}
                    placeholder="https://your-portfolio.com"
                  />
                  {errors.portfolio_link && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.portfolio_link.message}
                    </p>
                  )}
                </div>
                <div>
                  <Label htmlFor="linkedin_link">LinkedIn Link</Label>
                  <Input
                    id="linkedin_link"
                    {...register("linkedin_link")}
                    placeholder="https://linkedin.com/in/username"
                  />
                  {errors.linkedin_link && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.linkedin_link.message}
                    </p>
                  )}
                </div>
                <div>
                  <Label htmlFor="github_link">GitHub Link</Label>
                  <Input
                    id="github_link"
                    {...register("github_link")}
                    placeholder="https://github.com/username"
                  />
                  {errors.github_link && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.github_link.message}
                    </p>
                  )}
                </div>
              </div>
              {/* Certifications */}
              <div>
                <Label>Certifications</Label>
                <ChipsInput
                    control={control}
                    name="certifications"
                    placeholder="Type a certification and press Enter"
                />
                {errors.certifications && (
                    <p className="mt-1 text-sm text-red-600">
                    {errors.certifications.message as string}
                    </p>
                )}
              </div>

                {/* Languages */}
              <div>
                <Label>Languages Known</Label>
                <ChipsInput
                    control={control}
                    name="languages"
                    placeholder="Type a language and press Enter"
                />
                {errors.languages && (
                    <p className="mt-1 text-sm text-red-600">
                    {errors.languages.message as string}
                    </p>
                )}
              </div>
            </CardContent>
          </Card>
          

          {/* ========== Work Experience ========== */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-xl">
                <span>Work Experience</span>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() =>
                    workAppend({
                      company: "",
                      position: "",
                      experience_type: "Full-time",
                      start_month: "January",
                      start_year: 2023,
                      currently_work_here: false,
                      description: "",
                      location: "",
                    })
                  }
                >
                  <AiOutlinePlus className="mr-1" />
                  Add
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {workFields.map((field, index) => {
                const currentlyWorkHere = watch(`work_experiences.${index}.currently_work_here`);
                return (
                  <div
                    key={field.id}
                    className="rounded-md border border-gray-200 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">
                        Work Experience {index + 1}
                      </h3>
                      <button
                        type="button"
                        className="text-red-600 hover:text-red-800"
                        onClick={() => workRemove(index)}
                      >
                        <AiOutlineDelete size={20} />
                      </button>
                    </div>

                    <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                      {/* Company */}
                      <div>
                        <Label>Company</Label>
                        <Input
                          {...register(`work_experiences.${index}.company`)}
                          placeholder="Company Name"
                        />
                        {errors.work_experiences?.[index]?.company && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.work_experiences[index]?.company?.message}
                          </p>
                        )}
                      </div>

                      {/* Position */}
                      <div>
                        <Label>Position</Label>
                        <Input
                          {...register(`work_experiences.${index}.position`)}
                          placeholder="Software Engineer"
                        />
                        {errors.work_experiences?.[index]?.position && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.work_experiences[index]?.position?.message}
                          </p>
                        )}
                      </div>

                      {/* Experience Type */}
                      <div>
                        <Label>Experience Type</Label>
                        <select
                          className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                          {...register(`work_experiences.${index}.experience_type`)}
                        >
                          <option value="Full-time">Full-time</option>
                          <option value="Part-time">Part-time</option>
                          <option value="Internship">Internship</option>
                        </select>
                        {errors.work_experiences?.[index]?.experience_type && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.work_experiences[index]?.experience_type?.message}
                          </p>
                        )}
                      </div>

                      {/* Location */}
                      <div>
                        <Label>Location</Label>
                        <Input
                          {...register(`work_experiences.${index}.location`)}
                          placeholder="City, Country"
                        />
                        {errors.work_experiences?.[index]?.location && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.work_experiences[index]?.location?.message}
                          </p>
                        )}
                      </div>

                      {/* Start Month/Year */}
                      <div>
                        <Label>Start Month</Label>
                        <select
                          className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                          {...register(`work_experiences.${index}.start_month`)}
                        >
                          {validMonths.map((m) => (
                            <option key={m} value={m}>{m}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <Label>Start Year</Label>
                        <Input
                          type="number"
                          {...register(`work_experiences.${index}.start_year`)}
                          placeholder="2020"
                        />
                      </div>

                      {/* Currently Work Here */}
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          className="h-4 w-4"
                          {...register(`work_experiences.${index}.currently_work_here`)}
                        />
                        <Label>Currently Work Here</Label>
                      </div>

                      {/* End Month/Year (hide if currently_work_here is true) */}
                      {!currentlyWorkHere && (
                        <>
                          <div>
                            <Label>End Month</Label>
                            <select
                              className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                              {...register(`work_experiences.${index}.end_month`)}
                            >
                              <option value="">Select month</option>
                              {validMonths.map((m) => (
                                <option key={m} value={m}>{m}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <Label>End Year</Label>
                            <Input
                              type="number"
                              {...register(`work_experiences.${index}.end_year`)}
                              placeholder="2021"
                            />
                          </div>
                        </>
                      )}

                      {/* Description */}
                      <div className="col-span-2">
                        <Label>Description</Label>
                        <textarea
                          className="mt-1 block w-full rounded-md border border-gray-300 p-2"
                          {...register(`work_experiences.${index}.description`)}
                          placeholder="Describe your responsibilities"
                        />
                      </div>

                      {/* Technologies Used */}
                      <div className="col-span-2">
                        <Label>Technologies Used</Label>
                        <Input
                          {...register(`work_experiences.${index}.technologies_used`)}
                          placeholder="e.g. React, Node.js, AWS"
                        />
                      </div>
                    </div>

                    {/* Field-level errors from Zod refinements */}
                    {errors.work_experiences?.[index]?.end_year && (
                      <p className="mt-1 text-sm text-red-600">
                        {errors.work_experiences[index]?.end_year?.message}
                      </p>
                    )}
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* ========== Education ========== */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-xl">
                <span>Education</span>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() =>
                    eduAppend({
                      school_name: "",
                      start_month: "January",
                      start_year: 2023,
                      end_month: "January",
                      end_year: 2023,
                      major: "",
                      degree_type: "Bachelor's",
                      gpa: "",
                    })
                  }
                >
                  <AiOutlinePlus className="mr-1" />
                  Add
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {eduFields.map((field, index) => (
                <div
                  key={field.id}
                  className="rounded-md border border-gray-200 p-4"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">
                      Education {index + 1}
                    </h3>
                    <button
                      type="button"
                      className="text-red-600 hover:text-red-800"
                      onClick={() => eduRemove(index)}
                    >
                      <AiOutlineDelete size={20} />
                    </button>
                  </div>

                  <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {/* School Name */}
                    <div>
                      <Label>School Name</Label>
                      <Input
                        {...register(`education.${index}.school_name`)}
                        placeholder="University of X"
                      />
                      {errors.education?.[index]?.school_name && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.education[index]?.school_name?.message}
                        </p>
                      )}
                    </div>

                    {/* Major */}
                    <div>
                      <Label>Major</Label>
                      <Input
                        {...register(`education.${index}.major`)}
                        placeholder="Computer Science"
                      />
                    </div>

                    {/* Degree Type */}
                    <div>
                      <Label>Degree Type</Label>
                      <select
                        className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                        {...register(`education.${index}.degree_type`)}
                      >
                        <option value="">Select degree</option>
                        <option value="Bachelor's">Bachelor's</option>
                        <option value="Master's">Master's</option>
                        <option value="PhD">PhD</option>
                        <option value="Associate's">Associate's</option>
                        <option value="High School">High School</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>

                    {/* GPA */}
                    <div>
                      <Label>GPA</Label>
                      <Input {...register(`education.${index}.gpa`)} placeholder="3.8" />
                    </div>

                    {/* Start Month/Year */}
                    <div>
                      <Label>Start Month</Label>
                      <select
                        className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                        {...register(`education.${index}.start_month`)}
                      >
                        {validMonths.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label>Start Year</Label>
                      <Input
                        type="number"
                        {...register(`education.${index}.start_year`)}
                        placeholder="2020"
                      />
                    </div>

                    {/* End Month/Year */}
                    <div>
                      <Label>End Month</Label>
                      <select
                        className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                        {...register(`education.${index}.end_month`)}
                      >
                        <option value="">Select month</option>
                        {validMonths.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label>End Year</Label>
                      <Input
                        type="number"
                        {...register(`education.${index}.end_year`)}
                        placeholder="2024"
                      />
                    </div>
                  </div>

                  {/* Field-level errors from Zod refinements */}
                  {errors.education?.[index]?.end_year && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.education[index]?.end_year?.message}
                    </p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* ========== Projects ========== */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-xl">
                <span>Projects</span>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() =>
                    projectAppend({
                      project_name: "",
                      description: "",
                      start_month: "January",
                      start_year: 2023,
                    })
                  }
                >
                  <AiOutlinePlus className="mr-1" />
                  Add
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {projectFields.map((field, index) => (
                <div
                  key={field.id}
                  className="rounded-md border border-gray-200 p-4"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">
                      Project {index + 1}
                    </h3>
                    <button
                      type="button"
                      className="text-red-600 hover:text-red-800"
                      onClick={() => projectRemove(index)}
                    >
                      <AiOutlineDelete size={20} />
                    </button>
                  </div>

                  <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {/* Project Name */}
                    <div>
                      <Label>Project Name</Label>
                      <Input
                        {...register(`projects.${index}.project_name`)}
                        placeholder="My Awesome Project"
                      />
                      {errors.projects?.[index]?.project_name && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.projects[index]?.project_name?.message}
                        </p>
                      )}
                    </div>

                    {/* Experience Type */}
                    <div>
                      <Label>Experience Type</Label>
                      <select
                        className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                        {...register(`projects.${index}.experience_type`)}
                      >
                        <option value="">Select type</option>
                        <option value="Personal">Personal</option>
                        <option value="Academic">Academic</option>
                        <option value="Work-related">Work-related</option>
                      </select>
                    </div>

                    {/* Company (optional) */}
                    <div>
                      <Label>Company</Label>
                      <Input
                        {...register(`projects.${index}.company`)}
                        placeholder="If applicable"
                      />
                    </div>

                    {/* Position (optional) */}
                    <div>
                      <Label>Position</Label>
                      <Input
                        {...register(`projects.${index}.position`)}
                        placeholder="Developer, etc."
                      />
                    </div>

                    {/* Start Month/Year */}
                    <div>
                      <Label>Start Month</Label>
                      <select
                        className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                        {...register(`projects.${index}.start_month`)}
                      >
                        {validMonths.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label>Start Year</Label>
                      <Input
                        type="number"
                        {...register(`projects.${index}.start_year`)}
                        placeholder="2021"
                      />
                    </div>

                    {/* End Month/Year */}
                    <div>
                      <Label>End Month</Label>
                      <select
                        className="mt-1 block w-full rounded-md border border-gray-300 bg-white p-2"
                        {...register(`projects.${index}.end_month`)}
                      >
                        <option value="">Select month</option>
                        {validMonths.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label>End Year</Label>
                      <Input
                        type="number"
                        {...register(`projects.${index}.end_year`)}
                        placeholder="2022"
                      />
                    </div>

                    {/* Description */}
                    <div className="col-span-2">
                      <Label>Description</Label>
                      <textarea
                        className="mt-1 block w-full rounded-md border border-gray-300 p-2"
                        {...register(`projects.${index}.description`)}
                        placeholder="Describe the project"
                      />
                    </div>

                    {/* Project Link */}
                    <div>
                      <Label>Project Link</Label>
                      <Input
                        {...register(`projects.${index}.project_link`)}
                        placeholder="https://github.com/..."
                      />
                    </div>

                    {/* Technologies Used */}
                    <div>
                      <Label>Technologies Used</Label>
                      <Input
                        {...register(`projects.${index}.technologies_used`)}
                        placeholder="e.g. React, Node.js"
                      />
                    </div>
                  </div>

                  {/* Field-level errors from Zod refinements */}
                  {errors.projects?.[index]?.end_year && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.projects[index]?.end_year?.message}
                    </p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* ========== Skills ========== */}
          <Card className="p-4">
            <CardHeader>
            <CardTitle className="text-xl">Skills</CardTitle>
            </CardHeader>
            <CardContent>
            <ChipsInput
                control={control}
                name="skills"
                placeholder="Type a skill and press Enter"
            />
            </CardContent>
          </Card>


          {/* ========== Submit Button ========== */}
          <div className="flex justify-end">
            <Button type="submit" className="bg-indigo-600 text-white hover:bg-indigo-700">
              Submit
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// We can define validMonths in this file or import from your schema file
const validMonths = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];