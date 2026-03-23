import { User, Sparkles } from "lucide-react";

interface ChatMessageProps {
  role: "user" | "assistant";
  text: string;
}

const ChatMessage = ({ role, text }: ChatMessageProps) => {
  const isUser = role === "user";

  return (
    <div
      className="opacity-0 animate-message-in"
      style={{ animationDelay: "0ms" }}
    >
      <div className={`flex gap-3 px-4 py-5 ${isUser ? "bg-chat-user" : "bg-chat-assistant"} rounded-2xl`}>
        <div
          className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
            isUser
              ? "bg-primary/10 text-primary"
              : "bg-accent text-accent-foreground"
          }`}
        >
          {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-1.5">
            {isUser ? "You" : "Assistant"}
          </p>
          <div className="text-[0.938rem] leading-relaxed text-foreground whitespace-pre-wrap overflow-wrap-anywhere">
            {text}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
