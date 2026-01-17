# Routey - Tourism Chat Bot Frontend

A Next.js frontend for an intelligent tourism chatbot that helps users discover events, attractions, and activities.

## Features

- 🌍 **Dual-Language Support**: English & Arabic (RTL support)
-  **Real-Time Streaming**: Token-by-token responses with SSE
-  **Responsive Design**: Works on mobile, tablet, and desktop
-  **EY Brand Design**: Professional dark theme with accent colors
-  **Conversation History**: Persistent multi-conversation management
-  **Easy Setup**: Just 1 environment variable needed

## Quick Start

### Prerequisites
- Node.js 18+ (LTS)
- npm or yarn

### Installation

1. Clone the repository
\\\ash
git clone https://github.com/your-org/Tourism-Chatbot.git
cd Tourism-Chatbot/frontend
\\\

2. Install dependencies
\\\ash
npm install
\\\

3. Set up environment
\\\ash
cp .env.example .env.local
# Edit .env.local and add your backend URL if needed
\\\

4. Run development server
\\\ash
npm run dev
\\\

5. Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

See \.env.example\ for configuration:
- \NEXT_PUBLIC_API_URL\ - Backend API endpoint (default: http://localhost:8000)

## Scripts

- \
pm run dev\ - Start development server with hot reload
- \
pm run build\ - Build for production
- \
pm start\ - Run production build
- \
pm run lint\ - Run ESLint checks

## Pages

- **Home** (\/\) - Main chat interface
- **Settings** (\/settings\) - Language & preferences
- **Account** (\/account\) - Profile management
- **Help** (\/help\) - FAQs and documentation

## Technology Stack

- **Framework**: Next.js 16.1.1 with Turbopack
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **React**: 19.2.3

## Architecture

### Components
- **page.tsx** - Main chat interface with SSE streaming
- **settings/page.tsx** - User preferences and language selection
- **account/page.tsx** - Profile and account management
- **help/page.tsx** - Help center and FAQs

### Libraries
- **api.ts** - Centralized backend API client
- **translations.ts** - Multi-language support (English & Arabic)

## Backend Connection

The frontend communicates with FastAPI backend via:
- \POST /chat/stream\ - SSE streaming responses
- \GET /health\ - Backend health check
- \GET/PUT /user/profile\ - User management
- \GET/PUT /user/settings\ - Settings management

## Multi-Language Support

Currently supports:
-  English
-  العربية (Arabic with RTL)
-  Español
-  Français
-  Deutsch
-  Italiano

Language preference is saved to localStorage and persists across sessions.

## Contributing

1. Fork the repository
2. Create feature branch (\git checkout -b feature/AmazingFeature\)
3. Commit changes (\git commit -m 'Add AmazingFeature'\)
4. Push to branch (\git push origin feature/AmazingFeature\)
5. Open a Pull Request

## Deployment

### Production Build
\\\ash
npm run build
npm start
\\\

### Environment Variables for Production
- Set \NEXT_PUBLIC_API_URL\ to your production backend URL

### Vercel Deployment (Recommended)
1. Connect repo to Vercel
2. Set environment variable \NEXT_PUBLIC_API_URL\
3. Deploy (automatic on push)

## License

MIT License - See LICENSE file for details

## Support

For questions or issues, please open an issue on GitHub.
