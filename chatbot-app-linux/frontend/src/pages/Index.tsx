import { useState, useRef, useEffect, useCallback } from "react";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import ThinkingIndicator from "@/components/ThinkingIndicator";
import EmptyState from "@/components/EmptyState";
import { Sparkles } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
}

const API_BASE_URL = (window as any).APP_CONFIG?.API_BASE_URL ?? "";

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking, scrollToBottom]);

  const handleSend = async (question: string) => {
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, conversation_id: conversationId }),
      });

      if (!response.ok) {
        let detail = "Request failed";
        try {
          const errorData = await response.json();
          detail = errorData.detail || detail;
        } catch {}
        throw new Error(detail);
      }

      const data = await response.json();
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", text: data.answer },
      ]);
    } catch (error: any) {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", text: `Error: ${error.message}` },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setIsThinking(false);
  };

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-border bg-card px-6 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Sparkles className="h-4 w-4" />
        </div>
        <div>
          <h1 className="text-base font-semibold leading-tight text-foreground">
            AI Assistant
          </h1>
          <p className="text-xs text-muted-foreground">Ask anything</p>
        </div>
      </header>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto chat-scroll">
        {messages.length === 0 && !isThinking ? (
          <EmptyState />
        ) : (
          <div className="mx-auto max-w-3xl space-y-3 px-4 py-6">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} role={msg.role} text={msg.text} />
            ))}
            {isThinking && <ThinkingIndicator />}
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} onNewChat={handleNewChat} disabled={isThinking} />
    </div>
  );
};

export default Index;
