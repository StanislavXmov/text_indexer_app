import { useQuery } from "@tanstack/react-query";
import { FileTextIcon } from "lucide-react";
import { fetchDocuments, type DocumentItem } from "./api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

type DocumentListWidgetProps = {
  selectedDocumentId: string | null;
  onSelectDocument: (document: DocumentItem) => void;
};

function statusLabel(status: DocumentItem["status"]) {
  switch (status) {
    case "completed":
      return "Готов";
    case "failed":
      return "Ошибка";
    case "processing":
      return "Индексация";
    default:
      return "В очереди";
  }
}

function statusVariant(
  status: DocumentItem["status"]
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "completed":
      return "default";
    case "failed":
      return "destructive";
    case "processing":
      return "secondary";
    default:
      return "outline";
  }
}

export function DocumentListWidget(props: DocumentListWidgetProps) {
  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments,
    refetchInterval: (query) => {
      const documents = query.state.data ?? [];
      const hasActiveJobs = documents.some(
        (item) => item.status === "pending" || item.status === "processing"
      );
      return hasActiveJobs ? 2000 : false;
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Список документов</CardTitle>
        <CardDescription>
          Выберите документ со статусом &quot;Готов&quot; для вопросов.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {documentsQuery.isLoading ? (
          <div className="text-muted-foreground flex items-center gap-2 text-sm">
            <Spinner />
            Загружаем список документов...
          </div>
        ) : null}

        {documentsQuery.isError ? (
          <p className="text-destructive text-sm">
            Ошибка загрузки документов: {documentsQuery.error.message}
          </p>
        ) : null}

        {!documentsQuery.isLoading &&
        !documentsQuery.isError &&
        documentsQuery.data?.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            Пока нет документов. Загрузите первый PDF.
          </p>
        ) : null}

        {documentsQuery.data?.map((document) => {
          const isActive = props.selectedDocumentId === document.document_id;
          return (
            <button
              key={document.document_id}
              type="button"
              className={`border-border hover:bg-muted/60 flex w-full cursor-pointer items-center justify-between rounded-md border p-3 text-left transition ${
                isActive ? "ring-ring ring-2" : ""
              }`}
              onClick={() => {
                props.onSelectDocument(document);
              }}
            >
              <div className="min-w-0">
                <p className="flex items-center gap-2 truncate text-sm font-medium">
                  <FileTextIcon className="text-muted-foreground size-4 shrink-0" />
                  <span className="truncate">{document.original_filename}</span>
                </p>
                <p className="text-muted-foreground text-xs">{document.document_id}</p>
              </div>
              <Badge variant={statusVariant(document.status)}>{statusLabel(document.status)}</Badge>
            </button>
          );
        })}

        <div className="pt-1">
          <Button
            variant="outline"
            onClick={() => {
              void documentsQuery.refetch();
            }}
          >
            Обновить список
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
