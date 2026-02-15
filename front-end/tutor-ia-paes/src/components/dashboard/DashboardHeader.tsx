import Link from "next/link";

export function DashboardHeader() {
  return (
    <header className="sticky top-0 z-10 border-b border-foreground/10 bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="text-sm font-semibold tracking-tight"
            aria-label="Ir al inicio del dashboard"
          >
            Tutor IA PAES
          </Link>
          <span className="hidden text-sm text-foreground/70 md:inline">
            Dashboard
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-foreground/70">Usuario</span>
        </div>
      </div>
    </header>
  );
}
