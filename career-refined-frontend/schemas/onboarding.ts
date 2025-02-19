// schemas/userOnboarding.ts
import * as z from "zod";

const validMonths = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
] as const;

const validWorkExperienceTypes = ["Full-time", "Part-time", "Internship"] as const;
const validDegreeTypes = ["Bachelor's", "Master's", "PhD", "Associate's", "High School", "Other"] as const;
const validProjectTypes = ["Personal", "Academic", "Work-related"] as const;

/** Work Experience */
export const workExperienceSchema = z.object({
  company: z.string().min(1, "Company is required"),
  location: z.string().min(1, "Location is required"),
  position: z.string().min(1, "Position is required"),
  experience_type: z.enum(["Full-time", "Part-time", "Internship"], {
    errorMap: () => ({ message: "Experience type is required" }),
  }),
  start_month: z.enum(validMonths, {
    errorMap: () => ({ message: "Start month is required" }),
  }),
  start_year: z.number().min(1900, "Invalid start year"),
  end_month: z.enum(validMonths).optional(),
  end_year: z.number().min(1900, "Invalid end year").optional(),
  description: z.string().min(1, "Description is required"),
  currently_work_here: z.boolean(),
  technologies_used: z.string().optional(),
})
.refine(
  (data) => {
    if (!data.currently_work_here && data.end_year !== undefined) {
      return data.end_year >= data.start_year;
    }
    return true;
  },
  {
    path: ["end_year"],
    message: "End year cannot be before start year",
  }
);

/** Education */
export const educationSchema = z.object({
  school_name: z.string().min(1, "School name is required"),
  major: z.string().min(1, "Major is required"),
  degree_type: z.enum(validDegreeTypes, {
    errorMap: () => ({ message: "Degree type is required" }),
  }),
  gpa: z.string().optional(),
  start_month: z.enum(validMonths, {
    errorMap: () => ({ message: "Start month is required" }),
  }),
  start_year: z.number().min(1900, "Invalid start year"),
  end_month: z.enum(validMonths, {
    errorMap: () => ({ message: "End month is required" }),
  }),
  end_year: z.number().min(1900, "Invalid end year"),
})
.refine(
  (data) => {
    if (data.end_year !== undefined) {
      return data.end_year >= data.start_year;
    }
    return true;
  },
  {
    path: ["end_year"],
    message: "End year cannot be before start year",
  }
);


/** Project */
export const projectSchema = z.object({
  project_name: z.string().min(1, "Project name is required"),
  company: z.string().optional(),
  location: z.string().optional(),
  position: z.string().optional(),
  experience_type: z.enum(validProjectTypes).optional(),
  start_month: z.enum(validMonths, {
    errorMap: () => ({ message: "Start month is required" }),
  }),
  start_year: z.number().min(1900, "Invalid start year"),
  end_month: z.enum(validMonths).optional(),
  end_year: z.number().min(1900, "Invalid end year").optional(),
  description: z.string().min(1, "Description is required"),
  project_link: z.string().optional(),
  technologies_used: z.string().optional(),
})
.refine(
  (data) => {
    if (data.end_year !== undefined) {
      return data.end_year >= data.start_year;
    }
    return true;
  },
  {
    path: ["end_year"],
    message: "End year cannot be before start year",
  }
);


/** Top-level User schema */
export const userOnboardingSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email address"),
  phone_number: z.string().min(1, "Phone number is required"),
  location: z.string().min(1, "Location is required"),
  resume: z.any().optional(), // File upload remains optional
  portfolio_link: z.string().optional(),
  linkedin_link: z.string().optional(),
  github_link: z.string().optional(),
  work_experiences: z.array(workExperienceSchema).default([]),
  education: z.array(educationSchema).default([]),
  projects: z.array(projectSchema).default([]),
  skills: z.array(z.string()).default([]),
  certifications: z.array(z.string()).default([]),
  languages: z.array(z.string()).default([]),
});
