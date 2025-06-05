import React, { useCallback, useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  IconButton,
  CircularProgress
} from '@mui/material';
import { CloudUpload, InsertDriveFile, Delete } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  acceptedFormats?: string[];
  maxSizeMB?: number;
  maxFiles?: number;
  loading?: boolean;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  onFilesSelected,
  acceptedFormats = ['.pdf', '.csv', '.xlsx', '.txt'],
  maxSizeMB = 10,
  maxFiles = 5,
  loading = false
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    
    if (files.length + acceptedFiles.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    if (rejectedFiles.length > 0) {
      const firstRejection = rejectedFiles[0];
      if (firstRejection.errors[0].code === 'file-too-large') {
        setError(`File exceeds ${maxSizeMB}MB size limit`);
      } else if (firstRejection.errors[0].code === 'file-invalid-type') {
        setError(`Only ${acceptedFormats.join(', ')} formats allowed`);
      }
      return;
    }

    const newFiles = [...files, ...acceptedFiles];
    setFiles(newFiles);
    onFilesSelected(newFiles);
  }, [files, maxFiles, maxSizeMB, acceptedFormats]);

  const removeFile = (index: number) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
    onFilesSelected(newFiles);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFormats.reduce((acc, ext) => ({ ...acc, [ext]: [] }), {}),
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: true
  });

  return (
    <Box sx={{ width: '100%' }}>
      <Paper
        {...getRootProps()}
        variant="outlined"
        sx={{
          p: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          mb: 2
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 50, color: 'action.active', mb: 1 }} />
        <Typography variant="h6">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          {acceptedFormats.join(', ')} files (max {maxSizeMB}MB each)
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }}>
          Browse Files
        </Button>
      </Paper>

      {error && (
        <Typography color="error" variant="body2" sx={{ mb: 1 }}>
          {error}
        </Typography>
      )}

      {files.length > 0 && (
        <Paper variant="outlined" sx={{ p: 1, maxHeight: 200, overflow: 'auto' }}>
          <List dense>
            {files.map((file, index) => (
              <ListItem 
                key={index}
                secondaryAction={
                  <IconButton 
                    edge="end" 
                    onClick={() => removeFile(index)}
                    disabled={loading}
                  >
                    <Delete />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  <InsertDriveFile />
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                />
                {loading && <CircularProgress size={24} />}
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default FileUploadZone;