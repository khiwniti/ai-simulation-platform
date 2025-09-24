'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical, 
  Play, 
  Pause, 
  Settings, 
  Bell, 
  User,
  Zap,
  Folder,
  Clock,
  TrendingUp,
  Users,
  FileText,
  BarChart3,
  Cpu,
  Database,
  Activity
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '../../components/ui/button';
import { AnimatedContainer } from '../../components/animations/animated-container';
import { UserMenu } from '../../components/ui/user-menu';
import { CreateNotebookModal } from '../../components/notebook/CreateNotebookModal';

export default function EnsimuLabPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [showCreateNotebook, setShowCreateNotebook] = useState(false);
  const router = useRouter();

  // Mock data for projects
  const projects = [
    {
      id: '1',
      name: 'Airfoil CFD Analysis',
      type: 'Fluid Dynamics',
      status: 'running',
      progress: 75,
      lastModified: '2 minutes ago',
      collaborators: 3,
      simulations: 12
    },
    {
      id: '2', 
      name: 'Heat Transfer Study',
      type: 'Thermal Analysis',
      status: 'completed',
      progress: 100,
      lastModified: '1 hour ago',
      collaborators: 2,
      simulations: 8
    },
    {
      id: '3',
      name: 'Structural Optimization',
      type: 'Structural Analysis',
      status: 'pending',
      progress: 0,
      lastModified: '1 day ago',
      collaborators: 1,
      simulations: 0
    }
  ];

  const stats = [
    { label: 'Active Projects', value: '12', icon: Folder, color: 'text-blue-600' },
    { label: 'Running Simulations', value: '8', icon: Activity, color: 'text-green-600' },
    { label: 'Compute Hours', value: '247', icon: Cpu, color: 'text-purple-600' },
    { label: 'Team Members', value: '15', icon: Users, color: 'text-orange-600' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-50 border-green-200';
      case 'completed': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'pending': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const handleCreateNotebook = (notebookData: {
    name: string;
    description: string;
    template: string;
    type: string;
  }) => {
    // Generate a unique ID for the notebook
    const notebookId = Date.now().toString();
    
    // Navigate to the new notebook page
    router.push(`/notebook/${notebookId}?name=${encodeURIComponent(notebookData.name)}&template=${notebookData.template}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center group">
                <motion.div
                  className="relative p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg mr-3"
                  whileHover={{ scale: 1.05, rotate: 5 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <Zap className="w-5 h-5 text-white" />
                </motion.div>
                <div>
                  <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    EnsimuLab
                  </span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Where Simulations Come to Life
                  </p>
                </div>
              </Link>
            </div>

            {/* User Actions */}
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Bell className="w-4 h-4 mr-2" />
                Notifications
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <UserMenu />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <AnimatedContainer variant="slideUp" className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <h1 className="text-3xl font-bold mb-2">Welcome to EnsimuLab! 🚀</h1>
            <p className="text-blue-100 mb-6">
              Your engineering workspace is ready. Start creating simulations, analyzing data, and collaborating with your team.
            </p>
            <Button 
              variant="secondary" 
              size="lg"
              className="bg-white/20 hover:bg-white/30 text-white border-white/30"
              onClick={() => setShowCreateNotebook(true)}
            >
              <Plus className="w-5 h-5 mr-2" />
              Create New EnsimuNotebook
            </Button>
          </div>
        </AnimatedContainer>

        {/* Stats Dashboard */}
        <AnimatedContainer variant="slideUp" delay={0.2} className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl p-6 border border-white/20 shadow-lg"
                whileHover={{ scale: 1.02, y: -2 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      {stat.label}
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {stat.value}
                    </p>
                  </div>
                  <stat.icon className={`w-8 h-8 ${stat.color}`} />
                </div>
              </motion.div>
            ))}
          </div>
        </AnimatedContainer>

        {/* Projects Section */}
        <AnimatedContainer variant="slideUp" delay={0.4}>
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-white/20 shadow-xl">
            {/* Projects Header */}
            <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Recent Projects
                </h2>
                <Button variant="gradient" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  New Project
                </Button>
              </div>

              {/* Search & Filter */}
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search projects..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700/50 dark:text-white"
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
              </div>
            </div>

            {/* Projects List */}
            <div className="divide-y divide-gray-200/50 dark:divide-gray-700/50">
              {projects.map((project, index) => (
                <motion.div
                  key={project.id}
                  className="p-6 hover:bg-gray-50/50 dark:hover:bg-gray-700/20 transition-colors cursor-pointer"
                  whileHover={{ scale: 1.01 }}
                  onClick={() => setSelectedProject(project.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {project.name}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(project.status)}`}>
                          {project.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center space-x-1">
                          <FileText className="w-4 h-4" />
                          <span>{project.type}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Users className="w-4 h-4" />
                          <span>{project.collaborators} collaborators</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <BarChart3 className="w-4 h-4" />
                          <span>{project.simulations} simulations</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{project.lastModified}</span>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      {project.status === 'running' && (
                        <div className="mt-3">
                          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                            <span>Progress</span>
                            <span>{project.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <motion.div
                              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${project.progress}%` }}
                              transition={{ duration: 1, delay: index * 0.2 }}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {project.status === 'running' ? (
                        <Button variant="outline" size="sm">
                          <Pause className="w-4 h-4 mr-2" />
                          Pause
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm">
                          <Play className="w-4 h-4 mr-2" />
                          Run
                        </Button>
                      )}
                      <Button variant="outline" size="sm" className="px-2">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Empty State or Load More */}
            {projects.length === 0 && (
              <div className="p-12 text-center">
                <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No projects yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Get started by creating your first simulation project
                </p>
                <Button variant="gradient">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Project
                </Button>
              </div>
            )}
          </div>
        </AnimatedContainer>
      </div>

      {/* Create Notebook Modal */}
      <CreateNotebookModal
        isOpen={showCreateNotebook}
        onClose={() => setShowCreateNotebook(false)}
        onCreateNotebook={handleCreateNotebook}
      />
    </div>
  );
}