"use client";

import { useConversation } from "@elevenlabs/react";
import { useCallback, useState } from "react";
import { Mic, MicOff, Phone, PhoneOff } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function Conversation() {
    const [error, setError] = useState<string | null>(null);
    const conversation = useConversation({
        onConnect: () => console.log("Connected"),
        onDisconnect: () => console.log("Disconnected"),
        onMessage: (message) => console.log("Message:", message),
        onError: (e) => setError(typeof e === 'string' ? e : e.message),
    });

    const startConversation = useCallback(async () => {
        try {
            console.log("startConversation called");
            setError(null);

            if (!navigator.mediaDevices) {
                throw new Error("navigator.mediaDevices is undefined. Are you on HTTPS or localhost?");
            }

            // Request microphone permission first
            console.log("Requesting microphone permission...");
            await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log("Microphone permission granted");

            // Get signed URL
            console.log("Fetching signed URL...");
            const response = await fetch("/api/get-signed-url");
            console.log("Signed URL response status:", response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Failed to get signed URL:", errorText);
                throw new Error(`Failed to get signed URL: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Signed URL data received");

            if (!data.signedUrl) {
                throw new Error("Failed to get signed URL: No signedUrl in response");
            }

            console.log("Starting session with signed URL...");
            await conversation.startSession({
                signedUrl: data.signedUrl,
            });
            console.log("Session started");
        } catch (e: any) {
            console.error("Error in startConversation:", e);
            setError(e.message);
        }
    }, [conversation]);

    const stopConversation = useCallback(async () => {
        await conversation.endSession();
    }, [conversation]);

    const isConnected = conversation.status === "connected";
    const isSpeaking = conversation.isSpeaking;

    return (
        <div className="flex flex-col items-center justify-center space-y-8 p-8 w-full max-w-2xl mx-auto">
            <div className="relative">
                <AnimatePresence mode="wait">
                    {isConnected ? (
                        <motion.div
                            key="connected"
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            className="relative"
                        >
                            <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-colors duration-300 ${isSpeaking ? "bg-green-500 shadow-[0_0_30px_rgba(34,197,94,0.5)]" : "bg-blue-500 shadow-[0_0_30px_rgba(59,130,246,0.5)]"}`}>
                                <Mic className="w-12 h-12 text-white" />
                            </div>
                            {isSpeaking && (
                                <motion.div
                                    className="absolute inset-0 rounded-full border-4 border-green-400"
                                    animate={{ scale: [1, 1.2, 1], opacity: [1, 0, 1] }}
                                    transition={{ repeat: Infinity, duration: 1.5 }}
                                />
                            )}
                        </motion.div>
                    ) : (
                        <motion.div
                            key="disconnected"
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                        >
                            <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center">
                                <MicOff className="w-12 h-12 text-gray-400" />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <div className="flex flex-col items-center space-y-4">
                <h2 className="text-2xl font-bold text-gray-800">
                    {isConnected ? (isSpeaking ? "Agent is speaking..." : "Listening...") : "Ready to Call"}
                </h2>

                {error && (
                    <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm">
                        {error}
                    </div>
                )}

                <button
                    onClick={isConnected ? stopConversation : startConversation}
                    className={`px-8 py-4 rounded-full font-semibold text-lg flex items-center space-x-3 transition-all transform hover:scale-105 active:scale-95 ${isConnected
                        ? "bg-red-500 hover:bg-red-600 text-white shadow-lg hover:shadow-red-500/30"
                        : "bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-blue-600/30"
                        }`}
                >
                    {isConnected ? (
                        <>
                            <PhoneOff className="w-6 h-6" />
                            <span>End Call</span>
                        </>
                    ) : (
                        <>
                            <Phone className="w-6 h-6" />
                            <span>Start Call</span>
                        </>
                    )}
                </button>
            </div>

            {/* Transcript / Output Area */}
            <div className="w-full bg-gray-50 rounded-xl p-6 min-h-[200px] max-h-[400px] overflow-y-auto border border-gray-100">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Conversation Output</h3>
                <div className="space-y-2 text-gray-600">
                    <p className="italic text-sm text-gray-400">
                        The agent will ask for availability, price, and pickup time.
                        Speak clearly to provide this information.
                    </p>
                    {/* Note: The SDK might not expose the full transcript history directly in the hook state in all versions. 
                We can track it via onMessage if needed, but for now let's rely on the audio. 
                If we want to show text, we'd need to accumulate `onMessage` events.
            */}
                </div>
            </div>
        </div>
    );
}
