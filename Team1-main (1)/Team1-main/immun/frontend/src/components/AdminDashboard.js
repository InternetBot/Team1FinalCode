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
  Alert,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [records, setRecords] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/records/all-records');
      setRecords(response.data);
    } catch (error) {
      setError('Failed to fetch records');
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4">Admin Dashboard</Typography>
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

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User ID</TableCell>
              <TableCell>Vaccine Name</TableCell>
              <TableCell>Date Administered</TableCell>
              <TableCell>Next Due Date</TableCell>
              <TableCell>Provider</TableCell>
              <TableCell>Document</TableCell>
              <TableCell>Created At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {records.map((record) => (
              <TableRow key={record.id}>
                <TableCell>{record.user_id}</TableCell>
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
                <TableCell>
                  {new Date(record.created_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default AdminDashboard; 