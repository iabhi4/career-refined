# CareerRefined

CareerRefined is a **holistic platform** designed to streamline your job search journey by providing:
- **AI-powered resume tailoring** optimized for ATS systems.
- **Job application tracking** with smart organization.
- **Interactive editor** to enhance your AI-tailored resume.
- **Resume PDF generation** via LaTeX and secure storage in AWS S3.

Built for job seekers who want to **stand out** while keeping everything organized in one place.

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework**: [Next.js 13+](https://nextjs.org/) (App Router)
- **Styling**: [TailwindCSS](https://tailwindcss.com/)
- **Type Safety**: TypeScript + Zod Validation
- **State Management**: React Context API + Hooks

### **Backend**
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL
- **Task Queue**: Celery + RabbitMQ
- **PDF Generation**: LaTeX via Dockerized `pdflatex`
- **Storage**: AWS S3 for secure file storage
- **Authentication**: JWT/Cookie-based

### **AI Layer**
- Integrated **GPT** APIs for dynamic resume tailoring.
- A Retrieval-Augmented Generation (RAG) pipeline is used for GPT's responses by retrieving relevant data from user profile and combining it with the model’s reasoning to generate accurate & context-aware outputs
