import React, { useState } from 'react';
import { Card, Steps, Button, Progress, Alert, Typography } from 'antd';
import { RobotOutlined, FileTextOutlined, ShareAltOutlined, CheckCircleOutlined } from '@ant-design/icons';

const { Step } = Steps;
const { Title, Text } = Typography;

const KGBuildPipeline: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const steps = [
    {
      title: '文档解析',
      description: '解析上传的文档文件',
      icon: <FileTextOutlined />
    },
    {
      title: '实体提取',
      description: '使用AI提取实体和关系',
      icon: <RobotOutlined />
    },
    {
      title: '图谱构建',
      description: '构建知识图谱',
      icon: <ShareAltOutlined />
    },
    {
      title: '完成',
      description: '构建完成',
      icon: <CheckCircleOutlined />
    }
  ];

  const startBuild = async () => {
    setIsProcessing(true);
    setProgress(0);
    
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i);
      
      // 模拟处理过程
      for (let j = 0; j <= 100; j += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setProgress((i * 100 + j) / steps.length);
      }
    }
    
    setIsProcessing(false);
    setCurrentStep(steps.length);
  };

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={2}>知识图谱构建流程</Title>
        
        <Steps current={currentStep} style={{ marginBottom: 24 }}>
          {steps.map((step, index) => (
            <Step
              key={index}
              title={step.title}
              description={step.description}
              icon={step.icon}
            />
          ))}
        </Steps>

        {isProcessing && (
          <div style={{ marginBottom: 24 }}>
            <Text>正在处理...</Text>
            <Progress percent={Math.round(progress)} status="active" />
          </div>
        )}

        {currentStep === steps.length && (
          <Alert
            message="构建完成"
            description="知识图谱构建已完成"
            type="success"
            style={{ marginBottom: 24 }}
          />
        )}

        <Button
          type="primary"
          onClick={startBuild}
          loading={isProcessing}
          disabled={isProcessing}
        >
          开始构建
        </Button>
      </Card>
    </div>
  );
};

export default KGBuildPipeline;