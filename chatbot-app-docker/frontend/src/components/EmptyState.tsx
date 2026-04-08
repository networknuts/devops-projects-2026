import { Sparkles } from "lucide-react";

const EmptyState = () => (
  <div className="flex flex-1 flex-col items-center justify-center px-4 opacity-0 animate-message-in">
    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent text-accent-foreground mb-6">
      <Sparkles className="h-7 w-7" />
    </div>
    <h2 className="text-xl font-semibold text-foreground mb-2">
      What can I help you with?
    </h2>
    <p className="max-w-sm text-center text-sm text-muted-foreground leading-relaxed">
      Ask a question and get an AI-generated response. Your conversation will appear here.
    </p>
  </div>
);

export default EmptyState;
