// Public browser configuration shared by the admin page and public reviews.
// Copy this file to supabase-public-config.js and replace the placeholders.
// The anon/publishable key is designed for browser use; database RLS must remain enabled.
// NEVER place the Supabase service_role secret key here.
window.SMART_BUNNY_SUPABASE = {
  url: "https://YOUR_PROJECT.supabase.co",
  anonKey: "YOUR_PUBLIC_ANON_OR_PUBLISHABLE_KEY"
};
