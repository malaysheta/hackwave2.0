import type React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Copy, CopyCheck, Bot, User, Sparkles, Brain } from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { useState, ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import { cn, extractFinalAnswerText } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  ActivityTimeline,
  ProcessedEvent,
} from "@/components/ActivityTimeline"; // Assuming ActivityTimeline is in the same dir or adjust path


// Define Message type locally
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
    is_followup?: boolean;
  };
}

// Markdown component props type from former ReportView
type MdComponentProps = {
  className?: string;
  children?: ReactNode;
  [key: string]: any;
};

// Markdown components (from former ReportView.tsx)
const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2 text-white", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2 text-white", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1 text-white", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7 text-gray-200", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Badge className="text-xs mx-0.5 bg-blue-900/20 text-blue-400 border-blue-500/30">
      <a
        className={cn("text-blue-400 hover:text-blue-300 text-xs", className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3 text-gray-200", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3 text-gray-200", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1 text-gray-200", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn(
        "border-l-4 border-blue-500/50 pl-4 italic my-3 text-sm text-gray-300 bg-blue-900/10 rounded-r-lg py-2",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn(
        "bg-gray-800 rounded px-1 py-0.5 font-mono text-xs text-green-400 border border-gray-700",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        "bg-gray-800 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3 text-green-400 border border-gray-700",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-gray-600 my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn(
        "border border-gray-600 px-3 py-2 text-left font-bold text-white bg-gray-800",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td
      className={cn("border border-gray-600 px-3 py-2 text-gray-200", className)}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents,
}) => {
  return (
    <div className="flex items-start gap-3 justify-end">
      <div className="flex flex-col items-end max-w-[85%] md:max-w-[80%]">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm text-gray-400">You</span>
        </div>
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl rounded-br-md break-words min-h-7 max-w-[100%] px-4 pt-3 pb-3 shadow-lg hover:shadow-xl transition-shadow duration-300">
          <ReactMarkdown components={mdComponents}>
            {typeof message.content === "string"
              ? message.content
              : JSON.stringify(message.content)}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: Message;
  historicalActivity: ProcessedEvent[] | undefined;
  liveActivity: ProcessedEvent[] | undefined;
  isLastMessage: boolean;
  isOverallLoading: boolean;
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  historicalActivity,
  liveActivity,
  isLastMessage,
  isOverallLoading,
  mdComponents,
  handleCopy,
  copiedMessageId,
}) => {
  // Determine which activity events to show and if it's for a live loading message
  const activityForThisBubble =
    isLastMessage && isOverallLoading ? liveActivity : historicalActivity;
  const isLiveActivityForThisBubble = isLastMessage && isOverallLoading;

  return (
    <div className="flex items-start gap-3">
      <div className="flex flex-col max-w-[85%] md:max-w-[80%]">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm text-gray-400">HackWave AI</span>
          <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30 text-xs">
            <Sparkles className="w-3 h-3 mr-1" />
            Multi-Agent
          </Badge>
          {message.metadata?.is_followup && (
            <Badge variant="secondary" className="bg-blue-900/20 text-blue-400 border-blue-500/30 text-xs">
              Follow-up
            </Badge>
          )}
        </div>
        
        <div className="relative break-words flex flex-col">
          {activityForThisBubble && activityForThisBubble.length > 0 && (
            <div className="mb-3 border-b border-gray-700/50 pb-3 text-xs bg-gray-800/30 rounded-lg p-3">
              <ActivityTimeline
                processedEvents={activityForThisBubble}
                isLoading={isLiveActivityForThisBubble}
              />
            </div>
          )}
          
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 text-gray-100 rounded-2xl rounded-bl-md w-full min-h-[56px] p-4 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <ReactMarkdown components={mdComponents}>
              {typeof message.content === "string"
                ? message.content
                : JSON.stringify(message.content)}
            </ReactMarkdown>
          </div>
          
          <Button
            variant="default"
            className={`cursor-pointer bg-gray-700/50 border-gray-600/50 text-gray-300 self-end mt-3 hover:bg-gray-600/50 hover:text-white transition-all duration-300 ${
              message.content.length > 0 ? "visible" : "hidden"
            }`}
            onClick={() =>
              handleCopy(
                typeof message.content === "string"
                  ? extractFinalAnswerText(message.content)
                  : JSON.stringify(message.content),
                message.id!
              )
            }
          >
            {copiedMessageId === message.id ? (
              <>
                <CopyCheck className="w-4 h-4 mr-2" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 mr-2" />
                Copy
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (inputValue: string, effort: string) => void;
  onCancel: () => void;
  onNewAnalysis: () => void;
  liveActivityEvents: ProcessedEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
  streamingMessage?: string;
  threadId?: string;
  onShowLangGraphMemory?: () => void;
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  onNewAnalysis,
  liveActivityEvents,
  historicalActivities,
  streamingMessage,
  threadId,
  onShowLangGraphMemory,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };
  
  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Header */}
      <div className="flex justify-between items-center p-4 border-b border-gray-700/50 bg-gray-800/30 backdrop-blur-sm shadow-lg sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-lg font-semibold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            HackWave AI Chat
          </h2>
          <Badge variant="secondary" className="bg-green-900/20 text-green-400 border-green-500/30">
            <Sparkles className="w-3 h-3 mr-1" />
            Live
          </Badge>
          <span className="text-xs text-gray-400 bg-gray-700/50 px-3 py-1.5 rounded-full border border-gray-600/50 backdrop-blur-sm">
            {messages.filter(m => m.type === 'ai').length} Analysis{messages.filter(m => m.type === 'ai').length !== 1 ? 'es' : ''} • {messages.filter(m => m.type === 'human').length} Query{messages.filter(m => m.type === 'human').length !== 1 ? 'ies' : ''}
          </span>
        </div>
        
        {/* LangGraph Memory Button */}
        {threadId && onShowLangGraphMemory && (
          <Button
            variant="outline"
            size="sm"
            onClick={onShowLangGraphMemory}
            className="bg-blue-900/20 border-blue-500/30 text-blue-400 hover:bg-blue-800/30 hover:text-blue-300 transition-all duration-300"
          >
            <Brain className="w-4 h-4 mr-2" />
            Memory
          </Button>
        )}
      </div>
      
      <ScrollArea className="flex-1 overflow-y-auto" ref={scrollAreaRef}>
        <div className="p-4 md:p-6 space-y-6">
          {messages.map((message, index) => {
            const isLast = index === messages.length - 1;
            return (
              <div key={message.id || `msg-${Date.now()}-${index}-${Math.random().toString(36).substr(2, 9)}`} className="space-y-3">
                {message.type === "human" ? (
                  <HumanMessageBubble
                    message={message}
                    mdComponents={mdComponents}
                  />
                ) : (
                  <AiMessageBubble
                    message={message}
                    historicalActivity={historicalActivities[message.id!]}
                    liveActivity={liveActivityEvents} // Pass global live events
                    isLastMessage={isLast}
                    isOverallLoading={isLoading} // Pass global loading state
                    mdComponents={mdComponents}
                    handleCopy={handleCopy}
                    copiedMessageId={copiedMessageId}
                  />
                )}
              </div>
            );
          })}
          
          {isLoading &&
            (messages.length === 0 ||
              messages[messages.length - 1].type === "human") && (
              <div className="flex items-start gap-3 mt-3">
                <div className="flex flex-col max-w-[85%] md:max-w-[80%]">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center animate-pulse">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm text-gray-400">HackWave AI</span>
                    <Badge variant="secondary" className="bg-yellow-900/20 text-yellow-400 border-yellow-500/30 text-xs animate-pulse">
                      <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                      Processing
                    </Badge>
                  </div>
                  
                  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 text-gray-100 rounded-2xl rounded-bl-md w-full min-h-[56px] p-4 shadow-lg">
                    {liveActivityEvents.length > 0 ? (
                      <div className="text-xs">
                        <ActivityTimeline
                          processedEvents={liveActivityEvents}
                          isLoading={true}
                        />
                      </div>
                    ) : (
                      <div className="flex items-center justify-start h-full">
                        <Loader2 className="h-5 w-5 animate-spin text-blue-400 mr-2" />
                        <span className="text-gray-300">Processing your request...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
            
          {streamingMessage && (
            <div className="flex items-start gap-3 mt-3">
              <div className="flex flex-col max-w-[85%] md:max-w-[80%]">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm text-gray-400">HackWave AI</span>
                  <Badge variant="secondary" className="bg-blue-900/20 text-blue-400 border-blue-500/30 text-xs">
                    <Sparkles className="w-3 h-3 mr-1" />
                    Streaming
                  </Badge>
                </div>
                
                <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 text-gray-100 rounded-2xl rounded-bl-md w-full min-h-[56px] p-4 shadow-lg">
                  <ReactMarkdown components={mdComponents}>
                    {streamingMessage}
                  </ReactMarkdown>
                  <Button
                    variant="default"
                    className={`cursor-pointer bg-gray-700/50 border-gray-600/50 text-gray-300 self-end mt-3 hover:bg-gray-600/50 hover:text-white transition-all duration-300 ${
                      streamingMessage.length > 0 ? "visible" : "hidden"
                    }`}
                    onClick={() => handleCopy(extractFinalAnswerText(streamingMessage), "streaming")}
                  >
                    {copiedMessageId === "streaming" ? (
                      <>
                        <CopyCheck className="w-4 h-4 mr-2" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      
      <div className="border-t border-gray-700/50 bg-gray-800/30 backdrop-blur-sm">
        <InputForm
          onSubmit={onSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          onNewAnalysis={onNewAnalysis}
          hasHistory={messages.length > 0}
        />
      </div>
    </div>
  );
}
