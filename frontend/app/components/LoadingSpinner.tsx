export default function LoadingSpinner() {
    return (
        <div className="flex flex-col items-center mt-6">
            <div className="h-10 w-10 border-4 border-black dark:border-white border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 animate-pulse">Processando imagem...</p>
        </div>
    );
}