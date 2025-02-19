import axios from 'axios';
import { API_URL, API_ENDPOINTS } from '@/config/api';
import { OnboardingFormValues } from '@/types/onboarding';

export class OnboardingService {
  static async submitOnboardingData(formData: OnboardingFormValues, user_id: number) {
    try {
      // 1. Update basic user information

      const userResponse = await axios.post(
        `${API_URL}${API_ENDPOINTS.USERS}/${user_id}`,
        {
          name: formData.name,
          email: formData.email,
          phone_number: formData.phone_number,
          location: formData.location,
          portfolio_link: formData.portfolio_link,
          linkedin_link: formData.linkedin_link,
          github_link: formData.github_link,
          skills: formData.skills,
          languages: formData.languages,
          certifications: formData.certifications,
        }
      );

      const workExperiencePromises = formData.work_experiences.map((exp) =>
        axios.post(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}/work_experience`, {
          company: exp.company,
          location: exp.location,
          position: exp.position,
          experience_type: exp.experience_type,
          start_month: exp.start_month,
          start_year: exp.start_year,
          end_month: exp.end_month,
          end_year: exp.end_year,
          description: exp.description,
          technologies_used: exp.technologies_used,
          currently_work_here: exp.currently_work_here,
        })
      );

      // 3. Add education
      const educationPromises = formData.education.map((edu) =>
        axios.post(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}/education`, {
          school_name: edu.school_name,
          major: edu.major,
          degree_type: edu.degree_type,
          gpa: edu.gpa,
          start_month: edu.start_month,
          start_year: edu.start_year,
          end_month: edu.end_month,
          end_year: edu.end_year,
        })
      );

      // 4. Add projects
      const projectPromises = formData.projects.map((proj) =>
        axios.post(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}/projects`, {
          project_name: proj.project_name,
          company: proj.company,
          location: proj.location,
          position: proj.position,
          experience_type: proj.experience_type,
          start_month: proj.start_month,
          start_year: proj.start_year,
          end_month: proj.end_month,
          end_year: proj.end_year,
          description: proj.description,
          technologies_used: proj.technologies_used,
          project_link: proj.project_link,
        })
      );

      // Execute all promises concurrently
      const [workExperiences, education, projects] = await Promise.all([
        Promise.all(workExperiencePromises),
        Promise.all(educationPromises),
        Promise.all(projectPromises),
      ]);

      return {
        user: userResponse.data,
        workExperiences,
        education,
        projects,
      };
    } catch (error) {
      console.error('Error in onboarding submission:', error);
      throw error;
    }
  }
}