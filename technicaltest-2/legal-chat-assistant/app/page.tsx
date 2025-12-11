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
  Zap,
  MessageSquare,
  FileText,
  Shield,
  Search,
  Clock,
  Layers
} from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface CasePreview {
  id: string;
  title: string;
  category: string;
  status: 'resuelto' | 'en_proceso' | 'archivado';
  confidence: number;
}

export default function LegalChatAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '¡Hola! Soy tu asistente legal especializado. Accedo a nuestra base completa de historial de demandas y puedo explicarte sentencias en lenguaje comprensible. ¿En qué caso necesitas asesoría hoy?',
      sender: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Mock data for case previews
  const casePreviews: CasePreview[] = [
    { id: '001', title: 'Difamación en Facebook', category: 'Redes Sociales', status: 'resuelto', confidence: 92 },
    { id: '002', title: 'Acoso Escolar Digital', category: 'Educación', status: 'resuelto', confidence: 88 },
    { id: '003', title: 'PIAR - Protocolo Escolar', category: 'Educación', status: 'en_proceso', confidence: 76 },
  ];

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sample questions
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

  // Función para formatear hora consistentemente
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  // API response
  const sendQuery = async (userMessage: string) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage })
      });
      
      const data = await response.json();
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: data.answer,
        sender: 'assistant',
        timestamp: new Date()
      }]);
      
    } catch (error) {
      console.error('Error querying backend:', error);
      // Fallback to mock response if backend fails
      // ... (keep your existing mock response logic)
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      content: userMessage,
      sender: 'user',
      timestamp: new Date()
    }]);
    setInput('');

    sendQuery(userMessage);
  };

  return (
    <div className="min-h-screen bg-[#f7f7f7]">
      {/* Minimal background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-[#3e32a9]/5 to-[#46a8b9]/5" />
        <div className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-[#3e32a9]/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full bg-[#46a8b9]/10 blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto p-4 md:p-8">
        {/* Professional Header */}
        <motion.header 
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Logo */}
              <motion.div 
                className="relative"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="w-12 h-12 rounded-lg bg-white border border-gray-200 shadow-sm flex items-center justify-center">
                  <div className="text-[#3e32a9] font-semibold text-lg">L</div>
                </div>
              </motion.div>
              
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">Asistente Legal AI</h1>
                <p className="text-gray-600 text-sm">Consulta de historial de demandas • Análisis con IA</p>
              </div>
            </div>
            
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-gray-200">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-sm font-medium text-gray-700">Sistema activo</span>
              </div>
            </div>
          </div>
        </motion.header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar - Minimal Case Previews */}
          <motion.div 
            className="lg:col-span-1 space-y-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {/* Cases Panel */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-[#3e32a9]/10">
                  <Layers className="w-5 h-5 text-[#3e32a9]" />
                </div>
                <h3 className="font-semibold text-gray-900">Casos Destacados</h3>
              </div>
              
              <div className="space-y-4">
                {casePreviews.map((caseItem, index) => (
                  <motion.div
                    key={caseItem.id}
                    className="p-4 rounded-lg border border-gray-200 hover:border-[#3e32a9]/30 bg-white hover:shadow-sm transition-all duration-200 cursor-pointer"
                    whileHover={{ x: 4 }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => setInput(`Detalles del caso ${caseItem.title}`)}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-1">{caseItem.title}</h4>
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                            {caseItem.category}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            caseItem.status === 'resuelto' ? 'bg-green-100 text-green-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {caseItem.status}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold text-[#3e32a9]">{caseItem.confidence}%</div>
                      </div>
                    </div>
                    
                    <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                      <motion.div 
                        className="h-full bg-gradient-to-r from-[#3e32a9] to-[#46a8b9] rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${caseItem.confidence}%` }}
                        transition={{ duration: 1, delay: index * 0.2 }}
                      />
                    </div>
                    
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>Disponible</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Stats Panel */}
            <div className="bg-gradient-to-br from-[#3e32a9] to-[#46a8b9] rounded-xl p-5 text-white">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-white/20">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold">Rendimiento IA</h3>
                  <p className="text-white/80 text-sm">Métricas del sistema</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Precisión</span>
                    <span className="font-semibold">94.5%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/20 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-white rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: "94.5%" }}
                      transition={{ duration: 1.5 }}
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Velocidad</span>
                    <span className="font-semibold">0.8s</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/20 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-cyan-200 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: "90%" }}
                      transition={{ duration: 1.5, delay: 0.2 }}
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-white/20 text-center">
                <div className="text-xl font-semibold mb-1">158</div>
                <div className="text-white/70 text-sm">Casos analizados</div>
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
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-[#3e32a9] to-[#46a8b9] flex items-center justify-center">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-green-500 border-2 border-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">Asesor Legal Virtual</h2>
                    <p className="text-gray-600 text-sm">Respuestas en lenguaje claro y accesible</p>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                <AnimatePresence>
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : ''}`}
                    >
                      {message.sender === 'assistant' && (
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-[#3e32a9] to-[#46a8b9] flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                      )}
                      
                      <div
                        className={`max-w-[80%] rounded-2xl p-4 ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-r from-[#3e32a9] to-[#46a8b9] text-white'
                            : 'bg-gray-50 border border-gray-200'
                        }`}
                      >
                        <div className="whitespace-pre-line text-sm md:text-base leading-relaxed">
                          {message.content}
                        </div>
                        <div className={`text-xs mt-3 ${
                          message.sender === 'user' ? 'text-white/70' : 'text-gray-500'
                        }`}>
                          {formatTime(message.timestamp)}
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
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-[#3e32a9] to-[#46a8b9] flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="rounded-2xl bg-gray-50 border border-gray-200 p-4 max-w-[80%]">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 text-[#3e32a9] animate-spin" />
                          <span className="text-gray-600">Analizando casos...</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-6 border-t border-gray-200">
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Sample Questions */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <MessageSquare className="w-4 h-4 text-[#3e32a9]" />
                      <span className="text-sm font-medium text-gray-700">Preguntas de ejemplo:</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {sampleQuestions.map((question, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => setInput(question.text)}
                          className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm border border-gray-300 hover:border-[#3e32a9]/30 bg-white hover:bg-gray-50 transition-all duration-200"
                        >
                          <span className="text-[#3e32a9]">{question.icon}</span>
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
                      placeholder="Escribe tu pregunta sobre demandas o sentencias..."
                      className="w-full p-4 pr-12 rounded-xl border border-gray-300 focus:border-[#3e32a9] focus:ring-2 focus:ring-[#3e32a9]/20 bg-white transition-all duration-200 outline-none"
                      disabled={isLoading}
                    />
                    <button
                      type="submit"
                      disabled={isLoading || !input.trim()}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-lg bg-gradient-to-r from-[#3e32a9] to-[#46a8b9] text-white disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  
                  {/* Input Footer */}
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span>Conectado</span>
                      </div>
                    </div>
                    <div className="hidden md:block">
                      <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Enter</kbd> para enviar
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Minimal Footer */}
        <motion.footer 
          className="mt-8 pt-8 border-t border-gray-200"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <p className="text-gray-700 font-medium">Asistente Legal AI • Prueba de Concepto</p>
              <p className="text-gray-500 text-sm">Consultoría legal automatizada con IA generativa</p>
            </div>
            
            <div className="flex items-center gap-4">
              {[
                { label: 'Demandas', color: 'bg-[#3e32a9]' },
                { label: 'Sentencias', color: 'bg-[#46a8b9]' },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span className="text-gray-600 text-sm">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.footer>
      </div>
    </div>
  );
}