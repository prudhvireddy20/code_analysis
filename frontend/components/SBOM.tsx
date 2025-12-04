// components/SBOM.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";

interface SBOMEntry {
  name: string;
  version: string;
  type: string;
  purl?: string;
  tool: string;
}

export default function SBOM({ data }: { data: SBOMEntry[] }) {
  if (!data || data.length === 0) {
    return (
      <Card className="p-4">
        <p className="text-gray-600">No SBOM data available.</p>
      </Card>
    );
  }

  return (
    <Card className="shadow-md rounded-2xl">
      <CardContent>
        <h2 className="text-xl font-semibold mb-4">📦 SBOM (Software Bill of Materials)</h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Package Name</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>PURL</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((pkg, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-medium">{pkg.name}</TableCell>
                  <TableCell>{pkg.version}</TableCell>
                  <TableCell>{pkg.type}</TableCell>
                  <TableCell className="text-xs text-gray-500">{pkg.purl}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
