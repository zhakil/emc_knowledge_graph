import React, { useState, useRef, useCallback } from 'react';
import { Upload, Button, Card, Tabs, Input, message, Progress, Alert, Tag, Space, Typography, Divider, Modal } from 'antd';
import { 
  UploadOutlined, 
  FileTextOutlined, 
  FilePdfOutlined, 
  FileWordOutlined, 
  FileImageOutlined,
  EditOutlined,
  ClearOutlined,
  ScanOutlined,
  CloudUploadOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import './MultiFormatInputProcessor.css';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Text, Title } = Typography;
const { Dragger } = Upload;

interface FileInfo {
  name: string;
  type: string;
  size: number;
  content?: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  extractedText?: string;
  tokenCount?: number;
  errorMessage?: string;
}

interface MultiFormatInputProcessorProps {
  onTextExtracted: (text: string, metadata: any) => void;
  maxTokens?: number;
}

const MultiFormatInputProcessor: React.FC<MultiFormatInputProcessorProps> = ({ 
  onTextExtracted, 
  maxTokens = 1000000 
}) => {
  const [activeTab, setActiveTab] = useState('manual');
  const [manualText, setManualText] = useState('');
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalTokens, setTotalTokens] = useState(0);
  const [showTokenWarning, setShowTokenWarning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 示例EMC文本
  const sampleTexts = {
    emc_test: `SuperCharger Model SC-5000 EMC Test Report

Product Information:
- Manufacturer: ChargeCorp Technologies
- Model: SuperCharger SC-5000  
- Product Type: Industrial Electric Vehicle Charger
- Power Rating: 50kW DC Fast Charging

EMC Standards Applied:
- EN 55011:2016+A11:2020 (CISPR 11) - Industrial, scientific and medical equipment
- IEC 61000-4-3:2020 - Radiated immunity test
- IEC 61000-4-6:2013 - Conducted immunity test

Test Equipment Used:
- EMI Receiver: Rohde & Schwarz ESRP R3273
- Signal Generator: Keysight E8257D
- Antenna: EMCO 3115 Log-Periodic (30MHz-1GHz)
- Power Amplifier: Amplifier Research 75A250A

Test Results Summary:
Radiated Emissions Test (30MHz - 1GHz):
- Frequency Range: 30MHz to 1GHz
- Test Distance: 3 meters
- Test Environment: Semi-anechoic chamber
- Result: PASS - All emissions below Class A limits

Conducted Emissions Test (150kHz - 30MHz):
- Frequency Range: 150kHz to 30MHz  
- LISN: Schwarzbeck NNLK 8129
- Result: PASS - Compliant with EN 55011 Class A

Immunity Tests:
- Radiated Immunity (80MHz-1GHz): 10V/m - PASS
- Conducted Immunity (150kHz-80MHz): 10V - PASS
- ESD Immunity: ±8kV contact, ±15kV air - PASS

Conclusion: The SuperCharger SC-5000 demonstrates full compliance with EMC requirements.`,
    
    standard_doc: `EN 55011:2016+A11:2020 - Industrial, Scientific and Medical Equipment

Scope:
This European standard applies to industrial, scientific and medical (ISM) radio-frequency equipment and to spark-gap equipment operating at frequencies below 400 GHz.

Frequency Classifications:
- Group 1: Equipment in which radio-frequency energy is only used for the internal functioning
- Group 2: Equipment in which radio-frequency energy is intentionally generated for material treatment

Emission Limits:
Class A Equipment (Industrial environment):
- Conducted emissions (150kHz-30MHz): Quasi-peak limits
- Radiated emissions (30MHz-1GHz): Peak and average limits

Class B Equipment (Domestic environment):  
- More stringent limits than Class A
- Applicable to equipment intended for residential use

Test Methods:
- Conducted emissions measurement using LISN
- Radiated emissions measurement in anechoic/semi-anechoic chamber
- Measurement distance: 3m or 10m depending on frequency

Required Documentation:
- Technical construction file
- Declaration of conformity
- User instructions with EMC precautions`,

    equipment_spec: `EMI Receiver R3273 Technical Specifications

General:
- Manufacturer: Rohde & Schwarz
- Model: ESRP R3273
- Type: EMI Test Receiver
- Frequency Range: 20Hz to 26.5GHz

EMC Measurements:
- Conducted Emissions: 150kHz - 30MHz
- Radiated Emissions: 30MHz - 26.5GHz
- Real-time analysis capability
- CISPR 16-1-1 compliant

Key Features:
- FFT-based real-time spectrum analysis
- Parallel measurement of multiple detectors
- Automated EMC test sequences
- Built-in pre-compliance testing
- Integration with EMC32 software

Measurement Capabilities:
- Amplitude accuracy: ±1.5dB
- Phase noise: -140dBc/Hz at 10kHz offset
- EMI bandwidths: 200Hz, 9kHz, 120kHz
- Detectors: Peak, Quasi-peak, Average, RMS

Interfaces:
- LAN, USB, GPIB connectivity
- Remote control capability
- Data export formats: CSV, XML, PDF`
  };

  // 估算token数量（粗略估算：1 token ≈ 4字符）
  const estimateTokens = useCallback((text: string): number => {
    return Math.ceil(text.length / 4);
  }, []);

  // 处理手动输入文本
  const handleManualTextChange = (value: string) => {
    setManualText(value);
    const tokens = estimateTokens(value);
    setTotalTokens(tokens);
    
    if (tokens > maxTokens * 0.9) {
      setShowTokenWarning(true);
    } else {
      setShowTokenWarning(false);
    }
  };

  // 加载示例文本
  const loadSampleText = (type: keyof typeof sampleTexts) => {
    const text = sampleTexts[type];
    setManualText(text);
    handleManualTextChange(text);
    message.success('示例文本已加载');
  };

  // 文件上传前的验证
  const beforeUpload = (file: File) => {
    const isValidType = /\.(pdf|docx?|txt|png|jpe?g|gif|bmp)$/i.test(file.name);
    if (!isValidType) {
      message.error('不支持的文件格式！请上传PDF、Word、图片或文本文件。');
      return false;
    }

    const isLt100M = file.size / 1024 / 1024 < 100;
    if (!isLt100M) {
      message.error('文件大小不能超过100MB！');
      return false;
    }

    return true;
  };

  // 模拟文件内容提取
  const extractFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const fileType = file.type;
      const fileName = file.name.toLowerCase();
      
      setTimeout(() => {
        if (fileName.endsWith('.pdf')) {
          resolve(`[PDF内容提取] 
文档标题: ${file.name}
提取的文本内容: 
${sampleTexts.emc_test}
          
[元数据]
页数: 15
文件大小: ${(file.size / 1024).toFixed(1)}KB
创建时间: ${new Date().toLocaleString()}`);
        } else if (fileName.endsWith('.docx') || fileName.endsWith('.doc')) {
          resolve(`[Word文档内容提取]
文档: ${file.name}
提取的文本:
${sampleTexts.standard_doc}

[文档属性]
字数统计: 450
段落数: 12
创建者: EMC测试工程师`);
        } else if (/\.(png|jpe?g|gif|bmp)$/i.test(fileName)) {
          resolve(`[OCR图像识别结果]
图像文件: ${file.name}
识别的文本内容:
${sampleTexts.equipment_spec}

[图像信息]
分辨率: 1920x1080
文件格式: ${file.type}
OCR置信度: 94.5%`);
        } else if (fileName.endsWith('.txt')) {
          // 对于文本文件，读取实际内容
          const reader = new FileReader();
          reader.onload = (e) => {
            resolve(e.target?.result as string || '无法读取文件内容');
          };
          reader.readAsText(file, 'utf-8');
          return;
        } else {
          resolve(`文件: ${file.name}\n暂不支持该格式的内容提取。`);
        }
      }, Math.random() * 3000 + 1000); // 1-4秒随机延迟
    });
  };

  // 处理文件上传
  const handleFileUpload = async (file: File) => {
    const fileInfo: FileInfo = {
      name: file.name,
      type: file.type,
      size: file.size,
      status: 'uploading',
      progress: 0
    };

    setFiles(prev => [...prev, fileInfo]);
    setIsProcessing(true);

    try {
      // 模拟上传进度
      const uploadInterval = setInterval(() => {
        setFiles(prev => prev.map(f => 
          f.name === file.name && f.status === 'uploading' 
            ? { ...f, progress: Math.min(f.progress + Math.random() * 30, 100) }
            : f
        ));
      }, 200);

      // 等待上传完成
      await new Promise(resolve => setTimeout(resolve, 2000));
      clearInterval(uploadInterval);

      // 更新状态为处理中
      setFiles(prev => prev.map(f => 
        f.name === file.name 
          ? { ...f, status: 'processing', progress: 100 }
          : f
      ));

      // 提取文件内容
      const extractedText = await extractFileContent(file);
      const tokens = estimateTokens(extractedText);

      // 检查token限制
      if (totalTokens + tokens > maxTokens) {
        throw new Error(`添加此文件将超过最大token限制 (${maxTokens.toLocaleString()})。当前: ${totalTokens.toLocaleString()}, 新增: ${tokens.toLocaleString()}`);
      }

      // 更新文件状态
      setFiles(prev => prev.map(f => 
        f.name === file.name 
          ? { 
              ...f, 
              status: 'completed', 
              extractedText, 
              tokenCount: tokens 
            }
          : f
      ));

      setTotalTokens(prev => prev + tokens);
      message.success(`文件 ${file.name} 处理完成！提取了 ${tokens.toLocaleString()} 个token。`);

    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.name === file.name 
          ? { 
              ...f, 
              status: 'error', 
              errorMessage: error instanceof Error ? error.message : '处理失败'
            }
          : f
      ));
      message.error(`文件 ${file.name} 处理失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsProcessing(false);
    }

    return false; // 阻止默认上传行为
  };

  // 删除文件
  const removeFile = (fileName: string) => {
    const file = files.find(f => f.name === fileName);
    if (file && file.tokenCount) {
      setTotalTokens(prev => prev - file.tokenCount!);
    }
    setFiles(prev => prev.filter(f => f.name !== fileName));
  };

  // 合并所有文本内容
  const combineAllContent = () => {
    let combinedText = '';
    
    // 添加手动输入的文本
    if (manualText.trim()) {
      combinedText += `[手动输入文本]\n${manualText}\n\n`;
    }
    
    // 添加文件提取的文本
    files.forEach(file => {
      if (file.status === 'completed' && file.extractedText) {
        combinedText += `[文件: ${file.name}]\n${file.extractedText}\n\n`;
      }
    });
    
    return combinedText.trim();
  };

  // 开始提取分析
  const startExtraction = () => {
    const combinedText = combineAllContent();
    
    if (!combinedText) {
      message.warning('请输入文本或上传文件后再开始分析');
      return;
    }

    const metadata = {
      totalTokens,
      fileCount: files.filter(f => f.status === 'completed').length,
      manualTextLength: manualText.length,
      files: files.map(f => ({
        name: f.name,
        type: f.type,
        size: f.size,
        tokenCount: f.tokenCount
      }))
    };

    onTextExtracted(combinedText, metadata);
    message.success('开始实体关系提取分析...');
  };

  // 清空所有内容
  const clearAll = () => {
    Modal.confirm({
      title: '确认清空',
      content: '确定要清空所有输入内容和上传文件吗？',
      onOk: () => {
        setManualText('');
        setFiles([]);
        setTotalTokens(0);
        setShowTokenWarning(false);
        message.success('已清空所有内容');
      }
    });
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.toLowerCase();
    if (ext.endsWith('.pdf')) return <FilePdfOutlined style={{ color: '#d32f2f' }} />;
    if (ext.endsWith('.docx') || ext.endsWith('.doc')) return <FileWordOutlined style={{ color: '#1976d2' }} />;
    if (/\.(png|jpe?g|gif|bmp)$/i.test(ext)) return <FileImageOutlined style={{ color: '#388e3c' }} />;
    if (ext.endsWith('.txt')) return <FileTextOutlined style={{ color: '#f57c00' }} />;
    return <FileTextOutlined />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'processing';
      case 'uploading': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  return (
    <div className="multi-format-input-processor">
      {/* Token统计和警告 */}
      <Card className="token-stats-card" size="small">
        <div className="token-stats">
          <div className="token-counter">
            <Text strong>Token统计: </Text>
            <Tag color={totalTokens > maxTokens * 0.9 ? 'red' : totalTokens > maxTokens * 0.7 ? 'orange' : 'blue'}>
              {totalTokens.toLocaleString()} / {maxTokens.toLocaleString()}
            </Tag>
          </div>
          <Progress 
            percent={(totalTokens / maxTokens) * 100} 
            size="small"
            strokeColor={totalTokens > maxTokens * 0.9 ? '#ff4d4f' : '#1890ff'}
            showInfo={false}
          />
        </div>
        
        {showTokenWarning && (
          <Alert
            message="Token数量警告"
            description="当前token数量接近上限，请注意控制输入内容长度。"
            type="warning"
            closable
            style={{ marginTop: 8 }}
            icon={<InfoCircleOutlined />}
          />
        )}
      </Card>

      <Tabs activeKey={activeTab} onChange={setActiveTab} className="input-tabs">
        {/* 手动输入标签页 */}
        <TabPane 
          tab={
            <span>
              <EditOutlined />
              手动输入
            </span>
          } 
          key="manual"
        >
          <Card title="文本输入" className="manual-input-card">
            <div className="sample-texts">
              <Text strong>快速加载示例: </Text>
              <Space wrap>
                <Button size="small" onClick={() => loadSampleText('emc_test')}>
                  EMC测试报告
                </Button>
                <Button size="small" onClick={() => loadSampleText('standard_doc')}>
                  标准文档
                </Button>
                <Button size="small" onClick={() => loadSampleText('equipment_spec')}>
                  设备规格
                </Button>
              </Space>
            </div>
            
            <TextArea
              value={manualText}
              onChange={(e) => handleManualTextChange(e.target.value)}
              placeholder="请输入EMC相关文本内容进行实体关系提取分析..."
              rows={12}
              className="manual-text-area"
              showCount
              maxLength={maxTokens * 4} // 粗略限制字符数
            />
            
            <div className="text-stats">
              <Text type="secondary">
                字符数: {manualText.length} | 
                预估Token: {estimateTokens(manualText).toLocaleString()} |
                行数: {manualText.split('\n').length}
              </Text>
            </div>
          </Card>
        </TabPane>

        {/* 文件上传标签页 */}
        <TabPane 
          tab={
            <span>
              <CloudUploadOutlined />
              文件上传 ({files.length})
            </span>
          } 
          key="upload"
        >
          <Card title="多格式文件处理" className="upload-card">
            <Dragger
              beforeUpload={beforeUpload}
              customRequest={({ file }) => handleFileUpload(file as File)}
              multiple
              className="upload-dragger"
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持格式: PDF、Word (docx/doc)、图片 (png/jpg/gif)、文本 (txt)
                <br />
                单文件最大100MB，总token限制: {maxTokens.toLocaleString()}
              </p>
            </Dragger>

            <Divider>支持的处理能力</Divider>
            
            <div className="format-capabilities">
              <div className="capability-item">
                <FilePdfOutlined style={{ color: '#d32f2f', fontSize: 24 }} />
                <div>
                  <Text strong>PDF文档</Text>
                  <br />
                  <Text type="secondary">文本提取、表格识别、元数据解析</Text>
                </div>
              </div>
              
              <div className="capability-item">
                <FileWordOutlined style={{ color: '#1976d2', fontSize: 24 }} />
                <div>
                  <Text strong>Word文档</Text>
                  <br />
                  <Text type="secondary">结构化内容、样式保留、批注提取</Text>
                </div>
              </div>
              
              <div className="capability-item">
                <FileImageOutlined style={{ color: '#388e3c', fontSize: 24 }} />
                <div>
                  <Text strong>图像文件</Text>
                  <br />
                  <Text type="secondary">OCR文字识别、图表分析、元数据提取</Text>
                </div>
              </div>
              
              <div className="capability-item">
                <FileTextOutlined style={{ color: '#f57c00', fontSize: 24 }} />
                <div>
                  <Text strong>文本文件</Text>
                  <br />
                  <Text type="secondary">编码检测、格式化保留、大文件支持</Text>
                </div>
              </div>
            </div>
          </Card>

          {/* 文件列表 */}
          {files.length > 0 && (
            <Card title="处理中的文件" className="file-list-card" style={{ marginTop: 16 }}>
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <div className="file-info">
                    <div className="file-icon">
                      {getFileIcon(file.name)}
                    </div>
                    <div className="file-details">
                      <div className="file-name">{file.name}</div>
                      <div className="file-meta">
                        <Text type="secondary">
                          {(file.size / 1024).toFixed(1)}KB
                          {file.tokenCount && ` | ${file.tokenCount.toLocaleString()} tokens`}
                        </Text>
                      </div>
                    </div>
                    <div className="file-status">
                      <Tag color={getStatusColor(file.status)}>
                        {file.status === 'uploading' && '上传中'}
                        {file.status === 'processing' && '处理中'}
                        {file.status === 'completed' && '完成'}
                        {file.status === 'error' && '失败'}
                      </Tag>
                      <Button 
                        type="text" 
                        size="small" 
                        danger
                        onClick={() => removeFile(file.name)}
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                  
                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <Progress 
                      percent={file.progress} 
                      size="small" 
                      style={{ marginTop: 8 }}
                    />
                  )}
                  
                  {file.status === 'error' && file.errorMessage && (
                    <Alert 
                      message={file.errorMessage} 
                      type="error" 
                      style={{ marginTop: 8 }}
                    />
                  )}
                </div>
              ))}
            </Card>
          )}
        </TabPane>
      </Tabs>

      {/* 操作按钮 */}
      <Card className="action-card">
        <div className="action-buttons">
          <Button 
            type="primary" 
            size="large"
            icon={<ScanOutlined />}
            onClick={startExtraction}
            disabled={!combineAllContent() || isProcessing}
            loading={isProcessing}
          >
            开始实体关系提取分析
          </Button>
          
          <Button 
            size="large"
            icon={<ClearOutlined />}
            onClick={clearAll}
            disabled={!manualText && files.length === 0}
          >
            清空所有内容
          </Button>
        </div>
        
        <div className="content-summary">
          <Text type="secondary">
            内容概览: 
            {manualText && ` 手动文本 ${estimateTokens(manualText).toLocaleString()} tokens`}
            {manualText && files.length > 0 && ' + '}
            {files.length > 0 && ` ${files.length} 个文件 ${files.reduce((sum, f) => sum + (f.tokenCount || 0), 0).toLocaleString()} tokens`}
            {!manualText && files.length === 0 && ' 暂无内容'}
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default MultiFormatInputProcessor;