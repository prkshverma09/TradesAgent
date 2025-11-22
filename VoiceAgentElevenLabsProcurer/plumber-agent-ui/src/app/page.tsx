import { Conversation } from "@/components/Conversation";

export default function Home() {
    return (
        <main className="min-h-screen bg-white flex flex-col items-center justify-center p-4">
            <div className="text-center mb-12">
                <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">
                    Plumber Voice Agent
                </h1>
                <p className="text-lg text-gray-600 max-w-md mx-auto">
                    This agent represents a plumber calling a hardware store.
                    Act as the store clerk and provide availability, price, and pickup time.
                </p>
            </div>

            <Conversation />
        </main>
    );
}
