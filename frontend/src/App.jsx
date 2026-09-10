import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Send, FileText, UploadCloud, Info, BookOpen, AlertCircle, 
  Search, CheckCircle, ChevronDown, ChevronUp, Play, Pause, 
  SkipForward, List, Settings, Database, Activity, FileCheck,
  ThumbsUp, ThumbsDown, User, MessageSquare, Plus, CheckCircle2,
  Clock, Hash, DollarSign
} from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [docUploaded, setDocUploaded] = useState(false);
  const [docName, setDocName] = useState('');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // To mock the advanced data since backend only returns basic sources/metrics
  const [currentSources, setCurrentSources] = useState([]);
  const [currentMetrics, setCurrentMetrics] = useState(null);
  
  // Pipeline state
  const [showPipeline, setShowPipeline] = useState(false);
  const [pipelineExpandedStep, setPipelineExpandedStep] = useState(3); // Default expand step 3 (Dense)

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, showPipeline]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setDocUploaded(true);
      setDocName(response.data.doc_name);
      setMessages([
        {
          role: 'assistant',
          content: `The document **${response.data.doc_name}** has been successfully uploaded and indexed. You can now ask questions about it.`,
          isWelcome: true
        }
      ]);
      setCurrentSources([]);
      setCurrentMetrics(null);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to process document. Make sure the backend is running.');
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const newMessages = [...messages, { role: 'user', content: inputMessage }];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        question: inputMessage,
      });

      const advanced = response.data.advanced || {};
      const trace = response.data.trace || {};
      
      setMessages([
        ...newMessages,
        { 
          role: 'assistant', 
          content: response.data.answer,
          sources: response.data.sources || [],
          advanced: advanced,
          trace: trace
        },
      ]);
      setCurrentSources(response.data.sources || []);
      setCurrentMetrics(advanced);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([
        ...newMessages,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="dashboard">
      {/* LEFT SIDEBAR */}
      <div className="sidebar-left">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="brand-text">
            <h2>DocIntell</h2>
            <p>AI Document Intelligence</p>
          </div>
        </div>

        <div className="sidebar-nav">
          <button className="nav-item">
            <FileText size={18} /> Documents
          </button>
          <button className="nav-item active">
            <MessageSquare size={18} /> Ask Documents
          </button>
          <button className="nav-item">
            <Search size={18} /> RAG Inspector
          </button>
          <button className="nav-item">
            <Activity size={18} /> Evaluation Lab
          </button>
          <button className="nav-item">
            <FileCheck size={18} /> Experiments (A/B)
          </button>
          <button className="nav-item">
            <Settings size={18} /> Settings
          </button>
        </div>

        <div className="system-status">
          <div className="status-row">
            <span className="status-label">System Status</span>
            <span className="status-value"><div className="status-dot"></div> Online</span>
          </div>
          <div className="status-row">
            <span className="status-label">LLM</span>
            <span className="status-value"><div className="status-dot"></div> OpenAI GPT-4o</span>
          </div>
          <div className="status-row">
            <span className="status-label">Embeddings</span>
            <span className="status-value"><div className="status-dot"></div> text-embedding-3-s</span>
          </div>
          <div className="status-row">
            <span className="status-label">Vector DB</span>
            <span className="status-value"><div className="status-dot"></div> Chroma</span>
          </div>
          <div className="status-row">
            <span className="status-label">Reranker</span>
            <span className="status-value"><div className="status-dot"></div> bge-reranker-base</span>
          </div>
          <div className="status-row">
            <span className="status-label">BM25</span>
            <span className="status-value"><div className="status-dot"></div> Enabled</span>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-content">
        <div className="main-header">
          <div className="header-title">
            <h1>Ask Documents</h1>
            <p>Upload documents, ask questions, and get grounded answers with citations.</p>
          </div>
          <div className="header-actions">
            <input
              type="file"
              accept=".pdf"
              ref={fileInputRef}
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <button className="btn-upload" onClick={() => fileInputRef.current.click()}>
              <Plus size={16} /> Upload Documents
            </button>
            <div className="user-avatar">S</div>
          </div>
        </div>

        <div className="chat-scroll-area">
          {!docUploaded && messages.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '10vh', color: 'var(--text-secondary)' }}>
              <UploadCloud size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
              <h2>No Document Uploaded</h2>
              <p>Please upload a PDF document to begin asking questions.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className="message-row">
              <div className={`avatar ${msg.role}`}>
                {msg.role === 'user' ? <User size={20} /> : <div className="brand-icon" style={{width:'36px', height:'36px'}}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/></svg></div>}
              </div>
              
              <div className="message-content">
                <div className="message-bubble" style={{ backgroundColor: msg.role === 'user' ? '#f8fafc' : 'white' }}>
                  <div className="message-header">
                    <span className="timestamp">{new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </div>
                  
                  <div className="message-text">
                    {msg.content}
                    {msg.role === 'assistant' && !msg.isWelcome && msg.sources && msg.sources.length > 0 && (
                      <span>
                        {' '}
                        {msg.sources.map((s, i) => (
                          <span key={i} className="citation-tag">[{i + 1}]</span>
                        ))}
                      </span>
                    )}
                  </div>

                  {msg.role === 'assistant' && !msg.isWelcome && msg.advanced && (
                    <>
                      <div className="assistant-metrics">
                        <div className="badge-evidence">
                          <CheckCircle2 size={14} /> Evidence: {msg.advanced.evidenceCheck}
                        </div>
                        <div className="metric-pill">
                          <FileText size={14} /> Sources: {msg.sources?.length || 0}
                        </div>
                        <div className="metric-pill">
                          <Clock size={14} /> Latency: {msg.advanced.latency}
                        </div>
                        <div className="metric-pill">
                          <Hash size={14} /> Tokens: {msg.advanced.tokens}
                        </div>
                        <div className="metric-pill">
                          <DollarSign size={14} /> Est. Cost: {msg.advanced.cost}
                        </div>
                      </div>

                      <div className="assistant-actions">
                        <button className="btn-action">
                          <List size={16} /> View Sources
                        </button>
                        <button className={`btn-action ${showPipeline ? 'active' : ''}`} onClick={() => setShowPipeline(!showPipeline)}>
                          <Activity size={16} /> View RAG Pipeline
                        </button>
                        <button className="btn-icon"><ThumbsUp size={16} /></button>
                        <button className="btn-icon"><ThumbsDown size={16} /></button>
                      </div>

                      {/* RAG PIPELINE TRACE PANEL */}
                      {showPipeline && (
                        <div className="pipeline-panel">
                          <div className="pipeline-header">
                            <div className="pipeline-title">
                              <List size={18} /> RAG Pipeline (Execution Trace)
                              <span className="badge-completed"><CheckCircle2 size={12} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'2px'}}/> Completed</span>
                            </div>
                            <div className="pipeline-controls">
                              <button className="btn-play"><Play size={14} /> Play</button>
                              <button className="btn-icon" style={{display:'flex', gap:'4px'}}><Pause size={14}/> Pause</button>
                              <button className="btn-icon" style={{display:'flex', gap:'4px'}}><SkipForward size={14}/> Next</button>
                              <span style={{fontSize:'0.8rem', fontWeight:500, margin:'0 8px'}}>Show All</span>
                              <div style={{display:'flex', alignItems:'center', gap:'4px', fontSize:'0.8rem'}}>
                                <Settings size={14}/> Delay: 10s <ChevronDown size={14}/>
                              </div>
                            </div>
                          </div>

                          <div className="stepper-container">
                            <div className="stepper-line"></div>
                            <div className="stepper-line-progress" style={{width: '100%'}}></div>
                            
                            {['Query', 'Rewrite', 'Dense', 'BM25', 'Fusion', 'Rerank', 'Context', 'Evidence', 'Generation', 'Evaluation'].map((step, idx) => (
                              <div className="step-item" key={idx}>
                                <div className="step-circle">{idx + 1}</div>
                                <div className="step-label">{step}</div>
                                <div className="step-check"><CheckCircle size={14} /></div>
                              </div>
                            ))}
                          </div>

                          {/* Step 3 Detail */}
                          <div className="step-detail-card">
                            <div className="step-detail-header" onClick={() => setPipelineExpandedStep(pipelineExpandedStep === 3 ? null : 3)} style={{cursor: 'pointer'}}>
                              <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                                <Database size={16} /> Step 3: Dense Retrieval 
                                <span className="badge-completed"><CheckCircle2 size={12} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'2px'}}/> Completed</span>
                              </div>
                              <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                                <span style={{fontSize:'0.75rem', fontWeight:'normal'}}>Time: {msg.trace?.timings?.dense_retrieval_ms || 0} ms</span>
                                {pipelineExpandedStep === 3 ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                              </div>
                            </div>
                            {pipelineExpandedStep === 3 && (
                              <div className="step-detail-body">
                                <h4>Top 5 Results (Dense / Vector Search)</h4>
                                <table className="data-table">
                                  <thead>
                                    <tr>
                                      <th>Rank</th>
                                      <th>Document</th>
                                      <th>Page</th>
                                      <th>Chunk ID</th>
                                      <th>Similarity Score</th>
                                      <th>Preview</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {(msg.trace?.dense || []).map((row, i) => (
                                      <tr key={i}>
                                        <td>{row.rank}</td>
                                        <td>{row.doc}</td>
                                        <td>{row.page}</td>
                                        <td>{row.chunk_id}</td>
                                        <td>{row.score}</td>
                                        <td>{row.text}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            )}
                          </div>

                          {/* Dynamic Step Headers & Tables */}
                          {[
                            {id: 4, name: 'BM25 Retrieval', time: `${msg.trace?.timings?.sparse_retrieval_ms || 0} ms`, icon: <Search size={16}/>, data: msg.trace?.sparse},
                            {id: 5, name: 'Result Fusion (RRF)', time: `${msg.trace?.timings?.fusion_ms || 0} ms`, icon: <Activity size={16}/>, data: msg.trace?.fusion},
                            {id: 6, name: 'Reranking (Cross-Encoder)', time: `${msg.trace?.timings?.reranking_ms || 0} ms`, icon: <List size={16}/>, data: msg.trace?.rerank}
                          ].map(step => (
                            <div className="step-detail-card" key={step.id}>
                              <div className={`step-detail-header ${pipelineExpandedStep === step.id ? '' : 'collapsed'}`} onClick={() => setPipelineExpandedStep(pipelineExpandedStep === step.id ? null : step.id)} style={{cursor: 'pointer'}}>
                                <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                                  <span style={{color: 'var(--accent-blue)'}}>{step.icon}</span> Step {step.id}: {step.name} 
                                  <span className="badge-completed"><CheckCircle2 size={12} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'2px'}}/> Completed</span>
                                </div>
                                <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                                  <span style={{fontSize:'0.75rem', fontWeight:'normal', color: 'var(--text-secondary)'}}>Time: {step.time}</span>
                                  {pipelineExpandedStep === step.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </div>
                              </div>
                              {pipelineExpandedStep === step.id && (
                                <div className="step-detail-body">
                                  <table className="data-table">
                                    <thead>
                                      <tr>
                                        <th>Rank</th>
                                        <th>Document</th>
                                        <th>Page</th>
                                        <th>Chunk ID</th>
                                        <th>Score</th>
                                        <th>Preview</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {(step.data || []).map((row, i) => (
                                        <tr key={i}>
                                          <td>{row.rank}</td>
                                          <td>{row.doc}</td>
                                          <td>{row.page}</td>
                                          <td>{row.chunk_id}</td>
                                          <td>{row.score}</td>
                                          <td>{row.text}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              )}
                            </div>
                          ))}

                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && docUploaded && (
            <div className="message-row">
              <div className="avatar assistant">
                <div className="brand-icon" style={{width:'36px', height:'36px'}}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/></svg></div>
              </div>
              <div className="message-content">
                <div className="message-bubble" style={{display:'inline-block', padding: '1rem'}}>
                  <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                    <div className="status-dot" style={{backgroundColor:'var(--accent-blue)'}}></div> Processing...
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <div style={{color:'var(--text-muted)', padding:'0 8px'}}><FileText size={20}/></div>
            <input
              type="text"
              placeholder="Ask a question about your documents..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading || !docUploaded}
            />
            <button 
              className="btn-send" 
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading || !docUploaded}
            >
              <Send size={16} style={{marginLeft: '-2px', marginTop: '2px'}}/>
            </button>
          </div>
        </div>
      </div>

      {/* RIGHT SIDEBAR */}
      <div className="sidebar-right">
        {currentMetrics ? (
          <>
            <div className="right-section">
              <div className="right-section-header">
                <h3>Sources ({currentSources.length})</h3>
                <a href="#" className="link-view-all">View All</a>
              </div>
              
              {currentSources.map((source, idx) => (
                <div className="source-card" key={idx}>
                  <div className="source-card-header">
                    <FileText className="source-icon" size={18} />
                    <div className="source-title">
                      <span>{source.doc}</span>
                      <a href="#" style={{color:'var(--text-muted)'}}><Search size={14}/></a>
                    </div>
                  </div>
                  <div style={{paddingLeft: '28px'}}>
                    <div className="source-page">Page {source.page}</div>
                    <div className="source-snippet">
                      "{source.snippet}"
                    </div>
                    <div className="badge-used">Used in Answer</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="right-section">
              <div className="right-section-header">
                <h3>Key Metrics (This Query)</h3>
              </div>
              <div className="metrics-list">
                <div className="metric-row">
                  <span>Retrieval Latency</span>
                  <span>{currentMetrics.retrievalLatency}</span>
                </div>
                <div className="metric-row">
                  <span>Reranking Latency</span>
                  <span>{currentMetrics.rerankingLatency}</span>
                </div>
                <div className="metric-row">
                  <span>Generation Latency</span>
                  <span>{currentMetrics.generationLatency}</span>
                </div>
                <div className="metric-row total">
                  <span>Total Latency</span>
                  <span>{currentMetrics.latency}</span>
                </div>
                
                <div style={{height:'12px'}}></div>
                
                <div className="metric-row">
                  <span>Input Tokens</span>
                  <span>{currentMetrics.inputTokens}</span>
                </div>
                <div className="metric-row">
                  <span>Output Tokens</span>
                  <span>{currentMetrics.outputTokens}</span>
                </div>
                <div className="metric-row total">
                  <span>Total Tokens</span>
                  <span>{currentMetrics.tokens}</span>
                </div>

                <div style={{height:'12px'}}></div>

                <div className="metric-row">
                  <span>Estimated Cost</span>
                  <span>{currentMetrics.cost}</span>
                </div>
              </div>
            </div>

            <div className="right-section">
              <div className="right-section-header">
                <h3>Evidence Check</h3>
              </div>
              <div className="evidence-title">
                <CheckCircle2 size={16} /> {currentMetrics.evidenceCheck}
              </div>
              <div className="metrics-list">
                <div className="metric-row">
                  <span>Top Reranker Score</span>
                  <span>{currentMetrics.topRerankerScore}</span>
                </div>
                <div className="metric-row">
                  <span>Relevant Chunks</span>
                  <span>{currentMetrics.relevantChunks}</span>
                </div>
                <div className="metric-row">
                  <span>Configured Threshold</span>
                  <span>{currentMetrics.threshold}</span>
                </div>
                <div className="metric-row">
                  <span>Decision</span>
                  <span>{currentMetrics.decision}</span>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div style={{textAlign: 'center', marginTop: '20vh', color: 'var(--text-muted)'}}>
            <Info size={48} style={{opacity: 0.5, marginBottom: '1rem'}} />
            <p style={{fontSize: '0.9rem'}}>Upload a document and ask a question to see RAG pipeline traces, sources, and metrics.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
