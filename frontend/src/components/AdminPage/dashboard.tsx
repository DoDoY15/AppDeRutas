import React from 'react';

interface Metric {
  title: string;
  value: string;
  color: string;
}

const Dashboard: React.FC = () => {
  const metrics: Metric[] = [
    { title: 'Total de Registros', value: '1.234', color: 'bg-gradient-to-r from-blue-500 to-blue-600' },
    { title: 'Linhas Processadas', value: '98%', color: 'bg-gradient-to-r from-green-500 to-green-600' },
    { title: 'Erros Encontrados', value: '12', color: 'bg-gradient-to-r from-red-500 to-red-600' },
    { title: 'Última Atualização', value: 'Há 5 min', color: 'bg-gradient-to-r from-amber-500 to-amber-600' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Visão Geral</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric) => (
          <div key={metric.title} className={`metric-card ${metric.color}`}>
            <p className="text-sm font-medium opacity-80">{metric.title}</p>
            <p className="text-3xl font-bold mt-1">{metric.value}</p>
          </div>
        ))}
      </div>

      <h3 className="text-xl font-semibold text-gray-800 mb-4 mt-8 border-b pb-2">
        Análise Gráfica
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-50 border border-gray-200 p-6 rounded-lg h-80 flex items-center justify-center">
          <p className="text-gray-500 font-semibold">Gráfico 1: Performance (Placeholder)</p>
        </div>
        <div className="bg-gray-50 border border-gray-200 p-6 rounded-lg h-80 flex items-center justify-center">
          <p className="text-gray-500 font-semibold">Gráfico 2: Distribuição (Placeholder)</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;