export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <h1 className="text-xl font-semibold tracking-tight">Inicio</h1>
        <p className="text-sm text-foreground/70">
          Base para construir el panel: catálogo (exámenes/materias/temas), banco
          de preguntas, intentos, sesiones y progreso.
        </p>
      </section>

      <section className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="rounded-lg border border-foreground/10 p-4">
          <h2 className="text-sm font-semibold">Catálogo</h2>
          <p className="mt-1 text-sm text-foreground/70">
            Exámenes → Materias → Temas.
          </p>
        </div>

        <div className="rounded-lg border border-foreground/10 p-4">
          <h2 className="text-sm font-semibold">Preguntas</h2>
          <p className="mt-1 text-sm text-foreground/70">
            Banco de preguntas, alternativas y explicación.
          </p>
        </div>

        <div className="rounded-lg border border-foreground/10 p-4">
          <h2 className="text-sm font-semibold">Intentos</h2>
          <p className="mt-1 text-sm text-foreground/70">
            Seguimiento de intentos, estado y resultados.
          </p>
        </div>

        <div className="rounded-lg border border-foreground/10 p-4">
          <h2 className="text-sm font-semibold">Sesiones y progreso</h2>
          <p className="mt-1 text-sm text-foreground/70">
            Sesiones de estudio y métricas por tema.
          </p>
        </div>
      </section>
    </div>
  );
}
