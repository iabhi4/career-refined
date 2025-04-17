"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth";
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
  suggestions: Record<string, any>;
  task_id: number;
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
  
  const [addToTracker, setAddToTracker] = useState(false);

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

      const response: AnalysisResponse = await ApplicationService.createAndAnalyzeApplicationNew({
        user_id: userId,
        job_role: jobRole,
        company,
        location,
        job_description: jobDescription,
        add_to_tracker: addToTracker,
      });

      const processed = getProcessedKeywords(
        response.extracted_keywords,
        response.matched_keywords,
        jobDescription
      );

      const highlighted = highlightJobDescription(jobDescription, processed);

      setAnalysis({
        ...response,
        processedKeywords: processed,
        highlightedDescription: highlighted,
      });

      setCompany("");
      setLocation("");
      setJobRole("");
      setJobDescription("");
      setAddToTracker(false);
    } catch (error) {
      console.error("Error analyzing job description:", error);
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setAnalysis(null);
  }

  function navigateToEditor() {
    const suggestionsString = JSON.stringify(analysis?.suggestions);
    const missingKeywordsString = JSON.stringify(analysis?.missing_keywords);
    const extractedKeywordsString = JSON.stringify(analysis?.extracted_keywords);
    const matchedKeywordsString = JSON.stringify(analysis?.matched_keywords);
    router.push(`/editor?from=dashboard&suggestions=${encodeURIComponent(suggestionsString)}&missingKeywords=${encodeURIComponent(missingKeywordsString)}&extractedKeywords=${encodeURIComponent(extractedKeywordsString)}&matchedKeywords=${encodeURIComponent(matchedKeywordsString)}`);
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
            <div className="mt-4 flex items-center">
              {/* Analyze button on the left */}
              <Button
                onClick={handleAnalyze}
                disabled={loading || !jobDescription}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </Button>

              {/* Checkbox on the right (margin-left: auto pushes it to far right) */}
              <div className="ml-auto flex items-center space-x-2">
                <Checkbox
                  checked={addToTracker}
                  onCheckedChange={(checked) => setAddToTracker(Boolean(checked))}
                  id="addToTracker"
                />
                <label htmlFor="addToTracker" className="text-sm">
                  Add to tracker
                </label>
              </div>
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
              onClick={navigateToEditor}
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
      </main>
    </div>
  );
}