"use client";
import { ThemeProvider } from "next-themes";

export default function ThemeProviderWrapper({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider 
      attribute="class" 
      defaultTheme="dark"
      enableColorScheme={false}  // ← Adiciona isso!
    >
      {children}
    </ThemeProvider>
  );
}