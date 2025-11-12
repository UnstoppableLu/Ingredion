import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold text-green-500 mb-4">
        Ingredion Sustainability Portal
      </h1>
      <p className="text-gray-300 mb-10">
        Upload, explore, and visualize sustainability data.
      </p>

      <Link
        href="/dashboard"
        className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg text-lg transition duration-200"
      >
        Start →
      </Link>
    </main>
  );
}
