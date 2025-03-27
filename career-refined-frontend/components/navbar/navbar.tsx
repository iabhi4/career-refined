"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

const routes = [
  { label: "Job Tracker", href: "/tracker" },
  { label: "Editor", href: "/editor" },
  { label: "Dashboard", href: "/dashboard" },
];

interface NavbarProps {
  onLogout?: () => void;
}

export function Navbar({ onLogout }: NavbarProps) {
  const pathname = usePathname();

  // Filter out the current route
  const navLinks = routes.filter((route) => route.href !== pathname);

  return (
    <header className="flex items-center justify-between bg-white px-4 py-2 shadow-sm">
      <div className="flex items-center space-x-4">
        <Link href="/">
          <span className="text-xl font-bold">Career Refined</span>
        </Link>
        {/* Render only the routes that are not the current path */}
        {navLinks.map((route) => (
          <Link key={route.href} href={route.href}>
            {route.label}
          </Link>
        ))}
      </div>

      {/* Right side: Profile and Logout */}
      <div className="flex items-center space-x-4">
        <Link href="/profile">Profile</Link>
        <Button variant="outline" onClick={onLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}