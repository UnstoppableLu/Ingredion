import Link from "next/link";

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-black text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-green-900 p-6 flex flex-col space-y-6">
        <h2 className="text-2xl font-bold text-white mb-6">Ingredion</h2>
        <nav className="flex flex-col space-y-4">
          <Link href="/dashboard" className="hover:text-green-400">Dashboard</Link>
          <Link href="/upload" className="hover:text-green-400">Upload</Link>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}