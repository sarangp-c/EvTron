import "./globals.css";

export const metadata = {
  title: "EvTron | Campus Events",
  description: "Discover what's happening on campus with EvTron.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
