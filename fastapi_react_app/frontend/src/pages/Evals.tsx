import React, { useState, useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Container, Title, Card, Table, Button, Loader, Center } from "@mantine/core";

export function IndexPage() {
  const [inputs, setInputs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/inputs")
      .then((res) => res.json())
      .then((data) => {
        setInputs(data);
        setLoading(false);
      });
  }, []);

  if (loading)
    return (
      <Center h={200}>
        <Loader />
      </Center>
    );

  return (
    <Container>
      <Title>Evaluation Index</Title>
      <Card>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Input</Table.Th>
              <Table.Th>Action</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {inputs.map((input: any) => (
              <Table.Tr key={input.input_id}>
                <Table.Td>{input.input}</Table.Td>
                <Table.Td>
                  <Button onClick={() => navigate({ to: "/evaluate/$inputId", params: { inputId: input.input_id } })}>Evaluate</Button>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Card>
    </Container>
  );
}
