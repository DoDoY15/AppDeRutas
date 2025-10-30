import React, { useState } from 'react';

// URL base correta para seus endpoints de setup
const API_BASE_URL = 'http://localhost:8000/api/v1';

const FileUploader: React.FC = () => {
    
    const [userFile, setUserFile] = useState<File | null>(null);
    const [pdvFile, setPdvFile] = useState<File | null>(null);
    const [uploadingUsers, setUploadingUsers] = useState(false);
    const [uploadingPos, setUploadingPos] = useState(false);
    
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>, setFile: React.Dispatch<React.SetStateAction<File | null>>) => {
        if (event.target.files && event.target.files.length > 0) {
            setFile(event.target.files[0]);
        }
    };

    const handleUpload = async (file: File | null, endpoint: string, keyName: string , setLoadingState: React.Dispatch<React.SetStateAction<boolean>> ) => { 
        if (!file) {
            alert("Por favor, selecione um arquivo Excel.");
            return;
        }
        
        setLoadingState(true);
        const formData = new FormData();
        formData.append(keyName, file); 
        const FINAL_ENDPOINT = `/setup/${endpoint}`;
        try {

            const response = await fetch(`${API_BASE_URL}${FINAL_ENDPOINT}`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                alert(`Upload de ${keyName} bem-sucedido: ${result.details || result.message}`);
                // Limpa o estado do arquivo após o upload
                if (keyName === 'users_file') setUserFile(null);
                if (keyName === 'pos_file') setPdvFile(null);
            } else {
                const error = await response.json();
                alert(`Erro no upload: ${error.detail}`);
            }
        } catch (error) {
            console.error('Erro de rede:', error);
            alert("Erro de conexão com o servidor FastAPI.");
        } finally {
            setLoadingState(false);
        }
    };

    return (
        // O layout de grid que os coloca lado a lado
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6"> 
            
            {/* --------------------------- */}
            {/* BOX 1: Arquivo de Usuários  */} 
            {/* --------------------------- */}
            <div className="flex-1 bg-white p-6 rounded-lg shadow-lg border border-gray-200">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Subir Arquivo de Usuários</h2>
                
                <label
                    htmlFor="dropzone-users" 
                    className="flex flex-col justify-center items-center w-full h-48 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 cursor-pointer hover:bg-gray-100 transition duration-150"
                >
                    {/* Este é o JSX correto (que você tinha) */}
                    <div className="fill">
                      <svg
                      className="w-10 h-10 text-indigo-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg">
                      <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="1.5"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" >
                      </path>
                      </svg>
                    </div>
                    <div className="text-center sm:text-left">
                        <p className="text-xs text-gray-500 mt-0.5"> accept files: Excel </p>
                    </div>
                    
                    <input id="dropzone-users" type="file" className="hidden" accept=".xlsx, .xls" onChange={(e) => handleFileChange(e , setUserFile)}/>
                    <p className="mt-2 text-sm text-gray-500 justify-center text-center ">
                        {userFile ? `Selecionado: ${userFile.name}` : 'Nenhum arquivo selecionado'}
                    </p>
                </label>
                
                <button
                    onClick={() => handleUpload(userFile, 'users/upload', 'users_file', setUploadingUsers)} 
                    disabled={!userFile || uploadingUsers}
                    className={`mt-4 w-full px-4 py-2 rounded font-semibold transition duration-150 ${
                        !userFile || uploadingUsers
                            ? 'bg-gray-400 cursor-not-allowed' 
                            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                    }`}
                >
                    {uploadingUsers ? 'Enviando...' : 'Enviar Arquivo de Usuários'}
                </button>
            </div>

            {/* ------------------------ */}
            {/* BOX 2: Arquivo de PDVs   */}
            {/* ------------------------ */}
            <div className="flex-1 bg-white p-6 rounded-lg shadow-lg border border-gray-200">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Subir Arquivo de PDVs</h2>
                
                <label
                    htmlFor="dropzone-pdvs" 
                    className=" flex flex-col justify-center items-center w-full h-48 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 cursor-pointer hover:bg-gray-100 transition duration-150"
                >
                    <div className="fill">
                      <svg
                      className="w-10 h-10 text-indigo-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg">
                      <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="1.5"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" >
                      </path>
                      </svg>
                    </div>
                    <div className="text-center sm:text-left">
                        <p className="text-xs text-gray-500 mt-0.5"> accept files: Excel </p>
                    </div>
                    
                    <input id="dropzone-pdvs" type="file" className="hidden" accept=".xlsx, .xls" onChange={(e)=> handleFileChange(e , setPdvFile)}/>

                    <p className="mt-2 text-sm text-gray-500 justify-center text-center " >
                        {pdvFile ? `Selecionado: ${pdvFile.name}` : 'Nenhum arquivo selecionado'}
                    </p>
                </label>
                
                <button
                    onClick={() => handleUpload(pdvFile, 'pos/upload', 'pos_file', setUploadingPos)} 
                    disabled={!pdvFile || uploadingPos} 
                    className={`mt-4 w-full px-4 py-2 rounded font-semibold transition duration-150 ${
                        !pdvFile || uploadingPos
                            ? 'bg-gray-400 cursor-not-allowed' 
                            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                    }`}
                >
                    {uploadingPos ? 'Enviando...' : 'Enviar Arquivo de PDVs'}
                </button>
            </div>
        </div>
    );
};

export default FileUploader;