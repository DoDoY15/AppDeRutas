import React from 'react';

interface DashboardData {
  run_id: number;
  total_pdvs_assigned: number;   
  total_pdvs_unassigned: number;  
  created_at: string;
  total_visits_missed: number; 
}

interface DashboardProps {
  data: DashboardData | null;
  totalWorkers: number;
}

const Dashboard: React.FC<DashboardProps> = ({ data, totalWorkers }) => {

  if (!data) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Visão Geral</h2>
        <div className="text-center py-10 text-gray-500">
          Aguardando o fim do processamento...
        </div>
      </div>
    );
  }

  const total_pdvs_requeridos = data.total_pdvs_assigned + data.total_pdvs_unassigned;
  const taxa_de_atendimento_percent = total_pdvs_requeridos > 0 
    ? (data.total_pdvs_assigned / total_pdvs_requeridos) * 100 
    : 0;

  const metrics = [

    { title: 'PDVs Totalmente Atendidos', value: data.total_pdvs_assigned.toString(), color: 'bg-gradient-to-r from-green-500 to-green-600' },
    { title: 'PDVs Não (Totalmente) Atendidos', value: data.total_pdvs_unassigned.toString(), color: 'bg-gradient-to-r from-red-500 to-red-600' },

    { title: 'Visitas Faltantes', value: data.total_visits_missed.toString(), color: 'bg-gradient-to-r from-yellow-500 to-yellow-600' },
    
    { title: 'Taxa de Atendimento (PDVs)', value: `${taxa_de_atendimento_percent.toFixed(1)}%`, color: 'bg-gradient-to-r from-blue-500 to-blue-600' },
    { title: 'Trabalhadores Ativos', value: totalWorkers.toString(), color: 'bg-gradient-to-r from-purple-500 to-purple-600' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Métricas Globais (Run: {data.run_id})</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {metrics.map((metric) => (
          <div key={metric.title} className={`p-4 rounded-lg text-white ${metric.color}`}>
            <div className="text-sm font-medium uppercase tracking-wide">{metric.title}</div>
            <div className="text-3xl font-bold">{metric.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;