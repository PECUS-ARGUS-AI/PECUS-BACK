"use client";

import { useCallback } from "react";

export default function UploadCard({ onFileSelect }: { onFileSelect: (f: File) => void }) {
    const handleSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            onFileSelect(e.target.files[0]);
        }
    }, [onFileSelect]);

    return (
        <div className="w-full max-w-lg mx-auto">
            <label
                className="cursor-pointer flex flex-col items-center justify-center p-10 rounded-3xl 
                           border-2 border-dashed 
                           border-gray-400 dark:border-white/30 
                           bg-gray-200/50 dark:bg-white/10 
                           backdrop-blur-md 
                           transition 
                           hover:bg-gray-300/50 dark:hover:bg-white/20 
                           hover:border-gray-500 dark:hover:border-white/50 
                           hover:scale-[1.01] 
                           duration-300 shadow-xl"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-16 w-16 text-gray-700 dark:text-white mb-4 animate-pulse"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M3 15a4 4 0 014-4h10a4 4 0 110 8H7a4 4 0 01-4-4z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M12 3v12m0 0l-3-3m3 3l3-3" />
                </svg>

                <p className="text-gray-800 dark:text-white text-lg font-medium">
                    Clique aqui ou arraste uma imagem
                </p>
                <p className="text-gray-600 dark:text-white/60 text-sm mt-2">(JPG, JPEG, PNG)</p>

                <input type="file" className="hidden" accept="image/*" onChange={handleSelect} />
            </label>
        </div>
    );
}