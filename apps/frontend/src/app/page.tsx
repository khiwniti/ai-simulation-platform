import { Navigation } from '../components/layout/navigation'
import { HeroSection } from '../components/layout/hero-section'

export default function Home() {
  return (
    <main className="relative">
      <Navigation />
      <HeroSection />
      
      {/* Additional sections will be added here */}
      <section id="platform" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">Platform Features</h2>
            <p className="text-gray-600 dark:text-gray-300">Coming soon...</p>
          </div>
        </div>
      </section>
    </main>
  );
}