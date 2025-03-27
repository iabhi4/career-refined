import axios from "axios";
import { API_ENDPOINTS, API_URL, axiosConfig } from "@/config/api";

export class ProfileService {
    static async addExperience(user_id: number, formState: any) {
        const response = await axios.post(API_URL +  API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.WORK_EXPERIENCE, formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }

    static async editExperience(user_id: number, company: string, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.WORK_EXPERIENCE, { ...formState}, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }

    static async addEducation(user_id: number, formState: any) {
        const response = await axios.post(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.EDUCATION, formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }

    static async editEducation(user_id: number, school_name: string, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.EDUCATION, { ...formState }, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }

    static async addProject(user_id: number, formState: any) {
        const response = await axios.post(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.PROJECTS, formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }       

    static async editProject(user_id: number, project_name: string, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.PROJECTS, { ...formState }, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }

    static async updateSkills(user_id: number, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.SKILLS, formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;   
    }

    static async updateLanguages(user_id: number, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.LANGUAGES, formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }       
     

    static async updateCertifications(user_id: number, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.CERTIFICATIONS, formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }     

    static async editPersonalInfo(user_id: number, formState: any) {
        const response = await axios.put(API_URL + API_ENDPOINTS.USERS + "/" + user_id + "/", formState, {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }

    static async get_profile_data(user_id: number) {
        const response = await axios.get(API_URL + API_ENDPOINTS.USERS + "/" + user_id + API_ENDPOINTS.PROFILE + "/", {
            ...axiosConfig,
            withCredentials: true,
        });
        return response.data;
    }
  }
    
    
    
    
