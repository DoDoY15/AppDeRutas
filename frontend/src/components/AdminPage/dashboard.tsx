import React from 'react';

// 1. Interface para os dados do dashboard (COM NOMES CORRIGIDOS)
interface DashboardData {
  total_pdvs_assigned: number;       // <-- MUDANÇA AQUI
  total_pdvs_unassigned: number;     // <-- MUDANÇA AQUI
  created_at: string;                // <-- MUDANÇA AQUI
}

// 2. Props que o componente recebe
interface DashboardProps {
  data: DashboardData | null; // Pode ser nulo enquanto carrega
}

const Dashboard: React.FC<DashboardProps> = ({ data }) => {
  // 3. Se 'data' for nulo, mostre um placeholder
  if (!data) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Visão Geral</h2>
        <div className="text-center py-10 text-gray-500">
          Aguardando o fim do processamento para exibir as métricas...
        </div>
      </div>
    );
  }

  // 4. Se 'data' existir, calcule as métricas
  const total_pdvs = data.total_pdvs_assigned + data.total_pdvs_unassigned;
  
  // Cálculo seguro da taxa de atendimento
  const taxa_de_atendimento_percent = total_pdvs > 0 
    ? (data.total_pdvs_assigned / total_pdvs) * 100 
    : 0;

  const metrics = [
    { title: 'PDVs Atendidos', value: data.total_pdvs_assigned.toString(), color: 'bg-gradient-to-r from-green-500 to-green-600' },
    { title: 'PDVs Não Atendidos', value: data.total_pdvs_unassigned.toString(), color: 'bg-gradient-to-r from-red-500 to-red-600' },
    { title: 'Taxa de Atendimento', value: `${taxa_de_atendimento_percent.toFixed(1)}%`, color: 'bg-gradient-to-r from-blue-500 to-blue-600' },
    { title: 'Última Atualização', value: new Date(data.created_at).toLocaleString('pt-BR'), color: 'bg-gradient-to-r from-amber-500 to-amber-600' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Visão Geral</h2>
      
      {/* O resto do seu JSX é o mesmo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric) => (
            <div key={metric.title} className={`metric-card ${metric.color}`}>
              {/* ... (seu código de card) ... */}
            </div>
          ))}
        </div>
        {/* ... (Seus gráficos placeholder) ... */}
    </div>
  );
};

export default Dashboard;