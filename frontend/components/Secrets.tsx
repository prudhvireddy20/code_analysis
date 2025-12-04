import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { ShieldAlert } from "lucide-react";

interface GitleaksResult {
  file: string;
  line: number | string;
  rule: string;
  secret: string;
  tool: string;
  error?: string;
}

export default function Secrets({ data }: { data: GitleaksResult[] }) {
  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <CardContent className="text-center text-gray-500">
          <ShieldAlert className="w-6 h-6 mx-auto mb-2 text-gray-400" />
          <p>No secrets found 🎉</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <CardContent>
        <h2 className="text-xl font-semibold mb-4">🔑 Gitleaks Secrets</h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule</TableHead>
                <TableHead>File</TableHead>
                <TableHead>Line</TableHead>
                <TableHead>Secret</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{item.rule}</TableCell>
                  <TableCell className="font-mono text-sm">{item.file}</TableCell>
                  <TableCell>{item.line}</TableCell>
                  <TableCell className="text-red-500 font-mono">{item.secret}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
