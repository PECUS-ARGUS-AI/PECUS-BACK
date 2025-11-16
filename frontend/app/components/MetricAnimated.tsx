"use client";

import { useEffect, useState } from "react";

export default function MetricAnimated({ label, value }: { label: string; value: number }) {
    const [display, setDisplay] = useState(0);

    useEffect(() => {
        let start = 0;
        const end = value;
        const duration = 1200;
        const step = 16;

        const increment = (end - start) / (duration / step);

        const interval = setInterval(() => {
            start += increment;
            if (start >= end) {
                clearInterval(interval);
                setDisplay(end);
            } else {
                setDisplay(start);
            }
        }, step);

        return () => clearInterval(interval);
    }, [value]);

    return (
        <div className="bg-black/10 dark:bg-white/10 p-4 rounded-xl text-center">
            <p className="text-black/60 dark:text-white/60 text-sm">{label}</p>
            <p className="text-2xl font-bold mt-1">{display.toFixed(2)}</p>
        </div>
    );
}