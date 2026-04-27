import { useState } from "react";
import { DocumentListWidget } from "./document-list-widget";
import { DocumentQaWidget } from "./document-qa-widget";
import { DocumentUploadWidget } from "./document-upload-widget";
import type { DocumentItem } from "./api";

export function DashboardWidgets() {
  const [selectedDocument, setSelectedDocument] = useState<DocumentItem | null>(
    null,
  );

  return (
    <div className="space-y-4">
      <DocumentUploadWidget />
      <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
        <DocumentListWidget
          selectedDocumentId={selectedDocument?.document_id ?? null}
          onSelectDocument={(document) => {
            setSelectedDocument(document);
          }}
        />
        <DocumentQaWidget
          key={selectedDocument?.document_id ?? "no-document"}
          selectedDocument={selectedDocument}
        />
      </div>
    </div>
  );
}
