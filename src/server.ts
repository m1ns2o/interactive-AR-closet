import "dotenv/config";
import Fastify from "fastify";
import multipart from "@fastify/multipart";
import fastifyStatic from "@fastify/static";
import cors from "@fastify/cors";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { VTONService } from "./services/vton.service.js";
import type { VTONRequest } from "./types/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const fastify = Fastify({
	logger: {
		level: "info",
		transport: {
			target: "pino-pretty",
			options: {
				translateTime: "HH:MM:ss Z",
				ignore: "pid,hostname",
			},
		},
	},
});

await fastify.register(cors, {
	origin: true,
});

await fastify.register(multipart, {
	limits: {
		fileSize: 10 * 1024 * 1024, // 10MB
		files: 2,
	},
});

await fastify.register(fastifyStatic, {
	root: join(__dirname, "../public"),
	prefix: "/",
});

const vtonService = new VTONService();

// Store SSE connections by session ID
const progressStreams = new Map<string, any>();

fastify.get("/health", async () => {
	return { status: "ok", timestamp: new Date().toISOString() };
});

// SSE endpoint for progress updates
fastify.get("/api/progress/:sessionId", async (request, reply) => {
	const { sessionId } = request.params as { sessionId: string };

	reply.raw.writeHead(200, {
		"Content-Type": "text/event-stream",
		"Cache-Control": "no-cache",
		Connection: "keep-alive",
		"Access-Control-Allow-Origin": "*",
	});

	progressStreams.set(sessionId, reply.raw);

	request.raw.on("close", () => {
		progressStreams.delete(sessionId);
	});
});

fastify.post("/api/tryon", async (request, reply) => {
	try {
		const parts = request.parts();
		let humanImage: Buffer | null = null;
		let garmentImage: Buffer | null = null;
		let description = "A person wearing the garment";
		let autoMask = true;
		let autoCrop = true;
		let denoisingSteps = 30;
		let seed = 42;
		let sessionId: string | null = null;

		for await (const part of parts) {
			if (part.type === "file") {
				const buffer = await part.toBuffer();

				if (part.fieldname === "humanImage") {
					humanImage = buffer;
				} else if (part.fieldname === "garmentImage") {
					garmentImage = buffer;
				}
			} else {
				const value = (part as any).value;

				if (part.fieldname === "description") {
					description = value;
				} else if (part.fieldname === "autoMask") {
					autoMask = value === "true" || value === true;
				} else if (part.fieldname === "autoCrop") {
					autoCrop = value === "true" || value === true;
				} else if (part.fieldname === "denoisingSteps") {
					denoisingSteps = parseInt(value, 10);
				} else if (part.fieldname === "seed") {
					seed = parseInt(value, 10);
				} else if (part.fieldname === "sessionId") {
					sessionId = value;
				}
			}
		}

		if (!humanImage || !garmentImage) {
			return reply.code(400).send({
				success: false,
				error: "Both humanImage and garmentImage are required",
			});
		}

		const vtonRequest: VTONRequest = {
			humanImage,
			garmentImage,
			description,
			autoMask,
			autoCrop,
			denoisingSteps,
			seed,
		};

		fastify.log.info("Processing virtual try-on request");

		// Progress callback to send SSE updates with full ProgressInfo
		const onProgress = (info: {
			status: string;
			progress: number;
			message: string;
			eta?: number;
			queuePosition?: number;
			queueSize?: number;
			stepProgress?: { current: number; total: number; unit: string };
		}) => {
			if (sessionId && progressStreams.has(sessionId)) {
				const stream = progressStreams.get(sessionId);
				const data = JSON.stringify(info);
				stream.write(`data: ${data}\n\n`);
			}
		};

		const result = await vtonService.processTryOn(vtonRequest, onProgress);
		fastify.log.info("TryOn processing complete, sending response...");

		// Close the SSE stream
		if (sessionId && progressStreams.has(sessionId)) {
			try {
				const stream = progressStreams.get(sessionId);
				stream.write(
					`data: ${JSON.stringify({ status: "complete", progress: 100 })}\n\n`
				);
				stream.end();
				progressStreams.delete(sessionId);
				fastify.log.info("SSE stream closed");
			} catch (err) {
				fastify.log.error({ err }, "Error closing SSE stream");
			}
		}

		if (!result.success) {
			fastify.log.error("VTON failed, returning error response");
			return reply.code(500).send(result);
		}

		return reply.send(result);
	} catch (error) {
		fastify.log.error({ error }, "Error handling /api/tryon");
		return reply.code(500).send({
			success: false,
			error: error instanceof Error ? error.message : "Internal server error",
		});
	}
});

const start = async () => {
	try {
		const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;
		const host = process.env.HOST || "0.0.0.0";

		await fastify.listen({ port, host });

		const hasToken = !!process.env.HF_TOKEN;
		const tokenStatus = hasToken ? "✅ Authenticated" : "⚠️  No authentication";

		console.log(`
🚀 IDM-VTON API Server is running!

🔌 API Server:     http://localhost:${port} (Backend)
🎨 Frontend Dev:   http://localhost:5173 (Open this for Development!)
💡 API Endpoint:   http://localhost:${port}/api/tryon
❤️  Health Check:   http://localhost:${port}/health
🔑 HF Token:       ${tokenStatus}
    `);
	} catch (err) {
		fastify.log.error(err);
		process.exit(1);
	}
};

start();
