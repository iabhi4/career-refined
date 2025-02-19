import { z } from 'zod';
import { userOnboardingSchema } from '@/schemas/onboarding';

interface WorkExperience {
  company: string;
  position: string;
  experience_type: string;
  location?: string;
  start_month: string;
  start_year: number;
  end_month?: string;
  end_year?: number;
  currently_work_here: boolean;
  description?: string;
  technologies_used?: string;
}

interface Education {
  school_name: string;
  major?: string;
  degree_type?: string;
  gpa?: string;
  start_month: string;
  start_year: number;
  end_month?: string;
  end_year?: number;
}

interface Project {
  project_name: string;
  company?: string;
  location?: string;
  position?: string;
  experience_type?: string;
  start_month: string;
  start_year: number;
  end_month?: string;
  end_year?: number;
  description?: string;
  technologies_used?: string;
  project_link?: string;
}

export interface OnboardingFormValues {
  name: string;
  email: string;
  phone_number?: string;
  location?: string;
  portfolio_link?: string;
  linkedin_link?: string;
  github_link?: string;
  skills: string[];
  languages: string[];
  certifications: string[];
  work_experiences: WorkExperience[];
  education: Education[];
  projects: Project[];
}