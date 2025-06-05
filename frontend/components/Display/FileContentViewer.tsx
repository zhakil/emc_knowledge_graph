import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { IconButton, Tooltip, Box } from '@mui/material';
import { ContentCopy, Check } from '@mui/icons-material';

interface FileContentViewerProps {
  content: string;
  language: string;
  filename: string;
  maxHeight?: string | number;
  showLineNumbers?: boolean;
  wrapLines?: boolean;
}

const FileContentViewer: React.FC<FileContentViewerProps> = ({
  content,
  language,
  filename,
  maxHeight = '500px',
  showLineNumbers = true,
  wrapLines = false
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box sx={{ position: 'relative', border: '1px solid #e0e0e0', borderRadius: '4px' }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        bgcolor: '#2d2d2d', 
        color: 'white', 
        p: 1,
        borderTopLeftRadius: '4px',
        borderTopRightRadius: '4px'
      }}>
        <Box sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
          {filename}
        </Box>
        <Tooltip title={copied ? "Copied!" : "Copy to clipboard"} arrow>
          <IconButton onClick={handleCopy} size="small" sx={{ color: 'white' }}>
            {copied ? <Check fontSize="small" /> : <ContentCopy fontSize="small" />}
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ 
        maxHeight, 
        overflow: 'auto',
        borderBottomLeftRadius: '4px',
        borderBottomRightRadius: '4px'
      }}>
        <SyntaxHighlighter
          language={language}
          style={materialDark}
          showLineNumbers={showLineNumbers}
          wrapLines={wrapLines}
          customStyle={{ 
            margin: 0, 
            borderRadius: 0,
            fontSize: '0.85rem',
            backgroundColor: '#1e1e1e'
          }}
          lineNumberStyle={{ 
            color: '#858585', 
            minWidth: '2.5em' 
          }}
        >
          {content}
        </SyntaxHighlighter>
      </Box>
    </Box>
  );
};

export default FileContentViewer;