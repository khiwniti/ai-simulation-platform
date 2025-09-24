'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Separator } from '../../components/ui/separator';
import { 
  Calculator, 
  Waves, 
  Thermometer, 
  Zap, 
  Play, 
  Settings,
  Wrench,
  BarChart3,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface SimulationResults {
  [key: string]: any;
}

interface SimulationConfig {
  type: string;
  parameters: { [key: string]: any };
}

const SimulationPage = () => {
  const [activeTab, setActiveTab] = useState('fea');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [materials, setMaterials] = useState<any>({});
  const [simulationTypes, setSimulationTypes] = useState<any>({});
  const [config, setConfig] = useState<SimulationConfig>({
    type: 'fea',
    parameters: {}
  });

  // Fetch available materials and simulation types
  useEffect(() => {
    const fetchSimulationData = async () => {
      try {
        const [materialsRes, typesRes] = await Promise.all([
          fetch('/api/simulations/materials'),
          fetch('/api/simulations/types')
        ]);
        
        const materialsData = await materialsRes.json();
        const typesData = await typesRes.json();
        
        if (materialsData.success) setMaterials(materialsData.materials);
        if (typesData.success) setSimulationTypes(typesData.simulationTypes);
      } catch (error) {
        console.error('Error fetching simulation data:', error);
      }
    };

    fetchSimulationData();
  }, []);

  const runSimulation = async () => {
    setIsRunning(true);
    try {
      const response = await fetch(`/api/simulations/${activeTab}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config.parameters)
      });

      const data = await response.json();
      if (data.success) {
        setResults(data.results);
      } else {
        console.error('Simulation failed:', data.error);
      }
    } catch (error) {
      console.error('Error running simulation:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const updateConfig = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [key]: value
      }
    }));
  };

  const simulationIcons = {
    fea: Calculator,
    cfd: Waves,
    thermal: Thermometer
  };

  const getIcon = (type: string) => {
    const IconComponent = simulationIcons[type as keyof typeof simulationIcons] || Zap;
    return IconComponent;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent mb-4">
            Physics Simulation Engine
          </h1>
          <p className="text-gray-300 text-lg max-w-2xl mx-auto">
            Advanced engineering simulations powered by NumPy, SciPy, and AI-driven insights
          </p>
        </motion.div>

        {/* Simulation Type Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-800/50 backdrop-blur-sm border border-slate-700">
              <TabsTrigger 
                value="fea" 
                className="data-[state=active]:bg-blue-600 data-[state=active]:text-white"
              >
                <Calculator className="w-4 h-4 mr-2" />
                FEA
              </TabsTrigger>
              <TabsTrigger 
                value="cfd"
                className="data-[state=active]:bg-purple-600 data-[state=active]:text-white"
              >
                <Waves className="w-4 h-4 mr-2" />
                CFD
              </TabsTrigger>
              <TabsTrigger 
                value="thermal"
                className="data-[state=active]:bg-red-600 data-[state=active]:text-white"
              >
                <Thermometer className="w-4 h-4 mr-2" />
                Thermal
              </TabsTrigger>
            </TabsList>

            {/* FEA Configuration */}
            <TabsContent value="fea" className="mt-6">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-blue-600/20 rounded-lg">
                        <Calculator className="w-6 h-6 text-blue-400" />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-white">Finite Element Analysis</h3>
                        <p className="text-gray-400">Structural analysis with beam elements</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="length" className="text-gray-300">Length (m)</Label>
                          <Input
                            id="length"
                            type="number"
                            placeholder="1.0"
                            value={config.parameters.length || ''}
                            onChange={(e) => updateConfig('length', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                        <div>
                          <Label htmlFor="height" className="text-gray-300">Height (m)</Label>
                          <Input
                            id="height"
                            type="number"
                            placeholder="0.1"
                            value={config.parameters.height || ''}
                            onChange={(e) => updateConfig('height', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="force" className="text-gray-300">Applied Force (N)</Label>
                        <Input
                          id="force"
                          type="number"
                          placeholder="-1000"
                          value={config.parameters.force || ''}
                          onChange={(e) => updateConfig('force', parseFloat(e.target.value))}
                          className="bg-slate-700/50 border-slate-600 text-white"
                        />
                      </div>

                      <div>
                        <Label htmlFor="elements" className="text-gray-300">Number of Elements</Label>
                        <Input
                          id="elements"
                          type="number"
                          placeholder="20"
                          value={config.parameters.elements || ''}
                          onChange={(e) => updateConfig('elements', parseInt(e.target.value))}
                          className="bg-slate-700/50 border-slate-600 text-white"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Results Panel */}
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Results</h3>
                    {isRunning ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                        <span className="ml-3 text-gray-300">Running simulation...</span>
                      </div>
                    ) : results ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-gray-400 text-sm">Max Displacement</div>
                            <div className="text-white font-semibold">
                              {results.max_displacement?.toExponential(2)} m
                            </div>
                          </div>
                          <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-gray-400 text-sm">Max Stress</div>
                            <div className="text-white font-semibold">
                              {(results.max_stress / 1e6)?.toFixed(2)} MPa
                            </div>
                          </div>
                        </div>
                        <div className="p-3 bg-slate-700/50 rounded-lg">
                          <div className="text-gray-400 text-sm">Safety Factor</div>
                          <div className="flex items-center gap-2">
                            <div className="text-white font-semibold">
                              {results.safety_factor?.toFixed(2)}
                            </div>
                            {results.safety_factor > 2 ? (
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-yellow-400" />
                            )}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-400">
                        Configure parameters and run simulation to see results
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* CFD Configuration */}
            <TabsContent value="cfd" className="mt-6">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-purple-600/20 rounded-lg">
                        <Waves className="w-6 h-6 text-purple-400" />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-white">Computational Fluid Dynamics</h3>
                        <p className="text-gray-400">Fluid flow simulation</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="cfd-length" className="text-gray-300">Length (m)</Label>
                          <Input
                            id="cfd-length"
                            type="number"
                            placeholder="1.0"
                            value={config.parameters.length || ''}
                            onChange={(e) => updateConfig('length', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                        <div>
                          <Label htmlFor="cfd-height" className="text-gray-300">Height (m)</Label>
                          <Input
                            id="cfd-height"
                            type="number"
                            placeholder="1.0"
                            value={config.parameters.height || ''}
                            onChange={(e) => updateConfig('height', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="inlet-velocity" className="text-gray-300">Inlet Velocity (m/s)</Label>
                        <Input
                          id="inlet-velocity"
                          type="number"
                          placeholder="1.0"
                          value={config.parameters.inlet_velocity || ''}
                          onChange={(e) => updateConfig('inlet_velocity', parseFloat(e.target.value))}
                          className="bg-slate-700/50 border-slate-600 text-white"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="density" className="text-gray-300">Density (kg/m³)</Label>
                          <Input
                            id="density"
                            type="number"
                            placeholder="1.0"
                            value={config.parameters.density || ''}
                            onChange={(e) => updateConfig('density', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                        <div>
                          <Label htmlFor="viscosity" className="text-gray-300">Viscosity (Pa·s)</Label>
                          <Input
                            id="viscosity"
                            type="number"
                            placeholder="0.001"
                            value={config.parameters.viscosity || ''}
                            onChange={(e) => updateConfig('viscosity', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* CFD Results */}
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Results</h3>
                    {isRunning ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
                        <span className="ml-3 text-gray-300">Running simulation...</span>
                      </div>
                    ) : results ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-gray-400 text-sm">Reynolds Number</div>
                            <div className="text-white font-semibold">
                              {results.reynolds_number}
                            </div>
                          </div>
                          <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-gray-400 text-sm">Max Velocity</div>
                            <div className="text-white font-semibold">
                              {results.max_velocity} m/s
                            </div>
                          </div>
                        </div>
                        <div className="p-3 bg-slate-700/50 rounded-lg">
                          <div className="text-gray-400 text-sm">Grid Size</div>
                          <div className="text-white font-semibold">
                            {results.grid_size}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-400">
                        Configure parameters and run simulation to see results
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Thermal Configuration */}
            <TabsContent value="thermal" className="mt-6">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-red-600/20 rounded-lg">
                        <Thermometer className="w-6 h-6 text-red-400" />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-white">Thermal Analysis</h3>
                        <p className="text-gray-400">Heat transfer simulation</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="heat-source" className="text-gray-300">Heat Source (W)</Label>
                        <Input
                          id="heat-source"
                          type="number"
                          placeholder="1000"
                          value={config.parameters.heat_source || ''}
                          onChange={(e) => updateConfig('heat_source', parseFloat(e.target.value))}
                          className="bg-slate-700/50 border-slate-600 text-white"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="temp-bottom" className="text-gray-300">Bottom Temp (°C)</Label>
                          <Input
                            id="temp-bottom"
                            type="number"
                            placeholder="100"
                            value={config.parameters.temp_bottom || ''}
                            onChange={(e) => updateConfig('temp_bottom', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                        <div>
                          <Label htmlFor="temp-top" className="text-gray-300">Top Temp (°C)</Label>
                          <Input
                            id="temp-top"
                            type="number"
                            placeholder="20"
                            value={config.parameters.temp_top || ''}
                            onChange={(e) => updateConfig('temp_top', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="temp-left" className="text-gray-300">Left Temp (°C)</Label>
                          <Input
                            id="temp-left"
                            type="number"
                            placeholder="60"
                            value={config.parameters.temp_left || ''}
                            onChange={(e) => updateConfig('temp_left', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                        <div>
                          <Label htmlFor="temp-right" className="text-gray-300">Right Temp (°C)</Label>
                          <Input
                            id="temp-right"
                            type="number"
                            placeholder="20"
                            value={config.parameters.temp_right || ''}
                            onChange={(e) => updateConfig('temp_right', parseFloat(e.target.value))}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Thermal Results */}
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Results</h3>
                    {isRunning ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-red-400" />
                        <span className="ml-3 text-gray-300">Running simulation...</span>
                      </div>
                    ) : results ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-gray-400 text-sm">Max Temperature</div>
                            <div className="text-white font-semibold">
                              {results.max_temperature?.toFixed(2)} °C
                            </div>
                          </div>
                          <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-gray-400 text-sm">Min Temperature</div>
                            <div className="text-white font-semibold">
                              {results.min_temperature?.toFixed(2)} °C
                            </div>
                          </div>
                        </div>
                        <div className="p-3 bg-slate-700/50 rounded-lg">
                          <div className="text-gray-400 text-sm">Max Heat Flux</div>
                          <div className="text-white font-semibold">
                            {(results.max_heat_flux / 1000)?.toFixed(2)} kW/m²
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-400">
                        Configure parameters and run simulation to see results
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Run Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 text-center"
        >
          <Button
            onClick={runSimulation}
            disabled={isRunning}
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold shadow-lg"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Running Simulation...
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                Run Simulation
              </>
            )}
          </Button>
        </motion.div>

        {/* Materials Info */}
        {Object.keys(materials).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-12"
          >
            <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <Wrench className="w-5 h-5" />
                  Available Materials
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {Object.entries(materials).map(([key, material]: [string, any]) => (
                    <div key={key} className="p-4 bg-slate-700/50 rounded-lg">
                      <h4 className="font-semibold text-white mb-2">{key}</h4>
                      <div className="space-y-1 text-sm text-gray-300">
                        <div>Density: {material.density} kg/m³</div>
                        <div>Young's: {(material.youngs / 1e9).toFixed(0)} GPa</div>
                        <div>Thermal: {material.thermal} W/m·K</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SimulationPage;