// DataTable.tsx

import React from 'react';

const API_URL = 'http://localhost:8000'; // Garanta que esta URL esteja correta

// 1. Interface para os dados da tabela (ATUALIZADA)
// (Agora reflete 100% o que o back-end envia)
interface WorkerRouteData {
  id: number;
  user_id: number;
  total_pdvs_assigned: number;
  user: {
    full_name: string;
  };
  horas_semanais_estimadas: number;
  download_link: string;
  sequencia: {
    Segunda: string[];
    Terça: string[];
    Quarta: string[];
    Quinta: string[];
    Sexta: string[];
  };
}

// 2. Props que o componente recebe
interface DataTableProps {
  data: WorkerRouteData[];
}

const DataTable: React.FC<DataTableProps> = ({ data }) => {
  
  // Função auxiliar para renderizar a sequência de forma legível
  const renderSequencia = (sequenciaDia: string[]) => {
    if (sequenciaDia.length === 0) {
      return <span className="text-gray-400">--</span>; // Mostra '--' se o dia estiver vazio
    }
    // Retorna os nomes dos PDVs, permitindo quebra de linha
    return (
      <div className="flex flex-col space-y-1">
        {sequenciaDia.map((pdv, index) => (
          <span key={index} className="block">{`${index + 1}. ${pdv}`}</span>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200 overflow-x-auto">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Resultados da Rota por Trabalhador</h2>
      
      {data.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Nenhum dado processado ainda.</p>
          <p className="text-sm">Os resultados aparecerão aqui após o processamento.</p>
        </div>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {/* --- CABEÇALHOS ATUALIZADOS --- */}
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trabalhador</th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Segunda</th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Terça</th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quarta</th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quinta</th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sexta</th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Download</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row) => (
              <tr key={row.user_id} className="hover:bg-gray-50"> {/* Use user_id como chave */}
                <td className="px-3 py-4 align-top whitespace-nowrap text-sm font-medium text-gray-900">
                  {/* Requisito: usuario_id e usuario_nombre */}
                  <div>{row.user.full_name}</div>
                  <div className="text-xs text-gray-500">ID: {row.user_id}</div>
                </td>
                
                {/* --- CÉLULAS DA SEQUÊNCIA (Requisito) --- */}
                <td className="px-3 py-4 align-top text-xs text-gray-600">{renderSequencia(row.sequencia.Segunda)}</td>
                <td className="px-3 py-4 align-top text-xs text-gray-600">{renderSequencia(row.sequencia.Terça)}</td>
                <td className="px-3 py-4 align-top text-xs text-gray-600">{renderSequencia(row.sequencia.Quarta)}</td>
                <td className="px-3 py-4 align-top text-xs text-gray-600">{renderSequencia(row.sequencia.Quinta)}</td>
                <td className="px-3 py-4 align-top text-xs text-gray-600">{renderSequencia(row.sequencia.Sexta)}</td>
                
                <td className="px-3 py-4 align-top whitespace-nowrap text-sm">
                  {/* Requisito: download */}
                  <a
                    href={`${API_URL}${row.download_link}`}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                    download
                  >
                    Baixar Excel
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