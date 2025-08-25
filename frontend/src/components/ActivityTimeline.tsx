import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Loader2,
  Activity,
  Info,
  Search,
  TextSearch,
  Brain,
  Pen,
  ChevronDown,
  ChevronUp,
  DollarSign,
  Sparkles,
  CheckCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";

export interface ProcessedEvent {
  title: string;
  data: any;
}

interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[];
  isLoading: boolean;
}

export function ActivityTimeline({
  processedEvents,
  isLoading,
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] =
    useState<boolean>(false);
    
  const getEventIcon = (title: string, index: number) => {
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />;
    }
    if (title.toLowerCase().includes("query classification")) {
      return <Search className="h-4 w-4 text-blue-400" />;
    } else if (title.toLowerCase().includes("domain expert")) {
      return <Brain className="h-4 w-4 text-blue-400" />;
    } else if (title.toLowerCase().includes("ux/ui")) {
      return <Activity className="h-4 w-4 text-green-400" />;
    } else if (title.toLowerCase().includes("technical")) {
      return <TextSearch className="h-4 w-4 text-purple-400" />;
    } else if (title.toLowerCase().includes("revenue")) {
      return <DollarSign className="h-4 w-4 text-orange-400" />;
    } else if (title.toLowerCase().includes("moderator")) {
      return <Sparkles className="h-4 w-4 text-pink-400" />;
    } else if (title.toLowerCase().includes("final answer")) {
      return <CheckCircle className="h-4 w-4 text-green-400" />;
    }
    return <Activity className="h-4 w-4 text-gray-400" />;
  };

  const getEventColor = (title: string) => {
    if (title.toLowerCase().includes("query classification")) {
      return "border-blue-500/30 bg-blue-900/20";
    } else if (title.toLowerCase().includes("domain expert")) {
      return "border-blue-500/30 bg-blue-900/20";
    } else if (title.toLowerCase().includes("ux/ui")) {
      return "border-green-500/30 bg-green-900/20";
    } else if (title.toLowerCase().includes("technical")) {
      return "border-purple-500/30 bg-purple-900/20";
    } else if (title.toLowerCase().includes("revenue")) {
      return "border-orange-500/30 bg-orange-900/20";
    } else if (title.toLowerCase().includes("moderator")) {
      return "border-pink-500/30 bg-pink-900/20";
    } else if (title.toLowerCase().includes("final answer")) {
      return "border-green-500/30 bg-green-900/20";
    }
    return "border-gray-500/30 bg-gray-900/20";
  };

  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true);
    }
  }, [isLoading, processedEvents]);

  return (
    <Card className="border border-gray-700/50 rounded-lg bg-gray-800/30 backdrop-blur-sm max-h-96 shadow-lg">
      <CardHeader className="pb-3">
        <CardDescription className="flex items-center justify-between">
          <div
            className="flex items-center justify-start text-sm w-full cursor-pointer gap-2 text-gray-200 hover:text-white transition-colors"
            onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
          >
            <Sparkles className="h-4 w-4 text-blue-400" />
            Multi-Agent Analysis
            {isTimelineCollapsed ? (
              <ChevronDown className="h-4 w-4 ml-auto text-gray-400" />
            ) : (
              <ChevronUp className="h-4 w-4 ml-auto text-gray-400" />
            )}
          </div>
        </CardDescription>
      </CardHeader>
      {!isTimelineCollapsed && (
        <ScrollArea className="max-h-96 overflow-y-auto">
          <CardContent className="pt-0">
            {isLoading && processedEvents.length === 0 && (
              <div className="relative pl-8 pb-4">
                <div className="absolute left-3 top-3.5 h-full w-0.5 bg-gradient-to-b from-blue-500 to-purple-500" />
                <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center ring-4 ring-gray-800 shadow-lg">
                  <Loader2 className="h-3 w-3 text-white animate-spin" />
                </div>
                <div>
                  <p className="text-sm text-gray-200 font-medium">
                    Initializing analysis...
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Preparing multi-agent system
                  </p>
                </div>
              </div>
            )}
            {processedEvents.length > 0 ? (
              <div className="space-y-0">
                {processedEvents.map((eventItem, index) => (
                  <div key={index} className="relative pl-8 pb-4">
                    {index < processedEvents.length - 1 ||
                    (isLoading && index === processedEvents.length - 1) ? (
                      <div className="absolute left-3 top-3.5 h-full w-0.5 bg-gradient-to-b from-gray-600 to-gray-700" />
                    ) : null}
                    <div className="absolute left-0.5 top-2 h-6 w-6 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center ring-4 ring-gray-800 shadow-lg">
                      {getEventIcon(eventItem.title, index)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm text-gray-200 font-medium">
                          {eventItem.title}
                        </p>
                        <Badge variant="secondary" className={`text-xs ${getEventColor(eventItem.title)}`}>
                          {index + 1}/{processedEvents.length}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-400 leading-relaxed">
                        {typeof eventItem.data === "string"
                          ? eventItem.data
                          : Array.isArray(eventItem.data)
                          ? (eventItem.data as string[]).join(", ")
                          : JSON.stringify(eventItem.data)}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && processedEvents.length > 0 && (
                  <div className="relative pl-8 pb-4">
                    <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center ring-4 ring-gray-800 shadow-lg animate-pulse">
                      <Loader2 className="h-3 w-3 text-white animate-spin" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-200 font-medium">
                        Processing next step...
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        AI agents are collaborating
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : !isLoading ? ( // Only show "No activity" if not loading and no events
              <div className="flex flex-col items-center justify-center h-full text-gray-500 pt-10">
                <Info className="h-6 w-6 mb-3 text-gray-400" />
                <p className="text-sm text-gray-400">No activity to display.</p>
                <p className="text-xs text-gray-500 mt-1">
                  Timeline will update during processing.
                </p>
              </div>
            ) : null}
          </CardContent>
        </ScrollArea>
      )}
    </Card>
  );
}
