import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';

// 类型定义
interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: string[];
  category: string;
  createdAt: string;
  updatedAt: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    tokenUsage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
    };
    responseTime?: number;
    model?: string;
  };
}

interface ChatSession {
  id: string;
  name: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

interface DeepSeekConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  topP: number;
  stream: boolean;
}

interface APIUsageStats {
  totalRequests: number;
  totalTokens: number;
  totalCost: number;
  requestsToday: number;
  tokensToday: number;
  costToday: number;
  lastResetDate: string;
}

interface DeepSeekState {
  // API配置
  apiKey: string;
  baseUrl: string;
  config: DeepSeekConfig;
  
  // 会话管理
  sessions: ChatSession[];
  currentSessionId: string | null;
  
  // 模板管理
  templates: PromptTemplate[];
  
  // 响应状态
  isGenerating: boolean;
  streamingContent: string;
  error: string | null;
  
  // 使用统计
  usageStats: APIUsageStats;
  
  // UI状态
  sidebarOpen: boolean;
  darkMode: boolean;
}

interface DeepSeekActions {
  // API配置
  setApiKey: (key: string) => void;
  setBaseUrl: (url: string) => void;
  updateConfig: (config: Partial<DeepSeekConfig>) => void;
  
  // 会话管理
  createSession: (name?: string) => string;
  selectSession: (sessionId: string) => void;
  renameSession: (sessionId: string, name: string) => void;
  deleteSession: (sessionId: string) => void;
  clearSession: (sessionId: string) => void;
  
  // 消息管理
  sendMessage: (content: string, config?: Partial<DeepSeekConfig>) => Promise<void>;
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  editMessage: (sessionId: string, messageId: string, content: string) => void;
  deleteMessage: (sessionId: string, messageId: string) => void;
  
  // 模板管理
  loadTemplates: () => Promise<void>;
  saveTemplate: (template: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTemplate: (id: string, updates: Partial<PromptTemplate>) => void;
  deleteTemplate: (id: string) => void;
  
  // 流式响应
  startStreaming: () => void;
  updateStreamContent: (content: string) => void;
  stopStreaming: () => void;
  
  // 错误处理
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // 统计更新
  updateUsageStats: (tokens: number, cost: number) => void;
  resetDailyStats: () => void;
  
  // UI状态
  toggleSidebar: () => void;
  toggleDarkMode: () => void;
  
  // 导入导出
  exportSession: (sessionId: string) => string;
  importSession: (sessionData: string) => void;
  exportAllData: () => string;
  importAllData: (data: string) => void;
}

type DeepSeekStore = DeepSeekState & DeepSeekActions;

// 默认配置
const defaultConfig: DeepSeekConfig = {
  model: 'deepseek-chat',
  temperature: 0.7,
  maxTokens: 4000,
  topP: 0.9,
  stream: false,
};

const defaultUsageStats: APIUsageStats = {
  totalRequests: 0,
  totalTokens: 0,
  totalCost: 0,
  requestsToday: 0,
  tokensToday: 0,
  costToday: 0,
  lastResetDate: new Date().toDateString(),
};

// 默认模板
const defaultTemplates: PromptTemplate[] = [
  {
    id: 'emc-analysis',
    name: 'EMC标准分析',
    description: '分析EMC标准文档并提取关键信息',
    template: `作为EMC专家，请分析以下标准文档：

文档内容：
{document_content}

请提取：
1. 标准编号和版本
2. 适用频率范围  
3. 测试方法和要求
4. 限值和容差
5. 相关设备类型

以JSON格式返回结果。`,
    variables: ['document_content'],
    category: 'analysis',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'compliance-check',
    name: '合规性检查',
    description: '检查设备EMC合规性',
    template: `请评估设备的EMC合规性：

设备信息：{equipment_info}
测试报告：{test_report}
适用标准：{standards}

请分析合规性并给出改进建议。`,
    variables: ['equipment_info', 'test_report', 'standards'],
    category: 'compliance',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const useDeepSeekStore = create<DeepSeekStore>()(
  devtools(
    persist(
      (set, get) => ({
        // 初始状态
        apiKey: '',
        baseUrl: 'https://api.deepseek.com/v1',
        config: defaultConfig,
        sessions: [],
        currentSessionId: null,
        templates: defaultTemplates,
        isGenerating: false,
        streamingContent: '',
        error: null,
        usageStats: defaultUsageStats,
        sidebarOpen: true,
        darkMode: false,

        // API配置
        setApiKey: (key: string) => {
          set({ apiKey: key });
        },

        setBaseUrl: (url: string) => {
          set({ baseUrl: url });
        },

        updateConfig: (newConfig: Partial<DeepSeekConfig>) => {
          set((state) => ({
            config: { ...state.config, ...newConfig }
          }));
        },

        // 会话管理
        createSession: (name?: string) => {
          const sessionId = uuidv4();
          const sessionName = name || `会话 ${new Date().toLocaleString()}`;
          
          const newSession: ChatSession = {
            id: sessionId,
            name: sessionName,
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            isActive: true,
          };

          set((state) => ({
            sessions: [newSession, ...state.sessions],
            currentSessionId: sessionId,
          }));

          return sessionId;
        },

        selectSession: (sessionId: string) => {
          set({ currentSessionId: sessionId });
        },

        renameSession: (sessionId: string, name: string) => {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? { ...session, name, updatedAt: new Date().toISOString() }
                : session
            ),
          }));
        },

        deleteSession: (sessionId: string) => {
          set((state) => {
            const filteredSessions = state.sessions.filter(s => s.id !== sessionId);
            const newCurrentId = state.currentSessionId === sessionId 
              ? (filteredSessions[0]?.id || null)
              : state.currentSessionId;
            
            return {
              sessions: filteredSessions,
              currentSessionId: newCurrentId,
            };
          });
        },

        clearSession: (sessionId: string) => {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? { ...session, messages: [], updatedAt: new Date().toISOString() }
                : session
            ),
          }));
        },

        // 消息管理
        sendMessage: async (content: string, config?: Partial<DeepSeekConfig>) => {
          const state = get();
          
          if (!state.apiKey) {
            set({ error: '请先配置API密钥' });
            return;
          }

          let sessionId = state.currentSessionId;
          if (!sessionId) {
            sessionId = get().createSession();
          }

          // 添加用户消息
          const userMessage: ChatMessage = {
            id: uuidv4(),
            role: 'user',
            content,
            timestamp: new Date().toISOString(),
          };

          get().addMessage(sessionId, userMessage);
          set({ isGenerating: true, error: null });

          try {
            const requestConfig = { ...state.config, ...config };
            
            // 构建消息历史
            const session = state.sessions.find(s => s.id === sessionId);
            const messages = session?.messages.map(msg => ({
              role: msg.role,
              content: msg.content,
            })) || [];

            // 发送API请求
            const response = await fetch('/api/deepseek/chat', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.apiKey}`,
              },
              body: JSON.stringify({
                messages,
                ...requestConfig,
              }),
            });

            if (!response.ok) {
              throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            // 添加助手回复
            const assistantMessage: ChatMessage = {
              id: uuidv4(),
              role: 'assistant',
              content: data.content,
              timestamp: new Date().toISOString(),
              metadata: {
                tokenUsage: data.usage,
                responseTime: data.response_time,
                model: data.model,
              },
            };

            get().addMessage(sessionId, assistantMessage);
            
            // 更新使用统计
            if (data.usage) {
              const tokens = data.usage.total_tokens;
              const cost = tokens * 0.00001; // 假设成本
              get().updateUsageStats(tokens, cost);
            }

          } catch (error: any) {
            set({ error: error.message });
          } finally {
            set({ isGenerating: false });
          }
        },

        addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
          const fullMessage: ChatMessage = {
            ...message,
            id: uuidv4(),
            timestamp: new Date().toISOString(),
          };

          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? {
                    ...session,
                    messages: [...session.messages, fullMessage],
                    updatedAt: new Date().toISOString(),
                  }
                : session
            ),
          }));
        },

        editMessage: (sessionId: string, messageId: string, content: string) => {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? {
                    ...session,
                    messages: session.messages.map((msg) =>
                      msg.id === messageId ? { ...msg, content } : msg
                    ),
                    updatedAt: new Date().toISOString(),
                  }
                : session
            ),
          }));
        },

        deleteMessage: (sessionId: string, messageId: string) => {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? {
                    ...session,
                    messages: session.messages.filter((msg) => msg.id !== messageId),
                    updatedAt: new Date().toISOString(),
                  }
                : session
            ),
          }));
        },

        // 模板管理
        loadTemplates: async () => {
          try {
            const response = await fetch('/api/templates');
            if (response.ok) {
              const templates = await response.json();
              set({ templates });
            }
          } catch (error) {
            console.error('加载模板失败:', error);
          }
        },

        saveTemplate: (template: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
          const fullTemplate: PromptTemplate = {
            ...template,
            id: uuidv4(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };

          set((state) => ({
            templates: [...state.templates, fullTemplate],
          }));
        },

        updateTemplate: (id: string, updates: Partial<PromptTemplate>) => {
          set((state) => ({
            templates: state.templates.map((template) =>
              template.id === id
                ? { ...template, ...updates, updatedAt: new Date().toISOString() }
                : template
            ),
          }));
        },

        deleteTemplate: (id: string) => {
          set((state) => ({
            templates: state.templates.filter((template) => template.id !== id),
          }));
        },

        // 流式响应
        startStreaming: () => {
          set({ isGenerating: true, streamingContent: '' });
        },

        updateStreamContent: (content: string) => {
          set((state) => ({
            streamingContent: state.streamingContent + content,
          }));
        },

        stopStreaming: () => {
          set({ isGenerating: false, streamingContent: '' });
        },

        // 错误处理
        setError: (error: string | null) => {
          set({ error });
        },

        clearError: () => {
          set({ error: null });
        },

        // 统计更新
        updateUsageStats: (tokens: number, cost: number) => {
          set((state) => {
            const today = new Date().toDateString();
            const needsReset = state.usageStats.lastResetDate !== today;

            return {
              usageStats: {
                totalRequests: state.usageStats.totalRequests + 1,
                totalTokens: state.usageStats.totalTokens + tokens,
                totalCost: state.usageStats.totalCost + cost,
                requestsToday: needsReset ? 1 : state.usageStats.requestsToday + 1,
                tokensToday: needsReset ? tokens : state.usageStats.tokensToday + tokens,
                costToday: needsReset ? cost : state.usageStats.costToday + cost,
                lastResetDate: today,
              },
            };
          });
        },

        resetDailyStats: () => {
          set((state) => ({
            usageStats: {
              ...state.usageStats,
              requestsToday: 0,
              tokensToday: 0,
              costToday: 0,
              lastResetDate: new Date().toDateString(),
            },
          }));
        },

        // UI状态
        toggleSidebar: () => {
          set((state) => ({ sidebarOpen: !state.sidebarOpen }));
        },

        toggleDarkMode: () => {
          set((state) => ({ darkMode: !state.darkMode }));
        },

        // 导入导出
        exportSession: (sessionId: string) => {
          const state = get();
          const session = state.sessions.find(s => s.id === sessionId);
          return JSON.stringify(session, null, 2);
        },

        importSession: (sessionData: string) => {
          try {
            const session: ChatSession = JSON.parse(sessionData);
            session.id = uuidv4(); // 生成新ID避免冲突
            
            set((state) => ({
              sessions: [session, ...state.sessions],
            }));
          } catch (error) {
            set({ error: '导入会话数据格式错误' });
          }
        },

        exportAllData: () => {
          const state = get();
          return JSON.stringify({
            sessions: state.sessions,
            templates: state.templates,
            config: state.config,
            usageStats: state.usageStats,
          }, null, 2);
        },

        importAllData: (data: string) => {
          try {
            const importedData = JSON.parse(data);
            
            set({
              sessions: importedData.sessions || [],
              templates: importedData.templates || defaultTemplates,
              config: importedData.config || defaultConfig,
              usageStats: importedData.usageStats || defaultUsageStats,
            });
          } catch (error) {
            set({ error: '导入数据格式错误' });
          }
        },
      }),
      {
        name: 'deepseek-store',
        partialize: (state) => ({
          apiKey: state.apiKey,
          baseUrl: state.baseUrl,
          config: state.config,
          sessions: state.sessions,
          templates: state.templates,
          usageStats: state.usageStats,
          sidebarOpen: state.sidebarOpen,
          darkMode: state.darkMode,
        }),
      }
    ),
    {
      name: 'deepseek-store',
    }
  )
);

// 选择器hooks
export const useCurrentSession = () => {
  return useDeepSeekStore((state) => {
    const currentId = state.currentSessionId;
    return currentId ? state.sessions.find(s => s.id === currentId) : null;
  });
};

export const useTemplatesByCategory = (category?: string) => {
  return useDeepSeekStore((state) => 
    category 
      ? state.templates.filter(t => t.category === category)
      : state.templates
  );
};

export const useUsageStats = () => {
  return useDeepSeekStore((state) => state.usageStats);
};