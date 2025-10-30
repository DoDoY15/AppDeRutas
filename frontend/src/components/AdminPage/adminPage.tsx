import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Dashboard from './dashboard';
import DataTable from './dataTable';
import FileUploader from './fileUploader';


const API_URL = 'http://localhost:8000';

interface OptimizeTriggerProps {
  onStart: () => void;
  loading: boolean; 
}
// --- Componente de botão (interno da AdminPage) ---
const OptimizeTrigger = ({ onStart, loading }: OptimizeTriggerProps) => (
  <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
    <h2 className="text-xl font-semibold text-gray-800 mb-4">Iniciar Processamento</h2>
    <p className="text-gray-600 mb-4">
      Após fazer o upload dos PDVs e Trabalhadores, clique aqui para iniciar o
      processamento da otimização.
    </p>
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
  // Lógica de Otimização (não precisa da lógica de upload)
  const [status, setStatus] = useState('IDLE');
  const [dashboardData, setDashboardData] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [error, setError] = useState('');

  // (Funções fetchResults e checkStatus)
  const fetchResults = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/optimize/status/latest`);
      setDashboardData(response.data.dashboard || null);
      setTableData(response.data.table || []);
      
      setStatus('COMPLETED');
      setError('');
    } catch (e) {
      setError('Erro ao buscar resultados.');
      setStatus('FAILED');
    }
  }, []);

  const checkStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/optimize/status/latest`);
      const newStatus = response.data.status;
      console.log("STATUS RECEBIDO DO BACKEND:", newStatus);
      
      if (newStatus === 'RUNNING' || newStatus === 'PENDING') {
        setStatus('RUNNING');
      } else if (newStatus == 'COMPLETED') {
        setStatus('COMPLETED');
        await fetchResults(); 
      } else if (newStatus === 'FAILED') {
        setStatus('FAILED');
        setError('A otimização falhou no backend.');
      }
    } catch (e) {
      setError('Erro ao contatar o servidor.');
    }
  }, [fetchResults]);

  // Polling de status
  useEffect(() => {
    let intervalId: NodeJS.Timeout | undefined = undefined;

    if (status === 'RUNNING') {
      intervalId = setInterval(checkStatus, 5000);
    }
    return () => clearInterval(intervalId);
  }, [status, checkStatus]);
  //  botão "Iniciar"
  const handleStartOptimization = async () => {
    setStatus('RUNNING'); 
    setError('');
    setDashboardData(null);
    setTableData([]);
    try {
      await await axios.post(`${API_URL}/api/v1/optimize/run-optimization`);
    } catch (e) {
      setStatus('FAILED');
      setError('Falha ao iniciar a tarefa.');
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
          
          {/* 1. RENDERIZA O COMPONENTE DE UPLOAD */}
          <FileUploader />

          {/* 2. RENDERIZA O BOTÃO DE INICIAR */}
          <OptimizeTrigger onStart={handleStartOptimization} loading={status === 'RUNNING'} />

          {/* Feedback de Status */}
          {status === 'RUNNING' && <div className="text-blue-600 font-semibold p-4 bg-blue-50 rounded-lg">Processando otimização... Por favor, aguarde.</div>}
          {error && <div className="text-red-600 font-semibold p-4 bg-red-50 rounded-lg">{error}</div>}
        </div>

        {/* --- COLUNA DA DIREITA (Dashboard) --- */}
        <div className="lg:col-span-1">
          <Dashboard data={dashboardData} />
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