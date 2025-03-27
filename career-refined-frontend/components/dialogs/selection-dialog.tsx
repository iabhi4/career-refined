// components/dialogs/SelectionDialog.tsx
"use client";

import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

interface UserItem {
  id: number;
  company?: string;
  project_name?: string;
}

export interface UserItems {
  experiences: UserItem[];
  projects: UserItem[];
}

interface SelectionDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (selectedExps: number[], selectedProjs: number[]) => void;
  userItems: UserItems;
}

const SelectionDialog: React.FC<SelectionDialogProps> = ({ open, onClose, onConfirm, userItems }) => {
  const [selectedExps, setSelectedExps] = useState<number[]>([]);
  const [selectedProjs, setSelectedProjs] = useState<number[]>([]);

  const toggleExp = (expId: number) => {
    setSelectedExps((prev) => prev.includes(expId) ? prev.filter(id => id !== expId) : [...prev, expId]);
  };

  const toggleProj = (projId: number) => {
    setSelectedProjs((prev) => prev.includes(projId) ? prev.filter(id => id !== projId) : [...prev, projId]);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Select Work Experiences & Projects</DialogTitle>
        </DialogHeader>
        <div className="mt-4 space-y-4">
          <div>
            <p className="font-medium mb-2">Work Experiences</p>
            <div className="space-y-2">
              {userItems.experiences.map((exp) => (
                <div key={exp.id} className="flex items-center space-x-2">
                  <Checkbox
                    checked={selectedExps.includes(exp.id)}
                    onCheckedChange={() => toggleExp(exp.id)}
                  />
                  <span>{exp.company}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="font-medium mb-2">Projects</p>
            <div className="space-y-2">
              {userItems.projects.map((proj) => (
                <div key={proj.id} className="flex items-center space-x-2">
                  <Checkbox
                    checked={selectedProjs.includes(proj.id)}
                    onCheckedChange={() => toggleProj(proj.id)}
                  />
                  <span>{proj.project_name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <DialogFooter className="mt-6 flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={() => onConfirm(selectedExps, selectedProjs)}>Confirm</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default SelectionDialog;