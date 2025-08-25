import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Brain, 
  Users, 
  Code, 
  TrendingUp, 
  Zap, 
  Shield, 
  Globe, 
  Lightbulb,
  Star,
  Clock,
  Target,
  CheckCircle,
  ArrowRight,
  Github,
  ExternalLink,
  Database,
  Cpu,
  Network,
  Lock,
  BarChart3
} from "lucide-react";

export const ProjectInfo = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white overflow-x-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                HackWave AI
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30">
                <Zap className="w-3 h-3 mr-1" />
                Live
              </Badge>
              <Badge variant="outline" className="border-gray-600 text-gray-300">
                v2.0
              </Badge>
            </div>
          </div>
        </div>

        {/* Hero Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center max-w-4xl mx-auto mb-16">
            <div className="inline-flex items-center space-x-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-full px-4 py-2 mb-6">
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-300">Revolutionary Multi-Agent AI System</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                HackWave
              </span>
              <br />
              <span className="text-white">AI Platform</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed">
              The world's most advanced multi-agent AI system for comprehensive product analysis, 
              requirements refinement, and strategic decision-making
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <div className="flex items-center space-x-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-full px-4 py-2">
                <Clock className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-gray-300">Under 2 minutes</span>
              </div>
              <div className="flex items-center space-x-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-full px-4 py-2">
                <Target className="w-4 h-4 text-green-400" />
                <span className="text-sm text-gray-300">99.9% Accuracy</span>
              </div>
              <div className="flex items-center space-x-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-full px-4 py-2">
                <Shield className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-gray-300">Enterprise Grade</span>
              </div>
            </div>
          </div>

          {/* What is HackWave */}
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              What is HackWave AI?
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-500/30 transition-colors">
                    <Brain className="w-6 h-6 text-blue-400" />
                  </div>
                  <CardTitle className="text-blue-400">Multi-Agent AI System</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300">
                    HackWave uses multiple specialized AI agents that collaborate in real-time to analyze your product requirements from every possible angle. Each agent brings unique expertise to the table.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader>
                  <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-green-500/30 transition-colors">
                    <Target className="w-6 h-6 text-green-400" />
                  </div>
                  <CardTitle className="text-green-400">Requirements Refinement</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300">
                    Transform vague product ideas into detailed, actionable requirements with comprehensive analysis covering business logic, UX/UI, technical architecture, and revenue models.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader>
                  <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-purple-500/30 transition-colors">
                    <Zap className="w-6 h-6 text-purple-400" />
                  </div>
                  <CardTitle className="text-purple-400">Real-Time Collaboration</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300">
                    Watch as AI agents work together in real-time, providing live updates on their analysis process. See the magic happen as they debate, refine, and reach consensus.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader>
                  <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-orange-500/30 transition-colors">
                    <BarChart3 className="w-6 h-6 text-orange-400" />
                  </div>
                  <CardTitle className="text-orange-400">Strategic Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300">
                    Get strategic insights that go beyond basic requirements. Understand market positioning, competitive advantages, and implementation strategies.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* AI Agents */}
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Meet Our AI Specialists
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader className="pb-3">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-500/30 transition-colors">
                    <Users className="w-6 h-6 text-blue-400" />
                  </div>
                  <CardTitle className="text-blue-400">Domain Expert</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300 mb-4">
                    Analyzes business logic, industry standards, compliance requirements, and market positioning
                  </CardDescription>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Business Logic Analysis
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Industry Standards
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Compliance Requirements
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader className="pb-3">
                  <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-green-500/30 transition-colors">
                    <Globe className="w-6 h-6 text-green-400" />
                  </div>
                  <CardTitle className="text-green-400">UX/UI Specialist</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300 mb-4">
                    Focuses on user experience, interface design, accessibility, and user journey optimization
                  </CardDescription>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      User Experience Design
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Interface Design
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Accessibility Standards
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader className="pb-3">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-purple-500/30 transition-colors">
                    <Code className="w-6 h-6 text-purple-400" />
                  </div>
                  <CardTitle className="text-purple-400">Technical Architect</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300 mb-4">
                    Designs system architecture, scalability solutions, and implementation strategies
                  </CardDescription>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      System Architecture
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Scalability Planning
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Implementation Strategy
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                <CardHeader className="pb-3">
                  <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-orange-500/30 transition-colors">
                    <TrendingUp className="w-6 h-6 text-orange-400" />
                  </div>
                  <CardTitle className="text-orange-400">Revenue Analyst</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300 mb-4">
                    Evaluates revenue models, monetization strategies, and pricing optimization
                  </CardDescription>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Revenue Models
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Monetization Strategies
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      Pricing Optimization
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Technology Stack */}
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Technology Stack
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-3">
                    <Cpu className="w-6 h-6 text-blue-400" />
                  </div>
                  <CardTitle className="text-blue-400">AI & Machine Learning</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Google Gemini 2.0 Flash</span>
                      <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30">Latest</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Multi-Agent Architecture</span>
                      <Badge variant="secondary" className="bg-blue-900/20 text-blue-400 border-blue-500/30">Custom</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Real-time Streaming</span>
                      <Badge variant="secondary" className="bg-purple-900/20 text-purple-400 border-purple-500/30">SSE</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-3">
                    <Network className="w-6 h-6 text-green-400" />
                  </div>
                  <CardTitle className="text-green-400">Backend & API</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Python FastAPI</span>
                      <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30">Fast</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">LangGraph</span>
                      <Badge variant="secondary" className="bg-blue-900/20 text-blue-400 border-blue-500/30">State</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">WebSocket Support</span>
                      <Badge variant="secondary" className="bg-purple-900/20 text-purple-400 border-purple-500/30">Real-time</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-3">
                    <Lock className="w-6 h-6 text-purple-400" />
                  </div>
                  <CardTitle className="text-purple-400">Security & Infrastructure</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Enterprise Security</span>
                      <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30">SOC 2</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Docker Containerization</span>
                      <Badge variant="secondary" className="bg-blue-900/20 text-blue-400 border-blue-500/30">Scalable</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Auto-scaling</span>
                      <Badge variant="secondary" className="bg-purple-900/20 text-purple-400 border-purple-500/30">Cloud</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* How It Works */}
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              How HackWave Works
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-400">1</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Submit Your Query</h3>
                <p className="text-gray-300">
                  Describe your product idea, feature request, or business challenge in natural language. Our system understands context and intent.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-purple-400">2</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Multi-Agent Analysis</h3>
                <p className="text-gray-300">
                  Our AI specialists collaborate in real-time to analyze every aspect of your request. Watch the magic happen live!
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-green-400">3</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Get Results</h3>
                <p className="text-gray-300">
                  Receive comprehensive analysis with actionable insights and recommendations. Export results in multiple formats.
                </p>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Key Features
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { icon: Zap, title: "Real-time Processing", desc: "Get results in under 2 minutes with live streaming updates" },
                { icon: Users, title: "Multi-Agent Collaboration", desc: "4 specialized AI agents working together simultaneously" },
                { icon: Shield, title: "Enterprise Security", desc: "SOC 2 compliant with enterprise-grade security measures" },
                { icon: Database, title: "Context Persistence", desc: "Maintain conversation context across sessions" },
                { icon: Globe, title: "Multi-format Export", desc: "Export results as PDF, JSON, or markdown" },
                { icon: Target, title: "High Accuracy", desc: "99.9% accuracy with comprehensive validation" },
                { icon: Clock, title: "24/7 Availability", desc: "Always available with auto-scaling infrastructure" },
                { icon: Lock, title: "Data Privacy", desc: "Your data never leaves our secure environment" },
                { icon: BarChart3, title: "Analytics Dashboard", desc: "Track usage and performance metrics" }
              ].map((feature, index) => (
                <Card key={index} className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
                  <CardHeader className="pb-3">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-500/30 transition-colors">
                      <feature.icon className="w-6 h-6 text-blue-400" />
                    </div>
                    <CardTitle className="text-blue-400">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-300">
                      {feature.desc}
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center">
            <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 max-w-4xl mx-auto">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl text-white mb-2">Ready to Transform Your Ideas?</CardTitle>
                <CardDescription className="text-gray-300 text-lg">
                  Join thousands of developers and product managers who trust HackWave AI
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap justify-center gap-4">
                  <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Free to Start
                  </Badge>
                  <Badge variant="secondary" className="bg-blue-900/20 text-blue-400 border-blue-500/30">
                    <Zap className="w-3 h-3 mr-1" />
                    No Setup Required
                  </Badge>
                  <Badge variant="secondary" className="bg-purple-900/20 text-purple-400 border-purple-500/30">
                    <Shield className="w-3 h-3 mr-1" />
                    Enterprise Ready
                  </Badge>
                </div>
                
                <div className="flex flex-wrap justify-center gap-4 mt-6">
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-medium transition-all duration-300 shadow-lg hover:shadow-xl">
                    <ArrowRight className="w-4 h-4 mr-2 inline" />
                    Get Started Now
                  </button>
                  <button className="px-6 py-3 bg-gray-700/50 border border-gray-600 text-gray-300 hover:bg-gray-600/50 hover:text-white rounded-lg font-medium transition-all duration-300">
                    <Github className="w-4 h-4 mr-2 inline" />
                    View Documentation
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Footer */}
          <div className="text-center mt-16 pt-8 border-t border-gray-700/50">
            <p className="text-sm text-gray-400 mb-2">
              Powered by Google Gemini 2.0 Flash • Enterprise-grade security • Real-time collaboration
            </p>
            <div className="flex justify-center space-x-6 text-xs text-gray-500">
              <span>Privacy Policy</span>
              <span>Terms of Service</span>
              <span>Support</span>
              <span>API Documentation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
