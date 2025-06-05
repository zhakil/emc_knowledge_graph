import React, { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Paper,
    TextField,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Slider,
    Typography,
    Chip,
    IconButton,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Alert,
    CircularProgress,
    Divider
} from '@mui/material';
import {
    Send,
    Save,
    Clear,
    ExpandMore,
    PlayArrow,
    Stop,
    Settings,
    Template,
    History
} from '@mui/icons-material';
import { Editor } from '@monaco-editor/react';
import { useDeepSeekStore } from '../../stores/deepSeekStore';

interface PromptTemplate {
    id: string;
    name: string;
    description: string;
    template: string;
    variables: string[];
    category: string;
}

interface DeepSeekConfig {
    model: string;
    temperature: number;
    maxTokens: number;
    topP: number;
    stream: boolean;
}

const DeepSeekPromptEditor: React.FC = () => {
    // 状态管理
    const [prompt, setPrompt] = useState<string>('');
    const [config, setConfig] = useState<DeepSeekConfig>({
        model: 'deepseek-chat',
        temperature: 0.7,
        maxTokens: 4000,
        topP: 0.9,
        stream: false
    });

    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [templateVariables, setTemplateVariables] = useState<Record<string, string>>({});
    const [isGenerating, setIsGenerating] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    // Store hooks
    const {
        templates,
        sessionId,
        apiKey,
        sendPrompt,
        loadTemplates,
        saveTemplate,
        getSessionHistory
    } = useDeepSeekStore();

    // 加载模板
    useEffect(() => {
        loadTemplates();
    }, [loadTemplates]);

    // 处理模板选择
    const handleTemplateSelect = useCallback((templateId: string) => {
        const template = templates.find(t => t.id === templateId);
        if (template) {
            setSelectedTemplate(templateId);
            setPrompt(template.template);

            // 初始化模板变量
            const initialVars: Record<string, string> = {};
            template.variables.forEach(variable => {
                initialVars[variable] = '';
            });
            setTemplateVariables(initialVars);
        }
    }, [templates]);

    // 格式化提示词（替换变量）
    const formatPrompt = useCallback((template: string, variables: Record<string, string>): string => {
        let formatted = template;
        Object.entries(variables).forEach(([key, value]) => {
            formatted = formatted.replace(new RegExp(`{${key}}`, 'g'), value);
        });
        return formatted;
    }, []);

    // 发送提示词
    const handleSendPrompt = useCallback(async () => {
        if (!prompt.trim()) {
            setError('请输入提示词内容');
            return;
        }

        if (!apiKey) {
            setError('请在设置中配置DeepSeek API密钥');
            return;
        }

        setIsGenerating(true);
        setError('');

        try {
            // 格式化提示词
            const finalPrompt = selectedTemplate ?
                formatPrompt(prompt, templateVariables) : prompt;

            await sendPrompt({
                prompt: finalPrompt,
                config,
                sessionId
            });
        } catch (err: any) {
            setError(err.message || '发送请求失败');
        } finally {
            setIsGenerating(false);
        }
    }, [prompt, selectedTemplate, templateVariables, config, sessionId, apiKey, sendPrompt, formatPrompt]);

    // 清除编辑器
    const handleClear = useCallback(() => {
        setPrompt('');
        setSelectedTemplate('');
        setTemplateVariables({});
        setError('');
    }, []);

    // 保存为模板
    const handleSaveTemplate = useCallback(() => {
        if (!prompt.trim()) return;

        const template: PromptTemplate = {
            id: Date.now().toString(),
            name: `Template_${Date.now()}`,
            description: '用户自定义模板',
            template: prompt,
            variables: [], // 可以通过正则提取{variable}格式的变量
            category: 'custom'
        };

        saveTemplate(template);
    }, [prompt, saveTemplate]);

    // 渲染模板变量输入
    const renderTemplateVariables = () => {
        if (!selectedTemplate) return null;

        const template = templates.find(t => t.id === selectedTemplate);
        if (!template || template.variables.length === 0) return null;

        return (
            <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                    模板变量
                </Typography>
                {template.variables.map((variable) => (
                    <TextField
                        key={variable}
                        fullWidth
                        size="small"
                        label={variable}
                        value={templateVariables[variable] || ''}
                        onChange={(e) => setTemplateVariables(prev => ({
                            ...prev,
                            [variable]: e.target.value
                        }))}
                        sx={{ mb: 1 }}
                    />
                ))}
            </Box>
        );
    };

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* 工具栏 */}
            <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <FormControl size="small" sx={{ minWidth: 200 }}>
                        <InputLabel>选择模板</InputLabel>
                        <Select
                            value={selectedTemplate}
                            label="选择模板"
                            onChange={(e) => handleTemplateSelect(e.target.value)}
                        >
                            <MenuItem value="">
                                <em>无模板</em>
                            </MenuItem>
                            {templates.map((template) => (
                                <MenuItem key={template.id} value={template.id}>
                                    <Box>
                                        <Typography variant="body2">{template.name}</Typography>
                                        <Typography variant="caption" color="textSecondary">
                                            {template.description}
                                        </Typography>
                                    </Box>
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <Chip
                        label={`模型: ${config.model}`}
                        icon={<Settings />}
                        size="small"
                        variant="outlined"
                    />

                    <Box sx={{ flexGrow: 1 }} />

                    <IconButton onClick={handleSaveTemplate} title="保存为模板">
                        <Template />
                    </IconButton>
                    <IconButton onClick={handleClear} title="清除内容">
                        <Clear />
                    </IconButton>
                </Box>

                {/* 模板变量输入 */}
                {renderTemplateVariables()}
            </Paper>

            {/* 提示词编辑器 */}
            <Paper elevation={1} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                    <Typography variant="h6">提示词编辑器</Typography>
                </Box>

                <Box sx={{ flexGrow: 1, minHeight: 300 }}>
                    <Editor
                        height="100%"
                        defaultLanguage="markdown"
                        value={prompt}
                        onChange={(value) => setPrompt(value || '')}
                        options={{
                            wordWrap: 'on',
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            fontSize: 14,
                            lineNumbers: 'on',
                            folding: true,
                            automaticLayout: true
                        }}
                        theme="vs-light"
                    />
                </Box>
            </Paper>

            {/* 参数配置 */}
            <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="subtitle1">高级参数配置</Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 3 }}>
                        <FormControl size="small">
                            <InputLabel>模型</InputLabel>
                            <Select
                                value={config.model}
                                label="模型"
                                onChange={(e) => setConfig(prev => ({ ...prev, model: e.target.value }))}
                            >
                                <MenuItem value="deepseek-chat">DeepSeek Chat</MenuItem>
                                <MenuItem value="deepseek-coder">DeepSeek Coder</MenuItem>
                                <MenuItem value="deepseek-r1">DeepSeek R1</MenuItem>
                            </Select>
                        </FormControl>

                        <TextField
                            size="small"
                            type="number"
                            label="最大Token数"
                            value={config.maxTokens}
                            onChange={(e) => setConfig(prev => ({
                                ...prev,
                                maxTokens: parseInt(e.target.value) || 4000
                            }))}
                            inputProps={{ min: 100, max: 8000, step: 100 }}
                        />

                        <Box>
                            <Typography gutterBottom>Temperature: {config.temperature}</Typography>
                            <Slider
                                value={config.temperature}
                                onChange={(_, value) => setConfig(prev => ({
                                    ...prev,
                                    temperature: value as number
                                }))}
                                min={0}
                                max={2}
                                step={0.1}
                                valueLabelDisplay="auto"
                            />
                        </Box>

                        <Box>
                            <Typography gutterBottom>Top P: {config.topP}</Typography>
                            <Slider
                                value={config.topP}
                                onChange={(_, value) => setConfig(prev => ({
                                    ...prev,
                                    topP: value as number
                                }))}
                                min={0}
                                max={1}
                                step={0.05}
                                valueLabelDisplay="auto"
                            />
                        </Box>
                    </Box>
                </AccordionDetails>
            </Accordion>

            {/* 错误提示 */}
            {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                </Alert>
            )}

            {/* 操作按钮 */}
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button
                    variant="contained"
                    startIcon={isGenerating ? <CircularProgress size={16} /> : <Send />}
                    onClick={handleSendPrompt}
                    disabled={isGenerating || !prompt.trim()}
                    sx={{ flexGrow: 1 }}
                >
                    {isGenerating ? '生成中...' : '发送提示词'}
                </Button>

                {isGenerating && (
                    <Button
                        variant="outlined"
                        startIcon={<Stop />}
                        onClick={() => setIsGenerating(false)}
                    >
                        停止
                    </Button>
                )}
            </Box>
        </Box>
    );
};

export default DeepSeekPromptEditor;