import { useState } from "react";
import { Button } from "@/components/ui/button";
import { SquarePen, Send, StopCircle, Users, Sparkles, Zap } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, effort: string) => void;
  onCancel: () => void;
  onNewAnalysis: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  onNewAnalysis,
  isLoading,
  hasHistory,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");
  const [queryType, setQueryType] = useState("general");

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, queryType);
    setInternalInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit with Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  const getQueryTypeColor = (type: string) => {
    switch (type) {
      case "domain":
        return "bg-blue-900/20 text-blue-400 border-blue-500/30";
      case "ux_ui":
        return "bg-green-900/20 text-green-400 border-green-500/30";
      case "technical":
        return "bg-purple-900/20 text-purple-400 border-purple-500/30";
      case "revenue":
        return "bg-orange-900/20 text-orange-400 border-orange-500/30";
      default:
        return "bg-gray-900/20 text-gray-400 border-gray-500/30";
    }
  };

  const getQueryTypeIcon = (type: string) => {
    switch (type) {
      case "domain":
        return "🏢";
      case "ux_ui":
        return "🎨";
      case "technical":
        return "⚙️";
      case "revenue":
        return "💰";
      default:
        return "🤖";
    }
  };

  return (
    <form
      onSubmit={handleInternalSubmit}
      className="flex flex-col gap-3 p-4"
    >
      {/* Input Container */}
      <div className="relative">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-3 shadow-lg hover:shadow-xl transition-shadow duration-300">
          <Textarea
            value={internalInputValue}
            onChange={(e) => setInternalInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your product requirements or ask about specific aspects like user interface, technical architecture, business logic, or revenue models..."
            className="w-full text-gray-100 placeholder-gray-500 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none bg-transparent
                      md:text-base min-h-[40px] max-h-[120px] text-base"
            rows={1}
          />
          
          {/* Submit Button */}
          <div className="absolute bottom-3 right-3">
            {isLoading ? (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="text-red-400 hover:text-red-300 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200 shadow-lg"
                onClick={onCancel}
              >
                <StopCircle className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                type="submit"
                variant="ghost"
                className={`${
                  isSubmitDisabled
                    ? "text-gray-500 bg-gray-700/50"
                    : "text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl"
                } p-2 cursor-pointer rounded-full transition-all duration-200 text-sm font-medium`}
                disabled={isSubmitDisabled}
              >
                {isSubmitDisabled ? (
                  <Zap className="h-4 w-4" />
                ) : (
                  <>
                    <Sparkles className="h-3 w-3 mr-1" />
                    Analyze
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Controls Row */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        {/* Focus Selector */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg px-3 py-1.5">
            <Users className="h-3 w-3 text-gray-400" />
            <span className="text-xs text-gray-300 font-medium">Focus:</span>
            <Select value={queryType} onValueChange={setQueryType}>
              <SelectTrigger className="w-[140px] bg-transparent border-none cursor-pointer text-gray-200 text-xs">
                <SelectValue placeholder="Select focus" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700 text-gray-200">
                <SelectItem
                  value="general"
                  className="hover:bg-gray-700 focus:bg-gray-700 cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>🤖</span>
                    General Analysis
                  </span>
                </SelectItem>
                <SelectItem
                  value="domain"
                  className="hover:bg-gray-700 focus:bg-gray-700 cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>🏢</span>
                    Domain Expert
                  </span>
                </SelectItem>
                <SelectItem
                  value="ux_ui"
                  className="hover:bg-gray-700 focus:bg-gray-700 cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>🎨</span>
                    UX/UI Specialist
                  </span>
                </SelectItem>
                <SelectItem
                  value="technical"
                  className="hover:bg-gray-700 focus:bg-gray-700 cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>⚙️</span>
                    Technical Architect
                  </span>
                </SelectItem>
                <SelectItem
                  value="revenue"
                  className="hover:bg-gray-700 focus:bg-gray-700 cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <span>💰</span>
                    Revenue Analyst
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Current Focus Badge */}
          <Badge variant="secondary" className={`${getQueryTypeColor(queryType)} text-xs`}>
            <span className="mr-1">{getQueryTypeIcon(queryType)}</span>
            {queryType === "general" && "General"}
            {queryType === "domain" && "Domain"}
            {queryType === "ux_ui" && "UX/UI"}
            {queryType === "technical" && "Technical"}
            {queryType === "revenue" && "Revenue"}
          </Badge>
        </div>

        {/* New Analysis Button */}
        {hasHistory && (
          <Button
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 text-gray-300 hover:text-white hover:bg-gray-700/50 cursor-pointer rounded-lg px-3 py-1.5 transition-all duration-300 shadow-lg hover:shadow-xl text-xs"
            variant="outline"
            onClick={onNewAnalysis}
          >
            <SquarePen size={14} className="mr-1" />
            New Analysis
          </Button>
        )}
      </div>

      {/* Keyboard Shortcut Hint */}
      <div className="text-center">
        <p className="text-xs text-gray-500">
          💡 Press <kbd className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-xs">Ctrl+Enter</kbd> to submit quickly
        </p>
      </div>
    </form>
  );
};
