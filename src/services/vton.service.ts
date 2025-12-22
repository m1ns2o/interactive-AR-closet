import { Client } from "@gradio/client";
import type {
	VTONRequest,
	VTONResponse,
	GradioStatusEvent,
	GradioDataEvent,
	ProgressInfo,
} from "../types/index.js";

export type ProgressCallback = (info: ProgressInfo) => void;

export class VTONService {
	private readonly spaceId = "m1ns2o/IDM-VTON";
	private readonly apiName = "/tryon";
	// Estimated processing time in seconds (based on typical IDM-VTON runs)
	private readonly ESTIMATED_PROCESSING_TIME = 30;

	async processTryOn(
		request: VTONRequest,
		onProgress?: ProgressCallback
	): Promise<VTONResponse> {
		// Track state for accurate progress
		let lastKnownEta: number | undefined;
		let lastQueuePosition: number | undefined;
		let lastQueueSize: number | undefined;
		let processingStartTime: number | undefined;
		let progressUpdateInterval: ReturnType<typeof setInterval> | undefined;

		const sendProgress = (info: Partial<ProgressInfo>) => {
			onProgress?.({
				status: info.status ?? "processing",
				progress: info.progress ?? 0,
				message: info.message ?? "Processing...",
				eta: info.eta ?? lastKnownEta,
				queuePosition: info.queuePosition ?? lastQueuePosition,
				queueSize: info.queueSize ?? lastQueueSize,
				stepProgress: info.stepProgress,
			});
		};

		try {
			console.log("Connecting to Gradio space:", this.spaceId);
			sendProgress({
				status: "connecting",
				progress: 5,
				message: "Connecting to Gradio space...",
			});

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
			sendProgress({
				status: "submitting",
				progress: 10,
				message: "Submitting request to server...",
			});

			const job = app.submit(this.apiName, [
				imageEditorData,
				garmentImageBlob,
				request.description || "A person wearing the garment",
				request.autoMask ?? true,
				request.autoCrop ?? true,
				request.denoisingSteps ?? 30,
				request.seed ?? 42,
			]);

			// Start progress interval immediately after job submission
			processingStartTime = Date.now();
			progressUpdateInterval = setInterval(() => {
				if (!processingStartTime) return;

				const elapsed = (Date.now() - processingStartTime) / 1000;
				const estimatedTotal = this.ESTIMATED_PROCESSING_TIME;

				// Progress from 15% to 95% based on elapsed time
				// Use easing function for more natural feel
				const rawProgress = elapsed / estimatedTotal;
				const easedProgress = 1 - Math.pow(1 - Math.min(rawProgress, 1), 2);
				const progressPercent = 15 + easedProgress * 80;

				const remainingTime = Math.max(0, Math.ceil(estimatedTotal - elapsed));

				sendProgress({
					status: "generating",
					progress: Math.min(95, progressPercent),
					message: `Generating... (~${remainingTime}s remaining)`,
					eta: remainingTime,
				});
			}, 500);

			// Use Promise wrapper with async IIFE to handle iterator properly
			return new Promise<VTONResponse>((resolve, reject) => {
				(async () => {
					try {
						for await (const event of job) {
							console.log("Job event:", JSON.stringify(event));

							if (event.type === "status") {
								const statusEvent = event as unknown as GradioStatusEvent;
								const stage = statusEvent.stage;

								if (statusEvent.eta !== undefined) {
									lastKnownEta = statusEvent.eta;
								}
								if (statusEvent.position !== undefined) {
									lastQueuePosition = statusEvent.position;
								}
								if (statusEvent.queue_size !== undefined) {
									lastQueueSize = statusEvent.queue_size;
								}

								if (stage === "pending") {
									const positionText =
										lastQueuePosition !== undefined
											? `Position ${lastQueuePosition + 1}${lastQueueSize ? ` of ${lastQueueSize}` : ""}`
											: "Waiting in queue";
									const etaText = lastKnownEta
										? ` (ETA: ${Math.ceil(lastKnownEta)}s)`
										: "";

									sendProgress({
										status: "pending",
										progress: 15,
										message: `${positionText}${etaText}...`,
										queuePosition: lastQueuePosition,
										queueSize: lastQueueSize,
										eta: lastKnownEta,
									});
								} else if (stage === "generating") {
									// Progress is handled by the main interval
								} else if (stage === "complete") {
									// Just wait for data event
								} else if (stage === "error") {
									// Clear progress interval
									if (progressUpdateInterval) {
										clearInterval(progressUpdateInterval);
										progressUpdateInterval = undefined;
									}
									sendProgress({
										status: "error",
										progress: 0,
										message: statusEvent.message || "An error occurred",
									});
								}
							} else if (event.type === "data") {
								// Clear progress interval
								if (progressUpdateInterval) {
									clearInterval(progressUpdateInterval);
									progressUpdateInterval = undefined;
								}

								const dataEvent = event as unknown as GradioDataEvent;

								sendProgress({
									status: "complete",
									progress: 100,
									message: "Done!",
								});

								console.log("Received response from Gradio API");
								console.log(
									"Response data:",
									JSON.stringify(dataEvent.data, null, 2)
								);

								if (!dataEvent.data || dataEvent.data.length < 2) {
									reject(new Error("Invalid response from Gradio API"));
									return;
								}

								const outputImage =
									typeof dataEvent.data[0] === "object" &&
									dataEvent.data[0] !== null
										? (dataEvent.data[0] as any).url
										: dataEvent.data[0];

								const maskedImage =
									typeof dataEvent.data[1] === "object" &&
									dataEvent.data[1] !== null
										? (dataEvent.data[1] as any).url
										: dataEvent.data[1];

								console.log("Output image URL:", outputImage);
								console.log("Masked image URL:", maskedImage);
								console.log("Returning successful response");

								resolve({
									success: true,
									outputImage,
									maskedImage,
								});
								return; // Exit the async function immediately after resolve
							}
						}
						// If loop finishes without data
						if (progressUpdateInterval) {
							clearInterval(progressUpdateInterval);
							progressUpdateInterval = undefined;
						}
						reject(new Error("Stream finished without returning data"));
					} catch (err) {
						if (progressUpdateInterval) {
							clearInterval(progressUpdateInterval);
							progressUpdateInterval = undefined;
						}
						reject(err);
					}
				})();
			});
		} catch (error) {
			console.error("Error processing virtual try-on:", error);
			sendProgress({
				status: "error",
				progress: 0,
				message: error instanceof Error ? error.message : "Unknown error",
			});
			return {
				success: false,
				error:
					error instanceof Error ? error.message : "Unknown error occurred",
			};
		}
	}
}
