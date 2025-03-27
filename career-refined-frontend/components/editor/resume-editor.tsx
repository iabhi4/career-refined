"use client";

import React, {
  useMemo,
  useCallback,
  useRef,
  useImperativeHandle,
  forwardRef,
} from "react";
import {
  createEditor,
  Descendant,
  BaseEditor,
  Element as SlateElement,
} from "slate";
import {
  Slate,
  Editable,
  withReact,
  ReactEditor,
  useSlate,
} from "slate-react";
import { withHistory } from "slate-history";
import { Button } from "@/components/ui/button";

// ------------------ Slate Custom Types ------------------
export type CustomText = {
  text: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
};

export type CustomElement =
  | {
      type: "section";
      sectionType: "personalDetails" | "experience" | "projects" | "skills" | "education";
      children: Descendant[];
    }
  | {
      type: "heading";
      children: Descendant[];
    }
  | {
      type: "experience" | "project" | "education";
      children: Descendant[];
    }
  | {
      type: "label-value";
      label: string;
      children: Descendant[];
    }
  | {
      type: "paragraph";
      children: Descendant[];
    };

declare module "slate" {
  interface CustomTypes {
    Editor: BaseEditor & ReactEditor;
    Element: CustomElement;
    Text: CustomText;
  }
}

// ------------------ Default Slate Value ------------------
const DEFAULT_VALUE: Descendant[] = [
  {
    type: "paragraph",
    children: [{ text: "No resume data available." }],
  },
];

// ------------------ Utility Functions ------------------

/** Safely return a string (fallback to empty string) */
function safeStr(value: any): string {
  return value ?? "";
}

/** Deserialize JSON resume data into Slate nodes */
function deserializeResumeData(data: any): Descendant[] {
  const nodes: Descendant[] = [];

  // Personal Details Section
  if (data?.personalDetails) {
    const personalNodes: Descendant[] = [
      { type: "heading", children: [{ text: "Personal Details" }] },
      {
        type: "label-value",
        label: "Name",
        children: [{ text: safeStr(data.personalDetails.name) }],
      },
      {
        type: "label-value",
        label: "Phone",
        children: [{ text: safeStr(data.personalDetails.phone) }],
      },
      {
        type: "label-value",
        label: "Email",
        children: [{ text: safeStr(data.personalDetails.email) }],
      },
      {
        type: "label-value",
        label: "LinkedIn",
        children: [{ text: safeStr(data.personalDetails.linkedin) }],
      },
      {
        type: "label-value",
        label: "GitHub",
        children: [{ text: safeStr(data.personalDetails.github) }],
      },
    ];
    nodes.push({
      type: "section",
      sectionType: "personalDetails",
      children: personalNodes,
    });
  }

  // Experience Section
  if (Array.isArray(data?.experience) && data.experience.length > 0) {
    const expChildren: Descendant[] = [
      { type: "heading", children: [{ text: "Experience" }] },
    ];
    data.experience.forEach((exp: any) => {
      const expNode: Descendant = {
        type: "experience",
        children: [
          {
            type: "label-value",
            label: "Company",
            children: [{ text: safeStr(exp.company) }],
          },
          {
            type: "label-value",
            label: "Role",
            children: [{ text: safeStr(exp.role) }],
          },
          {
            type: "label-value",
            label: "Duration",
            children: [{ text: `${safeStr(exp.startDate)} - ${safeStr(exp.endDate)}` }],
          },
          {
            type: "label-value",
            label: "Location",
            children: [{ text: safeStr(exp.location) }],
          },
        ],
      };
      if (exp.responsibilities) {
        // Allow responsibilities to be either a string (split by newline) or an array
        const responsibilities = Array.isArray(exp.responsibilities)
          ? exp.responsibilities
          : String(exp.responsibilities).split("\n");
        expNode.children.push({
          type: "label-value",
          label: "Responsibilities",
          children: responsibilities.map((line: string) => ({
            type: "paragraph",
            children: [{ text: line }],
          })),
        });
      }
      expChildren.push(expNode);
    });
    nodes.push({
      type: "section",
      sectionType: "experience",
      children: expChildren,
    });
  }

  // Projects Section
  if (Array.isArray(data?.projects) && data.projects.length > 0) {
    const projChildren: Descendant[] = [
      { type: "heading", children: [{ text: "Projects" }] },
    ];
    data.projects.forEach((proj: any) => {
      const projNode: Descendant = {
        type: "project",
        children: [
          {
            type: "label-value",
            label: "Project",
            children: [{ text: safeStr(proj.name) }],
          },
          {
            type: "label-value",
            label: "Technologies",
            children: [{ text: safeStr(proj.technologies) }],
          },
          {
            type: "label-value",
            label: "Duration",
            children: [
              { text: `${safeStr(proj.startDate)} - ${safeStr(proj.endDate)}` },
            ],
          },
          {
            type: "label-value",
            label: "Description",
            children: Array.isArray(proj.description)
              ? proj.description.map((line: string) => ({
                  type: "paragraph",
                  children: [{ text: line }],
                }))
              : [{ text: safeStr(proj.description) }],
          },
        ],
      };
      projChildren.push(projNode);
    });
    nodes.push({
      type: "section",
      sectionType: "projects",
      children: projChildren,
    });
  }

  // Skills Section
  if (data?.skills) {
    const skillsChildren: Descendant[] = [
      { type: "heading", children: [{ text: "Skills" }] },
    ];

    // Define the categories and labels you want to show
    const skillCategories = [
      { label: "Languages", key: "languages" },
      { label: "Frameworks", key: "frameworks" },
      { label: "Developer Tools", key: "developerTools" },
      { label: "Cloud Technologies", key: "cloudTechnologies" },
      { label: "DBS Applications", key: "dbsApplications" },
      { label: "Other Skills & Tools", key: "otherSkillsAndTools" },
    ];

    // For each category, if there are any skills, add a label-value element.
    skillCategories.forEach((cat) => {
      const arr = data.skills[cat.key];
      if (arr && Array.isArray(arr) && arr.length > 0) {
        skillsChildren.push({
          type: "label-value",
          label: cat.label,
          children: [{ text: arr.join(", ") }],
        });
      }
    });

    nodes.push({
      type: "section",
      sectionType: "skills",
      children: skillsChildren,
    });
  }

  // Education Section
  if (Array.isArray(data?.education) && data.education.length > 0) {
    const eduChildren: Descendant[] = [
      { type: "heading", children: [{ text: "Education" }] },
    ];
    data.education.forEach((edu: any) => {
      const eduNode: Descendant = {
        type: "education",
        children: [
          {
            type: "label-value",
            label: "Institution",
            children: [{ text: safeStr(edu.institution) }],
          },
          {
            type: "label-value",
            label: "Degree",
            children: [{ text: safeStr(edu.degree) }],
          },
          {
            type: "label-value",
            label: "Duration",
            children: [{ text: `${safeStr(edu.startYear)} - ${safeStr(edu.endYear)}` }],
          },
          {
            type: "label-value",
            label: "Major",
            children: [{ text: safeStr(edu.major) }],
          },
        ],
      };
      eduChildren.push(eduNode);
    });
    nodes.push({
      type: "section",
      sectionType: "education",
      children: eduChildren,
    });
  }

  if (nodes.length === 0) {
    return [{ type: "paragraph", children: [{ text: "No resume data available." }] }];
  }
  return nodes;
}

/** Serialize Slate nodes back into JSON resume data */
function serializeSlateNodes(nodes: Descendant[]): any {
  const result: any = {};

  // Personal Details
  const pdSection = nodes.find(
    (n: any) => n.type === "section" && n.sectionType === "personalDetails"
  ) as any;
  if (pdSection && Array.isArray(pdSection.children)) {
    result.personalDetails = {};
    pdSection.children.forEach((child: any) => {
      if (child.type === "label-value") {
        const textContent = child.children.map((c: any) => c.text || "").join("").trim();
        switch (child.label) {
          case "Name":
            result.personalDetails.name = textContent;
            break;
          case "Phone":
            result.personalDetails.phone = textContent;
            break;
          case "Email":
            result.personalDetails.email = textContent;
            break;
          case "LinkedIn":
            result.personalDetails.linkedin = textContent;
            break;
          case "GitHub":
            result.personalDetails.github = textContent;
            break;
        }
      }
    });
  } else {
    result.personalDetails = undefined;
  }

  // Experience
  const expSection = nodes.find(
    (n: any) => n.type === "section" && n.sectionType === "experience"
  ) as any;
  if (expSection && Array.isArray(expSection.children)) {
    const expNodes = expSection.children.filter((child: any) => child.type === "experience");
    result.experience = expNodes.map((expNode: any) => {
      const expObj: any = {};
      expNode.children.forEach((child: any) => {
        if (child.type === "label-value") {
          const textContent = child.children
            .map((c: any) =>
              c.type === "paragraph" && Array.isArray(c.children)
                ? c.children.map((x: any) => x.text).join("")
                : c.text || ""
            )
            .join("\n")
            .trim();
          switch (child.label) {
            case "Company":
              expObj.company = textContent;
              break;
            case "Role":
              expObj.role = textContent;
              break;
            case "Duration":
              {
                const parts = textContent.split("-");
                expObj.startDate = parts[0]?.trim() || "";
                expObj.endDate = parts[1]?.trim() || "";
              }
              break;
            case "Location":
              expObj.location = textContent;
              break;
            case "Responsibilities":
              expObj.responsibilities = textContent ? textContent.split("\n").filter(Boolean) : [];
              break;
          }
        }
      });
      return expObj;
    });
  } else {
    result.experience = undefined;
  }

  // Projects
  const projSection = nodes.find(
    (n: any) => n.type === "section" && n.sectionType === "projects"
  ) as any;
  if (projSection && Array.isArray(projSection.children)) {
    const projNodes = projSection.children.filter((child: any) => child.type === "project");
    result.projects = projNodes.map((projNode: any) => {
      const projObj: any = {};
      projNode.children.forEach((child: any) => {
        if (child.type === "label-value") {
          const textContent = child.children
            .map((c: any) =>
              c.type === "paragraph" && Array.isArray(c.children)
                ? c.children.map((x: any) => x.text).join("")
                : c.text || ""
            )
            .join("\n")
            .trim();
          switch (child.label) {
            case "Project":
              projObj.name = textContent;
              break;
            case "Technologies":
              projObj.technologies = textContent;
              break;
            case "Duration":
              {
                const parts = textContent.split("-");
                projObj.startDate = parts[0]?.trim() || "";
                projObj.endDate = parts[1]?.trim() || "";
              }
              break;
            case "Description":
              projObj.description = textContent ? textContent.split("\n").filter(Boolean) : [];
              break;
          }
        }
      });
      return projObj;
    });
  } else {
    result.projects = undefined;
  }

  // Skills
  const skillsSection = nodes.find(
    (n: any) => n.type === "section" && n.sectionType === "skills"
  ) as any;
  if (skillsSection && Array.isArray(skillsSection.children)) {
    result.skills = {};
    skillsSection.children.forEach((child: any) => {
      if (child.type === "label-value") {
        const textContent = child.children
          .map((c: any) => c.text || "")
          .join("")
          .trim();
        switch (child.label) {
          case "Languages":
            result.skills.languages = textContent;
            break;
          case "Frameworks":
            result.skills.frameworks = textContent;
            break;
          case "Developer Tools":
            result.skills.developerTools = textContent;
            break;
          case "Cloud Technologies":
            result.skills.cloudTechnologies = textContent;
            break;
          case "DBS Applications":
            result.skills.dbsApplications = textContent;
            break;
          case "Other Skills & Tools":
            result.skills.otherSkillsAndTools = textContent;
            break;
          default:
            break;
        }
      }
    });
  } else {
    result.skills = undefined;
  }

  // Education
  const eduSection = nodes.find(
    (n: any) => n.type === "section" && n.sectionType === "education"
  ) as any;
  if (eduSection && Array.isArray(eduSection.children)) {
    const eduNodes = eduSection.children.filter((child: any) => child.type === "education");
    result.education = eduNodes.map((eduNode: any) => {
      const eduObj: any = {};
      eduNode.children.forEach((child: any) => {
        if (child.type === "label-value") {
          const textContent = child.children.map((c: any) => c.text || "").join("").trim();
          switch (child.label) {
            case "Institution":
              eduObj.institution = textContent;
              break;
            case "Degree":
              eduObj.degree = textContent;
              break;
            case "Duration":
              {
                const parts = textContent.split("-");
                eduObj.startYear = parts[0]?.trim() || "";
                eduObj.endYear = parts[1]?.trim() || "";
              }
              break;
            case "Location":
              eduObj.location = textContent;
              break;
          }
        }
      });
      return eduObj;
    });
  } else {
    result.education = undefined;
  }

  return result;
}

// ------------------ Resume Editor Component ------------------
interface ResumeEditorProps {
  /** Stringified JSON resume data for initialization */
  initialValue: string;
}

/**
 * ResumeEditor – Exposes getSerializedContent() via forwardRef so that the parent
 * can retrieve the latest editor data on demand.
 */
const ResumeEditor = forwardRef(({ initialValue }: ResumeEditorProps, ref) => {
  // Convert initial JSON to Slate nodes
  const initialNodes = useMemo(() => {
    if (initialValue) {
      let parsed: any;
      try {
        parsed = JSON.parse(initialValue);
      } catch (err) {
        console.error("Failed to parse JSON in ResumeEditor:", err);
        return DEFAULT_VALUE;
      }
      return deserializeResumeData(parsed);
    }
    return DEFAULT_VALUE;
  }, [initialValue]);

  const editor = useMemo(() => withHistory(withReact(createEditor())), []);
  const editorValueRef = useRef<Descendant[]>(initialNodes);

  useImperativeHandle(ref, () => ({
    getSerializedContent: () => serializeSlateNodes(editorValueRef.current),
  }));

  const renderElement = useCallback((props: any) => <Element {...props} />, []);
  const renderLeaf = useCallback((props: any) => <Leaf {...props} />, []);

  return (
    <Slate
      editor={editor}
      initialValue={initialNodes}
      onChange={(newValue) => {
        editorValueRef.current = newValue;
      }}
    >
      <div className="w-full h-full">
        {/* Toolbar */}
        <div className="mb-4 flex space-x-2">
          <FormatButton format="bold" icon="B" />
          <FormatButton format="italic" icon="I" />
          <FormatButton format="underline" icon="U" />
        </div>
        {/* Editable Area */}
        <Editable
          renderElement={renderElement}
          renderLeaf={renderLeaf}
          placeholder="Edit your resume content..."
          className="p-3 border border-gray-300 rounded w-full h-full overflow-auto"
        />
      </div>
    </Slate>
  );
});
ResumeEditor.displayName = "ResumeEditor";

// ------------------ Custom Element Renderer ------------------
const Element = ({ attributes, children, element }: any) => {
  switch (element.type) {
    case "heading":
      return (
        <h2
          {...attributes}
          contentEditable={false} // Prevent editing the heading
          className="text-xl font-bold mb-2 mt-4"
        >
          {children}
        </h2>
      );
    case "section":
      return (
        <div {...attributes} className="my-4 space-y-4">
          {children}
        </div>
      );
    case "experience":
    case "project":
    case "education":
      return (
        <div
          {...attributes}
          className="border border-gray-300 rounded p-4 bg-white shadow-sm mb-4"
        >
          {children}
        </div>
      );
    case "label-value":
      return (
        <div {...attributes} className="grid grid-cols-[120px_1fr] gap-2 mb-3">
          <div contentEditable={false} className="font-bold text-sm text-gray-700">
            {element.label}
          </div>
          <div className="text-sm text-gray-900">{children}</div>
        </div>
      );
    case "paragraph":
      return (
        <p {...attributes} className="leading-relaxed mb-1">
          {children}
        </p>
      );
    default:
      return (
        <p {...attributes} className="leading-relaxed mb-2">
          {children}
        </p>
      );
  }
};

// ------------------ Leaf Renderer ------------------
const Leaf = ({ attributes, children, leaf }: any) => {
  if (leaf.bold) children = <strong>{children}</strong>;
  if (leaf.italic) children = <em>{children}</em>;
  if (leaf.underline) children = <u>{children}</u>;
  return <span {...attributes}>{children}</span>;
};

// ------------------ Toolbar Button & Helpers ------------------
const FormatButton = ({ format, icon }: { format: string; icon: string }) => {
  const editor = useSlate();
  return (
    <Button
      variant="outline"
      onMouseDown={(event) => {
        event.preventDefault();
        toggleMark(editor, format);
      }}
    >
      {icon}
    </Button>
  );
};

const toggleMark = (editor: BaseEditor, format: string) => {
  const isActive = isMarkActive(editor, format);
  if (isActive) editor.removeMark(format);
  else editor.addMark(format, true);
};

const isMarkActive = (editor: BaseEditor, format: string) => {
  const marks = (editor as any).marks?.() || {};
  return marks[format] === true;
};

export default ResumeEditor;