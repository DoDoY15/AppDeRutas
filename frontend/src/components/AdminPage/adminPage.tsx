import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import FileUploader from './fileUploader';
import Dashboard from './dashboard';
import DataTable from './dataTable';

const AdminPage: React.FC = () => {
  return (
    // Container principal 
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col lg:ml-64">
        <Header />
        <main className="flex-1 p-6 md:p-10">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 border-l-4 border-indigo-600 pl-3">
              Painel de Processamento de Dados
            </h1>
            <p className="text-gray-500 mt-1 ml-4">
              Gerencie o upload, visualize métricas e dados processados.
            </p>
          </header>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            <div className="lg:col-span-1">
              <FileUploader />
            </div>
            <div className="lg:col-span-2">
              <Dashboard />
            </div>
          </div>  
          <section>
            <DataTable />
          </section>
        </main>
      </div>
    </div>
  );
};

export default AdminPage;