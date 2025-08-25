import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Input } from './ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Brain, 
  Search, 
  Trash2, 
  RefreshCw, 
  MessageSquare, 
  Clock,
  Hash,
  Database,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface LangGraphMemoryEntry {
  thread_id: string;
  user_query: string;
  response: string;
  context: Record<string, any>;
  timestamp: string;
  entry_id: string;
}

interface LangGraphMemoryStats {
  total_entries: number;
  thread_count: number;
  storage_type: string;
  created_at?: string;
  last_updated?: string;
}

interface LangGraphMemoryViewProps {
  threadId: string;
  onMemoryUpdate?: () => void;
}

const LangGraphMemoryView: React.FC<LangGraphMemoryViewProps> = ({ 
  threadId, 
  onMemoryUpdate 
}) => {
  const [memoryEntries, setMemoryEntries] = useState<LangGraphMemoryEntry[]>([]);
  const [memoryStats, setMemoryStats] = useState<LangGraphMemoryStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LangGraphMemoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('entries');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:2024/api';

  // Fetch memory entries
  const fetchMemoryEntries = async () => {
    if (!threadId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/langgraph-memory/${threadId}?limit=50`);
      const data = await response.json();
      
      if (response.ok) {
        setMemoryEntries(data.memory_entries || []);
        setMemoryStats(data.memory_stats || null);
        setSuccess(`Loaded ${data.memory_entries?.length || 0} memory entries`);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(`Failed to fetch memory: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      setError(`Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Search memory
  const searchMemory = async () => {
    if (!threadId || !searchQuery.trim()) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/langgraph-memory/search/${threadId}?query=${encodeURIComponent(searchQuery)}&limit=20`
      );
      const data = await response.json();
      
      if (response.ok) {
        setSearchResults(data.search_results || []);
        setSuccess(`Found ${data.search_results?.length || 0} results for "${searchQuery}"`);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(`Search failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      setError(`Search error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear memory
  const clearMemory = async () => {
    if (!threadId) return;
    
    if (!confirm('Are you sure you want to clear all memory for this thread? This action cannot be undone.')) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/langgraph-memory/${threadId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      
      if (response.ok && data.cleared) {
        setMemoryEntries([]);
        setSearchResults([]);
        setMemoryStats(null);
        setSuccess('Memory cleared successfully');
        setTimeout(() => setSuccess(null), 3000);
        onMemoryUpdate?.();
      } else {
        setError(`Failed to clear memory: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      setError(`Clear error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  // Truncate text
  const truncateText = (text: string, maxLength: number = 100) => {
    if (!text) return 'No content';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Check for duplicate content
  const isDuplicateContent = (entry: LangGraphMemoryEntry, index: number) => {
    if (index === 0) return false;
    
    const currentText = entry.response.toLowerCase();
    const previousText = memoryEntries[index - 1]?.response.toLowerCase();
    
    if (!previousText) return false;
    
    // Check for exact duplicates
    if (currentText === previousText) return true;
    
    // Check for significant overlap (more than 80% similar)
    const currentWords = new Set(currentText.split(' '));
    const previousWords = new Set(previousText.split(' '));
    
    const intersection = new Set([...currentWords].filter(x => previousWords.has(x)));
    const union = new Set([...currentWords, ...previousWords]);
    
    const similarity = intersection.size / union.size;
    return similarity > 0.8;
  };

  // Auto-refresh memory every 30 seconds
  useEffect(() => {
    fetchMemoryEntries();
    
    const interval = setInterval(() => {
      if (!isLoading) {
        fetchMemoryEntries();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, [threadId]);

  // Search with debounce
  useEffect(() => {
    if (searchQuery.trim()) {
      const timeoutId = setTimeout(searchMemory, 500);
      return () => clearTimeout(timeoutId);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const displayEntries = activeTab === 'search' ? searchResults : memoryEntries;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">LangGraph Memory</CardTitle>
            <Badge variant="secondary" className="text-xs">
              {memoryStats?.storage_type || 'MongoDB'}
            </Badge>
            {isLoading && (
              <Badge variant="outline" className="text-xs animate-pulse">
                <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                Loading
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchMemoryEntries}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={clearMemory}
              disabled={isLoading || memoryEntries.length === 0}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Status Messages */}
        {error && (
          <div className="flex items-center space-x-2 text-red-400 text-sm bg-red-900/20 p-2 rounded border border-red-500/30">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}
        
        {success && (
          <div className="flex items-center space-x-2 text-green-400 text-sm bg-green-900/20 p-2 rounded border border-green-500/30">
            <CheckCircle className="h-4 w-4" />
            <span>{success}</span>
          </div>
        )}
        
        {/* Memory Stats */}
        {memoryStats && (
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Database className="h-4 w-4" />
              <span>{memoryStats.total_entries} total entries</span>
            </div>
            <div className="flex items-center space-x-1">
              <Hash className="h-4 w-4" />
              <span>{memoryStats.thread_count} threads</span>
            </div>
            <div className="flex items-center space-x-1">
              <MessageSquare className="h-4 w-4" />
              <span>{memoryEntries.length} for this thread</span>
            </div>
            {memoryStats.last_updated && (
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span>Updated: {formatTimestamp(memoryStats.last_updated)}</span>
              </div>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="entries" className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4" />
              <span>Entries ({memoryEntries.length})</span>
            </TabsTrigger>
            <TabsTrigger value="search" className="flex items-center space-x-2">
              <Search className="h-4 w-4" />
              <span>Search ({searchResults.length})</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="entries" className="mt-4">
            {memoryEntries.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No memory entries found for this thread.</p>
                <p className="text-sm">Memory will be created as you interact with the system.</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={fetchMemoryEntries}
                  className="mt-4"
                  disabled={isLoading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            ) : (
              <ScrollArea className="h-96">
                <div className="space-y-4">
                                     {memoryEntries.map((entry, index) => (
                     <Card 
                       key={entry.entry_id} 
                       className={`border-l-4 hover:border-l-blue-400 transition-colors ${
                         isDuplicateContent(entry, index) 
                           ? 'border-l-orange-500 bg-orange-900/10' 
                           : 'border-l-blue-500'
                       }`}
                     >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-2">
                                                     <div className="flex items-center space-x-2">
                             <Badge variant="outline" className="text-xs">
                               Entry {memoryEntries.length - index}
                             </Badge>
                             {isDuplicateContent(entry, index) && (
                               <Badge variant="outline" className="text-xs bg-orange-900/20 text-orange-400 border-orange-500/30">
                                 Duplicate
                               </Badge>
                             )}
                             <span className="text-xs text-muted-foreground">
                               {formatTimestamp(entry.timestamp)}
                             </span>
                           </div>
                        </div>
                        
                        <div className="space-y-3">
                          <div>
                            <h4 className="font-medium text-sm mb-1 text-blue-400">User Query:</h4>
                            <p className="text-sm bg-muted p-2 rounded border border-gray-600/30">
                              {entry.user_query}
                            </p>
                          </div>
                          
                          <div>
                            <h4 className="font-medium text-sm mb-1 text-green-400">Response:</h4>
                            <p className="text-sm bg-muted p-2 rounded border border-gray-600/30">
                              {truncateText(entry.response, 200)}
                            </p>
                          </div>
                          
                          {entry.context && Object.keys(entry.context).length > 0 && (
                            <div>
                              <h4 className="font-medium text-sm mb-1 text-purple-400">Context:</h4>
                              <div className="text-xs bg-muted p-2 rounded border border-gray-600/30">
                                <div className="grid grid-cols-2 gap-2">
                                  {Object.entries(entry.context).map(([key, value]) => (
                                    <div key={key} className="break-words">
                                      <span className="font-medium text-purple-300">{key}:</span>
                                      <span className="ml-1 text-gray-300">
                                        {typeof value === 'object' 
                                          ? JSON.stringify(value).substring(0, 50) + '...'
                                          : String(value)
                                        }
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            )}
          </TabsContent>

          <TabsContent value="search" className="mt-4">
            <div className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Search in memory (e.g., 'payment', 'user', 'features')..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button onClick={searchMemory} disabled={isLoading || !searchQuery.trim()}>
                  <Search className="h-4 w-4" />
                </Button>
              </div>

              {searchResults.length === 0 && searchQuery.trim() && !isLoading && (
                <div className="text-center py-8 text-muted-foreground">
                  <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No results found for "{searchQuery}"</p>
                  <p className="text-sm">Try different keywords or check spelling</p>
                </div>
              )}

              {searchResults.length > 0 && (
                <ScrollArea className="h-80">
                  <div className="space-y-4">
                    {searchResults.map((entry, index) => (
                      <Card key={`search-${entry.entry_id}`} className="border-l-4 border-l-green-500 hover:border-l-green-400 transition-colors">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className="text-xs bg-green-900/20 text-green-400 border-green-500/30">
                                Search Result {index + 1}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {formatTimestamp(entry.timestamp)}
                              </span>
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div>
                              <h4 className="font-medium text-sm mb-1 text-blue-400">User Query:</h4>
                              <p className="text-sm bg-muted p-2 rounded border border-gray-600/30">
                                {entry.user_query}
                              </p>
                            </div>
                            
                            <div>
                              <h4 className="font-medium text-sm mb-1 text-green-400">Response:</h4>
                              <p className="text-sm bg-muted p-2 rounded border border-gray-600/30">
                                {truncateText(entry.response, 150)}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default LangGraphMemoryView;
