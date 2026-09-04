const PNG_SIGNATURE = new Uint8Array([
    0x89,
    0x50,
    0x4e,
    0x47,
    0x0d,
    0x0a,
    0x1a,
    0x0a,
]);

export async function onRequestPost(context) {
    const { request, env } = context;
    const contentLength = Number(request.headers.get("Content-Length"));

    if (contentLength > 300 * 1024) {
        return new Response(
            JSON.stringify({ error: "Request body must be 300KB or smaller" }),
            { status: 400, headers: { "Content-Type": "application/json" } },
        );
    }

    try {
        const formData = await request.formData();
        const name = formData.get("name");
        const email = formData.get("email");
        const drawing = formData.get("drawing");
        const turnstileToken = formData.get("cf-turnstile-response");

        // Verify the Turnstile token before doing anything else, so bots can't
        // trigger Discord notifications even if they bypass field validation.
        let turnstileResult;
        try {
            const turnstileResponse = await fetch(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: new URLSearchParams({
                        secret: env.TURNSTILE_SECRET_KEY,
                        response: turnstileToken ?? "",
                    }),
                },
            );
            turnstileResult = await turnstileResponse.json();
        } catch {
            return new Response(JSON.stringify({ error: "Invalid Turnstile token" }), {
                status: 403,
                headers: { "Content-Type": "application/json" },
            });
        }

        if (!turnstileResult.success) {
            return new Response(JSON.stringify({ error: "Invalid Turnstile token" }), {
                status: 403,
                headers: { "Content-Type": "application/json" },
            });
        }

        const fields = { name, email };
        for (const [fieldName, value] of Object.entries(fields)) {
            if (typeof value !== "string" || !value.trim()) {
                return new Response(
                    JSON.stringify({ error: `Missing required field: ${fieldName}` }),
                    { status: 400, headers: { "Content-Type": "application/json" } },
                );
            }
        }

        const trimmedName = name.trim();
        const trimmedEmail = email.trim();
        if (trimmedName.length > 100) {
            return new Response(
                JSON.stringify({ error: "Name must be 100 characters or fewer" }),
                { status: 400, headers: { "Content-Type": "application/json" } },
            );
        }

        if (trimmedEmail.length > 254) {
            return new Response(
                JSON.stringify({ error: "Email must be 254 characters or fewer" }),
                { status: 400, headers: { "Content-Type": "application/json" } },
            );
        }

        if (!trimmedEmail.includes("@")) {
            return new Response(JSON.stringify({ error: "Invalid email address" }), {
                status: 400,
                headers: { "Content-Type": "application/json" },
            });
        }

        if (!drawing || typeof drawing === "string") {
            return new Response(
                JSON.stringify({ error: "Missing required field: drawing" }),
                { status: 400, headers: { "Content-Type": "application/json" } },
            );
        }

        if (drawing.type !== "image/png") {
            return new Response(JSON.stringify({ error: "Drawing must be a PNG image" }), {
                status: 400,
                headers: { "Content-Type": "application/json" },
            });
        }

        if (drawing.size > 200 * 1024) {
            return new Response(
                JSON.stringify({ error: "Drawing must be 200KB or smaller" }),
                { status: 400, headers: { "Content-Type": "application/json" } },
            );
        }

        const drawingHeader = new Uint8Array(
            await drawing.slice(0, PNG_SIGNATURE.length).arrayBuffer(),
        );
        if (
            drawingHeader.length !== PNG_SIGNATURE.length ||
            !PNG_SIGNATURE.every((byte, index) => drawingHeader[index] === byte)
        ) {
            return new Response(
                JSON.stringify({ error: "Drawing must be a valid PNG image" }),
                { status: 400, headers: { "Content-Type": "application/json" } },
            );
        }

        const filename = "drawing.png";
        const discordFormData = new FormData();
        discordFormData.append(
            "payload_json",
            JSON.stringify({
                allowed_mentions: { parse: [] },
                embeds: [
                    {
                        title: "Νέα συμμετοχή στον ΜΕΓΑΛΟ ΔΙΑΓΩΝΙΣΜΟ",
                        color: 0x306998,
                        fields: [
                            { name: "Name", value: trimmedName, inline: true },
                            { name: "Email", value: trimmedEmail, inline: true },
                        ],
                        image: { url: `attachment://${filename}` },
                        timestamp: new Date().toISOString(),
                    },
                ],
            }),
        );
        discordFormData.append("files[0]", drawing, filename);

        let discordResponse;
        try {
            discordResponse = await fetch(env.DISCORD_CONTEST_WEBHOOK_URL, {
                method: "POST",
                body: discordFormData,
            });
        } catch {
            return new Response(
                JSON.stringify({ error: "Failed to send notification" }),
                { status: 502, headers: { "Content-Type": "application/json" } },
            );
        }

        if (!discordResponse.ok) {
            return new Response(
                JSON.stringify({ error: "Failed to send notification" }),
                { status: 502, headers: { "Content-Type": "application/json" } },
            );
        }

        return new Response(JSON.stringify({ ok: true }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
        });
    } catch {
        return new Response(JSON.stringify({ error: "Invalid form data" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
        });
    }
}
