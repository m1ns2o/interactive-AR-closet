export interface VTONRequest {
	humanImage: Buffer;
	garmentImage: Buffer;
	description?: string;
	autoMask?: boolean;
	autoCrop?: boolean;
	denoisingSteps?: number;
	seed?: number;
}

export interface VTONResponse {
	success: boolean;
	outputImage?: string;
	maskedImage?: string;
	error?: string;
}

export interface ImageEditorData {
	background: string | Blob | File;
	layers: any[];
	composite: any;
}

export interface GradioVTONParams {
	humanImageEditor: ImageEditorData;
	garmentImage: Blob;
	description: string;
	autoMask: boolean;
	autoCrop: boolean;
	denoisingSteps: number;
	seed: number;
}

export interface GradioVTONResult {
	data: [string, string];
}

export interface GradioStatusEvent {
	type: "status";
	endpoint: string;
	stage: "pending" | "generating" | "complete" | "error";
	queue?: boolean;
	position?: number;
	eta?: number;
	success?: boolean;
	time?: Date;
	progress?: number;
	message?: string;
}

export interface GradioDataEvent {
	type: "data";
	endpoint: string;
	data: any[];
	time: Date;
}
