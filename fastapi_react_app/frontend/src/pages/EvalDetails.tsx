import React, { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate, useParams } from "@tanstack/react-router";
import { Container, Title, Card, Table, Button, Textarea, Loader, Center, Group, ScrollArea, Text } from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";

// Define types for our data
interface DocumentType {
  document_id: string;
  document: string;
  notes: string | null;
  eval_type: string | null;
}

interface DataType {
  input: string;
  documents: DocumentType[];
}

interface EvaluationRowProps {
  doc: DocumentType;
  localNotesValue: string;
  onNotesChange: (documentId: string, newNotes: string) => void;
  onEvalUpdate: (documentId: string, evalType: string) => void;
  onSaveNotes: (documentId: string, notes: string) => void;
}

const EvaluationRow = React.memo(({ doc, localNotesValue, onNotesChange, onEvalUpdate, onSaveNotes }: EvaluationRowProps) => {
  const [notes, setNotes] = useState(localNotesValue);
  const [debouncedNotes] = useDebouncedValue(notes, 750);

  // Effect to handle debounced saving
  useEffect(() => {
    if (debouncedNotes !== localNotesValue) {
      onSaveNotes(doc.document_id, debouncedNotes);
    }
  }, [debouncedNotes, doc.document_id, localNotesValue, onSaveNotes]);

  return (
    <Table.Tr>
      <Table.Td>{doc.document}</Table.Td>
      <Table.Td>
        <Textarea
          value={notes}
          onChange={(e) => {
            setNotes(e.target.value);
            onNotesChange(doc.document_id, e.target.value);
          }}
          placeholder="Add notes..."
          rows={3}
          style={{ minWidth: 280 }}
        />
      </Table.Td>
      <Table.Td>
        <Group gap="xs">
          <Button
            variant={doc.eval_type === "good" ? "filled" : "outline"}
            color="green"
            onClick={() => onEvalUpdate(doc.document_id, "good")}
          >
            Good
          </Button>
          <Button variant={doc.eval_type === "bad" ? "filled" : "outline"} color="red" onClick={() => onEvalUpdate(doc.document_id, "bad")}>
            Bad
          </Button>
        </Group>
      </Table.Td>
    </Table.Tr>
  );
});
EvaluationRow.displayName = "EvaluationRow"; // Optional: for better debugging

export function EvaluatePage() {
  const { inputId } = useParams({ from: "/evaluate/$inputId" });
  const navigate = useNavigate();
  const [data, setData] = useState<DataType | null>(null); // Use DataType
  const [loading, setLoading] = useState(true);
  const [localNotesValues, setLocalNotesValues] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    fetch(`/api/evaluate/${inputId}`)
      .then((res) => res.json())
      .then((fetchedData: DataType) => {
        // Use DataType
        setData(fetchedData);
        setLoading(false);
      });
  }, [inputId]);

  // Synchronize localNotesValues with data from the server
  useEffect(() => {
    if (data?.documents) {
      setLocalNotesValues((prevLocalNotes) => {
        const newLocalNotes = { ...prevLocalNotes };
        let hasChanges = false;

        // Step 1: Ensure all current documents from server have an entry in localNotesValues if undefined.
        // This initializes notes for new documents or on first load, but respects existing local edits.
        data.documents.forEach((doc: DocumentType) => {
          const docId = doc.document_id;
          if (prevLocalNotes[docId] === undefined) {
            // Only initialize if not present in previous local state.
            // This preserves any notes typed by the user if prevLocalNotes[docId] was already set.
            newLocalNotes[docId] = doc.notes || ""; // Use server notes or empty string.
            hasChanges = true;
          }
        });

        // Step 2: Remove notes from localNotesValues if their documents no longer exist on the server.
        const serverDocIds = new Set(data.documents.map((d: DocumentType) => d.document_id));
        Object.keys(newLocalNotes).forEach((localDocId) => {
          if (!serverDocIds.has(localDocId)) {
            delete newLocalNotes[localDocId];
            hasChanges = true;
          }
        });

        // Only update state if there were actual changes to avoid unnecessary re-renders.
        return hasChanges ? newLocalNotes : prevLocalNotes;
      });
    } else if (!loading && !data) {
      // If data is explicitly null or undefined (and not just loading), clear all local notes.
      setLocalNotesValues({});
    }
  }, [data, loading]);

  const saveNotesToServer = useCallback(
    async (documentId: string, notes: string) => {
      if (!inputId) return;
      await fetch(`/api/evaluate/${inputId}/${documentId}/notes`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes }),
      });

      // Update local state to reflect the new notes
      setData((currentData) => {
        if (!currentData || !currentData.documents) return currentData;
        return {
          ...currentData,
          documents: currentData.documents.map((doc) => (doc.document_id === documentId ? { ...doc, notes } : doc)),
        };
      });
    },
    [inputId]
  );

  const handleNotesChange = useCallback((documentId: string, newNotes: string) => {
    setLocalNotesValues((prev) => ({ ...prev, [documentId]: newNotes }));
  }, []);

  const updateEval = useCallback(
    async (documentId: string, evalType: string) => {
      if (!inputId) return;
      // Update the eval type on the server
      await fetch(`/api/evaluate/${inputId}/${documentId}/eval`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eval_type: evalType }),
      });

      // Update the local state directly instead of re-fetching all data
      setData((currentData) => {
        if (!currentData || !currentData.documents) {
          // Should not happen if data was loaded, but as a safeguard
          return currentData;
        }
        return {
          ...currentData,
          documents: currentData.documents.map((doc) =>
            doc.document_id === documentId
              ? {
                  ...doc,
                  eval_type: evalType,
                }
              : doc
          ),
        };
      });
    },
    [inputId, setData]
  );

  if (loading)
    return (
      <Center h={200}>
        <Loader />
      </Center>
    );
  if (!data) return <Container>No data found</Container>;

  return (
    <Container fluid h={50}>
      <Title>Evaluating Input</Title>

      <Card withBorder>
        <ScrollArea h={300} type="always" scrollbarSize={8}>
          <Text style={{ whiteSpace: "pre-wrap" }}>{data.input}</Text>
        </ScrollArea>
      </Card>

      <Card>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Output</Table.Th>
              <Table.Th w={300}>Notes</Table.Th>
              <Table.Th w={200}>Evaluation</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.documents.map((doc: DocumentType) => (
              <EvaluationRow
                key={doc.document_id}
                doc={doc}
                localNotesValue={localNotesValues[doc.document_id] ?? doc.notes ?? ""}
                onNotesChange={handleNotesChange}
                onEvalUpdate={updateEval}
                onSaveNotes={saveNotesToServer}
              />
            ))}
          </Table.Tbody>
        </Table>
      </Card>

      <Button variant="outline" onClick={() => navigate({ to: "/" })}>
        Back to Index
      </Button>
    </Container>
  );
}
