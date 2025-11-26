# IDM-VTON API Server

A FastAPI-style server built with Fastify and TypeScript that provides an API interface to the [IDM-VTON](https://huggingface.co/spaces/yisol/IDM-VTON) virtual try-on model via Gradio API.

## Features

- 🚀 Fast and efficient API server using Fastify
- 📝 TypeScript for type safety
- 🎨 Beautiful HTML web interface for testing
- 🖼️ Support for image upload and processing
- ⚙️ Configurable parameters (denoising steps, seed, etc.)
- 🔄 CORS enabled for cross-origin requests

## Prerequisites

- Node.js 18+
- pnpm (or npm/yarn)

## Installation

```bash
# Install dependencies
pnpm install
```

## Usage

### Development Mode

**Option 1: Backend Only (Original HTML UI)**
```bash
# Run API server with hot-reload
pnpm dev
```

**Option 2: Full Stack Development (Vue + Nuxt UI)**
```bash
# Terminal 1: Run API server
pnpm dev

# Terminal 2: Run frontend dev server
pnpm dev:frontend
```

The API server will start at `http://localhost:3000`
The frontend dev server will start at `http://localhost:5173` (with API proxy)

### Production Mode

```bash
# Build frontend and backend
pnpm build

# Start production server
pnpm start
```

This will:
1. Build the Vue frontend to `public/` directory
2. Compile TypeScript backend
3. Serve both frontend and API from `http://localhost:3000`

## API Endpoints

### Health Check

```
GET /health
```

Returns server status.

### Virtual Try-On

```
POST /api/tryon
```

**Parameters (multipart/form-data):**

- `humanImage` (file, required): Image of a person
- `garmentImage` (file, required): Image of a garment
- `description` (string, optional): Description of the desired output (default: "A person wearing the garment")
- `autoMask` (boolean, optional): Enable automatic masking (default: true)
- `autoCrop` (boolean, optional): Enable automatic cropping (default: true)
- `denoisingSteps` (number, optional): Number of denoising steps (default: 30)
- `seed` (number, optional): Random seed for reproducibility (default: 42)

**Response:**

```json
{
  "success": true,
  "outputImage": "data:image/png;base64,...",
  "maskedImage": "data:image/png;base64,..."
}
```

## Web Interface

Visit `http://localhost:3000` in your browser to access the interactive test interface where you can:

1. Upload a human image
2. Upload a garment image
3. Configure parameters
4. Generate try-on results
5. View output and masked images

## Configuration

Create a `.env` file in the root directory (see `.env.example`):

```env
# Server Configuration
PORT=3000
HOST=0.0.0.0

# Hugging Face Authentication (Optional but Recommended)
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_token_here
```

### Hugging Face Token

While the IDM-VTON space is public, using a Hugging Face token provides:
- **Higher priority in queue**: Authenticated requests are processed faster
- **Better rate limits**: Avoid throttling during high traffic
- **Access to private spaces**: If you need to use private models

To get your token:
1. Visit [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token with "read" permission
3. Copy the token to your `.env` file

The server will automatically detect and use the token if present.

## Example Usage with cURL

```bash
curl -X POST http://localhost:3000/api/tryon \
  -F "humanImage=@/path/to/human.png" \
  -F "garmentImage=@/path/to/garment.png" \
  -F "description=A person wearing the garment" \
  -F "autoMask=true" \
  -F "autoCrop=true" \
  -F "denoisingSteps=30" \
  -F "seed=42"
```

## Example Usage with JavaScript

```javascript
const formData = new FormData();
formData.append('humanImage', humanImageFile);
formData.append('garmentImage', garmentImageFile);
formData.append('description', 'A person wearing the garment');
formData.append('denoisingSteps', 30);

const response = await fetch('http://localhost:3000/api/tryon', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

## Project Structure

```
idm-vton/
├── src/                           # Backend source
│   ├── server.ts                  # Main Fastify server
│   ├── services/
│   │   └── vton.service.ts        # Gradio API integration
│   └── types/
│       └── index.ts               # TypeScript type definitions
├── interactive-closet/            # Frontend source (Vue + Nuxt UI)
│   ├── src/
│   │   ├── App.vue                # Main app component
│   │   ├── pages/
│   │   │   └── index.vue          # Main try-on interface
│   │   └── components/            # Reusable components
│   ├── vite.config.ts             # Vite configuration
│   └── package.json               # Frontend dependencies
├── public/                        # Built frontend (served by backend)
│   ├── index.html                 # Entry point
│   └── assets/                    # JS/CSS bundles
├── uploads/                       # Temporary file storage
├── dist/                          # Compiled backend (after build)
├── package.json                   # Root package.json
├── tsconfig.json                  # TypeScript configuration
└── README.md
```

## Technologies Used

### Backend
- [Fastify](https://www.fastify.io/) - Fast web framework
- [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript
- [@gradio/client](https://www.gradio.app/docs/client) - Gradio API client
- [@fastify/multipart](https://github.com/fastify/fastify-multipart) - File upload handling
- [@fastify/static](https://github.com/fastify/fastify-static) - Static file serving
- [@fastify/cors](https://github.com/fastify/fastify-cors) - CORS support

### Frontend
- [Vue 3](https://vuejs.org/) - Progressive JavaScript framework
- [Nuxt UI](https://ui.nuxt.com/) - Beautiful & accessible component library
- [Vite](https://vitejs.dev/) - Next generation frontend tooling
- [TypeScript](https://www.typescriptlang.org/) - Type-safe development

## License

MIT
