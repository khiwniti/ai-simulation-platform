'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Zap, 
  Brain, 
  Code, 
  Rocket, 
  ArrowRight, 
  Play,
  Cpu,
  Clock,
  Target,
  Users
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '../components/ui/button';

export default function Home() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Header */}
      <header className="relative z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <motion.div
                className="relative p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg mr-3"
                whileHover={{ scale: 1.05, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Zap className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  EnsimuNotebook
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  AI-Enhanced Engineering Simulation
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/notebook/demo">
                <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white">
                  <Play className="w-4 h-4 mr-2" />
                  Try Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Powering the world's best{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                engineering teams
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              AI-enhanced Jupyter notebooks for rapid engineering simulation. 
              Iterate faster by evaluating designs in seconds, not weeks.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/notebook/demo">
                <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white">
                  <Rocket className="w-5 h-5 mr-2" />
                  Start Simulating
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              
              <Button variant="outline" size="lg">
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Outcomes Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white/50 dark:bg-gray-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Outcomes
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Clock,
                title: "Get to market faster",
                description: "Iterate faster by evaluating designs in seconds, not weeks"
              },
              {
                icon: Target,
                title: "Create new, better products",
                description: "Test vastly more design ideas and converge on the best"
              },
              {
                icon: Users,
                title: "Reduce development risk",
                description: "Reduce late-stage reworks by exploring more designs, earlier"
              }
            ].map((outcome, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2 }}
                className="text-center p-6 rounded-xl bg-white dark:bg-gray-800 shadow-lg"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <outcome.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {outcome.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {outcome.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Applications Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Applications
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Rapid Design Iteration",
                subtitle: "Faster design cycles",
                description: "Highly accurate physics predictions in near real-time to guide every design decision.",
                icon: Zap
              },
              {
                title: "Design Exploration",
                subtitle: "Evaluate many concepts", 
                description: "Launch thousands of model predictions in parallel to map the entire design space.",
                icon: Brain
              },
              {
                title: "Optimization",
                subtitle: "Converge on an optimal solution",
                description: "Optimize across many design requirements with fast model predictions and AI assistance.",
                icon: Target
              }
            ].map((app, index) => (
              <motion.div
                key={index}
                onHoverStart={() => setHoveredFeature(index)}
                onHoverEnd={() => setHoveredFeature(null)}
                className="relative p-8 rounded-xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer"
                whileHover={{ y: -5 }}
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                  <app.icon className="w-6 h-6 text-white" />
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  {app.title}
                </h3>
                
                <h4 className="text-sm font-semibold text-blue-600 dark:text-blue-400 mb-3">
                  {app.subtitle}
                </h4>
                
                <p className="text-gray-600 dark:text-gray-300">
                  {app.description}
                </p>

                {hoveredFeature === index && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute inset-0 border-2 border-blue-500 rounded-xl"
                  />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white/50 dark:bg-gray-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Capabilities
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                AI-Enhanced Development
              </h3>
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
                Develop, train & visualize Physics AI models in an integrated notebook 
                with intelligent code assistance for engineering simulations.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-gray-700 dark:text-gray-300">AI-powered code generation</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Code className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-gray-700 dark:text-gray-300">Physics simulation libraries</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Cpu className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-gray-700 dark:text-gray-300">Real-time visualization</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-8">
              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Zap className="w-12 h-12 text-white" />
                </div>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Ready to start?
                </h4>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  Jump into our AI-enhanced notebook and start building simulations.
                </p>
                <Link href="/notebook/demo">
                  <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white">
                    Open Notebook
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Metrics */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Scale. Speed. Accuracy.
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                number: "10k",
                label: "Test 10k designs in minutes with AI assistance.",
                icon: Target
              },
              {
                number: "2s",
                label: "Performance predictions in seconds via model inference.",
                icon: Clock
              },
              {
                number: "<1%",
                label: "Less than 1% error with AI-enhanced calculations.",
                icon: Brain
              }
            ].map((metric, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-8 rounded-xl bg-white dark:bg-gray-800 shadow-lg"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <metric.icon className="w-8 h-8 text-white" />
                </div>
                <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  {metric.number}
                </div>
                <p className="text-gray-600 dark:text-gray-300">
                  {metric.label}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-500 to-purple-600">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Discover EnsimuNotebook today.
            </h2>
            
            <p className="text-xl text-blue-100 mb-8">
              Start building AI-enhanced engineering simulations in your browser.
            </p>

            <Link href="/notebook/demo">
              <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100">
                <Rocket className="w-5 h-5 mr-2" />
                Start Building
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">EnsimuNotebook</span>
          </div>
          <p className="text-gray-400">
            AI-Enhanced Engineering Simulation • Beta Version
          </p>
        </div>
      </footer>
    </main>
  );
}