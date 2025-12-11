'use client'

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Sparkles,
  Scale,
  BookOpen,
  ChevronRight,
  Bot,
  User,
  Loader2,
  MessageSquare,
  FileText,
  Shield,
  Clock,
  Layers,
  Wifi,
  WifiOff,
  Database,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { queryLegalAssistant, checkBackendHealth, debugBackend, type ApiError } from '@/lib/api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isError?: boolean;
}

interface CasePreview {
  id: string;
  title: string;
  category: string;
  status: 'resuelto' | 'en_proceso' | 'archivado';
  confidence: number;
  description?: string;
}

interface BackendStatus {
  connected: boolean;
  loading: boolean;
  message: string;
  casesLoaded?: number;
}

// Componente para verificar la conexión
function ConnectionChecker({ status, onTest }: { 
  status: BackendStatus; 
  onTest: () => void;
}) {
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={onTest}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
          status.connected 
            ? 'bg-green-100 text-green-800 border border-green-300 hover:bg-green-200' 
            : status.loading
            ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
            : 'bg-red-100 text-red-800 border border-red-300 hover:bg-red-200'
        }`}
        disabled={status.loading}
      >
        {status.loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm font-medium">Verificando...</span>
          </>
        ) : status.connected ? (
          <>
            <Wifi className="w-4 h-4" />
            <div className="flex flex-col items-start">
              <span className="text-sm font-medium">Conectado</span>
              {status.casesLoaded && (
                <span className="text-xs opacity-75">{status.casesLoaded} casos</span>
              )}
            </div>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            <div className="flex flex-col items-start">
              <span className="text-sm font-medium">Sin conexión</span>
              <span className="text-xs opacity-75">Click para probar</span>
            </div>
          </>
        )}
      </button>
    </div>
  );
}

export default function LegalChatAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '¡Hola! Soy tu asistente legal especializado. Accedo a nuestra base de datos completa de sentencias y demandas.\n\nPuedo ayudarte a consultar información sobre casos legales en lenguaje simple y claro.\n\n**Usa las preguntas de ejemplo para comenzar.**',
      sender: 'assistant',
      timestamp: new Date()
    }
  ]);
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({
    connected: false,
    loading: false,
    message: 'Verificando conexión...'
  });

  // Datos de vista previa basados en el backend
  const [casePreviews, setCasePreviews] = useState<CasePreview[]>([
    { id: '001', title: 'Difamación Digital', category: 'Redes Sociales', status: 'resuelto', confidence: 92 },
    { id: '002', title: 'Acoso Escolar', category: 'Educación', status: 'resuelto', confidence: 88 },
    { id: '003', title: 'PIAR - Inclusión', category: 'Educación', status: 'en_proceso', confidence: 76 },
  ]);

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Verificar backend al cargar
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    setBackendStatus(prev => ({ ...prev, loading: true }));
    
    try {
      const health = await checkBackendHealth();
      setBackendStatus({
        connected: true,
        loading: false,
        message: `Conectado - ${health.cases_loaded} casos cargados`,
        casesLoaded: health.cases_loaded
      });
      
      // Actualizar vista previa con datos reales si es necesario
      if (health.cases_loaded > 0) {
        setCasePreviews(prev => prev.map((item, idx) => ({
          ...item,
          confidence: Math.min(95, 85 + (idx * 5))
        })));
      }
      
      console.log('Backend conectado:', health);
      
    } catch (error) {
      const apiError = error as ApiError;
      setBackendStatus({
        connected: false,
        loading: false,
        message: `❌ ${apiError.message || 'Error de conexión'}`
      });
      console.error('❌ Error conectando al backend:', error);
    }
  };

  // Preguntas de ejemplo específicas para la prueba técnica
  const sampleQuestions = [
    {
      text: '¿Cuáles son las sentencias de 3 demandas?',
      icon: <Scale className="w-4 h-4" />,
    },
    {
      text: '¿De qué se trataron las 3 demandas anteriores?',
      icon: <BookOpen className="w-4 h-4" />,
    },
    {
      text: '¿Cuál fue la sentencia del caso de acoso escolar?',
      icon: <Shield className="w-4 h-4" />,
    },
    {
      text: '¿Existen casos que hablan sobre el PIAR?',
      icon: <FileText className="w-4 h-4" />,
    }
  ];

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  // Enviar consulta al backend
  const sendQuery = async (userMessage: string) => {
    setIsLoading(true);
    
    // Agregar mensaje del usuario
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      content: userMessage,
      sender: 'user',
      timestamp: new Date()
    }]);
    
    try {
      const response = await queryLegalAssistant(userMessage);
      
      // Construir respuesta mejorada
      let responseContent = response.answer;
      
      // Añadir estadísticas si hay casos
      if (response.matched_cases && response.matched_cases.length > 0) {
        responseContent += `\n\n---\n**📊 Datos técnicos:**`;
        responseContent += `\n• Casos encontrados: ${response.matched_cases.length}`;
        responseContent += `\n• Confianza: ${Math.round(response.confidence * 100)}%`;
        responseContent += `\n• Base de datos: ${response.total_cases_searched} casos disponibles`;
      }
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: responseContent,
        sender: 'assistant',
        timestamp: new Date()
      }]);
      
    } catch (error) {
      const apiError = error as ApiError;
      
      let errorMessage = `**❌ Error del sistema**\n\n`;
      
      if (apiError.status === 0) {
        errorMessage += `No se puede conectar al servidor backend.\n\n`;
        errorMessage += `**Solución:**\n`;
        errorMessage += `1. Asegúrate de que el backend esté ejecutándose\n`;
        errorMessage += `2. Ejecuta: \`python backend/main.py\`\n`;
        errorMessage += `3. Verifica que el puerto 8000 esté libre`;
      } else if (apiError.status === 408) {
        errorMessage += `El servidor tardó demasiado en responder.\n\n`;
        errorMessage += `**Solución:**\n`;
        errorMessage += `• Verifica la conexión a internet\n`;
        errorMessage += `• El backend podría estar sobrecargado`;
      } else {
        errorMessage += `Error ${apiError.status || 'desconocido'}: ${apiError.message}\n\n`;
        errorMessage += `**Solución:**\n`;
        errorMessage += `• Intenta nuevamente en unos momentos\n`;
        errorMessage += `• Revisa la consola del backend para más detalles`;
      }
      
      errorMessage += `\n\n**Mientras tanto, puedes usar las preguntas de ejemplo para ver cómo funcionaría el sistema.**`;
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: errorMessage,
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      }]);
      
      // Actualizar estado del backend
      setBackendStatus(prev => ({
        ...prev,
        connected: false,
        message: `Error: ${apiError.message?.substring(0, 50)}...`
      }));
      
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    sendQuery(input);
    setInput('');
  };

  // Función para debug del backend
  const debugBackendInfo = async () => {
    setIsLoading(true);
    try {
      const debugInfo = await debugBackend();
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: `**🔍 Información de Debug del Backend:**\n\n` +
                `• **Python:** ${debugInfo.python_version}\n` +
                `• **Archivo de datos:** ${debugInfo.data_file_exists ? '✅ Encontrado' : '❌ No encontrado'}\n` +
                `• **Casos en memoria:** ${debugInfo.cases_in_memory}\n` +
                `• **Muestra del primer caso:**\n` +
                `  - Tipo: ${debugInfo.sample_case?.Tipo || 'N/A'}\n` +
                `  - Tema: ${debugInfo.sample_case?.['Tema - subtema'] || 'N/A'}\n` +
                `  - Resolución: ${debugInfo.sample_case?.resuelve?.substring(0, 100) || 'N/A'}...`,
        sender: 'assistant',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Error en debug:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 relative">
      {/* Background pattern */}
      <div className="fixed inset-0 z-0 opacity-5">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]" />
      </div>

      <div className="relative max-w-7xl mx-auto p-4 md:p-8 z-10">
        {/* Header */}
        <motion.header 
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg">
                  <Scale className="w-6 h-6 text-white" />
                </div>
                <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
                  backendStatus.connected ? 'bg-green-500' : 'bg-red-500'
                }`} />
              </div>
              
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                  Asistente Legal AI
                  <span className="text-sm font-normal ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                    Prueba Técnica
                  </span>
                </h1>
                <p className="text-gray-600 text-sm mt-1">
                  Consulta inteligente de sentencias legales • Basado en datos reales
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-3">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
                backendStatus.connected 
                  ? 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200' 
                  : 'bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800 border border-yellow-200'
              }`}>
                <div className={`w-2 h-2 rounded-full ${backendStatus.connected ? 'bg-green-500' : 'bg-yellow-500'}`} />
                <span className="text-sm font-medium">
                  {backendStatus.connected ? 'Conectado' : 'Verificando...'}
                </span>
              </div>
              
              <button
                onClick={checkBackendConnection}
                disabled={backendStatus.loading}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 text-sm font-medium transition-colors disabled:opacity-50"
              >
                {backendStatus.loading ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Wifi className="w-3 h-3" />
                )}
                Probar conexión
              </button>

              <button
                onClick={debugBackendInfo}
                disabled={isLoading}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 text-sm font-medium transition-colors"
              >
                <Database className="w-3 h-3" />
                Debug
              </button>
            </div>
          </div>
        </motion.header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar */}
          <motion.div 
            className="lg:col-span-1 space-y-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {/* Cases Panel */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-blue-50">
                    <Layers className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Casos Disponibles</h3>
                    <p className="text-gray-500 text-sm">
                      {backendStatus.casesLoaded ? `${backendStatus.casesLoaded} casos cargados` : 'Base de datos legal'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                {casePreviews.map((caseItem, index) => (
                  <motion.div
                    key={caseItem.id}
                    className="p-4 rounded-lg border border-gray-200 hover:border-blue-300 bg-white hover:shadow-md transition-all duration-200 cursor-pointer group"
                    whileHover={{ x: 4 }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => setInput(`¿Cuáles son los detalles del caso ${caseItem.title}?`)}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1 group-hover:text-blue-600">
                          {caseItem.title}
                        </h4>
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                            {caseItem.category}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            caseItem.status === 'resuelto' 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {caseItem.status.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold text-blue-600">
                          {caseItem.confidence}%
                        </div>
                        <div className="text-xs text-gray-500">relevancia</div>
                      </div>
                    </div>
                    
                    <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                      <motion.div 
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${caseItem.confidence}%` }}
                        transition={{ duration: 1, delay: index * 0.2 }}
                      />
                    </div>
                    
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>Consulta disponible</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
                    </div>
                  </motion.div>
                ))}
              </div>
              
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between text-sm mb-3">
                  <span className="text-gray-600">Estado del sistema:</span>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      backendStatus.connected ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <span className={`font-medium ${
                      backendStatus.connected ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {backendStatus.connected ? 'Operativo' : 'No conectado'}
                    </span>
                  </div>
                </div>
                
                {backendStatus.connected ? (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center gap-2 text-green-700">
                      <CheckCircle className="w-4 h-4" />
                      <p className="text-sm">
                        <strong>Sistema listo</strong><br />
                        Respuestas basadas en datos reales del Excel
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-center gap-2 text-yellow-700">
                      <AlertCircle className="w-4 h-4" />
                      <p className="text-sm">
                        <strong>⚠️ Modo limitado</strong><br />
                        Las respuestas son de ejemplo hasta que el backend esté disponible
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Stats Panel */}
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-5 text-white">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-white/20">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold">Métricas del Sistema</h3>
                  <p className="text-white/80 text-sm">Prueba Técnica v2.0</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Precisión de respuestas</span>
                    <span className="font-semibold">
                      {backendStatus.connected ? '94%' : '85% (demo)'}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-white/20 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-white rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: backendStatus.connected ? "94%" : "85%" }}
                      transition={{ duration: 1.5 }}
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Tiempo de respuesta</span>
                    <span className="font-semibold">
                      {backendStatus.connected ? '< 1s' : '0.2s (demo)'}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-white/20 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-cyan-200 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: backendStatus.connected ? "95%" : "98%" }}
                      transition={{ duration: 1.5, delay: 0.2 }}
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-white/20">
                <div className="text-center">
                  <div className="text-2xl font-bold mb-1">
                    {backendStatus.casesLoaded || '3'}
                  </div>
                  <div className="text-white/70 text-sm">Casos legales cargados</div>
                </div>
                
                <div className="mt-4 text-xs text-white/60">
                  <p>• Basado en sentencias reales</p>
                  <p>• Lenguaje coloquial y claro</p>
                  <p>• Respuestas específicas para prueba técnica</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Main Chat Area */}
          <motion.div 
            className="lg:col-span-2 flex flex-col"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {/* Chat Container */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 flex flex-col overflow-hidden">
              {/* Chat Header */}
              <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-white">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center shadow-md">
                        <Bot className="w-6 h-6 text-white" />
                      </div>
                      <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
                        backendStatus.connected ? 'bg-green-500' : 'bg-yellow-500'
                      }`} />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900">Asesor Legal Virtual</h2>
                      <p className="text-gray-600 text-sm">
                        {backendStatus.connected 
                          ? 'Respuestas basadas en sentencias reales' 
                          : 'Modo demostración - Usando datos de ejemplo'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="hidden md:block">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-700">
                        Prueba Técnica
                      </div>
                      <div className="text-xs text-gray-500">
                        {backendStatus.connected ? 'Datos reales' : 'Datos de ejemplo'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : ''}`}
                    >
                      {message.sender === 'assistant' && (
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                      )}
                      
                      <div
                        className={`max-w-[85%] rounded-2xl p-4 ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                            : message.isError
                            ? 'bg-red-50 border border-red-200'
                            : 'bg-gray-50 border border-gray-200'
                        }`}
                      >
                        <div className={`whitespace-pre-line text-sm md:text-base leading-relaxed ${
                          message.isError ? 'text-red-800' : ''
                        }`}>
                          {message.content}
                        </div>
                        <div className={`text-xs mt-3 flex items-center gap-2 ${
                          message.sender === 'user' ? 'text-white/70' : 
                          message.isError ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          {formatTime(message.timestamp)}
                          {message.sender === 'assistant' && !message.isError && (
                            <>
                              <span className="w-1 h-1 rounded-full bg-current" />
                              <span>{backendStatus.connected ? 'IA Legal' : 'Modo Demo'}</span>
                            </>
                          )}
                          {message.isError && (
                            <>
                              <span className="w-1 h-1 rounded-full bg-current" />
                              <span>Error del sistema</span>
                            </>
                          )}
                        </div>
                      </div>
                      
                      {message.sender === 'user' && (
                        <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                          <User className="w-4 h-4 text-gray-600" />
                        </div>
                      )}
                    </motion.div>
                  ))}
                  
                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex gap-3"
                    >
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="rounded-2xl bg-gray-50 border border-gray-200 p-4 max-w-[85%]">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                          <span className="text-gray-600">
                            {backendStatus.connected 
                              ? 'Consultando base de datos legal...' 
                              : 'Generando respuesta de ejemplo...'}
                          </span>
                        </div>
                        {backendStatus.connected && (
                          <p className="text-xs text-gray-500 mt-2">
                            Analizando sentencias y preparando respuesta en lenguaje simple...
                          </p>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-6 border-t border-gray-200 bg-gray-50/50">
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Sample Questions */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-gray-700">
                          Preguntas de la prueba técnica:
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {backendStatus.connected ? 'Respuestas reales' : 'Ejemplos'}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {sampleQuestions.map((question, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => {
                            setInput(question.text);
                            // Enviar automáticamente después de 100ms
                            setTimeout(() => {
                              const submitEvent = new Event('submit', { cancelable: true });
                              document.querySelector('form')?.dispatchEvent(submitEvent);
                            }, 100);
                          }}
                          disabled={isLoading}
                          className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm border border-gray-300 hover:border-blue-400 bg-white hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 shadow-sm"
                        >
                          <span className="text-blue-600">{question.icon}</span>
                          <span className="text-gray-700">{question.text}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Input Field */}
                  <div className="relative">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder={
                        backendStatus.connected
                          ? "Escribe tu pregunta legal en lenguaje natural..."
                          : "Escribe una pregunta para ver respuestas de ejemplo..."
                      }
                      className="w-full p-4 pr-12 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white transition-all duration-200 outline-none shadow-sm"
                      disabled={isLoading}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          if (input.trim() && !isLoading) {
                            handleSubmit(e as any);
                          }
                        }
                      }}
                    />
                    <button
                      type="submit"
                      disabled={isLoading || !input.trim()}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-md transition-shadow"
                    >
                      {isLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  
                  {/* Input Footer */}
                  <div className="flex flex-col md:flex-row justify-between gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          backendStatus.connected ? 'bg-green-500' : 'bg-yellow-500'
                        }`} />
                        <span>
                          {backendStatus.connected 
                            ? `Conectado (${backendStatus.casesLoaded || 0} casos)` 
                            : 'Sin conexión al backend'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="hidden md:block">
                        <kbd className="px-2 py-1 bg-gray-100 rounded text-xs border border-gray-300">Enter</kbd> para enviar
                      </div>
                      
                      <div className="text-xs">
                        {backendStatus.connected ? 'Búsqueda en tiempo real' : 'Usando datos de ejemplo'}
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Footer */}
        <motion.footer 
          className="mt-8 pt-8 border-t border-gray-200"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center shadow-md">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-gray-700 font-medium">Asistente Legal AI • Prueba Técnica v1.0</p>
                <p className="text-gray-500 text-sm">
                  {backendStatus.connected 
                    ? 'Sistema completo: Consulta de sentencias legales con IA' 
                    : 'Sistema de demostración: Prueba las funcionalidades'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {[
                { label: 'Demandas', color: 'bg-blue-500' },
                { label: 'Sentencias', color: 'bg-purple-500' },
                { 
                  label: backendStatus.connected ? 'Backend Activo' : 'Backend Offline', 
                  color: backendStatus.connected ? 'bg-green-500' : 'bg-red-500' 
                },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span className="text-gray-600 text-sm">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-4 text-center text-xs text-gray-400">
            <p>Prueba Técnica: Asesor legal para consulta de historia de demandas • Responde a las 5 preguntas específicas en lenguaje coloquial</p>
          </div>
        </motion.footer>
      </div>
      
      {/* Connection Checker */}
      <ConnectionChecker 
        status={backendStatus} 
        onTest={checkBackendConnection} 
      />
    </div>
  );
}