import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 bg-white border-b border-gray-200 shadow-sm z-10">
      <div className="flex items-center justify-between h-16 px-6">
        
        {/* Lado Esquerdo (Ex: Botão de Menu Mobile ou Título) */}
        <div>
          {/* Botão para abrir o menu em telas pequenas (lógica não incluída) */}
          <button className="lg:hidden text-gray-600">
            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg "><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" /></svg>
          </button>
          
          {/* Placeholder para barra de pesquisa (como na imagem) */}
          <div className="hidden lg:block">
            <span className="text-gray-400">Search...</span>
          </div>
        </div>

        {/* Lado Direito (Ícones de Ação) */}
        <div className="flex items-center space-x-4">
          <button className="p-2 text-gray-600 bg-gray-100 rounded-full hover:bg-gray-200">
             {/* Placeholder para ícone de Notificações */}
             <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341A6.002 6.002 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
          </button>
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
            B
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;