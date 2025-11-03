
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Dashboard from './dashboard';
import DataTable from './dataTable';
import FileUploader from './fileUploader';

const API_URL = 'http://localhost:8000';

// botão

interface OptimizeTriggerProps {
  onStart: () => void;
  loading: boolean; 
}
const OptimizeTrigger = ({ onStart, loading }: OptimizeTriggerProps) => (
  <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
    <h2 className="text-xl font-semibold text-gray-800 mb-4">Iniciar Processamento</h2>
    <button
      onClick={onStart}
      disabled={loading}
      className={`w-full px-4 py-3 text-white font-bold rounded-lg ${
        loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
      } transition-colors duration-200`}
    >
      {loading ? 'Processando...' : 'Iniciar Geração de Rotas'}
    </button>
  </div>
);
// --- Componente Principal da Página ---
const AdminPage: React.FC = () => {
  const [status, setStatus] = useState('IDLE');
  // Ajuste nos tipos para refletir os dados que vêm da API
  const [dashboardData, setDashboardData] = useState<any>(null); 
  const [tableData, setTableData] = useState<any[]>([]);
  const [error, setError] = useState('');

  const fetchResults = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/optimize/results/latest`);
      
      setDashboardData(response.data.dashboard || null);
      setTableData(response.data.table || []);
      setStatus('COMPLETED');
      setError('');
    } catch (e: any) {
      setError('Erro ao buscar resultados: ' + (e.message || 'Erro desconhecido'));
      setStatus('FAILED');
    }
  }, []);

  const checkStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/optimize/status/latest`);
      const newStatus = response.data.status;
      
      if (newStatus === 'RUNNING' || newStatus === 'PENDING') {
        setStatus('RUNNING');
      } else if (newStatus === 'COMPLETED') {
        setStatus('COMPLETED');
        fetchResults();
      } else if (newStatus === 'FAILED') {
        setStatus('FAILED');
        setError('A otimização falhou no backend.');
      }
    } catch (e: any) {
      setError('Erro ao contatar o servidor: ' + (e.message || 'Erro desconhecido'));
    }
  }, [fetchResults]);

  useEffect(() => {
    let intervalId: NodeJS.Timeout | undefined = undefined;

    if (status === 'RUNNING') {
      intervalId = setInterval(checkStatus, 5000);
    }
    return () => clearInterval(intervalId);
  }, [status, checkStatus]);

  // Botão "Iniciar"
  const handleStartOptimization = async () => {
    setStatus('RUNNING'); 
    setError('');
    setDashboardData(null);
    setTableData([]);
    try {
      await axios.post(`${API_URL}/api/v1/optimize/run-optimization`);
      // Inicia a primeira verificação imediatamente
      checkStatus(); 
    } catch (e: any) {
      setStatus('FAILED');
      setError('Falha ao iniciar a tarefa: ' + (e.message || 'Erro desconhecido'));
    }
  };
  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">
        Painel de Processamento de Dados
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* --- COLUNA DA ESQUERDA (Uploads e Botão) --- */}
        <div className="lg:col-span-2 space-y-6">
          <FileUploader />
          <OptimizeTrigger onStart={handleStartOptimization} loading={status === 'RUNNING'} />
          {/* ... (Feedback de Status) ... */}
        </div>

        {/* --- COLUNA DA DIREITA (Dashboard) --- */}
        <div className="lg:col-span-1">
          {/* --- 2. PASSE A PROP totalWorkers AQUI --- */}
          <Dashboard 
            data={dashboardData} 
            totalWorkers={tableData.length} 
          />
        </div>

        {/* --- LINHA INFERIOR (Tabela de Resultados) --- */}
        <div className="lg:col-span-3">
          <DataTable data={tableData} />
        </div>
      </div>
    </div>
  );
};

export default AdminPage;