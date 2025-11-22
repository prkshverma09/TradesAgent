import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { NextResponse } from "next/server";

export async function GET() {
    const client = new ElevenLabsClient({
        apiKey: process.env.ELEVENLABS_API_KEY,
    });

    const agentId = "agent_6101kap5qq6wfyn9sddyrrgrz77k"; // Hardcoded for now

    try {
        // Note: The SDK might not have a direct helper for signed URLs yet, 
        // but usually it's an endpoint like /v1/convai/conversation/get_signed_url
        // If the SDK doesn't support it, we can fetch directly.
        // Let's try to find it in the SDK or use fetch.

        // Using fetch for certainty as SDK method names vary
        const response = await fetch(
            `https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id=${agentId}`,
            {
                method: "GET",
                headers: {
                    "xi-api-key": process.env.ELEVENLABS_API_KEY!,
                },
            }
        );

        if (!response.ok) {
            throw new Error("Failed to get signed URL");
        }

        const data = await response.json();
        return NextResponse.json({ signedUrl: data.signed_url });
    } catch (error) {
        console.error("Error getting signed URL:", error);
        return NextResponse.json({ error: "Failed to get signed URL" }, { status: 500 });
    }
}
