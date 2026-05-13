"use client";
import React from 'react';
import Link from 'next/link';

type LayoutProps = {
  children: React.ReactNode;
};

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen bg-slate-900 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-700 p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded bg-sky-500" />
          <h1 className="text-xl font-bold">Aegis</h1>
        </div>

        <nav className="space-y-4">
          <Link
            href="/dashboard"
            className="block px-4 py-2 rounded hover:bg-slate-800 transition"
          >
            Dashboard
          </Link>
          <Link
            href="/import"
            className="block px-4 py-2 rounded hover:bg-slate-800 transition"
          >
            Import Repository
          </Link>
          <Link
            href="/api/auth/logout"
            className="block px-4 py-2 rounded hover:bg-slate-800 transition text-red-400"
          >
            Sign Out
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
