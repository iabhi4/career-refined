// types/application.ts

export interface ApplicationModel {
    id?: number;
    user_id: number;
    job_role: string;
    company?: string;
    location?: string;
    job_description: string;
    date_applied?: string;   // or Date, if you parse it as a JS Date
    application_status?: string;
  }
  
  /** If you have a specific shape for the analysis result: */
  export interface AnalysisResult {
    matched_keywords: string[];
    missing_keywords: string[];
    relevant_experiences: string[];
    relevant_projects: string[];
    suggestions: Record<string, any>; // or a more precise type if you know the structure
  }
  