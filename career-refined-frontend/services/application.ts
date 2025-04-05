import axios from "axios";
import { API_ENDPOINTS, API_URL, axiosConfig } from "@/config/api";

export class ApplicationService {
    // mockEditorData = {
    //     "personalDetails": {
    //       "name": "John Doe",
    //       "phone": "+1 234 567 890",
    //       "email": "john.doe@example.com",
    //       "linkedin": "https://linkedin.com/in/johndoe",
    //       "github": "https://github.com/johndoe"
    //     },
    //     "experience": [
    //       {
    //         "company": "Acme Corp",
    //         "startDate": "January 2020",
    //         "endDate": "December 2022",
    //         "role": "Senior Software Engineer",
    //         "location": "Remote",
    //         "responsibilities": "Led development of microservices architecture.\nManaged a team of engineers."
    //       }
    //     ],
    //     "projects": [
    //       {
    //         "name": "Realtime Chat App",
    //         "technologies": "WebSockets, Node.js, React",
    //         "startDate": "June 2021",
    //         "endDate": "October 2021",
    //         "description": "Built a real-time chat application.\nImplemented user authentication."
    //       }
    //     ],
    //     "skills": {
    //       "languages": "Python, JavaScript, C++",
    //       "frameworks": "React, Node.js",
    //       "developerTools": "Git, Docker",
    //       "libraries": "Slate, Express"
    //     },
    //     "education": [
    //       {
    //         "institution": "University of Example",
    //         "startYear": "2018",
    //         "endYear": "2020",
    //         "degree": "Master's",
    //         "location": "City, Country"
    //       }
    //     ]
    //   }

    // stringifiedMockEditorData = JSON.stringify(this.mockEditorData);
    // resumePdfUrl = "/Abhinav_Singh.pdf";

    static async createAndAnalyzeApplication(data: {
        user_id: number;
        job_role: string;
        company: string;
        location: string;
        job_description: string;
        add_to_tracker: boolean;
        }) {
        const response = await axios.post(`${API_URL}${API_ENDPOINTS.APPLICATIONS}`, data, {
            withCredentials: true,
        });
        return response.data;
    }

    static async getProjectAndExperience(user_id: number) {
        const response = await axios.get(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.PROJECTS_AND_EXPERIENCES}`, {
            withCredentials: true,
        });
        return response.data;
    }

    static async fetchCachedResumeData(user_id: number) {
        const response = await axios.get(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.EDITOR_DATA}`, {
          withCredentials: true,
        });
        //response.data.editorContent = JSON.stringify(response.data.editorContent);
        return response.data;
    }

    static async fetchEditorDataForFirstTime(user_id: number, selectedExps: number[], selectedProjects: number[]) {
        const response = await axios.get(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.EDITOR_DATA_FOR_FIRST_TIME}`, {
          params: { exps: selectedExps, projects: selectedProjects },
          withCredentials: true,
        });
        response.data.editorContent = JSON.stringify(response.data.editorContent);
        return response.data;
    }

    static async updateResume(user_id: number, editorContent: any) {
      const response = await axios.put(
        `${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.EDITOR_DATA}`, editorContent,
        { ...axiosConfig, withCredentials: true }
      );
      return response.data;
    }


    static async getPdfStatus(task_id: number) {
        const response = await axios.get(`${API_URL}${API_ENDPOINTS.EDITOR_DATA}${API_ENDPOINTS.PDF_STATUS}/${task_id}`, {
            withCredentials: true,
        });
        return response.data;
    }
    

    static async getTrackerData(user_id: number) {
        const response = await axios.get(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.TRACKER_DATA}`, {
            withCredentials: true,
        });
        return response.data;
    }

    static async saveManualApplication(user_id: number, data: any) {
        const response = await axios.post(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.MANUAL_APPLICATION}`, data, {
            withCredentials: true,
        });
        return response.data;
    }

    static async exportCSV(user_id: number) {
        const response = await axios.get(`${API_URL}${API_ENDPOINTS.USERS}/${user_id}${API_ENDPOINTS.CSV}`, {
            withCredentials: true,
            responseType: 'blob',
        });

        // Create a URL for the blob and trigger a download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'applications.csv'); // Specify the file name
        document.body.appendChild(link);
        link.click();
    }
}
