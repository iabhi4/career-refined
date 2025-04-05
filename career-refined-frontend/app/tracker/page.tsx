"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/navbar/navbar";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { ApplicationService } from "@/services/application";
import { useAuth } from "@/contexts/auth";

export default function JobTrackerPage() {
  const { toast } = useToast();
  const { userId } = useAuth(); 
  // We assume you have user ID from your auth context or something else
  // We'll skip that part for brevity

  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Search & Filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  // Dialog for adding an application
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [addFormData, setAddFormData] = useState<any>({
    job_role: "",
    company: "",
    location: "",
    date_applied: "",
    application_status: "Pending",
    job_description: "",
  });

  // Dialog for showing more details of a clicked application
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [selectedApp, setSelectedApp] = useState<any>(null);
  const todayString = new Date().toISOString().split("T")[0];

  // On mount, fetch data
  useEffect(() => {
    if (!userId) return;
    ApplicationService.getTrackerData(userId).then((data) => {
      setApplications(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <p className="p-4">Loading Applications...</p>;
  }

  // Filtering logic
  const filteredApplications = applications.filter((app) => {
    const role = app.job_role || "";
    const comp = app.company || "";

    const matchesSearch =
    role.toLowerCase().includes(searchQuery.toLowerCase()) ||
    comp.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter
      ? app.application_status.toLowerCase() === statusFilter.toLowerCase()
      : true;

    const matchesDate = dateFilter ? app.date_applied === dateFilter : true;

    return matchesSearch && matchesStatus && matchesDate;
  });

  // Pagination
  const totalPages = Math.ceil(filteredApplications.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentItems = filteredApplications.slice(startIndex, startIndex + itemsPerPage);

  function handlePageChange(newPage: number) {
    if (newPage < 1 || newPage > totalPages) return;
    setCurrentPage(newPage);
  }

  // When user clicks on a row, open details dialog
  function handleRowClick(app: any) {
    setSelectedApp(app);
    setShowDetailsDialog(true);
  }

  // Add Application
  async function handleAddApplication() {
    if (!userId) return;
    try {
      const saved = await ApplicationService.saveManualApplication(userId, addFormData);
      // => 1) Sends data to the backend
      // => 2) 'saved' should be the created application object
  
      setApplications([...applications, saved]);
      // => 3) Append to local state
  
      toast({ title: "Application added successfully!", duration: 3000 });
      setShowAddDialog(false);
      // => Reset form
      setAddFormData({
        job_role: "",
        company: "",
        location: "",
        date_applied: "",
        application_status: "Pending",
        job_description: "",
      });
    } catch (err) {
      toast({ title: "Failed to add application", variant: "destructive" });
    }
  }

  // UI for status label with color-coded styles
  function renderStatusBadge(status: string) {
    if (!status) {
      return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">Unknown</span>;
    }
    let badgeClass = "bg-muted text-muted-foreground";
    switch (status.toLowerCase()) {
      case "applied":
        badgeClass = "bg-blue-100 text-blue-800";
        break;
      case "interview":
        badgeClass = "bg-purple-100 text-purple-800";
        break;
      case "rejected":
        badgeClass = "bg-red-100 text-red-800";
        break;
      case "saved":
        badgeClass = "bg-gray-100 text-gray-800";
        break;
      case "offer":
        badgeClass = "bg-green-100 text-green-800";
        break;
      case "pending":
        badgeClass = "bg-yellow-100 text-yellow-800";
        break;
    }
    return (
      <span className={`px-2 py-1 rounded text-sm font-medium ${badgeClass}`}>
        {status}
      </span>
    );
  }

  function handleLogout() {
    // ...
  }

  async function handleExportCSV() {
    if (!userId) return;  
    try {
      await ApplicationService.exportCSV(userId);
      toast({ title: "CSV exported successfully!", duration: 3000 });
    } catch (err) {
      toast({ title: "Failed to export CSV", variant: "destructive" });
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar onLogout={handleLogout} />

      <main className="max-w-screen-xl mx-auto p-4">
        {/* Header: Title, Export CSV, Add Application */}
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold">Your Job Tracker</h1>
          <div className="space-x-2">
            <Button variant="outline" onClick={() => handleExportCSV()}>
              Export CSV
            </Button>
            <Button
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={() => setShowAddDialog(true)}
            >
              + Add Application
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-4">
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          {/* 
            We use a grid with 3 columns on md+ screens.
            On smaller screens, it becomes 1 column (stacked).
          */}
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search input */}
            <div className="flex flex-col">
              <Label htmlFor="search" className="text-sm font-medium">
                Search jobs or companies
              </Label>
              <Input
                id="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search..."
              />
            </div>

            {/* Status select */}
            <div className="flex flex-col">
              <Label className="text-sm font-medium">Status</Label>
              <select
                className="border border-muted rounded px-2 py-1"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">All</option>
                <option value="Applied">Applied</option>
                <option value="Interview">Interview</option>
                <option value="Rejected">Rejected</option>
                <option value="Saved">Saved</option>
                <option value="Offer">Offer</option>
                <option value="Pending">Pending</option>
              </select>
            </div>

            {/* Date input */}
            <div className="flex flex-col">
              <Label className="text-sm font-medium">Date Applied</Label>
              <Input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Table of Applications */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm border border-muted-foreground rounded">
            <thead className="bg-muted text-muted-foreground">
              <tr>
                <th className="py-2 px-3 text-left">Job Role</th>
                <th className="py-2 px-3 text-left">Company</th>
                <th className="py-2 px-3 text-left">Location</th>
                <th className="py-2 px-3 text-left">Date Applied</th>
                <th className="py-2 px-3 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {currentItems.map((app) => (
                <tr
                  key={app.id}
                  className="border-b last:border-none hover:bg-muted/50 cursor-pointer"
                  onClick={() => handleRowClick(app)}
                >
                  <td className="py-2 px-3">{app.job_role}</td>
                  <td className="py-2 px-3">{app.company}</td>
                  <td className="py-2 px-3">{app.location}</td>
                  <td className="py-2 px-3">
                    {new Date(app.date_applied).toLocaleDateString("en-US", { 
                      year: "numeric", month: "2-digit", day: "2-digit" 
                    })}
                  </td>
                  <td className="py-2 px-3">{renderStatusBadge(app.application_status)}</td>
                </tr>
              ))}
              {currentItems.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-4">
                    No applications found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">
            Showing page {currentPage} of {totalPages}
          </p>
          <div className="space-x-2">
            <Button variant="outline" onClick={() => handlePageChange(currentPage - 1)}>
              Previous
            </Button>
            <Button variant="outline" onClick={() => handlePageChange(currentPage + 1)}>
              Next
            </Button>
          </div>
        </div>
      </main>

      {/* Add Application Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Application</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label className="text-sm font-medium">Company Name</Label>
              <Input
                value={addFormData.company}
                onChange={(e) => setAddFormData({ ...addFormData, company: e.target.value })}
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Location</Label>
              <Input
                value={addFormData.location}
                onChange={(e) => setAddFormData({ ...addFormData, location: e.target.value })}
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Job Role</Label>
              <Input
                value={addFormData.job_role}
                onChange={(e) => setAddFormData({ ...addFormData, job_role: e.target.value })}
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Date Applied</Label>
              <Input
                type="date"
                value={addFormData.date_applied}
                onChange={(e) => setAddFormData({ ...addFormData, date_applied: e.target.value })}
                max={todayString}
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Status</Label>
              <select
                className="border border-muted rounded px-2 py-1 w-full"
                value={addFormData.application_status}
                onChange={(e) => setAddFormData({ ...addFormData, application_status: e.target.value })}
              >
                <option value="Pending">Pending</option>
                <option value="Applied">Applied</option>
                <option value="Interview">Interview</option>
                <option value="Rejected">Rejected</option>
                <option value="Saved">Saved</option>
                <option value="Offer">Offer</option>
              </select>
            </div>
            <div>
              <Label className="text-sm font-medium">Job Description</Label>
              <Textarea
                value={addFormData.job_description}
                onChange={(e) => setAddFormData({ ...addFormData, job_description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowAddDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleAddApplication}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Application Details Dialog (opens when user clicks a row) */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Application Details</DialogTitle>
          </DialogHeader>
          {selectedApp && (
            <div className="space-y-4">
              <p>
                <span className="font-medium">Job Role:</span> {selectedApp.job_role}
              </p>
              <p>
                <span className="font-medium">Company:</span> {selectedApp.company}
              </p>
              <p>
                <span className="font-medium">Location:</span> {selectedApp.location}
              </p>
              <p>
                <span className="font-medium">Date Applied:</span> {selectedApp.date_applied}
              </p>
              <p>
                <span className="font-medium">Status:</span> {selectedApp.application_status}
              </p>
              {selectedApp.job_description && (
                <div>
                  <p className="font-medium">Job Description:</p>
                  <ul className="list-disc list-inside text-sm mt-1 space-y-1">
                    {selectedApp.job_description
                      .split("\n")
                      .filter((line: string) => line.trim() !== "")
                      .map((line: string, idx: number) => (
                        <li key={idx}>{line}</li>
                      ))}
                  </ul>
                </div>
              )}
              {selectedApp.extracted_job_keywords && (
                <p>
                  <span className="font-medium">Extracted Keywords:</span> {selectedApp.extracted_job_keywords}
                </p>
              )}
              {/* {selectedApp.final_resume_used && (
                <p>
                  <span className="font-medium">Resume Used:</span> {selectedApp.final_resume_used}
                </p>
              )} */}
            </div>
          )}
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowDetailsDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}