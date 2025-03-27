// app/editor/page.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Navbar } from "@/components/navbar/navbar";
import ResumeEditor from "@/components/editor/resume-editor";
import NewOrLastDialog from "@/components/dialogs/new-or-last-dialog";
import SelectionDialog from "@/components/dialogs/selection-dialog";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Share2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { ApplicationService } from "@/services/application";
import { useAuth } from "@/contexts/auth";
import { mergeDeep } from "@/utils/application";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react"


interface UserItems {
  experiences: { id: number; company: string }[];
  projects: { id: number; project_name: string }[];
}

export default function EditorPage() {
  const { userId } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const fromDashboard = searchParams.get("from") === "dashboard";

  // Main editor and preview state
  const [editorContent, setEditorContent] = useState("");
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  // Analyzer bar data (if from dashboard)
  const [keywordMatches, setKeywordMatches] = useState<number[] | null>(null);
  const [missingKeywords, setMissingKeywords] = useState<number[] | null>(null);
  //const [suggestions, setSuggestions] = useState<string[]>([]);

  // Dialog states
  const [showNewOrLastDialog, setShowNewOrLastDialog] = useState(!fromDashboard);
  const [showSelectionDialog, setShowSelectionDialog] = useState(false);
  const [userItems, setUserItems] = useState<UserItems>({ experiences: [], projects: [] });
  const [selectedExps, setSelectedExps] = useState<number[]>([]);
  const [selectedProjs, setSelectedProjs] = useState<number[]>([]);

  const resumeEditorRef = useRef<any>(null);
  type SuggestionEntry = [keyword: string, revision: string];

  const [suggestions, setSuggestions] = useState<SuggestionEntry[]>([]);

  useEffect(() => {
    // Check if coming from the dashboard and userId is available
    if (fromDashboard && userId) {
        // Extract query parameters
        handleRouteFromDashboard(searchParams);
    }
}, [fromDashboard, userId, searchParams]);

  async function handleRouteFromDashboard(searchParams: URLSearchParams) {
    if (!userId) return;
        const expsParam = searchParams.get("exps");
        const projsParam = searchParams.get("projs");
        const keywordMatchesParam = searchParams.get("matchedKeywords");

        // Set selected experiences and projects from query parameters
        const matchedKeywordsParam = searchParams.get("matchedKeywords");
        if (matchedKeywordsParam) {
          try {
            const parsed = JSON.parse(decodeURIComponent(matchedKeywordsParam));
            // Ensure parsed is an array; if it's a single string, split on commas.
            setKeywordMatches(Array.isArray(parsed) ? parsed : parsed.split(","));
          } catch (err) {
            console.error("Error parsing matchedKeywords:", err);
            setKeywordMatches([]);
          }
        }

        // missingKeywords
        const missingKeywordsParam = searchParams.get("missingKeywords");
        if (missingKeywordsParam) {
          try {
            const parsed = JSON.parse(decodeURIComponent(missingKeywordsParam));
            setMissingKeywords(Array.isArray(parsed) ? parsed : parsed.split(","));
          } catch (err) {
            console.error("Error parsing missingKeywords:", err);
            setMissingKeywords([]);
          }
        }

        // suggestions
        const suggestionsParam = searchParams.get("suggestions");
        if (suggestionsParam) {
          try {
            const parsed = JSON.parse(decodeURIComponent(suggestionsParam));
            // parsed is an object like { "RESTful APIs": "Old snippet -> Proposed revision", ... }

            // Convert object to [string, string][]
            setSuggestions(Object.entries(parsed) as [string, string][]);
          } catch (error) {
            console.error("Error parsing suggestions:", error);
            setSuggestions([]);
          }
        }

        if (expsParam) {
            setSelectedExps(JSON.parse(decodeURIComponent(expsParam)));
        }
        if (projsParam) {
            setSelectedProjs(JSON.parse(decodeURIComponent(projsParam)));
        }
    try {
      const data = await ApplicationService.fetchEditorDataForFirstTime(
        userId,
        expsParam ? JSON.parse(decodeURIComponent(expsParam)) : [],
        projsParam ? JSON.parse(decodeURIComponent(projsParam)) : []
      );
      setEditorContent(data.editorContent)
      setPdfUrl(data.pdfUrl)
    } catch (error) {
      console.error("Error fetching editor data:", error);
      toast({ title: "Failed to fetch editor data", variant: "destructive" });
    }
  }

  async function handleNewResume() {
    setShowNewOrLastDialog(false);
    if (!userId) return;
    try {
      const items = await ApplicationService.getProjectAndExperience(userId);
      setUserItems(items);
      setShowSelectionDialog(true);
    } catch (error) {
      console.error("Error fetching user items:", error);
      toast({ title: "Failed to fetch user items", variant: "destructive" });
    }
  }

  async function handleLastResume() {
    setShowNewOrLastDialog(false);
    if (!userId) return;
    try {
      const data = await ApplicationService.fetchEditorData(userId);
      setEditorContent(data.editorContent);
      setPdfUrl(data.pdfUrl);
    } catch (error) {
      console.error("Error fetching cached resume:", error);
      toast({ title: "Failed to fetch cached resume", variant: "destructive" });
    }
  }

  async function handleConfirmSelections(selectedExps: number[], selectedProjs: number[]) {
    setShowSelectionDialog(false);
    if (!userId) return;
    try {
      const data = await ApplicationService.fetchEditorDataForFirstTime(userId, selectedExps, selectedProjs);
      setEditorContent(data.editorContent);
      setPdfUrl(data.pdfUrl);
    } catch (error) {
      console.error("Error fetching resume data with selections:", error);
      toast({ title: "Failed to update resume", variant: "destructive" });
    }
  }

  async function handleUpdatePdf() {
    if (!userId) return;
    if (resumeEditorRef.current) {
      const updatedJson = resumeEditorRef.current.getSerializedContent();
      try {
        const result = await ApplicationService.updateResume(userId, updatedJson);
        const taskId = result.task_id;
        
        // Optionally show a loading state for PDF generation
        toast({ title: "PDF generation in progress...", duration: 3000 });
        
        // const intervalId = setInterval(async () => {
        //   const statusResp = await ApplicationService.getPdfStatus(taskId);
        //   if (statusResp.state === "SUCCESS") {
        //     clearInterval(intervalId);
        //     const pdfUrl = statusResp.pdf_path;
        //     setPdfUrl(pdfUrl);
        //     toast({ title: "PDF updated successfully", duration: 3000 });
        //   } else if (statusResp.state === "FAILURE") {
        //     clearInterval(intervalId);
        //     alert("Failed to generate PDF: " + statusResp.error);
        //   }
        // }, 3000);
        
        // Remove or comment out this line if result.pdfUrl is not reliable:
        // setPdfUrl(result.pdfUrl);
      } catch (error) {
        console.error("Error updating PDF:", error);
        toast({ title: "Failed to update PDF", variant: "destructive" });
      }
    }
  }
  

  function handleDownloadPdf() {
    if (pdfUrl) window.open(pdfUrl, "_blank");
  }

  const handleEditorChange = (newData: any) => {
    try {
      // Parse the old data from state (which is a stringified JSON)
      const oldData = JSON.parse(editorContent);
      // Merge newData with oldData; missing keys in newData will remain from oldData.
      const merged = mergeDeep(oldData, newData);
      setEditorContent(JSON.stringify(merged));
    } catch (err) {
      console.error("Error merging updated JSON:", err);
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar onLogout={() => router.push("/auth/login")} />
      <main className="mx-auto max-w-screen-xl p-4">
        <h1 className="mb-4 text-2xl font-bold">Resume Editor</h1>
        {fromDashboard && (
          <Collapsible className="mb-6">
            {/* Collapsible Trigger with icon */}
            <CollapsibleTrigger 
              className="
                flex items-center justify-between 
                w-full 
                px-4 py-2 
                bg-secondary text-secondary-foreground 
                rounded-md shadow
              "
            >
              <span>Keywords &amp; Suggestions</span>
              {/* The icon rotates 180° when state=open */}
              <ChevronDown className="h-5 w-5 transition-transform data-[state=open]:rotate-180" />
            </CollapsibleTrigger>

            {/* Collapsible Content with a max height and scroll */}
            <CollapsibleContent 
              className="
                mt-4 
                max-h-[400px]  /* Adjust as needed */
                overflow-auto
              "
            >
              <div className="grid grid-cols-1 md:grid-cols-2 md:grid-rows-2 gap-4">
                {/* Matched Keywords (top-left) */}
                <Card className="bg-card text-card-foreground p-4 shadow rounded-lg">
                  <CardHeader>
                    <CardTitle className="text-sm text-muted-foreground">Matched Keywords</CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-48 overflow-auto">
                    <ul className="list-disc list-inside text-sm grid grid-cols-2 gap-x-4">
                      {keywordMatches?.map((keyword, idx) => (
                        <li key={idx}>{keyword}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Suggestions (right side, spans 2 rows) */}
                <Card className="bg-card text-card-foreground p-4 shadow rounded-lg md:row-span-2">
                  <CardHeader>
                    <CardTitle className="text-sm font-medium">Suggestions</CardTitle>
                  </CardHeader>
                  <CardContent className="h-full max-h-96 overflow-auto">
                  <ul>
                    {suggestions.map(([keyword, revision]) => (
                      <li key={keyword}>
                        <strong>{keyword}:</strong> {revision}
                      </li>
                    ))}
                  </ul>
                  </CardContent>
                </Card>

                {/* Missing Keywords (bottom-left) */}
                <Card className="bg-card text-card-foreground p-4 shadow rounded-lg">
                  <CardHeader>
                    <CardTitle className="text-sm text-muted-foreground">Missing Keywords</CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-48 overflow-auto">
                    <ul className="list-disc list-inside text-sm grid grid-cols-2 gap-x-4">
                      {missingKeywords?.map((keyword, idx) => (
                        <li key={idx}>{keyword}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 mb-4">
          {/* Left column remains empty */}
          <div></div>
          {/* Right column: buttons aligned to the right */}
          <div className="flex justify-end items-center space-x-2">
            <Button
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={handleUpdatePdf}
            >
              Update PDF
            </Button>
            <Button
              variant="outline"
              onClick={handleDownloadPdf}
              className="flex items-center space-x-1"
            >
              <Download size={16} />
              <span>Download PDF</span>
            </Button>
          </div>
        </div>

        {/* Then your existing grid with the editor and preview cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 w-full mx-auto">
        {/* Editor Card */}
        <Card className="bg-card text-card-foreground p-4 shadow rounded-lg h-[80vh] w-full flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg">Editor</CardTitle>
          </CardHeader>
          {/* 
            flex-1: Takes remaining vertical space after CardHeader 
            overflow-auto: Scroll inside if content is taller than 80vh 
          */}
          <CardContent className="flex-1 overflow-auto">
          {editorContent ? (
            <ResumeEditor
              ref={resumeEditorRef}
              initialValue={editorContent}
            />
          ) : (
            <p>Loading editor...</p>
          )}
          </CardContent>
        </Card>

        {/* Preview Card */}
        <Card className="bg-card text-card-foreground p-4 shadow rounded-lg h-[80vh] w-full flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg">Preview</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-auto flex justify-center items-center">
            {pdfUrl ? (
              <div className="w-full h-full overflow-hidden flex justify-center items-center">
                <iframe
                  src={`${pdfUrl}#toolbar=0&view=fitH`}
                  className="w-full h-full max-w-full"
                  style={{
                    border: "none",
                    objectFit: "cover",
                    height: "100%",
                    minHeight: "100%",
                  }}
                />
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No PDF preview available</p>
            )}
          </CardContent>
        </Card>
      </div>



      
      </main>

      {/* Dialog 1: New Resume or Last Resume */}
      <NewOrLastDialog
        open={showNewOrLastDialog}
        onClose={() => setShowNewOrLastDialog(false)}
        onNew={handleNewResume}
        onLast={handleLastResume}
      />

      {/* Dialog 2: Selection Dialog for new resume */}
      <SelectionDialog
        open={showSelectionDialog}
        onClose={() => setShowSelectionDialog(false)}
        onConfirm={handleConfirmSelections}
        userItems={userItems}
      />
    </div>
  );
}