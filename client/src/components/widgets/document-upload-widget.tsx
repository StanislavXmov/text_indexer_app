import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { UploadIcon } from "lucide-react";
import { uploadDocument } from "./api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";

export function DocumentUploadWidget() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      setSelectedFile(null);
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Загрузка документа</CardTitle>
        <CardDescription>
          Загрузите PDF, чтобы проиндексировать его для вопросов.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Input
          type="file"
          accept=".pdf,application/pdf"
          onChange={(event) => {
            setSelectedFile(event.target.files?.[0] ?? null);
          }}
        />
      </CardContent>
      <CardFooter className="flex items-center justify-between gap-3">
        <p className="text-muted-foreground text-xs">
          {selectedFile ? `Файл: ${selectedFile.name}` : "Файл не выбран"}
        </p>
        <Button
          disabled={!selectedFile || uploadMutation.isPending}
          onClick={() => {
            if (!selectedFile) {
              return;
            }
            uploadMutation.mutate(selectedFile);
          }}
        >
          {uploadMutation.isPending ? (
            <>
              <Spinner />
              Загружаем...
            </>
          ) : (
            <>
              <UploadIcon />
              Загрузить
            </>
          )}
        </Button>
      </CardFooter>
      {uploadMutation.isError ? (
        <CardContent className="pt-0">
          <p className="text-destructive text-sm">
            Ошибка загрузки: {uploadMutation.error.message}
          </p>
        </CardContent>
      ) : null}
    </Card>
  );
}
