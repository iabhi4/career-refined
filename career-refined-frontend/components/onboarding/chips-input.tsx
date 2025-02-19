"use client";

import * as React from "react";
import { useController, Control } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { X } from "lucide-react"; // or any icon from react-icons

interface ChipsInputProps {
  control: Control<any>; // the form's control
  name: string;          // the field name, e.g. "skills"
  placeholder?: string;
}

export function ChipsInput({ control, name, placeholder }: ChipsInputProps) {
  const {
    field,
    fieldState: { error },
  } = useController({ name, control });

  const [inputValue, setInputValue] = React.useState("");

  // When user presses Enter or comma, add the skill
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addChip(inputValue.trim());
    }
  };

  // Add skill if it's not empty
  const addChip = (chip: string) => {
    if (!chip) return;
    field.onChange([...(field.value || []), chip]);
    setInputValue("");
  };

  // Remove a skill by index
  const removeChip = (index: number) => {
    const updated = [...(field.value || [])];
    updated.splice(index, 1);
    field.onChange(updated);
  };

  return (
    <div>
      <div className="mb-2 flex flex-wrap gap-2">
        {(field.value || []).map((chip: string, idx: number) => (
          <div
            key={idx}
            className="flex items-center space-x-2 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700"
          >
            <span>{chip}</span>
            <button
              type="button"
              onClick={() => removeChip(idx)}
              className="focus:outline-none"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>

      <Input
        type="text"
        placeholder={placeholder || "Type and press Enter"}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
      />

      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error.message}
        </p>
      )}
    </div>
  );
}