import Link from "next/link";

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <aside className="fixed left-0 top-0 h-screen w-60 bg-gray-900 border-r border-green-700 p-6 flex flex-col">
        <h1 className="text-2xl font-bold text-green-500 mb-8">Ingredion Portal</h1>

        <nav className="flex flex-col gap-3 text-gray-300">
          <Link href="/" className="hover:text-green-400">Home</Link>
          <Link href="/dashboard" className="hover:text-green-400">Dashboard</Link>
          <Link href="/upload" className="hover:text-green-400">Upload</Link>
        </nav>
      </aside>

      <main className="ml-60 flex-1 overflow-y-auto p-10">
        {children}
      </main>
    </div>
  );
}