import type { Metadata } from "next";

import { DashboardFooter } from "@/components/dashboard/DashboardFooter";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";

export const metadata: Metadata = {
  title: "Dashboard · Tutor IA PAES",
};

export default function DashboardLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-dvh bg-background text-foreground">
      <div className="grid min-h-dvh grid-cols-1 md:grid-cols-[16rem_1fr]">
        <DashboardSidebar />

        <div className="flex min-h-dvh flex-col">
          <DashboardHeader />
          <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-6">
            {children}
          </main>
          <DashboardFooter />
        </div>
      </div>
    </div>
  );
}
