import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Utility function to extract final answer text from AI message content
export function extractFinalAnswerText(messageContent: string): string {
  // If the content contains "Final Answer:" section, extract only that part
  if (messageContent.includes('**Final Answer:**')) {
    const finalAnswerMatch = messageContent.match(/\*\*Final Answer:\*\*\s*([\s\S]*?)(?=\n\n\*\*|$)/);
    if (finalAnswerMatch) {
      return finalAnswerMatch[1].trim();
    }
  }
  
  // If no specific final answer section, return the full content
  return messageContent;
}
