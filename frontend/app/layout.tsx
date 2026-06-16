import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 직원 관리 콘솔",
  description: "PGX AI Staff Management Console",
};

const navItems = [
  { label: "대시보드", path: "/" },
  { label: "AI 직원 목록", path: "/agents" },
  { label: "RAG 컬렉션", path: "/rag" },
  { label: "작업 지시", path: "/tasks" },
  { label: "작업 로그", path: "/logs" },
  { label: "⚙️ 설정", path: "/settings" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <nav className="sidebar">
          <h1>🤖 AI Staff Console</h1>
          {navItems.map((item) => (
            <a key={item.path} href={item.path}>
              {item.label}
            </a>
          ))}
        </nav>
        <main className="main">{children}</main>
      </body>
    </html>
  );
}
