import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen flex flex-col">
      <Navbar variant="marketing" />
      <main className="flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
}
