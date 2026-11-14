
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useRef, useState } from "react";
import { askAcademicAssistant } from "../../services/academicAssistant";
import type { ChatMessage } from "../../types/academicAssistant";
import "./AcademicAssistant.css";

const suggestedQuestions = [
  "Show students with attendance below 75% in Grade 6 A.",
  "Which students have both marks below 40% and attendance below 75%?",
  "Show the subject performance for 2025-2026.",
  "Show students with declining performance in Grade 6 A.",
  "Show the academic performance of STU0001.",
];

const AcademicAssistant = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendQuestion = async (questionText?: string) => {
    const text = (questionText ?? question).trim();

    if (!text || loading) return;

    const userMessage: ChatMessage = {
      id: `${crypto.randomUUID()}-user`,
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await askAcademicAssistant({
        question: text,
      });

      const assistantMessage: ChatMessage = {
        id: `${crypto.randomUUID()}-assistant`,
        role: "assistant",
        content: response.answer,
        data_used: response.data_used,
        records_found: response.records_found,
        timestamp: new Date(),
      };

      setMessages((previous) => [...previous, assistantMessage]);
    } catch (err: unknown) {
      let errorMessage =
        "Unable to get a response. Please try again.";

      if (
        typeof err === "object" &&
        err !== null &&
        "response" in err
      ) {
        const response = (
          err as {
            response?: {
              data?: {
                detail?: string;
                message?: string;
              };
              status?: number;
            };
          }
        ).response;

        const detail = response?.data?.detail;

        if (typeof detail === "string" && detail.trim()) {
          errorMessage = detail;
        } else if (response?.status === 502) {
          errorMessage =
            "The AI service is temporarily unavailable. Please try again later.";
        } else if (response?.status === 503) {
          errorMessage =
            "The AI service is not configured or currently unavailable.";
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void sendQuestion();
  };

  const formatTime = (date: Date) =>
    date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <div className="academic-assistant-page">
      <div className="assistant-header">
        <div>
          <h1>AI Academic Assistant</h1>
          <p>
            Ask questions about student performance, attendance,
            subjects, and academic trends.
          </p>
        </div>

        <div className="assistant-status">
          <span className="status-dot" />
          Academic Data Assistant
        </div>
      </div>

      <div className="assistant-chat-container">
        {messages.length === 0 ? (
          <div className="assistant-welcome">
            <div className="assistant-welcome-icon">AI</div>

            <h2>How can I help you today?</h2>

            <p>
              Ask questions about your school's academic data.
              I'll retrieve relevant records and explain the results.
            </p>

            <div className="suggested-questions">
              <h3>Suggested questions</h3>

              <div className="suggestion-list">
                {suggestedQuestions.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className="suggestion-button"
                    onClick={() => void sendQuestion(item)}
                    disabled={loading}
                  >
                    <span>{item}</span>
                    <span className="suggestion-arrow">→</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="assistant-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-row ${message.role}`}
              >
                <div className="message-avatar">
                  {message.role === "user" ? "You" : "AI"}
                </div>

                <div className="message-content">
                  <div className="message-meta">
                    <strong>
                      {message.role === "user"
                        ? "You"
                        : "Academic Assistant"}
                    </strong>
                    <span>{formatTime(message.timestamp)}</span>
                  </div>

                    <div className="message-bubble">
                        {message.role === "assistant" ? (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                            </ReactMarkdown>
                        ) : (
                            message.content
                        )}
                        </div>

                  {message.role === "assistant" &&
                    message.data_used &&
                    message.data_used.length > 0 && (
                      <div className="message-data">
                        <strong>Data used</strong>
                        <div className="data-tags">
                          {message.data_used.map((item, index) => (
                            <span key={`${item}-${index}`}>
                              {item}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                  {message.role === "assistant" &&
                    message.records_found !== undefined && (
                      <div className="records-count">
                        {message.records_found} records found
                      </div>
                    )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row assistant">
                <div className="message-avatar">AI</div>
                <div className="message-content">
                  <div className="message-meta">
                    <strong>Academic Assistant</strong>
                  </div>
                  <div className="message-bubble typing-indicator">
                    <span />
                    <span />
                    <span />
                    <small>Analyzing academic data...</small>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {error && (
          <div className="assistant-error" role="alert">
            <strong>Unable to complete your request</strong>
            <p>{error}</p>
          </div>
        )}

        <form className="assistant-input-area" onSubmit={handleSubmit}>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about student performance, attendance, or academic trends..."
            rows={2}
            disabled={loading}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                void sendQuestion();
              }
            }}
          />

          <div className="assistant-input-footer">
            <span>Press Enter to send · Shift + Enter for a new line</span>

            <button
              type="submit"
              disabled={!question.trim() || loading}
            >
              {loading ? "Thinking..." : "Send"}
              <span>↑</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AcademicAssistant;
