// export const API_BASE_URL = "https://ai-job-application-assistant-dy68.onrender.com";
// for local testing, use the line below and comment out the line above
export const API_BASE_URL = "http://127.0.0.1:8000";

// The resume editor is a separate standalone app (React+Vite), embedded via
// iframe rather than merged into this app's build-free stack. Local-dev-only
// for now - it isn't deployed anywhere yet.
export const RESUME_EDITOR_URL = "http://localhost:5173";
export const RESUME_EDITOR_ORIGIN = "http://localhost:5173";

// These are Supabase's public "anon" values - safe to ship in frontend code.
// Fill them in from your Supabase project's Settings -> API page.
export const SUPABASE_URL = "https://pzpwkdmuziccglzjedvx.supabase.co";
export const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB6cHdrZG11emljY2dsemplZHZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYzODkzMzUsImV4cCI6MjEwMTk2NTMzNX0.1_tc9r7Psgr0ZYRMNcyZvQOHJTjWzYEGytEFTNCOw7I";
