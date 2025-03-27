// components/dialogs/NewOrLastDialog.tsx
"use client";

import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface NewOrLastDialogProps {
  open: boolean;
  onClose: () => void;
  onNew: () => void;
  onLast: () => void;
}

const NewOrLastDialog: React.FC<NewOrLastDialogProps> = ({ open, onClose, onNew, onLast }) => {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Start a Resume</DialogTitle>
        </DialogHeader>
        <p className="text-sm mb-4">
          Do you want to work on a <strong>new resume</strong> or load your <strong>last resume</strong>?
        </p>
        <DialogFooter className="mt-6 flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={onNew}>New Resume</Button>
          <Button onClick={onLast}>Last Resume</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default NewOrLastDialog;