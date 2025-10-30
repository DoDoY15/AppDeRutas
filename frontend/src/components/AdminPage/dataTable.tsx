import React from 'react';
// (Importe um ícone de Download, ex: from 'lucide-react')

// 1. Interface para os dados da tabela (COM NOMES CORRIGIDOS)
interface WorkerRouteData {
  id: number;                          // <-- MUDANÇA AQUI (era plan_id)
  total_pdvs_assigned: number;         // <-- MUDANÇA AQUI (era pdvs_atendidos)
  
  // Objeto 'user' aninhado
  user: {
    full_name: string;                 // <-- MUDANÇA AQUI (era nome_trabalhador)
  };
  
  // Estes são provavelmente calculados pela API, então os nomes devem estar corretos
  horas_semanais_estimadas: number;
  download_link: string;
}

// 2. Props que o componente recebe
interface DataTableProps {
  data: WorkerRouteData[]; // Recebe o array
}

const DataTable: React.FC<DataTableProps> = ({ data }) => {
  // 3. Seu getStatusClass não é mais necessário aqui
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200 overflow-x-auto">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Resultados da Rota por Trabalhador</h2>
      
      {/* 4. Use 'data.length' (vindo das props) */}
      {data.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Nenhum dado processado ainda.</p>
          <p className="text-sm">Os resultados aparecerão aqui após o processamento.</p>
        </div>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {/* 5. Cabeçalhos corretos */}
              <th className="table-header-cell">Trabalhador</th>
              <th className="table-header-cell">PDVs Atendidos</th>
              <th className="table-header-cell">Horas (Est.)</th>
              <th className="table-header-cell">Download da Rota</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {/* 6. Map sobre os dados das props */}
            {data.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50"> {/* <-- MUDANÇA AQUI (key={row.id}) */}
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {row.user.full_name} {/* <-- MUDANÇA AQUI (era row.nome_trabalhador) */}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {row.total_pdvs_assigned} {/* <-- MUDANÇA AQUI (era row.pdvs_atendidos) */}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {row.horas_semanais_estimadas.toFixed(1)}h
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {/* 7. O link de download */}
                  <a
                    href={row.download_link}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                    // (Você precisará criar este endpoint de download)
                  >
                    Baixar Rota
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DataTable;