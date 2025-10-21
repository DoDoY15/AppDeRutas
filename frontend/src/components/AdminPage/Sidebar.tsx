import React from 'react';

interface IconPlaceholderProps {
    src: string;
    alt: string;
}

const IconPlaceholder: React.FC<IconPlaceholderProps> = ({ src, alt }) => (
    <div className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
        <img src={src} alt={alt} className="w-full h-full object-contain" />
    </div>
);


const Sidebar: React.FC = () => {
    return (
        <div className="fixed inset-y-0 left-0 w-64 bg-slate-900 text-gray-300 transform -translate-x-full lg:translate-x-0 transition-transform duration-300 ease-in-out z-30 overflow-y-auto">
            
            {/* Logo / Perfil */}
            <div className="flex items-center justify-center h-20 border-b border-slate-700">
                <span className="text-white text-2xl font-bold">Meu Painel</span>
            </div>

            {/* Navegação Principal */}
            <nav className="flex-1 px-4 py-6 space-y-1">
                <p className="px-3 text-xs uppercase tracking-wider text-gray-500 font-semibold mt-4 mb-2">Principal</p>
                
                <div
                    className="flex items-center space-x-3 px-3 py-2 bg-indigo-600 text-white rounded-lg transition duration-150 cursor-pointer"
                >
                    <IconPlaceholder src="/Icons/home.png" alt="Ícone Home" />
                    <span>Home</span>
                </div>

                <div 
                    className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-slate-700 hover:text-white transition duration-150 cursor-pointer"
                >
                    <IconPlaceholder src="/Icons/google-docs.png" alt="Ícone Documento" />
                    <span>Processamentos</span>
                </div>
            </nav>
            
            {/* Seção Admin */}
            <nav className="flex-1 px-4 py-6 space-y-1">
                 <p className="px-3 text-xs uppercase tracking-wider text-gray-500 font-semibold mt-4 mb-2">Admin</p>
                 
                 {/* Link Usuários */}
                 <div 
                    className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-slate-700 hover:text-white transition duration-150 cursor-pointer"
                 >
                    <IconPlaceholder src="/Icons/user.png" alt="Ícone Usuários" />
                    <span>Usuários</span>
                 </div>

                 {/* Link Configurações */}
                 <div 
                    className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-slate-700 hover:text-white transition duration-150 cursor-pointer"
                 >
                    <IconPlaceholder src="/Icons/settings.png" alt="Ícone Configurações" />
                    <span>Configurações</span>
                 </div>
            </nav>
        </div>
    );
};

export default Sidebar;