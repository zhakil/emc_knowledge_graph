import React, { useState } from 'react';
import { Editor } from '@monaco-editor/react';
import { PromptTemplate } from '../../types/prompt';

interface PromptEditorProps {
  templates: PromptTemplate[];
  onExecute: (prompt: string, params: any) => Promise<void>;
}

export const PromptEditor: React.FC<PromptEditorProps> = ({
  templates,
  onExecute
}) => {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [parameters, setParameters] = useState<Record<string, any>>({
    temperature: 0.7,
    max_tokens: 2000,
    model: 'deepseek-chat'
  });

  const handleTemplateSelect = (template: PromptTemplate) => {
    setCurrentPrompt(template.content);
  };

  return (
    <div className="prompt-editor">
      <div className="template-selector">
        <select onChange={(e) => {
          const template = templates.find(t => t.id === e.target.value);
          if (template) handleTemplateSelect(template);
        }}>
          <option value="">选择模板...</option>
          {templates.map(t => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
      </div>

      <Editor
        height="400px"
        defaultLanguage="markdown"
        value={currentPrompt}
        onChange={(value) => setCurrentPrompt(value || '')}
        options={{
          minimap: { enabled: false },
          lineNumbers: 'on',
          wordWrap: 'on'
        }}
      />

      <div className="parameters">
        <h3>AI参数配置</h3>
        <div className="param-group">
          <label>温度 (Temperature)</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={parameters.temperature}
            onChange={(e) => setParameters({
              ...parameters,
              temperature: parseFloat(e.target.value)
            })}
          />
          <span>{parameters.temperature}</span>
        </div>
        
        <div className="param-group">
          <label>最大令牌数</label>
          <input
            type="number"
            value={parameters.max_tokens}
            onChange={(e) => setParameters({
              ...parameters,
              max_tokens: parseInt(e.target.value)
            })}
          />
        </div>
      </div>

      <button 
        className="execute-btn"
        onClick={() => onExecute(currentPrompt, parameters)}
      >
        执行查询
      </button>
    </div>
  );
};