'use client';
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";

interface NoirEntry {
  rule?: string;
  file?: string;
  description?: string;
  severity?: string;
  tool: string;
  error?: string;
}

export default function Noir({ data }: { data: NoirEntry[] }) {
  console.log("NOIR data:", data);
  if (!data || data.length === 0)
  {
    return (
      <Card className="p-4">
        <p className="text-gray-600">No findings from OWASP Noir.</p>
      </Card>
    );
  }

  return (
    <Card className="shadow-md rounded-2xl">
      <CardContent>
        <h2 className="text-xl font-semibold mb-4">🕵️‍♂️ OWASP Noir Results</h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule</TableHead>
                <TableHead>File</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Severity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((entry, idx) => (
                <TableRow key={idx}>
                  <TableCell>{entry.rule || "-"}</TableCell>
                  <TableCell>{entry.file || "-"}</TableCell>
                  <TableCell>{entry.description || entry.error || "-"}</TableCell>
                  <TableCell>{entry.severity || "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
