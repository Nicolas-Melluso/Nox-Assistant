import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

export default function App() {
  const [apiUrl, setApiUrl] = useState('http://localhost:5000');
  const [status, setStatus] = useState({
    running: false,
    listening: false,
    connected_clients: 0,
    last_wake: '',
    last_partial: '',
    last_command: '',
    last_event_at: 0,
    voice_device: '',
    voice_sample_rate: '',
    voice_last_error: '',
  });
  const [voiceFeedback, setVoiceFeedback] = useState({
    phase: 'idle',
    text: 'Sin actividad de voz',
  });
  const [logs, setLogs] = useState([]);
  const [command, setCommand] = useState('');
  const [autoConfirm, setAutoConfirm] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const wsRef = useRef(null);
  const logsEndRef = useRef(null);

  // Inicializar WebSocket y cargar URL de API
  useEffect(() => {
    const initApi = async () => {
      if (window.electron?.getApiUrl) {
        const url = await window.electron.getApiUrl();
        setApiUrl(url);
        connectWebSocket(url);
      } else {
        connectWebSocket(apiUrl);
      }
    };

    initApi();
    fetchStatus();
    const statusInterval = setInterval(fetchStatus, 2000);
    return () => clearInterval(statusInterval);
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const connectWebSocket = (url) => {
    const wsUrl = url.replace('http', 'ws') + '/ws';
    try {
      wsRef.current = new WebSocket(wsUrl);
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketEvent(data);
      };
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Could not connect WebSocket:', error);
    }
  };

  const handleWebSocketEvent = (data) => {
    const { type, data: eventData } = data;

    switch (type) {
      case 'voice_wake':
        setVoiceFeedback({ phase: 'wake', text: `Wake word detectada: ${eventData.text}` });
        addLog({ stage: 'WAKE', text: eventData.text, level: 'info' });
        break;
      case 'voice_partial':
        setVoiceFeedback({ phase: 'partial', text: `Escuchando: ${eventData.text}` });
        addLog({ stage: 'PARTIAL', text: eventData.text, level: 'info' });
        break;
      case 'voice_command':
        setVoiceFeedback({ phase: 'command', text: `Comando detectado: ${eventData.command}` });
        addLog({ stage: 'COMMAND', text: eventData.command, level: 'success' });
        break;
      case 'voice_result':
        setVoiceFeedback({ phase: 'result', text: 'Respuesta generada. Volviendo a escucha...' });
        addLog({ stage: 'RESPONSE', text: eventData.message, level: 'success' });
        break;
      case 'listening':
        setVoiceFeedback({ phase: 'listening', text: 'Micrófono activo. Esperando wake word...' });
        addLog({ stage: 'STATUS', text: 'Escuchando...', level: 'info' });
        break;
      case 'error':
        setVoiceFeedback({ phase: 'error', text: eventData.message || 'Error en servicio de voz' });
        addLog({ stage: 'ERROR', text: eventData.message, level: 'error' });
        break;
      default:
        break;
    }
  };

  const addLog = (log) => {
    setLogs((prev) => [...prev, { ...log, id: Date.now() }]);
  };

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/status`);
      setStatus(response.data);

      if (response.data.last_partial) {
        setVoiceFeedback({ phase: 'partial', text: `Escuchando: ${response.data.last_partial}` });
      } else if (response.data.last_command) {
        setVoiceFeedback({ phase: 'command', text: `Último comando: ${response.data.last_command}` });
      } else if (response.data.last_wake) {
        setVoiceFeedback({ phase: 'wake', text: `Wake detectada: ${response.data.last_wake}` });
      } else if (response.data.voice_last_error) {
        setVoiceFeedback({ phase: 'error', text: `Error de voz: ${response.data.voice_last_error}` });
      } else if (response.data.listening) {
        setVoiceFeedback({ phase: 'listening', text: 'Micrófono activo. Esperando wake word...' });
      } else if (!response.data.running) {
        setVoiceFeedback({ phase: 'idle', text: 'Servicio de voz detenido' });
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const startVoice = async () => {
    try {
      await axios.post(`${apiUrl}/api/voice/start`);
      addLog({ stage: 'STATUS', text: 'Servicio de voz iniciado', level: 'success' });
    } catch (error) {
      addLog({ stage: 'ERROR', text: error.message, level: 'error' });
    }
  };

  const stopVoice = async () => {
    try {
      await axios.post(`${apiUrl}/api/voice/stop`);
      addLog({ stage: 'STATUS', text: 'Servicio de voz detenido', level: 'warning' });
    } catch (error) {
      addLog({ stage: 'ERROR', text: error.message, level: 'error' });
    }
  };

  const executeCommand = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;

    setIsProcessing(true);
    try {
      const response = await axios.post(`${apiUrl}/api/command`, {
        command: command,
        auto_confirm: autoConfirm,
      });

      addLog({
        stage: 'COMMAND',
        text: command,
        level: 'success',
      });

      addLog({
        stage: 'RESPONSE',
        text: response.data.message,
        level: 'success',
      });

      if (response.data.tools_used.length > 0) {
        addLog({
          stage: 'TOOLS',
          text: response.data.tools_used.join(', '),
          level: 'info',
        });
      }

      setCommand('');
    } catch (error) {
      addLog({
        stage: 'ERROR',
        text: error.response?.data?.detail || error.message,
        level: 'error',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getLevelClass = (level) => {
    const levels = {
      info: 'log-info',
      success: 'log-success',
      warning: 'log-warning',
      error: 'log-error',
    };
    return levels[level] || 'log-info';
  };

  const feedbackClass = `voice-feedback voice-${voiceFeedback.phase}`;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎙️ NOX Desktop</h1>
          <div className="status-badge">
            <span
              className={`status-dot ${status.listening ? 'listening' : ''} ${
                status.running ? 'running' : ''
              }`}
            />
            {status.listening ? 'Escuchando' : status.running ? 'Activo' : 'Inactivo'}
          </div>
        </div>
        <div className="header-actions">
          {!status.running ? (
            <button onClick={startVoice} className="btn btn-primary">
              ▶️ Iniciar Voz
            </button>
          ) : (
            <button onClick={stopVoice} className="btn btn-danger">
              ⏹️ Detener
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        <section className="logs-section">
          <div className="logs-header">
            <h2>📋 Actividad</h2>
            <button
              onClick={() => setLogs([])}
              className="btn btn-small"
            >
              Limpiar
            </button>
          </div>
          <div className="logs-container">
            {logs.map((log) => (
              <div key={log.id} className={`log-entry ${getLevelClass(log.level)}`}>
                <span className="log-stage">[{log.stage}]</span>
                <span className="log-text">{log.text}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </section>

        <section className="command-section">
          <h3>💬 Comando Manual</h3>

          <div className={feedbackClass}>
            <div className="voice-feedback-title">Feedback de voz</div>
            <div className="voice-feedback-text">{voiceFeedback.text}</div>
            <div className="voice-feedback-meta">
              wake: {status.last_wake || '-'} | parcial: {status.last_partial || '-'}
            </div>
            <div className="voice-feedback-meta">
              mic: {String(status.voice_device || 'default')} @ {String(status.voice_sample_rate || 'auto')} Hz
            </div>
            {status.voice_last_error ? (
              <div className="voice-feedback-meta" style={{ color: '#ef4444' }}>
                error: {status.voice_last_error}
              </div>
            ) : null}
          </div>

          <form onSubmit={executeCommand} className="command-form">
            <div className="form-group">
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Escribe un comando..."
                disabled={isProcessing}
                className="command-input"
              />
              <button
                type="submit"
                disabled={isProcessing || !command.trim()}
                className="btn btn-primary"
              >
                {isProcessing ? '⏳ Procesando...' : '📤 Enviar'}
              </button>
            </div>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={autoConfirm}
                onChange={(e) => setAutoConfirm(e.target.checked)}
              />
              Auto-confirmar acciones
            </label>
          </form>
        </section>
      </main>

      <footer className="app-footer">
        <div className="footer-info">
          <small>API: {apiUrl}</small>
          <small>Clientes: {status.connected_clients}</small>
        </div>
      </footer>
    </div>
  );
}
