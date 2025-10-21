import React from 'react';

interface TableItem {
  id: number;
  nome: string;
  valor: number | string;
  status: 'Processado' | 'Pendente' | 'Erro';
}

const DataTable: React.FC = () => {
  const data: TableItem[] = [
    { id: 1001, nome: 'Item Exemplo A', valor: 150.75, status: 'Processado' },
    { id: 1002, nome: 'Item Exemplo B', valor: 'N/A', status: 'Erro' },
    { id: 1003, nome: 'Item Exemplo C', valor: 99.00, status: 'Pendente' },
    { id: 1004, nome: 'Item Exemplo D', valor: 12.50, status: 'Processado' },
  ];

  const getStatusClass = (status: TableItem['status']): string => {
    switch (status) {
      case 'Processado':
        return 'bg-green-100 text-green-800';
      case 'Pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'Erro':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200 overflow-x-auto">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Resultados da Tabela</h2>
      {data.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Nenhum dado processado ainda.</p>
          <p className="text-sm">Os resultados aparecerão aqui após o processamento do arquivo.</p>
        </div>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="table-header-cell">ID</th>
              <th className="table-header-cell">Nome do Item</th>
              <th className="table-header-cell">Valor</th>
              <th className="table-header-cell">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {item.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {item.nome}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {typeof item.valor === 'number' ? `R$ ${item.valor.toFixed(2)}` : item.valor}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusClass(item.status)}`}
                  >
                    {item.status}
                  </span>
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