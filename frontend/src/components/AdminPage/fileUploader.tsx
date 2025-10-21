import React from 'react';

const FileUploader: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200 h-full">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">Subir Arquivo Excel</h2>
      
      {/* Dropzone Label */}
      <label
        htmlFor="dropzone-file"
        className="flex flex-col justify-center items-center w-full h-48 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 cursor-pointer hover:bg-gray-100 transition duration-150"
      >
        {/* Container para o Ícone e o Texto (Lado a Lado) */}
        <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-4 p-4">

          <svg
            className="w-10 h-10 text-indigo-500 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            ></path>
          </svg>
          
          {/* Container do Texto */}
          <div className="text-center sm:text-left">
            <p className="text-sm text-gray-600">
              <span className="font-semibold text-indigo-600">Clique para subir</span>
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              Ou arraste e solte (.xlsx, .xls)
            </p>
          </div>

        </div>
        <input id="dropzone-file" type="file" className="hidden" accept=".xlsx, .xls" />
      </label>
    </div>
  );
};

export default FileUploader;