import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [records, setRecords] = useState([]);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    vaccine_name: '',
    date_administered: null,
    next_due_date: null,
    provider: '',
    file: null,
  });

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/records/my-records');
      setRecords(response.data);
    } catch (error) {
      setError('Failed to fetch records');
    }
  };

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData((prev) => ({ ...prev, file: e.target.files[0] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const formDataToSend = new FormData();
    Object.keys(formData).forEach((key) => {
      if (formData[key] !== null) {
        formDataToSend.append(key, formData[key]);
      }
    });

    try {
      await axios.post('http://localhost:5000/api/records/upload', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSuccess('Record uploaded successfully');
      handleClose();
      fetchRecords();
      setFormData({
        vaccine_name: '',
        date_administered: null,
        next_due_date: null,
        provider: '',
        file: null,
      });
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to upload record');
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4">Welcome, {user.username}!</Typography>
          <Button variant="outlined" color="error" onClick={handleLogout}>
            Logout
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Button
        variant="contained"
        color="primary"
        onClick={handleOpen}
        sx={{ mb: 3 }}
      >
        Upload New Record
      </Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Vaccine Name</TableCell>
              <TableCell>Date Administered</TableCell>
              <TableCell>Next Due Date</TableCell>
              <TableCell>Provider</TableCell>
              <TableCell>Document</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {records.map((record) => (
              <TableRow key={record.id}>
                <TableCell>{record.vaccine_name}</TableCell>
                <TableCell>{new Date(record.date_administered).toLocaleDateString()}</TableCell>
                <TableCell>
                  {record.next_due_date
                    ? new Date(record.next_due_date).toLocaleDateString()
                    : 'N/A'}
                </TableCell>
                <TableCell>{record.provider || 'N/A'}</TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    href={`http://localhost:5000/api/records/document/${record.id}`}
                    target="_blank"
                  >
                    View Document
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Immunization Record</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              label="Vaccine Name"
              name="vaccine_name"
              value={formData.vaccine_name}
              onChange={handleInputChange}
            />
            <DatePicker
              label="Date Administered"
              value={formData.date_administered}
              onChange={(date) =>
                setFormData((prev) => ({ ...prev, date_administered: date }))
              }
              renderInput={(params) => (
                <TextField {...params} margin="normal" required fullWidth />
              )}
            />
            <DatePicker
              label="Next Due Date"
              value={formData.next_due_date}
              onChange={(date) =>
                setFormData((prev) => ({ ...prev, next_due_date: date }))
              }
              renderInput={(params) => (
                <TextField {...params} margin="normal" fullWidth />
              )}
            />
            <TextField
              margin="normal"
              fullWidth
              label="Provider"
              name="provider"
              value={formData.provider}
              onChange={handleInputChange}
            />
            <Button
              variant="outlined"
              component="label"
              fullWidth
              sx={{ mt: 2 }}
            >
              Upload Document
              <input
                type="file"
                hidden
                onChange={handleFileChange}
                accept=".pdf,.png,.jpg,.jpeg"
              />
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Dashboard; 