import React, { useState } from "react";
import axios from "axios";  
import styles from "./Login.module.css";
import { constants } from "buffer";


export const Login: React.FC = () => {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');   

    const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password  );

        try {
            const response = await axios.post('http://127.0.0.1:8000/app/api/api_v1/token', params);

            alert('Login bem-sucedido! Token: ' + response.data.access_token);
            // TODO: handle token (e.g. save to localStorage, set auth state, redirect)
        } catch (err: any) {
            const message = err.response?.data?.detail || 'Erro no login. Por favor, tente novamente.';
            setError(message);
        } finally {
            setIsLoading(false);
        }   

    };

    return (
            <><div className={styles.header}>
            <h2 className={styles.title}>Login</h2>
            <p className={styles.subtitle}>Faça login para continuar.</p>
        </div><form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.inputGroup}>
                    <label htmlFor="username" className={styles.label}>Utilizador</label>
                    <input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className={styles.input}
                        placeholder="seu.utilizador"
                        required
                        disabled={isLoading} />
                </div>

                <div className={styles.inputGroup}>
                    <label htmlFor="password" className={styles.label}>Password</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className={styles.input}
                        placeholder="••••••••"
                        required
                        disabled={isLoading} />
                </div>

                {error && <p className={styles.errorMessage}>{error}</p>}

                <div>
                    <button type="submit" disabled={isLoading} className={styles.button}>
                        {isLoading ? 'A entrar...' : 'Entrar'}
                    </button>
                </div>
            </form></>
  );
};