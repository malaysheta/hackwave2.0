import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Download, 
  FileText, 
  Settings, 
  CheckCircle,
  Clock,
  User,
  Bot,
  Sparkles
} from "lucide-react";
import { useState } from "react";

interface Message {
  type: "human" | "ai";
  content: string;
  id: string;
  metadata?: {
    processing_time?: number;
    query_type?: string;
    debate_category?: string;
    domain_analysis?: string;
    ux_analysis?: string;
    technical_analysis?: string;
    revenue_analysis?: string;
    moderator_aggregation?: string;
    debate_resolution?: string;
  };
}

interface PDFDownloadProps {
  messages: Message[];
  onDownload: (format: 'pdf' | 'markdown' | 'json') => void;
  isLoading?: boolean;
}

export const PDFDownload: React.FC<PDFDownloadProps> = ({ 
  messages, 
  onDownload, 
  isLoading = false
}) => {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'markdown' | 'json'>('pdf');

  const formatOptions = [
    {
      value: 'pdf' as const,
      label: 'PDF Document',
      description: 'Professional formatted document with styling',
      icon: FileText,
      color: 'text-red-400',
      bgColor: 'bg-red-500/20',
      borderColor: 'border-red-500/30'
    },
    {
      value: 'markdown' as const,
      label: 'Markdown',
      description: 'Plain text format with markdown syntax',
      icon: FileText,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/30'
    },
    {
      value: 'json' as const,
      label: 'JSON Data',
      description: 'Structured data format for developers',
      icon: FileText,
      color: 'text-green-400',
      bgColor: 'bg-green-500/20',
      borderColor: 'border-green-500/30'
    }
  ];

  const getConversationSummary = () => {
    const humanMessages = messages.filter(m => m.type === 'human');
    const aiMessages = messages.filter(m => m.type === 'ai');
    
    return {
      totalMessages: messages.length,
      humanMessages: humanMessages.length,
      aiMessages: aiMessages.length,
      lastMessageTime: new Date().toLocaleString(),
      averageResponseTime: aiMessages.length > 0 ? '2 minutes' : 'N/A'
    };
  };

  const summary = getConversationSummary();

  return (
    <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Download className="w-5 h-5 text-white" />
          </div>
          <div>
            <CardTitle className="text-white">Export Conversation</CardTitle>
            <CardDescription className="text-gray-300">
              Download your analysis results in multiple formats
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Conversation Summary */}
        <div className="bg-gray-700/30 rounded-lg p-4 border border-gray-600/50">
          <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            Conversation Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-bold text-white">{summary.totalMessages}</div>
              <div className="text-xs text-gray-400">Total Messages</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-400">{summary.humanMessages}</div>
              <div className="text-xs text-gray-400">Your Queries</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-400">{summary.aiMessages}</div>
              <div className="text-xs text-gray-400">AI Responses</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-400">{summary.averageResponseTime}</div>
              <div className="text-xs text-gray-400">Avg Response</div>
            </div>
          </div>
        </div>

        {/* Format Selection */}
        <div>
          <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
            <Settings className="w-4 h-4 text-gray-400" />
            Select Export Format
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {formatOptions.map((option) => (
              <div
                key={option.value}
                className={`relative cursor-pointer rounded-lg border-2 p-4 transition-all duration-200 ${
                  selectedFormat === option.value
                    ? `${option.borderColor} ${option.bgColor}`
                    : 'border-gray-600 bg-gray-700/30 hover:bg-gray-700/50'
                }`}
                onClick={() => setSelectedFormat(option.value)}
              >
                {selectedFormat === option.value && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-white" />
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 ${option.bgColor} rounded-lg flex items-center justify-center`}>
                    <option.icon className={`w-4 h-4 ${option.color}`} />
                  </div>
                  <div>
                    <div className={`font-medium ${selectedFormat === option.value ? 'text-white' : 'text-gray-300'}`}>
                      {option.label}
                    </div>
                    <div className="text-xs text-gray-400">
                      {option.description}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Preview */}
        <div>
          <h3 className="text-sm font-semibold text-gray-200 mb-3">Preview</h3>
          <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-600/50 max-h-40 overflow-y-auto">
            <div className="space-y-2">
              {messages.slice(-3).map((message, index) => (
                <div key={index} className="flex items-start gap-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'human' 
                      ? 'bg-blue-500/20' 
                      : 'bg-green-500/20'
                  }`}>
                    {message.type === 'human' ? (
                      <User className="w-3 h-3 text-blue-400" />
                    ) : (
                      <Bot className="w-3 h-3 text-green-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-gray-400 mb-1">
                      {message.type === 'human' ? 'You' : 'HackWave AI'}
                    </div>
                    <div className="text-sm text-gray-300 truncate">
                      {message.content.substring(0, 100)}
                      {message.content.length > 100 && '...'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Download Button */}
        <div className="flex justify-center">
    <Button
            onClick={() => onDownload(selectedFormat)}
            disabled={isLoading || messages.length === 0}
            className={`w-full max-w-md ${
              isLoading
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
            } transition-all duration-300`}
          >
            {isLoading ? (
              <>
                <Clock className="w-4 h-4 mr-2 animate-spin" />
                Generating...
        </>
      ) : (
        <>
                <Download className="w-4 h-4 mr-2" />
                Download {selectedFormat.toUpperCase()}
        </>
      )}
    </Button>
        </div>

        {/* Format Info */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            {selectedFormat === 'pdf' && 'PDF includes all messages with professional formatting and styling'}
            {selectedFormat === 'markdown' && 'Markdown format is perfect for documentation and sharing'}
            {selectedFormat === 'json' && 'JSON format contains structured data for developers and APIs'}
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
