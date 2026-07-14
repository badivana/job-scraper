# AI Job Finder - Frontend

This is the frontend of the AI Job Finder SaaS application.

## Technology Stack

- [Next.js 15](https://nextjs.org/)
- [React 18](https://reactjs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)

## Getting Started

1. Install dependencies: `npm install`
2. Run the development server: `npm run dev`
3. Open [http://localhost:3000](http://localhost:3000) to view the app.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm lint` - Run ESLint

## Project Structure

- `src/app` - Next.js app router (pages, layouts)
- `src/components` - Reusable components
- `src/lib` - Utility functions
- `public` - Static assets

## Styling

This project uses Tailwind CSS for styling. The theme is configured in `tailwind.config.ts` and includes custom CSS variables as defined in the UI context.

## UI Components

UI components are built using shadcn/ui. New components can be added using the `npx shadcn@latest add` command.