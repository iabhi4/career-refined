import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

interface AuthCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AuthCard({ title, description, children, footer }: AuthCardProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#F9FAFB] px-4">
      <Card className="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-8 shadow-lg">
        <CardHeader className="mb-4 text-center">
          <CardTitle className="text-2xl font-bold">{title}</CardTitle>
          {description ? (
            <CardDescription className="mt-1 text-base text-gray-600">
              {description}
            </CardDescription>
          ) : null}
        </CardHeader>

        {/* Card Content (the form or any other children) */}
        <CardContent>
          {children}
        </CardContent>

        {/* Optional footer (buttons or links) */}
        {footer && <CardFooter>{footer}</CardFooter>}
      </Card>
    </div>
  );
}