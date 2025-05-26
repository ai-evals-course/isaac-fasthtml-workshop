import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "@tanstack/react-router";
import { Container, Title, Card, Table, Button, Textarea, Loader, Center, Group } from "@mantine/core";

export function EvaluatePage() {
  const { inputId } = useParams({ from: "/evaluate/$inputId" });
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null); // Add type for data
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/evaluate/${inputId}`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      });
  }, [inputId]);

  const updateNotes = async (documentId: string, notes: string) => {
    await fetch(`/api/evaluate/${inputId}/${documentId}/notes`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ notes }),
    });
  };

  const updateEval = async (documentId: string, evalType: string) => {
    await fetch(`/api/evaluate/${inputId}/${documentId}/eval`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ eval_type: evalType }),
    });

    const response = await fetch(`/api/evaluate/${inputId}`);
    const newData = await response.json();
    setData(newData);
  };

  if (loading)
    return (
      <Center h={200}>
        <Loader />
      </Center>
    );
  if (!data) return <Container>No data found</Container>;

  return (
    <Container>
      <Title>Evaluating Input</Title>

      <Card>{data.input.replace(/\\n/g, "\n")}</Card>

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
            {data.documents.map((doc: any) => (
              <Table.Tr key={doc.document_id}>
                <Table.Td>{doc.document}</Table.Td>
                <Table.Td>
                  <Textarea
                    value={doc.notes}
                    onChange={(e) => updateNotes(doc.document_id, e.target.value)}
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
                      onClick={() => updateEval(doc.document_id, "good")}
                    >
                      Good
                    </Button>
                    <Button
                      variant={doc.eval_type === "bad" ? "filled" : "outline"}
                      color="red"
                      onClick={() => updateEval(doc.document_id, "bad")}
                    >
                      Bad
                    </Button>
                  </Group>
                </Table.Td>
              </Table.Tr>
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
