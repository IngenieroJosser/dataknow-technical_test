import axios, { AxiosError } from 'axios';

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

// Función simple de conexión sin autenticación
export const apiRequest = async <T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  endpoint: string,
  data?: any
): Promise<T> => {
  const baseUrl = 'http://127.0.0.1:8000';
  const url = `${baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  console.log(`🌐 Enviando ${method} a: ${url}`);
  
  try {
    const config = {
      method,
      url,
      data: method === 'POST' || method === 'PUT' ? data : undefined,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: 10000, // 10 segundos
    };
    
    const response = await axios(config);
    console.log(`✅ Respuesta recibida de ${url}:`, response.status);
    
    return response.data;
    
  } catch (error) {
    const axiosError = error as AxiosError;
    
    console.error(`❌ Error en ${method} ${url}:`, {
      message: axiosError.message,
      code: axiosError.code,
      status: axiosError.response?.status,
      data: axiosError.response?.data,
    });
    
    // Errores específicos
    if (axiosError.code === 'ECONNABORTED') {
      throw {
        message: 'El servidor tardó demasiado en responder. Verifica que el backend esté corriendo.',
        status: 408,
        details: { url, method }
      } as ApiError;
    }
    
    if (!axiosError.response) {
      throw {
        message: 'No se puede conectar al servidor. Asegúrate de que el backend esté ejecutándose en http://127.0.0.1:8000',
        status: 0,
        details: { url, method }
      } as ApiError;
    }
    
    // Error HTTP
    throw {
      message: axiosError.response.data || axiosError.response.data || `Error ${axiosError.response.status}`,
      status: axiosError.response.status,
      details: axiosError.response.data
    } as ApiError;
  }
};

// Función específica para consultas legales
export const queryLegalAssistant = async (question: string) => {
  return apiRequest<{
    answer: string;
    confidence: number;
    matched_cases: any[];
    timestamp: string;
    total_cases_searched: number;
  }>('POST', '/query', { question });
};

// Función para verificar salud del backend
export const checkBackendHealth = async () => {
  return apiRequest<{
    status: string;
    service: string;
    timestamp: string;
    cases_loaded: number;
    version: string;
  }>('GET', '/health');
};

// Función para debugging
export const debugBackend = async () => {
  return apiRequest<{
    backend_running: boolean;
    python_version: string;
    data_file_exists: boolean;
    cases_in_memory: number;
    sample_case: any;
    timestamp: string;
  }>('GET', '/debug');
};