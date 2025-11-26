import { Client } from "@gradio/client";
import type {
	VTONRequest,
	VTONResponse,
	GradioStatusEvent,
	GradioDataEvent,
} from "../types/index.js";

export type ProgressCallback = (
	status: string,
	progress?: number,
	message?: string
) => void;

export class VTONService {
	private readonly spaceId = "yisol/IDM-VTON";
	private readonly apiName = "/tryon";

	async processTryOn(
		request: VTONRequest,
		onProgress?: ProgressCallback
	): Promise<VTONResponse> {
		try {
			console.log("Connecting to Gradio space:", this.spaceId);
			onProgress?.("connecting", 10, "Connecting to Gradio space...");

			// Get HF token from environment variable if available
			const hfToken = process.env.HF_TOKEN;

			if (hfToken) {
				console.log("Using Hugging Face authentication token");
			} else {
				console.log("No HF token found, connecting without authentication");
			}

			const app = await Client.connect(this.spaceId, {
				hf_token: hfToken as `hf_${string}` | undefined,
			});

			const humanImageBlob = new Blob([request.humanImage], {
				type: "image/png",
			});
			const garmentImageBlob = new Blob([request.garmentImage], {
				type: "image/png",
			});

			const imageEditorData = {
				background: humanImageBlob,
				layers: [],
				composite: null,
			};

			console.log("Sending request to Gradio API...");
			onProgress?.("submitting", 20, "Submitting request...");

			const job = app.submit(this.apiName, [
				imageEditorData,
				garmentImageBlob,
				request.description || "A person wearing the garment",
				request.autoMask ?? true,
				request.autoCrop ?? true,
				request.denoisingSteps ?? 30,
				request.seed ?? 42,
			]);

			let result: any = null;
			let completed = false;

			// Start timer-based progress updates (estimated 60-70 seconds total)
			const startTime = Date.now();
			const estimatedDuration = 65000; // 65 seconds average

			const progressInterval = setInterval(() => {
				if (completed) {
					clearInterval(progressInterval);
					return;
				}

				const elapsed = Date.now() - startTime;
				const progress = Math.min(90, 20 + (elapsed / estimatedDuration) * 70);
				const remaining = Math.max(
					0,
					Math.ceil((estimatedDuration - elapsed) / 1000)
				);

				let message = "Processing images...";
				if (elapsed < 5000) {
					message = "Connecting to server...";
				} else if (elapsed < 10000) {
					message = "Waiting in queue...";
				} else if (elapsed < 20000) {
					message = "Starting AI processing...";
				} else if (remaining > 15) {
					message = `AI is working hard... (~${remaining}s remaining)`;
				} else if (remaining > 5) {
					message = `Almost done! (~${remaining}s remaining)`;
				} else {
					message = "Finalizing your result...";
				}

				onProgress?.("processing", progress, message);
			}, 1000); // Update every second

			// Listen to events from the job
			try {
				for await (const event of job) {
					console.log("Job event:", event);

					if (event.type === "status") {
						const statusEvent = event as unknown as GradioStatusEvent;
						const stage = statusEvent.stage;
						console.log("Status stage:", stage);

						if (stage === "pending") {
							onProgress?.("pending", 30, "Request in queue...");
						} else if (stage === "generating") {
							// 'processing' is often 'generating' in newer versions, checking both or sticking to known ones
							onProgress?.("processing", 50, "Processing images...");
						} else if (stage === "complete") {
							onProgress?.("complete", 95, "Finalizing results...");
						}
					} else if (event.type === "data") {
						const dataEvent = event as unknown as GradioDataEvent;
						result = dataEvent;
						completed = true;
						clearInterval(progressInterval);
						onProgress?.("complete", 95, "Finalizing results...");
					}
				}
			} finally {
				clearInterval(progressInterval);
				completed = true;
			}

			console.log("Received response from Gradio API");
			console.log("Response data:", JSON.stringify(result.data, null, 2));

			if (!result.data || result.data.length < 2) {
				throw new Error("Invalid response from Gradio API");
			}

			// Gradio API returns objects with 'url' property, not direct strings
			const outputImage =
				typeof result.data[0] === "object" && result.data[0] !== null
					? (result.data[0] as any).url
					: result.data[0];

			const maskedImage =
				typeof result.data[1] === "object" && result.data[1] !== null
					? (result.data[1] as any).url
					: result.data[1];

			console.log("Output image URL:", outputImage);
			console.log("Masked image URL:", maskedImage);

			onProgress?.("done", 100, "Complete!");

			return {
				success: true,
				outputImage,
				maskedImage,
			};
		} catch (error) {
			console.error("Error processing virtual try-on:", error);
			onProgress?.(
				"error",
				0,
				error instanceof Error ? error.message : "Unknown error"
			);
			return {
				success: false,
				error:
					error instanceof Error ? error.message : "Unknown error occurred",
			};
		}
	}
}
