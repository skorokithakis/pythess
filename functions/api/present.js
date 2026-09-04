export async function onRequestPost(context) {
    const { request, env } = context;

    const formData = await request.formData();
    const name = formData.get("name");
    const email = formData.get("email");
    const title = formData.get("title");
    const description = formData.get("description");
    const comments = formData.get("comments");
    const turnstileToken = formData.get("cf-turnstile-response");

    // Verify the Turnstile token before doing anything else, so bots can't
    // trigger Discord notifications even if they bypass field validation.
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
    const turnstileResult = await turnstileResponse.json();
    if (!turnstileResult.success) {
        return new Response(JSON.stringify({ error: "Invalid Turnstile token" }), {
            status: 403,
            headers: { "Content-Type": "application/json" },
        });
    }

    const fields = { name, email, title, description };
    for (const [fieldName, value] of Object.entries(fields)) {
        if (!value || !value.trim()) {
            return new Response(
                JSON.stringify({ error: `Missing required field: ${fieldName}` }),
                { status: 400, headers: { "Content-Type": "application/json" } },
            );
        }
    }

    if (!email.trim().includes("@")) {
        return new Response(JSON.stringify({ error: "Invalid email address" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
        });
    }

    const embedFields = [
        { name: "Name", value: name.trim(), inline: true },
        { name: "Email", value: email.trim(), inline: true },
        { name: "Description", value: description.trim() },
    ];
    // Optional; Discord rejects embed fields with an empty value.
    if (comments && comments.trim()) {
        embedFields.push({ name: "Comments", value: comments.trim() });
    }

    const discordResponse = await fetch(env.DISCORD_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            embeds: [
                {
                    title: title.trim(),
                    color: 0x306998,
                    fields: embedFields,
                    timestamp: new Date().toISOString(),
                },
            ],
        }),
    });

    if (!discordResponse.ok) {
        return new Response(JSON.stringify({ error: "Failed to send notification" }), {
            status: 502,
            headers: { "Content-Type": "application/json" },
        });
    }

    return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
    });
}
