import "./globals.css";

export const metadata = {
  title: "Tennis Predictor",
  description: "A simple homepage for the Tennis Predictor project.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
