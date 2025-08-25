import { InputForm } from "./InputForm";
import { Button } from "@/components/ui/button";
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
  Info,
  ArrowRight
} from "lucide-react";
import { useState } from "react";
import { ProjectInfo } from "./ProjectInfo";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string
  ) => void;
  onCancel: () => void;
  onNewAnalysis: () => void;
  onLoadHistory?: () => void;
  isLoading: boolean;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  onNewAnalysis,
  onLoadHistory,
  isLoading,
}) => {
  const [showProjectInfo, setShowProjectInfo] = useState(false);

  if (showProjectInfo) {
    return (
      <div className="min-h-screen">
        <ProjectInfo />
        <div className="fixed top-4 left-4 z-50">
          <Button
            onClick={() => setShowProjectInfo(false)}
            variant="outline"
            className="bg-gray-800/50 backdrop-blur-sm border-gray-600 text-gray-300 hover:bg-gray-700/50 hover:text-white transition-all duration-300"
          >
            <ArrowRight className="w-4 h-4 mr-2 rotate-180" />
            Back to Chat
          </Button>
        </div>
      </div>
    );
  }

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
              <Button
                onClick={() => setShowProjectInfo(true)}
                variant="outline"
                className="bg-gray-800/50 backdrop-blur-sm border-gray-600 text-gray-300 hover:bg-gray-700/50 hover:text-white transition-all duration-300"
              >
                <Info className="w-4 h-4 mr-2" />
                About Project
              </Button>
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

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 hover:bg-gray-800/50 transition-all duration-300 group">
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-500/30 transition-colors">
                  <Users className="w-6 h-6 text-blue-400" />
                </div>
                <CardTitle className="text-blue-400">Domain Expert</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-300">
                  Analyzes business logic, industry standards, compliance requirements, and market positioning
                </CardDescription>
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
                <CardDescription className="text-gray-300">
                  Focuses on user experience, interface design, accessibility, and user journey optimization
                </CardDescription>
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
                <CardDescription className="text-gray-300">
                  Designs system architecture, scalability solutions, and implementation strategies
                </CardDescription>
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
                <CardDescription className="text-gray-300">
                  Evaluates revenue models, monetization strategies, and pricing optimization
                </CardDescription>
              </CardContent>
            </Card>
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
                  Describe your product idea, feature request, or business challenge in natural language
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-purple-400">2</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Multi-Agent Analysis</h3>
                <p className="text-gray-300">
                  Our AI specialists collaborate in real-time to analyze every aspect of your request
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-green-400">3</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Get Results</h3>
                <p className="text-gray-300">
                  Receive comprehensive analysis with actionable insights and recommendations
                </p>
              </div>
            </div>
          </div>

          {/* Input Section */}
          <div className="max-w-4xl mx-auto">
            <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl text-white mb-2">Ready to Get Started?</CardTitle>
                <CardDescription className="text-gray-300 text-lg">
                  Describe your product idea or business challenge below
                </CardDescription>
              </CardHeader>
              <CardContent>
                <InputForm
                  onSubmit={handleSubmit}
                  isLoading={isLoading}
                  onCancel={onCancel}
                  onNewAnalysis={onNewAnalysis}
                  hasHistory={false}
                />
              </CardContent>
            </Card>
          </div>

          {/* Load History Button */}
          {onLoadHistory && (
            <div className="text-center mt-8">
              <Button
                onClick={onLoadHistory}
                variant="outline"
                className="bg-gray-800/50 backdrop-blur-sm border-gray-600 text-gray-300 hover:bg-gray-700/50 hover:text-white transition-all duration-300"
              >
                <Lightbulb className="w-4 h-4 mr-2" />
                Load Previous Conversations
              </Button>
            </div>
          )}

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
