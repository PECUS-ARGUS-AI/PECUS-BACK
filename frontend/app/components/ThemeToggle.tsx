"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => setMounted(true), []);
    
    // Retorna um placeholder invisível ao invés de null
    if (!mounted) {
        return (
            <button className="fixed top-6 right-6 bg-white/10 dark:bg-black/20 
                       p-3 rounded-full shadow-xl backdrop-blur-md opacity-0">
                🌙
            </button>
        );
    }

    return (
        <button
            onClick={() => {
                console.log("Tema atual:", theme);
                setTheme(theme === "dark" ? "light" : "dark");
            }}
            className="fixed top-6 right-6 bg-white/10 dark:bg-black/20 
                       p-3 rounded-full shadow-xl backdrop-blur-md 
                       hover:scale-110 transition cursor-pointer"
        >
            {theme === "dark" ? "🌞" : "🌙"}
        </button>
    );
}