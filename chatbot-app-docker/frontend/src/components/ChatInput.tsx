import { useState, useRef, useEffect } from "react";
import { Send, Plus } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  onNewChat: () => void;
  disabled?: boolean;
}

const ChatInput = ({ onSend, onNewChat, disabled }: ChatInputProps) => {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
    }
  }, [value]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-border bg-card p-4">
      <div className="mx-auto max-w-3xl">
        <div className="relative flex items-end gap-2 rounded-2xl border border-border bg-background p-2 shadow-sm transition-shadow focus-within:shadow-md focus-within:border-primary/30">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything…"
            disabled={disabled}
            rows={1}
            className="flex-1 resize-none bg-transparent px-2 py-2 text-[0.938rem] leading-relaxed text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-50"
          />
          <div className="flex gap-1.5 pb-1">
            <button
              type="button"
              onClick={onNewChat}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground active:scale-95"
              title="New chat"
            >
              <Plus className="h-4 w-4" />
            </button>
            <button
              type="submit"
              disabled={disabled || !value.trim()}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary/90 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </form>
  );
};

export default ChatInput;
