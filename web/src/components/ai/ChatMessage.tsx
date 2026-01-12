import { Bot, User, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  isStreaming?: boolean;
}

export function ChatMessage({ role, content, timestamp, isStreaming }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = role === 'user';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (ts: number) => {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={clsx("flex gap-3 group", isUser && "flex-row-reverse")}>
      <div
        className={clsx(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
          isUser
            ? "bg-accent-gold/20 text-accent-gold"
            : "bg-accent-blue/20 text-accent-blue"
        )}
      >
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      <div className={clsx("flex flex-col max-w-[80%]", isUser && "items-end")}>
        <div
          className={clsx(
            "p-3 rounded-lg relative",
            isUser
              ? "bg-accent-gold/10 border border-accent-gold/30 text-white"
              : "bg-bg-card border border-bg-tertiary text-gray-200"
          )}
        >
          <div className="whitespace-pre-wrap break-words">
            {content}
            {isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-accent-blue animate-pulse" />
            )}
          </div>

          {!isUser && !isStreaming && content && (
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 p-1 text-gray-500 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
              title="Copy message"
            >
              {copied ? <Check size={14} /> : <Copy size={14} />}
            </button>
          )}
        </div>

        <span className="text-xs text-gray-500 mt-1 px-1">
          {formatTime(timestamp)}
        </span>
      </div>
    </div>
  );
}
