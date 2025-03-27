// schemas/applicationSchema.ts

import { z } from "zod";

// Example Zod schema matching your ApplicationModel
export const applicationSchema = z.object({
  id: z.number().optional(),
  user_id: z.number(),
  job_role: z.string().min(1, "Job role is required"),
  company: z.string().optional(),
  location: z.string().optional(),
  job_description: z.string().min(1, "Job description is required"),
  date_applied: z.string().optional(),
  application_status: z.string().optional().default("Draft"),
});

// The TypeScript type derived from this Zod schema:
export type ApplicationSchemaType = z.infer<typeof applicationSchema>;
