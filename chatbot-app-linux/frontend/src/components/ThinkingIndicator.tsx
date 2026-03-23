const ThinkingIndicator = () => (
  <div className="flex gap-3 px-4 py-5 bg-chat-assistant rounded-2xl opacity-0 animate-message-in">
    <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
      <div className="flex gap-1">
        <span className="h-1.5 w-1.5 rounded-full bg-current animate-pulse-dot" />
        <span className="h-1.5 w-1.5 rounded-full bg-current animate-pulse-dot" style={{ animationDelay: "0.2s" }} />
        <span className="h-1.5 w-1.5 rounded-full bg-current animate-pulse-dot" style={{ animationDelay: "0.4s" }} />
      </div>
    </div>
    <div className="min-w-0 flex-1">
      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-1.5">
        Assistant
      </p>
      <p className="text-[0.938rem] text-muted-foreground italic">Thinking…</p>
    </div>
  </div>
);

export default ThinkingIndicator;
