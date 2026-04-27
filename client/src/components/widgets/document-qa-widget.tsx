import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { askDocumentQuestion, fetchAskJob, type DocumentItem } from "./api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Textarea } from "@/components/ui/textarea";

type DocumentQaWidgetProps = {
  selectedDocument: DocumentItem | null;
};

function parseAnswerSections(rawAnswer: string) {
  const sourcesMatch = rawAnswer.match(/\*\*Sources:\*\*([\s\S]*)$/i);
  const answerText = sourcesMatch
    ? rawAnswer.slice(0, sourcesMatch.index).trim()
    : rawAnswer.trim();

  const sources = sourcesMatch
    ? sourcesMatch[1]
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => /^\d+\./.test(line))
    : [];

  return { answerText, sources };
}

function renderInlineBold(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      const content = part.slice(2, -2).trim();
      return <strong key={`${content}-${index}`}>{content}</strong>;
    }
    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

export function DocumentQaWidget({ selectedDocument }: DocumentQaWidgetProps) {
  const [question, setQuestion] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);

  const askMutation = useMutation({
    mutationFn: (input: { documentId: string; question: string }) =>
      askDocumentQuestion({
        documentId: input.documentId,
        question: input.question,
      }),
    onSuccess: (job) => {
      setJobId(job.job_id);
    },
  });

  const askJobQuery = useQuery({
    queryKey: ["ask-job", jobId],
    queryFn: () => fetchAskJob(jobId as string),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || status === "pending" || status === "processing") {
        return 2000;
      }
      return false;
    },
  });

  const canAsk =
    selectedDocument?.status === "completed" &&
    question.trim().length > 0 &&
    !askMutation.isPending;
  const parsedAnswer = parseAnswerSections(askJobQuery.data?.answer ?? "");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Вопрос по документу</CardTitle>
        <CardDescription>
          {selectedDocument
            ? `Документ: ${selectedDocument.original_filename}`
            : "Сначала выберите документ в списке слева"}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Textarea
          placeholder="Например: О чем документ и какие ключевые выводы?"
          value={question}
          onChange={(event) => {
            setQuestion(event.target.value);
          }}
          disabled={!selectedDocument || selectedDocument.status !== "completed"}
        />
        <Button
          disabled={!canAsk}
          onClick={() => {
            if (!selectedDocument || !question.trim()) {
              return;
            }

            askMutation.mutate({
              documentId: selectedDocument.document_id,
              question: question.trim(),
            });
          }}
        >
          {askMutation.isPending ? (
            <>
              <Spinner />
              Отправляем вопрос...
            </>
          ) : (
            "Задать вопрос"
          )}
        </Button>

        {selectedDocument && selectedDocument.status !== "completed" ? (
          <p className="text-muted-foreground text-sm">
            Документ пока не готов. Дождитесь завершения индексации.
          </p>
        ) : null}

        {askMutation.isError ? (
          <p className="text-destructive text-sm">
            Ошибка при отправке вопроса: {askMutation.error.message}
          </p>
        ) : null}

        {jobId ? (
          <div className="border-border space-y-2 rounded-md border p-3">
            <p className="text-muted-foreground text-xs">job_id: {jobId}</p>
            {!askJobQuery.data ||
            askJobQuery.data.status === "pending" ||
            askJobQuery.data.status === "processing" ? (
              <div className="flex items-center gap-2 text-sm">
                <Spinner />
                Готовим ответ...
              </div>
            ) : null}

            {askJobQuery.data?.status === "completed" ? (
              <div className="space-y-3 text-sm">
                <div className="space-y-1">
                  <p className="font-semibold">Question:</p>
                  <p className="whitespace-pre-wrap">
                    {askJobQuery.data.question || "Вопрос не найден"}
                  </p>
                </div>

                <div className="space-y-1">
                  <p className="font-semibold">Answer:</p>
                  <p className="whitespace-pre-wrap">
                    {renderInlineBold(parsedAnswer.answerText || "Ответ пустой")}
                  </p>
                </div>

                {parsedAnswer.sources.length > 0 ? (
                  <div className="space-y-1">
                    <p className="font-semibold">Sources:</p>
                    <ul className="list-decimal space-y-1 pl-5">
                      {parsedAnswer.sources.map((source) => (
                        <li key={source} className="break-all">
                          {renderInlineBold(source.replace(/^\d+\.\s*/, ""))}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            ) : null}

            {askJobQuery.data?.status === "failed" ? (
              <p className="text-destructive text-sm">
                Ошибка: {askJobQuery.data.error_message ?? "Неизвестная ошибка"}
              </p>
            ) : null}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
