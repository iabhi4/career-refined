"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import {
  ProcessedKeyword,
  getProcessedKeywords,
  highlightJobDescription,
} from "@/utils/application";
import { ApplicationService } from "@/services/application";

interface AnalysisResponse {
  extracted_keywords: string[] | { technical_keywords: string[] };
  matched_keywords: string[];
  missing_keywords: string[];
  relevant_experiences: string[];
  relevant_projects: string[];
  suggestions: Record<string, any>;
}

interface DashboardAnalysis extends AnalysisResponse {
  processedKeywords: ProcessedKeyword[];
  highlightedDescription: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { userId } = useAuth();

  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const [analysis, setAnalysis] = useState<DashboardAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [experiences, setExperiences] = useState<{id: number; company: string}[]>([]);
  const [projects, setProjects] = useState<{id: number; project_name: string}[]>([]);
  const [selectedExps, setSelectedExps] = useState<number[]>([]);
  const [selectedProjs, setSelectedProjs] = useState<number[]>([]);

  function handleLogout() {
    router.push("/auth/login");
    toast({
      title: "Logged out successfully",
      variant: "default",
      duration: 3000,
    });
  }

  async function handleAnalyze() {
    setLoading(true);
    try {
      if (!userId) {
        throw new Error("User ID is not available");
      }

      // Call your backend
      const response: AnalysisResponse = await ApplicationService.createAndAnalyzeApplication({
        user_id: userId,
        job_role: jobRole,
        company,
        location,
        job_description: jobDescription,
      });

      // Build array of processed keywords
      const processed = getProcessedKeywords(
        response.extracted_keywords,
        response.matched_keywords,
        jobDescription
      );

      // Create highlighted HTML
      const highlighted = highlightJobDescription(jobDescription, processed);

      // Store everything in state
      setAnalysis({
        ...response,
        processedKeywords: processed,
        highlightedDescription: highlighted,
      });

      // Clear input fields
      setCompany("");
      setLocation("");
      setJobRole("");
      setJobDescription("");
    } catch (error) {
      console.error("Error analyzing job description:", error);
      // handle error (toast, etc.)
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setAnalysis(null);
  }

  async function handleGoToEditor() {
    if (!userId) {
      throw new Error("User ID is not available");
    }
    try {
      // 1. Fetch the user items from backend
      const data = await ApplicationService.getProjectAndExperience(userId);
      
      // 2. Set them in state
      setExperiences(data.experiences);
      setProjects(data.projects);
      
      // 3. Reset any old selections
      setSelectedExps([]);
      setSelectedProjs([]);
      
      // 4. Open the dialog
      setIsDialogOpen(true);
    } catch (error) {
      console.error("Failed to fetch user items:", error);
    }
  }

  function toggleExpSelection(expId: number) {
    setSelectedExps((prev) =>
      prev.includes(expId) ? prev.filter((id) => id !== expId) : [...prev, expId]
    );
  }

  function toggleProjSelection(projId: number) {
    setSelectedProjs((prev) =>
      prev.includes(projId) ? prev.filter((id) => id !== projId) : [...prev, projId]
    );
  }

  function handleConfirmSelection() {
    console.log("Selected experiences:", selectedExps);
    console.log("Selected projects:", selectedProjs);
    const selectedExpsString = JSON.stringify(selectedExps); // Convert to string
    const selectedProjsString = JSON.stringify(selectedProjs);
    const suggestionsString = JSON.stringify(analysis?.suggestions); // New
    const missingKeywordsString = JSON.stringify(analysis?.missing_keywords); // New
    const extractedKeywordsString = JSON.stringify(analysis?.extracted_keywords); // New
    const matchedKeywordsString = JSON.stringify(analysis?.matched_keywords); // New
    // For example, navigate to editor page with the selected IDs
    router.push(`/editor?from=dashboard&exps=${encodeURIComponent(selectedExpsString)}&projs=${encodeURIComponent(selectedProjsString)}&suggestions=${encodeURIComponent(suggestionsString)}&missingKeywords=${encodeURIComponent(missingKeywordsString)}&extractedKeywords=${encodeURIComponent(extractedKeywordsString)}&matchedKeywords=${encodeURIComponent(matchedKeywordsString)}`);
    setIsDialogOpen(false);
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navbar */}
      <Navbar onLogout={handleLogout} />

      <main className="mx-auto max-w-5xl p-6">
        <h1 className="mb-4 text-2xl font-bold">Analyze Job Description</h1>

        {/* ===== Job Details Card ===== */}
        <Card className="mb-4 bg-card text-card-foreground p-8 shadow-lg rounded-lg">
          <CardHeader>
            <CardTitle className="text-xl">Job Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="mb-1 block font-medium">Company Name</label>
                <Input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Enter company name"
                  className="bg-background"
                />
              </div>

              <div>
                <label className="mb-1 block font-medium">Location</label>
                <Input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Enter location"
                  className="bg-background"
                />
              </div>

              <div>
                <label className="mb-1 block font-medium">Job Role</label>
                <Input
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                  placeholder="Enter job role"
                  className="bg-background"
                />
              </div>

              <div className="md:col-span-2">
                <label className="mb-1 block font-medium">Job Description</label>
                <Textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Enter the job description here..."
                  className="h-24 bg-background"
                />
              </div>
            </div>

            {/* ===== Analyze Button at the old position ===== */}
            <div className="mt-4">
              <Button
                onClick={handleAnalyze}
                disabled={loading || !jobDescription}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* ===== Only show these two side-by-side buttons if we have analysis ===== */}
        {analysis && (
          <div className="flex items-center space-x-2 mb-6">
            <Button
              variant="outline"
              onClick={handleClear}
              className="border border-muted text-muted-foreground hover:bg-muted"
            >
              Clear
            </Button>

            <Button
              variant="outline"
              onClick={handleGoToEditor}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Go to Editor
            </Button>
          </div>
        )}

        {/* ===== If we have analysis, show the two-column layout ===== */}
        {analysis && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Left Column: Keyword Frequency & Chart */}
            <Card className="bg-card text-card-foreground p-6 shadow-lg rounded-lg">
              <CardHeader>
                <CardTitle className="text-lg">Keyword Frequency &amp; Chart</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {analysis.processedKeywords.map(({ keyword, frequency, inResume }) => (
                    <div
                      key={keyword}
                      className="flex items-center justify-between p-2 border rounded"
                    >
                      {/* Keyword + highlight if inResume */}
                      <div className="flex items-center space-x-2">
                        <span
                          className={`relative group px-1 rounded font-medium ${
                            inResume ? "bg-green-200" : "bg-transparent"
                          }`}
                        >
                          {keyword}
                          <span className="absolute left-0 bottom-full mb-1 hidden group-hover:block whitespace-nowrap bg-muted text-muted-foreground text-xs px-1 py-0.5 rounded shadow">
                            {inResume ? "Already in Resume" : "Can add in resume"}
                          </span>
                        </span>

                        {/* Frequency bar */}
                        <div className="w-32 bg-muted h-2 relative">
                          <div
                            className="bg-primary h-2"
                            style={{ width: `${frequency * 10}px` }}
                          />
                        </div>
                      </div>

                      <span className="text-sm font-semibold">{frequency}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Right Column: Highlighted Job Description */}
            {analysis.highlightedDescription && (
              <Card className="bg-card text-card-foreground p-6 shadow-lg rounded-lg">
                <CardHeader>
                  <CardTitle className="text-lg">Highlighted Job Description</CardTitle>
                </CardHeader>
                <CardContent>
                  <div
                    className="text-sm leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: analysis.highlightedDescription }}
                  />
                </CardContent>
              </Card>
            )}
          </div>
        )}
        {/* ====== DIALOG ====== */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Select Work Experiences & Projects</DialogTitle>
            </DialogHeader>
            
            <div className="mt-4 space-y-4">
              {/* Experiences Section */}
              <div>
                <p className="font-medium mb-2">Work Experiences</p>
                <div className="space-y-2">
                  {experiences.map((exp) => (
                    <div key={exp.id} className="flex items-center space-x-2">
                      <Checkbox
                        checked={selectedExps.includes(exp.id)}
                        onCheckedChange={() => toggleExpSelection(exp.id)}
                      />
                      <span>{exp.company}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Projects Section */}
              <div>
                <p className="font-medium mb-2">Projects</p>
                <div className="space-y-2">
                  {projects.map((proj) => (
                    <div key={proj.id} className="flex items-center space-x-2">
                      <Checkbox
                        checked={selectedProjs.includes(proj.id)}
                        onCheckedChange={() => toggleProjSelection(proj.id)}
                      />
                      <span>{proj.project_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <DialogFooter className="mt-6">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={handleConfirmSelection}>
                Confirm
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}