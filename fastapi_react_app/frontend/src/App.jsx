import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, useParams } from 'react-router-dom'
import { Container, Title, Card, Table, Button, Textarea, Loader, Center, Group } from '@mantine/core'

function App() {
  return (
    <Container>
      <Routes>
        <Route path="/" element={<IndexPage />} />
        <Route path="/evaluate/:inputId" element={<EvaluatePage />} />
      </Routes>
    </Container>
  )
}

function IndexPage() {
  const [inputs, setInputs] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetch('/api/inputs')
      .then(res => res.json())
      .then(data => {
        setInputs(data)
        setLoading(false)
      })
  }, [])

  if (loading) return <Center h={200}><Loader /></Center>

  return (
    <div>
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
            {inputs.map(input => (
              <Table.Tr key={input.input_id}>
                <Table.Td>{input.input}</Table.Td>
                <Table.Td>
                  <Button onClick={() => navigate(`/evaluate/${input.input_id}`)}>
                    Evaluate
                  </Button>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Card>
    </div>
  )
}

function EvaluatePage() {
  const { inputId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/evaluate/${inputId}`)
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
  }, [inputId])

  const updateNotes = async (documentId, notes) => {
    await fetch(`/api/evaluate/${inputId}/${documentId}/notes`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    })
  }

  const updateEval = async (documentId, evalType) => {
    await fetch(`/api/evaluate/${inputId}/${documentId}/eval`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ eval_type: evalType })
    })
    
    const response = await fetch(`/api/evaluate/${inputId}`)
    const newData = await response.json()
    setData(newData)
  }

  if (loading) return <Center h={200}><Loader /></Center>
  if (!data) return <div>No data found</div>

  return (
    <div>
      <Title>Evaluating Input</Title>
      
      <Card>
        {data.input.replace(/\\n/g, '\n')}
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
            {data.documents.map(doc => (
              <Table.Tr key={doc.document_id}>
                <Table.Td>
                  {doc.document}
                </Table.Td>
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
                      variant={doc.eval_type === 'good' ? 'filled' : 'outline'}
                      color="green"
                      onClick={() => updateEval(doc.document_id, 'good')}
                    >
                      Good
                    </Button>
                    <Button
                      variant={doc.eval_type === 'bad' ? 'filled' : 'outline'}
                      color="red"
                      onClick={() => updateEval(doc.document_id, 'bad')}
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
      
      <Button variant="outline" onClick={() => navigate('/')}>
        Back to Index
      </Button>
    </div>
  )
}

export default App
