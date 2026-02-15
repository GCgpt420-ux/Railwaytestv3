import Link from "next/link";

const NAV_ITEMS: Array<{ label: string; description?: string }> = [
  { label: "Inicio" },
  { label: "Exámenes", description: "Catálogo de exámenes" },
  { label: "Materias", description: "Subjects por examen" },
  { label: "Temas", description: "Topics por materia" },
  { label: "Preguntas", description: "Banco de preguntas" },
  { label: "Intentos", description: "Attempts y resultados" },
  { label: "Sesiones", description: "Study sessions" },
  { label: "Progreso", description: "User progress" },
  { label: "Usuarios", description: "Gestión de usuarios" },
];

export function DashboardSidebar() {
  return (
    <aside className="border-b border-foreground/10 bg-background md:min-h-dvh md:border-b-0 md:border-r">
      <div className="mx-auto w-full max-w-6xl px-4 py-4 md:px-6 md:py-6">
        <div className="flex items-center justify-between md:block">
          <div className="flex flex-col">
            <span className="text-sm font-semibold tracking-tight">
              Navegación
            </span>
            <span className="text-xs text-foreground/70">
              Secciones principales
            </span>
          </div>
        </div>

        <nav className="mt-4 grid gap-1">
          {NAV_ITEMS.map((item) => {
            const isHome = item.label === "Inicio";
            const content = (
              <div className="flex flex-col">
                <span className="text-sm">{item.label}</span>
                {item.description ? (
                  <span className="text-xs text-foreground/70">
                    {item.description}
                  </span>
                ) : null}
              </div>
            );

            return isHome ? (
              <Link
                key={item.label}
                href="/dashboard"
                className="rounded-md px-3 py-2 transition-colors hover:bg-foreground/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/20"
              >
                {content}
              </Link>
            ) : (
              <div
                key={item.label}
                className="rounded-md px-3 py-2 text-foreground/80"
                aria-disabled="true"
              >
                {content}
              </div>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
