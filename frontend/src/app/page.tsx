export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between bg-background p-8">
      <section className="space-y-4 text-center">
        <h1 className="text-3xl font-bold text-foreground">
          AI Job Finder
        </h1>
        <p className="text-lg text-muted-foreground">
          Find your dream job with AI-powered matching.
        </p>
      </section>
    </main>
  );
}