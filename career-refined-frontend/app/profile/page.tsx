"use client";

import React, { useState, useEffect } from "react";
import { User, Pencil, Plus } from "lucide-react";
import Image from "next/image";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Navbar } from "@/components/navbar/navbar";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/auth";
import { Toast } from "@/components/ui/toast";
import router from "next/router";
import { ProfileService } from "@/services/profile";

// Create a context to pass formData, setFormData, editIndex, and sectionDialog
const DialogFormContext = React.createContext<any>(null);

/** 
 * RenderField component.
 * It reads formData and setFormData from context and renders an input or textarea.
 */
type RenderFieldProps = {
  label: string;
  field: string;
  type?: "text" | "textarea";
};

const RenderField: React.FC<RenderFieldProps> = ({ label, field, type = "text" }) => {
  const { formData, setFormData } = React.useContext(DialogFormContext) || { formData: {}, setFormData: () => {} };
  return (
    <div key={field}>
      <label className="block text-sm font-medium mb-1">{label}</label>
      {type === "textarea" ? (
        <Textarea
          value={formData[field] || ""}
          onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
        />
      ) : (
        <Input
          value={formData[field] || ""}
          onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
        />
      )}
    </div>
  );
};

/**
 * ConditionalRenderField component.
 * It checks if we're editing and skips rendering identifier fields.
 */
type ConditionalRenderFieldProps = {
  label: string;
  field: string;
  type?: "text" | "textarea";
};

const ConditionalRenderField: React.FC<ConditionalRenderFieldProps> = ({ label, field, type = "text" }) => {
  const { formData, editIndex, sectionDialog } = React.useContext(DialogFormContext) || { formData: {}, editIndex: null, sectionDialog: null };

  // When editing, skip the identifier field.
  if (editIndex !== null) {
    if (sectionDialog === "experience" && field === "company") return null;
    if (sectionDialog === "education" && field === "school_name") return null;
    if (sectionDialog === "projects" && field === "project_name") return null;
  }
  return <RenderField label={label} field={field} type={type} />;
};

export default function ProfilePage() {
  const { toast } = useToast();
  const { userId } = useAuth();

  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<any>(null);

  // On mount, fetch profile data
  useEffect(() => {
    if (!userId) return;
    ProfileService.get_profile_data(userId)
      .then((data) => {
        // Ensure these fields are arrays:
        data.skills = parseToArray(data.skills);
        data.languages = parseToArray(data.languages);
        data.certifications = parseToArray(data.certifications);
        setProfile(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [userId]);

  // ------------- DIALOG STATES -------------
  const [showPersonalDialog, setShowPersonalDialog] = useState(false);
  // "experience" | "projects" | "education"
  const [sectionDialog, setSectionDialog] = useState<null | "experience" | "projects" | "education">(null);
  // For edit mode, you might still keep editIndex if needed (or set it to a non-null value)
  const [editIndex, setEditIndex] = useState<number | null>(null); // null => add
  const [editIdentifier, setEditIdentifier] = useState<string | null>(null);
  const [formData, setFormData] = useState<any>({});

  const [chipsDialogType, setChipsDialogType] = useState<null | "skills" | "languages" | "certifications">(null);
  const [chipsValue, setChipsValue] = useState<string[]>([]);

  if (loading) {
    return <div className="p-4">Loading profile...</div>;
  }
  if (!profile) {
    return <div className="p-4">No profile data found.</div>;
  }

  // ------------- PERSONAL -------------
  function openPersonalDialog() {
    const pd = profile.personalDetails;
    setFormData({ ...pd });
    setShowPersonalDialog(true);
  }
  async function savePersonalDetails() {
    if (!userId) return;
    try {
      await ProfileService.editPersonalInfo(userId, formData);
      setProfile({ ...profile, personalDetails: formData });
      toast({ title: "Personal details updated!", duration: 3000 });
      setShowPersonalDialog(false);
    } catch (err) {
      toast({ title: "Failed to update personal details", variant: "destructive" });
    }
  }

  // ------------- EXPERIENCE / EDUCATION / PROJECTS -------------
  function openAddDialog(section: "experience" | "education" | "projects") {
    setSectionDialog(section);
    setEditIndex(null);
    setEditIdentifier(null);
    setFormData({});
  }
  function openEditDialog(section: "experience" | "education" | "projects", idx: number) {
    setSectionDialog(section);
    setEditIndex(idx);
    const existing = profile[section][idx];
    setFormData({ ...existing });
    let identifier = "";
    if (section === "experience") {
      identifier = existing.company; // Company becomes the identifier.
    } else if (section === "education") {
      identifier = existing.school_name; // School Name is used.
    } else if (section === "projects") {
      identifier = existing.project_name; // Project Name is used.
    }
    setEditIdentifier(identifier);
  }
  async function saveSectionDialog() {
    if (!userId || !sectionDialog) return;
    if (editIdentifier === null) {
      // Add mode
      if (sectionDialog === "experience") {
        const updatedFormData = sanitizeFormData(formData);
        const newExp = await ProfileService.addExperience(userId, updatedFormData);
        setProfile({ ...profile, experience: [...profile.experience, newExp] });
        toast({ title: "New experience added!", duration: 3000 });
      } else if (sectionDialog === "education") {
        const newEdu = await ProfileService.addEducation(userId, formData);
        setProfile({ ...profile, education: [...profile.education, newEdu] });
        toast({ title: "New education added!", duration: 3000 });
      } else if (sectionDialog === "projects") {
        const newProj = await ProfileService.addProject(userId, formData);
        setProfile({ ...profile, projects: [...profile.projects, newProj] });
        toast({ title: "New project added!", duration: 3000 });
      }
    } else {
      // Edit mode: Use the identifier for matching
      const updatedFormData = sanitizeFormData(formData);
      if (sectionDialog === "experience") {
        const updatedExp = await ProfileService.editExperience(userId, editIdentifier, updatedFormData);
        const updated = profile.experience.map((exp: any) =>
          exp.company === editIdentifier ? updatedFormData : exp
        );
        setProfile({ ...profile, experience: updated });
        toast({ title: "Experience updated!", duration: 3000 });
      } else if (sectionDialog === "education") {
        const updatedEdu = await ProfileService.editEducation(userId, editIdentifier, updatedFormData);
        const updated = profile.education.map((edu: any) =>
          edu.school_name === editIdentifier ? updatedFormData : edu
        );
        setProfile({ ...profile, education: updated });
        toast({ title: "Education updated!", duration: 3000 });
      } else if (sectionDialog === "projects") {
        const updatedProj = await ProfileService.editProject(userId, editIdentifier, updatedFormData);
        const updated = profile.projects.map((proj: any) =>
          proj.project_name === editIdentifier ? updatedFormData : proj
        );
        setProfile({ ...profile, projects: updated });
        toast({ title: "Project updated!", duration: 3000 });
      }
    }
    // Clear dialog state
    setSectionDialog(null);
    setFormData({});
    setEditIdentifier(null);
    setEditIndex(null);
  }

  // ------------- SKILLS / LANGUAGES / CERTIFICATIONS -------------
  function openChipsDialog(type: "skills" | "languages" | "certifications") {
    setChipsDialogType(type);
    setChipsValue([...profile[type]]);
  }
  async function saveChipsDialog() {
    if (!userId || !chipsDialogType) return;
    
    const updatedString = arrayToCommaSeparatedString(chipsValue);
    
    if (chipsDialogType === "skills") {
      const skillsData = { "skills": updatedString };
      await ProfileService.updateSkills(userId, skillsData);
      setProfile({ ...profile, skills: parseToArray(updatedString) });
      toast({ title: "Skills updated!", duration: 3000 });
    } else if (chipsDialogType === "languages") {
      const languagesData = { "languages": updatedString };
      await ProfileService.updateLanguages(userId, languagesData);
      setProfile({ ...profile, languages: parseToArray(updatedString) });
      toast({ title: "Languages updated!", duration: 3000 });
    } else if (chipsDialogType === "certifications") {
      const certificationsData = { "certifications": updatedString };
      await ProfileService.updateCertifications(userId, certificationsData);
      setProfile({ ...profile, certifications: parseToArray(updatedString) });
      toast({ title: "Certifications updated!", duration: 3000 });
    }
    setChipsDialogType(null);
  }

  function sanitizeFormData(formData: any) {
    const sanitizedData = { ...formData };
    if (sanitizedData.hasOwnProperty("start_year")) {
      const parsedStart = parseInt(sanitizedData.start_year, 10);
      sanitizedData.start_year = isNaN(parsedStart) ? null : parsedStart;
    }
    if (sanitizedData.hasOwnProperty("end_year")) {
      const parsedEnd = parseInt(sanitizedData.end_year, 10);
      sanitizedData.end_year = isNaN(parsedEnd) ? null : parsedEnd;
    }
    return sanitizedData;
  }

  // For read-only display
  function renderReadOnlyField(label: string, value: any) {
    if (!value) return null;
    return (
      <p>
        <span className="font-medium">{label}:</span> {value}
      </p>
    );
  }

  function renderExperienceItem(exp: any, idx: number) {
    const lines = (exp.description || "").split("\n").filter((line: string) => line.trim() !== "");
    return (
      <div key={idx} className="relative border p-3 rounded mb-4">
        <Pencil
          className="absolute top-2 right-2 w-5 h-5 cursor-pointer hover:text-primary"
          onClick={() => openEditDialog("experience", idx)}
        />
        {exp.position && <p className="font-medium">{exp.position}</p>}
        {exp.company && <p className="text-sm text-muted-foreground">{exp.company}</p>}
        {(exp.start_month || exp.end_month) && (
          <p className="text-sm">
            {exp.start_month} {exp.start_year} - {exp.end_month} {exp.end_year}
          </p>
        )}
        {lines.length > 0 && (
          <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
            {lines.map((line: string, i: number) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  function renderEducationItem(edu: any, idx: number) {
    const hasSchool = edu.school_name && edu.school_name.trim() !== "";
    const hasDegree = edu.degree_type && edu.degree_type.trim() !== "";
    const hasDates = edu.start_month || edu.end_month;
    return (
      <div key={idx} className="border p-3 rounded flex items-center justify-between">
        <div>
          {hasSchool && <p className="font-medium">{edu.school_name}</p>}
          {hasDegree && <p className="text-sm text-muted-foreground">{edu.degree_type}</p>}
          {hasDates && (
            <p className="text-sm">
              {edu.start_month} {edu.start_year} - {edu.end_month} {edu.end_year}
            </p>
          )}
          {edu.major && edu.major.trim() !== "" && <p className="text-sm">Major: {edu.major}</p>}
          {edu.gpa && edu.gpa.trim() !== "" && <p className="text-sm">GPA: {edu.gpa}</p>}
        </div>
        <Pencil
          className="cursor-pointer hover:text-primary"
          onClick={() => openEditDialog("education", idx)}
        />
      </div>
    );
  }

  function renderProjectItem(proj: any, idx: number) {
    const lines = (proj.description || "").split("\n").filter((line: string) => line.trim() !== "");
    return (
      <div key={idx} className="relative border p-3 rounded mb-4">
        <Pencil
          className="absolute top-2 right-2 w-5 h-5 cursor-pointer hover:text-primary"
          onClick={() => openEditDialog("projects", idx)}
        />
        {proj.project_name && <p className="font-medium">{proj.project_name}</p>}
        {lines.length > 0 && (
          <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
            {lines.map((line: string, i: number) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  // Helpers for arrays
  function parseToArray(value: any): string[] {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    if (typeof value === "string") {
      return value.split(",").map((item) => item.trim()).filter((item) => item.length > 0);
    }
    return [];
  }

  function arrayToCommaSeparatedString(arr: string[]): string {
    return arr.join(", ");
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar onLogout={() => { router.push("/auth/login"); Toast({ title: "Logged out successfully", variant: "default" }); }} />
      <main className="max-w-screen-lg mx-auto p-4">
        {/* ===== Personal Details ===== */}
        <Card className="mb-6 bg-card text-card-foreground shadow rounded-lg">
          <CardHeader className="relative px-6 pt-6 pb-2">
            <Pencil
              className="absolute top-6 right-6 cursor-pointer hover:text-primary"
              onClick={openPersonalDialog}
            />
            <div className="flex items-center space-x-4">
              <div className="relative w-20 h-20 bg-muted rounded-full overflow-hidden">
                <div className="relative w-20 h-20 bg-muted rounded-full flex items-center justify-center overflow-hidden">
                  <User className="w-10 h-10 text-muted-foreground" />
                </div>
              </div>
              <div>
                <CardTitle className="text-2xl">{profile.personalDetails.name || "N/A"}</CardTitle>
                {profile.personalDetails.location && (
                  <p className="text-sm text-muted-foreground">{profile.personalDetails.location}</p>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="px-6 pb-6 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            {renderReadOnlyField("Email", profile.personalDetails.email)}
            {renderReadOnlyField("Phone", profile.personalDetails.phone_number)}
            {renderReadOnlyField("Portfolio", profile.personalDetails.portfolio_link)}
            {renderReadOnlyField("LinkedIn", profile.personalDetails.linkedin_link)}
            {renderReadOnlyField("GitHub", profile.personalDetails.github_link)}
          </CardContent>
        </Card>

        {/* ===== Work Experience ===== */}
        <Card className="mb-6 bg-card text-card-foreground p-4 shadow rounded-lg">
          <CardHeader className="relative px-6 pt-6 pb-2">
            <Plus
              className="absolute top-6 right-6 cursor-pointer hover:text-primary"
              onClick={() => openAddDialog("experience")}
            />
            <CardTitle className="text-lg">Work Experience</CardTitle>
          </CardHeader>
          <CardContent className="px-6 pb-6 space-y-4">
            {profile.experience.map((exp: any, idx: number) => renderExperienceItem(exp, idx))}
          </CardContent>
        </Card>

        {/* ===== Education ===== */}
        <Card className="mb-6 bg-card text-card-foreground p-4 shadow rounded-lg">
          <CardHeader className="relative px-6 pt-6 pb-2">
            <Plus
              className="absolute top-6 right-6 cursor-pointer hover:text-primary"
              onClick={() => openAddDialog("education")}
            />
            <CardTitle className="text-lg">Education</CardTitle>
          </CardHeader>
          <CardContent className="px-6 pb-6 space-y-4">
            {profile.education.map((edu: any, idx: number) => renderEducationItem(edu, idx))}
          </CardContent>
        </Card>

        {/* ===== Projects ===== */}
        <Card className="mb-6 bg-card text-card-foreground p-4 shadow rounded-lg">
          <CardHeader className="relative px-6 pt-6 pb-2">
            <Plus
              className="absolute top-6 right-6 cursor-pointer hover:text-primary"
              onClick={() => openAddDialog("projects")}
            />
            <CardTitle className="text-lg">Projects</CardTitle>
          </CardHeader>
          <CardContent className="px-6 pb-6 space-y-4">
            {profile.projects.map((proj: any, idx: number) => renderProjectItem(proj, idx))}
          </CardContent>
        </Card>

        {/* ===== Skills, Languages, Certifications ===== */}
        <Card className="mb-6 bg-card text-card-foreground p-4 shadow rounded-lg">
          <CardHeader className="px-6 pt-6 pb-2">
            <CardTitle className="text-lg">Other Important Details</CardTitle>
          </CardHeader>
          <CardContent className="px-6 pb-6 space-y-4">
            {/* Skills */}
            <div>
              <div className="flex items-center justify-between">
                <p className="font-medium mb-2">Skills:</p>
                <Plus className="cursor-pointer hover:text-primary" onClick={() => openChipsDialog("skills")} />
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill: string, idx: number) => (
                  <span key={idx} className="bg-muted px-2 py-1 rounded text-sm">{skill}</span>
                ))}
              </div>
            </div>
            {/* Languages */}
            <div>
              <div className="flex items-center justify-between">
                <p className="font-medium mb-2">Languages:</p>
                <Plus className="cursor-pointer hover:text-primary" onClick={() => openChipsDialog("languages")} />
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.languages.map((lang: string, idx: number) => (
                  <span key={idx} className="bg-muted px-2 py-1 rounded text-sm">{lang}</span>
                ))}
              </div>
            </div>
            {/* Certifications */}
            <div>
              <div className="flex items-center justify-between">
                <p className="font-medium mb-2">Certifications:</p>
                <Plus className="cursor-pointer hover:text-primary" onClick={() => openChipsDialog("certifications")} />
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.certifications.map((cert: string, idx: number) => (
                  <span key={idx} className="bg-muted px-2 py-1 rounded text-sm">{cert}</span>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* ===== Dialog: Personal Details ===== */}
      <Dialog open={showPersonalDialog} onOpenChange={setShowPersonalDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Personal Details</DialogTitle>
          </DialogHeader>
          <DialogFormContext.Provider value={{ formData, setFormData, editIndex: null, sectionDialog: null }}>
            <div className="space-y-4">
              <RenderField label="Name" field="name" />
              <RenderField label="Location" field="location" />
              <RenderField label="Email" field="email" />
              <RenderField label="Phone" field="phone_number" />
              <RenderField label="Portfolio" field="portfolio_link" />
              <RenderField label="LinkedIn" field="linkedin_link" />
              <RenderField label="GitHub" field="github_link" />
            </div>
          </DialogFormContext.Provider>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowPersonalDialog(false)}>Cancel</Button>
            <Button onClick={savePersonalDetails}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ===== Dialog: Add/Edit Experience/Education/Projects ===== */}
      <Dialog open={!!sectionDialog} onOpenChange={() => setSectionDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editIdentifier === null
                ? `Add ${sectionDialog}`
                : `Edit ${sectionDialog} - ${editIdentifier}`
              }
            </DialogTitle>
          </DialogHeader>
          <DialogFormContext.Provider value={{ formData, setFormData, editIndex, sectionDialog }}>
            <div className="space-y-4">
              {sectionDialog === "experience" && (
                <>
                  <ConditionalRenderField label="Company" field="company" />
                  <ConditionalRenderField label="Location" field="location" />
                  <ConditionalRenderField label="Position" field="position" />
                  <ConditionalRenderField label="Experience Type" field="experience_type" />
                  <ConditionalRenderField label="Start Month" field="start_month" />
                  <ConditionalRenderField label="Start Year" field="start_year" />
                  <ConditionalRenderField label="End Month" field="end_month" />
                  <ConditionalRenderField label="End Year" field="end_year" />
                  <ConditionalRenderField label="Technologies Used" field="technologies_used" />
                  <ConditionalRenderField label="Description" field="description" type="textarea" />
                </>
              )}
              {sectionDialog === "education" && (
                <>
                  <ConditionalRenderField label="School Name" field="school_name" />
                  <ConditionalRenderField label="Major" field="major" />
                  <ConditionalRenderField label="Degree Type" field="degree_type" />
                  <ConditionalRenderField label="GPA" field="gpa" />
                  <ConditionalRenderField label="Start Month" field="start_month" />
                  <ConditionalRenderField label="Start Year" field="start_year" />
                  <ConditionalRenderField label="End Month" field="end_month" />
                  <ConditionalRenderField label="End Year" field="end_year" />
                  <ConditionalRenderField label="Location" field="location" />
                </>
              )}
              {sectionDialog === "projects" && (
                <>
                  <ConditionalRenderField label="Project Name" field="project_name" />
                  <ConditionalRenderField label="Company" field="company" />
                  <ConditionalRenderField label="Location" field="location" />
                  <ConditionalRenderField label="Position" field="position" />
                  <ConditionalRenderField label="Experience Type" field="experience_type" />
                  <ConditionalRenderField label="Technologies Used" field="technologies_used" />
                  <ConditionalRenderField label="Start Month" field="start_month" />
                  <ConditionalRenderField label="Start Year" field="start_year" />
                  <ConditionalRenderField label="End Month" field="end_month" />
                  <ConditionalRenderField label="End Year" field="end_year" />
                  <ConditionalRenderField label="Project Link" field="project_link" />
                  <ConditionalRenderField label="Description" field="description" type="textarea" />
                </>
              )}
            </div>
          </DialogFormContext.Provider>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setSectionDialog(null)}>Cancel</Button>
            <Button onClick={saveSectionDialog}>{editIndex === null ? "Save" : "Update"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ===== Dialog: Chips Editor for Skills/Languages/Certifications ===== */}
      <Dialog open={!!chipsDialogType} onOpenChange={() => setChipsDialogType(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit {chipsDialogType}</DialogTitle>
          </DialogHeader>
          <ChipsEditor initialItems={chipsValue} onChange={(val) => setChipsValue(val)} />
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setChipsDialogType(null)}>Cancel</Button>
            <Button onClick={saveChipsDialog}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/** ChipsEditor for adding/removing string-based items */
function ChipsEditor({ initialItems, onChange }: { initialItems: string[]; onChange: (val: string[]) => void }) {
  const [items, setItems] = useState<string[]>(initialItems);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    onChange(items);
  }, [items]);

  function handleAdd() {
    const val = draft.trim();
    if (val && !items.includes(val)) {
      setItems([...items, val]);
    }
    setDraft("");
  }
  function removeItem(idx: number) {
    const updated = [...items];
    updated.splice(idx, 1);
    setItems(updated);
  }

  return (
    <div className="mt-4">
      <div className="mb-2 flex flex-wrap gap-2">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-center space-x-2 bg-muted px-2 py-1 rounded text-sm">
            <span>{item}</span>
            <button type="button" onClick={() => removeItem(idx)} className="text-xs text-red-600">x</button>
          </div>
        ))}
      </div>
      <Input
        placeholder="Type and press Enter"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleAdd();
          }
        }}
      />
    </div>
  );
}

/**
 * Helper to convert a value to an array.
 */
function parseToArray(value: any): string[] {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === "string") {
    return value.split(",").map((item) => item.trim()).filter((item) => item.length > 0);
  }
  return [];
}

/** Helper to convert an array into a comma-separated string. */
function arrayToCommaSeparatedString(arr: string[]): string {
  return arr.join(", ");
}